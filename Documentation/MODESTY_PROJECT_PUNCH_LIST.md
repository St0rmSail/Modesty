# Modesty Project Punch List

**Current build:** 0.38.0 - Background Presence Foundation complete; Researcher, Librarian, and Fishing Buddy parked
**Current focus:** Bounded Discord Communications

## Build 0.38.0 - Background Presence Foundation - Complete

- [x] Keep the local process and heartbeat alive while the visual Study is hidden.
- [x] Make the Windows close button and `Hide the Study` enter truthful `background` presence.
- [x] Provide a Windows tray restore surface for the same live session.
- [x] Provide explicit tray **Show the Study** and **Quit Modesty** actions.
- [x] Keep `Bye` as a clean full shutdown without a false background notification.
- [x] Document that hiding starts no scheduled, online, Discord, or fictional work.
- [x] Pass live close, tray restore, command hide, tray controls, and corrected goodbye tests.
- [x] Pass all 173 automated tests and 113-file syntax validation.

## Build 0.37.0 - Voice Foundation - Complete

- [x] Preserve local, original, low-overhead speech and Drew's explicit permanent-voice selection gate.
- [x] Make the Voice Agent pipeline replaceable so permanent voice selection does not block implementation.
- [x] Select HD3000 desktop microphone input and headphone playback as the first operating target.
- [x] Require shared on-screen and configurable-keyboard push-to-talk plus visible hard-off and activity states.
- [x] Separate local capture, recognition, turn control, conversation, synthesis, and playback.
- [x] Keep raw audio ephemeral by default, retain typed fallback, and keep the Team headset's meaning unchanged.
- [x] Audit available local audio devices, runtime dependencies, and machine capacity without opening an audio stream.
- [x] Confirm separate HD3000 input, SG03 stereo output, and the SG03 hands-free/profile collision risk.
- [x] Require replaceable descriptive device preferences, explicit rebinding, safe mic-off on input failure, and visible Realtek-speaker fallback on headphone failure.
- [x] Prove shared-mode capture and playback without changing any Windows default.
- [x] Select sherpa-onnx with CPU Whisper base.en INT8 and provisional CPU Kokoro output from evidence gathered on this machine.
- [x] Implement the bounded end-to-end voice turn and pass automated engine, device-policy, help, regression, and syntax checks.
- [x] Demonstrate the bounded end-to-end voice turn through the live Study.
- [x] Pass simultaneous game, Discord, and Modesty audio plus clean shutdown/restart without discernible rerouting or device lock.

## Build 0.36.0 - RF4 Codex Questions - Complete

- [x] Add a deterministic RF4-only one-species lookup over the private codex.
- [x] Answer trophy, water, bait-check, bait-suggestion and general species questions naturally.
- [x] Tolerate a clear minor species misspelling and refuse ambiguous or absent species.
- [x] Bound long lists, label source and evidence rank, and preserve unknown as unknown.
- [x] Keep absent bait evidence distinct from proof that a bait cannot work.
- [x] Update deterministic command help and project documentation with the new natural surface.
- [x] Pass the live Modesty question set and accept the reply quality with all 165 automated tests passing.

## Build 0.35.0 - Fishing Codex Evidence Intake - Complete

- [x] Confirm the official local save location and inspect only bounded known files.
- [x] Recognise the Avalanche ADF binary signature without treating unknown fields as progress.
- [x] Hash current and recovery-slot containers and report matching snapshots without exposing the account directory.
- [x] Refuse oversized files, symlinks, path escape, and files changing during inspection.
- [x] Add a deterministic natural command, help entry, focused tests, and documentation.
- [x] Add a content-free before/after observation that compares only relative paths, sizes, and hashes outside the save directory.
- [x] Refine broad container changes into content-free 4 KiB changed-region fingerprints.
- [x] Define an RF4-only weakest-rank Almanac intake with transactional provenance and structural refusal.
- [x] Separate hotspot states into rumoured, locally known, and Drew-selected favourite.
- [x] Demonstrate the first full RF4 fish-catalogue import in the live checkout: 251 species, 133 baits, 1,159 unique species-bait links, 18 waters, and 580 species-water links.
- [x] Pass the live Modesty commands and accept the truthful opaque-format and RF4 import reports.

Fishing codex foundation amendment:

- [x] Require an explicit best-tackle entry, evidence basis, and source for every applicable game/species/fishing-style combination.
- [x] Preserve uncertainty as `Not yet established` instead of inventing advice.
- [x] Add linked schema foundations for versions, methods, structured setups, locations, contextual recommendations, sources, player state, and catch evidence before game adapters begin populating the codex.
- [x] Model bait effectiveness and selectivity per game, species, fishing style, conditions, and evidence rather than assigning one universal bait-strength value.
- [x] Add contextual groundbait recipes, component effects, compatibility, substitution, and location/method suitability without precomputing the endless permutation space.
- [x] Keep numerical optimisation backstage and make Modesty's normal output concise, practical advice with substitutes and unsuitable-method warnings.
- [x] Add a separate companion layer for scoped likes/dislikes, truth-labelled fishing memories, recall cooldowns, and recent-response fingerprints so advice can remain personal and varied without corrupting technical evidence.
- [x] Implement the first semantic recommendation service: rank stored evidence, switch away from a poorly suited method, check owned substitutions, attach eligible preference/memory context, and fail unknown without guessing.

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

## Build 0.18.0 - Complete

- [x] Add an in-window comparison set limited to two or three distinct story pages.
- [x] Compare shared and distinguishing metadata with per-story sources and cautions.
- [x] Flag likely duplicate or cross-post candidates as leads rather than proof.
- [x] Refuse incomplete, duplicate-source, one-item, and oversized comparison inputs.
- [x] Update Researcher help and the common capability benchmark honestly.
- [x] Demonstrate collection, comparison Briefing, and disposition in `E:\Modesty`.
- [x] Complete the restore-point audit and milestone commit after acceptance.

## Build 0.19.0 - Implemented; Live Acceptance Paused

- [x] Establish the API-key versus OAuth versus public-transcript boundary.
- [x] Add bounded public English YouTube transcript intake with safe URL parsing.
- [x] Keep transcript retrieval off the Study interface thread.
- [x] Add timestamp-linked mixed-source synthesis with explicit source roles and limits.
- [x] Fail closed for unavailable transcripts without leaking transport detail.
- [x] Pin and validate the local transcript dependency on the live Windows environment.
- [x] Pass all 102 automated tests in `E:\Modesty`.
- [x] Record the persistent Scribble Hub Cloudflare 522 outage as an external acceptance blocker, not a product failure.
- [ ] Demonstrate the mixed-source Briefing and disposition in `E:\Modesty`.
- [ ] Decide the Level 4 award from the actual report, not merely passing code.
- [ ] Complete the restore-point audit and milestone commit after acceptance.

## Build 0.20.0 - Complete

- [x] Canonise The Stacks at `E:\Modesty Stacks`.
- [x] Remove recovery of the lost Calibre library from every implementation gate.
- [x] Add safe idempotent external collection initialization.
- [x] Add a bounded persistent read-only Intake catalogue.
- [x] Detect supported formats, unsupported files, obvious damaged containers, exact duplicates, and stale entries without acting on them.
- [x] Add the deterministic Librarian command, help section, readiness state, and focused tests.
- [x] Pass all 108 live tests, create the empty Stacks foundation, and reach `MODESTY : READY` with Librarian ready.
- [x] Demonstrate startup and the inventory command on six expendable copied samples in `E:\Modesty`.
- [x] Award Librarian Level 1 and fit her accepted truthful Alexandrian Bobblehead between the Archivist and Researcher.
- [x] Complete the restore-point audit and milestone commit after acceptance.

## Shared visual polishing

- [ ] Remove residual white or pale extraction halos from Bobblehead edges without changing approved figures, placement, scale, or shelf contact.

## Build 0.21.0 - Complete

- [x] Limit repair to one named UTF-8 Markdown or plain-text Intake file no larger than 2 MiB.
- [x] Preserve the original and create a separate provisional Workbench derivative.
- [x] Record source/output hashes, mechanical actions, cautions, timestamps, and disposition.
- [x] Refuse stale approval if either source or derivative changes after preparation.
- [x] Reuse the Briefing Hologram with local Keep Repair and Toss Repair controls.
- [x] Add deterministic command documentation and tests.
- [x] Pass all 113 live automated tests.
- [x] Demonstrate Keep Repair and verify the original and derivative physically.
- [x] Demonstrate Toss Repair and verify that only the provisional derivative is deleted.
- [x] Complete the restore-point paperwork audit and milestone commit after acceptance.
- [x] Push the milestone commit to `origin/main`.

## Builds 0.22.0 through 0.26.0 - Complete

- [x] Read and search supported private works with source-linked passages.
- [x] Recognize EPUB chapter headings and persist explicitly confirmed exact-edition reading positions.
- [x] Build an incremental source-supplied work and edition catalogue.
- [x] Present evidence-ranked file-level edition relationship groups without false generic-metadata matches.
- [x] Resolve one exact duplicate reversibly through preparation, exact approval, and Archive retention.
- [x] Preserve the canonical `Song And Silence` Handbooks copy and verify its redundant exact copy in Archive.
- [x] Pass all 123 automated tests through Build 0.26.
- [x] Commit and push Build 0.26.

## Build 0.27.0 - Natural Librarian Control Surface - Complete

- [x] Support concise contextual requests and visible choice references for ordinary Librarian work.
- [x] Keep deterministic IDs and exact commands available underneath for audit and recovery.
- [x] Permit contextual confirmation such as `yes, do that` only for one clearly pending reviewed action.
- [x] Refuse ambiguous references rather than guessing.
- [x] Update help around goals and examples instead of requiring a memorized command catalogue.
- [x] Pass the natural duplicate and restart-safe reading flows plus all 127 automated tests.

## Build 0.28.0 - Bounded Intake Shelving Desk - Complete

- [x] Review the current catalogue and limit each Ready list to five items.
- [x] Separate items ready for a source-backed Author/Title destination from uncertain metadata and edition conflicts.
- [x] Present proposed destinations and reasons before any move.
- [x] Allow natural review and approval without requiring job-ID memorization.
- [x] Recheck all source hashes and destinations before the first move; roll back completed moves on failure.
- [x] Preserve unknown metadata visibly rather than guessing from filenames or prose.
- [x] Demonstrate five Ready items, natural exclusion of CRUMPETS, four approved moves, and 28 truthfully held items in the live Stacks.
- [x] Physically verify four Originals, absent former Intake paths, retained CRUMPETS, resolved ledger state, and updated catalogue hashes.
- [x] Pass all 132 automated tests.

## Build 0.29.0 - Metadata Review Desk - Complete

- [x] Present a bounded set of held items with incomplete source metadata.
- [x] Keep embedded metadata, filename-derived suggestions, and confirmed corrections visibly distinct.
- [x] Let Drew edit or reject title and author suggestions naturally.
- [x] Record source hash, original fields, confirmed fields, provenance, and resolution state.
- [x] Do not rewrite the source file or conflate metadata correction with edition-conflict resolution.
- [x] Feed only explicitly confirmed identity into a normal shelving preview.
- [x] Live-test one `leave it`, one completed correction, and the corrected item in the ordinary shelving preview.
- [x] Verify Sandstorm retained SHA-256 `cb39abef3d51387be1274ee69372893cfce667616aaab46391ed41639f276680` and was not shelved during acceptance.
- [x] Reconcile acceptance evidence, 135-test count, roadmap, benchmark, and milestone paperwork.

## Build 0.30.0 - Preferred Edition Desk - Complete

- [x] Reuse displayed edition relationships rather than introduce another discovery command family.
- [x] Allow one unambiguous preferred choice only from a displayed non-identical group.
- [x] Keep exact duplicates on their separate reversible resolution path.
- [x] Preview the chosen edition and every retained alternative before confirmation.
- [x] Recheck every member SHA-256 before recording preference.
- [x] Move, rewrite, archive, and delete nothing during preference recording.
- [x] Allow only the chosen exact edition into ordinary shelving while alternatives remain held.
- [x] Add natural help, deterministic recovery wording, and focused tests.
- [x] Live-test the real `Magic in the Blood` pair and verify both files remain present with their recorded hashes.
- [x] Verify `(266)` appears first in Ready while `(251)` remains a visibly held retained alternative.
- [x] Reconcile the acceptance evidence and 138-test milestone paperwork.

## Build 0.31.0 - Series Review Desk - Complete

- [x] Present no more than five source-supplied series groups per desk view.
- [x] Exclude retained alternative editions from logical series order.
- [x] Flag duplicate positions without inventing correct bibliography.
- [x] Let Drew confirm or correct one exact book's series and numeric volume naturally.
- [x] Record original fields, confirmed fields, exact hash, provenance, and disposition.
- [x] Preserve `leave it` and changed-source fail-closed paths.
- [x] Never rewrite a reading file or reorganize an existing Original automatically.
- [x] Produce series-aware ordinary shelving destinations only after confirmation.
- [x] Live-test `Magic at the Gate` as left and preferred `Magic in the Blood (266)` as confirmed Allie Beckstrom volume 2.
- [x] Verify unchanged source SHA-256 and the `Devon Monk/Allie Beckstrom/02 - Magic in the Blood/...` preview without moving it.
- [x] Reconcile the acceptance evidence and 141-test milestone paperwork.

## Build 0.32.0 - Passage Bookmarks and Notes - Complete

- [x] Create several passage anchors independently of the single saved reading position.
- [x] Attach a bounded private note to the displayed passage.
- [x] List active bookmarks as stable visible choices.
- [x] Reopen the exact source passage after restart.
- [x] Fail closed when the source path or SHA-256 edition changes.
- [x] Retire an active bookmark without deleting its audit row.
- [x] Never rewrite or annotate the reading source itself.
- [x] Update deterministic help and natural command examples.
- [x] Pass live acceptance and all 144 automated tests.

## Build 0.33.0 - Reading Desk - Complete

- [x] Open a dedicated legible surface for ordinary open, resume, and bookmark passages.
- [x] Keep the conversation panel out of the reading area while the Desk is open.
- [x] Provide Next Passage and session-local Previous controls.
- [x] Disable save and bookmark actions while reviewing an older cached passage.
- [x] Reuse explicit Save Place, Bookmark, and Bookmark with Note operations.
- [x] Close without silently advancing progress or changing the source.
- [x] Pass the live visual and restart-safe continuity sequence.
- [x] Reconcile acceptance evidence and all 145 automated tests.

## Build 0.34.0 - Fishing Buddy: First Cast - Complete

- [x] Promote the Fishing Buddy to a distinct canonical Team role.
- [x] Separate fishing judgement from Researcher evidence gathering, Nurse guidance, Archivist filing, and Schedule reminders.
- [x] Reframe the primary portfolio around four fishing simulators while retaining real fishing as secondary future scope.
- [x] Define local-only per-game codex, external companion, information, entertainment, and future fishing-mode visuals.
- [x] Record no-save-write, no-injection, no-traffic-interception, no-anti-cheat-evasion, and source-permission boundaries.
- [x] Implement private codex foundations and read-only installation/source discovery.
- [x] Add one concise natural command plus help and tests.
- [x] Demonstrate a truthful local discovery report before awarding the Bobblehead.
- [x] Correctly discover RF4 as a standalone installation and use Steam only for the other three games.
- [x] Pass all 148 automated tests and accept the live four-game report.
