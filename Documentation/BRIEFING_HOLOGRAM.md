# Briefing Hologram

**Status:** Functional presentation and decision lifecycle accepted; dedicated gesturing artwork pending

The Briefing Hologram is Modesty's approved surface for substantial human-facing output. It prevents the conversation panel from becoming a cramped document reader while preserving Modesty as the sole conversational presence.

## Output vocabulary

- **Return:** Modesty's concise spoken or chat response. It gives the answer and significance without dictating the entire report.
- **Briefing:** the substantial interactive presentation Drew reads and questions.
- **Report:** the durable document derived from a Briefing if Drew chooses to keep it.
- **Evidence Pack:** the sources, quotations, warnings, dates, and supporting material behind the assessment.

## Briefing Mode

Opening a Briefing will:

1. hide the ordinary conversation panel;
2. move Modesty temporarily to the bottom-right presentation position;
3. eventually use a dedicated professional magician's-assistant presentation gesture indicating the material to her left;
4. unfold a translucent holographic reading surface from a central horizontal seam toward the top and bottom of the Study;
5. occupy most of the area to Modesty's left, including the desk side of the Study;
6. retain a compact text input so Drew can question Modesty without restoring the ordinary panel; and
7. use a motivated return transition and restore Modesty's canonical pose and placement when closed.

The presentation pose owns separate geometry. It must never silently alter the accepted standing pose, pivot, scale, shadow, breathing, or blink behaviour.

The functional transition currently follows a direct eased path to a larger bottom-right duty position, with Modesty's toes aligned to the taskbar edge and her shadow travelling with her. More characterful outbound and return paths are deferred to visual polishing. They must preserve the approved duty endpoint and return to the identical neutral endpoint, but they should not mechanically retrace one another: a rising outward arc and a complementary descending return arc are valid.

The accepted duty endpoint uses `anchor_x: 0.85`, `anchor_y: 1.105`, and `height: 0.80`. Modesty wears the Team headset throughout the Briefing because she is presenting a Team return; at ordinary ready-state idle she does not wear it.

The hologram may be translucent, but readability outranks spectacle. Body text needs sufficient contrast against the bright Study. The surface should support scrolling, search, headings, lists, expandable evidence, and adjustable translucency. External or returned media remains subject to the Grand Library media-intake rules.

## Pending Report lifecycle

Every completed Briefing produces a recoverable **Pending Report**. It survives application restart and remains undecided until Drew explicitly chooses:

- **Keep Privately** in the Filing Cabinet intake;
- **Send to Bookshelf Inbox** for shared curation; or
- **Toss Report** and delete its content.

Close remains disabled while the report is undecided. After one disposition succeeds, that choice is visibly highlighted, the alternatives lock, and Close becomes available. This makes the decision state legible without relying on a small status sentence.

A content-free audit may record that a report was discarded. Report content must not be filed automatically merely because research completed. A future preference may default new work to temporary or likely-permanent, but an unanswered Pending Report is never silently discarded.

## Presentation structure

A research Briefing should show:

1. direct answer;
2. strongest candidates or conclusions;
3. cautions, conflicts, and uncertainty;
4. complete bounded results;
5. expandable evidence and sources; and
6. suggested actions such as investigate, watch, dismiss, keep, or toss.

The same surface can later present Librarian repair comparisons, uncertain OCR, edition conflicts, and export decisions.

The current foundation implements a readable translucent surface, compact questioning, restart-safe Pending Reports, explicit private, Bookshelf Inbox, and toss decisions, gated Close control, centre-opening animation, reversible duty movement, travelling shadow, active-duty headset, and temporary Grand Library visual suppression. The dedicated gesturing sprite and final movement arcs remain polishing work.

The full-height centre-opening animation, 17-pixel report text, compact online indicator, filing and toss acknowledgements, return to the conversation narrative, and bottom-right duty endpoint were accepted in `E:\Modesty` on 2026-08-15. The hologram reserves Modesty's right-side presentation space while retaining a generous readable column.
