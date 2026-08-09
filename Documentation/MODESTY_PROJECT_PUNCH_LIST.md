# Modesty Project Punch List

**Current build:** 0.12.0 - Library Gateway (in progress)
**Current focus:** Explicit and bounded Grand Library online access

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

## Build 0.12.0

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
- [ ] Apply redaction and size limits.
- [x] Implement bounded, source-linked, unverified returns into the Bookshelf Inbox.
- [ ] Record an audit trail of what was borrowed, returned, and why.
- [ ] Prevent direct online-agent access to either local store.
- [ ] Demonstrate and inspect the first Smithsonian expedition.

## Engineering housekeeping

- [ ] Add a reproducible dependency manifest.
- [ ] Audit legacy `modesty.py` and duplicate boot/config paths.
- [ ] Add focused automated tests for memory and animation sampling.
- [ ] Preserve `python main.py` as the launch command.
