from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class LicenseState:
    status: str = "unknown"  # active | past_due | expired | invalid | unknown
    grace_ends_at: Optional[float] = None  # epoch seconds
    last_checked: Optional[float] = None
    request_tally: int = 0

    def in_grace(self) -> bool:
        return self.grace_ends_at is not None and time.time() < self.grace_ends_at

    def increment_request(self) -> int:
        self.request_tally += 1
        return self.request_tally

    def reset_tally(self) -> None:
        self.request_tally = 0


class GlobalState:
    def __init__(self) -> None:
        self.cloak_enabled: bool = True
        self.license = LicenseState()
        self._lock = asyncio.Lock()

    async def set_cloak(self, enabled: bool) -> None:
        async with self._lock:
            self.cloak_enabled = enabled

    async def is_cloak_enabled(self) -> bool:
        async with self._lock:
            return self.cloak_enabled


state = GlobalState()
