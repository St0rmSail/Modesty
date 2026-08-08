# Modesty

Modesty is Drew's local-first personal AI assistant, presented through the Study View: a Windows application showing Modesty in her permanent Study.

Run the application from the repository root:

```powershell
python main.py
```

`main.py` is the canonical entry point. Do not rename it or create numbered variants.

## Project record

Start with [The Ledger](Documentation/PROJECT_LEDGER.md). It links the approved canon, actual software architecture, Team roles, capability status, decisions, and roadmap.

The repository is authoritative for Modesty's design and implementation. The private Filing Cabinet and living shared Bookshelf hold the knowledge Modesty and the Team use. The Grand Library is the explicit online mode through which approved Bookshelf material may be borrowed and new knowledge returned.

## Current build

**0.12.0 - Library Gateway (in progress)**

Build 0.11.0 is complete. Modesty can search source-linked passages across the private Filing Cabinet and shared Bookshelf through a local SQLite FTS5 index that tracks changed, moved, and deleted files. The next build establishes the explicit, bounded Grand Library online gateway.
