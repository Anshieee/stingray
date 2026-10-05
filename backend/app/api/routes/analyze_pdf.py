"""POST /api/v1/analyze/pdf: PDF upload into the shared analysis pipeline.

Thin route: bounded multipart read, deterministic ingestion, then the existing
analyze service. Filenames are untrusted display text, never filesystem paths;
parsing is in-memory only. Provider is never called on ingestion failure.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import JSONResponse

from app.api.routes.analyze import analysis_error_response, get_analysis_provider
from app.models.analysis import AnalysisMode, AnalyzeResponse
from app.services.analysis import analyze_ingested
from app.services.analysis_providers import AnalysisProvider
from app.services.ingestion import (
    MAX_PDF_BYTES,
    ExtractedTextTooLargeError,
    InvalidPdfError,
    PdfNoExtractableTextError,
    PdfSourceIngestor,
    PdfTooLargeError,
)

router = APIRouter(tags=["analyze"])

_READ_CHUNK_SIZE = 65536

# Content types accepted when the client supplies one; the parser is decisive.
_ACCEPTED_CONTENT_TYPES = frozenset({"application/pdf", "application/octet-stream"})

_INGESTION_ERROR_MAP: tuple[tuple[type[ValueError], int, str, str], ...] = (
    (InvalidPdfError, 400, "INVALID_PDF", "Uploaded file is not a valid PDF."),
    (
        PdfNoExtractableTextError,
        400,
        "PDF_NO_EXTRACTABLE_TEXT",
        "PDF contains no extractable text; scanned/image-only PDF OCR "
        "is not yet implemented.",
    ),
    (
        PdfTooLargeError,
        413,
        "PDF_TOO_LARGE",
        "PDF upload exceeds the file-size limit.",
    ),
    (
        ExtractedTextTooLargeError,
        413,
        "EXTRACTED_TEXT_TOO_LARGE",
        "Extracted PDF text exceeds the analysis text limit.",
    ),
)


def _ingestion_error_response(error: ValueError) -> JSONResponse | None:
    for error_type, status_code, code, message in _INGESTION_ERROR_MAP:
        if isinstance(error, error_type):
            return JSONResponse(
                status_code=status_code,
                content={"status": "error", "error": {"code": code, "message": message}},
            )
    return None


def register_pdf_error_handlers(application) -> None:
    """Handle ingestion errors raised in dependencies or endpoints."""

    for error_type, status_code, code, message in _INGESTION_ERROR_MAP:

        def _handler(
            _request: Request,
            _error: ValueError,
            _status_code: int = status_code,
            _code: str = code,
            _message: str = message,
        ) -> JSONResponse:
            return JSONResponse(
                status_code=_status_code,
                content={
                    "status": "error",
                    "error": {"code": _code, "message": _message},
                },
            )

        application.add_exception_handler(error_type, _handler)


@router.post("/analyze/pdf", response_model=AnalyzeResponse, status_code=200)
async def analyze_pdf(
    file: UploadFile = File(...),  # noqa: B008
    provider: AnalysisProvider = Depends(get_analysis_provider),  # noqa: B008
) -> AnalyzeResponse | JSONResponse:
    """Ingest one PDF upload, then run the shared analysis pipeline."""
    if file.content_type and file.content_type not in _ACCEPTED_CONTENT_TYPES:
        error = _ingestion_error_response(InvalidPdfError("content type"))
        assert error is not None
        return error
    data = bytearray()
    while True:
        chunk = await file.read(_READ_CHUNK_SIZE)
        if not chunk:
            break
        data += chunk
        if len(data) > MAX_PDF_BYTES:
            error = _ingestion_error_response(PdfTooLargeError("upload too large"))
            assert error is not None
            return error
    try:
        ingested = PdfSourceIngestor().ingest_bytes(bytes(data), filename=file.filename)
    except (InvalidPdfError, PdfNoExtractableTextError, PdfTooLargeError,
            ExtractedTextTooLargeError) as error:
        response = _ingestion_error_response(error)
        assert response is not None
        return response
    try:
        outcome = analyze_ingested(ingested, provider)
    except ValueError as error:
        response = analysis_error_response(error)
        if response is not None:
            return response
        raise
    return AnalyzeResponse(
        status="ok",
        mode=AnalysisMode.AI_STRUCTURED_ANALYSIS,
        provider=outcome.provider,
        requested_model=outcome.requested_model,
        provider_reported_model=outcome.provider_reported_model,
        canonical_content=outcome.canonical,
        warnings=[],
    )
