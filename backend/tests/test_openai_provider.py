"""Phase 2B OpenAI adapter tests (fake SDK client only, no network/tokens)."""

from __future__ import annotations

import httpx2
import openai
import pytest

from app.models.analysis import CanonicalSemanticAnalysis
from app.models.canonical import EvidenceReference, ProvenancedClaim
from app.models.common import ProvenanceStatus
from app.services.analysis_providers import (
    ProviderAuthenticationError,
    ProviderInvalidResponseError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from app.services.source_preparation import prepare_source

SOURCE_TEXT = "Project Aurora update.\n\nSecond paragraph with 12 October 2026.\n"


class FakeParsedResponse:
    def __init__(self, parsed, model=None) -> None:
        self.output_parsed = parsed
        self.model = model


class FakeResponsesNamespace:
    def __init__(self, result=None, error=None) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.result


class FakeClient:
    def __init__(self, namespace) -> None:
        self.responses = namespace


def _provider(namespace, model="test-model-x"):
    from app.services.openai_provider import OpenAIAnalysisProvider  # noqa: E402

    return OpenAIAnalysisProvider(
        api_key="test-key",
        model=model,
        client=FakeClient(namespace),
    )


def _valid_parsed(prepared):
    first_id = prepared.segments[0].id
    return CanonicalSemanticAnalysis(
        facts=[
            ProvenancedClaim(
                text="Aurora noted.",
                status=ProvenanceStatus.OBSERVED,
                evidence=[EvidenceReference(segment_id=first_id)],
            )
        ]
    )


def test_responses_parse_is_invoked():
    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_valid_parsed(prepared)))
    provider = _provider(namespace)
    provider.analyze(prepared)
    assert len(namespace.calls) == 1
    assert "parse" in dir(FakeClient(namespace).responses)


def test_text_format_is_semantic_schema():
    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_valid_parsed(prepared)))
    _provider(namespace).analyze(prepared)
    assert namespace.calls[0]["text_format"] is CanonicalSemanticAnalysis


def test_requested_model_passed_exactly():
    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_valid_parsed(prepared)))
    _provider(namespace, model="test-model-x").analyze(prepared)
    assert namespace.calls[0]["model"] == "test-model-x"


def test_source_segments_supplied_as_untrusted_input():
    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_valid_parsed(prepared)))
    _provider(namespace).analyze(prepared)
    assert prepared.segments[0].id in str(namespace.calls[0]["input"])


def test_trusted_instructions_passed_separately_from_source():
    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_valid_parsed(prepared)))
    _provider(namespace).analyze(prepared)
    assert "instructions" in namespace.calls[0]
    assert namespace.calls[0]["instructions"] != namespace.calls[0]["input"]


def test_parsed_output_used_directly():
    prepared = prepare_source(SOURCE_TEXT)
    parsed = _valid_parsed(prepared)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(parsed))
    result = _provider(namespace).analyze(prepared)
    assert result.semantic_analysis == parsed


def test_reported_model_preserved_when_present():
    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(
        result=FakeParsedResponse(_valid_parsed(prepared), model="openai-reported-1")
    )
    result = _provider(namespace).analyze(prepared)
    assert result.provider_reported_model == "openai-reported-1"


def test_absent_reported_model_is_none():
    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_valid_parsed(prepared)))
    result = _provider(namespace).analyze(prepared)
    assert result.provider_reported_model is None
    assert result.requested_model == "test-model-x"


def test_refusal_is_controlled_failure():
    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(None))
    with pytest.raises(ProviderInvalidResponseError):
        _provider(namespace).analyze(prepared)


def test_sdk_timeout_is_controlled_failure():
    prepared = prepare_source(SOURCE_TEXT)
    error = openai.APITimeoutError(request=httpx2.Request("POST", "https://x.test"))
    namespace = FakeResponsesNamespace(error=error)
    with pytest.raises(ProviderTimeoutError):
        _provider(namespace).analyze(prepared)


def test_sdk_auth_error_is_controlled_failure():
    prepared = prepare_source(SOURCE_TEXT)
    response = httpx2.Response(401, request=httpx2.Request("POST", "https://x.test"))
    error = openai.AuthenticationError("bad key", response=response, body=None)
    namespace = FakeResponsesNamespace(error=error)
    with pytest.raises(ProviderAuthenticationError):
        _provider(namespace).analyze(prepared)


def test_sdk_rate_limit_is_controlled_failure():
    prepared = prepare_source(SOURCE_TEXT)
    response = httpx2.Response(429, request=httpx2.Request("POST", "https://x.test"))
    error = openai.RateLimitError("limited", response=response, body=None)
    namespace = FakeResponsesNamespace(error=error)
    with pytest.raises(ProviderRateLimitError):
        _provider(namespace).analyze(prepared)
