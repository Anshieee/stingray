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
