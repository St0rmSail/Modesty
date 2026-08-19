# The Librarian

**Status:** Build 0.24 work and edition identity complete; demonstrated Level 2 strengthened

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

## Visual representation

The Librarian earned a new, separate Bobblehead by completing her first functional contract on 2026-08-18. Drew accepted Alex as an Alexandrian-inspired adult librarian in a low-backed white Grecian dress, tall hairstyle, jewel-coloured pharaonic collar, Egyptian brassard, and papyrus scroll, seated on a level stack of five books. Her transparent runtime asset is fitted between the Archivist and Researcher at their established height and common shelf baseline. Fine pale edge-halo removal remains a non-blocking shared Bobblehead polishing task.

Earlier project documents used *Librarian* as a preliminary name for today's Archivist. That synonym remains superseded. This document establishes a newly approved, separate Librarian role concerned with reading works rather than knowledge curation.
