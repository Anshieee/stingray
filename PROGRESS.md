# Progress

- **Current iteration:** v0.4.0 — Phase 3A document ingestion foundation + PDF analysis.
- **Current verified tag:** v0.3.3.
- **Last human-verified fallback tag:** v0.3.4.
- **Current candidate:** v0.4.0 (ingestion only; no output generation, no frontend change).
- **Current human-verified implementation:** v0.3.3 (Phase 2B, real FreeLLMAPI smoke passed).
- **v0.3.1 status:** rejected local candidate (nested extras silently accepted).
- **v0.3.3 smoke history:** real FreeLLMAPI auto-router smoke passed
  (`freellmapi`, router `auto`); routed-model observation was request-specific.
- **Phase 3A status:** implemented and locally verified with injected fakes;
  real PDF + real provider analysis not yet run.
- **Local release status:** v0.4.0 created locally; awaiting human verification.
- **Next planned phase:** Phase 4 — real artifact generation (not started).

## Completed items

- Repository boundary established; pre-existing sandbox tooling preserved and ignored.
- FastAPI factory, health endpoint, seven truthful capability definitions, output
  enumeration, provenance vocabulary and typed `/api/v1/transform` contracts.
- Deterministic service for one bounded plain-text `executive_summary` artifact.
- Minimal Next.js/React/Tailwind workspace with strict TypeScript, live API transport,
  loading/error/result states and component tests.
- Backend behavioural tests, ruff, frontend lint/typecheck/test/build scripts.
- Deterministic canonical scaffolding: line-ending normalization, paragraph
  segments with exact offsets, stable IDs, SHA-256 identity, evidence references,
  provenance-aware claims, empty canonical shell and structural cross-validation.
- Provider-backed analysis: provider-neutral interface, OpenAI Responses-API
  structured-output adapter (timeout 30s, max_retries 1), env-driven config,
  `POST /api/v1/analyze` with honest typed errors, injected-fake test coverage.
- Setup documentation, architecture/provenance/API contracts and ADRs.
- CI workflow and repeatable live quick E2E/OpenAPI and index-hygiene scripts.

## Verification record

Automated/local checks completed on **2026-10-04** and independently re-run successfully
by the human, using Git 2.55.0, Python 3.12.13 (default system Python is 3.14.7),
Node 24.21.0 and npm 12.1.0:

| Check | Evidence |
| --- | --- |
| Backend install | uv-seeded Python 3.12 venv; pip editable install constrained by `requirements-dev.lock` |
| Backend lint | `python -m ruff check backend scripts`: All checks passed! |
| Backend tests | `python -m pytest backend/tests -q`: 21 passed in 0.48s |
| Frontend clean install | `npm ci`: installed locked dependencies successfully |
| Frontend lint | `npm run lint`: exit 0, zero warnings |
| Frontend typecheck | `npm run typecheck`: route types generated; TypeScript exit 0 |
| Frontend tests | `npm test`: 1 file / 7 tests passed |
| Frontend production build | `npm run build`: compiled, typed and prerendered `/` and `/_not-found` |
| Live backend | HTTP 200 for health (`status=ok`) and capabilities (exactly seven entries, all false; four provenance states) |
| Live transform | Project Aurora fixture returned HTTP 200, one `executive_summary`, `DETERMINISTIC_STUB`, visible marker, identical repeated artifact and HTTP 422 for whitespace input |
| Live OpenAPI | 5,893 unmodified HTTP response bytes exported to ignored `artifacts/openapi.json`; three paths, TransformRequest/TransformResponse, enums and false availability constraint checked |
| Live frontend | Built server returned HTTP 200 and the walking-skeleton workspace response |
| Index hygiene | No environment/artifact/sandbox files, credential-pattern matches or machine-specific home paths; staged whitespace check clean |

Live export SHA-256:
`c46eadfe8575e78f9955a9bf1300c52b8c4579fd1eabd917a892bb26fa46b660`.
The live script stopped both process groups after verification. These automated/local
results were independently re-run by the human; they do not include hosted-CI evidence.

Human browser/visual verification of Phase 1 is complete: real submission worked,
successful output was visibly labeled `DETERMINISTIC STUB / NO AI`, backend-down state
produced an honest connection error, empty source input produced a validation error,
no fake confidence/citations/analytics were shown, and layout was usable.
Browser-extension DOM injection (Dark Reader, Video Speed Controller) caused false
hydration warnings during verification; they were not Stringray defects.

The previous human-verified fallback tag is v0.2.2. Phase 1 remains complete; this
candidate adds only the deterministic Phase 2A foundation. A local annotated tag
does not establish remote publication.

## Phase 2A verification (v0.3.0 candidate)

Deterministic canonical checks run with `backend/.venv/bin/python -m pytest
backend/tests -q` (51 passed: 21 Phase-1 regression + 30 canonical). Coverage
includes the literal normalization oracle (37 chars, fixed SHA-256), exact
paragraph offsets, stable/unique IDs, OBSERVED-evidence invariants, no-confidence
contract, and loud cross-validation failures. No AI provider, model call, new
route, frontend change or new dependency was introduced. Structural validation
proves cited segments exist with valid locations; it does not prove semantic
entailment.

## Phase 2B verification (v0.3.3 human-verified)

Backend `pytest` (123 passed, plus strict-schema and FreeLLMAPI suites) covers semantic-only
provider schema, server-owned identity combination, single provider call,
OBSERVED-evidence failures without silent repair, Raven source-as-data handling,
`/analyze` HTTP/error taxonomy via injected fakes, and adapter behavior via
mock SDK clients (parse path, text format, model passing, segment input, separate
instructions, parsed-output use, reported-model honesty, refusal/timeout/auth/
rate-limit mapping). No test performs network calls or spends tokens. OpenAI SDK
3.24.0 (`openai>=3.24.0,<4`) is used as the OpenAI-compatible protocol client.
Live E2E scrubs provider env vars from its child
backend and proves `/analyze` returns 503 unconfigured.

Human verification of v0.3.3 PASSED: 15 FreeLLMAPI focused tests, full backend
suite, ruff, pip check, empty frontend diff, live deterministic verifier and
clean hygiene were independently rerun. The human then ran one authorized real
FreeLLMAPI auto-router smoke (`FREELLMAPI_MODEL=auto`,
`FREELLMAPI_BASE_URL=http://localhost:3001/v1`): HTTP 200 with
`provider: freellmapi`, `requested_model: auto` and provider-reported
`deepseek-ai/DeepSeek-V4-Flash-0731`; server-owned SHA/segments and real segment
evidence verified; date, 18-team statistic and risk-review request OBSERVED with
evidence; risk interpretation INFERRED; unknowns UNKNOWN without fabrication;
no confidence field and no invalid evidence. Phase 2B is complete.

## Current limitations

- AI transformation of outputs is NOT implemented; `/analyze` performs source
  analysis only and the frontend is not connected to it.
- Plain text is the only input path; `executive_summary` is the only exposed output
  path and is a deterministic integration stub, not a genuine summary.
- The six generation controls are modeled as nullable request data but do not affect
  the stub. Source text is bounded at 10,000 characters and over-limit input is rejected.
- No document/media/URL ingestion, uploads, model calls, semantic grounding,
  rendering/exporting, authentication, database, workers or publishing.
- All seven transformations remain contract definitions with `implemented: false`;
  only executive_summary has `stub_available: true`.
- Deterministic canonical preparation and structural evidence validation exist
  internally; AI-driven canonical extraction and semantic entailment checking are
  deferred to later phases.
- The frontend does not yet expose the future generation controls.
- Deliverable outlines exist; no demo video or technical slide deck has been produced.

## Open issues

- Hosted GitHub Actions has not run; no push is authorized.
- ESLint is pinned to 9.39.5: the installed Next.js React lint plugin fails under
  ESLint 10 (`contextOrFilename.getFilename is not a function`). ESLint 9 emits a
  support/deprecation notice on install. Revisit when the plugin supports ESLint 10.
- The sandbox's default npm cache is unwritable and Python 3.12 lacks bundled pip;
  use a writable npm cache and a uv-seeded venv as documented in README.

## Next scope

Phase 3A — document ingestion foundation.
