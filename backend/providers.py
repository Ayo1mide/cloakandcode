from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Callable, Optional

from .config import settings
from . import keyvault


@dataclass
class Provider:
    name: str
    base_url: str
    auth_header_builder: Callable[[], dict]


def _bearer(token: Optional[str]) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def _api_key(header_name: str, token: Optional[str]) -> dict:
    return {header_name: token} if token else {}


class ProviderRegistry:
    def __init__(self) -> None:
        self.providers: Dict[str, Provider] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            Provider(
                name="openai",
                base_url=str(settings.openai_base),
                auth_header_builder=lambda: _bearer(keyvault.get_key("openai")),
            )
        )
        self.register(
            Provider(
                name="anthropic",
                base_url=str(settings.anthropic_base),
                auth_header_builder=lambda: _api_key("x-api-key", keyvault.get_key("anthropic")),
            )
        )
        if settings.azure_openai_base:
            self.register(
                Provider(
                    name="azure-openai",
                    base_url=str(settings.azure_openai_base),
                    auth_header_builder=lambda: _api_key("api-key", keyvault.get_key("azure-openai")),
                )
            )
        self.register(
            Provider(
                name="gemini",
                base_url=str(settings.gemini_base),
                auth_header_builder=lambda: {"x-goog-api-key": keyvault.get_key("gemini")} if keyvault.get_key("gemini") else {},
            )
        )
        if settings.ollama_base:
            self.register(
                Provider(
                    name="ollama",
                    base_url=str(settings.ollama_base),
                    auth_header_builder=lambda: _bearer(keyvault.get_key("ollama")),
                )
            )
        self.register(
            Provider(
                name="perplexity",
                base_url=str(settings.perplexity_base),
                auth_header_builder=lambda: _bearer(keyvault.get_key("perplexity")),
            )
        )
        self.register(
            Provider(
                name="cohere",
                base_url=str(settings.cohere_base),
                auth_header_builder=lambda: _bearer(keyvault.get_key("cohere")),
            )
        )
        self.register(
            Provider(
                name="mistral",
                base_url=str(settings.mistral_base),
                auth_header_builder=lambda: _api_key("Authorization", f"Bearer {keyvault.get_key('mistral')}" if keyvault.get_key("mistral") else None),
            )
        )
        self.register(
            Provider(
                name="groq",
                base_url=str(settings.groq_base),
                auth_header_builder=lambda: _bearer(keyvault.get_key("groq")),
            )
        )
        self.register(
            Provider(
                name="together",
                base_url=str(settings.together_base),
                auth_header_builder=lambda: _bearer(keyvault.get_key("together")),
            )
        )
        self.register(
            Provider(
                name="openrouter",
                base_url=str(settings.openrouter_base),
                auth_header_builder=lambda: _bearer(keyvault.get_key("openrouter")),
            )
        )

    def register(self, provider: Provider) -> None:
        self.providers[provider.name] = provider

    def get(self, name: str) -> Provider:
        key = name.lower()
        if key not in self.providers:
            raise KeyError(f"Unknown provider '{name}'")
        return self.providers[key]

    def choose_default(self, header_provider: str | None) -> Provider:
        if header_provider:
            return self.get(header_provider)
        return self.get("openai")


registry = ProviderRegistry()
