# Grand Library Media Return Policy

**Status:** Enforced text-only boundary for Build 0.12.0

## Present rule

The Grand Library accepts no media files or active media references. A provider may return bounded UTF-8 text with ordinary HTTPS citations. Before any Inbox note is written, the Gateway rejects:

- binary or non-text content;
- Markdown and Obsidian embeds, including `![...](...)` and `![[...]]`;
- all raw HTML, including comments and visual, frame, object, or style containers;
- `data:`, `blob:`, `file:`, and `javascript:` addresses;
- unsafe control characters;
- multiline titles that could alter quarantine metadata;
- titles longer than 200 characters; and
- bodies larger than 64 KiB after UTF-8 encoding.

A refusal consumes the one-shot approval, creates no Inbox note, and records only the failure type in the content-free audit. The same active-markup rules apply to questions and loaned passages because those fields are copied into the quarantined note. Ordinary `https://` citations remain text: Modesty does not fetch or embed their targets merely to quarantine the note.

## Why text only

Opening a note containing remote embeds can disclose network information and fetch content that was never separately approved. Media also introduces format confusion, parser exploits, oversized payloads, metadata leakage, licensing questions, and executable or polyglot files. Renaming a file or trusting a server-supplied content type is not sufficient.

## Future media intake

Media remains prohibited until a separate intake path is implemented and tested. That future path must, at minimum:

1. preview each proposed item with source, declared type, byte size, checksum, and licence or rights information;
2. require approval distinct from the research loan and distinct for each bounded batch;
3. download into a non-rendering quarantine outside established Bookshelf collections;
4. impose an allowlist of necessary formats and verify file signatures rather than extensions or remote headers;
5. reject archives, executables, scripts, documents with active content, unknown formats, redirects outside the approved host boundary, and size or count overruns;
6. strip unnecessary metadata and create safe derivatives where appropriate;
7. scan and inspect before any human preview or application opens the original;
8. retain the original source URL, retrieval time, checksum, rights statement, and inspection result;
9. require explicit Archivist promotion after inspection; and
10. fail closed, remove partial downloads, and record no sensitive content in the audit.

Until every applicable requirement exists, providers must return citations to media rather than the media itself.
