# Modesty

Modesty is Drew's local-first personal AI assistant, presented through the Study View: a Windows application showing Modesty in her permanent Study.

Run the application from the repository root:

```powershell
python main.py
```

`main.py` is the canonical entry point. Do not rename it or create numbered variants.

## Project record

Start with [The Ledger](Documentation/PROJECT_LEDGER.md). It links the approved canon, actual software architecture, Team roles, capability status, decisions, and roadmap.

The repository is authoritative for Modesty's design and implementation. The future Grand Library is for the knowledge Modesty and the Team use; it is not a substitute for project documentation.

## Current build

**0.8.1 - The Ledger**

Build 0.8.0 provides local conversation through Ollama, persistent SQLite conversation history, and explicit personal memories with visible source, edit, and delete controls. Build 0.8.1 consolidates the project record without changing runtime behaviour.
