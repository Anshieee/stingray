# Progress

- **Current iteration:** v0.2.0 — Phase 1 / walking skeleton.
- **Current verified tag:** v0.1.0.
- **Last human-verified fallback tag:** v0.1.0.
- **Current candidate:** v0.2.0.
- **v0.2.0 automated/local verification:** passed independently by the human.
- **v0.2.0 human browser/visual verification:** outstanding.
- **Local release status:** v0.2.0 created locally; awaiting human browser/visual verification.
- **Next planned phase:** Phase 2 — Canonical Content Model and real structured source understanding.

## Completed items

- Repository boundary established; pre-existing sandbox tooling preserved and ignored.
- FastAPI factory, health endpoint, seven truthful capability definitions, output
  enumeration, provenance vocabulary and typed `/api/v1/transform` contracts.
- Deterministic service for one bounded plain-text `executive_summary` artifact.
- Minimal Next.js/React/Tailwind workspace with strict TypeScript, live API transport,
  loading/error/result states and component tests.
- Backend behavioural tests, ruff, frontend lint/typecheck/test/build scripts.
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
results were independently re-run by the human; they do not include browser visual
verification or hosted-CI evidence.

The current human-verified tag remains v0.1.0. The v0.2.0 candidate must not be
promoted until the human browser/visual verification is recorded. A local annotated
tag does not establish independent verification.

## Current limitations

- AI transformation is NOT implemented. The provider is `<AI_PROVIDER_LATER>`.
- Plain text is the only input path; `executive_summary` is the only exposed output
  path and is a deterministic integration stub, not a genuine summary.
- The six generation controls are modeled as nullable request data but do not affect
  the stub. Source text is bounded at 10,000 characters and over-limit input is rejected.
- No document/media/URL ingestion, uploads, canonical extraction, model calls,
  evidence/grounding, rendering/exporting, authentication, database, workers or publishing.
- All seven transformations remain contract definitions with `implemented: false`;
  only executive_summary has `stub_available: true`.
- Provenance states and rules exist; EvidenceReference, claim validation and the
  full canonical content model are deferred.
- The frontend does not yet expose the future generation controls.
- Deliverable outlines exist; no demo video or technical slide deck has been produced.

## Open issues

- Human browser/visual verification of the local v0.2.0 candidate is outstanding;
  v0.1.0 remains the current human-verified fallback tag.
- Hosted GitHub Actions has not run; no push is authorized.
- Browser visual appearance and manual browser interaction have not been inspected.
- ESLint is pinned to 9.39.5: the installed Next.js React lint plugin fails under
  ESLint 10 (`contextOrFilename.getFilename is not a function`). ESLint 9 emits a
  support/deprecation notice on install. Revisit when the plugin supports ESLint 10.
- The sandbox's default npm cache is unwritable and Python 3.12 lacks bundled pip;
  use a writable npm cache and a uv-seeded venv as documented in README.

## Next scope

Phase 2 — Canonical Content Model and real structured source understanding.
