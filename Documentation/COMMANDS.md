# Modesty Command Help

**Status:** Authoritative user command reference

Ask Modesty **Help** or **What commands can I use?** for the short index. Ask **Help with the Grand Library**, **Help with the Researcher**, **Help with the Archivist**, **Help with Briefings**, **Help with chat**, or **Help with time zones** for exact instructions. After the index is open, a natural follow-up such as **the Grand Library please** also works.

## Grand Library

- `Open the Grand Library` — opens local loopback test mode. The internet remains disconnected.
- `Open the Grand Library online` — opens bounded online access. Opening it sends nothing by itself.
- `Close the Grand Library` — closes either mode and cancels pending gateway loans.
- `Prepare a Grand Library loopback: <question>` — previews a local-only test loan.
- `Approve Grand Library loan: <loan identifier>` — approves only the exact previewed loan.

The local and online opening commands are intentionally different. Close the Grand Library before changing modes.

## Researcher

The first implemented duty is:

- `Ask the Researcher: What are the latest offerings in the harem category?`

Open the Grand Library online first. The duty opens a visible local Scribble Hub browser. When listings are visible, use **Prepare Briefing from visible listings**. No account action or filing occurs merely because the page opened.

## Briefings

- **Briefing** reopens the latest undecided Pending Report.
- **Keep Privately** sends the report to the Filing Cabinet Inbox through the Archivist.
- **Bookshelf Inbox** sends it to shared intake for later curation.
- **Toss** deletes the Pending Report content without filing it.
- **Close** remains unavailable until one of those three dispositions succeeds. The selected disposition lights visibly, then Close becomes available.

## Archivist

- `Ask the Archivist to file privately: <text>`
- `Ask the Archivist to file on the Bookshelf: <text>`
- `Ask the Archivist to retrieve: <query>`
- `Ask the Archivist to review: <query>`
- `Approve the Archivist to move to Workbench: <filename>`
- `Ask the Archivist to classify: <query>`
- `Approve the Archivist to file in <collection>: <filename>`

Valid established Bookshelf collections are Projects, Research, Reference, Procedures, and Media.

## Local Library search

- `Ask the Library: <question>` — searches the local Filing Cabinet and Bookshelf and returns bounded source-linked passages.
- `Ask the Library to re-index` — refreshes the local search catalogue and reports stale entries or metadata warnings.

## Conversation

Ordinary conversation does not require a command. Type naturally and Modesty will answer through the configured local model.

- `Bye` or `Goodbye, Modesty` — Modesty says goodbye and closes the Study normally.

## Time zones

These answers are local and immediate; they do not open the Grand Library or call the language model.

- `What time is it in Uganda?`
- `What is the current time in Kenya?`
- `What time is it in Tanzania?`
- `What time is it in South Africa?`
- `What time is it in GMT?`
- `Convert 14:00 in South Africa to Uganda`
- `Convert 9:30 PM in Uganda to South Africa`
- `What time is it in London?`
- `What time is it in Marseille?`
- `What time is it in Chiang Mai?`
- `What time is it in New Zealand?`
- `What time is it in Sydney?`
- `What time is it in US East Coast?`
- `Convert 12:00 on 2026-07-15 in London to South Africa`

Supported working zones include South Africa/SAST; Uganda, Kenya, Tanzania and East Africa/EAT; GMT/UTC; Britain/London; France/Paris/Marseille; Germany/Berlin; Thailand/Bangkok/Chiang Mai; New Zealand/Auckland; Sydney, Melbourne, Brisbane, Adelaide and Perth; and US East Coast/New York, Central/Chicago, and West Coast/Los Angeles.

These answers use Modesty's installed offline timezone-rule database, including daylight-saving changes. `Australia` and `USA` alone are deliberately rejected as ambiguous; name the city or regional zone. Add `on YYYY-MM-DD` when converting a future or past event so the correct seasonal rule is applied.

Use deterministic help whenever you need exact operational wording. Examples include `What commands can I use?`, `Help with the Grand Library`, `remind me how to open the Grand Library`, or a topic-only follow-up after the help index.

This document records implemented deterministic commands. Ordinary conversation does not require command phrasing.
