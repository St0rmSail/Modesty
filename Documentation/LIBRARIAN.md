# The Librarian

**Status:** Build 0.31 Series Review Desk complete

The Librarian is a dedicated unseen Team specialist responsible for Drew's private reading collection. She is not the Archivist under another name and never speaks as a separate chat personality. Modesty consults her through the Team headset and presents her results.

## Portfolio

The Librarian owns:

- books, stories, manuscripts, fan fiction, and other long-form reading material;
- PDF, EPUB, Word, Markdown, plain-text, scanned, piecemeal, and other legitimately held sources;
- work identity, alternate editions, mirrors, cross-posts, chapter sequence, and freshness;
- reading position, bookmarks, annotations, watchlists, and resume delivery;
- duplicate detection and consolidation proposals;
- OCR and transcription cleanup;
- repair of encoding, paragraph, line-break, hyphenation, punctuation, and heading faults;
- clean master manuscripts and consistent reading editions; and
- provenance and transformation history for every repaired work.

The permanent name for the private collection under her care is **The Stacks**. Its configured local root is `E:\Modesty Stacks`, separate from the repository, Filing Cabinet, and Bookshelf.

## Preservation rule

The Librarian never overwrites an original. Each managed work may contain:

1. untouched original sources;
2. a clean master manuscript;
3. one or more reading editions;
4. metadata and provenance;
5. permitted covers and media;
6. alternate platform editions;
7. repair history; and
8. reading position and notes.

One unified manuscript standard does not mean forcing every work into one file format. Reflowable books may use EPUB, page-faithful material may retain PDF, and editable masters may use DOCX or Markdown. The source and purpose determine the output.

Obvious mechanical repairs may be automated and logged. Missing passages, conflicting editions, uncertain OCR, reordered chapters, or meaning-changing corrections require review through the Briefing Hologram.

## Boundaries

- The **Researcher** discovers and investigates works, authors, sites, warnings, reviews, and suitability.
- The **Librarian** manages works, editions, repairs, reading continuity, and the private reading collection.
- The **Archivist** manages knowledge in the Filing Cabinet and Bookshelf. A bibliographic record or accepted report may be handed to the Archivist; an entire copyrighted collection may not be silently copied to the Bookshelf.
- The future **Communications specialist** handles WhatsApp and other delivery channels.
- The future **Vision/Capture specialist** owns screenshot and general OCR capture controls. The Librarian may request OCR for a reading source without absorbing the whole perception remit.

The Librarian may process material Drew legitimately possesses for private use. She must not defeat DRM, bypass access controls, or republish an author's work.

## Lost legacy catalogue

The old Calibre library is presumed lost after multiple house moves, hard-drive failures, and machine upgrades. Its recovery is not an implementation dependency, migration target, authority, or planning constraint. If isolated Calibre-compatible files or metadata are ever rediscovered, they enter Intake as optional sources and receive the same read-only provenance treatment as any other material.

## Build 0.20 first duty

`Ask the Librarian to inventory The Stacks` scans only copied material beneath `The Stacks/Intake`. It records bounded file metadata, SHA-256 identity, obvious EPUB/DOCX/PDF container faults, exact duplicate groups, unsupported formats, and stale catalogue entries in local generated data. It does not parse whole manuscripts for meaning and never renames, moves, repairs, converts, deletes, or publishes a reading file.

The first live test should use expendable copied samples. The real collection can grow organically after this boundary is demonstrated; no vanished legacy catalogue is required.

Live acceptance passed on 2026-08-18. The Librarian catalogued six supported Intake files, found no unsupported or damaged items, and reported that no file was renamed, moved, repaired, converted, deleted, or published. Combined with the 108-test suite, this earns demonstrated Level 1.

## Build 0.21 first repair

`Ask the Librarian to repair: <filename>` accepts one explicitly named UTF-8 `.txt` or `.md` file directly inside Intake, up to 2 MiB. It applies only mechanical line-ending, non-breaking-space, trailing-whitespace, excessive-blank-line, and final-newline corrections. Possible hyphenation and suspicious short wrapped lines are reported as cautions and remain unchanged.

The original remains in Intake and is never overwritten. A provisional derivative is created in Workbench with a unique repair identifier. The local Librarian catalogue stores source and derivative hashes, paths, every applied action and caution, creation and resolution timestamps, and pending, kept, or discarded state. Approval re-checks both hashes so a stale Briefing cannot silently approve externally changed content.

The existing Briefing Hologram becomes a local repair review for this provider. **Keep Repair** retains the derivative in Workbench. **Toss Repair** deletes only the provisional derivative. Neither route sends copyrighted reading material to the Filing Cabinet or Bookshelf. This implementation does not perform paragraph reflow, dehyphenation, OCR, PDF repair, conversion, semantic correction, bulk work, or promotion into Reading.

Live acceptance passed on 2026-08-18. Keep Repair retained the expected hashed derivative in Workbench; Toss Repair removed only its provisional derivative. Both Intake samples retained their pre-test hashes, both ledger dispositions persisted, and the Briefing controls and conversational outcomes were accepted. Combined with all 113 live tests, this advances the Librarian to demonstrated Level 2.

## Build 0.22 catalogue, reading, and first shelving

The Librarian can now interpret one explicitly named work beneath Intake rather than merely count its container. `Ask the Librarian to examine: <relative Intake path>` supports TXT, Markdown, HTML, DOCX, EPUB, and PDFs with an existing text layer. The reader does not execute embedded content. It extracts embedded title and author where available, counts the readable extent, returns a bounded opening passage, and records local source-linked passages for later retrieval. Very large PDFs are bounded honestly; image-only PDFs fail with an explicit future-OCR requirement.

`Ask the Librarian to find: <words or phrase>` searches only works she has actually examined and returns bounded passages with title, author, section or page, and exact Stacks source. The full manuscript is never copied into chat, the Filing Cabinet, or the Bookshelf.

Inspection proposes a conservative `Originals/Author/Title/original-file` destination and issues a unique `LS-ID`. Nothing moves during inspection. `Approve Librarian shelving: <LS-ID>` rechecks the source SHA-256, refuses an occupied destination, creates only the needed shelf folders, and moves the byte-identical original from Intake to Originals. Unknown metadata stays visibly labelled rather than guessed from prose. MOBI, AZW3, RTF, legacy DOC, LIT, archive containers, DRM, OCR, batch approval, duplicate merging, and automatic renaming remain outside this bounded build.

Live acceptance passed on 2026-08-19 using the real `Axeman` EPUB. The Librarian extracted 167,521 words across all nine EPUB spine documents and retrieved five passages for distinctive wording known to occur in Chapter 12. EPUB spine documents are currently labelled `Section 1`, `Section 2`, and so forth; a single spine document may contain several human chapters. Human chapter-heading detection and chapter-aware citations belong to the later reading-continuity work and do not invalidate complete text extraction or passage retrieval.

## Build 0.23 reading continuity

The EPUB reader now recognizes conservative standalone headings such as `Chapter 12`, `Prologue`, and `Epilogue`, even when several chapters share one spine document. Passage citations and opening controls can therefore use human chapter labels where the source supplies them; material without reliable headings retains its truthful page, section, or document label.

`Ask the Librarian to open: <title or Stacks path> at Chapter <number>` returns one bounded passage and an `RP-ID`. `Continue reading: <RP-ID>` displays the next passage without changing permanent progress. `Mark my place: <RP-ID>` is the sole confirmation that the end of the latest displayed passage becomes the next unread position. `Ask the Librarian to resume: <title or Stacks path>` restores that confirmed position after restart.

Progress is keyed to the source SHA-256, not merely a title or filename. A changed edition cannot inherit an old position silently, and an ambiguous title requires an exact Stacks path. This build does not infer that visible text was read, synchronize devices, track unapproved online copies, or create a dedicated visual ebook reader.

Live acceptance passed on 2026-08-19. Axeman opened at the correctly detected `Chapter 12`, continued through a bounded second passage without silently saving, persisted only the explicitly marked endpoint, and resumed at the next unread text after restart. The exact edition's passage index was refreshed with chapter-aware labels. Combined with all 120 live tests, this completes the first truthful reading-continuity loop without advancing the common benchmark beyond Level 2.

## Build 0.24 work and edition identity

`Ask the Librarian to identify works and editions` incrementally catalogues readable files beneath both Intake and Originals. EPUB source metadata may supply title, author, ISBN or other identifiers, series name and number, publisher, language, and publication date. DOCX and PDF contribute only fields their containers actually expose. Unknown values remain unknown; prose and filenames are not mined for invented bibliographic certainty. One invocation refreshes at most 25 changed or new files and reports the remainder, preventing a large first catalogue from monopolizing the Study interface.

The catalogue distinguishes three evidence strengths: identical SHA-256 proves exact duplicate bytes; a shared non-UUID identifier is a strong same-publication lead; normalized title and author is only a possible same-work review group. None authorizes deletion, merging, replacement, or automatic selection of a preferred edition. Size and modification identity allow unchanged records to be reused without repeatedly hashing or parsing the full collection.

Live acceptance passed on 2026-08-19. Three 25-file refreshes catalogued 75 real readable files with zero metadata failures. The final identity set contained 27 named authors, 10 named series, three exact duplicate groups, two shared strong-identifier groups, and six possible title/author same-work groups. The immediate repeat refreshed zero files and reused all 75 records, proving the incremental boundary. No reading file was renamed, moved, merged, deleted, converted, or overwritten; all 122 tests passed.

## Build 0.25 Edition Review Desk

`Ask the Librarian to review edition groups` turns aggregate counts into a bounded, readable list of exact file paths, formats, sizes, and relationship evidence. A group is shown once at its strongest useful level: exact hash first, then shared non-UUID identifier, then normalized title and author. A shared identifier may include an exact pair plus a third differing file because that third edition relationship still needs review.

Generic `Untitled` or unknown-author metadata is excluded from weak same-work grouping so unrelated poorly tagged PDFs do not become a fictional relationship. The review remains observation-only: it does not choose a preferred edition, merge files, delete duplicates, or authorize shelving.

Live acceptance passed on 2026-08-19. The Librarian presented three exact duplicate pairs—`Song And Silence`, `Gunmetal Magic`, and `Stronghold Builder's Guide`—and one non-identical `Magic in the Blood` pair sharing ISBN 9780451462671. No title/author-only group qualified under the conservative rule because apparent remaining matches lacked a trustworthy author. Generic untitled records did not leak into the report. The four groups included exact paths, formats, and sizes; no preferred edition was selected and no file changed. All 122 tests passed.

## Build 0.26 reversible exact-duplicate resolution

The first governed consolidation duty applies only to files whose complete SHA-256 values match. Drew must supply the reviewed hash and choose the exact Stacks path that remains canonical. Preparation creates a persistent `DR-ID` and an explicit source-to-Archive plan without moving anything.

Approval rechecks the canonical file, every redundant source, and every empty destination. Redundant byte-identical copies move into `Archive/Exact Duplicates/<hash>/` with their former Intake or Originals path retained beneath that record. A failed multi-file move rolls completed moves back where possible. Nothing is deleted, and non-identical shared-identifier or possible-work groups cannot enter this workflow. Reading positions for the same exact hash are redirected to the chosen canonical path.

Live acceptance passed on 2026-08-19. Drew selected the Handbooks `Song And Silence` copy; `DR-44C88BB7` retained it at 22,666,472 bytes and archived the byte-identical root Intake copy under hash `e5b44f628756494c`. The former root path is clear, the Archive copy is present, and nothing was deleted. All 123 tests passed.

## Build 0.27 natural control surface

The growing exact-command vocabulary is no longer acceptable as the ordinary Librarian interface. Deterministic commands, hashes, and job IDs remain necessary underneath for safe replay and audit, but Drew can now guide visible work using concise language: `show me the duplicates`, `keep the Handbooks copy of Song and Silence`, `yes, do that`, `open Axeman at chapter 12`, `keep reading`, `save my place`, and `resume Axeman`.

Natural wording translates into the existing deterministic operation rather than creating a second authority path. A copy can be chosen only from the edition groups displayed during the current Study session. An ambiguous folder or title produces a short distinction request. Contextual approval works only when exactly one duplicate-resolution preview has been prepared in that session; it cannot approve shelving, research, or an unrelated action. Reading continuation and place-saving similarly use only the current passage session, while resume relies on the already persisted exact-edition position.

This is functional accessibility and cognitive-load work, not visual polish. Live acceptance must prove one natural duplicate preview and approval, one ambiguity refusal, and the natural open/continue/save/restart/resume sequence before the build is complete.

Live acceptance passed on 2026-08-19. Drew used the concise contextual vocabulary to review duplicates, received a safe clarification instead of a guessed choice, prepared and approved an exact-duplicate action without typing its hash or `DR-ID`, and completed the natural open, continue, save, restart, and resume reading sequence without typing an `RP-ID`. Exact confirmation gates remained intact and all 127 automated tests passed.

## Build 0.28 bounded Intake shelving desk

`Show me what can be shelved` uses the existing edition catalogue to prepare at most five Ready Intake items. Proposed `Originals/Author/Title/original-file` destinations come only from source-supplied author and title metadata. The preview separately reports a bounded sample of held items and reasons, plus counts for additional eligible or held material.

An item is held when metadata is unknown, the catalogue reports a warning, the source belongs to an exact, identifier-linked, or title/author edition relationship, the source changed, an earlier single-item shelving proposal remains pending, or its destination exists or competes with another proposal. The Librarian does not use filenames or prose to invent missing identity and does not move an item merely to empty Intake.

`Leave <title or folder> out` removes one unambiguously matched Ready item while leaving the source in Intake; it cannot add an item or redirect a destination. `Shelve those` approves only the resulting Ready list from the current Study session. The persistent exact form remains available through help. Approval performs a complete source-hash and destination preflight before the first move, updates local catalogue and reading references after success, and rolls completed filesystem moves back if a later move fails. The batch is all-or-nothing, and a new preview supersedes an older unapproved batch. Live acceptance must demonstrate one small approved real batch, one natural exclusion, and at least one truthful held-back item.

Live acceptance passed on 2026-08-21. Batch `LB-2A8EAE65` presented five Ready items, 28 held items with reasons, and 39 additional eligible items deferred to later batches. Drew naturally removed `CRUMPETS` and approved the remaining four. Physical verification found all four unchanged originals at their proposed destinations, all four former Intake paths absent, CRUMPETS retained in Intake, the batch ledger marked `shelved`, and all four edition-catalogue paths updated with their hashes. All 132 automated tests passed.

The run also exposed the next honest bottleneck: many held items lack trustworthy embedded author or title metadata.

## Build 0.29 bounded Metadata Review Desk

`Show me books needing metadata` presents no more than five incomplete Intake records that are safe to review. Items with catalogue warnings or unresolved edition relationships remain outside this desk. Each entry distinguishes catalogued source fields from a filename-derived title suggestion; the suggestion is never silently promoted.

`Review <displayed title or filename>` opens exactly one item from the visible set. `Title is ...` and `Author is ...` stage Drew-supplied facts, while `leave it` closes the review without changing catalogue identity. `Save that` requires both specific fields, rechecks the source SHA-256, records original and confirmed values plus review disposition locally, and marks the confirmed values as Drew-confirmed. The book itself is never rewritten. Confirmed identity is keyed to the exact source hash, so changed replacement bytes cannot inherit it, and the item must still pass the ordinary bounded shelving preview and approval before it moves.

Live acceptance must demonstrate one deliberately left suggestion, one completed correction, source-byte preservation, and the corrected item appearing in the ordinary shelving preview.

Live acceptance passed on 2026-08-21. Drew first reviewed `[D&D 3.5E ENG] Sandstorm.pdf` and chose `leave it`; review `MR-67345FED` retained empty staged fields with disposition `left`. Drew then explicitly confirmed `Sandstorm: Mastering the Perils of Fire and Sand` by Bruce R. Cordell in review `MR-976B4B72`. The override ledger retained the original catalogue fields, confirmed fields, exact source hash, provenance, and resolution. The physical Intake PDF still matched SHA-256 `cb39abef3d51387be1274ee69372893cfce667616aaab46391ed41639f276680`, and ordinary shelving batch `LB-3D28F4A5` placed that corrected exact source first in its Ready list. Nothing was shelved during this acceptance. All 135 automated tests passed.

## Build 0.30 bounded Preferred Edition Desk

`Show me the edition choices` presents the existing evidence-ranked relationship groups. After that visible review, `prefer <displayed folder or filename>` can select exactly one member of a non-identical shared-identifier or title/author group. An ambiguous description stops for clarification, and exact byte duplicates remain under the separate exact-duplicate desk.

The resulting `PE-ID` preview lists the chosen reading edition and every retained alternative. Contextual `yes, do that` is valid only when it is the sole pending Librarian action. Approval rechecks every member's SHA-256 and records the preference by the complete set of exact member hashes; it moves, deletes, rewrites, or archives nothing. The chosen exact edition may then pass the existing shelving gate, while every non-preferred alternative remains held with an explicit retention reason. A later changed edition invalidates stale approval rather than inheriting preference.

Live acceptance should use the two real non-identical `Magic in the Blood` EPUBs: display the relationship, choose one exact path, approve the preference, confirm both sources remain physically present, and verify only the chosen edition enters an ordinary shelving preview. Do not shelve it during this acceptance.

Live acceptance passed on 2026-08-21. Drew preferred `Intake/eBooks/Devon Monk/Magic in the Blood (266)/Magic in the Blood - Devon Monk.epub` through `PE-ED180937`, based on the displayed shared ISBN 9780451462671 relationship. The `(266)` source retained SHA-256 `7e08f29050d19f771aa29b191a9862fb9a914dafdeb899855fd9f919396e296a`; the retained `(251)` alternative retained SHA-256 `a25bb586f7f473b45811eced5b4c7e501948d347d929f2ed1c2ee047778a56d3`. Both files remained physically present in Intake. Ordinary batch `LB-0F661048` placed `(266)` first in Ready while the visible preview held `(251)` as the retained alternative. Nothing was shelved. All 138 automated tests passed.

## Build 0.31 bounded Series Review Desk

The live catalogue contains 14 series-bearing records across 10 source labels. `Show me the series` presents at most five groups at once and excludes editions already designated as retained alternatives. It displays each book's source-supplied series name, volume number, title, author, and exact path, and marks duplicate positions without claiming the bibliography is correct.

`Review <displayed title>` opens one exact book. Existing source fields are staged but remain explicitly unconfirmed; `series is ...` and `volume is ...` allow natural correction. `Save that` requires a specific series and non-negative numeric position, rechecks the source SHA-256, and records the original fields, confirmed fields, provenance, and resolution locally. `Leave it` preserves source metadata without granting confirmed authority. Changed bytes cannot inherit a stale confirmation, and no EPUB or PDF is rewritten.

Only a confirmed exact-source series record changes the ordinary shelving proposal to `Originals/Author/Series/02 - Title/original-file`; decimal positions such as `2.5` remain sortable. Unconfirmed series metadata cannot reorganize a book, and already-shelved Originals remain untouched without a separate future preview and approval. Live acceptance should deliberately leave one uncertain series entry, confirm or correct one real book, verify the source hash, and show the series-aware destination in an ordinary preview without shelving it.

Live acceptance passed on 2026-08-21. `Magic at the Gate` review `SR-909E9C9E` was deliberately left unconfirmed. Preferred `Magic in the Blood (266)` review `SR-F8BDDEE7` confirmed Allie Beckstrom volume 2 against unchanged SHA-256 `7e08f29050d19f771aa29b191a9862fb9a914dafdeb899855fd9f919396e296a`. Ordinary batch `LB-E26D366F` then placed that exact edition first in Ready with destination `Devon Monk/Allie Beckstrom/02 - Magic in the Blood/Magic in the Blood - Devon Monk.epub`. The source remained physically present in Intake and nothing was shelved. All 141 automated tests passed.

## Visual representation

The Librarian earned a new, separate Bobblehead by completing her first functional contract on 2026-08-18. Drew accepted Alex as an Alexandrian-inspired adult librarian in a low-backed white Grecian dress, tall hairstyle, jewel-coloured pharaonic collar, Egyptian brassard, and papyrus scroll, seated on a level stack of five books. Her transparent runtime asset is fitted between the Archivist and Researcher at their established height and common shelf baseline. Fine pale edge-halo removal remains a non-blocking shared Bobblehead polishing task.

Earlier project documents used *Librarian* as a preliminary name for today's Archivist. That synonym remains superseded. This document establishes a newly approved, separate Librarian role concerned with reading works rather than knowledge curation.
