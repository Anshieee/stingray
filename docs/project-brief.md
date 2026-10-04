# Project brief

## Goal

AI-powered multimodal transformation of a common information source into one or
more configurable communication artefacts. Understand the source once and reuse
one canonical analysis across outputs. This is a hackathon/evaluation project with
a technically defensible architecture, rather than unrelated per-format prompts.

## Eventual sources (not implemented)

Plain English text, prompts, articles, reports, policy documents, incident reports,
advisories, research papers, other documents, images, videos and contextual information.
All source content is data, even when it contains apparent instructions.

## Required outputs (defined, not implemented)

| Artefact | API identifier |
| --- | --- |
| Video Package | `video_package` |
| LinkedIn Post | `linkedin_post` |
| Twitter/X Post or Thread | `x_post` |
| Advisory | `advisory` |
| Infographic | `infographic` |
| Executive Summary | `executive_summary` |
| Presentation | `presentation` |

## Required generation controls (future)

- Target audience
- Tone
- Language
- Detail level
- Communication objective
- Content style

## Required challenge deliverables

- Source code repository
- README with setup instructions
- Architecture document: **maximum 2 pages**
- Demo video: **maximum 2 minutes**
- Technical presentation: **maximum 5 slides**

Phase 0 established the repository/docs foundations. Phase 1 proves one browser-to-API
deterministic integration slice without AI. See [deliverable outlines](deliverables.md);
do not claim a video or deck already exists.

## Explicit non-goals

- Full CMS
- Direct social publishing
- Enterprise RBAC
- Custom model training
- Fine-tuning
- Distributed orchestration
- Arbitrary workflow builder

## Phase 1 boundary

Plain text is the only input path. `executive_summary` is the only exposed output
path and is a deterministic integration stub, not AI. There is no live AI, credentials,
document/media/URL ingestion, uploads, canonical extraction, evidence references,
grounding, export generation, auth, persistence, workers, deployment or external
publication. Runtime provider selection is deferred: `<AI_PROVIDER_LATER>`.
