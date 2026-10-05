"""Typed deterministic canonical-content domain models (Phase 2A, no AI)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.common import ProvenanceStatus, SourceType


class SourceMetadata(BaseModel):
    """Deterministic identity for one prepared plain-text source."""

    source_type: SourceType = Field(description="Input kind that produced this source.")
    sha256: str = Field(
        pattern=r"[0-9a-f]{64}",
        description="SHA-256 of UTF-8 normalized source text.",
    )
    character_count: int = Field(ge=0, description="len(normalized_text).")
    segment_count: int = Field(ge=0, description="Number of source segments.")
    filename: str | None = Field(
        default=None, description="Untrusted display name from upload, if any."
    )
    page_count: int | None = Field(
        default=None, ge=1, description="Total document pages, if applicable."
    )


class SourceSegment(BaseModel):
    """One deterministic paragraph segment with exact source offsets."""

    id: str = Field(min_length=1, description="Stable deterministic segment identifier.")
    order: int = Field(ge=0, description="Zero-based source-relative order.")
    text: str = Field(min_length=1, description="Exact normalized_source[start:end].")
    start_offset: int = Field(ge=0, description="Inclusive character index.")
    end_offset: int = Field(gt=0, description="Exclusive character index.")

    @model_validator(mode="after")
    def _check_offsets_shape(self) -> SourceSegment:
        if self.start_offset >= self.end_offset:
            raise ValueError("start_offset must be < end_offset")
        if not self.text.strip():
            raise ValueError("segment text must not be empty or whitespace-only")
        return self


class PreparedSource(BaseModel):
    """Backend/domain object (not an API response in Phase 2A)."""

    normalized_text: str = Field(description="Line-ending normalized source text.")
    metadata: SourceMetadata
    segments: list[SourceSegment]


class EvidenceReference(BaseModel):
    """Minimal pointer to one prepared source segment."""

    model_config = ConfigDict(extra="forbid")

    segment_id: str = Field(min_length=1, description="Must exist in PreparedSource.")


class ProvenancedClaim(BaseModel):
    """Reusable provenance-aware claim without numeric confidence."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    status: ProvenanceStatus
    evidence: list[EvidenceReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_observed_evidence(self) -> ProvenancedClaim:
        if self.status == ProvenanceStatus.OBSERVED and len(self.evidence) == 0:
            raise ValueError("OBSERVED claims require at least one evidence reference")
        return self


class CanonicalContent(BaseModel):
    """Shared deterministic representation for future output generators."""

    source: SourceMetadata
    segments: list[SourceSegment]
    title_or_subject: ProvenancedClaim | None = None
    summary: ProvenancedClaim | None = None
    facts: list[ProvenancedClaim] = Field(default_factory=list)
    entities: list[ProvenancedClaim] = Field(default_factory=list)
    dates: list[ProvenancedClaim] = Field(default_factory=list)
    statistics: list[ProvenancedClaim] = Field(default_factory=list)
    key_messages: list[ProvenancedClaim] = Field(default_factory=list)
    risks: list[ProvenancedClaim] = Field(default_factory=list)
    recommendations: list[ProvenancedClaim] = Field(default_factory=list)
    unknowns: list[ProvenancedClaim] = Field(default_factory=list)

    def all_claims(self) -> list[ProvenancedClaim]:
        """Return every semantic claim in a stable field order."""
        claims: list[ProvenancedClaim] = []
        if self.title_or_subject is not None:
            claims.append(self.title_or_subject)
        if self.summary is not None:
            claims.append(self.summary)
        claims.extend(self.facts)
        claims.extend(self.entities)
        claims.extend(self.dates)
        claims.extend(self.statistics)
        claims.extend(self.key_messages)
        claims.extend(self.risks)
        claims.extend(self.recommendations)
        claims.extend(self.unknowns)
        return claims


def build_empty_canonical(prepared: PreparedSource) -> CanonicalContent:
    """Build an empty semantic shell around a prepared source.

    Copies metadata/segments and leaves every semantic slot absent/empty.
    Never infers title, summary, facts, risks or recommendations.
    """
    return CanonicalContent(
        source=prepared.metadata.model_copy(deep=True),
        segments=[segment.model_copy(deep=True) for segment in prepared.segments],
        title_or_subject=None,
        summary=None,
        facts=[],
        entities=[],
        dates=[],
        statistics=[],
        key_messages=[],
        risks=[],
        recommendations=[],
        unknowns=[],
    )
