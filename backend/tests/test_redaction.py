import pytest

from backend.redaction import redact_content, restore_content


def test_redact_and_restore_email():
    payload = {"messages": [{"role": "user", "content": "Contact me at jane@example.com"}]}
    secret_map = {}
    redacted = redact_content(payload, secret_map)
    text = redacted["messages"][0]["content"]
    assert "[SECRET_" in text
    restored = restore_content(text, secret_map)
    assert "jane@example.com" in restored


def test_no_messages_no_change():
    payload = {"foo": "bar"}
    secret_map = {}
    redacted = redact_content(payload, secret_map)
    assert redacted == payload
    assert secret_map == {}
