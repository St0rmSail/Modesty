# Modesty Project Punch List

**Current build:** 0.11.0 - Ask the Library (in progress)
**Current focus:** Local source-linked retrieval across both knowledge stores

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

## Build 0.11.0

- [ ] Build a local index, starting with SQLite FTS5.
- [ ] Retrieve from both stores while preserving origin on every result.
- [ ] Give Modesty source-linked passages rather than unsourced summaries.
- [ ] Support re-index, deletion, and stale-file detection.

## Engineering housekeeping

- [ ] Add a reproducible dependency manifest.
- [ ] Audit legacy `modesty.py` and duplicate boot/config paths.
- [ ] Add focused automated tests for memory and animation sampling.
- [ ] Preserve `python main.py` as the launch command.
