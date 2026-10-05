"""Application analysis workflow: prepare once, call provider, validate loudly."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.analysis import CanonicalSemanticAnalysis
from app.models.canonical import CanonicalContent, PreparedSource
from app.models.common import SourceType
from app.services.analysis_providers import (
    AnalysisProvider,
    CanonicalAnalysisValidationError,
    ProviderAnalysisResult,
)
from app.services.canonical_validation import (
    CanonicalValidationError,
    validate_canonical_against_source,
)
from app.services.ingestion import IngestedSource
from app.services.source_preparation import prepare_source


class AnalysisOutcome(BaseModel):
    """Validated combination of server-owned identity and provider semantics."""

    model_config = {"arbitrary_types_allowed": True}

    prepared: PreparedSource
    canonical: CanonicalContent
    provider: str
    requested_model: str
    provider_reported_model: str | None = None


def _combine(prepared: PreparedSource, semantic: CanonicalSemanticAnalysis) -> CanonicalContent:
    """Combine server-owned identity with provider-owned semantic claims."""
    return CanonicalContent(
        source=prepared.metadata.model_copy(deep=True),
        segments=[segment.model_copy(deep=True) for segment in prepared.segments],
        title_or_subject=semantic.title_or_subject,
        summary=semantic.summary,
        facts=list(semantic.facts),
        entities=list(semantic.entities),
        dates=list(semantic.dates),
        statistics=list(semantic.statistics),
        key_messages=list(semantic.key_messages),
        risks=list(semantic.risks),
        recommendations=list(semantic.recommendations),
        unknowns=list(semantic.unknowns),
    )


def analyze_source(
    raw_text: str,
    provider: AnalysisProvider,
    source_type: SourceType = SourceType.TEXT,
) -> AnalysisOutcome:
    """Prepare source, call provider once, validate; never silently repair."""
    prepared = prepare_source(raw_text, source_type=source_type)
    return _analyze_prepared(prepared, provider)


def analyze_ingested(ingested: IngestedSource, provider: AnalysisProvider) -> AnalysisOutcome:
    """Analyze an ingested source, preserving server-owned ingestion metadata."""
    prepared = prepare_source(ingested.text, source_type=ingested.source_type)
    prepared.metadata.filename = ingested.filename
    prepared.metadata.page_count = ingested.page_count
    return _analyze_prepared(prepared, provider)


def _analyze_prepared(prepared: PreparedSource, provider: AnalysisProvider) -> AnalysisOutcome:
    result: ProviderAnalysisResult = provider.analyze(prepared)
    canonical = _combine(prepared, result.semantic_analysis)
    try:
        validate_canonical_against_source(canonical, prepared)
    except CanonicalValidationError as error:
        raise CanonicalAnalysisValidationError(str(error)) from error
    return AnalysisOutcome(
        prepared=prepared,
        canonical=canonical,
        provider=result.provider,
        requested_model=result.requested_model,
        provider_reported_model=result.provider_reported_model,
    )
