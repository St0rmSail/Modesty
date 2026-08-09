# Project Ledger

**Status:** Authoritative index
**Reviewed:** 2026-08-09
**Current build:** 0.12.0 - Library Gateway (complete)

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
