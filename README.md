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

**0.16.0 - Schedule and Reminders (complete)**

Build 0.13 completed the Researcher, visible bounded Scribble Hub discovery, Briefing Hologram, Pending Report decisions, and truthful Team presentation state. Build 0.14 added local time, persistent session presence, clean/interrupted shutdown awareness, contextual greetings, and immediate offline working-time conversions.

Build 0.15 adds inspectable, explicitly narrative autobiography with bounded topic recall, correction and retirement controls, prompt-grounded fidelity, and a strict factual-evidence boundary. Autonomous episode creation remains deliberately disabled. See [Modesty's Personal Chronicle](Documentation/PERSONAL_CHRONICLE.md).

Build 0.16 adds persistent local reminders, deterministic lifecycle commands, a visible Schedule window, and bounded due/overdue opening notices. See [Schedule and Reminders](Documentation/SCHEDULE_AND_REMINDERS.md).

Smithsonian setup and validation instructions are in [Documentation/SMITHSONIAN_SETUP.md](Documentation/SMITHSONIAN_SETUP.md).
The bounded first-expedition sequence is in [Documentation/SMITHSONIAN_EXPEDITION.md](Documentation/SMITHSONIAN_EXPEDITION.md).
