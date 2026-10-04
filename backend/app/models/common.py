from enum import StrEnum


class OutputType(StrEnum):
    VIDEO_PACKAGE = "video_package"
    LINKEDIN_POST = "linkedin_post"
    X_POST = "x_post"
    ADVISORY = "advisory"
    INFOGRAPHIC = "infographic"
    EXECUTIVE_SUMMARY = "executive_summary"
    PRESENTATION = "presentation"


class SourceType(StrEnum):
    TEXT = "text"


class TransformationMode(StrEnum):
    DETERMINISTIC_STUB = "DETERMINISTIC_STUB"


class ProvenanceStatus(StrEnum):
    """Source support semantics, independent of output type or confidence."""

    OBSERVED = "OBSERVED"  # Explicit source support; requires future EvidenceReference.
    INFERRED = "INFERRED"  # System interpretation or creative material, not a source fact.
    UNKNOWN = "UNKNOWN"  # Evidence is absent or cannot be determined.
    NOT_APPLICABLE = "NOT_APPLICABLE"  # The field does not logically apply.
