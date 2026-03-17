from __future__ import annotations

import json
from typing import Any, Dict, Tuple

import httpx
from fastapi import APIRouter, Request, Response

from ..config import settings
from ..providers import registry, Provider
from ..redaction import redact_content, restore_content
from ..state import state

router = APIRouter()


def _detect_provider(headers: Dict[str, str], payload: Dict[str, Any] | None) -> Provider:
    header_provider = headers.get("x-provider")
    if header_provider:
        return registry.choose_default(header_provider)

    h_lower = {k.lower(): v for k, v in headers.items()}
    if "anthropic-version" in h_lower:
        return registry.get("anthropic")
    model = None
    if payload:
        model = payload.get("model") or payload.get("messages", [{}])[0].get("model")
    if isinstance(model, str) and "claude" in model.lower():
        return registry.get("anthropic")
    if isinstance(model, str) and "gemini" in model.lower():
        return registry.get("gemini")
    if isinstance(model, str) and "pplx" in model.lower():
        return registry.get("perplexity")
    if isinstance(model, str) and ("mistral" in model.lower() or "mixtral" in model.lower()):
        return registry.get("mistral")
    if isinstance(model, str) and ("command" in model.lower() or "cohere" in model.lower()):
        return registry.get("cohere")
    if isinstance(model, str) and ("grok" in model.lower() or "xai" in model.lower()):
        return registry.get("groq")
    if isinstance(model, str) and ("openrouter" in model.lower()):
        return registry.get("openrouter")
    if isinstance(model, str) and ("llama" in model.lower() or "ollama" in model.lower()):
        return registry.get("ollama")
    if isinstance(model, str) and ("groq" in model.lower()):
        return registry.get("groq")
    if isinstance(model, str) and ("together" in model.lower()):
        return registry.get("together")
    # default
    return registry.get("openai")


async def _within_license_limits() -> bool:
    lic = state.license
    if lic.status in ("active", "past_due") or lic.in_grace():
        return True
    if lic.status in ("invalid", "expired", "unknown"):
        return lic.increment_request() <= settings.max_requests_when_unlicensed
    return True


async def _forward(
    client: httpx.AsyncClient,
    provider: Provider,
    path: str,
    method: str,
    headers: Dict[str, str],
    body: bytes | None,
) -> httpx.Response:
    url = f"{provider.base_url.rstrip('/')}/{path}"
    upstream_headers = dict(headers)
    lower = {k.lower(): k for k in upstream_headers.keys()}

    # Only inject provider auth if caller did not supply one
    provider_auth = provider.auth_header_builder()
    for key, value in provider_auth.items():
        if key.lower() not in lower:
            upstream_headers[key] = value

    upstream_headers.pop("host", None)
    upstream_headers.pop("content-length", None)
    upstream_headers.pop("x-provider", None)
    upstream_headers.pop("x-cloak-toggle", None)
    return await client.request(method, url, content=body, headers=upstream_headers)


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(request: Request, path: str) -> Response:
    body_bytes = await request.body()
    secret_map: Dict[str, str] = {}
    payload = None

    if body_bytes:
        try:
            payload = json.loads(body_bytes)
        except json.JSONDecodeError:
            payload = None

    provider = _detect_provider(dict(request.headers), payload)

    if not await _within_license_limits():
        return Response(
            content=json.dumps({"error": "License invalid; daily local limit reached."}),
            status_code=402,
            media_type="application/json",
        )

    # Redact only when enabled and payload is JSON
    headers = dict(request.headers)
    content_type = headers.get("content-type", "")
    should_cloak = await state.is_cloak_enabled() and "application/json" in content_type

    if should_cloak and payload is not None:
        redacted = redact_content(payload, secret_map)
        body_bytes = json.dumps(redacted).encode("utf-8")

    async with httpx.AsyncClient(timeout=None) as client:
        upstream_resp = await _forward(
            client=client,
            provider=provider,
            path=path,
            method=request.method,
            headers=headers,
            body=body_bytes if body_bytes else None,
        )

    # Restore secrets inside JSON responses when applicable
    content = upstream_resp.content
    if secret_map and upstream_resp.headers.get("content-type", "").startswith("application/json"):
        try:
            resp_json = upstream_resp.json()
            if isinstance(resp_json, dict):
                if "choices" in resp_json:
                    for choice in resp_json["choices"]:
                        if "message" in choice and isinstance(choice["message"], dict):
                            msg_content = choice["message"].get("content")
                            if isinstance(msg_content, str):
                                choice["message"]["content"] = restore_content(msg_content, secret_map)
                content = json.dumps(resp_json).encode("utf-8")
        except Exception:
            pass

    resp_headers = dict(upstream_resp.headers)
    # If no auth was provided anywhere, warn the caller
    if (
        "authorization" not in {k.lower() for k in headers}
        and "x-api-key" not in {k.lower() for k in headers}
        and not provider.auth_header_builder()
    ):
        resp_headers["x-cloak-warning"] = "No upstream API key provided; request likely failed."

    return Response(
        content=content,
        status_code=upstream_resp.status_code,
        headers=resp_headers,
        media_type=upstream_resp.headers.get("content-type"),
    )
