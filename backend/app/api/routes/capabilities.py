from fastapi import APIRouter

from app.models.capabilities import CapabilitiesResponse, TransformationCapability
from app.models.common import OutputType, ProvenanceStatus

router = APIRouter(tags=["capabilities"])


@router.get("/capabilities", response_model=CapabilitiesResponse)
def capabilities() -> CapabilitiesResponse:
    """List defined transformation identifiers, availability, and provenance vocabulary."""
    return CapabilitiesResponse(
        transformations=[
            TransformationCapability(output_type=output_type, implemented=False)
            for output_type in OutputType
        ],
        provenance_statuses=list(ProvenanceStatus),
    )
