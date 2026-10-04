# Architecture — living Phase 2A foundation

This concise source is the basis for the eventual **maximum-2-page** architecture
deliverable. Final paginated layout is future work, not a completed submission.

## Implemented walking skeleton (unchanged)

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
There is no storage, AI provider or model call. A deterministic canonical layer
exists internally but is not exposed over HTTP.

## Implemented Phase 2A deterministic layer — no AI analysis

```text
Raw text
  -> normalize_source_text() (CRLF/CR to LF, all else preserved)
  -> PreparedSource (normalized text, SourceMetadata, SourceSegment[])
  -> CanonicalContent shell (metadata + segment catalog, empty semantics)
  -> validate_canonical_against_source() (loud structural checks)
```

Normalization is line-ending only. Segmentation is paragraph-oriented: one or more
blank/whitespace-only lines separate segments; offsets are exact character indices
with `normalized[start:end] == segment.text`; order is zero-based source-relative;
IDs are deterministic hashes (no UUID/timestamp) unique within one source. Identity
is UTF-8 SHA-256 plus character/segment counts. `EvidenceReference` holds only a
segment ID. `ProvenancedClaim` reuses `ProvenanceStatus` with OBSERVED requiring
evidence and no numeric confidence. `CanonicalContent` carries metadata, the segment
catalog and semantic slots (title/summary plus facts, entities, dates, statistics,
key messages, risks, recommendations, unknowns) that may legitimately be empty.
An empty-shell helper copies source identity without inventing semantics.

## Planned content path — AI analysis below remains unimplemented

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
  typed walking-skeleton request/response contracts. Phase 2A adds internal
  `CanonicalContent`, `EvidenceReference` and structural validation; AI-driven
  canonical extraction and semantic grounding belong to later work.

## Verification and deferred decisions

Backend route/engine tests, frontend component tests, lint/type checks, production
build and the live quick E2E/schema checks establish the vertical slice. CI runs the
same core checks. Provider selection, ingestion formats, evidence addressing,
canonical schema, generation strategy and artifact formats remain future decisions.
No database, queue or distributed infrastructure is justified by this iteration.
