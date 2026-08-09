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

**0.12.0 - Library Gateway (complete)**

Build 0.12.0 is complete. Modesty's Grand Library starts closed, separates local loopback from bounded online access, previews and approval-gates exact loans, protects secrets and local stores, quarantines sourced text returns, and records a content-free audit. The first authenticated Smithsonian return completed the Inbox-to-Research lifecycle. Active media remains fail-closed until a dedicated inspected-media intake exists. The accepted Study sequence truthfully distinguishes online access from local readiness.

Smithsonian setup and validation instructions are in [Documentation/SMITHSONIAN_SETUP.md](Documentation/SMITHSONIAN_SETUP.md).
The bounded first-expedition sequence is in [Documentation/SMITHSONIAN_EXPEDITION.md](Documentation/SMITHSONIAN_EXPEDITION.md).
