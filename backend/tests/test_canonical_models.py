"""Phase 2A canonical-model + cross-validation tests."""

from __future__ import annotations

import pytest

from app.models.canonical import (
    CanonicalContent,
    EvidenceReference,
    ProvenancedClaim,
    build_empty_canonical,
)
from app.models.common import ProvenanceStatus
from app.services.source_preparation import RAW_ORACLE_FIXTURE, prepare_source

RAW_ORACLE = RAW_ORACLE_FIXTURE


def _segment_id(prepared, order=0):
    return sorted(prepared.segments, key=lambda s: s.order)[order].id


def test_observed_claim_without_evidence_rejected():
    with pytest.raises(ValueError):
        ProvenancedClaim(text="Aurora launched", status=ProvenanceStatus.OBSERVED, evidence=[])


def test_observed_claim_with_evidence_accepted():
    prepared = prepare_source(RAW_ORACLE)
    claim = ProvenancedClaim(
        text="Alpha",
        status=ProvenanceStatus.OBSERVED,
        evidence=[EvidenceReference(segment_id=_segment_id(prepared, 0))],
    )
    assert claim.evidence[0].segment_id == _segment_id(prepared, 0)


def test_inferred_may_exist_without_evidence():
    claim = ProvenancedClaim(text="Should brief leaders", status=ProvenanceStatus.INFERRED)
    assert claim.evidence == []


def test_unknown_may_exist_without_evidence():
    claim = ProvenancedClaim(text="Impact unknown", status=ProvenanceStatus.UNKNOWN)
    assert claim.evidence == []


def test_not_applicable_may_exist_without_evidence():
    claim = ProvenancedClaim(text="Video duration n/a", status=ProvenanceStatus.NOT_APPLICABLE)
    assert claim.evidence == []


def test_no_numeric_confidence_field():
    assert "confidence" not in ProvenancedClaim.model_fields
    assert "confidence" not in EvidenceReference.model_fields
    assert "confidence" not in CanonicalContent.model_fields


def _valid_pair():
    prepared = prepare_source(RAW_ORACLE)
    canonical = build_empty_canonical(prepared)
    assert canonical.facts == []
    return prepared, canonical


def test_valid_pair_validates():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared, canonical = _valid_pair()
    validate_canonical_against_source(canonical, prepared)


def test_nonexistent_evidence_rejected():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared, canonical = _valid_pair()
    canonical.facts.append(
        ProvenancedClaim(
            text="Alpha",
            status=ProvenanceStatus.OBSERVED,
            evidence=[EvidenceReference(segment_id="seg-does-not-exist")],
        )
    )
    with pytest.raises(ValueError, match="evidence|segment"):
        validate_canonical_against_source(canonical, prepared)


def test_duplicate_segment_ids_rejected():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared, canonical = _valid_pair()
    duplicate = canonical.segments[0].model_copy()
    canonical.segments.append(duplicate)
    with pytest.raises(ValueError, match="[Dd]uplicate|unique"):
        validate_canonical_against_source(canonical, prepared)


def test_changed_sha_rejected():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared, canonical = _valid_pair()
    canonical.source.sha256 = "0" * 64
    with pytest.raises(ValueError, match="[Ss][Hh][Aa]|digest"):
        validate_canonical_against_source(canonical, prepared)


def test_changed_character_count_rejected():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared, canonical = _valid_pair()
    canonical.source.character_count = canonical.source.character_count + 1
    with pytest.raises(ValueError, match="character_count|character count"):
        validate_canonical_against_source(canonical, prepared)


def test_invalid_offsets_rejected():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared, canonical = _valid_pair()
    canonical.segments[0].end_offset = canonical.source.character_count + 99
    with pytest.raises(ValueError, match="offset"):
        validate_canonical_against_source(canonical, prepared)


def test_mismatched_segment_text_rejected():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared, canonical = _valid_pair()
    canonical.segments[0].text = "Tampered text"
    with pytest.raises(ValueError, match="text|slice"):
        validate_canonical_against_source(canonical, prepared)


def test_differing_segment_catalog_rejected():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared = prepare_source(RAW_ORACLE)
    other = prepare_source("Alpha\n\nGamma\n")
    canonical = build_empty_canonical(other)
    with pytest.raises(ValueError, match="[Ss]egment|SHA|digest|catalog"):
        validate_canonical_against_source(canonical, prepared)


def test_empty_semantic_lists_valid():
    from app.services.canonical_validation import validate_canonical_against_source

    prepared, canonical = _valid_pair()
    assert canonical.facts == []
    assert canonical.entities == []
    assert canonical.unknowns == []
    validate_canonical_against_source(canonical, prepared)


def test_shell_construction_invents_nothing():
    prepared = prepare_source(RAW_ORACLE)
    canonical = build_empty_canonical(prepared)
    assert canonical.title_or_subject is None
    assert canonical.summary is None
    assert canonical.facts == []
    assert canonical.risks == []
    assert canonical.recommendations == []
