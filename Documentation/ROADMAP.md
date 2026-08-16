# Roadmap

**Current marker:** Build 0.18.0 - Story Comparison (complete)
**Reviewed:** 2026-08-16

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
| 0.12.0 | Library Gateway | Fail-closed bounded online loans, first curated expedition, media boundary, and truthful Study state |
| 0.13.0 | The Researcher | Visible bounded Scribble Hub discovery, coherent Briefings, explicit disposition, and truthful Team presentation |
| 0.14.0 | Time and Presence | Session truth, elapsed absence, clean/interrupted recovery, local greetings, and offline working-zone conversion |

## Active build

### 0.18.0 - Story Comparison - Complete

Strengthen Researcher Level 3 with bounded same-source-type corroboration. Drew can collect two or three visible public Scribble Hub story pages and request one comparison Briefing. The Researcher distinguishes shared signals, candidate differences, visible cautions, reader-report limits, and likely duplicate or cross-post leads while retaining every direct source.

Definition of done:

- Collect two or three distinct current story pages without filing or account action.
- Compare shared and distinguishing metadata rather than concatenating separate reports.
- Preserve per-story sources and keep reader reports separate from observed page facts.
- Detect strong title/synopsis similarity as a duplicate or cross-post lead, never proof.
- Refuse one-item, duplicate-source, and oversized comparison sets.
- Demonstrate the comparison through the existing Pending Report and Briefing lifecycle in `E:\Modesty`.
- Keep Level 4 unearned until a later build synthesizes distinctly different source types.

Demonstrated on 2026-08-16: Drew collected distinct live Scribble Hub story pages, returned to the listing between selections, produced the comparison Briefing, inspected its source/evidence boundaries, and completed disposition. All 96 live tests passed.

### 0.17.0 - Story Investigation - Complete

Extend the proven visible-browser Researcher workflow from category discovery to one bounded story-page evidence pass. The generic investigation contract separates observed facts, reported evidence, cautions, missing evidence, recommendation strength, sources, and retrieval time. The first adapter reads only the current visible public Scribble Hub story page. Account actions, chapter acquisition, mirroring, and access-control bypass remain excluded.

Definition of done:

- Investigate the currently visible public Scribble Hub story page without account action.
- Distinguish page facts from reader reports and retain a direct source.
- State cautions and missing evidence instead of implying certainty about hidden content.
- Return the investigation through the existing Pending Report and Briefing lifecycle.
- Document the visible control in deterministic Researcher help.
- Demonstrate the complete flow in `E:\Modesty` before marking the build complete.

Demonstrated on 2026-08-16: a real public Scribble Hub story page produced the evidence-led Briefing after the embedded-browser JSON transport was made explicit. All 93 live tests passed.

### 0.16.0 - Schedule and Reminders - Complete

Persistent local reminders, explicit dates, stable IDs, deterministic help, due/overdue opening-address context, and a readable lifecycle surface are implemented and demonstrated. Calendar accounts, recurrence, natural-language date guessing, and background notification delivery remain future work.

### 0.15.0 - The Personal Chronicle - Complete

The local structured episode store, compact validation, bounded active-only recall, narrative-only prompt boundary, input/transcript retrieval, and user review window are implemented and demonstrated. Persistence, correction, concrete recall, false-premise rejection, factual-evidence refusal, and retirement exclusion passed live. Autonomous self-authored episodes and bulk generation are deliberately excluded from this foundation.

Definition of done:

- Persist compact explicitly narrative episodes across restart.
- Let Drew add, inspect, correct, retire, and delete episodes visibly.
- Retrieve only a few relevant active episodes for a conversation topic.
- Preserve provenance and last-recalled time.
- Demonstrate that Modesty may use an episode as analogy but not factual evidence.
- Keep autonomous episode creation disabled until the inspectable path is accepted.

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

### 0.12.0 - Library Gateway - Complete

Step One was demonstrated on 2026-08-09 using a strictly local loopback provider. The Gateway starts closed, requires an explicit open command, previews an immutable bounded packet, accepts only its exact loan ID, quarantines the return in the Bookshelf Inbox, records a content-free audit trail, cancels pending loans on close, and starts closed again after restart. Automatic source selection was removed after a structural Bookshelf index passage proved irrelevant; outbound Bookshelf evidence now requires future explicit selection.

Step Two implements Windows current-user encrypted storage for the Smithsonian API key and a separate one-purpose HTTPS validation command. Validation calls only the Smithsonian Open Access statistics endpoint, retains no response content, and audits only provider, endpoint, outcome, and HTTP status when applicable.

Step Two was demonstrated in `E:\Modesty` on 2026-08-09. Step Three implements a distinct Smithsonian online state, exact packet preview and approval, a maximum five-record Open Access search, source-linked formatting, and an unverified Inbox return. After the Open Access API proved unable to supply the originally proposed Kathleen McNulty article evidence, Drew approved retargeting the first trophy to the exact Smithsonian record for ENIAC Accumulator #2. The provider refuses every other question.

The final clean expedition, loan `GL-20260809-2BCA584B`, retrieved one exact NMAH record with a resolvable Smithsonian ARK citation and no leaked secret or local path. The Gateway closed with no pending loan. The Archivist reviewed the quarantined return, moved it to Workbench only after approval, classified it as Research, and filed it physically in `E:\Modesty Bookshelf\Research` after a second explicit approval. Inbox and Workbench were left clear. The first complete online knowledge lifecycle is demonstrated.

The Gateway now enforces a fail-closed text-only return policy before any Inbox write. Media, embeds, raw HTML, active or local URI schemes, control characters, non-text values, and size overruns are refused. Future media intake remains disabled until the separate controls in [MEDIA_RETURN_POLICY.md](MEDIA_RETURN_POLICY.md) exist. The refusal suite passed in `E:\Modesty` on 2026-08-09.

The final Study sequence was accepted on 2026-08-09. Only real online mode opens a five-second concealed shelf panel and reveals the illuminated Grand Library globe; local loopback remains visually ordinary. The chat panel clears for the reveal, restores automatically, and carries a persistent illuminated online badge until explicit closure. The effect remains attached to its marked shelf bay during resize, closing removes every online signal, and startup resets closed. Provider-neutral opening language keeps the Grand Library distinct from the Smithsonian expedition.

Definition of done:

- Explicitly open and close Grand Library online mode.
- Export bounded loans from the Bookshelf only.
- Preview consequential outbound knowledge.
- Apply redaction and size limits.
- Receive sourced returns into the Bookshelf Inbox.
- Record an audit trail of what was borrowed, returned, and why.
- Provide no direct online-agent access to either local store.

## Later functional milestones

### 0.13.0 - The Researcher - Complete

The visible local browser handoff, bounded Scribble Hub discovery, concise Return, Pending Report, functional Briefing Hologram, restart recovery, explicit disposition controls, reversible duty movement, and truthful headset state are implemented and demonstrated. The Researcher Bobblehead and its runtime state are live. The physical Grand Library globe, Bobblehead pedestal perspective, dedicated gesturing sprite, and more characterful movement arcs are deferred visual polish rather than functional blockers. See [RESEARCHER.md](RESEARCHER.md) and [BRIEFING_HOLOGRAM.md](BRIEFING_HOLOGRAM.md).

The Briefing duty movement now uses separate bottom-right geometry, travels with its grounding shadow, suppresses the open Grand Library alcove while the Briefing is visible, and reverses to the exact accepted standing geometry. The dedicated gesturing pose asset and a more characterful movement path remain visual-polishing work; neither may alter the accepted neutral pose or duty endpoints.

### 0.14.0 - Time and Presence - Complete

Truthful local time, an atomic session heartbeat ledger, clean-versus-interrupted shutdown detection, elapsed-absence greetings, the offline/background/present/working state foundation, and immediate offline working-zone conversion are implemented. Clean nine-minute and sub-minute restarts passed live; isolated interrupted recovery produced the correct last-heartbeat warning. See [TIME_AND_PRESENCE.md](TIME_AND_PRESENCE.md).

Background hosting, schedule editing, calendar integration, authorized maintenance windows, narrative vignettes, day/night visuals, and tablet access build on this foundation later. A readable Study clock is welcome polish but cannot block the operational milestone.

### Later - The Librarian

Implement the private reading collection and source inventory before bulk conversion. Begin with a read-only sample, immutable originals, a transformation ledger, one repaired derivative, and explicit review of uncertain corrections. Calibre integration, cross-platform Story Records, update tracking, and reading continuity follow only after that foundation is demonstrated. See [LIBRARIAN.md](LIBRARIAN.md).

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
- Treat command help as part of implementation: update the local guide and tolerant deterministic help tests before closing any command-bearing build.
