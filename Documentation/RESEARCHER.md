# The Researcher

**Status:** Build 0.18 story comparison complete

**Capability benchmark:** Level 3 demonstrated. Build 0.17 bridged bounded discovery to one evidence-led story investigation. See [AGENT_CAPABILITY_BENCHMARK.md](AGENT_CAPABILITY_BENCHMARK.md).

Build 0.18 strengthens Level 3 without claiming Level 4. The visible Researcher browser retains two or three distinct story-page evidence packets, then produces one comparison Briefing. Shared genres and tags, distinguishing signals, caution differences, direct sources, and likely duplicate/cross-post leads are made explicit. Because every page is still the same source type, this is comparison preparation rather than independent multi-source corroboration. The complete live lifecycle passed on 2026-08-16.

The Researcher is an unseen Team specialist. She gathers and evaluates evidence; she is not a second chat personality. Modesty frames the assignment, obtains required consent, and returns the result to Drew in her own voice. The Archivist preserves an accepted result only after the ordinary Inbox and Workbench checks.

## A useful return

A completed research duty must give Drew:

1. a direct answer to the question;
2. a bounded shortlist rather than an unfiltered dump;
3. the evidence for each assessment;
4. warnings, conflicts, uncertainty, and missing evidence;
5. source links and retrieval time; and
6. a clear statement of anything changed, downloaded, or filed.

“A result was placed on a shelf” is not a research report.

Modesty gives the concise Return in conversation. Substantial findings appear in the Briefing Hologram. The resulting Pending Report is preserved or discarded only after Drew's explicit choice; see [BRIEFING_HOLOGRAM.md](BRIEFING_HOLOGRAM.md).

## First source: Scribble Hub

The first approved question is **What are the latest offerings in the harem category?** The reproducible discovery query uses Scribble Hub's Series Finder, Harem genre, Date Added sort, descending order:

`https://www.scribblehub.com/series-finder/?sf=1&gi=1015&mgi=or&sort=dateadded&order=desc`

The first pass may collect public discovery metadata only: title, author, source URL, synopsis, genres, tags, content warnings, chapter count, visible reception signals, and update state. Modesty must distinguish discovery candidates from recommendations. Hidden tonal turns cannot be ruled out from a listing; a recommendation requires an individual evidence pass.

Build 0.17 adds that individual evidence pass for the currently visible Scribble Hub story page. **Investigate current story page** creates a Pending Report that separates:

1. observed public page facts, including synopsis, genres, tags, and visible statistics;
2. reported reader evidence, quoted only from bounded visible review paragraphs;
3. caution signals and missing evidence;
4. a deliberately limited recommendation strength; and
5. source URL and retrieval time.

Reviewer identities and account metadata are not collected. If a page does not expose enough public evidence, the Researcher refuses to manufacture an investigation. A visible page can reveal warning signs, but it cannot prove that a long story contains no hidden tonal turn or establish a personal match without approved preference evidence.

For a comparison, Drew opens each candidate page and selects **Add current story to comparison**. After two or three distinct pages have been added, **Prepare comparison briefing** creates one Pending Report. The comparison set exists only in that Researcher window until the report is created.

Scribble Hub currently challenges ordinary automated HTTP access. Modesty must not bypass that protection. Live intake will use a visible, user-controlled local browser session. Account changes, reading-list changes, messages, ratings, follows, and downloads require their own explicit authority.

## Story text and reading continuity

Discovery metadata is not permission to mirror a story. Full chapter acquisition is deferred until the source's supported access and the author's rights permit it. Reading position and new-chapter tracking should store identifiers, URLs, timestamps, and progress—not unauthorized duplicate story text. Authenticated reading-list feeds are a promising later update mechanism but are not part of this foundation.

## Team boundaries

- **Researcher:** discovery, investigation, comparison, evidence, and report.
- **Modesty:** intent, consent, orchestration, and the spoken/written return to Drew.
- **Archivist:** provenance, quarantine, classification, curation, and later recall.
- **Future Communications specialist:** WhatsApp and other messaging surfaces. It may deliver a Researcher report but does not perform the research.
- **Librarian:** receives accepted story discoveries for edition management, cross-post reconciliation, repairs, and reading continuity.

## Implemented foundation

- `Brain/Team/researcher.py` defines the evidence-led assessment and report contract.
- `Brain/Team/investigation.py` defines the reusable source-neutral investigation structure.
- `Runtime/Research/scribblehub.py` defines the exact first query and a bounded public-listing parser.
- `Runtime/Research/browser_window.py` performs bounded extraction from the user-visible current story page.
- Tests ensure empty evidence cannot become a fake report and every candidate retains a source.

The visible local browser handoff, bounded listing extraction, Pending Report creation, concise conversational Return, and Briefing Hologram handoff were demonstrated in `E:\Modesty`. The Researcher earned an approved adult archaeologist Bobblehead with expedition gear, research notebook, coiled rope, and a lit Lamp of Learning. Her runtime presence reflects real Researcher readiness and duty state.

The Bobblehead's current placement beside the pillar and beneath the desk lamp is accepted for this build. Its pedestal can appear slightly tipped forward because the source artwork's viewing angle is higher than the Study shelf's perspective. This is a polishing item only: revisit the pedestal perspective and shelf contact later without changing the approved figurine, Lamp of Learning, or present placement unless visual comparison justifies it.
