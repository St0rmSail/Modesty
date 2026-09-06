# The Fishing Buddy

**Status:** Parked at Build 0.36; RF4 Codex Questions live-accepted at demonstrated Level 2
**Reviewed:** 2026-09-06

The Fishing Buddy is the unseen Team specialist who helps Drew play and learn from fishing simulators. Real-world angling remains a later secondary mode. She is not a chat personality. Modesty consults her through the Team headset and presents the advice, observations, and companionship. The companion runs independently of a game window so the Study may occupy another monitor and a later remote client may use a tablet or phone.

## Responsibility

The Fishing Buddy owns:

- a separate private local codex for Russian Fishing 4, Fisher Online, Professional Fishing 2, and Call of the Wild: The Angler;
- maps, locations, hotspots, species, baits, groundbait recipes, weather, time, behaviour, tackle, and shop economics;
- explicit best-tackle entries for every game-specific species and applicable fishing-style combination, including evidence basis and source; feeder, float, spinning, bottom, trolling, and game-specific methods may therefore recommend different tackle for the same fish; unknown recommendations remain visibly `Not yet established` rather than being guessed;
- Drew's game-specific level, unlocked waters, cash, equipment, catches, experiments, and confirmed observations;
- suggestions for a fishing session based on access, budget, equipment, goals, and current evidence;
- permitted read-only game progress and catch observation without manual catch entry where a trustworthy interface exists;
- sourced public guides, forums, videos, transcript passages, techniques, recipes, and hotspot leads;
- session companionship: concise local activity reports, useful facts, jokes, and optional explicitly controlled music;
- improving later recommendations from Drew's confirmed simulator history.

All codex and personal progression records remain local. Online evidence enters only through explicit bounded retrieval with source and retrieval time; it is not silently published or treated as proven. The Fishing Buddy may not modify saves, inject into a process, intercept network traffic, evade anti-cheat, scrape a source that forbids automation, operate an account, purchase game items, or represent chat rumours as facts. The Researcher may later gather authorized public evidence, but the Fishing Buddy owns fishing interpretation. The Archivist files approved durable general knowledge; the Schedule owns reminders. Optional music requires a separate explicit source and control boundary.

## Build 0.34 — First Cast

The first duty establishes the private multi-game simulator foundation and reports what can truthfully be observed on this machine. It must be useful before any fragile game-specific parser is attempted.

First Cast must:

1. create separate private local codex foundations for all four approved games;
2. discover Russian Fishing 4 from bounded standalone launcher/install evidence, and the other three games from local Steam manifests, without modifying them;
3. record only the existence, path, and capability class of possible local read-only data sources—not their private contents;
4. distinguish `unsupported`, `manual reference only`, `candidate read-only source`, and later `verified adapter` states;
5. report the next safest game-specific adapter and why;
6. expose one short natural command through Modesty and update deterministic help.

No save parsing, catch claims, online scraping, chat monitoring, music, remote client, or visual transformation enters this first foundation unless separately reviewed and tested.

The live acceptance found standalone Russian Fishing 4 at `G:\RF42026` and found Fisher Online, Professional Fishing 2, and Call of the Wild: The Angler through their Steam manifests. It identified The Angler's local save folder only as a candidate read-only source, did not interpret its contents, and changed no save, account, game process, or network service. All 148 automated tests passed. The Fishing Buddy reaches demonstrated Level 1 and earns her future Bobblehead.

## Growth path

After First Cast, each game receives its own bounded adapter. Later builds may add read-only progress, automatic catches where genuinely observable, personal tackle and shop planning, maps/hotspots, sourced web and transcript intake, session recommendations, chat leads, humour, music, and remote display. Each source class must distinguish game state, Drew's observation, community report, and general reference knowledge.

The private codex database separates species identity from tackle recommendations. Every applicable game/species/fishing-style combination carries a non-blank best-tackle value. A newly catalogued combination may begin as `Not yet established`; later evidence can replace it while retaining whether the recommendation came from Drew, observed game state, or an identified external source. “Best” is scoped to that game and style and should eventually account for progression, target size, location, and budget rather than pretending one universal rig is always optimal.

The schema keeps independently changing facts linked rather than flattening them into the species row. It has foundations for games and versions; species and methods; structured tackle setups; waterbodies, spots, coordinates, cast presentation and depth; contextual recommendations covering target class, objective, conditions, level, skills, cost, expected return, ownership, confidence and freshness; identified sources; player state; and catch/session evidence. This structure is intentionally ready before parsers populate it, but an empty field is never evidence that Modesty knows the answer.

Bait effectiveness is also relational. A bait such as redworm or nightcrawler has a stable game-specific identity, but its strength is recorded separately for each species and fishing style. The record may distinguish effectiveness, relative score, selectivity, presentation, compatible hook range, conditions, supporting catches, confidence, source, and game version. Modesty must not describe a bait as universally stronger merely because it outperforms another bait for one target.

The same principle applies to groundbait and every tackle component without precomputing an endless matrix. Groundbait recipes retain ingredients, quantities, preparation, delivery, cost, attraction strength, selectivity, duration and overfeeding risk by species, method, location and conditions. Other component effects, compatibility rules, substitutions and location/method suitability are stored only when evidence exists. The recommendation engine may calculate and cache a result when needed; it does not create rows for every theoretical permutation.

These scores are backstage evidence, not Drew's user interface. Modesty should normally give a concise direction such as “cheese is stronger than maggots for tench here,” “use sweetcorn as the best substitute you own,” or “this spot is poor for feeder fishing; float fishing is better.” She may explain the decisive reasons and uncertainty when useful, but should not expose a numerical optimisation grind unless Drew explicitly asks for it.

Simple advice must not become a repeated sentence template with different nouns inserted. The codex therefore retains a separate companion layer for Drew's and Modesty's scoped likes and dislikes, fishing-memory links, emotional salience, recall cooldowns, and recent recommendation fingerprints. Actual observations, Drew-confirmed memories, shared narrative and fictional colour remain explicitly distinguishable. A lost fish may become a memorable shared episode; a preference for float fishing may provide warmth or break a genuine technical tie.

Personality never contaminates evidence. Modesty may say she fancies trying the floats today when float and feeder options are both sound, or briefly remember the fish that escaped at this spot. She may not claim floats are technically stronger merely because she likes them, fabricate a shared catch, repeat one anecdote until it becomes tiresome, or sacrifice Drew's stated goal without saying so. Language remains generated from meaning and current context rather than selected from a small bank of canned answers.

The first recommendation service now returns semantic guidance rather than a finished canned sentence. It ranks stored contextual evidence, can reject a poorly suited requested method in favour of a better evidenced one, checks an attached setup for unavailable components and looks for owned substitutes, then supplies separately labelled preference and eligible memory context. The eventual Modesty-facing presenter turns that meaning into natural language while recent-response history helps avoid repetition. If no stored recommendation exists, the service returns unknown rather than inventing tackle.

Build 0.35 begins with The Angler because its local save directory is visible. The files use Avalanche ADF binary containers rather than a documented plain-text schema. The first adapter therefore inspects only bounded known filenames, sizes, signatures, SHA-256 identities, snapshot relationships and mid-read change. It does not decode internal fields or claim level, cash, inventory, unlocks or catches. A third-party ADF tool is evidence that the container family can be explored, not authority for The Angler's save-field meanings or permission to modify saves.

A controlled observation may persist a content-free baseline outside the game directory, allow one ordinary play event, and later report which relative containers changed. The baseline contains hashes, sizes and format labels—not decoded bytes or the Steam account directory. This narrows future analysis without turning correlation into a claim about what any field means.

The first live observation showed that a normal save cycle rewrites almost every active and recovery container. Build 0.35 therefore also records 4 KiB block hashes and reports bounded changed byte ranges without retaining raw save content. A changed range is correlation evidence only; it is not a named field and does not authorize save editing.

RF4 Tackle Box may seed the RF4 codex as a distinct weakest-rank `community_reference` source. Stable catalogue intake includes species names, trophy thresholds, location associations, bait associations, activity, time and hook guidance. It cannot silently populate another game's records, overwrite stronger evidence, or masquerade as Drew's observation. Groundbait recipes are a later bounded intake capped at five per meaningful grouping.

Dynamic hotspots have a separate evidence lifecycle. New community leads begin as **rumoured**. A spot becomes **known** only after local testing or equivalent stronger verification. **Favourite** is reserved exclusively for Drew's explicit personal selection from known spots; neither an importer nor repeated success may assign it automatically. Rumours remain available for fresh suggestions and refresh monitoring without displacing known local results.

## Build 0.36 — RF4 Codex Questions

The first useful RF4 enquiry layer answers short natural one-species questions about trophy thresholds, listed waters, bait associations, activity, time, depth, hook guidance and community notes. Drew may mention RF4 directly or address the Fishing Buddy without memorising one rigid sentence. Clear minor spelling errors may resolve approximately; ambiguous or absent species are refused rather than guessed.

Every answer is confined to the Russian Fishing 4 records and labels its selected source and evidence rank. Missing fields remain `not yet established`, and absence from the imported bait list is not proof that a bait cannot work. Long lists are bounded for the conversation panel. This increment does not infer hotspots, recipes, live catches, player progress, tackle ownership or facts from another game.

Drew accepted bait suggestions, waters, trophy weights, an Atlantic cod overview, a named-bait check, approximate spelling recovery, and clean unknown-species refusal through the live Study on 2026-09-06. All 165 automated tests and syntax checks passed. Together with the bounded source-labelled RF4 intake, this raises the Fishing Buddy's demonstrated maturity to Level 2 bounded retrieval; it does not imply personal game-state observation or autonomous fishing advice.

The Fishing Buddy is deliberately parked at this clean restore point while Voice, background presence, and Discord communication receive priority. When resumed, the next functional target is dynamic RF4 hotspot evidence followed by method-aware tackle and a personal-state-informed session planner. Parking does not cancel the remaining codex, game-adapter, companion, remote-display, or visual work.

## Visual representation

The Fishing Buddy earns a Bobblehead only after her first real duty passes. An empty pedestal may use the approved **Gone Fishing** sign until then.

During fishing-companion mode, **Modesty herself** wears a lure-covered baseball cap and carries a large fishing rod. The Study becomes an outdoor lakeside scene with Modesty standing on a rock in the shallows and a tackle box at her feet. This is a future presentation mode, not proof that the Fishing Buddy is a second visible or speaking personality. The accepted neutral Study and Modesty geometry remain untouched until the mode has its own reversible endpoints and approved assets.
