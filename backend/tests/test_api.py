import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
    assert set(schema["paths"]) == {"/health", "/api/v1/capabilities"}
    for path in schema["paths"].values():
        assert "200" in path["get"]["responses"]
    assert set(schema["components"]["schemas"]["ProvenanceStatus"]["enum"]) == {
        "OBSERVED", "INFERRED", "UNKNOWN", "NOT_APPLICABLE"
    }
