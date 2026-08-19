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

**0.24.0 - Work and Edition Identity (complete)**

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

Smithsonian setup and validation instructions are in [Documentation/SMITHSONIAN_SETUP.md](Documentation/SMITHSONIAN_SETUP.md).
The bounded first-expedition sequence is in [Documentation/SMITHSONIAN_EXPEDITION.md](Documentation/SMITHSONIAN_EXPEDITION.md).
