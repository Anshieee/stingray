# Changelog

## v0.3.4 — Phase 2B verified closeout

Documentation only; no application behavior changed.
No remote release or publication.

- Recorded completed human verification of v0.3.3 and a passed real FreeLLMAPI
  auto-router smoke (`provider: freellmapi`, router `auto`, routed model
  observed as reported by the provider): server-owned source identity and
  evidence-backed OBSERVED/INFERRED/UNKNOWN semantics behaved as intended.

## v0.3.3 — Phase 2B FreeLLMAPI provider adaptation

Local candidate; backend provider adaptation only, no frontend change.
No remote release or publication.

- Generalized the structured Responses adapter to OpenAI-compatible endpoints
  with explicit provider identity and base URL; `AI_PROVIDER=freellmapi` uses
  `FREELLMAPI_API_KEY`/`FREELLMAPI_MODEL` (e.g. `auto`) with a documented local
  router default, returning `provider: freellmapi` without fabricating the
  reported model.
- Direct `AI_PROVIDER=openai` support preserved unchanged; live verification
  scrubs both provider families and still proves unconfigured 503 behavior.

## v0.3.2 — Phase 2B strict nested provider schema repair

Repair only; no new product functionality, no frontend change.
No remote release or publication.

- Made shared canonical models `ProvenancedClaim` and `EvidenceReference`
  explicitly strict (`extra="forbid"`), so nested `confidence` or other unknown
  provider fields are rejected instead of silently ignored.
- Narrowed the staged-content hygiene credential heuristic to exempt provable
  non-secrets (environment lookups, bare pass-throughs, obviously fake test
  literals) while still flagging realistic hard-coded credentials.

## v0.3.1 — Phase 2B provider-backed structured source analysis

Local candidate; backend analysis only, no frontend feature work.
No remote release or publication.

- Added provider-neutral analysis interface with server-owned source identity and
  semantic-only provider output, plus an application service that prepares once,
  calls the provider once and validates loudly without silent repair.
- Added official OpenAI Responses-API structured-output adapter (Pydantic parsing,
  env-driven model/key, 30s timeout, max_retries 1) and `POST /api/v1/analyze`
  with honest typed errors and distinct requested/reported model metadata.
- Automated tests use injected fakes and mock SDK clients only; live verification
  scrubs provider credentials and proves unconfigured 503 behavior.

## v0.3.0 — Phase 2A deterministic canonical scaffolding

Local candidate; no AI provider, model calls, new API route or frontend change.
No remote release or publication.

- Added deterministic source preparation: CRLF/CR-to-LF normalization, paragraph
  segments with exact offsets, stable IDs, UTF-8 SHA-256 and typed metadata.
- Added typed canonical domain: evidence references, provenance-aware claims with
  OBSERVED-requires-evidence, empty canonical shell and loud structural validation.
- Structural validation proves cited segments exist with valid locations; semantic
  entailment remains future work.

## v0.2.2 — Phase 1 verified closeout

Human-verified fallback is now v0.2.1; Phase 1 browser/visual verification is
complete. No remote release or publication.

- Recorded completed human verification for Phase 1 with no application change.
- Recreated the ignored local backend virtual environment from locked
  dependencies after the repository move (stale editable-install path fix).

## v0.2.0 — Phase 1 walking skeleton

Local candidate; automated/local verification passed independently by the human.
Browser/visual verification remains outstanding. No remote release or publication.

- Added typed `POST /api/v1/transform` for plain text and exactly one
  `executive_summary` request.
- Added a separate deterministic transformation service with bounded whitespace
  normalization and explicit `DETERMINISTIC_STUB` response mode.
- Added real frontend-to-backend fetch, loading/error states and visibly marked
  `DETERMINISTIC STUB / NO AI` output.
- Extended live verification to cover the real transform request, repeatability,
  invalid input, frontend production response and live OpenAPI schemas.

AI transformation, canonical analysis, evidence extraction and other output paths
remain unimplemented.

## v0.1.0 — Phase 0 foundation

Human-verified baseline; no remote release or publication.

- Added a minimal Next.js/React/TypeScript/Tailwind frontend shell.
- Added FastAPI health and capability endpoints; all seven output types are unavailable.
- Defined explicit provenance status vocabulary and architectural/honesty contracts.
- Added backend/frontend checks, dependency locks, CI and live OpenAPI verification.
- Added setup instructions, project-memory documents and challenge-deliverable outlines.

AI transformation, ingestion, extraction and generation are not implemented.
