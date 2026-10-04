# Stringray

Stringray is a planned AI-powered multimodal platform that understands a common
information source once and transforms it into configurable communication artefacts.

**v0.1.0 — Phase 0 / foundation. AI transformation is NOT implemented.**
This iteration provides a minimal frontend, health/capability APIs, engineering
checks, and documented contracts. The local tag awaits human verification; see
[PROGRESS.md](PROGRESS.md).

## Architecture and layout

Planned flow (content processing is future work):

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

The frontend is an informational shell; it does not call the backend in Phase 0.
The backend exposes definitions and process health, not generation services.
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
loaded or needed. If a sandbox has an unwritable default npm cache, prefix the install
command with `env npm_config_cache=.npm-cache`; that cache is ignored.

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

After building, with ports 8000 and 3000 free, run the repeatable live check from the root:

```sh
backend/.venv/bin/python scripts/verify_live.py
```

It starts both processes, checks real HTTP responses, exports the **live** OpenAPI
response to ignored `artifacts/openapi.json`, checks both API paths and the served
frontend shell, then stops its processes. This is HTTP verification, not visual browser inspection.

## API and live OpenAPI export

With the backend running:

```sh
curl --fail --silent --show-error http://127.0.0.1:8000/health
curl --fail --silent --show-error http://127.0.0.1:8000/api/v1/capabilities
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

## Roadmap, deliverables and limitations

- **P0 (this iteration):** foundation and contracts.
- **P1 Walking Skeleton:** real browser -> live API -> clearly labeled deterministic
  transformation stub -> browser, without live AI.
- **Later, separately scoped:** ingestion, canonical extraction/evidence, provider
  integration, grounded transformations, render/export and evaluation.

Challenge deliverables: source code, setup README, architecture document **maximum
2 pages**, demo video **maximum 2 minutes**, technical presentation **maximum 5 slides**.
The latter deliverables have planning skeletons in [docs/deliverables.md](docs/deliverables.md);
the video and presentation do not yet exist.

There are no uploads, ingestion, canonical extraction, transformations, live AI calls,
renderers/exporters, authentication, persistence, queues or external publishing.
All seven output types are definitions marked unavailable. Provenance semantics are
documented; evidence extraction and claim-level validation are future work. The
eventual runtime provider remains `<AI_PROVIDER_LATER>`.
