from __future__ import annotations

import re
from typing import Dict, Tuple

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    _HAS_PRESIDIO = True
except ImportError:
    _HAS_PRESIDIO = False


TOKEN_TEMPLATE = "[SECRET_{i}]"


def _simple_detect(text: str) -> list[Tuple[int, int]]:
    """Fallback detector for tokens that look like keys or emails."""
    hits: list[Tuple[int, int]] = []
    for match in re.finditer(r"(sk-[A-Za-z0-9]{20,})|([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,})", text):
        start, end = match.span()
        hits.append((start, end))
    return hits


def redact_content(payload: dict, secret_map: Dict[str, str]) -> dict:
    """
    Redact secrets/PII in the 'messages' content of an OpenAI/Anthropic style chat payload.
    Only modifies in-memory objects; no disk writes.
    """
    messages = payload.get("messages", [])
    if not messages:
        return payload

    analyzer = AnalyzerEngine() if _HAS_PRESIDIO else None
    anonymizer = AnonymizerEngine() if _HAS_PRESIDIO else None

    for msg in messages:
        content = msg.get("content")
        if not isinstance(content, str):
            continue

        if _HAS_PRESIDIO and analyzer and anonymizer:
            results = analyzer.analyze(text=content, entities=[], language="en")
            anonymized = anonymizer.anonymize(text=content, analyzer_results=results)
            new_text = anonymized.text
            # Preserve original strings per token
            for idx, res in enumerate(results):
                token = TOKEN_TEMPLATE.format(i=len(secret_map) + idx + 1)
                secret_map[token] = content[res.start : res.end]
            msg["content"] = new_text
        else:
            hits = _simple_detect(content)
            offset = 0
            new_text = content
            for idx, (start, end) in enumerate(hits):
                token = TOKEN_TEMPLATE.format(i=len(secret_map) + idx + 1)
                secret_map[token] = content[start:end]
                new_text = new_text[: start + offset] + token + new_text[end + offset :]
                offset += len(token) - (end - start)
            msg["content"] = new_text

    return payload


def restore_content(text: str, secret_map: Dict[str, str]) -> str:
    restored = text
    for token, secret in secret_map.items():
        restored = restored.replace(token, secret)
    return restored
