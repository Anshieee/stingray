"""Deterministic source ingestion: external input -> text for prepare_source().

TEXT passes submitted text through unchanged. PDF extracts text-bearing pages
in document order with pypdf (in-memory BytesIO only; filenames are untrusted
display text, never filesystem paths). No OCR: scanned/image-only PDFs are
rejected honestly. Embedded PDF document metadata is never treated as content.
"""

from __future__ import annotations

from io import BytesIO

from pydantic import BaseModel, Field

from app.models.common import SourceType
from app.models.transform import MAX_SOURCE_TEXT_LENGTH
from app.services.source_preparation import normalize_source_text

# Hackathon-safe upload bound, enforced before expensive parsing.
MAX_PDF_BYTES = 10 * 1024 * 1024

# Deterministic page separator for flattened PDF text.
PAGE_SEPARATOR = "\n\n"


class InvalidPdfError(ValueError):
    """Bytes are empty, malformed, or not actually a PDF."""


class PdfTooLargeError(ValueError):
    """Upload exceeds MAX_PDF_BYTES."""


class PdfNoExtractableTextError(ValueError):
    """Valid PDF with no meaningful extractable text (OCR not implemented)."""


class ExtractedTextTooLargeError(ValueError):
    """Flattened text exceeds the downstream analysis text policy."""


class IngestedSource(BaseModel):
    """Deterministic ingestion output; feeds prepare_source(), not canonical."""

    source_type: SourceType
    text: str = Field(min_length=1)
    filename: str | None = None
    page_count: int | None = Field(default=None, ge=1)


class TextSourceIngestor:
    """Pass submitted text through as a TEXT ingested source."""

    def ingest_text(self, text: str) -> IngestedSource:
        return IngestedSource(source_type=SourceType.TEXT, text=text)


class PdfSourceIngestor:
    """Extract text-bearing PDF pages deterministically, in memory only."""

    def __init__(self, max_bytes: int = MAX_PDF_BYTES) -> None:
        self._max_bytes = max_bytes

    def ingest_bytes(self, data: bytes, filename: str | None = None) -> IngestedSource:
        if len(data) == 0:
            raise InvalidPdfError("Uploaded file is empty; not a valid PDF.")
        if len(data) > self._max_bytes:
            raise PdfTooLargeError(
                f"PDF exceeds the {self._max_bytes}-byte upload limit."
            )
        try:
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(data))
            page_texts = [page.extract_text() or "" for page in reader.pages]
            total_pages = len(reader.pages)
        except Exception as error:
            raise InvalidPdfError("Input could not be parsed as a PDF.") from error
        if total_pages == 0:
            raise InvalidPdfError("PDF contains no pages.")
        flattened = PAGE_SEPARATOR.join(
            cleaned for page in page_texts if (cleaned := normalize_source_text(page).strip())
        )
        if not flattened.strip():
            raise PdfNoExtractableTextError(
                "PDF contains no extractable text; scanned/image-only PDF OCR "
                "is not yet implemented."
            )
        if len(flattened) > MAX_SOURCE_TEXT_LENGTH:
            raise ExtractedTextTooLargeError(
                "Extracted PDF text exceeds the "
                f"{MAX_SOURCE_TEXT_LENGTH}-character analysis limit; "
                "long-document chunking is not yet implemented."
            )
        return IngestedSource(
            source_type=SourceType.PDF,
            text=flattened,
            filename=filename,
            page_count=total_pages,
        )
