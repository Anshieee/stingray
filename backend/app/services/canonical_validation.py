"""Cross-object structural validation for canonical content (Phase 2A).

Proves structural evidence validity (cited segment exists, offsets valid, text
matches, OBSERVED has evidence). Does NOT prove semantic entailment: a valid
reference may still misstate the cited passage. Semantic grounding belongs to a
later validation/grounding phase.
"""

from __future__ import annotations

from app.models.canonical import CanonicalContent, PreparedSource
from app.models.common import ProvenanceStatus
from app.services.source_preparation import sha256_hex


class CanonicalValidationError(ValueError):
    """Raised when canonical content violates a structural invariant."""


def validate_canonical_against_source(
    canonical: CanonicalContent, prepared: PreparedSource
) -> None:
    """Validate canonical content against its prepared source; raise loudly."""
    if canonical.source.sha256 != prepared.metadata.sha256:
        raise CanonicalValidationError(
            "canonical source SHA-256 digest does not match prepared source digest"
        )
    if canonical.source.character_count != prepared.metadata.character_count:
        raise CanonicalValidationError(
            "canonical source character_count does not match prepared source count"
        )
    if prepared.metadata.character_count != len(prepared.normalized_text):
        raise CanonicalValidationError(
            "prepared source character_count does not match normalized text length"
        )
    if sha256_hex(prepared.normalized_text) != prepared.metadata.sha256:
        raise CanonicalValidationError(
            "prepared source SHA-256 digest does not match normalized text"
        )
    canonical_ids = [segment.id for segment in canonical.segments]
    if len(canonical_ids) != len(set(canonical_ids)):
        raise CanonicalValidationError("duplicate segment IDs in canonical content")
    prepared_ids = [segment.id for segment in prepared.segments]
    if len(prepared_ids) != len(set(prepared_ids)):
        raise CanonicalValidationError("duplicate segment IDs in prepared source")

    if canonical.source.segment_count != len(canonical.segments):
        raise CanonicalValidationError(
            "canonical source segment_count does not match segment catalog length"
        )

    if [segment.order for segment in canonical.segments] != list(
        range(len(canonical.segments))
    ):
        raise CanonicalValidationError("segment ordering is not deterministic 0..n-1")
    ordered = sorted(canonical.segments, key=lambda s: s.order)
    for first, second in zip(ordered, ordered[1:], strict=False):
        if not first.start_offset < second.start_offset:
            raise CanonicalValidationError("segment ordering is not source-relative")

    for segment in canonical.segments:
        if not 0 <= segment.start_offset < segment.end_offset:
            raise CanonicalValidationError(
                f"invalid segment offsets for {segment.id}: offsets must satisfy "
                "0 <= start < end"
            )
        if segment.end_offset > canonical.source.character_count:
            raise CanonicalValidationError(
                f"invalid segment offsets for {segment.id}: end exceeds character_count"
            )
        expected = prepared.normalized_text[segment.start_offset : segment.end_offset]
        if segment.text != expected:
            raise CanonicalValidationError(
                f"segment text does not match source slice for {segment.id}"
            )

    prepared_by_order = sorted(prepared.segments, key=lambda s: s.order)
    if len(canonical.segments) != len(prepared_by_order) or any(
        c != p for c, p in zip(ordered, prepared_by_order, strict=True)
    ):
        raise CanonicalValidationError(
            "canonical segment catalog does not match prepared source catalog"
        )

    valid_ids = set(prepared_ids)
    for claim in canonical.all_claims():
        for reference in claim.evidence:
            if reference.segment_id not in valid_ids:
                raise CanonicalValidationError(
                    "evidence reference points to unknown segment ID "
                    f"{reference.segment_id}"
                )
        if claim.status == ProvenanceStatus.OBSERVED and len(claim.evidence) == 0:
            raise CanonicalValidationError("OBSERVED claim requires evidence reference")
