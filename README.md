# Stringray

Stringray is a planned AI-powered multimodal platform that understands a common
information source once and transforms it into configurable communication artefacts.

**v0.4.0 candidate — Phase 3A document ingestion foundation.**
`POST /api/v1/analyze` handles plain text and `POST /api/v1/analyze/pdf` accepts
text-bearing PDF uploads through the same deterministic
prepare → provider → validate pipeline (no OCR; scanned PDFs are rejected
honestly). Without provider configuration both return a controlled 503; the
browser Phase-1 slice is unchanged and the frontend is not connected to analysis
yet; see
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
deterministic stub artifact for `/transform`. `POST /api/v1/analyze` is a separate
backend-only analysis endpoint (not wired into the browser): it prepares the source
deterministically, calls the configured OpenAI structured-analysis provider once,
and returns validated canonical content, or an honest machine-readable error when
unconfigured or when the provider fails. Source identity (SHA-256, counts, segment
catalog) always comes from the server, never the model.
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
repeats a known Project Aurora request, checks invalid input, proves `/analyze`
returns a controlled 503 without provider configuration (no AI tokens spent),
exports the **live**
OpenAPI response to ignored `artifacts/openapi.json`, checks the served frontend
workspace, then stops its processes. This is HTTP verification, not visual browser inspection.
Provider env names (`AI_PROVIDER`, `OPENAI_API_KEY`, `OPENAI_MODEL`,
`FREELLMAPI_API_KEY`, `FREELLMAPI_BASE_URL`, `FREELLMAPI_MODEL`) are scrubbed
from the verification child process; automated checks never call a real model.

## API and live OpenAPI export

With the backend running:

```sh
curl --fail --silent --show-error http://127.0.0.1:8000/health
curl --fail --silent --show-error http://127.0.0.1:8000/api/v1/capabilities
curl --fail --silent --show-error --request POST http://127.0.0.1:8000/api/v1/transform \
  --header 'Content-Type: application/json' \
  --data '{"source":{"type":"text","text":"The organization announced Project Aurora on 4 October 2026."},"outputs":["executive_summary"],"controls":{"target_audience":null,"tone":null,"language":null,"detail_level":null,"communication_objective":null,"content_style":null}}'
curl --fail --silent --show-error --request POST http://127.0.0.1:8000/api/v1/analyze \
  --header 'Content-Type: application/json' \
  --data '{"source":{"type":"text","text":"The organization announced Project Aurora on 4 October 2026."}}'
curl --fail --silent --show-error --request POST http://127.0.0.1:8000/api/v1/analyze/pdf \
  --form 'file=@backend/tests/fixtures/atlas.pdf;type=application/pdf'
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

## Phase 2B analysis contract and manual smoke (human only)

`POST /api/v1/analyze` accepts only `{"source": {"type": "text", "text": "..."}}`
(1..10,000 chars, non-whitespace, same policy as Phase 1). `POST
/api/v1/analyze/pdf` accepts one `multipart/form-data` PDF upload (field `file`,
<=10 MiB, text-bearing only): pages are extracted in order with pypdf, flattened
with `"\n\n"` separators and analyzed through the same pipeline, reporting
`source_type: pdf`. Scanned/image-only PDFs return a controlled 400 (no OCR yet);
oversized uploads or over-limit extracted text return 413 without truncation. Success returns
`status: ok`, `mode: AI_STRUCTURED_ANALYSIS`, truthful `provider` /
`requested_model` / `provider_reported_model` (null when unreported), validated
`canonical_content` and empty `warnings`. Failures are typed
`{"status": "error", "error": {"code": ..., "message": ...}}` without secrets or
source text: unconfigured/auth/rate-limit → 503, timeout → 504, upstream/refusal/
invalid/validation → 502, bad input → 422.

Manual real-provider smoke is a separate explicit human action and is never run by
automated agents. Direct OpenAI: `AI_PROVIDER=openai` with `OPENAI_MODEL` and
`OPENAI_API_KEY` in the environment. FreeLLMAPI auto router:
`AI_PROVIDER=freellmapi` with `FREELLMAPI_MODEL=auto`,
`FREELLMAPI_BASE_URL=http://localhost:3001/v1` and `FREELLMAPI_API_KEY` in the
environment. Start the API, e.g.:

```sh
AI_PROVIDER=freellmapi FREELLMAPI_MODEL=auto \
  FREELLMAPI_BASE_URL=http://localhost:3001/v1 FREELLMAPI_API_KEY=<secret> \
  backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend \
  --host 127.0.0.1 --port 8000
```

then POST source `Project Aurora will begin on 12 October 2026. The programme will
initially involve 18 research teams. Leadership requested a risk review before
launch.` Expect OBSERVED evidence-backed date/statistic claims, INFERRED-only risk
interpretation, resolvable segment IDs, server-owned SHA/segments and no confidence
scores. Never paste keys into chat or commit them.

## Roadmap, deliverables and limitations

- **P0:** foundation and contracts (`v0.1.0`).
- **P1:** real browser -> live API -> clearly labeled deterministic
  `executive_summary` stub -> browser, without live AI.
- **P2A:** deterministic canonical scaffolding (`v0.3.0`).
- **P2B (this iteration):** provider-backed structured source analysis via
  `/api/v1/analyze`; frontend remains on the Phase-1 slice.
- **Later, separately scoped:** ingestion, grounded transformations, render/export and evaluation.

Challenge deliverables: source code, setup README, architecture document **maximum
2 pages**, demo video **maximum 2 minutes**, technical presentation **maximum 5 slides**.
The latter deliverables have planning skeletons in [docs/deliverables.md](docs/deliverables.md);
the video and presentation do not yet exist.

There are no uploads, document/media/URL ingestion, live AI calls, provider adapters,
renderers/exporters, authentication, persistence, queues or external publishing.
Only the deterministic `executive_summary` integration stub is available; all seven
output types remain definitions with `implemented: false`. Provenance semantics and
structural evidence validation exist; semantic entailment checking and AI-driven
canonical extraction are future work. The
eventual runtime provider remains `<AI_PROVIDER_LATER>`.
