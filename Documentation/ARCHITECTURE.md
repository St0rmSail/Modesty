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
| The Team | `Brain/Team/archivist.py`, `Brain/Team/delegation.py` | Archivist implemented and demonstrated |
| Filing Cabinet vault | `Runtime/Knowledge/stores.py`, external configured root | Implemented and demonstrated |
| Bookshelf repository | `Runtime/Knowledge/stores.py`, external configured root | Implemented and demonstrated |
| Local Library search | `Runtime/Knowledge/catalog.py`, SQLite FTS5 | Implemented and demonstrated |
| Grand Library gateway | `Runtime/Library/` | Loopback demonstrated; encrypted credential storage and bounded Smithsonian validation implemented; expedition provider not implemented |
| Perception, voice, tools, planning | package/config placeholders | Not implemented |

## Data ownership

- `Data/modesty.db` is local generated state and is excluded from Git.
- `Data/Secrets/` contains current-user encrypted credentials and is excluded from Git; clear-text credentials never belong in repository files, chat, audit logs, loan packets, or returned notes.
- Conversation history and approved personal memories are structured parts of the Filing Cabinet domain.
- The repository stores Modesty's design, contracts, schemas, and implementation record.
- The Filing Cabinet stores private personal and working knowledge.
- The Bookshelf stores curated shared knowledge used by Modesty and the authorized Team.

## Knowledge boundary

The approved direction is two physically distinct local stores and one connection mode:

```text
Filing Cabinet/   # private Obsidian vault; local access only
Bookshelf/        # living shared repository; local and curated
Grand Library     # explicit online gateway state; not a directory
```

New and returned material enters a staging area before becoming established Bookshelf knowledge. Modesty may use both local stores through the Archivist. Online agents may borrow selected, read-only packets from the Bookshelf and return sourced contributions, but receive no filesystem or vault access. Returned contributions land in the Bookshelf Inbox and cannot silently rewrite established knowledge.

The Bookshelf should use Markdown compatible with Open Knowledge Format (OKF). The Filing Cabinet may use natural Obsidian Markdown with lighter metadata. OKF is an authoring/interchange convention, not the permission system. Deterministic code must enforce the physical boundary.

The configured roots are currently `E:\Modesty Filing Cabinet` and `E:\Modesty Bookshelf`. They are initialized idempotently during startup. Initialization creates only missing foundations and never replaces an existing file.

## Bookshelf growth pipeline

```text
Create, discover, or receive knowledge
  -> Bookshelf Inbox
  -> Archivist validation and provenance check
  -> Workbench for linking, reconciliation, and curation
  -> established Bookshelf collection
  -> later revision, supersession, or Archive
```

Trust levels prevent both uncontrolled growth and needless approval friction:

- **Routine:** formatting, indexes, links, and clear metadata repair; Archivist may apply automatically.
- **Normal:** sourced, non-destructive additions; Archivist may integrate and report.
- **Important:** replacing established knowledge or changing a project decision; Drew approves.
- **Protected:** moving anything from the Filing Cabinet to the Bookshelf; Drew explicitly approves.

## Engineering boundaries

- Rendering draws state; it does not decide behaviour.
- Animation samples elapsed time and requests lightweight redraws.
- Character assets define pose-local pivots; Study configuration defines placement.
- The Study owns lighting and ground effects.
- The local model converses; specialist services and Team members perform bounded work.
- Permission decisions must not be delegated to a language model.
