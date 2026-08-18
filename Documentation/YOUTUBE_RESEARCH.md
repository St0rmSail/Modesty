# YouTube Research Boundary

**Status:** Implemented and tested; live mixed-source acceptance paused
**Reviewed:** 2026-08-16

Build 0.19 uses one explicitly supplied public YouTube video as the second source type in a bounded mixed-source story investigation.

The adapter and its live Windows dependency pass the 102-test project suite. Final acceptance remains deliberately open: on 2026-08-16 the selected YouTube source was available, but Scribble Hub returned persistent Cloudflare 522 origin timeouts. Resume the exact end-to-end Briefing test after Scribble Hub recovers. Do not interpret the outage as transcript failure or award Level 4 without the resulting report.

## Access route

The YouTube Data API and public transcript access are separate concerns:

- The official Data API can provide public video/channel metadata using a project and API key. It is quota-controlled.
- Official caption listing and download endpoints require OAuth authorization and are not a general API-key route for downloading arbitrary public transcripts.
- Modesty's first transcript adapter uses the pinned open-source `youtube-transcript-api` package to retrieve captions that YouTube exposes to its ordinary public web client. It uses no login, cookies, account action, API key, or browser-profile access.

Primary references:

- YouTube Data API overview: https://developers.google.com/youtube/v3/getting-started
- Official captions list boundary: https://developers.google.com/youtube/v3/docs/captions/list
- Local transcript adapter project: https://github.com/jdepoix/youtube-transcript-api

## Fail-closed rules

- Accept one complete `youtube.com` or `youtu.be` video URL supplied by Drew.
- Request English public captions only.
- Retain at most 300 snippets and 24,000 normalized characters in working evidence.
- Treat every transcript passage as a claim by the video's speaker, not a verified fact.
- Preserve direct timestamp links for passages used in the Briefing.
- Report whether captions are generated when the provider exposes that status.
- If captions are absent, non-English, empty, blocked, or require additional YouTube proof, stop plainly.
- Never use proxies, proof-token workarounds, cookies, account credentials, CAPTCHA bypass, or transcript scraping escalation silently.
- Never file the transcript automatically or treat public caption access as permission to mirror a video.

## First mixed-source duty

1. Add exactly one visible Scribble Hub story page to the Researcher evidence set.
2. Paste one public YouTube video URL into the Researcher window.
3. State the explicit research focus that should connect or distinguish the sources.
4. Select **Add YouTube transcript and prepare mixed-source briefing**.
5. The Researcher identifies timestamped transcript passages overlapping page signals or the explicit focus; reports configured caution/conflict phrases; distinguishes page observation from speaker report; and exposes missing corroboration.
6. The existing Pending Report and Briefing disposition governs retention.

Keyword overlap proves relevance only. It does not prove that the speaker is correct, that the video reviewed the same edition in full, or that no important concern was omitted. Visual content, comments, likes, account state, and complete-video interpretation remain outside this first adapter.

Focus-only relevance is not page corroboration. If the transcript answers Drew's explicit focus but the Scribble Hub metadata does not expose that subject, the Briefing must say so rather than pretending the two sources agree.
