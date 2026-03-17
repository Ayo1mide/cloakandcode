from __future__ import annotations

import asyncio
import time
from typing import Optional

import httpx

from .config import settings
from .state import state, LicenseState


class LicenseManager:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(timeout=10.0)
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    async def _loop(self) -> None:
        while True:
            try:
                await self.verify_license()
            except Exception:
                # Silent failure to avoid crashing; will retry on next interval
                pass
            await asyncio.sleep(settings.renewal_interval_seconds)

    async def verify_license(self) -> None:
        payload = {"key": settings.lemon_api_key, "machine_id": self._machine_id()}
        # primary verify endpoint
        try:
            res = await self.client.get(
                settings.license_verify_url,
                params={"key": settings.lemon_api_key},
            )
            status = res.json().get("status", "unknown") if res.is_success else "unknown"
        except Exception:
            status = "unknown"

        # Lemon Squeezy license sync (best effort)
        if settings.lemon_api_key:
            try:
                ls_res = await self.client.post(
                    f"{settings.lemon_license_api}/activate",
                    headers={"Authorization": f"Bearer {settings.lemon_api_key}"},
                    json=payload,
                )
                if ls_res.is_success:
                    status = ls_res.json().get("status", status)
            except Exception:
                pass

        await self._update_state(status)

    async def _update_state(self, status: str) -> None:
        now = time.time()
        lic: LicenseState = state.license
        lic.last_checked = now
        lic.status = status

        if status == "past_due":
            lic.grace_ends_at = now + settings.license_grace_days * 86400
        elif status == "active":
            lic.grace_ends_at = None
            lic.reset_tally()
        elif status == "expired":
            # keep existing grace if any; otherwise none
            if not lic.grace_ends_at:
                lic.grace_ends_at = now

    def _machine_id(self) -> str:
        # Simple machine identifier; replace with platform node or hardware hash if desired
        import platform

        return platform.node()


license_manager = LicenseManager()
