from typing import Literal

from pydantic import BaseModel, Field

from app.models.common import OutputType, ProvenanceStatus, TransformationMode


class TransformationCapability(BaseModel):
    output_type: OutputType
    implemented: Literal[False] = Field(
        description="Always false: a deterministic stub is not real transformation support."
    )
    stub_available: bool = Field(
        description="Whether a clearly labeled non-AI integration stub is available."
    )
    stub_mode: TransformationMode | None = Field(
        description="The explicit mode used by an available stub, if any."
    )


class CapabilitiesResponse(BaseModel):
    transformations: list[TransformationCapability]
    provenance_statuses: list[ProvenanceStatus] = Field(
        description="Defined provenance vocabulary; source analysis is not implemented."
    )
