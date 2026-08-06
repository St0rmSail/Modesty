# MODESTY PROJECT PUNCH LIST

**Purpose:** This file is the compact, non-code source of truth for Project Modesty.  
**Location:** Keep it in the root of `E:\Modesty`.  
**Last reviewed:** 2026-08-04  
**Current engineering marker:** **Build 0.2.0 — Basic Study window exists**

> Modesty is an enthusiast project, not a commercial production. Prefer simple, maintainable, reusable solutions that a non-programmer can install, test, and recover.

---

## 1. Project in one paragraph

Modesty is Drew's local-first personal AI assistant, presented through the **Study View**: a live Windows application showing Modesty in her warm, permanent Study. She begins as a visible placeholder, becomes a usable chatbot, gains persistent memory and personal knowledge, then receives perception, tools, specialist Team members, planning, delegation, and agentic behaviour. After the core system is complete, development changes from “building Modesty” to adding capabilities, activities, animations, and personality over time.

---

## 2. Working rules

- Drew is the **Project Owner, Creative Director, and Integrator**, not the programmer.
- ChatGPT supplies complete code and precise copy/paste/save/run instructions.
- Never destroy a working build. Back up or version each known-good milestone.
- Build the smallest working step, test it, then continue.
- The Study geometry is frozen unless a genuine defect is found.
- Visual design must have **enduring appeal**.
- Modesty is alluring, confident, and knowingly playful, while remaining tasteful and non-explicit.
- The Study View supports the software; it must not become a resource-hungry production.
- Update this file whenever a milestone completes or the roadmap materially changes.

---

## 3. Canonical terms

- **The Study:** Modesty's virtual home and working environment.
- **Study View:** The live application view of the Study shown on Drew's monitor.
- **Painting:** The framed artwork above the grandfather clock.
- **Avatar:** Modesty's visible, animated representation.
- **The Team:** Specialist agents working behind the scenes.
- **Bobbleheads:** Study representations of Team members and their status.
- **Resident:** A permanent element of the Study.
- **Transient:** An object that appears only when needed, such as Modesty's chair.
- **Boot Sequence:** The transition from graphite concept view to the complete, operational Study View.
- **Keeping House:** Modesty's maintenance activities, including plants, bonsai, bobbleheads, and clock.

---

## 4. Major roadmap

### M0 — Foundation and identity
**Goal:** Define what Modesty is and establish a runnable foundation.  
**Status:** **Mostly complete**

Completed:
- Mission and local-first direction
- Study layout and final perspective
- Canonical vocabulary
- Modesty's daywear, default pose, jewellery, movement philosophy
- Early Python project structure
- Configuration paths
- Basic boot diagnostics
- Basic Team noticeboard concept
- Basic PySide6 Study window

Still needed:
- Consolidate duplicate/older boot paths
- Record current dependencies cleanly
- Confirm one canonical application entry point

### M1 – Static Study View

████████████████████ 100%

COMPLETE

Completed:

✓ Study renders
✓ Correct scaling
✓ Correct resizing
✓ Canonical Character Reference
✓ Transparent Modesty asset
✓ Independent render layer
✓ Character positioning

### M2 – Living Presence

██░░░░░░░░░░░░░░░░ 10%

Started

Completed:

□ Contact shadow

□ Idle breathing

□ Blink

□ Eye focus

□ Window conversation pose

□ Desk conversation pose

□ Transition framework

### M3 — Usable chatbot
**Goal:** Modesty can hold a conversation instead of being decoration.  
**Status:** **Early groundwork only**

Definition of done:
- Text entry and readable response area
- Ollama connection
- One chosen local language model
- Canonical system/personality prompt
- Current conversation history
- Errors displayed in plain language
- Study View reflects listening, thinking, and speaking states

### M4 — Persistent memory
**Goal:** Modesty remembers Drew, projects, preferences, and prior work across sessions.  
**Status:** **Folders and concepts exist; implementation not confirmed**

Required blocks:
- SQLite or equivalent structured memory
- Vector database
- Embedding model
- Document ingestion
- Retrieval-Augmented Generation (RAG)
- Memory write rules
- Memory correction and deletion
- Source/provenance tracking
- Backup and recovery

### M5 — Knowledge and Grand Library
**Goal:** Modesty can search and use local documents reliably.  
**Status:** **Concept designed; implementation not confirmed**

Required blocks:
- Watched knowledge folders
- Supported file types
- Chunking and indexing
- Search/retrieval interface
- Grand Library online/offline state
- Glasses and Library animation added later, after functionality works

### M6 — Perception and communication
**Goal:** Give Modesty practical eyes, ears, and voice.  
**Status:** **Not implemented**

Required blocks:
- Webcam access with explicit privacy controls
- Screen/screenshot understanding
- OCR
- Microphone input
- Speech-to-text
- Text-to-speech
- Camera indicator and hard off switch
- Vision reflected by the eyes in the Boot Sequence

### M7 — Tools and useful assistance
**Goal:** Modesty can act on the computer with permission.  
**Status:** **Architecture placeholders only**

Possible early tools:
- File search and document handling
- Calendar and reminders
- Email support
- Notes and project tracking
- Web research through an explicit online gateway
- Health and medication support through the Nurse
- Logging, permissions, confirmation, and undo where practical

### M8 — Team and orchestration
**Goal:** Specialist agents perform bounded jobs under Modesty's direction.  
**Status:** **Conceptual structure exists; members incomplete**

Required blocks:
- Executive/orchestrator
- Task routing
- Team member contracts
- Shared noticeboard/event system
- Tool permissions
- Failure handling
- Activity/status reporting through Bobbleheads
- No unnecessary multi-agent theatre

### M9 — Agentic Modesty
**Goal:** Modesty can plan, delegate, use tools, remember, resume, and report results.  
**Status:** **Not implemented**

Definition of done:
- Breaks goals into steps
- Selects appropriate tools or Team members
- Requests approval for consequential actions
- Executes and verifies work
- Recovers from partial failure
- Resumes interrupted tasks
- Records useful outcomes in memory
- Explains what she did without dumping internal machinery on Drew

### M10 — Living Study
**Goal:** Ongoing enrichment after core capability is stable.  
**Status:** **Design library growing**

Examples:
- Keeping House
- Team checks and Bobblehead behaviour
- Grand Library reveal
- Desk, window, and carpet conversational positions
- Reading, sunbathing, walking, resting
- Transient chair and props
- Outfit context
- More Team members
- Additional personality and animations

This milestone has no final endpoint.

---

## 5. Current implementation snapshot

Observed in the 2026-08-04 folder snapshot:

- `main.py` starts Runtime bootstrap and the Study window.
- `Runtime/study.py` creates a PySide6 window titled **Modesty's Study** at 1280×720.
- The current Study window displays centred greeting text, not the Study artwork.
- Runtime configuration defines folders for Obsidian, VectorDB, OCR, and Knowledge.
- Bootstrap checks for the Obsidian notebook path and creates a sample in-memory NoticeBoard.
- An Ollama diagnostic/boot path exists.
- `Brain/modesty.yaml` names `llama3.1:latest`, with internet, voice, and vision disabled.
- Brain subsystem folders exist, but most contain only package placeholders.
- `Buildlog.md` records the first successful boot.
- There appear to be older and newer boot paths. These must be audited and consolidated before adding more layers.
- The included `.venv` makes snapshots unnecessarily large; future snapshots should normally exclude it.

### Honest progress estimate

- Creative foundation: **about 80%**
- Runnable application foundation: **about 35%**
- Visible Study placeholder: **about 15%**
- Usable chatbot: **about 10%**
- Persistent memory/RAG: **about 5%**
- Perception: **about 2%**
- Tools and Team orchestration: **about 5%**
- Agentic AI: **about 2%**
- Living Study animations: **design-rich, implementation near 0%**

These percentages are navigation aids, not engineering measurements.

---

## 6. YOU ARE HERE

**Current focus: M1 — Visible placeholder**

Next concrete punch list:

- [ ] Make a safe backup of the current working folder.
- [ ] Remove `.venv`, caches, logs, and generated data from future snapshots.
- [ ] Audit which entry point is canonical: `main.py` or `modesty.py`.
- [ ] Consolidate duplicate boot code without breaking the current build.
- [ ] Put the approved Study background into a clearly named asset folder.
- [ ] Display that image correctly in `Runtime/study.py`.
- [ ] Test resize, maximise, minimise, close, and relaunch.
- [ ] Save window size and position.
- [ ] Add the static Modesty placeholder only after the background is stable.
- [ ] Create a known-good milestone backup: **M1 Study View Placeholder**.
- [ ] Update this file and `Buildlog.md`.

---

## 7. Team status — compact marker

- **Modesty / Executive:** role defined; orchestration not implemented.
- **Nurse:** role concept exists; tools and workflows not implemented.
- **Librarian:** represented by Knowledge, Obsidian, VectorDB, and Grand Library concepts; RAG not implemented.
- **Vision:** role defined by webcam/screen/OCR needs; not implemented.
- **Voice:** role defined; not implemented.
- **Researcher:** online research role discussed; explicit gateway not implemented.
- **Planner:** planning role implied; not implemented.
- **Accountant:** recurring character and possible finance/budget specialist; not specified enough to build.
- **NoticeBoard:** small in-memory prototype exists; persistence and real routing are absent.

A separate detailed Team document should be maintained once roles, tools, permissions, and dependencies are audited.

---

## 8. Update protocol for future snapshots

Whenever a Modesty snapshot is shared:

1. Read this file first.
2. Read `Buildlog.md`.
3. Inspect the actual code and compare it with the claims above.
4. Correct stale percentages and milestone status.
5. Add newly completed items.
6. Mark the exact next concrete task.
7. Do not assume a planned folder means a feature is implemented.
8. Do not overwrite known-good code without giving Drew backup instructions.
9. Return an updated copy of this file for placement in `E:\Modesty`.
10. Trigger a roadmap review whenever a milestone reaches 100%.

---

## 9. Immediate decision

The next engineering action is **not** choosing a Vector DB or adding animations.

It is:

> **Turn the existing PySide6 greeting window into the approved static Study View, while preserving the current runnable build.**
