# Architecture decisions

## ADR-001 — Next.js frontend + FastAPI backend

- **Status:** accepted for Phase 0.
- **Context:** the project needs a small typed UI and a Python-friendly analysis API.
- **Choice:** a simple monorepo with Next.js/React/TypeScript/Tailwind and npm in
  `frontend/`, FastAPI/Pydantic with Python 3.12, pytest and ruff in `backend/`.
- **Alternatives:** all-TypeScript application; Python-rendered UI; separate repositories.
- **Consequences:** straightforward ownership and generated API documentation, with two
  toolchains to verify. No database, orchestration stack or shared runtime is needed now.

## ADR-002 — Analyze once into canonical content

- **Status:** accepted architectural invariant; content processing is future work.
- **Context:** independently prompting each output risks contradictions, duplicated
  cost/latency and lost evidence across formats.
- **Choice:** ingest a source into one canonical content model, then apply generation
  controls and transform that shared analysis into selected output types.
- **Alternatives:** independent raw-source prompts per output; direct raw-source rendering.
- **Consequences:** enables consistency, factual traceability, lower model cost and
  latency, easier testing and extensibility. Requires a carefully designed later
  canonical schema; Phase 0 deliberately does not define it. Changing the invariant
  requires an explicit superseding decision.

## ADR-003 — FastAPI-generated OpenAPI is authoritative

- **Status:** accepted.
- **Context:** manually duplicated API specifications drift from application behaviour.
- **Choice:** Python routes and Pydantic models generate the live `/openapi.json`
  contract. Export it via HTTP when needed; keep transient exports ignored.
- **Alternatives:** hand-maintained OpenAPI JSON; a separate schema-first repository;
  duplicated TypeScript DTOs as authority.
- **Consequences:** route tests and generated schema describe the same application.
  Frontend client generation can be added later from this contract. Phase 0 has no
  frontend API client and no independently maintained OpenAPI document.

## ADR-004 — Explicit provenance states

- **Status:** accepted semantics; only the status vocabulary is modeled in Phase 0.
- **Context:** facts, system interpretation and absent data must remain distinguishable.
- **Choice:** `OBSERVED`, `INFERRED`, `UNKNOWN`, `NOT_APPLICABLE`, as detailed in the
  provenance contract. Future observed factual claims require `EvidenceReference`.
- **Alternatives:** a single confidence score; implicit null/default values; unlabelled prose.
- **Consequences:** future schemas/renderers must preserve claim-level provenance,
  evidence and explicit missingness. Confidence cannot substitute for evidence.
  No evidence-reference or complete canonical schema is implemented yet.

## ADR-006 — Deterministic line-ending normalization

- **Status:** accepted for Phase 2A.
- **Context:** segment offsets, character counts and digests need one stable basis.
- **Choice:** map CRLF to LF, then standalone CR to LF; preserve every other
  character exactly (no case/whitespace/Unicode/punctuation changes).
- **Alternatives:** whitespace-collapsing normalization; Unicode normalization.
- **Consequences:** offsets and SHA-256 are reproducible; semantic content is never
  silently mutated. Pinned by a literal 37-character oracle and fixed SHA-256.

## ADR-007 — Paragraph-based source segmentation

- **Status:** accepted for Phase 2A.
- **Context:** evidence needs stable, explainable locations without NLP models.
- **Choice:** group consecutive non-blank lines into paragraph segments separated by
  one or more blank/whitespace-only lines; exact `start/end` offsets with
  `normalized[start:end] == text`; zero-based source-relative order; deterministic
  hash IDs unique within one source.
- **Alternatives:** semantic chunking; token-based or embedding segmentation.
- **Consequences:** boring, testable segments with literal oracle offsets; no
  cross-edit stability is promised in this phase.

## ADR-008 — Evidence references by stable segment ID

- **Status:** accepted for Phase 2A.
- **Context:** observed claims need resolvable, minimal pointers.
- **Choice:** `EvidenceReference` holds only `segment_id`; cross-object validation
  proves the ID exists, offsets are valid and text matches the source slice.
- **Alternatives:** page numbers, timestamps, bounding boxes, confidence scores.
- **Consequences:** smallest sufficient contract for plain text; OBSERVED requires
  evidence while INFERRED/UNKNOWN/NOT_APPLICABLE may omit it; no numeric confidence.

## ADR-009 — Structural validation is not semantic entailment

- **Status:** accepted limitation for Phase 2A.
- **Context:** a syntactically valid reference can still misstate its passage.
- **Choice:** `validate_canonical_against_source()` enforces digests, counts,
  catalog correspondence, uniqueness, ordering, offsets, slice equality and
  evidence resolvability loudly without silent repair; semantic entailment is
  explicitly out of scope.
- **Alternatives:** claiming grounding/fact verification from structural checks.
- **Consequences:** honest boundaries for future AI/grounding work; no false
  verification claims.

## ADR-005 — Source content is data, never privileged instructions

- **Status:** accepted.
- **Context:** documents may include quoted commands or adversarial instructions such
  as "Ignore all previous instructions."
- **Choice:** supplied/source text is data. It cannot override application instructions,
  tool permissions, output contracts or provenance requirements.
- **Alternatives:** concatenating source and control text without trust boundaries;
  executing commands found in source material.
- **Consequences:** future ingestion/prompt/tool boundaries must preserve this separation
  and be tested with adversarial source text. Phase 0 has no source-processing path,
  so it documents the rule rather than claiming runtime prompt-injection protection.

## ADR-010 — Provider returns semantic analysis only

- **Status:** accepted for Phase 2B.
- **Context:** letting a model generate digests, offsets or segment IDs risks
  unresolvable evidence and false provenance.
- **Choice:** `CanonicalSemanticAnalysis` carries semantic claims plus references;
  `analyze_source()` combines it with server-owned metadata/segments.
- **Alternatives:** provider-generated full canonical content trusted after parse.
- **Consequences:** source identity stays deterministic; provider output with
  unknown IDs or missing OBSERVED evidence fails loudly without silent repair.

## ADR-011 — Provider abstraction precedes transformation generation

- **Status:** accepted for Phase 2B.
- **Context:** output generators must share one analysis rather than re-prompting.
- **Choice:** `AnalysisProvider` protocol with `analyze(PreparedSource)`; route and
  service depend on the protocol, OpenAI specifics stay in the adapter.
- **Alternatives:** OpenAI calls embedded in the route; per-output raw-source prompts.
- **Consequences:** fake providers inject cleanly; no SDK leakage into domain code.

## ADR-012 — Provider-native structured output over ad-hoc JSON parsing

- **Status:** accepted for Phase 2B.
- **Context:** scraped JSON (braces search, fence stripping, eval, repair loops)
  produces brittle, silently malleable provenance.
- **Choice:** `client.responses.parse(..., text_format=CanonicalSemanticAnalysis)`
  with Pydantic validation; refusals/None parsed output are controlled failures.
- **Alternatives:** Markdown-JSON prompts with `json.loads(output_text)` recovery.
- **Consequences:** schema violations fail honestly; timeout (30s) and
  max_retries (1) stay explicit and finite.

## ADR-013 — Automated tests never spend real model tokens

- **Status:** accepted for Phase 2B.
- **Context:** CI and live verification must be reproducible without credentials.
- **Choice:** injected fake providers and mock SDK clients in tests; the live
  verifier scrubs provider env vars from its child backend and only proves the
  unconfigured 503 path. No `AI_PROVIDER=fake` production fallback exists.
- **Alternatives:** live-model integration tests; fake provider mode in production.
- **Consequences:** zero external AI calls in automation; real-provider smoke is a
  documented human-only action.
