# Modesty Voice

**Status:** Deferred audition; no voice selected or implemented

**Reviewed:** 2026-08-09

## Settled direction

Modesty's speech synthesis should run locally. Ordinary speech must not depend on a subscription service or send her dialogue to a remote provider. The eventual voice must remain usable with modest processing overhead alongside her local language model and Study runtime.

The creative reference is Scarlett Johansson's restrained Black Widow-era register and composure, not her identifiable voice. Modesty requires an original voice: adult American, low mezzo or contralto-leaning, lightly husky, composed, intimate without sounding seductive, precisely but naturally articulated, quietly confident, and capable of dry warmth. She should never sound chirpy, childlike, theatrically sultry, or like a celebrity impersonation.

## Current leading candidate

Kokoro-82M `af_nicole` is the current leading audition candidate because its register, timbre, and audibility suit Drew's hearing better than the alternatives tested so far.

Known concern: Nicole's default delivery can sound overly breathy and ASMR-like. That intimacy is attractive in the right moment but inappropriate for routine duties. A grocery list must sound like competent assistance, not as though Modesty is breathing into Drew's ear or attempting seduction.

Rejected initial comparisons:

- `af_bella`: too high in register;
- `af_heart`: too childlike for Modesty.

These observations are audition results, not permanent bans. Model or voice revisions may justify listening again later.

## Deferred audition plan

Do not integrate text-to-speech into Modesty yet. Revisit the candidates periodically and judge them over time rather than choosing from one impressive sample.

First compare Nicole using identical text at speeds:

- `1.00` as the control;
- `1.08`;
- `1.12`;
- `1.16`.

Use at least three duties:

1. **Practical:** "Your grocery list has milk, coffee, potatoes, and washing powder."
2. **Conversational:** "Good morning, Drew. I kept the Grand Library closed while you were away."
3. **Serious:** "That medication interaction may be important. I recommend checking it before proceeding."

The practical sentence is the decisive ASMR check. A voice that makes groceries sound seductive fails even if it performs beautifully elsewhere.

Also evaluate:

- latency and CPU/GPU load alongside Ollama and the Study;
- intelligibility at comfortable listening volume;
- fatigue after an extended conversation;
- short acknowledgements as well as full sentences;
- punctuation and sentence chunking;
- whether light compression or restrained equalisation improves clarity without manufacturing a different identity.

## Selection gate

A voice becomes canonical only after Drew has repeatedly auditioned it over time and explicitly approves it. Implementation follows selection; it must not be used to force a premature choice. Piper remains a possible lightweight fallback, while heavier cloning-oriented systems remain unjustified unless the small local candidates demonstrably fail.
