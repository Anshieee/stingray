"""Phase 2A source-preparation tests (normalization + segmentation oracle)."""

from __future__ import annotations

RAW_ORACLE = "Alpha\r\n\r\nBeta line one.\r\nBeta line two.\r\n"
NORMALIZED_ORACLE = "Alpha\n\nBeta line one.\nBeta line two.\n"
ORACLE_CHAR_COUNT = 37
ORACLE_SHA256 = "0496469bec58feb6eb0d7b607d38f4d8afb348410b8f96fbfe8605d12d348e69"


def test_crlf_normalizes_to_lf():
    from app.services.source_preparation import normalize_source_text

    assert normalize_source_text("a\r\nb") == "a\nb"


def test_standalone_cr_normalizes_to_lf():
    from app.services.source_preparation import normalize_source_text

    assert normalize_source_text("a\rb") == "a\nb"


def test_other_content_remains_unchanged():
    from app.services.source_preparation import normalize_source_text

    raw = "  Alpha\t  Beta  \u00e9  \u2014  end"
    assert normalize_source_text(raw) == raw


def test_normalization_is_deterministic():
    from app.services.source_preparation import normalize_source_text

    raw = "x\r\ny\r★\r\n"
    assert normalize_source_text(raw) == normalize_source_text(raw)


def test_fixed_oracle_character_count():
    from app.services.source_preparation import normalize_source_text

    normalized = normalize_source_text(RAW_ORACLE)
    assert normalized == NORMALIZED_ORACLE
    assert len(normalized) == ORACLE_CHAR_COUNT == 37


def test_fixed_oracle_sha256():
    from app.services.source_preparation import normalize_source_text, sha256_hex

    normalized = normalize_source_text(RAW_ORACLE)
    assert sha256_hex(normalized) == ORACLE_SHA256


def test_fixed_oracle_produces_exactly_two_segments():
    from app.services.source_preparation import prepare_source

    prepared = prepare_source(RAW_ORACLE)
    assert len(prepared.segments) == 2


def test_oracle_segment_one_text_and_offsets():
    from app.services.source_preparation import prepare_source

    prepared = prepare_source(RAW_ORACLE)
    first = sorted(prepared.segments, key=lambda s: s.order)[0]
    assert first.text == "Alpha"
    assert first.start_offset == 0
    assert first.end_offset == 5


def test_oracle_segment_two_text_and_offsets():
    from app.services.source_preparation import prepare_source

    prepared = prepare_source(RAW_ORACLE)
    second = sorted(prepared.segments, key=lambda s: s.order)[1]
    assert second.text == "Beta line one.\nBeta line two."
    assert second.start_offset == 7
    assert second.end_offset == 36


def test_segments_slice_source_exactly():
    from app.services.source_preparation import prepare_source

    prepared = prepare_source(RAW_ORACLE)
    for segment in prepared.segments:
        assert prepared.normalized_text[segment.start_offset : segment.end_offset] == segment.text


def test_repeated_preparation_gives_identical_ids_and_metadata():
    from app.services.source_preparation import prepare_source

    first = prepare_source(RAW_ORACLE)
    second = prepare_source(RAW_ORACLE)
    assert [s.id for s in first.segments] == [s.id for s in second.segments]
    assert first.metadata.sha256 == second.metadata.sha256
    assert first.metadata.character_count == second.metadata.character_count
    assert first.normalized_text == second.normalized_text


def test_segment_ids_unique_within_source():
    from app.services.source_preparation import prepare_source

    prepared = prepare_source(RAW_ORACLE)
    ids = [s.id for s in prepared.segments]
    assert len(ids) == len(set(ids))


def test_whitespace_separators_do_not_become_segments():
    from app.services.source_preparation import prepare_source

    prepared = prepare_source("Alpha\n\n\n   \n\t\nBeta\n")
    texts = [s.text for s in prepared.segments]
    assert texts == ["Alpha", "Beta"]
    for segment in prepared.segments:
        assert segment.text.strip() != ""


def test_empty_source_rejected_with_existing_semantics():
    import pytest

    from app.services.source_preparation import prepare_source

    with pytest.raises(ValueError, match="non-whitespace"):
        prepare_source(" \n\t ")
    with pytest.raises(ValueError, match="non-whitespace"):
        prepare_source("")
