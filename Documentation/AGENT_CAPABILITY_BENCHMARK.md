# Agent Capability Benchmark

**Status:** Canonical comparative framework
**Reviewed:** 2026-08-19

This benchmark keeps every Team specialist honest about three different things:

1. **Demonstrated level** — what has passed in the live `E:\Modesty` checkout.
2. **Implemented level** — what exists in code but still needs live acceptance.
3. **Build increment** — the exact capability gap the active build is meant to close.

It is a functional maturity scale, not a claim about personality, intelligence, model size, or visual polish. A narrow specialist can be excellent at one duty without being a general autonomous agent.

## Common maturity scale

| Level | Name | Observable meaning |
|---:|---|---|
| 0 | Representation | A role, placeholder, or visual identity exists, but no executable duty does. |
| 1 | Callable duty | Modesty can invoke one deterministic bounded operation and report success or failure truthfully. |
| 2 | Bounded retrieval | The specialist can acquire or retrieve limited material with source identity, explicit boundaries, and safe failure. |
| 3 | Evidence-led investigation | It can evaluate a specific subject, separate fact from report or inference, expose uncertainty, and return a coherent sourced Briefing. |
| 4 | Multi-source synthesis | It can plan and compare several appropriate sources, resolve conflicts, cite claims, and produce a useful consolidated report. |
| 5 | Bounded autonomous project | It can execute a multi-step assignment over time with budgets, checkpoints, interruption, recovery, audit, and approval gates. |
| 6 | Mature adaptive specialist | It selects and evaluates tools and sources robustly across varied real work, measures quality, learns from corrections safely, and remains governable. |

Levels are cumulative. A specialist cannot honestly claim a higher level while provenance, uncertainty, recovery, or user control from a lower level is missing.

## Researcher — current world position

**Demonstrated:** Level 3 — one evidence-led investigation of the current visible public Scribble Hub story page, accepted live on 2026-08-16.

**Other implemented capability awaiting acceptance:** None beyond the Build 0.19 candidate recorded below.

**Build 0.18 increment achieved:** same-type corroboration within Level 3. Two or three public Scribble Hub story pages retain individual sources, expose agreements and differences, and identify duplicate/cross-post leads. This prepares but does not satisfy Level 4 because the evidence is not independently corroborated across different source types.

**Implemented, acceptance paused:** Build 0.19's Level 4 attempt combines observed Scribble Hub page evidence with timestamped speaker-reported YouTube transcript evidence. All 102 live automated tests pass, but the real report could not complete while Scribble Hub returned persistent Cloudflare 522 origin timeouts. The report must still demonstrate meaningful overlap or conflict handling, claim-linked provenance, and honest missing corroboration before Level 4 is awarded.

**Build 0.17 increment achieved:** bridged Level 2 to Level 3 by turning one discovered candidate into a structured investigation with observed facts, bounded reader reports, cautions, missing evidence, recommendation strength, source, retrieval time, and explicit report disposition.

**Not yet demonstrated or present:** live cross-source synthesis and conflict handling are not yet demonstrated; source planning, preference modelling, general website adapters, long-running research plans, automatic recovery, and measured report quality are not present. YouTube transcript evidence and claim-linked timestamp provenance are implemented but remain inside the paused Level 4 acceptance gate.

Against the wider field, strong locally hosted research-agent systems commonly reach Level 4 when carefully assembled with capable models, browser/search tools, document processing, citation pipelines, and substantial hardware. Experimental or heavily engineered systems may approach Level 5 on constrained tasks. Hosted frontier research products can reach Levels 5–6 more often because they combine stronger models, large tool infrastructure, and managed compute. Modesty is therefore behind the world leaders in breadth and autonomy, but ahead of a raw local chatbot in safety boundaries, truthful state, explicit evidence separation, and user-governed retention.

This comparison is architectural and deliberately approximate. “Locally hosted research agent” has no single audited world league table, hardware varies dramatically, and polished demonstrations do not prove dependable daily operation.

## Librarian — current world position

**Demonstrated:** Level 2 — on 2026-08-18 Modesty invoked the Librarian's bounded Intake catalogue and then completed one reversible source-identified text repair through both local Keep and Toss decisions without changing either original.

**Implemented beyond the demonstrated level:** None. Build 0.26 is accepted within Level 2.

**Build 0.20 increment achieved:** bridged Level 0 to Level 1 by proving that Modesty can invoke the Librarian, catalogue copied samples, report supported and unsupported formats, obvious container damage, exact duplicates, and stale records, and leave every source byte untouched.

**Build 0.21 increment achieved:** bridged Level 1 to Level 2 with one source-identified, size-bounded, reversible UTF-8 text repair. Live proof covered original preservation, a separate Workbench derivative, transformation provenance, stale-hash refusal in tests, and both explicit dispositions.

**Build 0.22 increment achieved:** strengthened Level 2 by making a named work genuinely readable and searchable, proposing a conservative Author/Title home, and retaining exact approval for shelving. Live proof read 167,521 words from `Axeman` and retrieved five indexed passages for distinctive Chapter 12 wording. This is not yet mature edition management: embedded title and author are accepted as source metadata, unknown values remain explicit, and no duplicate merge or semantic inference occurs.

**Build 0.23 increment achieved:** closed the immediate continuity gap by recognizing source-supplied chapter headings, displaying bounded passages, advancing only within a temporary reading session, and persisting the next unread position only after explicit confirmation for the exact source hash. Axeman's Chapter 12 open, continue, mark, restart, and resume sequence passed live with 120 automated tests.

**Build 0.24 increment achieved:** distinguished exact duplicate bytes, shared publication identifiers, and weaker title/author relationships before scaling shelving or consolidation. The real catalogue completed 75 files across three bounded refreshes, then reused all 75 unchanged entries. It found 27 authors, 10 series, three exact duplicate groups, two strong-identifier groups, and six possible same-work groups without altering source files.

**Build 0.25 increment achieved:** turned aggregate relationship counts into four reviewable file-level groups while suppressing generic-metadata false matches and retaining a strict no-mutation boundary. Live evidence showed three exact duplicate pairs and one differing pair sharing an ISBN; no weak group was manufactured where author metadata was unknown.

**Build 0.26 increment achieved:** Drew selected the canonical Handbooks member of a proven exact-hash group and approved `DR-44C88BB7`; the redundant `Song And Silence` copy was retained reversibly in Archive, nothing was deleted, and authority did not extend to non-identical editions.

**Next increment:** Build 0.27 replaces mandatory command memorization with a bounded contextual Librarian dialogue while retaining deterministic IDs and exact operations underneath. Usability is now a capability gate.

**Not yet present:** preferred decisions between non-identical editions, rich bookmarks and annotations, series normalization, PDF/EPUB repair or conversion, OCR, MOBI/AZW3/RTF/legacy-DOC readers, update tracking, device synchronization, Calibre migration, and autonomous collection governance. The lost Calibre library is not a prerequisite; `Calibre migration` here means only optional handling if compatible fragments are ever rediscovered.

Capable contemporary local library systems such as Calibre already provide mature metadata editing, conversion, device support, and large-catalogue management. Document-management and ebook-repair toolchains can add OCR and validation. Modesty's Librarian is therefore far behind established library software in breadth. Her intended advantage is not replacing those tools prematurely: it is a governable assistant layer that preserves originals, joins provenance and reading continuity across formats, and presents uncertain changes for approval.

**Proof accepted for Build 0.21:** all 113 automated tests, coherent local Briefings, pre/post original hashes, a verified kept Workbench derivative, a verified tossed derivative, and persistent `kept` and `discarded` ledger states.

## Required specialist entry

Every implemented Team specialist must keep a short entry containing:

- demonstrated level and the live evidence for it;
- implemented-but-unaccepted level, if different;
- active build increment;
- important missing abilities before the next level;
- a plain comparison with capable contemporary local systems;
- the tests and real duty that will prove the increment.

Update the entry when a build begins, after live acceptance, and during every restore-point audit. Never advance a demonstrated level because code exists or a mock passed.

## Current Team snapshot

| Specialist | Demonstrated | Current increment |
|---|---:|---|
| Archivist | Level 3 | No active build; local filing, retrieval, classification, and approval-gated curation are demonstrated, but broad autonomous collection governance is not. |
| Researcher | Level 3 | Build 0.19 mixed Scribble Hub/YouTube synthesis is implemented and tested; Level 4 remains pending the postponed live report after Scribble Hub recovers. |
| Librarian | Level 2 | Build 0.26 reversible exact-duplicate resolution is accepted; Build 0.27 must make the control surface natural before capability expands. |

Future specialists enter this table when their role becomes canonical and receive a detailed section when implementation begins.
