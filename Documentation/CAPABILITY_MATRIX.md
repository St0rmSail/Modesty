# Capability Matrix

**Baseline:** Build 0.10.0 in progress, inventory demonstrated 2026-08-08
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
| Bookshelf intake and curation | Yes | Partial | Partial | Inbox and Workbench exist; Archivist workflow remains unimplemented |
| Grand Library online mode | Yes | No | No | Explicit gateway state; not a storage directory |
| Local document indexing/RAG | Partial | No | No | FTS5 first; embeddings later if justified |
| Archivist | Yes | Partial | Partial | Read-only inventory demonstrated; curation and Bobblehead remain |
| Team orchestration | Partial | No | No | Noticeboard is only an in-memory prototype |
| Web research gateway | Partial | No | No | Bookshelf-loan and returned-contribution boundary required |
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
