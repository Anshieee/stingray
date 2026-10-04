# Stringray

Stringray is a planned AI-powered multimodal platform that understands a common
information source once and transforms it into configurable communication artefacts.

**v0.2.0 — Phase 1 / walking skeleton. AI transformation is NOT implemented.**
This iteration connects a real plain-text browser request to a live FastAPI route,
a deterministic transformation stub and a browser result. The local tag awaits
human verification; see
[PROGRESS.md](PROGRESS.md).

## Architecture and layout

Current thin slice:

```text
Browser -> Next.js workspace -> POST /api/v1/transform -> deterministic stub -> browser result
```

Planned full flow (canonical content processing is future work):

```text
Source -> Ingestion -> Canonical Content Model -> Generation Controls
       -> Transformation Engine -> Validation/Grounding -> Render/Export
```

All future generators consume the **same canonical analysis**, not independent
reinterpretations of the raw source. Source content is data, never instructions.
FastAPI-generated OpenAPI is the authoritative API contract.

```text
frontend/       Next.js, React, strict TypeScript, Tailwind, Vitest
backend/        FastAPI, Pydantic, pytest, ruff
docs/           Project brief, architecture and API/provenance contracts
scripts/        Repeatable live verification and tracked-content hygiene
.github/        CI workflow
AGENTS.md       Instructions for future coding sessions
DECISIONS.md    Architecture decision records
PROGRESS.md     Phase status, verification and open issues
CHANGELOG.md    Iteration history
.env.example    Reserved environment variable names; no values required
```

The frontend is a minimal walking-skeleton workspace. It sends only plain text and
requests the `executive_summary` output. The backend returns one clearly labeled
deterministic stub artifact. No AI model, canonical analysis, evidence or grounding
is involved. The seven-output vocabulary remains the eventual product specification.
Pre-existing root npm manifests in the operator's sandbox belong to Omnirush,
are preserved locally, and are ignored. Run project npm commands in `frontend/`.

## Prerequisites

- Git, Python **3.12** with venv/pip, Node.js **24 LTS (24.15 or newer)**, npm.
- Linux/macOS for the commands below and the process-based live verification script.
- `curl` for the manual API examples. No API keys, database or AI provider required.

Commands start in the project root unless a block explicitly changes directory.
They work in bash and fish without activating a virtual environment or using heredocs.

## Backend setup and local server

```sh
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -c backend/requirements-dev.lock -e './backend[dev]'
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

If your Python distribution lacks venv/pip and `uv` is available, use
`uv venv --python python3.12 --seed backend/.venv` for the first command.
`requirements-dev.lock` pins the resolved application/dev dependencies; pip remains
the installation interface. To intentionally refresh the lock with `uv`, run:

```sh
cd backend
uv pip compile --python .venv/bin/python pyproject.toml --extra dev --output-file requirements-dev.lock
cd ..
```

## Frontend setup and local server

In another terminal, from the root:

```sh
cd frontend
npm ci
npm run dev
```

Open <http://127.0.0.1:3000>. Stop either server with Ctrl+C. No environment file is
loaded or needed for the documented local defaults. The browser backend origin is
configured in one place by `NEXT_PUBLIC_BACKEND_BASE_URL`; set it to
`http://127.0.0.1:8000` when overriding the default. If a sandbox has an unwritable
default npm cache, prefix the install command with `env npm_config_cache=.npm-cache`;
that cache is ignored. FastAPI permits only `http://127.0.0.1:3000` and
`http://localhost:3000` for development CORS.

## Checks and production build

Backend, from the root:

```sh
backend/.venv/bin/python -m ruff check backend scripts
backend/.venv/bin/python -m pytest backend/tests -q
```

Frontend, from the root:

```sh
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
npm start
```

`typecheck` generates Next.js route types before running strict TypeScript checks.
`npm start` serves the production build locally; it is not a deployment step.
Next.js telemetry can be disabled by prefixing Next commands with
`env NEXT_TELEMETRY_DISABLED=1`.

After building, with ports 8000 and 3000 free, run the repeatable quick end-to-end check from the root:

```sh
backend/.venv/bin/python scripts/verify_live.py
```

It starts both processes, checks real health/capability/transform HTTP responses,
repeats a known Project Aurora request, checks invalid input, exports the **live**
OpenAPI response to ignored `artifacts/openapi.json`, checks the served frontend
workspace, then stops its processes. This is HTTP verification, not visual browser inspection.

## API and live OpenAPI export

With the backend running:

```sh
curl --fail --silent --show-error http://127.0.0.1:8000/health
curl --fail --silent --show-error http://127.0.0.1:8000/api/v1/capabilities
curl --fail --silent --show-error --request POST http://127.0.0.1:8000/api/v1/transform \
  --header 'Content-Type: application/json' \
  --data '{"source":{"type":"text","text":"The organization announced Project Aurora on 4 October 2026."},"outputs":["executive_summary"],"controls":{"target_audience":null,"tone":null,"language":null,"detail_level":null,"communication_objective":null,"content_style":null}}'
mkdir -p artifacts
curl --fail --silent --show-error http://127.0.0.1:8000/openapi.json --output artifacts/openapi.json
python3.12 -c 'import json; from pathlib import Path; print(sorted(json.loads(Path("artifacts/openapi.json").read_text())["paths"]))'
```

Interactive API documentation: <http://127.0.0.1:8000/docs>.
Do not hand-maintain or commit an independent OpenAPI JSON document. See
[API contract](docs/api-contract.md) and [provenance contract](docs/provenance-contract.md).

## CI and hygiene

The push/pull-request workflow installs locked dependencies and runs backend ruff/pytest
and frontend lint/typecheck/tests/build, without secrets or AI calls.
Before committing, stage only intended project files and run:

```sh
python3.12 scripts/check_hygiene.py
git diff --cached --check
git diff --cached --stat
```

The hygiene script checks the Git index, including staged new files. Its credential
patterns are a heuristic aid, not proof that arbitrary secrets are absent.

## Phase 1 contract and limitations

The only usable transformation request is `POST /api/v1/transform` with a plain-text
source and exactly `executive_summary` in `outputs`. The six generation-control
fields are modeled and preserved as nullable request data, but they do not alter the
stub. Source text is limited to **10,000 characters** as a conservative bounded-input
guard for this local integration slice; over-limit requests are rejected, never silently
truncated. The deterministic engine normalizes whitespace and returns a bounded excerpt.
Its output begins with `[DETERMINISTIC STUB]`, and the API mode is `DETERMINISTIC_STUB`.

## Roadmap, deliverables and limitations

- **P0:** foundation and contracts (`v0.1.0`).
- **P1 (this iteration):** real browser -> live API -> clearly labeled deterministic
  `executive_summary` stub -> browser, without live AI.
- **P2:** canonical content model and real structured source understanding.
- **Later, separately scoped:** ingestion, canonical extraction/evidence, provider
  integration, grounded transformations, render/export and evaluation.

Challenge deliverables: source code, setup README, architecture document **maximum
2 pages**, demo video **maximum 2 minutes**, technical presentation **maximum 5 slides**.
The latter deliverables have planning skeletons in [docs/deliverables.md](docs/deliverables.md);
the video and presentation do not yet exist.

There are no uploads, document/media/URL ingestion, canonical extraction, live AI calls,
renderers/exporters, authentication, persistence, queues or external publishing.
Only the deterministic `executive_summary` integration stub is available; all seven
output types remain definitions with `implemented: false`. Provenance semantics are
documented; evidence extraction and claim-level validation are future work. The
eventual runtime provider remains `<AI_PROVIDER_LATER>`.
