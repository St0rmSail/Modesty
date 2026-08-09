# Capability Matrix

**Baseline:** Build 0.11.0 complete; Build 0.12.0 in progress
**Reviewed:** 2026-08-08

| Capability | Design | Code | Demonstrated | Notes / gap |
|---|---:|---:|---:|---|
| Canonical Study background | Yes | Yes | Yes | Geometry frozen |
| Independent Modesty layer | Yes | Yes | Yes | Current standing height `0.67` |
| Grounding shadow | Yes | Yes | Yes | Study-owned and pivot-relative |
| Idle breathing | Yes | Yes | Yes | Elapsed-time, subtle, feet anchored |
| Natural blink | Yes | Yes | Yes | Clear-eyed open and closed assets |
| Eye focus/tracking | Partial | No | No | Eye artwork corrected; tracking deferred as fluff |
| Text conversation UI | Yes | Yes | Yes | Overlay in Study View |
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
| Grand Library online mode | Yes | Yes | Yes | Closed-by-default loopback and one-purpose Smithsonian mode demonstrated; media policy and final Study representation remain build work |
| Local document indexing/RAG | Yes | Yes | Yes | FTS5 passage retrieval with source paths; embeddings remain unjustified |
| Archivist | Yes | Yes | Yes | Functional contract and truthful Bobblehead presence demonstrated |
| Team readiness display | Yes | Yes | Yes | Archivist presence, absence sign, readiness lamp, and Team headset demonstrated |
| Team orchestration | Partial | No | No | Noticeboard is only an in-memory prototype |
| Web research gateway | Partial | Partial | Yes | First authenticated Smithsonian retrieval completed through quarantine and Archivist curation; general Researcher remains unimplemented |
| Voice | Partial | No | No | Config disabled |
| Vision/OCR | Partial | No | No | Config disabled; privacy controls required |
| General tools and computer actions | Partial | No | No | Permission and undo framework required |
| Agentic planning/resume | Partial | No | No | No executive implementation yet |
| Living Study activities | Rich concept | No | No | Keeping House and location behaviours remain future work |

## Known engineering debt

- `README.md`, the old punch list, and Buildlog had fallen behind Builds 0.4 through 0.8; Build 0.8.1 repairs the record.
- Dependency installation is not captured in a committed `requirements.txt` or equivalent.
- `modesty.py` and duplicate boot/config paths require a non-destructive audit.
- Automated coverage currently protects knowledge-store initialization and Archivist inventory; other systems still lack focused tests.
- Configuration duplicates the Ollama model in YAML and Python.
- Window placement/settings persistence remains unimplemented.
- Generated `Backup/` snapshots and historic scaffolding should be reviewed, not casually deleted.
