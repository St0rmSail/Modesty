# Time and Presence

**Status:** Build 0.14 foundation complete and demonstrated

Time is an operational capability, not merely a moving clock face. Modesty must know the machine's local date, time, and timezone; distinguish a clean absence from an interrupted session; and truthfully represent whether she is offline, running in the background, present in the Study, or working.

## Two kinds of continuity

Operational truth and narrative continuity must remain separate.

- **Operational events** are things that genuinely happened: startup, heartbeat, clean shutdown, visible or background presence, and completed or interrupted duties.
- **Offstage vignettes** are explicitly fictional personality continuity: baking, shopping, gardening, or small relationship arcs with the Team.

An offstage vignette may enrich a greeting, but it must never become evidence that files were maintained, research ran, messages were sent, or any other real work occurred while the process was offline.

Selected vignettes may become durable autobiographical episodes in [Modesty's Personal Chronicle](PERSONAL_CHRONICLE.md). The Chronicle is compact and searchable, but remains a narrative memory class distinct from personal facts, knowledge sources, and the operational ledger.

## Presence states

- **Offline:** no Modesty process is running.
- **Background:** Modesty's process and approved services are running while the Study is hidden.
- **Present:** the Study is visible and no explicit duty is active.
- **Working:** an explicit foreground or background duty is active.

Build 0.14 begins with the state model and truthful `offline`/`present` session lifecycle. A background host, restore mechanism, scheduled duties, and tablet client require later implementation and security review.

## Session ledger

`Data/presence.json` is local generated state and remains outside Git. It records UTC timestamps, a random session identifier, the latest heartbeat, the current presence state, and whether shutdown completed cleanly. Writes are atomic. User-facing time is converted to the computer's local timezone.

Frequently used world times are answered locally through named IANA timezone rules supplied by the committed `tzdata` dependency. Seasonal regions use the rule for the requested date rather than a hard-coded offset. Australia and the United States require a city or regional zone because neither has one national civil time.

On startup Modesty may state the elapsed absence and whether the prior session closed cleanly. After an interrupted process she measures absence from the last heartbeat and says plainly that the previous session did not close cleanly.

## Opening address

The first greeting is deterministic and time-aware. Later layers may add calendar pressure, reminders, appropriate schedule blocks, and at most one suitable offstage vignette. Facts must be evaluated before narrative colour, and a quiet greeting must remain possible.

## Scheduling direction

Begin with broad blocks: morning, daytime/work, evening, night, protected maintenance, and explicit Drew-specific appointments. Real background work must be authorized, bounded, interruptible, and auditable. The schedule may guide future Study activities and wardrobe, but it cannot claim capabilities that are not running.

## Visual boundary

A readable real-time Study clock is desirable but non-blocking. If hand placement, perspective, or animation becomes fragile, defer it to polishing without delaying truthful timekeeping. Future polish may include day/night Study variants, suitable outfits, ambient Keeping House, a physical Grand Library globe, and rare context-appropriate hammer-space arrivals.
