# Project Ledger

**Status:** Authoritative index
**Reviewed:** 2026-08-21
**Current build:** 0.32.0 - Passage Bookmarks and Notes (complete); 0.19 acceptance paused

The Ledger keeps design, software, and status aligned. It records conclusions rather than raw conversation. If a document disagrees with running code, the disagreement must be investigated; a planned folder or enthusiastic discussion is not proof of implementation.

## Authority order

1. Drew's latest explicit decision.
2. Verified behaviour and current code on `main`.
3. Canon and decision records in this directory.
4. Older plans and conversation proposals.

## Status vocabulary

- **Canonical:** explicitly approved and currently authoritative.
- **Implemented:** present in current code.
- **Tested:** observed working in the recorded build cycle.
- **Proposed:** discussed but not approved or built.
- **Unresolved:** a decision is still required.
- **Superseded:** retained for history but no longer authoritative.

## Authoritative documents

- [Canon](CANON.md): what Modesty and the Study are.
- [Architecture](ARCHITECTURE.md): concepts mapped to software.
- [The Team](TEAM.md): roles, boundaries, and implementation status.
- [Capability Matrix](CAPABILITY_MATRIX.md): honest build inventory and gaps.
- [Decision Log](DECISION_LOG.md): settled project-wide decisions.
- [Roadmap](ROADMAP.md): ordered next work and definitions of done.
- [Personality Canon](MODESTY_PERSONALITY_CANON.md): the Anita/Merry identity rule.
- [Build Log](Buildlog.md): chronological milestone record.
- [Voice](VOICE.md): local voice direction, current audition findings, and selection gate.
- [Researcher](RESEARCHER.md): report contract, first Scribble Hub assignment, and browser/rights boundary.
- [Librarian](LIBRARIAN.md): private reading collection, editions, repairs, provenance, and continuity.
- [Briefing Hologram](BRIEFING_HOLOGRAM.md): substantial-output presentation and Pending Report lifecycle.
- [Command Help](COMMANDS.md): authoritative user-facing deterministic command reference.
- [Time and Presence](TIME_AND_PRESENCE.md): session truth, presence states, greeting, scheduling direction, and narrative boundary.
- [Personal Chronicle](PERSONAL_CHRONICLE.md): compact persistent fictional autobiography and its evidence boundary.
- [Schedule and Reminders](SCHEDULE_AND_REMINDERS.md): persistent local reminders, due context, commands, and future calendar boundary.
- [Agent Capability Benchmark](AGENT_CAPABILITY_BENCHMARK.md): common maturity scale, world comparison, and active-build increment for each specialist.
- [YouTube Research Boundary](YOUTUBE_RESEARCH.md): public-transcript access route, limits, provenance, and first mixed-source duty.

## Evidence reviewed for Build 0.8.1

The Ledger was reconciled against:

- the complete ChatGPT conversation **Modesty Design Bible - v0.2 The Awakening**;
- the complete ChatGPT conversation **Theorycrafting Modlist Visuals**;
- the complete Codex task **Implement Build 0.4.0 breathing**, including the subsequent work through Build 0.8.0;
- repository history through commit `9c5e308` (Build 0.8.0);
- current source, configuration, and assets on `main`.

Raw transcripts are deliberately not committed. They contain brainstorming, reversals, failed attempts, and potentially personal material. Only curated outcomes belong in this public repository.

## Maintenance rule

A milestone is not complete until:

1. the code runs;
2. the requested behaviour has been demonstrated;
3. its Study representation exists when applicable;
4. the capability matrix, roadmap, decision log, and build log are updated where affected.
5. every new or changed deterministic user command is present in `COMMANDS.md`, reachable through Modesty's help routing in natural language, and protected by a help-routing test.
6. the restore-point audit reconciles README, Project Ledger, Punch List, Roadmap, Architecture, Capability Matrix, Decision Log, Build Log, command help, tests, configuration, and relevant assets against the live checkout.
7. every active specialist records its demonstrated level, implemented level, world comparison, exact build increment, and proof required in `AGENT_CAPABILITY_BENCHMARK.md`.

The restore-point audit happens before the milestone commit. Stale status markers are defects, even when the code itself works.
