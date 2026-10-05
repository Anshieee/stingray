"""Environment-driven analysis-provider configuration (names only, no secrets)."""

from __future__ import annotations

import os

from app.services.analysis_providers import AnalysisProvider, ProviderNotConfigured
from app.services.openai_provider import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS

SUPPORTED_PROVIDERS = ("openai", "freellmapi")

# Normal local FreeLLMAPI router endpoint (non-secret; explicit override allowed).
DEFAULT_FREELLMAPI_BASE_URL = "http://localhost:3001/v1"


def provider_from_environment() -> AnalysisProvider:
    """Build the configured provider or raise ProviderNotConfigured honestly."""
    from app.services.openai_provider import (
        OpenAIAnalysisProvider,
        OpenAICompatibleAnalysisProvider,
    )

    provider_name = os.environ.get("AI_PROVIDER", "").strip()
    if not provider_name:
        raise ProviderNotConfigured("AI analysis provider is not configured.")
    if provider_name not in SUPPORTED_PROVIDERS:
        raise ProviderNotConfigured(
            "Unsupported AI provider: "
            f"{provider_name!r}. Supported: openai, freellmapi."
        )
    if provider_name == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = os.environ.get("OPENAI_MODEL", "")
        if not api_key:
            raise ProviderNotConfigured("OpenAI API key is not configured.")
        if not model:
            raise ProviderNotConfigured("OpenAI model is not configured.")
        return OpenAIAnalysisProvider(
            api_key=api_key,
            model=model,
            timeout=REQUEST_TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES,
        )
    api_key = os.environ.get("FREELLMAPI_API_KEY", "")
    model = os.environ.get("FREELLMAPI_MODEL", "")
    base_url = os.environ.get("FREELLMAPI_BASE_URL", "").strip()
    if not api_key:
        raise ProviderNotConfigured("FreeLLMAPI API key is not configured.")
    if not model:
        raise ProviderNotConfigured("FreeLLMAPI model is not configured.")
    return OpenAICompatibleAnalysisProvider(
        api_key=api_key,
        model=model,
        provider="freellmapi",
        base_url=base_url or DEFAULT_FREELLMAPI_BASE_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=MAX_RETRIES,
    )
