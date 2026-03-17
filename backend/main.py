from __future__ import annotations

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes.proxy import router as proxy_router
from .routes.test import router as test_router
from .state import state
from .license import license_manager


def create_app() -> FastAPI:
    app = FastAPI(title="Cloak and Code Proxy", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event() -> None:
        await license_manager.start()

    @app.get("/health")
    async def health() -> dict:
        return {
            "status": "ok",
            "cloak_enabled": await state.is_cloak_enabled(),
            "license_status": state.license.status,
        }

    @app.post("/toggle")
    async def toggle(cloak: bool) -> dict:
        await state.set_cloak(cloak)
        return {"cloak_enabled": cloak}

    app.include_router(proxy_router, prefix="")
    app.include_router(test_router, prefix="")
    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    asyncio.run(license_manager.start())
    run()
