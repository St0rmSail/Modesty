# Capability Matrix

**Baseline:** Build 0.18.0 complete; Build 0.19 acceptance paused; Build 0.21 complete
**Reviewed:** 2026-08-18

| Capability | Design | Code | Demonstrated | Notes / gap |
|---|---:|---:|---:|---|
| Canonical Study background | Yes | Yes | Yes | Geometry frozen |
| Independent Modesty layer | Yes | Yes | Yes | Current standing height `0.67` |
| Grounding shadow | Yes | Yes | Yes | Study-owned and pivot-relative |
| Idle breathing | Yes | Yes | Yes | Elapsed-time, subtle, feet anchored |
| Natural blink | Yes | Yes | Yes | Clear-eyed open and closed assets |
| Eye focus/tracking | Partial | No | No | Eye artwork corrected; tracking deferred as fluff |
| Text conversation UI | Yes | Yes | Yes | Overlay in Study View; Up/Down recalls sent input and Page Up/Page Down scrolls the transcript while typing |
| Local Ollama conversation | Yes | Yes | Yes | `gemma4:e2b`; bidirectional chat confirmed |
| Conversation persistence | Yes | Yes | Yes | SQLite; restart test passed |
| Conversation history controls | Yes | Yes | Yes | Open, create, and delete conversations |
| Approved personal memories | Yes | Yes | Yes | Visible source, add, edit, delete |
| Automatic identity recognition | Partial | No | No | One Windows account does not itself identify the typist |
| Filing Cabinet vault | Yes | Yes | Yes | Private Obsidian foundation created externally |
| Living Bookshelf repository | Yes | Yes | Yes | Separate external collection and folders created |
| OKF knowledge structure | Yes | Yes | Yes | Starter index, log, and concept template created |
| Knowledge filing and retrieval | Yes | Partial | Yes | Explicit Inbox filing and bounded local excerpt retrieval demonstrated |
| Bookshelf intake and curation | Yes | Yes | Yes | Approval-gated Inbox, Workbench, and established-collection lifecycle demonstrated |
| Grand Library online mode | Yes | Yes | Yes | Closed-by-default loopback, bounded online provider, text-only media boundary, and truthful Study state demonstrated |
| Local document indexing/RAG | Yes | Yes | Yes | FTS5 passage retrieval with source paths; embeddings remain unjustified |
| Archivist | Yes | Yes | Yes | Functional contract and truthful Bobblehead presence demonstrated |
| Librarian | Yes | Yes | Yes | Level 2 demonstrated: read-only catalogue plus one reversible hashed UTF-8 repair with accepted local Keep/Toss Briefings; broader formats and semantic repair remain absent |
| Team readiness display | Yes | Yes | Yes | Archivist, Researcher, and Librarian presence, readiness lamp, Team headset, and duty-state changes demonstrated; pedestal perspective and pale extraction halos deferred to polish |
| Team orchestration | Partial | No | No | Noticeboard is only an in-memory prototype |
| Web research gateway | Yes | Yes | Yes | Smithsonian, bounded Scribble Hub discovery, and one current-story evidence pass demonstrated without account action or silent filing |
| Story-page investigation | Yes | Yes | Yes | Visible public Scribble Hub page facts and bounded review evidence feed the established Briefing lifecycle; chapters and account actions excluded |
| Same-type story comparison | Yes | Yes | Yes | Two or three visible Scribble Hub pages compare with source retention, explicit limits, and duplicate leads rather than false proof |
| Mixed-source story research | Yes | Yes | No | Scribble Hub plus bounded public English YouTube synthesis and 102 live tests pass; acceptance is paused by a persistent external Scribble Hub 522 outage |
| Briefing Hologram and Pending Reports | Yes | Yes | Yes | Readable expanding surface, compact questioning, restart-safe pending state, gated disposition, reversible duty movement, and truthful headset state demonstrated; gesture artwork remains polish |
| Local time and session presence | Yes | Yes | Yes | Afternoon and sub-minute greetings, graceful shutdown, nine-minute absence, clean restart, and isolated interrupted recovery demonstrated |
| Offline working time zones | Yes | Yes | Yes | Fixed African/GMT and DST-aware Britain, Europe, Thailand, Australia, New Zealand, and US named zones demonstrated locally |
| Background service presence | Yes | Partial | No | State is defined; hidden Study host, restore control, scheduled work, and remote client are not implemented |
| Schedule and calendar awareness | Yes | Partial | Yes | Local reminders, lifecycle commands/window, and due opening context demonstrated; recurrence, accounts, and background delivery remain unimplemented |
| Personal Chronicle | Yes | Yes | Yes | Structured episodes, visible review, corrected-place matching, concrete active-only recall, provenance, retirement exclusion, and factual-evidence boundary demonstrated |
| Voice | Partial | No | No | Config disabled |
| Vision/OCR | Partial | No | No | Config disabled; privacy controls required |
| General tools and computer actions | Partial | No | No | Permission and undo framework required |
| Agentic planning/resume | Partial | No | No | No executive implementation yet |
| Living Study activities | Rich concept | No | No | Keeping House and location behaviours remain future work |

## Known engineering debt

- `README.md`, the old punch list, and Buildlog had fallen behind Builds 0.4 through 0.8; Build 0.8.1 repairs the record.
- Runtime dependencies are captured in `requirements.txt`; installation on a clean Windows recovery remains to be rehearsed.
- `modesty.py` and duplicate boot/config paths require a non-destructive audit.
- Automated coverage currently protects knowledge-store initialization and Archivist inventory; other systems still lack focused tests.
- Configuration duplicates the Ollama model in YAML and Python.
- Window placement/settings persistence remains unimplemented.
- Generated `Backup/` snapshots and historic scaffolding should be reviewed, not casually deleted.
