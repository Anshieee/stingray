"""FreeLLMAPI auto-router provider tests (fake clients only, no network/tokens)."""

from __future__ import annotations

import pytest

from app.models.analysis import CanonicalSemanticAnalysis
from app.models.canonical import EvidenceReference, ProvenancedClaim
from app.models.common import ProvenanceStatus
from app.services.analysis_providers import ProviderNotConfigured
from app.services.source_preparation import prepare_source

SOURCE_TEXT = "Project Aurora update.\n\nSecond paragraph.\n"
FAKE_KEY = "test-key"


class FakeParsedResponse:
    def __init__(self, parsed, model=None) -> None:
        self.output_parsed = parsed
        self.model = model


class FakeResponsesNamespace:
    def __init__(self, result=None) -> None:
        self.result = result
        self.calls: list[dict] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class FakeClient:
    def __init__(self, namespace) -> None:
        self.responses = namespace


class CapturingClientFactory:
    """Records OpenAI-compatible client construction kwargs without networking."""

    def __init__(self, namespace) -> None:
        self.namespace = namespace
        self.kwargs: dict | None = None

    def __call__(self, **kwargs):
        self.kwargs = kwargs
        return FakeClient(self.namespace)


def _semantic(prepared):
    return CanonicalSemanticAnalysis(
        facts=[
            ProvenancedClaim(
                text="Aurora noted.",
                status=ProvenanceStatus.OBSERVED,
                evidence=[EvidenceReference(segment_id=prepared.segments[0].id)],
            )
        ]
    )


def test_freellmapi_selected_from_environment(monkeypatch):
    from app.services.analysis_config import provider_from_environment

    monkeypatch.setenv("AI_PROVIDER", "freellmapi")
    monkeypatch.setenv("FREELLMAPI_API_KEY", FAKE_KEY)
    monkeypatch.setenv("FREELLMAPI_MODEL", "auto")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = provider_from_environment()
    assert provider._provider_name == "freellmapi"


def test_freellmapi_key_and_model_read_from_env(monkeypatch):
    from app.services.analysis_config import provider_from_environment

    monkeypatch.setenv("AI_PROVIDER", "freellmapi")
    monkeypatch.setenv("FREELLMAPI_API_KEY", FAKE_KEY)
    monkeypatch.setenv("FREELLMAPI_MODEL", "auto")
    provider = provider_from_environment()
    assert provider._api_key == FAKE_KEY
    assert provider._model == "auto"


def test_freellmapi_base_url_passed_to_client(monkeypatch):
    from app.services.analysis_config import provider_from_environment

    monkeypatch.setenv("AI_PROVIDER", "freellmapi")
    monkeypatch.setenv("FREELLMAPI_API_KEY", FAKE_KEY)
    monkeypatch.setenv("FREELLMAPI_MODEL", "auto")
    monkeypatch.setenv("FREELLMAPI_BASE_URL", "http://localhost:3001/v1")
    provider = provider_from_environment()
    assert provider._base_url == "http://localhost:3001/v1"


def test_freellmapi_default_base_url_is_local_router(monkeypatch):
    from app.services.analysis_config import (
        DEFAULT_FREELLMAPI_BASE_URL,
        provider_from_environment,
    )

    monkeypatch.setenv("AI_PROVIDER", "freellmapi")
    monkeypatch.setenv("FREELLMAPI_API_KEY", FAKE_KEY)
    monkeypatch.setenv("FREELLMAPI_MODEL", "auto")
    monkeypatch.delenv("FREELLMAPI_BASE_URL", raising=False)
    provider = provider_from_environment()
    assert provider._base_url == DEFAULT_FREELLMAPI_BASE_URL == "http://localhost:3001/v1"


def test_configured_router_auto_passed_unchanged():
    from app.services.openai_provider import OpenAICompatibleAnalysisProvider

    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_semantic(prepared)))
    provider = OpenAICompatibleAnalysisProvider(
        api_key=FAKE_KEY,
        model="auto",
        provider="freellmapi",
        base_url="http://localhost:3001/v1",
        client=FakeClient(namespace),
    )
    provider.analyze(prepared)
    assert namespace.calls[0]["model"] == "auto"


def test_application_provider_identity_is_freellmapi():
    from app.services.openai_provider import OpenAICompatibleAnalysisProvider

    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_semantic(prepared)))
    provider = OpenAICompatibleAnalysisProvider(
        api_key=FAKE_KEY,
        model="auto",
        provider="freellmapi",
        base_url="http://localhost:3001/v1",
        client=FakeClient(namespace),
    )
    result = provider.analyze(prepared)
    assert result.provider == "freellmapi"
    assert result.requested_model == "auto"


def test_reported_model_not_fabricated():
    from app.services.openai_provider import OpenAICompatibleAnalysisProvider

    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_semantic(prepared)))
    provider = OpenAICompatibleAnalysisProvider(
        api_key=FAKE_KEY,
        model="auto",
        provider="freellmapi",
        base_url="http://localhost:3001/v1",
        client=FakeClient(namespace),
    )
    result = provider.analyze(prepared)
    assert result.provider_reported_model is None


def test_structured_text_format_and_parse_path():
    from app.services.openai_provider import OpenAICompatibleAnalysisProvider

    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_semantic(prepared)))
    OpenAICompatibleAnalysisProvider(
        api_key=FAKE_KEY,
        model="auto",
        provider="freellmapi",
        base_url="http://localhost:3001/v1",
        client=FakeClient(namespace),
    ).analyze(prepared)
    assert len(namespace.calls) == 1
    assert namespace.calls[0]["text_format"] is CanonicalSemanticAnalysis


def test_trusted_instructions_separate_from_source_input():
    from app.services.openai_provider import OpenAICompatibleAnalysisProvider

    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_semantic(prepared)))
    OpenAICompatibleAnalysisProvider(
        api_key=FAKE_KEY,
        model="auto",
        provider="freellmapi",
        base_url="http://localhost:3001/v1",
        client=FakeClient(namespace),
    ).analyze(prepared)
    assert "instructions" in namespace.calls[0]
    assert prepared.segments[0].id in str(namespace.calls[0]["input"])
    assert namespace.calls[0]["instructions"] != namespace.calls[0]["input"]


def test_server_identity_unchanged_through_provider():
    from app.services.analysis import analyze_source
    from app.services.openai_provider import OpenAICompatibleAnalysisProvider

    prepared = prepare_source(SOURCE_TEXT)
    namespace = FakeResponsesNamespace(result=FakeParsedResponse(_semantic(prepared)))
    provider = OpenAICompatibleAnalysisProvider(
        api_key=FAKE_KEY,
        model="auto",
        provider="freellmapi",
        base_url="http://localhost:3001/v1",
        client=FakeClient(namespace),
    )
    outcome = analyze_source(SOURCE_TEXT, provider)
    assert outcome.canonical.source.sha256 == prepared.metadata.sha256
    assert [s.id for s in outcome.canonical.segments] == [s.id for s in prepared.segments]


def test_missing_freellmapi_key_is_not_configured(monkeypatch):
    from app.services.analysis_config import provider_from_environment

    monkeypatch.setenv("AI_PROVIDER", "freellmapi")
    monkeypatch.delenv("FREELLMAPI_API_KEY", raising=False)
    monkeypatch.setenv("FREELLMAPI_MODEL", "auto")
    with pytest.raises(ProviderNotConfigured):
        provider_from_environment()


def test_missing_freellmapi_model_is_not_configured(monkeypatch):
    from app.services.analysis_config import provider_from_environment

    monkeypatch.setenv("AI_PROVIDER", "freellmapi")
    monkeypatch.setenv("FREELLMAPI_API_KEY", FAKE_KEY)
    monkeypatch.delenv("FREELLMAPI_MODEL", raising=False)
    with pytest.raises(ProviderNotConfigured):
        provider_from_environment()


def test_direct_openai_still_supported(monkeypatch):
    from app.services.analysis_config import provider_from_environment

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_KEY)
    monkeypatch.setenv("OPENAI_MODEL", "test-openai-model")
    provider = provider_from_environment()
    assert provider._provider_name == "openai"
    assert provider._base_url is None


def test_unsupported_provider_fails_honestly(monkeypatch):
    from app.services.analysis_config import provider_from_environment

    monkeypatch.setenv("AI_PROVIDER", "other-provider")
    with pytest.raises(ProviderNotConfigured):
        provider_from_environment()


def test_strict_nested_schema_retained():
    schema = CanonicalSemanticAnalysis.model_json_schema()
    assert schema.get("additionalProperties") is False
    definitions = schema.get("$defs", {})
    assert definitions["ProvenancedClaim"].get("additionalProperties") is False
    assert definitions["EvidenceReference"].get("additionalProperties") is False
