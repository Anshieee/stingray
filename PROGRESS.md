# Progress

- **Current iteration:** v0.1.0 — Phase 0 / foundation.
- **Current verified tag:** NONE.
- **Local release status:** Created locally; awaiting human verification.
- **Next planned phase:** P1 Walking Skeleton.

## Completed items

- Repository boundary established; pre-existing sandbox tooling preserved and ignored.
- FastAPI factory, health endpoint, explicitly unavailable capability definitions,
  output enumeration and provenance vocabulary.
- Minimal Next.js/React/Tailwind shell with strict TypeScript and a component smoke test.
- Backend behavioural tests, ruff, frontend lint/typecheck/test/build scripts.
- Setup documentation, architecture/provenance/API contracts and ADRs.
- CI workflow and repeatable live HTTP/OpenAPI and index-hygiene scripts.

## Verification record

Automated/local checks completed on **2026-10-04**, using Git 2.55.0, Python
3.12.13 (default system Python is 3.14.7), Node 24.21.0 and npm 12.1.0:

| Check | Evidence |
| --- | --- |
| Backend install | uv-seeded Python 3.12 venv; pip editable install constrained by `requirements-dev.lock` |
| Backend lint | `python -m ruff check backend scripts`: All checks passed! |
| Backend tests | `python -m pytest backend/tests -q`: 4 passed in 0.64s |
| Frontend clean install | `npm ci`: installed locked dependencies successfully |
| Frontend lint | `npm run lint`: exit 0, zero warnings |
| Frontend typecheck | `npm run typecheck`: route types generated; TypeScript exit 0 |
| Frontend tests | `npm test`: 1 file / 1 test passed |
| Frontend production build | `npm run build`: compiled, typed and prerendered `/` and `/_not-found` |
| Live backend | HTTP 200 for health (`status=ok`) and capabilities (exactly seven entries, all false; four provenance states) |
| Live OpenAPI | 2,239 unmodified HTTP response bytes exported to ignored `artifacts/openapi.json`; both paths, enums and false availability constraint checked |
| Live frontend | Built server returned HTTP 200 and the foundation-only shell text |
| Index hygiene | No environment/artifact/sandbox files, credential-pattern matches or machine-specific home paths; staged whitespace check clean |

Live export SHA-256:
`a7288c50b50f5451e4757102a0b26d78e001f17a52a70abe28984cff6abfa58c`.
The live script stopped both process groups after verification. These are local
automated results, not browser visual or hosted-CI evidence.

Only external/human verification can promote a tag to "current verified tag";
record the verifier, date and evidence here when available. A local annotated tag
does not establish independent verification.

## Current limitations

- AI transformation is NOT implemented. The provider is `<AI_PROVIDER_LATER>`.
- No ingestion, uploads, canonical extraction, model calls, generated content,
  rendering/exporting, authentication, database, workers or publishing.
- All seven transformations are contract definitions with `implemented: false`.
- Provenance states and rules exist; EvidenceReference, claim validation and the
  full canonical content model are deferred.
- The frontend shell does not yet call the backend.
- Deliverable outlines exist; no demo video or technical slide deck has been produced.

## Open issues

- Human verification of the local v0.1.0 candidate is outstanding.
- Hosted GitHub Actions has not run; no push is authorized.
- Browser visual appearance has not been inspected.
- ESLint is pinned to 9.39.5: the installed Next.js React lint plugin fails under
  ESLint 10 (`contextOrFilename.getFilename is not a function`). ESLint 9 emits a
  support/deprecation notice on install. Revisit when the plugin supports ESLint 10.
- The sandbox's default npm cache is unwritable and Python 3.12 lacks bundled pip;
  use a writable npm cache and a uv-seeded venv as documented in README.

## Next scope

Phase 1 — Walking Skeleton: real browser -> live API -> deterministic transformation
stub -> browser, without live AI. Any stub must be visibly labeled. Phase 1 has not begun.
