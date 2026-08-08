# The Team

**Status:** Canonical framework; Archivist foundation implemented
**Reviewed:** 2026-08-08

The Team is a group of unseen functional specialists working behind the scenes. They are not chat personalities and never speak to Drew as alternate characters. Modesty is the sole conversational presence: she consults the Team through her headset and communicates their results. Team activity is monitored through corresponding Bobbleheads on her Bookshelf.

There should be no unnecessary multi-agent theatre. A separate agent must earn its existence through a distinct skill set, permission boundary, or workload.

## Shared contract

Every implemented member needs:

- a narrow responsibility;
- accepted inputs and returned outputs;
- permitted tools and data zones;
- failure and retry behaviour;
- provenance and activity reporting;
- an interruption/approval boundary;
- a truthful Bobblehead state when applicable.

## Current roster

| Member | Responsibility | Boundary | Status |
|---|---|---|---|
| **Modesty / Executive** | Understand intent, converse, obtain consent, route work, and report results | Does not replace every specialist | Role canonical; orchestration not implemented |
| **Archivist** | Maintain the Filing Cabinet and living Bookshelf; curate, classify, link, index, retrieve, and preserve provenance | Cannot move Filing Cabinet material onto the Bookshelf without Drew's approval | Inventory, retrieval, filing, and approval-gated Bookshelf curation demonstrated; visual representation remains |
| **Researcher** | Conduct explicit online research and return sourced findings | Borrows task-relevant Bookshelf packets; no local filesystem access | Conceptual |
| **Nurse** | Health, medication, reminders, and wellbeing support | High-trust domain requiring explicit safeguards | Conceptual |
| **Planner** | Decompose and track longer jobs | Plans do not imply permission to execute | Implied; not specified enough to build |
| **Vision** | Webcam, screen, screenshot, and OCR perception | Explicit indicators and hard-off controls required | Conceptual |
| **Voice** | Speech-to-text and text-to-speech | Microphone access must be explicit | Conceptual |
| **Accountant** | Budget, finance, and shopping support | Financial actions require strong confirmation | Recurring concept; contract unresolved |
| **Gaming Guru** | Games, character designs, modlists, and gaming reference knowledge | Separate gaming material from Modesty project canon | Domain confirmed; contract unresolved |

Artist, briefing/courier, and fishing-oriented specialists appeared in brainstorming. They remain Proposed until Drew confirms that each deserves a permanent Team role rather than being a tool or capability of another member.

## Archivist clarification

Early project documents used **Librarian** for the knowledge role. The current term is **Archivist**. This is a terminology evolution, not evidence of two Team members.

Modesty is small by design and should not curate these collections herself. She asks the unseen Archivist to perform bounded archival work and presents the result herself. The Archivist maintains the private Filing Cabinet, grows the Bookshelf, prepares loans when the Grand Library is online, and processes returned contributions through Inbox and Workbench stages. The Archivist may use deterministic tooling and a stronger authorized model for individual curation tasks, while all security decisions remain in code and under Drew's control.

## Bobbleheads

Bobbleheads are varied, collected anime-style figurines, roughly similar in scale rather than a matching set. They are visual ambassadors, not literal portraits. A Bobblehead is earned only when its Team member exists and has been tested.

The first earned Bobblehead is the Archivist: a typically stern librarian in a tweed pencil skirt and oversized glasses. Her design should remain readable at bookshelf scale. Modesty's headset is the visible communication channel between Modesty and the unseen Team; it is not evidence that the Team can speak directly to Drew.

Expected states are Idle, Working, Waiting, Needs Attention, and Offline/Absent. Their behaviour must report real subsystem state.
