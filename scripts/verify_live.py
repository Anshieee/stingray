"""Verify real local HTTP services and export unmodified live OpenAPI bytes.

Run with the backend venv's Python after building the frontend. Requires POSIX
process groups and free ports 8000/3000. Logs and exports stay in ignored artifacts/.
"""

import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
from contextlib import ExitStack
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
OUTPUTS = {
    "video_package", "linkedin_post", "x_post", "advisory",
    "infographic", "executive_summary", "presentation",
}
STATUSES = {"OBSERVED", "INFERRED", "UNKNOWN", "NOT_APPLICABLE"}
FIXTURE = "The organization announced Project Aurora on 4 October 2026."
HTTP = build_opener(ProxyHandler({}))


def request(url: str, method: str = "GET", payload: dict | None = None) -> tuple[int, bytes]:
    body = None if payload is None else json.dumps(payload).encode()
    headers = {} if body is None else {"Content-Type": "application/json"}
    outgoing = Request(url, data=body, headers=headers, method=method)
    try:
        with HTTP.open(outgoing, timeout=3) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


def fetch(url: str) -> bytes:
    response_status, body = request(url)
    assert response_status == 200, f"Unexpected HTTP status for {url}: {response_status}"
    return body


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    response_status, body = request(url, method="POST", payload=payload)
    return response_status, json.loads(body)


def wait_for_server(process: subprocess.Popen, url: str) -> None:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Server exited before {url} was ready; see artifacts/*.log")
        try:
            fetch(url)
            return
        except (URLError, TimeoutError, ConnectionError):
            time.sleep(0.25)
    raise TimeoutError(f"Server did not become ready: {url}")


def stop(process: subprocess.Popen) -> None:
    # npm starts a child server: stop the owned process group, not just npm.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)


def main() -> None:
    for port in (8000, 3000):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    ARTIFACTS.mkdir(exist_ok=True)
    with ExitStack() as stack:
        backend_log = stack.enter_context((ARTIFACTS / "backend.log").open("w"))
        frontend_log = stack.enter_context((ARTIFACTS / "frontend.log").open("w"))
        backend = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--app-dir", "backend",
             "--host", "127.0.0.1", "--port", "8000"],
            cwd=ROOT, stdout=backend_log, stderr=subprocess.STDOUT, start_new_session=True,
        )
        stack.callback(stop, backend)
        frontend = subprocess.Popen(
            ["npm", "start", "--", "--port", "3000"], cwd=ROOT / "frontend",
            env={**os.environ, "NEXT_TELEMETRY_DISABLED": "1"},
            stdout=frontend_log, stderr=subprocess.STDOUT, start_new_session=True,
        )
        stack.callback(stop, frontend)
        wait_for_server(backend, "http://127.0.0.1:8000/health")
        wait_for_server(frontend, "http://127.0.0.1:3000")

        health = fetch("http://127.0.0.1:8000/health")
        assert json.loads(health) == {"status": "ok"}
        print("GET http://127.0.0.1:8000/health -> HTTP 200")
        print(health.decode())

        capabilities = fetch("http://127.0.0.1:8000/api/v1/capabilities")
        data = json.loads(capabilities)
        entries = data["transformations"]
        assert len(entries) == 7
        assert {item["output_type"] for item in entries} == OUTPUTS
        assert all(item["implemented"] is False for item in entries)
        assert len(data["provenance_statuses"]) == 4
        assert set(data["provenance_statuses"]) == STATUSES
        print("GET http://127.0.0.1:8000/api/v1/capabilities -> HTTP 200")
        print(capabilities.decode())
        print("Verified exactly 7 transformations, all implemented=false; 4 provenance states.")

        transform_request = {
            "source": {"type": "text", "text": FIXTURE},
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
        first_status, first = post_json(
            "http://127.0.0.1:8000/api/v1/transform", transform_request
        )
        assert first_status == 200
        assert first["status"] == "ok"
        assert first["mode"] == "DETERMINISTIC_STUB"
        assert len(first["artifacts"]) == 1
        assert first["artifacts"][0]["output_type"] == "executive_summary"
        assert first["artifacts"][0]["content"].startswith("[DETERMINISTIC STUB]")
        assert FIXTURE in first["artifacts"][0]["content"]
        print("POST http://127.0.0.1:8000/api/v1/transform -> HTTP 200")
        print(json.dumps(first, separators=(",", ":")))
        print("Verified executive_summary, DETERMINISTIC_STUB, one artifact and visible marker.")

        second_status, second = post_json(
            "http://127.0.0.1:8000/api/v1/transform", transform_request
        )
        assert second_status == 200
        assert first["artifacts"] == second["artifacts"]
        print("Repeated POST -> HTTP 200; semantic artifact content is identical.")

        invalid_request = {
            **transform_request,
            "source": {"type": "text", "text": " \n\t "},
        }
        invalid_status, invalid = post_json(
            "http://127.0.0.1:8000/api/v1/transform", invalid_request
        )
        assert invalid_status == 422
        print(f"Invalid whitespace request -> HTTP {invalid_status}")
        print(json.dumps(invalid, separators=(",", ":")))
        print("Verified ordinary invalid input returns typed HTTP 422, not HTTP 500.")

        url = "http://127.0.0.1:8000/openapi.json"
        raw_schema = fetch(url)
        export = ARTIFACTS / "openapi.json"
        export.write_bytes(raw_schema)
        assert export.read_bytes() == raw_schema
        schema = json.loads(export.read_bytes())
        assert set(schema["paths"]) == {
            "/health", "/api/v1/capabilities", "/api/v1/transform"
        }
        models = schema["components"]["schemas"]
        assert set(models["OutputType"]["enum"]) == OUTPUTS
        assert set(models["ProvenanceStatus"]["enum"]) == STATUSES
        assert models["TransformationCapability"]["properties"]["implemented"]["const"] is False
        assert "TransformRequest" in models
        assert "TransformResponse" in models
        print(f"GET {url} -> HTTP 200")
        print(f"Exported {len(raw_schema)} unchanged HTTP bytes to artifacts/openapi.json")
        print(f"SHA-256: {hashlib.sha256(raw_schema).hexdigest()}")
        print(f"OpenAPI paths: {', '.join(sorted(schema['paths']))}")
        print("OpenAPI TransformRequest/TransformResponse, output/provenance enums and implemented=false constraint verified.")

        html = fetch("http://127.0.0.1:3000").decode()
        assert "Stringray" in html
        assert "Phase 1 / walking skeleton" in html
        print("GET http://127.0.0.1:3000 -> HTTP 200; production workspace content verified.")
    print("Owned backend/frontend process groups stopped. Browser visuals were not inspected.")


if __name__ == "__main__":
    main()
