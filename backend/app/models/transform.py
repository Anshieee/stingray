from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.common import OutputType, SourceType, TransformationMode

MAX_SOURCE_TEXT_LENGTH = 10_000


class SourceInput(BaseModel):
    type: SourceType
    text: str = Field(
        min_length=1,
        max_length=MAX_SOURCE_TEXT_LENGTH,
        description="Plain text source; Phase 1 accepts at most 10,000 characters.",
    )

    @field_validator("text")
    @classmethod
    def text_must_contain_non_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source.text must contain non-whitespace text")
        return value


class GenerationControls(BaseModel):
    target_audience: str | None = None
    tone: str | None = None
    language: str | None = None
    detail_level: str | None = None
    communication_objective: str | None = None
    content_style: str | None = None


class TransformRequest(BaseModel):
    source: SourceInput
    outputs: list[OutputType] = Field(min_length=1)
    controls: GenerationControls


class TransformArtifact(BaseModel):
    output_type: Literal["executive_summary"]
    content: str


class TransformResponse(BaseModel):
    status: Literal["ok"]
    mode: TransformationMode
    artifacts: list[TransformArtifact] = Field(min_length=1, max_length=1)
    warnings: list[str]
