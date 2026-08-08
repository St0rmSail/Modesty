# System Architecture

**Status:** Current implementation plus approved boundaries
**Reviewed:** 2026-08-08

## Runtime path

```text
main.py
  -> Runtime.Core.bootstrap.startup()
  -> Runtime.study.run()
       -> StudyRenderer
       -> ConversationPanel
```

`main.py` is the only manual entry point. `modesty.py` and the duplicate `Brain/Boot` path are legacy structures pending audit; they are not alternative launch instructions.

## Concept to software map

| Design concept | Current software counterpart | State |
|---|---|---|
| Study View | `Runtime/study.py` | Implemented |
| Study and character layers | `Runtime/Rendering/renderer.py` | Implemented |
| Study-owned contact shadow | `Runtime/Rendering/shadows.py`, `Config/study_lighting.json` | Implemented |
| Pose pivot and placement | `Assets/Modesty/Standing/pose.json`, `Config/modesty_position.json` | Implemented |
| Breathing and blinking | `Runtime/Animation/` | Implemented |
| Local conversation | `Runtime/Conversation/`, Ollama HTTP API | Implemented |
| Current local model | `gemma4:e2b` | Implemented and tested |
| Conversation history | `Brain/Memory/database.py`, SQLite | Implemented and restart-tested |
| Approved personal facts | `personal_memories` table and memory dialogs | Implemented and tested |
| Noticeboard | `Runtime/Core/noticeboard.py` | Prototype only |
| The Team | `Brain/Team/` | Package placeholder only |
| Grand Library | no active implementation | Designed, not implemented |
| Perception, voice, tools, planning | package/config placeholders | Not implemented |

## Data ownership

- `Data/modesty.db` is local generated state and is excluded from Git.
- Conversation history and approved personal memories are structured data, not the Grand Library.
- The repository stores Modesty's design, contracts, schemas, and implementation record.
- The Grand Library will store knowledge used by Modesty and the Team.

## Grand Library boundary

The approved direction is two physically distinct local roots:

```text
Grand Library/
  Private/   # available to Modesty and authorized local services only
  Shared/    # eligible for bounded, approved use by online agents
```

New material is Private by default. Labels are useful metadata but are not the sole security boundary. Modesty may search both through the Archivist; online agents receive only selected packets from Shared. They do not receive direct filesystem or vault access.

The Library should use Markdown compatible with Open Knowledge Format (OKF). OKF is an authoring/interchange convention, not the permission system. Modesty-specific metadata may add visibility and provenance fields, but deterministic code must enforce the physical boundary.

## Engineering boundaries

- Rendering draws state; it does not decide behaviour.
- Animation samples elapsed time and requests lightweight redraws.
- Character assets define pose-local pivots; Study configuration defines placement.
- The Study owns lighting and ground effects.
- The local model converses; specialist services and Team members perform bounded work.
- Permission decisions must not be delegated to a language model.
