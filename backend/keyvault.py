from __future__ import annotations

import keyring
from typing import Optional

# Service name used for OS keychain entries
SERVICE = "CloakAndCode"


def get_key(name: str) -> Optional[str]:
    """
    Fetch provider API key from OS keychain.
    Returns None if not found. Keys are never written to disk by this module.
    """
    try:
        return keyring.get_password(SERVICE, name)
    except Exception:
        return None


def set_key(name: str, value: str) -> None:
    """
    Store provider API key in OS keychain.
    Intended to be called from the Tauri UI; not invoked by the proxy during normal flow.
    """
    keyring.set_password(SERVICE, name, value)


def delete_key(name: str) -> None:
    try:
        keyring.delete_password(SERVICE, name)
    except Exception:
        pass
