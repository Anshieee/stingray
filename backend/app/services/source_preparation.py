"""Deterministic plain-text source preparation (Phase 2A, no AI).

Normalization contract:
1. CRLF (\\r\\n) becomes LF (\\n).
2. Remaining standalone CR (\\r) becomes LF (\\n).
3. All other characters are preserved exactly (no lowercasing, no whitespace
   collapsing, no Unicode rewriting, no punctuation changes).
"""

from __future__ import annotations

import hashlib

from app.models.canonical import PreparedSource, SourceMetadata, SourceSegment
from app.models.common import SourceType
from app.models.transform import MAX_SOURCE_TEXT_LENGTH

# Fixed oracle fixture shared with tests (literal, not computed).
RAW_ORACLE_FIXTURE = "Alpha\r\n\r\nBeta line one.\r\nBeta line two.\r\n"

_EMPTY_MESSAGE = "source.text must contain non-whitespace text"


def normalize_source_text(raw: str) -> str:
    """Apply the Phase 2A line-ending normalization contract."""
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def sha256_hex(normalized_text: str) -> str:
    """Return SHA-256 hex of UTF-8 encoded normalized text (stdlib only)."""
    return hashlib.sha256(normalized_text.encode()).hexdigest()


def segment_id_for(order: int, start: int, end: int, text: str) -> str:
    """Derive a stable deterministic segment ID (no randomness/timestamps)."""
    digest = hashlib.sha256(f"{order}:{start}:{end}:{text}".encode()).hexdigest()
    return f"seg-{order:04d}-{digest[:12]}"


def _segment_spans(normalized: str) -> list[tuple[str, int, int]]:
    """Split normalized text into paragraph spans (text, start, end)."""
    lines: list[tuple[int, str, int]] = []
    index = 0
    length = len(normalized)
    while index < length:
        newline = normalized.find("\n", index)
        if newline == -1:
            lines.append((index, normalized[index:], length))
            break
        lines.append((index, normalized[index:newline], newline + 1))
        index = newline + 1

    groups: list[list[tuple[int, str, int]]] = []
    current: list[tuple[int, str, int]] = []
    for line_start, content, _line_end in lines:
        if content.strip() == "":
            if current:
                groups.append(current)
                current = []
            continue
        current.append((line_start, content, line_start + len(content)))
    if current:
        groups.append(current)

    spans: list[tuple[str, int, int]] = []
    for group in groups:
        start = group[0][0]
        end = group[-1][2]
        spans.append((normalized[start:end], start, end))
    return spans


def prepare_source(raw: str, source_type: SourceType = SourceType.TEXT) -> PreparedSource:
    """Normalize, hash, count and deterministically segment raw source text."""
    if not raw.strip():
        raise ValueError(_EMPTY_MESSAGE)
    if len(raw) > MAX_SOURCE_TEXT_LENGTH:
        raise ValueError(
            f"source text exceeds {MAX_SOURCE_TEXT_LENGTH} characters; input rejected"
        )
    normalized = normalize_source_text(raw)
    if not normalized.strip():
        raise ValueError(_EMPTY_MESSAGE)
    digest = sha256_hex(normalized)
    character_count = len(normalized)
    spans = _segment_spans(normalized)
    if not spans:
        raise ValueError(_EMPTY_MESSAGE)
    segments = [
        SourceSegment(
            id=segment_id_for(order, start, end, text),
            order=order,
            text=text,
            start_offset=start,
            end_offset=end,
        )
        for order, (text, start, end) in enumerate(spans)
    ]
    metadata = SourceMetadata(
        source_type=source_type,
        sha256=digest,
        character_count=character_count,
        segment_count=len(segments),
    )
    return PreparedSource(normalized_text=normalized, metadata=metadata, segments=segments)
