from app.models.common import OutputType, TransformationMode
from app.models.transform import TransformArtifact, TransformRequest, TransformResponse

STUB_WARNINGS = [
    "Deterministic integration stub only; no AI model was used.",
    "Generation controls are modeled but are not applied by this stub.",
]
STUB_INTRO = (
    "This is deterministic integration scaffolding, not an AI-generated executive summary."
)
MAX_EXCERPT_LENGTH = 280


class UnsupportedTransformRequest(ValueError):
    """Raised when a typed request is valid but outside the Phase 1 slice."""


def transform_request(request: TransformRequest) -> TransformResponse:
    """Return a stable, bounded echo for the one supported Phase 1 output."""
    if request.outputs != [OutputType.EXECUTIVE_SUMMARY]:
        raise UnsupportedTransformRequest(
            "Phase 1 supports only the executive_summary output through a deterministic stub"
        )

    normalized_text = " ".join(request.source.text.split())
    excerpt = normalized_text[:MAX_EXCERPT_LENGTH]
    if len(normalized_text) > MAX_EXCERPT_LENGTH:
        excerpt += "…"
    content = f"[DETERMINISTIC STUB]\n{STUB_INTRO}\nSource excerpt: {excerpt}"

    return TransformResponse(
        status="ok",
        mode=TransformationMode.DETERMINISTIC_STUB,
        artifacts=[TransformArtifact(output_type="executive_summary", content=content)],
        warnings=STUB_WARNINGS,
    )
