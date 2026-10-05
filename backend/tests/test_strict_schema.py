"""Strict nested provider-schema regression tests (human-probe equivalent).

Proves unknown fields are REJECTED (not silently ignored) at every level of
provider-controlled input. No numeric confidence field exists by design.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.analysis import CanonicalSemanticAnalysis
from app.models.canonical import EvidenceReference, ProvenancedClaim
from app.models.common import ProvenanceStatus


def test_top_level_source_identity_rejected():
    with pytest.raises(ValidationError):
        CanonicalSemanticAnalysis(**{"source": {"sha256": "x"}})  # type: ignore[arg-type]


def test_nested_claim_confidence_rejected():
    with pytest.raises(ValidationError):
        ProvenancedClaim(
            **{  # type: ignore[arg-type]
                "text": "Example inference",
                "status": ProvenanceStatus.INFERRED,
                "evidence": [],
                "confidence": 0.99,
            }
        )


def test_nested_evidence_confidence_rejected():
    with pytest.raises(ValidationError):
        EvidenceReference(**{"segment_id": "seg-0000-abc", "confidence": 0.99})  # type: ignore[arg-type]


def test_arbitrary_nested_claim_field_rejected():
    with pytest.raises(ValidationError):
        ProvenancedClaim(
            **{  # type: ignore[arg-type]
                "text": "Example",
                "status": ProvenanceStatus.UNKNOWN,
                "evidence": [],
                "unexpected_field": "nope",
            }
        )


def test_valid_claim_still_parses():
    claim = ProvenancedClaim(text="Example inference", status="INFERRED", evidence=[])
    assert claim.text == "Example inference"


def test_valid_evidence_still_parses():
    reference = EvidenceReference(segment_id="seg-0000-abc")
    assert reference.segment_id == "seg-0000-abc"


def test_human_probe_semantic_payload_rejected():
    payload = {
        "facts": [
            {
                "text": "Example inference",
                "status": ProvenanceStatus.INFERRED,
                "evidence": [],
                "confidence": 0.99,
            }
        ]
    }
    with pytest.raises(ValidationError):
        CanonicalSemanticAnalysis(**payload)  # type: ignore[arg-type]


def test_valid_semantic_payload_parses():
    payload = {
        "facts": [
            {"text": "Example inference", "status": ProvenanceStatus.INFERRED, "evidence": []}
        ]
    }
    parsed = CanonicalSemanticAnalysis(**payload)
    assert len(parsed.facts) == 1


def test_generated_schema_forbids_additional_properties():
    schema = CanonicalSemanticAnalysis.model_json_schema()
    assert schema.get("additionalProperties") is False
    definitions = schema.get("$defs", {})
    assert definitions["ProvenancedClaim"].get("additionalProperties") is False
    assert definitions["EvidenceReference"].get("additionalProperties") is False
