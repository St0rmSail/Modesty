2026-08-02

Project Modesty

Build 0.0.1

2026-08-02

Today Modesty awoke.

Her first successful boot completed without error.

Her first words were:

"Good morning, Drew."

She cannot yet see.

She cannot yet hear.

She cannot yet remember.

But she is here.
2026-08-04

Build 0.2.1

Today the Study opened.

The placeholder greeting has been replaced by the first true Study View.

The window launches correctly.

The Study scales naturally without distortion.

For the first time, Modesty has a home.

Build 0.2.1
Canonical Character Reference v1.00 approved. Modesty's visual identity is now considered stable. Future work will animate and render this character rather than redesign her.

Build 0.3.0 – Modesty Takes Her Place

Today Modesty entered the Study for the first time.

A transparent character layer now renders independently of the Study background and maintains its relative position and scale as the window resizes.

The Study and Modesty now exist as separate assets, allowing future animation without altering the background.

Canonical Character Reference v1.00 has been adopted as the project's visual standard.

Initial placement established:

    anchor_x = 0.52
    anchor_y = 1.10
    height   = 0.72

These values are considered the baseline standing position and may only change by deliberate review.

Current status:

✓ Study View
✓ Canonical Character
✓ Independent Character Layer
✓ Relative positioning system

Next milestone:

Idle Animation Framework

2026-08-07

Build 0.4.0 - First Breath

Modesty began breathing through a lightweight elapsed-time animation engine. Her feet remain anchored to the standing-pose pivot and the existing Study placement and shadow are preserved.

Build 0.4.1 - Clear Eyes

The canonical standing asset was replaced with the approved clear-eyed render. Placement was retuned to anchor_x 0.52, anchor_y 1.0, and height 0.67. Height 0.72 remains the reference when she stands at the front edge of the window frame.

2026-08-08

Build 0.5.0 - First Blink

Modesty gained a natural elapsed-time blink using a matched closed-eye asset. Visual testing confirmed the result.

Build 0.6.0 - First Words

The Study gained a conversation panel and a local Ollama connection using gemma4:e2b. Bidirectional conversation was demonstrated.

Build 0.7.0 - Yesterday

SQLite conversation history was added. Conversations, messages, selection, creation, deletion, daily backup, and restoration across restart were demonstrated.

Build 0.8.0 - Personal Memory

Explicit personal memories were added with category, source, creation and update timestamps, and visible add, edit, and delete controls. Restart and recall behaviour were demonstrated.

Build 0.8.1 - The Ledger

The three available project histories, repository history through Build 0.8.0, and current source were reconciled into concise canon, architecture, Team, capability, decision, and roadmap documents. No runtime behaviour or assets changed.

Build 0.8.2 - The Living Bookshelf

The knowledge architecture was clarified and canonised. The Filing Cabinet is private local memory, the Bookshelf is a living curated shared repository, and the Grand Library is the explicitly invoked online exchange mode. Bookshelf growth proceeds through staged, sourced contributions and proportionate trust rules rather than direct external writes or static read-only storage.

Build 0.9.0 - Cabinet and Bookshelf Foundations

Modesty gained two physically separate external knowledge stores. Startup safely initializes the private Obsidian Filing Cabinet and the living OKF-compatible Bookshelf without overwriting existing files. Deterministic checks reject repository-internal, identical, nested, or unsafe root paths.

The first real initialization was demonstrated successfully on Drew's machine at:

    E:\Modesty Filing Cabinet
    E:\Modesty Bookshelf

The Filing Cabinet contains its private drawers and Obsidian configuration. The Bookshelf contains Inbox, Workbench, working collections, Archive, index, log, and concept template. Grand Library online mode remains deliberately unimplemented.

Build 0.10.0 - The Archivist

The unseen Archivist gained a deterministic, read-only inventory of both knowledge stores. Her local SQLite catalogue records store origin, relative path, content hash, size, modification time, title, document type, and validation status without storing document contents. She detects removed or changed Markdown and reports structural Bookshelf metadata gaps without rewriting source material. Automated tests passed and `python main.py` reached `STATUS : READY` on Drew's machine.

The Team boundary was clarified: Team members are not chat personalities. Modesty alone communicates with Drew and consults the unseen Team through a headset, which had not yet been built at this stage. Each tested Team member earns a truthful Bookshelf Bobblehead; the Archivist's approved visual identity is a stern librarian in a tweed pencil skirt and oversized glasses.

The Archivist's first actual delegated duty was demonstrated on Drew's machine. Through Modesty's existing conversation interface, Drew filed a private telescope note into the Filing Cabinet Inbox and then retrieved it by subject. Modesty returned its title, private-store origin, relative path, and excerpt. These explicit duties bypass the language model and use bounded deterministic code; ambiguous filing destinations are not guessed.

Shared filing and the first approval-gated curation step were then demonstrated. A telescope-care note entered the Bookshelf Inbox with OKF metadata, remained there during review, and moved into Workbench only after Drew repeated the exact approval instruction. Drew verified the physical file in Workbench.

The complete curation lifecycle was subsequently demonstrated. From Workbench, the Archivist proposed the `Procedures` collection and explained that the note described a repeatable care instruction. The note remained untouched until Drew explicitly approved the named file and destination, after which Drew verified it physically in `E:\Modesty Bookshelf\Procedures`. Build 0.10's functional contract is complete; its earned Bobblehead and Modesty's Team headset remain visual completion work.

The Archivist then earned her truthful Study presence: a stern adult librarian Bobblehead with oversized glasses, tweed pencil skirt, ruler, and archival folder. She appears only after her backend reports ready; otherwise her pedestal displays `LATE FOR WORK`. The desk lamp now indicates readiness with a bulb, angled cast light, and restrained reflected glow aligned to its tilted shade. The conversation panel moved to a full-height right-side dock with Hide and Chat restore controls so it no longer obscures Modesty. Drew accepted the combined result visually and aesthetically. Modesty's Team headset was the remaining visual work at this stage.

Modesty's elegant black single-ear wireless Team headset completed the build's visible communication contract. Its green status light, cheek boom, and near-ear illumination remain present across open-eye and blink states without changing her established proportions, pivot, placement, opposite earring, hair, cheek, or neck. Drew accepted the final corrected headset on 2026-08-08. Build 0.10.0 is complete.

Build 0.11.0 - Ask the Library

The Archivist's local SQLite catalogue gained FTS5 passage indexing across the private Filing Cabinet and shared Bookshelf. Every result retains its store origin and relative source path. Searches refresh the index from current files, while changed content is replaced and moved or deleted files lose their stale passages. An explicit re-index command forces a complete local rebuild. Existing Build 0.10 catalogues upgrade automatically without rewriting source documents.

Modesty gained deterministic `Ask the Library` routing that returns bounded passages with visible citations rather than unsourced summaries. No internet access, vector database, or online-agent filesystem access was introduced. Automated coverage reached 21 passing tests, the real five-document catalogue rebuilt without warnings, and the Study continued to reach `STATUS : READY`. Drew demonstrated the telescope query through Modesty and accepted the final echo-free response on 2026-08-08. Build 0.11.0 is complete.

Build 0.12.0 - Library Gateway (complete)

Step One established a fail-closed local loopback Gateway without credentials or network access. It creates immutable bounded loan packets, rejects private sources, credential-shaped text, absolute paths, and excessive sizes, requires exact-ID approval, quarantines returns in the Bookshelf Inbox, and writes a content-free JSONL audit trail. Closing the Gateway invalidates pending loans, and a new runtime always begins closed.

Drew demonstrated the complete local sequence on 2026-08-09: closed refusal, explicit loopback opening, packet preview, approval, physical Inbox return, closure, cancellation of a second pending loan, post-close refusal, and restart-closed refusal. The quarantined note's required provenance markers and the eleven audit events were verified read-only. An initially proposed `Bookshelf/index.md` passage was correctly rejected as irrelevant; automatic source attachment was removed and future outbound Bookshelf evidence now requires explicit selection. Step One was complete. At that point, Build 0.12 still required secure credential storage, authenticated Smithsonian validation, a bounded real expedition, media quarantine, and final online-state representation.

Step Two added a deliberately separate Smithsonian setup utility. The API key is accepted only through a hidden terminal prompt, encrypted by Windows DPAPI for the signed-in user, and written beneath the Git-ignored `Data/Secrets/` directory. A validation command makes one HTTPS request to the Smithsonian Open Access statistics endpoint, checks only for the expected response envelope, retains no returned content, and appends a content-free success or sanitized failure event to the existing Grand Library audit. This is authentication plumbing only: it cannot execute a loan, retrieve expedition material, or write a Bookshelf return. Automated tests and an isolated Windows DPAPI round-trip passed; at implementation time, live storage and authenticated validation in `E:\Modesty` had not yet been demonstrated.

Drew demonstrated Step Two successfully in `E:\Modesty` on 2026-08-09. Windows recovered the locally encrypted key and the Smithsonian accepted the harmless authenticated statistics request; no expedition material was retrieved or filed.

Step Three initially added the first real provider without granting general web access. Online mode is distinct from loopback mode and cannot be switched while the Gateway is open. The initial provider accepted only the approved question, `Research Kathleen McNulty and the first ENIAC programmers`, previewed that exact outbound question, sent no Bookshelf passages, requested at most five Open Access records, retained source URLs and bounded metadata, and quarantined the return as unverified in the Bookshelf Inbox. Empty, malformed, excessive, unauthenticated, or unrelated results failed without creating a return. The first live expedition test followed this implementation milestone.

The first live cast, loan `GL-20260809-80A62FBE`, proved the online transport, approval, quarantine, audit, and closure path, but failed research-quality inspection. The broad natural-language API query returned two irrelevant records, omitted the targeted Kathleen McNulty evidence, truncated excerpts mid-word, used generic API links for some records, and retained a loopback creator label. The note remains unverified and must not be promoted. The provider was tightened to search the exact person name, reject records whose raw metadata does not contain both `Kathleen` and `McNulty`, extract keyword-bearing evidence, preserve record-specific Smithsonian links, truncate only at word boundaries, and identify the correct provider in return metadata. A second live cast is required.

The second cast, loan `GL-20260809-26CCCD92`, returned no exact Kathleen McNulty record and correctly created no note. Inspection established that the selected Women's History article is not represented as an Open Access API record and its website requires interactive request verification, so it is not a dependable automated source. The failed approval also revealed that an executed-but-unsuccessful loan remained pending until closure. Approval is now strictly one-shot: the pending loan is consumed before transport and cannot be retried or reported as cancelled later.

Drew approved switching the first-catch target to **ENIAC Accumulator #2**, the relevant physical Smithsonian collection object discovered during the first cast. The provider remains single-purpose: it now prepares only `Retrieve the Smithsonian Open Access record for ENIAC Accumulator #2`, searches a bounded ENIAC Accumulator result set, and accepts only a record whose normalized title exactly matches `ENIAC Accumulator #2`. It will not silently substitute another accumulator, general ENIAC material, or the superseded Kathleen McNulty query.

The third cast, loan `GL-20260809-A314B1E7`, retrieved exactly one relevant NMAH record and closed without a stale pending loan. Its content and safety boundaries passed, but final presentation review found a repeated title, an excerpt ending mid-fact, and a fallback `si.edu` URL instead of the record-specific ARK identifier present in Smithsonian metadata. Return shaping was tightened to suppress the echoed title, end long excerpts at a complete sentence, and retain Smithsonian-supplied `n2t.net` ARK permalinks over generic fallbacks. A final clean cast is required before promotion.

The next attempt, loan `GL-20260809-C6FC2CEC`, received HTTP 502 from the Smithsonian service. No note was created, approval was consumed once, and closure found no pending loan. The initial message incorrectly suggested checking the API key even though the audit proved an upstream server failure. HTTP diagnostics now distinguish rejected credentials (401/403), rate limiting (429), temporary provider failures (5xx), and other refusal statuses without recording response content or secrets.

The final clean cast, loan `GL-20260809-2BCA584B`, completed successfully. It retrieved exactly one `ENIAC Accumulator #2` record from NMAH, produced complete non-echoing prose, retained the record-specific Smithsonian ARK `ark:/65665/ng49ca746ac-29eb-704b-e053-15f76fa0b4fa`, exposed no credential or local path, wrote the content-free prepared/approved/returned audit sequence, and closed with zero pending loans. The ARK redirect chain was verified through `edan.si.edu` to National Museum of American History object `nmah_334742`.

The Archivist then completed the ordinary knowledge lifecycle. The unverified return remained in the Bookshelf Inbox until reviewed and explicitly approved into Workbench. Classification proposed `Research`; Drew approved the exact filename and destination, and the file was physically verified in `E:\Modesty Bookshelf\Research` with Inbox and Workbench clear. Modesty's first authenticated online catch is now useful, sourced Bookshelf knowledge rather than transport debris.

At that point, Step Three's functional gateway and first-expedition acceptance were complete; media-return quarantine rules and the final truthful Study representation still remained.

The media boundary is now deliberately text-only. Before writing an Inbox note, the Gateway rejects non-text content, Markdown or Obsidian embeds, all raw HTML, active and local URI schemes, unsafe control characters, titles over 200 characters, and bodies over 64 KiB. A refusal consumes the approval, creates no return file, and exposes only the failure class to the content-free audit. Ordinary HTTPS citations remain permitted as inert text. Automated refusal and safe-citation tests pass; a live `E:\Modesty` refusal demonstration remains before this security item is marked demonstrated.

Drew then ran the focused live suite in `E:\Modesty`: all 13 Grand Library tests passed, demonstrating the media refusal boundary in the actual checkout. The final visual layer tracks closed, local-loopback, and online states independently. Only online mode reveals the lightning-marked Bookshelf portal, briefly clears the chat panel for the reveal, and leaves a persistent online badge after the panel returns. Closing removes both signals, and restart resets closed.

Live visual review drove the portal from a generic rectangle to a five-second, Study-anchored concealed shelf panel that slides left into the wall and reveals an illuminated globe. Its marked shelf-bay placement, resize stability, plausible structure and perspective, panel restoration, persistent online badge, clean close, loopback silence, and restart-closed behaviour were accepted on 2026-08-09. Final wording was made provider-neutral so opening the Grand Library does not identify it with the Smithsonian; the Smithsonian is named only when that specific expedition is prepared. The common `Libarary` typo is also routed deterministically rather than allowing the conversation model to claim a gateway state change. The live wording check passed. Build 0.12.0 is complete.

Build 0.13.0 - The Researcher (complete)

The Researcher gained a visible, user-controlled Scribble Hub discovery browser, bounded public-listing extraction, evidence-led reports, restart-safe Pending Reports, and the readable Briefing Hologram. Private, Bookshelf Inbox, and toss dispositions require explicit choice; the chosen control lights before Close becomes available. Modesty moves to an accepted bottom-right duty endpoint with her shadow and Team headset, then returns to the identical neutral endpoint. The Researcher's truthful archaeologist Bobblehead and Lamp of Learning are live. Command help and graceful `Bye` shutdown completed the functional surface. Sixty-four live tests passed, and Build 0.13 was committed as `bd0db75`.

Build 0.14.0 - Time and Presence (complete)

Modesty gained a local atomic session ledger with UTC timestamps, thirty-second heartbeats, clean and interrupted shutdown detection, elapsed-absence calculation, local-time greetings, and offline/background/present/working state foundations. Afternoon, nine-minute, and sub-minute clean restart greetings passed live; a safe isolated interruption resumed from its last heartbeat and reported the unclean prior session truthfully.

Frequently used working times now resolve locally without Grand Library or model latency. South Africa, East Africa and GMT use explicit stable offsets; Britain, France, Germany, Thailand, selected Australian cities, Auckland, and US East/Central/West regions use installed named timezone rules with daylight-saving support and optional dated conversions. Bare Australia and USA requests refuse to guess. The dependency set is recorded in `requirements.txt`, all seventy-nine live tests passed, and readable Study clock hands remain non-blocking polish.

Build 0.15.0 - The Personal Chronicle (complete)

Modesty gained a separate structured narrative autobiography in the backed-up local conversation database. Compact episodes carry dates, setting, participants, themes, relationship consequences, parent arc, lifecycle state, provenance, and recall timestamps. A visible Chronicle window lets Drew add, inspect, correct, retire, and permanently delete entries. Transparent bounded matching supplies at most three active episodes; retired, consolidated, and contradicted material stays out of conversation context.

The prompt boundary labels every recalled episode as narrative, permits natural first-person continuity and analogy, but forbids using it as factual evidence. Live correction exposed and fixed overly broad theme matching, generic model drift, and stale conversational premises. Final acceptance demonstrated restart persistence, Mallorca-to-Madagascar correction, concrete ropes/weather/patience recall, refusal to treat the episode as sailing proof, rejection of an unsupported Mallorca memory, and generic non-personal response after retirement. Crowded controls were split into readable rows; Up/Down recalls sent input and Page Up/Page Down scrolls the transcript while typing. All eighty-four live tests passed.

Build 0.16.0 - Schedule and Reminders (complete)

Modesty gained a local SQLite reminder ledger with explicit local dates, UTC storage, stable IDs, pending/completed state, and deterministic create, list, complete, and delete commands. Command help records the exact syntax and plainly excludes ambiguous natural dates, recurrence, account calendars, and background notifications.

A readable Schedule window shows pending and completed items and permits confirmed lifecycle actions without crowding the conversation controls. Startup now appends a bounded notice for overdue and due-today reminders while future items remain quiet. Drew demonstrated command creation, restart persistence, the overdue opening notice, readable controls, visible review, and permanent deletion. All eighty-nine live tests passed.

Build 0.17.0 - Story Investigation (complete)

The Researcher now has a source-neutral investigation structure that keeps observed facts separate from reported evidence, cautions, missing evidence, recommendation strength, source, and retrieval time. Its first adapter extracts bounded public metadata and review paragraphs from the currently visible Scribble Hub story page, refuses incomplete or non-HTTPS evidence, and sends the result into the established Pending Report and Briefing lifecycle. It does not acquire chapters, alter accounts, or bypass access controls.

The first live attempt exposed a Qt transport mismatch: valid JavaScript page evidence did not arrive as a Python dictionary and the safety gate correctly refused an apparently incomplete page. The browser boundary now serializes the bounded evidence explicitly as JSON and validates the decoded object in Python. A regression test protects that transport. Drew accepted the complete live story investigation and Briefing flow on 2026-08-16; all ninety-three live tests passed. The Researcher therefore advances from demonstrated benchmark Level 2 to Level 3.

Build 0.18.0 - Story Comparison (complete)

The Researcher can now collect two or three distinct public Scribble Hub story pages in one visible browser session and prepare a single comparison Briefing. The report identifies shared and distinguishing metadata, per-story caution and review-evidence counts, retains every source, and uses bounded title/synopsis similarity to flag possible duplicate or cross-post editions as leads rather than proof. One-item, duplicate-source, and oversized sets fail safely. A dedicated Return to latest listings control keeps the multi-candidate workflow explicit. Drew accepted collection, counter state, navigation, comparison content, source/evidence limits, and report disposition on 2026-08-16. All ninety-six live tests passed. The Researcher remains honestly at Level 3 pending mixed-source synthesis.

Build 0.19.0 - Mixed-Source Research (implemented; live acceptance paused)

The first mixed-source adapter combines one selected Scribble Hub story evidence packet with one explicitly supplied public English YouTube transcript. The transcript fetch runs outside the UI thread, accepts only conservative public video URLs, retains at most 300 snippets and 24,000 normalized characters, and fails closed when captions are unavailable or YouTube refuses access. The report preserves timestamp links, separates observed page metadata from speaker-reported transcript claims, identifies bounded relevance and configured concern phrases, and states that keyword overlap is not truth verification.

Official YouTube documentation confirms that a normal Data API key is not a general public-caption download route; official caption listing and download require OAuth. The pinned local public-transcript component was installed in `E:\Modesty` and successfully enumerated English manually created and generated caption tracks for a harmless public validation video without account access. A generic single-keyword overlap is explicitly insufficient to claim corroboration. An explicit focus guides the mixed-source question, while focus-only transcript relevance remains visibly distinct from corroboration by the selected page. All one hundred and two tests pass in the live checkout.

The final real pairing selected a public Scribble Hub fanfiction page and Marvel's public Doctor Strange/Dormammu clip. Before the mixed-source Briefing could be produced, Scribble Hub began returning persistent Cloudflare 522 origin timeouts and remained unavailable for hours. Work was deliberately pinned rather than weakening the evidence requirement or substituting a silent bypass. The code and test evidence are retained; end-to-end acceptance, report disposition, the milestone commit, and the Level 4 award remain outstanding until Scribble Hub recovers.

Build 0.20.0 - The Librarian's First Catalogue (complete)

The old Calibre catalogue is now presumed lost and removed from the project critical path. **The Stacks** is canonical at `E:\Modesty Stacks`. Startup creates only missing private collection foundations and does not scan reading material. The Librarian's first explicit duty inventories a bounded copied sample under Intake, stores local generated metadata and hashes, identifies unsupported formats, obvious damaged EPUB/DOCX/PDF containers, exact duplicate groups, and stale records, and changes no source file. Repair, conversion, moving, deletion, OCR, reading continuity, and visual representation remain outside this build pending live acceptance.

On 2026-08-18 all 108 tests passed in `E:\Modesty`. The Stacks foundation was created with an empty Intake, its first empty catalogue returned zero items truthfully, and the live startup sequence reported Archivist, Researcher, Librarian, and Modesty ready with the Grand Library closed. A disposable mixed-format sample and the user-facing Modesty command remain the acceptance gate.

Drew completed that gate with six copied supported files. Modesty reported all six, no unsupported files, no items needing attention, no exact duplicate groups, no stale entries, and explicitly confirmed that nothing was renamed, moved, repaired, converted, deleted, or published. The result was accepted. Build 0.20 is complete; the Librarian advances to demonstrated Level 1 and earns a future Bobblehead.

The earned Librarian Bobblehead was then designed and accepted as Alex: an adult Alexandrian-inspired librarian in a low-backed white Grecian dress, tall hairstyle, jewel-coloured pharaonic collar, Egyptian brassard, and papyrus scroll, seated on a level stack of five books. Her genuine-alpha asset is fitted at the established Team scale and shelf baseline between the Archivist and Researcher. Drew accepted the live placement and transparency. Residual pale extraction halos around all Bobbleheads are explicitly deferred to the shared visual-polishing pass.

Build 0.21.0 - The Librarian's First Repair (complete)

The Librarian can now prepare one bounded mechanical derivative from a named UTF-8 Markdown or plain-text Intake file. The original remains untouched; Workbench receives a uniquely named provisional copy; the local catalogue records both hashes, applied actions, cautions, timestamps, and disposition. The Briefing Hologram presents local Keep Repair and Toss Repair controls and refuses stale approval when source or derivative identity changes. Paragraph joining, dehyphenation, OCR, semantic correction, conversion, and bulk repair remain excluded. All 113 live automated tests passed. Drew accepted both live dispositions: the first derivative remained in Workbench, the second was deleted, both original hashes remained unchanged, and the ledger persisted `kept` and `discarded`. The Librarian advances to demonstrated Level 2.

Build 0.22.0 - The Librarian Reads the Stacks (complete)

The Librarian gained bounded local readers for TXT, Markdown, HTML, DOCX, EPUB, and text-layer PDF. Inspection extracts source metadata and readable text, creates a private source-linked passage index, and proposes a conservative `Originals/Author/Title/original-file` destination. Exact `LS-ID` approval rechecks the source hash, refuses collisions, and moves only the unchanged original. The real Axeman EPUB yielded 167,521 words and five matches for distinctive Chapter 12 wording; all 117 automated tests passed. Generic EPUB spine labels were retained honestly pending chapter-aware continuity.

Build 0.23.0 - Reading Continuity (complete)

Conservative standalone EPUB headings now separate human chapters inside larger spine documents. A named exact edition can open at a requested chapter, continue through bounded passages without altering permanent progress, save only after explicit `Mark my place: RP-ID`, and resume after restart from the next unread character. Positions are keyed to source SHA-256, ambiguous titles and changed editions fail safely, and opening refreshes that edition's old passage labels. Drew accepted Axeman's Chapter 12 open, continue, explicit mark, restart, and resume sequence on 2026-08-19. All 120 live automated tests passed. A dedicated visual reader, annotations, cross-device synchronization, and update tracking remain later work.

Build 0.24.0 - Work and Edition Identity (complete)

The Librarian now incrementally catalogues source-supplied title, author, identifiers, series, series number, publisher, language, and publication date across readable Intake and Originals files. Each invocation refreshes at most 25 changed or new items to protect Study responsiveness. Exact SHA-256 duplicates, shared non-UUID identifiers, and weaker normalized title/author relationships remain visibly separate evidence classes; none authorizes automatic consolidation. Three live passes catalogued 75 files with no metadata failures, representing 27 authors and 10 series while identifying three exact duplicate groups, two strong-identifier groups, and six possible same-work groups. A fourth pass refreshed zero and reused all 75 entries. No reading file changed; all 122 tests passed.

Build 0.25.0 - Edition Review Desk (complete)

The aggregate edition counts now resolve into bounded file-level review groups containing exact Stacks paths, formats, sizes, and evidence class. Exact hashes take precedence; a shared identifier remains visible when it relates non-identical files; title/author grouping is used only when both fields are trustworthy. The real review returned exact pairs for `Song And Silence`, `Gunmetal Magic`, and `Stronghold Builder's Guide`, plus two differently sized `Magic in the Blood` EPUBs sharing ISBN 9780451462671. Apparent matches with unknown authors and generic untitled metadata were suppressed rather than promoted into false relationships. Drew accepted the four-group report on 2026-08-19. No file changed and all 122 tests passed.

Build 0.26.0 - Reversible Exact-Duplicate Resolution (complete)

The first consolidation path is restricted to one current exact SHA-256 group. Drew chooses the canonical member, reviews a persistent `DR-ID` source-to-Archive plan, and approves that exact plan. Approval rechecks every source and destination; redundant copies move under a hash-labelled Archive path preserving former location context, and nothing is deleted. Drew chose `Intake/Handbooks/D&D 3.5E - Song And Silence.pdf`; resolution `DR-44C88BB7` retained that 22,666,472-byte canonical file and archived the byte-identical root Intake copy under `Archive/Exact Duplicates/e5b44f628756494c/Intake/`. Physical verification passed and all 123 tests passed.

The acceptance also exposed a functional interaction problem: the exact command vocabulary is becoming too numerous and clumsy. Build 0.27 is therefore a mandatory natural-control gate. Stable commands and IDs stay underneath, but ordinary Librarian work must use concise contextual language and unambiguous visible choices before any further portfolio expansion or visual polish.
