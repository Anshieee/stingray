import pytest
from fastapi.testclient import TestClient

from app.main import create_app

VALID_TRANSFORM_REQUEST = {
    "source": {
        "type": "text",
        "text": "The organization announced Project Aurora on 4 October 2026.",
    },
    "outputs": ["executive_summary"],
    "controls": {
        "target_audience": None,
        "tone": None,
        "language": None,
        "detail_level": None,
        "communication_objective": None,
        "content_style": None,
    },
}


@pytest.fixture
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_local_frontend_origin_is_allowed_to_call_transform(client):
    response = client.options(
        "/api/v1/transform",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_capabilities_define_exactly_seven_unimplemented_outputs(client):
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    transformations = response.json()["transformations"]
    assert len(transformations) == 7
    assert {item["output_type"] for item in transformations} == {
        "video_package",
        "linkedin_post",
        "x_post",
        "advisory",
        "infographic",
        "executive_summary",
        "presentation",
    }
    assert all(item["implemented"] is False for item in transformations)


def test_provenance_vocabulary(client):
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    statuses = response.json()["provenance_statuses"]
    assert len(statuses) == 4
    assert set(statuses) == {"OBSERVED", "INFERRED", "UNKNOWN", "NOT_APPLICABLE"}


def test_generated_openapi_documents_current_contract(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert set(schema["paths"]) == {
        "/health",
        "/api/v1/capabilities",
        "/api/v1/transform",
        "/api/v1/analyze",
        "/api/v1/analyze/pdf",
    }
    assert "200" in schema["paths"]["/health"]["get"]["responses"]
    assert "200" in schema["paths"]["/api/v1/capabilities"]["get"]["responses"]
    assert "200" in schema["paths"]["/api/v1/transform"]["post"]["responses"]
    assert "200" in schema["paths"]["/api/v1/analyze"]["post"]["responses"]
    assert "200" in schema["paths"]["/api/v1/analyze/pdf"]["post"]["responses"]
    assert (
        "multipart/form-data"
        in schema["paths"]["/api/v1/analyze/pdf"]["post"]["requestBody"]["content"]
    )
    assert "TransformRequest" in schema["components"]["schemas"]
    assert "TransformResponse" in schema["components"]["schemas"]
    assert "AnalyzeRequest" in schema["components"]["schemas"]
    assert "AnalyzeResponse" in schema["components"]["schemas"]
    assert set(schema["components"]["schemas"]["ProvenanceStatus"]["enum"]) == {
        "OBSERVED", "INFERRED", "UNKNOWN", "NOT_APPLICABLE"
    }


def test_valid_transform_returns_one_deterministic_executive_summary(client):
    response = client.post("/api/v1/transform", json=VALID_TRANSFORM_REQUEST)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["mode"] == "DETERMINISTIC_STUB"
    assert len(body["artifacts"]) == 1
    assert body["artifacts"][0]["output_type"] == "executive_summary"
    assert body["artifacts"][0]["content"].startswith("[DETERMINISTIC STUB]")
    assert "Project Aurora" in body["artifacts"][0]["content"]
    assert body["warnings"]


def test_repeated_transform_is_semantically_deterministic(client):
    first = client.post("/api/v1/transform", json=VALID_TRANSFORM_REQUEST)
    second = client.post("/api/v1/transform", json=VALID_TRANSFORM_REQUEST)
    assert first.status_code == second.status_code == 200
    assert first.json()["artifacts"] == second.json()["artifacts"]


def test_whitespace_only_text_is_rejected(client):
    request = {**VALID_TRANSFORM_REQUEST, "source": {"type": "text", "text": " \n\t "}}
    response = client.post("/api/v1/transform", json=request)
    assert response.status_code == 422


def test_unsupported_source_type_is_rejected(client):
    request = {**VALID_TRANSFORM_REQUEST, "source": {"type": "image", "text": "input"}}
    response = client.post("/api/v1/transform", json=request)
    assert response.status_code == 422


def test_zero_outputs_are_rejected(client):
    request = {**VALID_TRANSFORM_REQUEST, "outputs": []}
    response = client.post("/api/v1/transform", json=request)
    assert response.status_code == 422


def test_unsupported_output_is_rejected_in_phase_one(client):
    request = {**VALID_TRANSFORM_REQUEST, "outputs": ["linkedin_post"]}
    response = client.post("/api/v1/transform", json=request)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert isinstance(errors, str)
    assert "executive_summary" in errors


def test_over_limit_text_is_rejected_without_truncation(client):
    request = {
        **VALID_TRANSFORM_REQUEST,
        "source": {"type": "text", "text": "x" * 10_001},
    }
    response = client.post("/api/v1/transform", json=request)
    assert response.status_code == 422


def test_capabilities_mark_stub_without_claiming_real_implementation(client):
    response = client.get("/api/v1/capabilities")
    executive_summary = next(
        item for item in response.json()["transformations"]
        if item["output_type"] == "executive_summary"
    )
    assert executive_summary["implemented"] is False
    assert executive_summary["stub_available"] is True
    assert executive_summary["stub_mode"] == "DETERMINISTIC_STUB"


@pytest.mark.parametrize("outputs", [
    ["executive_summary", "executive_summary"],
    ["executive_summary", "linkedin_post"],
])
def test_multiple_outputs_are_rejected(client, outputs):
    response = client.post(
        "/api/v1/transform", json={**VALID_TRANSFORM_REQUEST, "outputs": outputs}
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


def test_source_size_is_checked_before_normalization(client):
    request = {
        **VALID_TRANSFORM_REQUEST,
        "source": {"type": "text", "text": "x" + " " * 10_000},
    }
    assert client.post("/api/v1/transform", json=request).status_code == 422
    request["source"]["text"] = "x" * 10_000
    assert client.post("/api/v1/transform", json=request).status_code == 200


def test_unrelated_origin_is_not_allowed(client):
    response = client.options(
        "/api/v1/transform",
        headers={"Origin": "https://unrelated.example", "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
