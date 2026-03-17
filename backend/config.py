import os
from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080
    dev_enable_test_endpoints: bool = False

    # Upstream providers
    openai_base: AnyHttpUrl = "https://api.openai.com/v1"
    anthropic_base: AnyHttpUrl = "https://api.anthropic.com"
    azure_openai_base: AnyHttpUrl | None = None  # e.g. https://{resource}.openai.azure.com
    gemini_base: AnyHttpUrl = "https://generativelanguage.googleapis.com"
    ollama_base: AnyHttpUrl | None = "http://127.0.0.1:11434"
    perplexity_base: AnyHttpUrl = "https://api.perplexity.ai"
    cohere_base: AnyHttpUrl = "https://api.cohere.ai"
    mistral_base: AnyHttpUrl = "https://api.mistral.ai"
    groq_base: AnyHttpUrl = "https://api.groq.com/openai/v1"
    together_base: AnyHttpUrl = "https://api.together.xyz/v1"
    openrouter_base: AnyHttpUrl = "https://openrouter.ai/api/v1"

    # API keys BYOK: retrieved at runtime from OS keychain, never persisted in files/env.

    # Licensing / Lemon Squeezy
    license_verify_url: AnyHttpUrl = "https://api.cloakandcode.ai/verify"
    lemon_license_api: AnyHttpUrl = "https://api.lemonsqueezy.com/v1/licenses"
    lemon_api_key: str | None = os.getenv("LEMON_SQUEEZY_API_KEY")
    license_grace_days: int = 3
    max_requests_when_unlicensed: int = 20

    # Renewal cadence (seconds)
    renewal_interval_seconds: int = 60 * 60 * 24  # 24h

    class Config:
        env_prefix = "CLOAK_"
        case_sensitive = False


settings = Settings()
