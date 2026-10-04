"""POST /api/v1/analyze: provider-backed structured source analysis."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.models.analysis import AnalysisMode, AnalyzeRequest, AnalyzeResponse
from app.services.analysis import analyze_source
from app.services.analysis_config import provider_from_environment
from app.services.analysis_providers import (
    AnalysisProvider,
    CanonicalAnalysisValidationError,
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderInvalidResponseError,
    ProviderNotConfigured,
    ProviderRateLimitError,
    ProviderTimeoutError,
)

router = APIRouter(tags=["analyze"])

# Fixed public messages: never echo provider internals, secrets, or source text.
_ERROR_MAP: tuple[tuple[type[ValueError], int, str, str], ...] = (
    (
        ProviderNotConfigured,
        503,
        "PROVIDER_NOT_CONFIGURED",
        "AI analysis provider is not configured.",
    ),
    (
        ProviderAuthenticationError,
        503,
        "PROVIDER_AUTHENTICATION_ERROR",
        "Analysis provider authentication failed.",
    ),
    (
        ProviderRateLimitError,
        503,
        "PROVIDER_RATE_LIMITED",
        "Analysis provider rate limit reached.",
    ),
    (
        ProviderTimeoutError,
        504,
        "PROVIDER_TIMEOUT",
        "Analysis provider request timed out.",
    ),
    (
        ProviderConnectionError,
        502,
        "PROVIDER_CONNECTION_ERROR",
        "Analysis provider connection failed.",
    ),
    (
        ProviderInvalidResponseError,
        502,
        "PROVIDER_INVALID_RESPONSE",
        "Analysis provider returned an unusable response.",
    ),
    (
        CanonicalAnalysisValidationError,
        502,
        "CANONICAL_VALIDATION_FAILED",
        "Provider result failed canonical validation.",
    ),
)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "error": {"code": code, "message": message}},
    )


def analysis_error_response(error: ValueError) -> JSONResponse | None:
    """Map taxonomy errors to safe responses; None when unmapped."""
    for error_type, status_code, code, message in _ERROR_MAP:
        if isinstance(error, error_type):
            return _error_response(status_code, code, message)
    return None


def register_analysis_error_handlers(application) -> None:
    """Handle provider errors raised in dependencies (outside endpoint try)."""

    for error_type, status_code, code, message in _ERROR_MAP:

        def _handler(
            _request: Request,
            _error: ValueError,
            _status_code: int = status_code,
            _code: str = code,
            _message: str = message,
        ) -> JSONResponse:
            return _error_response(_status_code, _code, _message)

        application.add_exception_handler(error_type, _handler)


def get_analysis_provider(request: Request) -> AnalysisProvider:
    """Dependency seam: explicit app override wins, otherwise environment config."""
    override = getattr(request.app.state, "analysis_provider", None)
    if override is not None:
        return override
    return provider_from_environment()


@router.post("/analyze", response_model=AnalyzeResponse, status_code=200)
def analyze(
    request: AnalyzeRequest,
    provider: AnalysisProvider = Depends(get_analysis_provider),  # noqa: B008
) -> AnalyzeResponse | JSONResponse:
    """Analyze plain text once into validated canonical content."""
    try:
        outcome = analyze_source(request.source.text, provider)
    except tuple(error_type for error_type, _, _, _ in _ERROR_MAP) as error:
        response = analysis_error_response(error)
        if response is not None:
            return response
        raise  # pragma: no cover
    return AnalyzeResponse(
        status="ok",
        mode=AnalysisMode.AI_STRUCTURED_ANALYSIS,
        provider=outcome.provider,
        requested_model=outcome.requested_model,
        provider_reported_model=outcome.provider_reported_model,
        canonical_content=outcome.canonical,
        warnings=[],
    )
