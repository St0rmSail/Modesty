# Decision Log

**Reviewed:** 2026-08-08

This compact register records settled decisions. Create a separate detailed decision record only when consequences or alternatives need more space.

| ID | Decision | Status |
|---|---|---|
| D-001 | Modesty is a local-first enthusiast project, not a commercial-scale production. | Canonical |
| D-002 | Drew is Project Owner, Creative Director, and Integrator; instructions must not assume programming knowledge. | Canonical |
| D-003 | Preserve a runnable build; make small demonstrable changes and document milestones. | Canonical |
| D-004 | `python main.py` is the canonical launch path; numbered filenames are forbidden. | Implemented |
| D-005 | The Study View is a truthful, diegetic interface rather than a conventional dashboard. | Canonical |
| D-006 | The approved Study geometry is frozen; Residents and Transients have distinct meanings. | Canonical |
| D-007 | Modesty is one identity; Anita and Merry are personality aspects, not separate entities. | Canonical |
| D-008 | Character placement uses Study-relative coordinates while each pose owns its normalized pivot. | Implemented |
| D-009 | Shadows belong to Study lighting; breathing and blinking use lightweight elapsed-time animation. | Implemented |
| D-010 | Canonical Character Reference v1.00 anchors visual identity; the clear-eyed render is the current standing asset. | Implemented |
| D-011 | Standing height is `0.67` at the current position; use `0.72` at the front window-frame edge. | Implemented |
| D-012 | The chosen local conversation model is Ollama `gemma4:e2b`. | Implemented |
| D-013 | Conversation history and approved personal facts use local SQLite storage with user-visible controls. | Implemented |
| D-014 | The repository is authoritative for project canon, architecture, status, and contracts. | Canonical |
| D-015 | The Grand Library holds operational knowledge and begins with physically separate Private and Shared roots. | Approved direction |
| D-016 | New Library material is Private by default; only Drew can approve promotion to Shared. | Approved direction |
| D-017 | Adopt OKF-compatible Markdown from the Library foundation; OKF does not enforce permissions. | Approved direction |
| D-018 | Modesty fronts Library interactions; the Archivist performs curation and retrieval work. | Canonical boundary |
| D-019 | Online agents receive bounded, auditable Shared knowledge packets, never direct vault access. | Approved direction |
| D-020 | Raw design conversations are evidence, not repository documentation; commit curated conclusions only. | Canonical |

## Superseded decisions and names

- **Librarian** is superseded by **Archivist** for the knowledge specialist.
- Early references to Anita and Merry as separate residents or Team members are invalidated by D-007.
- Early standing placement `height: 0.72` at `anchor_y: 1.10` was superseded after the clear-eyed asset changed scale and grounding.
- Early proposed model names were superseded by `gemma4:e2b`.
- Early milestone numbering that placed blinking at 0.4.1 was superseded by the Clear Eyes correction and Build 0.5.0 First Blink.
