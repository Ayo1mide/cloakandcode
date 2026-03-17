from backend.routes.proxy import _detect_provider
from backend.providers import registry


def test_detect_anthropic_by_header():
    provider = _detect_provider({"anthropic-version": "2023-06-01"}, None)
    assert provider.name == "anthropic"


def test_detect_gemini_by_model():
    provider = _detect_provider({}, {"model": "gemini-pro"})
    assert provider.name == "gemini"


def test_detect_perplexity_by_model():
    provider = _detect_provider({}, {"model": "pplx-70b-chat"})
    assert provider.name == "perplexity"


def test_detect_mistral_by_model():
    provider = _detect_provider({}, {"model": "mistral-medium"})
    assert provider.name == "mistral"


def test_default_openai():
    provider = _detect_provider({}, {})
    assert provider.name == "openai"
