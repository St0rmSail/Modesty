# Roadmap

**Current marker:** Build 0.8.1 - The Ledger
**Reviewed:** 2026-08-08

## Completed build line

| Build | Name | Demonstrated outcome |
|---|---|---|
| 0.2.1 | The Study Opens | Study renders and resizes without distortion |
| 0.3.0 | Modesty Takes Her Place | Independent character layer and relative placement |
| 0.3.1 | Grounded | Study-owned contact shadow |
| 0.4.0 | First Breath | Subtle frame-rate-independent breathing |
| 0.4.1 | Clear Eyes | Correct clear-eyed canonical standing asset and grounding |
| 0.5.0 | First Blink | Natural elapsed-time blinking |
| 0.6.0 | First Words | Bidirectional local conversation through `gemma4:e2b` |
| 0.7.0 | Yesterday | Persistent conversation history across restart |
| 0.8.0 | Personal Memory | Explicit personal facts with source/edit/delete controls |
| 0.8.1 | The Ledger | Project-wide design and implementation record aligned |

## Immediate sequence

### 0.9.0 - Grand Library Foundations

Definition of done:

- Create new Private and Shared local roots outside the repository.
- Register both roots in configuration without assuming `Data/Obsidian` is the live vault.
- Establish OKF-compatible `index.md` and note templates.
- Define default-private promotion rules and provenance fields.
- Add no online access.

### 0.10.0 - The Archivist

Definition of done:

- Implement the first bounded Team-member contract.
- Ingest Markdown without rewriting source notes unexpectedly.
- Validate metadata, hashes, visibility, and provenance.
- Propose classifications and links for Drew's approval.
- Report work and failure plainly through Modesty.

### 0.11.0 - Ask the Library

Definition of done:

- Build a local index, starting with SQLite FTS5.
- Retrieve from both zones locally while preserving zone on every result.
- Give Modesty source-linked passages rather than unsourced summaries.
- Support re-index, deletion, and stale-file detection.

### 0.12.0 - Library Gateway

Definition of done:

- Export bounded packets from Shared only.
- Preview and approve outbound knowledge.
- Apply redaction and size limits.
- Record an audit trail of what was shared and why.
- Provide no direct online-agent vault access.

## Later functional milestones

- Voice with explicit microphone control.
- Vision, screen understanding, and OCR with visible privacy state.
- Useful tools with confirmation, logging, and undo where practical.
- Executive routing, durable Team contracts, and persistent noticeboard state.
- Agentic planning, interruption, recovery, resume, and evidence-backed reporting.
- Living Study enrichment after corresponding backend capabilities work.

## Roadmap discipline

- Do not select a vector database before FTS5 retrieval demonstrates a real limitation.
- Do not add a Team member when a tool or ordinary module is sufficient.
- Do not polish animations ahead of functional capability.
- Review this roadmap whenever a build completes or a major decision changes.
