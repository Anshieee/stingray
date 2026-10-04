"""Typed analysis API contracts (Phase 2B, provider-backed, no frontend)."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.canonical import CanonicalContent, ProvenancedClaim
from app.models.transform import SourceInput


class AnalysisMode(StrEnum):
    AI_STRUCTURED_ANALYSIS = "AI_STRUCTURED_ANALYSIS"


class CanonicalSemanticAnalysis(BaseModel):
    """Provider-owned semantic content only; source identity is server-owned."""

    model_config = ConfigDict(extra="forbid")

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


class AnalyzeRequest(BaseModel):
    """Plain-text source only; reuses Phase-1 validated source constraints."""

    source: SourceInput


class AnalyzeResponse(BaseModel):
    status: Literal["ok"]
    mode: AnalysisMode
    provider: str
    requested_model: str
    provider_reported_model: str | None = None
    canonical_content: CanonicalContent
    warnings: list[str] = Field(default_factory=list)


class AnalysisErrorDetail(BaseModel):
    code: str
    message: str


class AnalysisErrorResponse(BaseModel):
    status: Literal["error"]
    error: AnalysisErrorDetail
