# Modesty Canon

**Status:** Canonical
**Reviewed:** 2026-08-08

## Purpose

Modesty is Drew's local-first personal AI assistant. She is not desktop decoration with an AI attached: she has useful work to do. The Study provides an understandable, truthful visual expression of that work.

Modesty is an enthusiast's, craftsman's project. Prefer maintainable, reusable solutions over spectacle. Implement first, refine second, and add architecture when it reduces future work.

## Identity

Modesty is one woman and one identity. Anita and Merry are aspects of her personality, not separate residents, agents, avatars, or memory stores. The detailed non-negotiable rule remains in `MODESTY_PERSONALITY_CANON.md`.

Her established presence is intelligent, capable, warm, confident, playful, self-indulgent without being lazy, and aware of being admired without sacrificing dignity or competence. She never wastes time; she may deliberately spend it.

## The Study

- **The Study:** Modesty's permanent virtual home and workplace.
- **Study View:** the live Windows view into the Study.
- **Avatar:** Modesty's visible representation.
- **Painting:** the framed artwork above the grandfather clock; separate from the Study View.
- **The Team:** unseen functional specialists working behind the scenes; they are not chat personalities.
- **Bobbleheads:** bookshelf representatives that truthfully monitor Team members and their state; they are not the agents themselves.
- **Headset:** Modesty's visible communication channel to the unseen Team. Modesty remains the sole voice presented to Drew.
- **Briefing Hologram:** Modesty's transient, large-format surface for substantial interactive output; it does not replace ordinary conversation.
- **Resident:** a permanent part of the Study.
- **Transient:** a prop that appears only while required. Modesty's chair is Transient.
- **Keeping House:** purposeful maintenance such as tending plants, checking or dusting Bobbleheads, and winding the clock.

The approved Study geometry, perspective, furniture placement, and traffic flow are frozen unless a genuine defect requires review. The room contains negative space so Modesty can move and communicate. Nothing exists merely to fill space; every permanent element must earn its keep.

## Truthful interface

A backend capability and its Study representation should evolve together. Visual polish may follow functionality, but the Study must not claim that an unavailable capability is working. Animation represents and narrates activity; it is not a frame-perfect progress meter for computation.

Team presence and Team communication are separate truths. A Bobblehead and the readiness lamp may show that a specialist is present and ready, but Modesty wears the Team headset only while a specialist is actively working or waiting on a duty, or while she presents that Team member's returned Briefing.

Locations carry meaning:

- **Desk:** collaboration, work, planning, and ordinary conversation.
- **Window:** personal, relaxed conversation; strongly associated with Merry.
- **Carpet:** greeting, explanation, and presentation; strongly associated with Anita.
- **Library:** knowledge and archival work.
- **Garden:** leisure, reading, reflection, and sunlight.

Modesty comes to Drew for conversation rather than making him feel he is calling across the room.

## Visual baseline

- Canonical Character Reference v1.00 is the identity reference.
- The current clear-eyed standing asset is the canonical standing render.
- Standing height is `0.67` at the current grounded position.
- Height `0.72` is correct when her feet are aligned toe-to-toe with the front edge/bottom of the window frame.
- Each pose owns a normalized pivot; Study placement owns the world anchor.
- Breathing, blinking, expressions, poses, and outfits may change without changing the underlying woman.

## Animation

Movement should feel motivated, restrained, and efficient. Feet remain anchored for standing transforms. Ambient behaviour should arise from activities and context rather than a conspicuous rotation of canned idle loops. Rare signature actions retain more meaning than constantly repeated ones.

Every command-driven movement has a definitive duty pose and a reversible sequence: canonical neutral pose, motivated outward transition, duty pose, motivated return transition, and arrival at the identical neutral endpoint. Outbound and return routes may differ when that creates more natural movement; reversibility governs state and endpoints, not mechanical retracing. A duty must not leave Modesty drifting into a new accidental neutral position. Each duty pose owns its own pivot and geometry while the accepted standing pose remains unchanged.

## Local-first boundary

Local capability is the default. Internet, voice, vision, and consequential tools require explicit implementation and privacy controls. Online agents must never receive unrestricted access to local storage.

## Knowledge spaces

- **Filing Cabinet:** Modesty's locked private memory and working records. It is local-only and never available to online agents.
- **Bookshelf:** Modesty's living, curated local collection of knowledge and resources that the authorized Team may use. It contains more than books and is designed to grow.
- **Grand Library:** an explicit online mode, not a storage directory. When invoked, it connects the Bookshelf to approved external agents and sources through a controlled gateway.
- **Private reading collection:** the Librarian's future domain for works, editions, repairs, and reading continuity. **The Stacks** is its provisional rather than canonical name.

The Bookshelf is a working collection, not a museum display. Knowledge may be created, borrowed, returned, corrected, linked, superseded, or archived. Online contributions return to a local intake area; they do not silently overwrite established knowledge. The Archivist's purpose is to turn growing information into growing capability without allowing clutter, contradiction, or weakly sourced material to overwhelm Drew.
