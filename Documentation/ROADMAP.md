# Roadmap

**Current marker:** Build 0.12.0 - Library Gateway (in progress)
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
| 0.10.0 | The Archivist | Approval-gated local knowledge curation and truthful Team representation |
| 0.11.0 | Ask the Library | Local source-linked passage retrieval across both knowledge stores |

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

### 0.10.0 - The Archivist - Complete

Read-only inventory, origin tracking, content hashing, stale-record cleanup, and structural Bookshelf metadata warnings were demonstrated on 2026-08-08. The catalogue remains local and ignored by Git.

Private filing and retrieval, shared Inbox filing, review, Workbench promotion, collection proposal, and final filing were also demonstrated through Modesty. Every consequential Bookshelf move waited for Drew's explicit approval.

The Archivist Bobblehead, `LATE FOR WORK` state, desk-lamp readiness indication, full-height dismissible right-side conversation panel, and Modesty's Team headset were demonstrated and accepted. Build 0.10.0 is complete.

Definition of done:

- Implement the first bounded Team-member contract.
- Ingest Markdown without rewriting source notes unexpectedly.
- Validate metadata, hashes, store identity, and provenance.
- Propose classifications and links for Drew's approval.
- Curate returned material from Inbox through Workbench onto the Bookshelf.
- Report work and failure plainly through Modesty.
- Add the Archivist's stern-librarian Bobblehead and Modesty's Team headset, driven by truthful subsystem state.

### 0.11.0 - Ask the Library - Complete

SQLite FTS5 passage indexing now covers both knowledge stores while preserving private/shared origin and exact relative paths. Normal questions refresh changed, moved, and deleted files before searching; an explicit re-index command performs a complete rebuild. Drew accepted the echo-free, source-linked response through Modesty on 2026-08-08.

Definition of done:

- Build a local index, starting with SQLite FTS5.
- Retrieve from both stores locally while preserving origin on every result.
- Give Modesty source-linked passages rather than unsourced summaries.
- Support re-index, deletion, and stale-file detection.

### 0.12.0 - Library Gateway

Step One was demonstrated on 2026-08-09 using a strictly local loopback provider. The Gateway starts closed, requires an explicit open command, previews an immutable bounded packet, accepts only its exact loan ID, quarantines the return in the Bookshelf Inbox, records a content-free audit trail, cancels pending loans on close, and starts closed again after restart. Automatic source selection was removed after a structural Bookshelf index passage proved irrelevant; outbound Bookshelf evidence now requires future explicit selection.

Step Two implements Windows current-user encrypted storage for the Smithsonian API key and a separate one-purpose HTTPS validation command. Validation calls only the Smithsonian Open Access statistics endpoint, retains no response content, and audits only provider, endpoint, outcome, and HTTP status when applicable.

Step Two was demonstrated in `E:\Modesty` on 2026-08-09. Step Three implements a distinct Smithsonian online state, exact packet preview and approval, a maximum five-record Open Access search, source-linked formatting, and an unverified Inbox return. After the Open Access API proved unable to supply the originally proposed Kathleen McNulty article evidence, Drew approved retargeting the first trophy to the exact Smithsonian record for ENIAC Accumulator #2. The provider refuses every other question.

The final clean expedition, loan `GL-20260809-2BCA584B`, retrieved one exact NMAH record with a resolvable Smithsonian ARK citation and no leaked secret or local path. The Gateway closed with no pending loan. The Archivist reviewed the quarantined return, moved it to Workbench only after approval, classified it as Research, and filed it physically in `E:\Modesty Bookshelf\Research` after a second explicit approval. Inbox and Workbench were left clear. The first complete online knowledge lifecycle is demonstrated.

The Gateway now enforces a fail-closed text-only return policy before any Inbox write. Media, embeds, raw HTML, active or local URI schemes, control characters, non-text values, and size overruns are refused. Future media intake remains disabled until the separate controls in [MEDIA_RETURN_POLICY.md](MEDIA_RETURN_POLICY.md) exist. The refusal suite passed in `E:\Modesty` on 2026-08-09.

The final Study sequence is implemented pending Drew's visual review. Only real online mode opens a cyan portal and lightning mark over the Bookshelf; local loopback remains visually ordinary. The chat panel hides briefly for the reveal, restores automatically, and carries a persistent illuminated online badge until explicit closure. Startup resets the visual state closed.

Definition of done:

- Explicitly open and close Grand Library online mode.
- Export bounded loans from the Bookshelf only.
- Preview consequential outbound knowledge.
- Apply redaction and size limits.
- Receive sourced returns into the Bookshelf Inbox.
- Record an audit trail of what was borrowed, returned, and why.
- Provide no direct online-agent access to either local store.

## Later functional milestones

- Local voice after the deferred audition and explicit selection recorded in [VOICE.md](VOICE.md), with separate explicit microphone control for listening.
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
