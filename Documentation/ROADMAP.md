# Roadmap

**Current marker:** Build 0.10.0 - The Archivist (in progress)
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
| 0.8.2 | The Living Bookshelf | Filing Cabinet, Bookshelf growth, and Grand Library mode canonised |
| 0.9.0 | Cabinet and Bookshelf Foundations | Both external stores safely initialized and demonstrated |

## Immediate sequence

### 0.9.0 - Cabinet and Bookshelf Foundations - Complete

Definition of done:

- Create the private Filing Cabinet Obsidian vault outside the repository.
- Create the separate living Bookshelf repository with Inbox, Workbench, collections, and Archive.
- Register both roots in configuration without assuming `Data/Obsidian` is the live vault.
- Establish OKF-compatible Bookshelf indexes and templates.
- Encode provenance and the Routine, Normal, Important, and Protected trust levels.
- Add no online access.

Demonstrated on 2026-08-08 at `E:\Modesty Filing Cabinet` and `E:\Modesty Bookshelf`.

### 0.10.0 - The Archivist

Read-only inventory, origin tracking, content hashing, stale-record cleanup, and structural Bookshelf metadata warnings were demonstrated on 2026-08-08. The catalogue remains local and ignored by Git. The Archivist Bobblehead and Modesty's headset are now required visual work because the first Team backend exists.

Definition of done:

- Implement the first bounded Team-member contract.
- Ingest Markdown without rewriting source notes unexpectedly.
- Validate metadata, hashes, store identity, and provenance.
- Propose classifications and links for Drew's approval.
- Curate returned material from Inbox through Workbench onto the Bookshelf.
- Report work and failure plainly through Modesty.
- Add the Archivist's stern-librarian Bobblehead and Modesty's Team headset, driven by truthful subsystem state.

### 0.11.0 - Ask the Library

Definition of done:

- Build a local index, starting with SQLite FTS5.
- Retrieve from both stores locally while preserving origin on every result.
- Give Modesty source-linked passages rather than unsourced summaries.
- Support re-index, deletion, and stale-file detection.

### 0.12.0 - Library Gateway

Definition of done:

- Explicitly open and close Grand Library online mode.
- Export bounded loans from the Bookshelf only.
- Preview consequential outbound knowledge.
- Apply redaction and size limits.
- Receive sourced returns into the Bookshelf Inbox.
- Record an audit trail of what was borrowed, returned, and why.
- Provide no direct online-agent access to either local store.

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
