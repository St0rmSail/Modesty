# Roadmap

**Current marker:** Build 0.28.0 - Bounded Intake Shelving Desk (complete); Build 0.29.0 Metadata Review Desk next; Build 0.19 acceptance paused externally
**Reviewed:** 2026-08-19

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

## Paused build

### 0.19.0 - Mixed-Source Research - Implemented; Live Acceptance Paused

Attempt the Researcher's Level 4 threshold with one bounded mixed-source duty: synthesize observed Scribble Hub story-page evidence and speaker-reported YouTube transcript passages in one claim-linked Briefing.

Definition of done:

- Accept one explicit public YouTube video URL after exactly one story page is selected.
- Retrieve a bounded public English transcript without login, cookies, account action, or API key.
- Keep the network operation off the Study interface thread.
- Preserve direct story and timestamped video provenance.
- Distinguish observed page metadata from statements made by a video's speaker.
- Surface overlap, conflicts, missing corroboration, generated-caption status, and retrieval limits.
- Fail closed when captions are unavailable or YouTube refuses access.
- Demonstrate the complete mixed-source Briefing and disposition in `E:\Modesty`.
- Award Level 4 only after the live report is coherent, source-linked, and honest about what it did not prove.

Pause record, 2026-08-16: implementation and all 102 live automated tests pass. The planned real pairing could not complete because Scribble Hub returned persistent Cloudflare 522 origin timeouts. Resume from the live mixed-source Briefing test after the service recovers; do not rebuild the adapter, award Level 4, or call the build failed on the strength of an external outage.

## Active build

### 0.26.0 - Reversible Exact-Duplicate Resolution - Complete

Resolve proven byte-identical clutter without deleting a reading source or guessing which path Drew values.

Definition of done:

- Accept only one current exact SHA-256 duplicate group.
- Require Drew to name the exact member that remains canonical.
- Prepare a persistent `DR-ID` and show every proposed Archive move before action.
- Recheck all source hashes and refuse occupied destinations at approval time.
- Retain redundant copies under a hash-labelled Archive path preserving former location context.
- Delete nothing and exclude shared-identifier or possible-work groups.
- Roll back completed moves when a later filesystem move fails where practical.
- Redirect exact-edition reading continuity to the chosen canonical path.
- Update deterministic help and pass the complete live suite.

Acceptance should resolve one expendable or approved real exact pair, verify the chosen copy remains byte-identical, verify the redundant copy exists in Archive, and confirm the review no longer reports that group.

Accepted on 2026-08-19: Drew chose the Handbooks copy of `D&D 3.5E - Song And Silence.pdf` as canonical. Resolution `DR-44C88BB7` rechecked SHA-256 `e5b44f628756494cb01e44ef2d919c4e7395de52339000ad6a824cde560d3602`, retained the canonical file in place, and moved the redundant root Intake copy into its hash-labelled Archive path. Both retained files remained 22,666,472 bytes and nothing was deleted. All 123 tests passed.

### 0.27.0 - Natural Librarian Control Surface - Complete

The expanding deterministic command vocabulary has become a functional usability defect. Normal guided work must accept concise contextual language such as `show me the duplicates`, `keep the Handbooks copy`, `yes, do that`, `open Axeman at chapter 12`, and `save my place`. Stable IDs and exact commands remain internal safety and audit mechanisms, not mandatory syntax Drew must memorize. This must be solved before additional Librarian duties or visual polish.

Definition of done:

- Translate a small natural vocabulary into the existing audited Librarian operations.
- Retain the reviewed edition groups, one prepared duplicate action, and one active reading passage only within the current Study session.
- Resolve a natural copy description only against the displayed group paths and ask for distinction when zero or several match.
- Permit contextual approval only for the single duplicate-resolution preview prepared in that session.
- Preserve explicit confirmation before any file move and retain exact commands for recovery and audit.
- Support natural chapter opening, continuation, place saving, and restart-safe resume without silently advancing progress.
- Update deterministic help and pass the complete live suite.

Acceptance should naturally review the remaining real duplicate groups, prepare one approved exact pair without moving it, confirm with `yes, do that`, and verify both canonical and Archive results. It should also open Axeman at Chapter 12, continue, save, restart, and resume using natural wording. An intentionally vague copy choice must stop for clarification without preparing or moving anything.

Accepted on 2026-08-19: the natural duplicate dialogue clarified an ambiguous choice, prepared and approved only the selected exact-hash action, and retained the underlying confirmation boundary without requiring Drew to type a hash or job identifier. The natural chapter-open, continue, save, restart, and resume sequence also passed without requiring an `RP-ID`. All 127 automated tests passed.

### 0.28.0 - Bounded Intake Shelving Desk - Complete

Turn the existing single-book shelving proof into a useful but controlled Intake workflow. The Librarian should prepare a small catalogue-backed batch, distinguish items with sufficient source metadata from uncertain or conflicting editions, and present coherent proposed homes before any move. Drew should be able to select and approve naturally; exact IDs remain underneath for audit.

The build must not become a blind bulk organizer. It may not guess authors or titles from prose, overwrite a destination, merge non-identical editions, approve its own proposal, or move an uncertain item merely to empty Intake. Source hashes and destination availability are rechecked at approval. Live acceptance requires one small approved batch and one deliberately held-back ambiguous item.

**Overnight pause, 2026-08-19:** Build 0.27 is accepted, all 127 tests pass, and its restore-point paperwork is reconciled. Resume by reviewing the existing single-item shelving and edition-catalogue APIs, then specify the bounded proposal object and natural review dialogue before writing move logic.

Implementation candidate, 2026-08-21: the Desk prepares at most five Ready items from existing source metadata, displays held-back reasons, persists one superseding batch preview, and accepts natural `shelve those` approval. Every source and destination is preflighted before movement; successful moves retain hashes and update local edition/reading references. Focused coverage includes batch bounds, edition and unknown-metadata holds, no-move preview, stale-source refusal before the first move, natural approval, and ambiguous contextual-confirmation refusal.

Accepted on 2026-08-21: the real preview showed five Ready, 28 held, and 39 later-eligible items. Drew removed CRUMPETS naturally and approved four destinations. Physical verification confirmed the four Originals, absent former Intake paths, retained CRUMPETS, resolved batch ledger, and updated edition paths/hashes. All 132 tests passed.

### 0.29.0 - Metadata Review Desk - Next

Turn unknown or incomplete source identity into a reviewable correction problem without pretending a filename is authoritative metadata. Present a small held-item set with existing embedded fields, clearly labelled filename-derived suggestions where useful, and editable title/author values. Drew's explicit confirmation may update local catalogue metadata and prepare a shelving destination; inference alone may not.

The build must retain source hashes, record original metadata and every confirmed correction, refuse ambiguous bulk approval, avoid rewriting the source file, and keep edition-conflict review separate. Live acceptance should correct one genuinely incomplete item, reject or leave one uncertain suggestion, and then show the corrected item entering an ordinary bounded shelving preview.

### 0.25.0 - Edition Review Desk - Complete

Expose the real files behind edition relationship counts before asking Drew to choose anything.

Definition of done:

- List exact paths, formats, and sizes for bounded relationship groups.
- Present exact hashes, shared strong identifiers, and possible title/author matches as distinct evidence classes.
- Show a relationship once at its strongest useful evidence level, except when an additional non-identical file expands a shared-identifier group.
- Exclude generic untitled and unknown-author records from weak same-work grouping.
- Keep preferred-edition selection, consolidation, deletion, and shelving out of this read-only review.
- Update deterministic help and pass the complete live suite.

Acceptance passed on 2026-08-19. The real review returned four bounded groups: exact duplicate pairs for `Song And Silence`, `Gunmetal Magic`, and `Stronghold Builder's Guide`, plus one non-identical `Magic in the Blood` pair sharing ISBN 9780451462671. No weak title/author group qualified because the remaining apparent filename matches lacked trustworthy author metadata; generic unknown-author and untitled records were correctly suppressed. Every exact path, format, and byte size was shown, and no file changed. All 122 tests passed.

### 0.24.0 - Work and Edition Identity - Complete

Establish trustworthy bibliographic identity before any bulk shelving or consolidation.

Definition of done:

- Incrementally catalogue supported reading files beneath Intake and Originals.
- Preserve source-supplied title, author, identifiers, series, series number, publisher, language, and publication date.
- Reuse unchanged records by path, size, and modification identity.
- Refresh at most 25 changed or new files per invocation and report the remainder.
- Prove exact duplicates only by matching SHA-256.
- Treat shared strong identifiers as same-publication leads and normalized title/author as weaker same-work leads.
- Report metadata failures without preventing unrelated files from being catalogued.
- Never merge, rename, move, delete, overwrite, or select a preferred edition automatically.
- Update deterministic help and pass the complete live suite.

Acceptance should demonstrate the command on the real Stacks, confirm useful series/identifier counts, then repeat it to prove incremental reuse. Review screens, preferred-edition decisions, and bulk shelving follow this identity foundation.

Accepted on 2026-08-19: three bounded refresh passes catalogued 75 readable files with no metadata failures. The completed catalogue represents 27 named authors, 10 named series, three exact duplicate groups, two shared strong-identifier groups, and six possible title/author same-work groups. A fourth pass refreshed zero files, reused all 75 unchanged entries, and reported zero remaining. No reading file moved or changed. All 122 automated tests passed.

### 0.23.0 - Reading Continuity - Complete

Make the Librarian's extracted text resumable without guessing what Drew has read.

Definition of done:

- Recognize conservative human chapter headings within EPUB spine documents.
- Open a named exact edition at a requested chapter and return a bounded passage.
- Continue through bounded passages without silently changing permanent progress.
- Save progress only after an explicit `Mark my place: RP-ID` command.
- Resume after restart at the next unread character of the exact SHA-256 edition.
- Refuse missing positions, changed editions, ambiguous titles, unsafe paths, and stale sessions.
- Preserve page or section labels when no reliable chapter heading exists.
- Keep progress local, private, and separate from Filing Cabinet and Bookshelf knowledge.
- Update deterministic help and pass the complete live suite before acceptance.

The dedicated reading display, bookmarks, annotations, device synchronization, and automatic update tracking remain later work.

Accepted on 2026-08-19: Axeman opened directly at human `Chapter 12`, continued under one temporary `RP-ID`, saved progress only after Drew explicitly marked the displayed endpoint, and resumed from the next unread text after restart. Opening the exact edition also refreshed old generic EPUB section labels in its local passage index. All 120 live automated tests passed.

### 0.22.0 - The Librarian Reads the Stacks - Complete

Turn the Intake manifest into a useful private catalogue. The Librarian reads one named supported work, records honest bibliographic identity and source-linked passages, proposes coherent shelving, and moves the unchanged original only after exact approval.

Definition of done:

- Read TXT, Markdown, HTML, DOCX, EPUB, and text-layer PDF without executing embedded content.
- Accept safe relative paths beneath nested Intake folders.
- Report title, author, readable extent, bounded opening text, source hash, and extraction limits.
- Build a private local passage index and return bounded source-linked matches from examined works.
- Propose `Originals/Author/Title/original-file` without pretending uncertain metadata is known.
- Move nothing until exact `LS-ID` approval; recheck the source hash and refuse collisions.
- Keep originals byte-identical and keep copyrighted contents out of the Filing Cabinet and Bookshelf.
- Fail clearly for image-only PDF, DRM, archive containers, and formats whose reader is not implemented.
- Update deterministic command help and pass the full live test suite before acceptance.

Accepted on 2026-08-19: the Librarian read the real `Axeman` EPUB as 167,521 words across nine EPUB spine sections and returned five indexed matches for distinctive Chapter 12 wording. This proves that extraction reached the later chapter; the displayed section numbers describe EPUB spine documents rather than human chapter numbers. Detecting chapter headings and reporting human chapter labels is deferred explicitly to reading continuity. The common capability level remains Level 2 because this build strengthens bounded retrieval and collection handling rather than performing an evidence-led investigation.

### 0.21.0 - The Librarian's First Repair - Complete

Prove one reversible transformation without risking an original. The Librarian accepts one explicitly named UTF-8 `.txt` or `.md` file directly inside Intake, limited to 2 MiB, and creates a provisional mechanically repaired derivative in Workbench. A persistent transformation ledger records source and derivative identity, hashes, applied actions, cautions, timestamps, and final disposition.

Definition of done:

- Preserve the named Intake original byte-for-byte and never rename or move it.
- Restrict the first repair to safe newline and whitespace normalization; do not guess hyphenation, paragraph joins, missing text, or meaning-changing corrections.
- Create only one hashed provisional derivative in Workbench.
- Record every applied action and caution in the local Librarian ledger.
- Re-check source and derivative hashes before approval.
- Present the result through a local Briefing with Keep Repair and Toss Repair controls.
- Keep leaves the derivative in Workbench; Toss deletes only that derivative; neither route files reading material through the Archivist.
- Document the deterministic command and demonstrate both dispositions on expendable samples.
- Pass the complete live automated suite and restart cleanly.

Demonstrated on 2026-08-18: all 113 live tests passed. Drew completed both local Briefing dispositions. Keep retained `build-021-keep-sample.repaired-cce43288.txt` in Workbench; Toss removed the provisional derivative for the second sample. Both Intake originals retained their recorded pre-test SHA-256 hashes, the ledger records `kept` and `discarded` resolution states, and no repair Pending Report remains from either trial. The Librarian advances from demonstrated Level 1 to Level 2.

### 0.20.0 - The Librarian's First Catalogue - Complete

Give the Librarian her first callable Level 1 duty without risking irreplaceable reading material. Establish canonical **The Stacks** at `E:\Modesty Stacks`, inventory only copied Intake samples, persist a local generated catalogue, and report what was seen without altering a source file.

Definition of done:

- Create only missing `Intake`, `Originals`, `Workbench`, `Reading`, and `Archive` foundations outside the repository.
- Preserve an existing index and every reading file byte-for-byte.
- Inventory at most 5,000 Intake files on explicit request, never during startup.
- Record relative path, format, size, modification identity, SHA-256, obvious container warnings, and last-seen time.
- Report unsupported files, exact duplicate groups, and stale catalogue entries without acting on them.
- Add deterministic command help and truthful readiness state.
- Demonstrate the command on expendable copied samples in `E:\Modesty Stacks\Intake`.
- Keep repair, conversion, rename, move, deletion, OCR, and reading position out of this build's functional duty.

The vanished Calibre library is not a prerequisite or expected migration source. If fragments ever reappear, they are merely optional Intake material.

Demonstrated on 2026-08-18: all 108 live tests passed, startup reported the Librarian ready, and the user-facing duty catalogued six supported copied files with no unsupported or damaged items and no source mutation. The Librarian advances from Level 0 to demonstrated Level 1. Her subsequently earned Alexandrian Bobblehead is accepted on the live shelf between the Archivist and Researcher; pale edge-halo cleanup remains shared visual polish.

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

### Later - The Librarian Repairs and Reading Continuity

After the read-only catalogue is demonstrated, add a transformation ledger, one repaired derivative, and explicit review of uncertain corrections. Cross-platform Story Records, update tracking, and reading continuity follow only after that foundation. No step depends on recovery of the lost Calibre library. See [LIBRARIAN.md](LIBRARIAN.md).

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
