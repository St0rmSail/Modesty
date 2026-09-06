# Modesty Voice

**Status:** Build 0.37 complete and live accepted; no permanent voice selected

**Reviewed:** 2026-09-06

## Settled direction

Modesty's speech synthesis should run locally. Ordinary speech must not depend on a subscription service or send her dialogue to a remote provider. The eventual voice must remain usable with modest processing overhead alongside her local language model and Study runtime.

The creative reference is Scarlett Johansson's restrained Black Widow-era register and composure, not her identifiable voice. Modesty requires an original voice: adult American, low mezzo or contralto-leaning, lightly husky, composed, intimate without sounding seductive, precisely but naturally articulated, quietly confident, and capable of dry warmth. She should never sound chirpy, childlike, theatrically sultry, or like a celebrity impersonation.

## Current comparison baseline

Kokoro-82M `af_nicole` is the closest audition candidate found so far because its register, timbre, and audibility suit Drew's hearing better than the alternatives tested. It is a comparison baseline, not the leading permanent choice and not an approved voice.

Known concern: Nicole's default delivery can sound overly breathy and ASMR-like. That intimacy is attractive in the right moment but inappropriate for routine duties. A grocery list must sound like competent assistance, not as though Modesty is breathing into Drew's ear or attempting seduction.

Rejected initial comparisons:

- `af_bella`: too high in register;
- `af_heart`: too childlike for Modesty.

These observations are audition results, not permanent bans. Model or voice revisions may justify listening again later.

## Voice Agent architecture

Permanent voice selection does not block the Voice Agent foundation. Capture, local speech recognition, turn control, Modesty's existing conversation path, speech generation, and playback remain replaceable layers. A provisional voice may be used for engineering and audition without becoming canonical.

The first operating assumptions are:

- primary microphone: desktop **HD3000**;
- playback: Drew's headphones;
- push-to-talk: both an on-screen control and a keyboard shortcut;
- raw microphone audio: discarded by default after transcription;
- recognized text: shown and passed through the same conversation route as typed input;
- text input: always remains available as the reliable fallback.

These are preferred roles, not hardwired hardware identities. Modesty discovers currently available endpoints at startup, resolves the configured preference by user-readable device description and capability, and lets Drew choose a replacement. Windows endpoint IDs and numeric indices are observations only and must not become durable configuration because reinstalling Windows, changing ports, replacing hardware, or reinstalling a driver may change them.

If the preferred microphone disappears, Voice returns to `MIC OFF` and requests a replacement rather than opening another microphone. If the preferred headphones disappear, Modesty falls back inside her own playback routing to the configured Realtek desktop speakers and displays a clear notice that speaker fallback is active. This does not change the Windows default device. Replacement headphones become preferred only after Drew selects them; the speakers remain the durable authorized fallback unless Drew changes that policy.

The on-screen control and keyboard shortcut must operate one shared state machine. The interface must distinguish `MIC OFF`, `LISTENING`, `TRANSCRIBING`, `THINKING`, and `SPEAKING`, offer an immediate hard-off state, and fail back to text without trapping the Study. The initial keyboard shortcut must be configurable and must not become a system-wide hook until conflicts with games and other applications have been tested.

Listening begins only through deliberate push-to-talk. The first build has no wake word, always-listening mode, background recording, speaker identification, remote microphone, or Discord voice-channel authority. Headphone output reduces acoustic feedback but does not remove the requirement for clean cancellation and device-failure handling.

Audio coexistence is a release requirement. Modesty must use ordinary shared audio streams, never request exclusive ownership of the headphones or microphone, and never change Windows' default playback, default recording, or default communications device. Starting or stopping Modesty must not reroute, mute, disable, or reconfigure Discord or a running game. Device selection belongs to Modesty's own configuration only. Streams must release cleanly on shutdown and recover visibly if Windows reports that a selected device was removed or changed.

Bluetooth headsets require special caution because Windows may expose separate high-quality playback and hands-free communications profiles; opening a microphone can force a profile change that degrades or removes game audio. The hardware audit must record the actual headphone connection and endpoint names before an adapter is chosen. Modesty must not silently switch profiles to make voice work.

Stopping speech and interrupting with a new turn are distinct operations. The first foundation must at least stop playback immediately and allow a fresh push-to-talk turn. Full-duplex overlap, echo cancellation, and conversational barge-in may follow only after the bounded path is stable.

Modesty normally speaks the concise Return. Long Briefings, reports, citations, lists, and reading passages remain visual unless Drew explicitly asks her to read them. The Team headset retains its existing meaning—active communication with an unseen Team specialist—and must not double as the microphone/listening indicator.

Discord text and Discord voice are separate Communications capabilities. Local Voice does not authorize joining a channel, transmitting microphone audio, receiving or recording other participants, or speaking publicly as Drew.

## Continuing audition plan

Revisit candidates periodically and judge them over time rather than choosing from one impressive sample.

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

## Selection and implementation gates

A voice becomes canonical only after Drew has repeatedly auditioned it over time and explicitly approves it. The replaceable Voice Agent pipeline may be implemented with a provisional voice before that decision; implementation must not silently turn the provisional speaker into Modesty's permanent identity. Piper remains a possible lightweight fallback, while heavier cloning-oriented systems remain unjustified unless smaller local candidates demonstrably fail.

## Build 0.37 — Voice Foundation acceptance

The first build must:

1. discover and explicitly select the HD3000 input and headphone output without relying on fragile device numbers;
2. provide on-screen and configurable keyboard push-to-talk with a visible hard-off state;
3. perform bounded local speech recognition and expose recognized text;
4. send that text through the existing deterministic-command and conversation path;
5. speak a concise response through a replaceable provisional local voice;
6. stop playback immediately on request and accept a fresh voice turn;
7. discard raw audio by default and record no hidden microphone history;
8. retain typing as an uninterrupted fallback when capture, recognition, synthesis, or playback fails;
9. remain responsive alongside the Study and local Ollama model;
10. pass a live coexistence test with game audio and Discord already using the selected headphones, without taking exclusive control, changing a Windows default, rerouting another application, or leaving a device locked after shutdown;
11. update local help, tests, architecture, privacy state, and recovery paperwork before closure.

Wake words, always-listening operation, full duplex, remote clients, Discord, voice cloning, permanent voice selection, and elaborate mouth animation are outside Build 0.37.

## 2026-09-06 read-only hardware audit

- CPU: AMD Ryzen 5 7500X3D, 6 cores / 12 logical processors.
- Memory: 31.2 GB available as installed system capacity.
- GPU: NVIDIA GeForce RTX 4060 Ti with 8 GB VRAM confirmed by the NVIDIA management interface; integrated AMD graphics also present.
- Preferred input visible to Qt: `Desktop Microphone (Microsoft LifeCam HD-3000)` and currently the default input.
- Preferred output visible to Qt: `Headphones (2- Monster Airmars SG03)` and currently the default output.
- Hazardous alternate input: `Headset (2- Monster Airmars SG03)`, corresponding to the headset communications path; Windows also exposes a separate `Monster Airmars SG03 Hands-Free` endpoint.
- Authorized fallback output: `Speakers (Realtek(R) Audio)`. Modesty may use it automatically only when the preferred headphone endpoint is unavailable, must announce the fallback visually, and must not change any Windows default.
- Current project Python: 3.14.6 with PySide6 and Qt Multimedia available.
- Not currently installed in the project environment: sounddevice, PyAudio, NumPy, SciPy, Torch, ONNX Runtime, faster-whisper, OpenAI Whisper, Kokoro, Piper, or WebRTC VAD packages.
- NVIDIA reported approximately 6.6 GB of 8 GB VRAM free during the audit; Ollama had no model loaded at that instant. The accepted `gemma4:e2b` model remains installed, so simultaneous loaded-model testing is still required.

The implementation uses Qt Multimedia for shared capture and per-application playback routing, and `sherpa-onnx` 1.13.7 for both local inference directions. Recognition uses the official Whisper `base.en` INT8 encoder/decoder on CPU. Provisional speech uses the official Kokoro multilingual v1.0 model on CPU with `af_nicole` speaker 6 at speed 1.12. This deliberately preserves RTX VRAM for Ollama and keeps the engines behind a replaceable adapter.

The official 6.62-second Whisper test recording transcribed correctly in 0.288 seconds on this machine, an observed real-time factor of 0.043. A practical `af_nicole` sentence and a short runtime smoke sentence both synthesized successfully. The downloaded archives were path-checked before extraction. Recorded archive SHA-256 identities are `475BC7052CE299C007F6D5D5407BA8601F819A2867F6EECEE510ED17DF581542` for Whisper base.en and `C133D26353D776DA730870DAC7DA07DBFC9A5E3BC80CC5E8E83AB6E823BE7046` for Kokoro multi-lang v1.0.

Model files live under ignored `Data/Models/Voice`; tracked configuration stores project-relative model locations and descriptive device preferences, never endpoint indices. Voice starts `MIC OFF`. The on-screen control uses press-and-hold; the configured F8 key uses the same press/release state machine. Raw capture stays in memory and is discarded after transcription. Generated speech uses one temporary WAV that is removed after playback.

Live acceptance on 2026-09-06 passed the bounded voice turn, visible state changes, recognized-text routing, provisional headphone speech, immediate interruption, F8 and on-screen controls, typed fallback, shutdown/restart, and simultaneous Discord/game coexistence. Drew observed no discernible rerouting, degradation, or retained device lock. The automatic Realtek failure path remains policy- and test-covered rather than physically demonstrated by unplugging the headphones during this acceptance.
