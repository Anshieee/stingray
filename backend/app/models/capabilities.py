from typing import Literal

from pydantic import BaseModel, Field

from app.models.common import OutputType, ProvenanceStatus


class TransformationCapability(BaseModel):
    output_type: OutputType
    implemented: Literal[False] = Field(
        description="Always false in Phase 0: a defined output is not an available transformation."
    )


class CapabilitiesResponse(BaseModel):
    transformations: list[TransformationCapability]
    provenance_statuses: list[ProvenanceStatus] = Field(
        description="Defined provenance vocabulary; source analysis is not implemented."
    )
