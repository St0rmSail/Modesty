# First Smithsonian Expedition

**Scope:** Build 0.12.0, Step Three

This provider is intentionally restricted to one approved first expedition: retrieving the Smithsonian Open Access record for **ENIAC Accumulator #2**. It is not a general Researcher and has no access to the Filing Cabinet, Bookshelf filesystem, browser, or arbitrary web addresses.

## Boundary

- Online mode and loopback mode are separate and cannot be switched while open.
- Opening online mode sends nothing.
- The exact question is previewed before approval.
- No Bookshelf passage accompanies this first request.
- Only the Smithsonian Open Access HTTPS API is contacted.
- At most five records are accepted.
- Returned text is bounded and every usable record retains a Smithsonian source URL.
- The return enters `Bookshelf/Inbox` with `verified: unverified`.
- The Archivist must review and curate it later; it does not become established knowledge automatically.

## Live sequence

After pulling the Step Three commit, start Modesty normally with `python main.py`. In Modesty's chat panel, enter each command separately:

```text
Open the Grand Library online
```

Opening must confirm that no request has yet been sent. Then prepare the only allowed expedition:

```text
Prepare a Smithsonian expedition: Retrieve the Smithsonian Open Access record for ENIAC Accumulator #2
```

Inspect the preview. It must say that no Bookshelf passages are leaving and provide a unique approval command. Copy that approval command exactly into the chat panel.

After the result returns, close the connection:

```text
Close the Grand Library
```

Do not promote the returned note yet. First inspect Modesty's response and the new `E:\Modesty Bookshelf\Inbox\*-grand-library-smithsonian-*.md` file for relevance, source links, formatting, and unexpected material.

## First-cast quality result

Loan `GL-20260809-80A62FBE` completed the transport safely but did not pass research inspection. Its quarantined note is test evidence, not useful knowledge, and must not be promoted. The corrected provider requires a second live cast using the same command sequence.

Loan `GL-20260809-26CCCD92` correctly refused to create a return because the Open Access API contains no record explicitly matching Kathleen McNulty. The intended Women's History article also requires interactive web verification and is unsuitable as an unattended provider source. The first-catch target therefore requires an explicit decision before another cast.

Drew approved ENIAC Accumulator #2 as the replacement target. The prior Kathleen McNulty command is superseded and must now be refused. The exact-title collection record is the only acceptable third-cast return.
