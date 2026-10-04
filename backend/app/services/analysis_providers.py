"""Provider-neutral analysis interface and application error taxonomy."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field

from app.models.analysis import CanonicalSemanticAnalysis
from app.models.canonical import PreparedSource


class ProviderNotConfigured(ValueError):
    """No analysis provider is configured via environment."""


class ProviderAuthenticationError(ValueError):
    """Provider rejected credentials or service configuration."""


class ProviderRateLimitError(ValueError):
    """Provider reported rate limiting."""


class ProviderTimeoutError(ValueError):
    """Provider request exceeded its finite timeout."""


class ProviderConnectionError(ValueError):
    """Provider transport or upstream failure."""


class ProviderInvalidResponseError(ValueError):
    """Provider refusal, malformed structured output, or unusable response."""


class CanonicalAnalysisValidationError(ValueError):
    """Provider result failed canonical structural validation."""


class ProviderAnalysisResult(BaseModel):
    """Application-owned provider result; no SDK objects leak through."""

    semantic_analysis: CanonicalSemanticAnalysis
    provider: str = Field(min_length=1)
    requested_model: str = Field(min_length=1)
    provider_reported_model: str | None = None


class AnalysisProvider(Protocol):
    """Provider-neutral interface; service layer depends only on this."""

    def analyze(self, prepared: PreparedSource) -> ProviderAnalysisResult:
        """Analyze one prepared source exactly once, returning semantic content."""
        ...  # pragma: no cover
