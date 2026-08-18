# Decision Log

**Reviewed:** 2026-08-16

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
| D-015 | The Filing Cabinet is Modesty's locked, local-only personal memory and private Obsidian vault. | Canonical |
| D-016 | The Bookshelf is a separate, living local repository of curated shared knowledge and resources; it contains more than books. | Canonical |
| D-017 | The Grand Library is an explicitly invoked online exchange mode, not a storage directory. | Canonical |
| D-018 | Adopt OKF-compatible Markdown primarily for the Bookshelf; OKF does not enforce permissions. | Canonical |
| D-019 | Modesty fronts knowledge interactions; the Archivist maintains both stores and curates Bookshelf growth. | Canonical boundary |
| D-020 | Raw design conversations are evidence, not repository documentation; commit curated conclusions only. | Canonical |
| D-021 | Online agents borrow bounded read-only Bookshelf packets and return sourced contributions to Inbox; they never receive direct local access or silently rewrite established knowledge. | Canonical |
| D-022 | Bookshelf changes use Routine, Normal, Important, and Protected trust levels; only Drew may approve movement from Filing Cabinet to Bookshelf. | Canonical |
| D-023 | Team members are unseen functional specialists, never chat personalities. Modesty alone speaks to Drew, consults them through a headset, and their tested state is represented by individual Bookshelf Bobbleheads. | Canonical |
| D-024 | Every specialist must clean up its own operational debris under explicit retention rules; the Archivist governs knowledge hygiene, and a separate Housekeeper is deferred until cross-specialist maintenance becomes a distinct recurring capability. | Canonical |
| D-025 | Modesty's eventual voice must be local and original; `af_nicole` leads a deferred long-term audition, but no voice is selected or implemented until Drew explicitly approves it after repeated listening. | Canonical direction |
| D-026 | A Researcher duty returns a coherent, sourced assessment through Modesty before optional Archivist preservation; a file location alone is not a useful report. | Canonical |
| D-027 | Scribble Hub discovery uses a visible user-controlled browser and public metadata; Modesty will not bypass access controls or infer permission to mirror story text, alter an account, or message anyone. | Canonical boundary |
| D-028 | WhatsApp belongs to a future Communications specialist; it may carry research results but does not absorb the Researcher's remit. | Canonical boundary |
| D-029 | The Briefing Hologram is the approved substantial-output surface; Modesty gives a concise Return while the interactive Briefing holds detail and may become a durable Report. | Canonical |
| D-030 | Completed Briefings remain recoverable Pending Reports until Drew explicitly keeps them privately, sends them to Bookshelf Inbox, or tosses them. | Canonical |
| D-031 | The Librarian is a new Team member distinct from the Archivist, responsible for private reading works, editions, repairs, cross-post continuity, and reading position. | Canonical |
| D-032 | Librarian repairs preserve untouched originals and provenance; uncertain or meaning-changing corrections require review, and neither DRM circumvention nor silent redistribution is permitted. | Canonical boundary |
| D-033 | A build that adds or changes a deterministic user command is incomplete until Modesty's local command guide, tolerant help routing, and help-routing tests are updated with it. | Canonical process rule |
| D-034 | Command-driven movement follows neutral pose, motivated outward transition, definitive duty pose, and a motivated return to the identical neutral endpoint. Outbound and return paths may differ; reversibility governs state and endpoints rather than mechanical retracing. Duty geometry never mutates the accepted standing baseline. | Canonical animation rule |
| D-035 | The Researcher Bobblehead's current pillar-side placement is accepted; its apparently forward-tipped pedestal is a deferred perspective-polish item, not a blocker or reason to alter the approved figurine. | Accepted with polishing note |
| D-036 | Bobbleheads and the readiness lamp mean Team members are present; the headset means active Team communication. Modesty wears it only during a working or waiting Team duty and while presenting that duty's Briefing. | Canonical visual-state rule |
| D-037 | An active Briefing cannot close while its report is undecided. A successful private, Bookshelf, or toss disposition visibly highlights the chosen control, locks the alternatives, and enables Close. | Canonical interaction rule |
| D-038 | `Bye` and `Goodbye, Modesty` are deterministic graceful-exit commands: Modesty acknowledges Drew, then the Study follows its normal application shutdown path. | Canonical command |
| D-039 | Time and presence use a persistent operational ledger with local-time presentation, UTC storage, heartbeats, clean/interrupted shutdown detection, and explicit offline/background/present/working states. | Canonical architecture |
| D-040 | Offstage vignettes are narrative continuity, never operational evidence. They may enrich greetings but cannot claim real research, maintenance, messaging, or other work while Modesty was offline. | Canonical truth boundary |
| D-041 | A readable real-time Study clock is desirable but cannot block Time and Presence; fragile clock-face animation is deferred to polishing. | Canonical priority |
| D-042 | Modesty's durable fictional autobiography belongs in a separately labelled Personal Chronicle. It may provide analogy and continuity but never factual evidence; compact episode records consolidate into bounded arcs to prevent memory bloat. | Canonical memory boundary |
| D-043 | Regular working-zone answers and dated conversions are deterministic local functions requiring neither Grand Library nor language model. Fixed African/GMT zones use explicit offsets; Britain, Europe, Thailand, Australia, New Zealand, and US regions use installed named timezone rules, with ambiguous countries requiring a city or region. | Canonical capability |
| D-044 | Every milestone commit is a restore point and requires a repository-wide reconciliation of status documents, commands, tests, configuration, assets, and live behavior before commit. Stale paperwork is a completion defect. | Canonical process rule |
| D-045 | The Personal Chronicle is authoritative for Modesty's narrative autobiography. Relevant recall must use concrete recorded details; generic model invention, stale conversational wording, and user premises cannot silently create or replace an episode. | Canonical narrative-integrity rule |
| D-046 | The first schedule is local and deterministic: explicit local dates and times become UTC-backed reminders with stable IDs. Due time creates a notice, never a claim that work occurred; accounts, recurrence, natural-language dates, and background delivery require later controlled builds. | Canonical schedule boundary |
| D-047 | Research investigations use a source-neutral evidence contract that separates observed facts, reported evidence, cautions, missing evidence, recommendation strength, source, and retrieval time. The first Scribble Hub adapter reads only the current visible public story page; account actions and chapter acquisition require separate authority and design. | Canonical research boundary |
| D-048 | Every Team specialist uses the common capability benchmark: demonstrated live level, implemented-but-unaccepted level, world comparison, exact active-build increment, remaining gap, and proof required. Code or a mock cannot advance the demonstrated level. | Canonical measurement rule |
| D-049 | Same-type comparison strengthens evidence-led investigation but does not earn multi-source-synthesis Level 4. Level 4 requires successful synthesis across distinctly different source types with claim-linked provenance and conflict handling. | Canonical benchmark boundary |
| D-050 | First YouTube research uses bounded public English captions exposed to the ordinary web client, with no login, cookies, API key, proxies, or bypass. Official Data API metadata remains separate; official caption endpoints require OAuth. Transcript statements are speaker claims and retain timestamp provenance. | Canonical research boundary |
| D-051 | An external source outage pauses, but does not fail, an acceptance run. Implemented and automated-test status remain distinct from demonstrated capability; Build 0.19 and the Level 4 award stay open until the real mixed-source Briefing passes after Scribble Hub recovers. | Canonical verification rule |
| D-052 | **The Stacks** is the canonical private reading collection at `E:\Modesty Stacks`. Its first duty inventories only copied Intake material and may not alter a reading file. | Canonical Librarian foundation |
| D-053 | The old Calibre library is presumed lost and imposes no recovery, migration, schema, authority, or implementation constraint. Any fragment rediscovered later is optional Intake material like any other source. | Canonical scope correction |

## Superseded decisions and names

- **Librarian** remains superseded by **Archivist** as the old name for the knowledge specialist. The newly approved Librarian is a separate reading specialist defined after that terminology change.
- Early references to Anita and Merry as separate residents or Team members are invalidated by D-007.
- Early standing placement `height: 0.72` at `anchor_y: 1.10` was superseded after the clear-eyed asset changed scale and grounding.
- Early proposed model names were superseded by `gemma4:e2b`.
- Early milestone numbering that placed blinking at 0.4.1 was superseded by the Clear Eyes correction and Build 0.5.0 First Blink.
- The earlier design placing Private and Shared roots inside the Grand Library was superseded: Filing Cabinet and Bookshelf are stores; Grand Library is the online mode connecting the Bookshelf outward.
