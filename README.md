# Modesty

Modesty is Drew's local-first personal AI assistant, presented through the Study View: a Windows application showing Modesty in her permanent Study.

Run the application from the repository root:

```powershell
python main.py
```

Install the recorded Python dependencies into the active environment when setting up or recovering Modesty:

```powershell
python -m pip install -r requirements.txt
```

`main.py` is the canonical entry point. Do not rename it or create numbered variants.

## Project record

Start with [The Ledger](Documentation/PROJECT_LEDGER.md). It links the approved canon, actual software architecture, Team roles, capability status, decisions, and roadmap.

The repository is authoritative for Modesty's design and implementation. The private Filing Cabinet and living shared Bookshelf hold the knowledge Modesty and the Team use. The Grand Library is the explicit online mode through which approved Bookshelf material may be borrowed and new knowledge returned.

## Current build

**0.31.0 - Series Review Desk (complete)**

Build 0.29 adds a bounded **Metadata Review Desk** for incomplete Intake records. It visibly separates embedded catalogue fields, filename suggestions, and Drew-confirmed corrections; requires both title and author plus explicit `save that`; binds corrections to the unchanged SHA-256 source; never rewrites a book; and sends corrected items back through the ordinary shelving preview. Live acceptance left the Sandstorm suggestion unchanged once, then confirmed `Sandstorm: Mastering the Perils of Fire and Sand` by Bruce R. Cordell and placed that exact unchanged source first in the ordinary shelving preview. All 135 tests passed.

Build 0.30 adds a bounded **Preferred Edition Desk** for non-identical files that share relationship evidence. Drew selects one exact displayed edition; approval rechecks every member hash and records only a reading preference. No copy moves or is deleted. Live acceptance preferred the `(266)` `Magic in the Blood` EPUB, retained both exact source files with verified hashes, placed `(266)` first in Ready, and held `(251)` as the retained alternative. All 138 tests passed.

Build 0.31 adds a bounded **Series Review Desk**. Source-supplied series fields remain visibly unverified until Drew confirms or corrects one exact book. Confirmed series identity is hash-bound, never rewrites the source, and produces a sortable `Author/Series/02 - Title/original-file` destination through the ordinary shelving gate. Live acceptance left `Magic at the Gate` unconfirmed, confirmed preferred `Magic in the Blood (266)` as Allie Beckstrom volume 2, preserved its exact hash, and produced the accepted series-aware preview. All 141 tests passed.

Build 0.13 completed the Researcher, visible bounded Scribble Hub discovery, Briefing Hologram, Pending Report decisions, and truthful Team presentation state. Build 0.14 added local time, persistent session presence, clean/interrupted shutdown awareness, contextual greetings, and immediate offline working-time conversions.

Build 0.15 adds inspectable, explicitly narrative autobiography with bounded topic recall, correction and retirement controls, prompt-grounded fidelity, and a strict factual-evidence boundary. Autonomous episode creation remains deliberately disabled. See [Modesty's Personal Chronicle](Documentation/PERSONAL_CHRONICLE.md).

Build 0.16 adds persistent local reminders, deterministic lifecycle commands, a visible Schedule window, and bounded due/overdue opening notices. See [Schedule and Reminders](Documentation/SCHEDULE_AND_REMINDERS.md).

Build 0.17 extends the Researcher from listing discovery to a bounded evidence pass over the currently visible public Scribble Hub story page. It separates page facts, reader reports, cautions, missing evidence, recommendation strength, source, and retrieval time while excluding chapter acquisition and account actions. The complete live Briefing flow passed on 2026-08-16. See [The Researcher](Documentation/RESEARCHER.md).

Build 0.18 adds bounded same-source-type corroboration: collect two or three public Scribble Hub story pages, compare shared and distinguishing signals, retain every source, and flag likely duplicate or cross-post candidates without presenting similarity as proof. The complete live comparison passed on 2026-08-16. It prepares the Level 4 research machinery but does not earn Level 4 until mixed source types are synthesized successfully.

Build 0.19 attempts the Researcher's Level 4 threshold by combining one visible Scribble Hub story page with one explicitly supplied public English YouTube transcript. Timestamped speaker-reported passages remain distinct from observed page metadata, conflicts and missing corroboration are explicit, and unavailable captions fail closed. See [YouTube Research Boundary](Documentation/YOUTUBE_RESEARCH.md).

The implementation and 102-test live suite are complete. The final end-to-end acceptance run was paused on 2026-08-16 because Scribble Hub returned Cloudflare 522 origin timeouts for several hours. This is an external source outage, not a demonstrated Modesty failure. Build 0.19 remains uncommitted and the Researcher remains at demonstrated Level 3 until a real mixed-source Briefing and disposition pass after Scribble Hub recovers.

Build 0.20 establishes canonical **The Stacks** at `E:\Modesty Stacks` and gives the Librarian a bounded read-only catalogue of copied Intake samples. The lost Calibre library is no longer a prerequisite. No repair, conversion, rename, move, deletion, publication, or reading-continuity work enters this first duty.

Drew accepted the live duty on 2026-08-18: the Librarian catalogued six supported Intake files, reported no unsupported or damaged items, and changed no reading file. She therefore earns demonstrated capability Level 1. Her earned Alexandrian Librarian Bobblehead is now fitted truthfully between the Archivist and Researcher.

Build 0.21 adds one deliberately bounded repair path for a named UTF-8 Markdown or plain-text Intake file. The original remains byte-for-byte untouched; a mechanically repaired derivative, source/output hashes, action log, cautions, and resolution state remain local to The Stacks. The existing Briefing Hologram presents Keep Repair or Toss Repair rather than filing copyrighted reading material through the Archivist. Drew accepted both live dispositions: Keep retained only the repaired Workbench derivative, Toss removed only its provisional derivative, and both originals retained their pre-test hashes. The Librarian therefore advances to demonstrated Level 2.

Build 0.22 turns that manifest into a working private catalogue. The Librarian can examine a named nested TXT, Markdown, HTML, DOCX, EPUB, or text-layer PDF; report its source metadata and readable opening; index bounded source-linked passages; search works she has actually examined; and propose a coherent Author/Title home. Nothing moves until an exact shelving approval rechecks the original hash and destination. Live acceptance read 167,521 words from the real `Axeman` EPUB and retrieved five passages for distinctive Chapter 12 wording. Current EPUB labels identify spine documents rather than human chapters; chapter-heading recognition is deferred to reading continuity. OCR, protected formats, batch sorting, duplicate merging, and reading position remain later work. The Librarian remains at Level 2 because this is bounded retrieval rather than evidence-led investigation.

Build 0.23 recognizes conservative human chapter headings inside EPUB spine documents and adds explicit reading continuity. Drew can open an exact edition at a chapter, continue through bounded passages without silently advancing saved progress, mark the latest displayed endpoint deliberately, and resume after restart. Positions are keyed to source SHA-256; changed or ambiguous editions fail safely. Axeman's Chapter 12 open, continue, mark, restart, and resume sequence passed live alongside all 120 automated tests. A dedicated visual reader, annotations, synchronization, and automatic update tracking remain later work.

Build 0.24 adds an incremental work-and-edition catalogue across Intake and Originals. It retains source-supplied bibliographic fields, proves exact duplicates only by hash, separates shared identifiers from weaker title/author review leads, and reuses unchanged entries. Live acceptance catalogued 75 files with 27 authors, 10 series, three exact duplicate groups, two shared strong-identifier groups, six possible same-work groups, and no metadata failures; the immediate repeat reused all 75 entries. It does not merge, delete, rename, move, or choose a preferred edition.

Build 0.25 exposes the exact files behind those relationship counts. Each bounded group is labelled as an exact hash duplicate, shared strong identifier, or possible title/author match; generic untitled and unknown-author metadata cannot create weak false groups. Live acceptance reported three exact duplicate pairs and one non-identical pair sharing an ISBN, with exact paths, formats, and sizes. No weak match was invented from missing author metadata. This review remains read-only and makes no preferred-edition, consolidation, deletion, or shelving decision.

Build 0.26 adds the first governed exact-duplicate resolution. Drew names the canonical path from a proven hash group, reviews a persistent `DR-ID` plan, and approves it exactly. The accepted `Song And Silence` resolution retained the Handbooks copy and archived the byte-identical root Intake copy without deletion. Changed sources, occupied destinations, non-identical editions, and unapproved plans fail safely.

Build 0.27 replaces routine command memorization with concise contextual guidance. Exact commands and IDs remain underneath for safety, recovery, and audit, while normal operation accepts requests such as showing duplicates, choosing a displayed copy, approving the single prepared action, and opening, continuing, saving, or resuming a reading place. Ambiguous choices stop for clarification and no confirmation gate is removed. The natural duplicate and restart-safe reading flows passed live alongside all 127 automated tests.

Smithsonian setup and validation instructions are in [Documentation/SMITHSONIAN_SETUP.md](Documentation/SMITHSONIAN_SETUP.md).
The bounded first-expedition sequence is in [Documentation/SMITHSONIAN_EXPEDITION.md](Documentation/SMITHSONIAN_EXPEDITION.md).
