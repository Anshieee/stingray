"""Phase 3A ingestion tests (text + deterministic PDF extraction)."""

from __future__ import annotations

import pytest

from app.models.common import SourceType
from app.models.transform import MAX_SOURCE_TEXT_LENGTH
from app.services.ingestion import (
    ExtractedTextTooLargeError,
    InvalidPdfError,
    PdfNoExtractableTextError,
    PdfSourceIngestor,
    PdfTooLargeError,
    TextSourceIngestor,
)
from tests.pdf_fixtures import ATLAS_LINES, build_atlas_pdf, build_pdf


def test_text_ingestor_preserves_current_behavior():
    ingested = TextSourceIngestor().ingest_text("  Aurora note.  ")
    assert ingested.source_type == SourceType.TEXT
    assert ingested.text == "  Aurora note.  "
    assert ingested.filename is None
    assert ingested.page_count is None


def test_source_type_pdf_exists():
    assert SourceType.PDF == "pdf"
    assert set(SourceType) >= {"text", "pdf"}


def test_valid_simple_pdf_text_extracted():
    ingested = PdfSourceIngestor().ingest_bytes(build_atlas_pdf(), filename="atlas.pdf")
    assert ingested.source_type == SourceType.PDF
    for line in ATLAS_LINES:
        assert line in ingested.text
    assert ingested.page_count == 3


def test_page_order_is_deterministic():
    first = PdfSourceIngestor().ingest_bytes(build_atlas_pdf()).text
    second = PdfSourceIngestor().ingest_bytes(build_atlas_pdf()).text
    assert first == second
    positions = [first.index(line) for line in ATLAS_LINES]
    assert positions == sorted(positions)


def test_deterministic_page_separator():
    ingested = PdfSourceIngestor().ingest_bytes(build_atlas_pdf())
    assert ingested.text == "\n\n".join(ATLAS_LINES)


def test_repeated_ingestion_identical():
    data = build_pdf([["Alpha."], [], ["Beta."]])
    assert PdfSourceIngestor().ingest_bytes(data).text == "Alpha.\n\nBeta."
    assert (
        PdfSourceIngestor().ingest_bytes(data).text
        == PdfSourceIngestor().ingest_bytes(data).text
    )


def test_empty_bytes_rejected():
    with pytest.raises(InvalidPdfError):
        PdfSourceIngestor().ingest_bytes(b"")


def test_invalid_bytes_rejected():
    with pytest.raises(InvalidPdfError):
        PdfSourceIngestor().ingest_bytes(b"not a pdf at all")


def test_truncated_pdf_rejected():
    valid = build_atlas_pdf()
    with pytest.raises(InvalidPdfError):
        PdfSourceIngestor().ingest_bytes(valid[:len(valid) // 2])


def test_no_text_pdf_rejected():
    with pytest.raises(PdfNoExtractableTextError):
        PdfSourceIngestor().ingest_bytes(build_pdf([[]]))
    with pytest.raises(PdfNoExtractableTextError):
        PdfSourceIngestor().ingest_bytes(build_pdf([[], ["   "]]))


def test_upload_above_byte_limit_rejected():
    from app.services.ingestion import MAX_PDF_BYTES

    with pytest.raises(PdfTooLargeError):
        PdfSourceIngestor().ingest_bytes(b"x" * (MAX_PDF_BYTES + 1))


def test_extracted_text_above_limit_rejected_without_truncation():
    big_line = "y" * (MAX_SOURCE_TEXT_LENGTH + 1)
    with pytest.raises(ExtractedTextTooLargeError):
        PdfSourceIngestor().ingest_bytes(build_pdf([[big_line]]))


def test_filename_never_used_as_filesystem_path(tmp_path):
    ingested = PdfSourceIngestor().ingest_bytes(
        build_atlas_pdf(), filename="../../etc/evil.pdf"
    )
    assert ingested.filename == "../../etc/evil.pdf"
    assert list(tmp_path.iterdir()) == []


def test_no_temporary_file_required(monkeypatch):
    monkeypatch.setenv("TMPDIR", "/nonexistent-tmpdir-stringray-test")
    monkeypatch.setenv("TEMP", "/nonexistent-tmpdir-stringray-test")
    monkeypatch.setenv("TMP", "/nonexistent-tmpdir-stringray-test")
    ingested = PdfSourceIngestor().ingest_bytes(build_atlas_pdf())
    assert ATLAS_LINES[0] in ingested.text
