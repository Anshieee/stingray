"""OpenAI-compatible Responses-API adapter (structured Pydantic parsing).

Speaks the OpenAI Responses protocol, which both direct OpenAI and
OpenAI-compatible routers (e.g. FreeLLMAPI) accept. Transport SDK identity never
determines application provider identity: callers pass an explicit `provider`
name (e.g. "openai" or "freellmapi") and, for compatible routers, an explicit
`base_url`. No JSON scraping.

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


class OpenAICompatibleAnalysisProvider:
    """Responses-API structured analysis against an OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: str,
        model: str,
        provider: str = "openai",
        base_url: str | None = None,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
        client: Any | None = None,
        client_factory: Callable[[], Any] | None = None,
    ) -> None:
        if not api_key:
            raise ProviderAuthenticationError(f"{provider} API key is not configured.")
        if not model:
            raise ProviderAuthenticationError(f"{provider} model is not configured.")
        self._api_key = api_key
        self._model = model
        self._provider_name = provider
        self._base_url = base_url
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
            base_url=self._base_url,
            timeout=self._timeout,
            max_retries=self._max_retries,
        )

    def analyze(self, prepared: PreparedSource) -> ProviderAnalysisResult:
        import openai

        client = self._get_client()
        source_input = build_analysis_input(prepared)
        label = self._provider_name
        try:
            response = client.responses.parse(
                model=self._model,
                instructions=TRUSTED_ANALYSIS_INSTRUCTIONS,
                input=source_input,
                text_format=CanonicalSemanticAnalysis,
                timeout=self._timeout,
            )
        except openai.AuthenticationError as error:
            raise ProviderAuthenticationError(f"{label} authentication failed.") from error
        except openai.RateLimitError as error:
            raise ProviderRateLimitError(f"{label} rate limit reached.") from error
        except openai.APITimeoutError as error:
            raise ProviderTimeoutError(f"{label} request timed out.") from error
        except openai.APIConnectionError as error:
            raise ProviderConnectionError(f"{label} connection failed.") from error
        except openai.OpenAIError as error:
            raise ProviderInvalidResponseError(f"{label} request failed.") from error
        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            raise ProviderInvalidResponseError(
                f"{label} returned no parsed structured output (refusal or invalid)."
            )
        if not isinstance(parsed, CanonicalSemanticAnalysis):
            try:
                parsed = CanonicalSemanticAnalysis.model_validate(parsed)
            except Exception as error:
                raise ProviderInvalidResponseError(
                    f"{label} structured output failed validation."
                ) from error
        reported = getattr(response, "model", None)
        provider_reported_model = reported if isinstance(reported, str) and reported else None
        return ProviderAnalysisResult(
            semantic_analysis=parsed,
            provider=self._provider_name,
            requested_model=self._model,
            provider_reported_model=provider_reported_model,
        )


class OpenAIAnalysisProvider(OpenAICompatibleAnalysisProvider):
    """Direct-OpenAI identity over the shared compatible adapter (no base_url)."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
        client: Any | None = None,
        client_factory: Callable[[], Any] | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            provider="openai",
            base_url=None,
            timeout=timeout,
            max_retries=max_retries,
            client=client,
            client_factory=client_factory,
        )
