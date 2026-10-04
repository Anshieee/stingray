# Architecture — living Phase 0 skeleton

This concise source is the basis for the eventual **maximum-2-page** architecture
deliverable. Final paginated layout is future work, not a completed submission.

## Implemented foundation

```text
Browser -> Next.js informational shell (frontend/)
HTTP client -> FastAPI (backend/)
                |-- GET /health
                |-- GET /api/v1/capabilities
                `-- generated OpenAPI / documentation
```

There is **no browser-to-API integration yet**. The frontend uses React, strict
TypeScript and Tailwind; the API uses Python 3.12 and Pydantic. Capabilities describe
seven defined outputs, all `implemented: false`. There is no storage or AI provider.

## Planned content path — all components below are unimplemented

```text
Source
  -> Ingestion
  -> Canonical Content Model
  -> Generation Controls
  -> Transformation Engine
  -> Validation/Grounding
  -> Render/Export
```

Generation controls parameterize transformation of the canonical analysis; they do
not cause each format generator to reinterpret raw input independently. The future
provider remains `<AI_PROVIDER_LATER>`.

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
- Phase 0 models only output identifiers, status vocabulary and capability availability.
  CanonicalContent and EvidenceReference schemas belong to later work.

## Verification and deferred decisions

Backend route tests, a frontend component test, lint/type checks, production build
and live HTTP/schema checks establish the foundation. CI runs the same core checks.
Provider selection, ingestion formats, evidence addressing, canonical schema,
generation strategy and artifact formats remain future decisions. No database,
queue or distributed infrastructure is justified by this iteration.
