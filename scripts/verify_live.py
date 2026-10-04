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
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
OUTPUTS = {
    "video_package", "linkedin_post", "x_post", "advisory",
    "infographic", "executive_summary", "presentation",
}
STATUSES = {"OBSERVED", "INFERRED", "UNKNOWN", "NOT_APPLICABLE"}
HTTP = build_opener(ProxyHandler({}))


def fetch(url: str) -> bytes:
    with HTTP.open(url, timeout=3) as response:
        assert response.status == 200, f"Unexpected HTTP status for {url}: {response.status}"
        return response.read()


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

        url = "http://127.0.0.1:8000/openapi.json"
        raw_schema = fetch(url)
        export = ARTIFACTS / "openapi.json"
        export.write_bytes(raw_schema)
        assert export.read_bytes() == raw_schema
        schema = json.loads(export.read_bytes())
        assert set(schema["paths"]) == {"/health", "/api/v1/capabilities"}
        models = schema["components"]["schemas"]
        assert set(models["OutputType"]["enum"]) == OUTPUTS
        assert set(models["ProvenanceStatus"]["enum"]) == STATUSES
        assert models["TransformationCapability"]["properties"]["implemented"]["const"] is False
        print(f"GET {url} -> HTTP 200")
        print(f"Exported {len(raw_schema)} unchanged HTTP bytes to artifacts/openapi.json")
        print(f"SHA-256: {hashlib.sha256(raw_schema).hexdigest()}")
        print(f"OpenAPI paths: {', '.join(sorted(schema['paths']))}")
        print("OpenAPI output/provenance enums and implemented=false constraint verified.")

        html = fetch("http://127.0.0.1:3000").decode()
        for text in ("Stringray", "Phase 0 / foundation",
                     "AI transformation is not implemented in v0.1.0."):
            assert text in html
        print("GET http://127.0.0.1:3000 -> HTTP 200; production shell content verified.")
    print("Owned backend/frontend process groups stopped. Browser visuals were not inspected.")


if __name__ == "__main__":
    main()
