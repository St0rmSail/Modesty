# Modesty Project Punch List

**Current build:** 0.17.0 - Story Investigation (complete)
**Current focus:** Select the next capability increment from the benchmark and roadmap

The detailed project record now begins at [PROJECT_LEDGER.md](PROJECT_LEDGER.md). This file remains the short working checklist.

## Before Build 0.9.0

- [x] Reconcile three project conversations with current `main`.
- [x] Separate canon, architecture, Team roles, status, decisions, and roadmap.
- [x] Record Builds 0.4.0 through 0.8.0 that were missing from documentation.
- [x] Drew reviews the Ledger for misinterpreted or missing canon.
- [x] Resolve the Filing Cabinet, Bookshelf, and Grand Library distinction before writing knowledge code.

## Build 0.9.0 - Complete

- [x] Confirm physical locations for the Filing Cabinet and Bookshelf.
- [x] Create the private Filing Cabinet Obsidian vault.
- [x] Create the living Bookshelf with Inbox, Workbench, collections, and Archive.
- [x] Add OKF-compatible Bookshelf indexes and note templates.
- [x] Add deterministic path validation and preserve existing files.
- [x] Demonstrate first-run initialization on Drew's E: drive.

## Build 0.10.0 - Complete

- [x] Define and demonstrate the Archivist's first executable contract.
- [x] Inventory Markdown in both stores without modifying it.
- [x] Record source store, path, hash, size, and modification timestamp.
- [x] Validate structural Bookshelf metadata and surface gaps without automatic rewriting.
- [x] Demonstrate the approval-gated Inbox-to-Workbench review path.
- [x] Demonstrate bounded private filing and retrieval reported through Modesty.
- [x] Propose an established Bookshelf collection without moving the Workbench item.
- [x] Demonstrate explicit approval before moving into the proposed collection.
- [x] Report the review and curation workflow through Modesty in plain language.
- [x] Create and demonstrate the Archivist's stern-librarian Bobblehead, absence sign, and readiness lamp.
- [x] Create and demonstrate Modesty's headset as the visible Team communication channel.

## Build 0.11.0 - Complete

- [x] Build a local index using SQLite FTS5.
- [x] Retrieve from both stores while preserving origin on every result.
- [x] Give Modesty source-linked passages rather than unsourced summaries.
- [x] Support re-index, changed files, moved files, deletion, and stale-file detection.
- [x] Demonstrate and accept echo-free Library answers through Modesty.

## Build 0.12.0 - Complete

### Local loopback foundation - Complete

- [x] Start closed and refuse outbound work while closed.
- [x] Open and close an explicitly labelled local loopback mode.
- [x] Preview an immutable, size-limited packet before exact-ID approval.
- [x] Reject Filing Cabinet sources, credentials, absolute paths, and oversized packets.
- [x] Quarantine a test-only return in the Bookshelf Inbox.
- [x] Record a content-free audit trail for refusal, preparation, approval, return, cancellation, and closure.
- [x] Cancel pending loans on close and return to closed state after restart.
- [x] Require explicit future source selection rather than silently attaching search matches.

### Real provider and online boundary

- [x] Implement Windows current-user encrypted storage outside Git.
- [x] Implement a one-purpose authenticated Smithsonian statistics check with content-free audit.
- [x] Demonstrate key storage and authenticated validation in the live checkout.
- [x] Implement explicit open and close controls for a distinct Grand Library online mode.
- [x] Keep the first expedition's outbound Bookshelf selection empty.
- [x] Preview the exact outbound question and return boundary before approval.
- [x] Apply credential redaction, outbound packet limits, response limits, and bounded excerpts.
- [x] Implement bounded, source-linked, unverified returns into the Bookshelf Inbox.
- [x] Record a content-free audit trail of preparation, approval, outcome, failure class, and closure.
- [x] Prevent the online provider from receiving filesystem or direct local-store access.
- [x] Demonstrate and inspect the first Smithsonian expedition.
- [x] Complete approved Inbox to Workbench to Research curation of the first trophy.
- [x] Define and enforce a fail-closed text-only boundary before accepting any media-bearing return.
- [x] Demonstrate in `E:\Modesty` that embedded-media refusal tests pass without an Inbox file.
- [x] Implement the Study's truthful Grand Library online-state sequence.
- [x] Visually review and accept the five-second shelf-panel transition, temporary panel hide, persistent online badge, clean close, loopback silence, resize stability, and restart-closed state in `E:\Modesty`.

## Engineering housekeeping

- [x] Add a reproducible dependency manifest.
- [ ] Audit legacy `modesty.py` and duplicate boot/config paths.
- [ ] Add focused automated tests for memory and animation sampling.
- [ ] Preserve `python main.py` as the launch command.

## Build 0.13.0 - Complete

- [x] Implement bounded visible Scribble Hub discovery without bypassing access controls.
- [x] Return a coherent sourced Briefing rather than only a file location.
- [x] Preserve undecided reports across restart and require explicit private, shared, or toss disposition.
- [x] Implement the readable Briefing Hologram, duty movement, moving shadow, truthful headset state, and Researcher Bobblehead.
- [x] Add tolerant deterministic command help and graceful `Bye` shutdown.
- [x] Demonstrate the complete live lifecycle and pass 64 tests.

## Build 0.14.0 - Complete

- [x] Persist UTC startup, heartbeat, presence, and clean shutdown state outside Git.
- [x] Produce local-time greetings with truthful elapsed clean or interrupted absence.
- [x] Define offline, background, present, and working states without pretending background hosting exists yet.
- [x] Answer regular African/GMT working times locally.
- [x] Add DST-aware named zones for Britain, Europe, Thailand, selected Australia, Auckland, and US East/Central/West.
- [x] Reject ambiguous Australia and USA requests rather than guessing.
- [x] Record dependencies and demonstrate all 79 live tests.

## Build 0.15.0 - Complete

- [x] Keep narrative episodes separate from factual personal memories.
- [x] Implement compact local episode storage with status and provenance.
- [x] Implement visible add, edit, retire, and delete controls.
- [x] Implement bounded relevant recall of active episodes only.
- [x] Label recalled context as narrative and prohibit factual-evidence use.
- [x] Demonstrate persistence and review controls in the live Study.
- [x] Demonstrate relevant analogy without factual misuse.
- [x] Demonstrate false-premise rejection and retirement exclusion in a new conversation.
- [x] Preserve readable controls plus keyboard input recall and transcript paging.
- [x] Run all 84 live tests and perform the restore-point paperwork audit.

## Build 0.16.0 - Complete

- [x] Persist explicit local-date reminders with stable IDs.
- [x] Add deterministic create, list, complete, and delete commands plus help.
- [x] Add a readable Schedule review surface without crowding existing controls.
- [x] Add bounded overdue and due-today opening notices.
- [x] Demonstrate restart persistence, overdue greeting, review, and confirmed deletion.
- [x] Run all 89 live tests and perform the restore-point paperwork audit.

## Build 0.17.0 - Complete

- [x] Define a reusable investigation report contract.
- [x] Add bounded extraction for the current visible public Scribble Hub story page.
- [x] Separate observed page facts, reader-reported evidence, cautions, and missing evidence.
- [x] Keep account actions, chapters, mirroring, and access-control bypass out of scope.
- [x] Route the result into the existing Pending Report and Briefing lifecycle.
- [x] Update deterministic Researcher help and focused tests.
- [x] Demonstrate extraction, Briefing presentation, and disposition in `E:\Modesty`.
- [x] Complete the restore-point audit and milestone commit after acceptance.
