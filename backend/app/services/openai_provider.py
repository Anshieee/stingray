"""Official OpenAI Responses-API adapter (structured Pydantic parsing, no JSON scraping).

Timeout: 30s per request. Retries: SDK max_retries=1. No network at import time;
no API key required to import this module or start FastAPI.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.models.analysis import CanonicalSemanticAnalysis
from app.models.canonical import PreparedSource
from app.services.analysis_prompts import (
    TRUSTED_ANALYSIS_INSTRUCTIONS,
    build_analysis_input,
)
from app.services.analysis_providers import (
    ProviderAnalysisResult,
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderInvalidResponseError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)

REQUEST_TIMEOUT_SECONDS = 30.0
MAX_RETRIES = 1


class OpenAIAnalysisProvider:
    """OpenAI-backed AnalysisProvider using responses.parse structured output."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
        client: Any | None = None,
        client_factory: Callable[[], Any] | None = None,
    ) -> None:
        if not api_key:
            raise ProviderAuthenticationError("OpenAI API key is not configured.")
        if not model:
            raise ProviderAuthenticationError("OpenAI model is not configured.")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = client
        self._client_factory = client_factory

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        if self._client_factory is not None:
            return self._client_factory()
        import openai

        return openai.OpenAI(
            api_key=self._api_key,
            timeout=self._timeout,
            max_retries=self._max_retries,
        )

    def analyze(self, prepared: PreparedSource) -> ProviderAnalysisResult:
        import openai

        client = self._get_client()
        source_input = build_analysis_input(prepared)
        try:
            response = client.responses.parse(
                model=self._model,
                instructions=TRUSTED_ANALYSIS_INSTRUCTIONS,
                input=source_input,
                text_format=CanonicalSemanticAnalysis,
                timeout=self._timeout,
            )
        except openai.AuthenticationError as error:
            raise ProviderAuthenticationError(f"OpenAI authentication failed: {error}") from error
        except openai.RateLimitError as error:
            raise ProviderRateLimitError(f"OpenAI rate limit: {error}") from error
        except openai.APITimeoutError as error:
            raise ProviderTimeoutError(f"OpenAI request timed out: {error}") from error
        except openai.APIConnectionError as error:
            raise ProviderConnectionError(f"OpenAI connection failed: {error}") from error
        except openai.OpenAIError as error:
            raise ProviderInvalidResponseError(f"OpenAI request failed: {error}") from error
        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            raise ProviderInvalidResponseError(
                "OpenAI returned no parsed structured output (refusal or invalid)."
            )
        if not isinstance(parsed, CanonicalSemanticAnalysis):
            try:
                parsed = CanonicalSemanticAnalysis.model_validate(parsed)
            except Exception as error:
                raise ProviderInvalidResponseError(
                    f"OpenAI structured output failed validation: {error}"
                ) from error
        reported = getattr(response, "model", None)
        provider_reported_model = reported if isinstance(reported, str) and reported else None
        return ProviderAnalysisResult(
            semantic_analysis=parsed,
            provider="openai",
            requested_model=self._model,
            provider_reported_model=provider_reported_model,
        )
