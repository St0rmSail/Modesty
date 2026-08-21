# Modesty Command Help

**Status:** Authoritative user command reference

Ask Modesty **Help** or **What commands can I use?** for the short index. Ask **Help with the Grand Library**, **Help with the Researcher**, **Help with the Librarian**, **Help with the Archivist**, **Help with Briefings**, **Help with chat**, or **Help with time zones** for exact instructions. After the index is open, a natural follow-up such as **the Grand Library please** also works.

## Grand Library

- `Open the Grand Library` — opens local loopback test mode. The internet remains disconnected.
- `Open the Grand Library online` — opens bounded online access. Opening it sends nothing by itself.
- `Close the Grand Library` — closes either mode and cancels pending gateway loans.
- `Prepare a Grand Library loopback: <question>` — previews a local-only test loan.
- `Approve Grand Library loan: <loan identifier>` — approves only the exact previewed loan.

The local and online opening commands are intentionally different. Close the Grand Library before changing modes.

## Researcher

The first implemented duty is:

- `Ask the Researcher: What are the latest offerings in the harem category?`

Open the Grand Library online first. The duty opens a visible local Scribble Hub browser. When listings are visible, use **Prepare Briefing from visible listings**. No account action or filing occurs merely because the page opened.

To investigate one candidate, open its public Scribble Hub story page in that same visible browser and use **Investigate current story page**. The Researcher will prepare a bounded Briefing from visible synopsis, genres, tags, statistics, and review paragraphs. This does not download chapters, change the account, or file the report. The ordinary Briefing decision still controls whether the report is kept or tossed.

To compare candidates, visit a story page and use **Add current story to comparison**. Use **Return to latest listings** to select the next candidate. Repeat for one or two more distinct stories, then use **Prepare comparison briefing**. The Researcher accepts two or three pages, retains each source, and treats possible duplicate or cross-post similarity as a lead rather than proof. Nothing is filed until the ordinary Briefing decision.

For mixed-source research, add exactly one story with **Add current story to comparison**, paste one complete public YouTube video URL, and state the research focus in the field below it. Then use **Add YouTube transcript and prepare mixed-source briefing**. Modesty requests a bounded public English transcript without account access. Missing or restricted captions fail plainly. Timestamped transcript passages are speaker-reported evidence, not verified story facts, and focus-only relevance is not reported as page corroboration. The ordinary Briefing decision still governs retention.

If Scribble Hub shows a Cloudflare 522 error, stop refreshing and postpone the duty. That response means the external site's origin is not answering Cloudflare; it is not permission to bypass the site and does not by itself show that Modesty or the YouTube transcript adapter failed.

## Librarian

For ordinary work, speak to the visible context rather than memorizing job identifiers:

- `catalogue the books`
- `show me the duplicates`
- `show me the edition choices`
- `keep the Handbooks copy of Song and Silence`
- `prefer <displayed folder or filename>` — prepares a preference only for one displayed non-identical edition
- `yes, do that` — approves only the single duplicate-resolution preview prepared in this Study session
- `open Axeman at chapter 12`
- `keep reading`
- `save my place`
- `resume Axeman`
- `show me what can be shelved`
- `leave <displayed title or folder> out` — removes one unambiguous Ready item from the current preview
- `shelve those` — approves only the Ready list in the shelving preview currently displayed
- `show me books needing metadata`
- `review <displayed title or filename>`
- `title is <confirmed title>` / `author is <confirmed author>`
- `save that` — confirms both staged fields for the unchanged exact source
- `leave it` — closes the current metadata review without changing the catalogue

If a description matches more than one displayed file, Modesty asks for the title or folder instead of guessing. `Yes, do that` has no operational meaning unless one exact duplicate action is waiting for approval. The exact recovery forms below remain available for audit and help:

- `Ask the Librarian to inventory The Stacks`
- `Ask the Librarian to repair: <filename>`
- `Ask the Librarian to examine: <relative Intake path>`
- `Ask the Librarian to find: <words or phrase>`
- `Approve Librarian shelving: <LS-ID>`
- `Ask the Librarian to open: <title or Stacks path> at Chapter <number>`
- `Continue reading: <RP-ID>`
- `Mark my place: <RP-ID>`
- `Ask the Librarian to resume: <title or Stacks path>`
- `Ask the Librarian to identify works and editions`
- `Ask the Librarian to review edition groups`
- `Ask the Librarian to prepare exact duplicate resolution: <hash> keep: <Stacks relative path>`
- `Approve Librarian duplicate resolution: <DR-ID>`
- `Approve Librarian preferred edition: <PE-ID>`
- `Ask the Librarian to prepare a bounded Intake shelving batch`
- `Approve Librarian shelving batch: <LB-ID>`
- `Ask the Librarian to review incomplete metadata`

This performs a bounded read-only scan of copied files in `The Stacks/Intake`. It reports supported and unsupported formats, obvious damaged containers, exact duplicate groups, and stale catalogue entries. It does not rename, move, repair, convert, delete, publish, or file any reading material. The old Calibre catalogue is not required.

The first repair duty accepts one named UTF-8 `.txt` or `.md` file directly inside `The Stacks/Intake`, up to 2 MiB. It creates a provisional derivative in `The Stacks/Workbench`, records source and derivative hashes plus every mechanical change, and opens a local Briefing. **Keep Repair** retains the derivative in Workbench; **Toss Repair** deletes only that derivative. The original is never renamed, moved, overwritten, or deleted. Hyphenation and uncertain paragraph joining remain unchanged for review.

**Examine** reads one explicitly named TXT, Markdown, HTML, DOCX, EPUB, or text-layer PDF beneath Intake. It reports embedded title and author where available, a bounded opening passage, readable extent, and a proposed `Originals/Author/Title/original-file` destination. It also creates a private local passage index so **find** can return source-linked passages from works actually examined. Nothing moves until the exact `LS-ID` approval. Approval rechecks the source hash, refuses collisions, and shelves the unchanged original. Scanned PDFs require later OCR; DRM and access-control bypass are never attempted.

**Open** returns a bounded passage from the named exact edition. EPUB chapter headings such as `Chapter 12`, `Prologue`, and `Epilogue` are recognized when they appear as standalone headings. **Continue reading** displays the next passage but does not silently alter saved progress. **Mark my place** explicitly confirms the end of the latest displayed passage as the next unread position. **Resume** uses only that confirmed position and only for the same SHA-256 edition; changed or ambiguous editions fail safely. Reading positions remain private local generated data.

**Identify works and editions** incrementally reads source-supplied title, author, strong identifiers, series, series number, publisher, language, and publication date from supported files in Intake and Originals. Each invocation refreshes at most 25 changed or new files so the Study remains responsive; repeat until the reported remaining count is zero. It reports exact byte duplicates separately from shared identifiers and normalized title/author review leads. It reuses unchanged catalogue entries and never merges, renames, moves, deletes, or overwrites a file.

**Review edition groups** lists each bounded relationship once at its strongest available evidence level: exact SHA-256 duplicate, shared strong identifier, or possible same work by title and author. Generic unknown-author and untitled metadata is excluded from weak grouping. Review does not choose a preferred edition or change a file.

**Show me the edition choices** uses that same visible relationship review. **Prefer ...** may select one unambiguous member only from a displayed non-identical group; exact byte duplicates continue to use duplicate resolution. The preference preview shows the chosen reading edition and every retained alternative. Contextual **yes, do that** rechecks every member hash and records the preferred exact edition locally. No file moves or is deleted. The chosen edition may then enter the ordinary shelving preview, while alternatives remain held and retained.

**Prepare exact duplicate resolution** accepts only a currently catalogued SHA-256 duplicate group and requires Drew to name the exact member that stays canonical. Preparation changes nothing and reports every proposed Archive destination. Exact `DR-ID` approval rechecks every hash and destination, leaves the chosen copy in place, and moves redundant byte-identical copies into `The Stacks/Archive/Exact Duplicates/<hash>/...`. Nothing is deleted. Shared identifiers and possible same-work groups are ineligible.

**Show me what can be shelved** prepares one bounded Intake preview containing at most five Ready items. Destinations use only source-supplied author and title metadata already in the edition catalogue. Unknown metadata, warnings, exact or possible edition relationships, changed sources, pending single-item proposals, and occupied or competing destinations are held back with reasons. Nothing moves during preview. **Leave ... out** can remove one unambiguously described Ready item; it cannot add or redirect a file. **Shelve those** approves only the resulting Ready list; approval rechecks every hash and destination before moving any item and rolls back completed moves if a later move fails. Held and removed items stay in Intake.

**Show me books needing metadata** presents at most five incomplete Intake records that are not damaged and are not part of an edition conflict. Embedded fields, unknown fields, and a filename-derived title suggestion are labelled separately. **Review ...** can select only one item from that visible set. A filename suggestion is never staged automatically: Drew supplies a specific title and author, then **save that** records the confirmed catalogue identity against the unchanged SHA-256 source. **Leave it** records no correction. Saving never rewrites the reading file, and a changed source fails closed. The corrected item still moves only through the ordinary shelving preview and approval.

## Briefings

- **Briefing** reopens the latest undecided Pending Report.
- **Keep Privately** sends the report to the Filing Cabinet Inbox through the Archivist.
- **Bookshelf Inbox** sends it to shared intake for later curation.
- **Toss** deletes the Pending Report content without filing it.
- **Close** remains unavailable until one of those three dispositions succeeds. The selected disposition lights visibly, then Close becomes available.

Librarian repair Briefings use **Keep Repair** and **Toss Repair** instead. They govern only the provisional Workbench derivative and never file the reading material in the Filing Cabinet or Bookshelf.

## Archivist

- `Ask the Archivist to file privately: <text>`
- `Ask the Archivist to file on the Bookshelf: <text>`
- `Ask the Archivist to retrieve: <query>`
- `Ask the Archivist to review: <query>`
- `Approve the Archivist to move to Workbench: <filename>`
- `Ask the Archivist to classify: <query>`
- `Approve the Archivist to file in <collection>: <filename>`

Valid established Bookshelf collections are Projects, Research, Reference, Procedures, and Media.

## Local Library search

- `Ask the Library: <question>` — searches the local Filing Cabinet and Bookshelf and returns bounded source-linked passages.
- `Ask the Library to re-index` — refreshes the local search catalogue and reports stale entries or metadata warnings.

## Conversation

Ordinary conversation does not require a command. Type naturally and Modesty will answer through the configured local model.

- `Bye` or `Goodbye, Modesty` — Modesty says goodbye and closes the Study normally.

## Time zones

These answers are local and immediate; they do not open the Grand Library or call the language model.

- `What time is it in Uganda?`
- `What is the current time in Kenya?`
- `What time is it in Tanzania?`
- `What time is it in South Africa?`
- `What time is it in GMT?`
- `Convert 14:00 in South Africa to Uganda`
- `Convert 9:30 PM in Uganda to South Africa`
- `What time is it in London?`
- `What time is it in Marseille?`
- `What time is it in Chiang Mai?`
- `What time is it in New Zealand?`
- `What time is it in Sydney?`
- `What time is it in US East Coast?`
- `Convert 12:00 on 2026-07-15 in London to South Africa`

Supported working zones include South Africa/SAST; Uganda, Kenya, Tanzania and East Africa/EAT; GMT/UTC; Britain/London; France/Paris/Marseille; Germany/Berlin; Thailand/Bangkok/Chiang Mai; New Zealand/Auckland; Sydney, Melbourne, Brisbane, Adelaide and Perth; and US East Coast/New York, Central/Chicago, and West Coast/Los Angeles.

These answers use Modesty's installed offline timezone-rule database, including daylight-saving changes. `Australia` and `USA` alone are deliberately rejected as ambiguous; name the city or regional zone. Add `on YYYY-MM-DD` when converting a future or past event so the correct seasonal rule is applied.

## Schedule and reminders

The first local schedule commands use explicit local dates and 24-hour times so Modesty never guesses an ambiguous date.

- `Remind me on 2026-08-16 at 09:30: Call the office`
- `Show my reminders`
- `List my reminders`
- `Complete reminder 1`
- `Delete reminder 1`

Reminder numbers are stable local identifiers. Completing retains the record; deleting removes it. Calendar accounts, background notifications, and natural-language dates such as `next Friday` are not implemented yet.

Use deterministic help whenever you need supported natural examples or exact recovery wording. Examples include `What commands can I use?`, `Help with the Grand Library`, `Help with the Librarian`, `remind me how to open the Grand Library`, or a topic-only follow-up after the help index.

This document records implemented deterministic commands. Ordinary conversation does not require command phrasing.
