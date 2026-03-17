from __future__ import annotations

import json
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request

from ..redaction import redact_content
from ..providers import registry
from .. import keyvault
from ..config import settings

router = APIRouter()


@router.post("/redact")
async def redact_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Testing helper: returns redacted payload and the temporary secret map.
    Accepts either { "messages": [...] } or { "text": "..." }.
    """
    secret_map: Dict[str, str] = {}
    working = payload
    if "text" in payload and "messages" not in payload:
        working = {"messages": [{"role": "user", "content": payload["text"]}]}

    redacted = redact_content(working, secret_map)
    return {"redacted": redacted, "secret_map": secret_map}


@router.post("/set-key")
async def set_key(provider: str, key: str) -> Dict[str, str]:
    """
    Testing helper: stores provider key in OS keychain.
    Guarded by CLOAK_DEV_ENABLE_TEST_ENDPOINTS.
    """
    if not settings.dev_enable_test_endpoints:
        raise HTTPException(status_code=404, detail="Not enabled")

    # Validate provider exists in registry
    try:
        registry.get(provider)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    keyvault.set_key(provider, key)
    return {"status": "ok", "provider": provider}
