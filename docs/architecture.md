# Architecture — living Phase 1 skeleton

This concise source is the basis for the eventual **maximum-2-page** architecture
deliverable. Final paginated layout is future work, not a completed submission.

## Implemented walking skeleton

```text
Browser
  -> Next.js workspace (plain text + executive_summary choice)
  -> POST /api/v1/transform
  -> FastAPI typed request/response
  -> deterministic transformation service
  -> one executive_summary artifact
  -> browser result marked DETERMINISTIC STUB / NO AI
```

The browser uses a configured backend origin and makes a real HTTP request. FastAPI
validates plain text, the output selection and a 10,000-character conservative
source limit. The service normalizes whitespace and returns a bounded excerpt; it
does not summarize, call a model or fabricate citations/evidence. Capabilities
describe seven defined outputs, all `implemented: false`; only the executive-summary
deterministic stub advertises `stub_available: true` and `stub_mode: DETERMINISTIC_STUB`.
There is no storage, canonical extraction or AI provider.

## Planned content path — canonical components below remain unimplemented

```text
Source
  -> Ingestion
  -> Canonical Content Model
  -> Generation Controls
  -> Transformation Engine
  -> Validation/Grounding
  -> Render/Export
```

Generation controls are modeled in the walking-skeleton request as nullable fields,
but do not alter the deterministic stub. In the eventual system they parameterize
transformation of one canonical analysis; they do not cause each format generator to
reinterpret raw input independently. The future provider remains `<AI_PROVIDER_LATER>`.

| Future component | Intended responsibility |
| --- | --- |
| Source / Ingestion | Accept supported modalities; preserve source identity and locations |
| Canonical Content Model | One shared analysis with facts, uncertainty and evidence references |
| Generation Controls | Audience, tone, language, detail, objective and content style |
| Transformation Engine | Produce selected artefact structures from the same canonical analysis |
| Validation/Grounding | Check factual support, labels and requested output constraints |
| Render/Export | Render validated structures into requested artefacts |

## Invariants and boundaries

- Shared canonical analysis provides cross-output consistency, traceability, lower
  model cost/latency, simpler testing and extension (ADR-002).
- Source material is **data**, not privileged instructions or tool authorization.
- Provenance is explicit: OBSERVED / INFERRED / UNKNOWN / NOT_APPLICABLE.
  Future observed claims require evidence; missing data never becomes fabricated facts.
- The live FastAPI OpenAPI schema is authoritative; frontend contracts will derive from it.
- Phase 1 models output identifiers, status vocabulary, capability availability and
  typed walking-skeleton request/response contracts. CanonicalContent and
  EvidenceReference schemas belong to later work.

## Verification and deferred decisions

Backend route/engine tests, frontend component tests, lint/type checks, production
build and the live quick E2E/schema checks establish the vertical slice. CI runs the
same core checks. Provider selection, ingestion formats, evidence addressing,
canonical schema, generation strategy and artifact formats remain future decisions.
No database, queue or distributed infrastructure is justified by this iteration.
