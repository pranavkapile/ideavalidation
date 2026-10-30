# Self-Hosted Live Speech Translation Platform — Plan

**Goal:** a self-hostable service where a speaker talks in any supported language and
listeners hear (and read) it live in their chosen language(s) — many-to-many —
built almost entirely from open-source components, with minimal custom code and
the smallest hardware footprint that still works.

---

## 1. Core pipeline

```
 Mic (browser) ──WebRTC/WS──▶ VAD ─▶ STT ─▶ text segment (+ detected lang)
                                              │
                                              ▼
                              Translate once per *active* target language
                                              │
                         ┌────────────────────┼────────────────────┐
                         ▼                    ▼                    ▼
                      TTS (es)             TTS (hi)             TTS (fr)
                         │                    │                    │
                         └──── fan-out to every listener of that language ────┘
                                   (captions over WS + audio stream)
```

The main resource saving: **translation and TTS run once per target
language per room, not once per listener.** Languages nobody is listening to are
never produced.

---

## 2. Component choices (open source)

| Stage | Recommended | Why | Low-resource fallback | Avoid for commercial use |
|---|---|---|---|---|
| Voice activity detection | **Silero VAD** (MIT) | Tiny, CPU, cuts audio into utterances so STT only runs on speech | WebRTC VAD | — |
| Speech-to-text | **faster-whisper** (MIT, CTranslate2) served by **WhisperLive** (MIT) | ~99 languages, auto language detection, int8 on CPU, streaming server already written | **whisper.cpp** server; **Vosk** (Apache 2.0) for very weak CPUs (fewer languages, lower quality) | — |
| Translation | **NLLB-200 distilled-600M** converted to CTranslate2 int8 | 200 languages, any-to-any in one model, ~1 GB RAM in int8 | **LibreTranslate** / Argos Translate (AGPL/MIT) — zero-code REST API, CPU-only, ~40 languages | NLLB weights are **CC-BY-NC** → for commercial use swap to **MADLAD-400** (Apache 2.0) or **Opus-MT** (CC-BY) pairs |
| Text-to-speech | **Piper** (fast, CPU, ONNX, 30+ languages, many voices) | Real-time on a Raspberry Pi 4–class CPU; per-language voice files ~20–60 MB | **eSpeak NG** (robotic but ~100 languages) | **XTTS-v2** (Coqui CPML, non-commercial) — better quality/voice cloning but GPU-hungry |
| Real-time transport | **LiveKit server** (Apache 2.0, single Go binary) | WebRTC rooms, one track per language, handles many listeners/NAT/TURN | Plain WebSocket from a small Python service (fine for < ~50 listeners) | — |
| Reverse proxy / TLS | **Caddy** | Automatic HTTPS (browsers require HTTPS for mic access) | nginx + certbot | — |
| Packaging | **Docker Compose** | One file to run the whole stack | — | — |

> **All-in-one alternative:** Meta **SeamlessStreaming** does streaming
> speech→speech translation (~100 input / 36 speech-output languages) in a single
> model, but it needs a ≥16 GB GPU and is **CC-BY-NC**. Good for a research demo,
> not for a cheap or commercial deployment.

---

## 3. The only custom code: a small orchestrator (~300–500 lines)

One Python service (FastAPI + asyncio) that glues the boxes together:

1. **Rooms:** `room_id → {speakers, listeners_by_lang}`.
2. **Ingest:** receives speaker audio (16 kHz mono PCM), forwards it to WhisperLive.
3. **On each finalized STT segment** (text + detected source language):
   - set `targets = active listener languages − {source}`
   - call translation for each target (batched in one CTranslate2 call)
   - push caption JSON `{lang, text, original, ts}` to that language's subscribers
   - call Piper for each target and push the audio chunk to that language's
     channel (LiveKit track or WebSocket).
4. **Caching:** LRU cache on `(text, src, tgt)` for repeated phrases.
5. **Back-pressure:** if TTS falls behind, drop audio and keep captions
   (captions are cheap; stale audio is useless).

Frontend: one static HTML page (vanilla JS) — "Speak" button (getUserMedia →
AudioWorklet → WS/LiveKit) and "Listen" with a language dropdown, live captions
and an audio player. No framework needed.

Everything else is configuration.

---

## 4. Latency budget (target: 2–4 s end-to-end)

| Step | CPU-only tier | GPU tier |
|---|---|---|
| VAD end-of-speech wait | 300–600 ms | 300–600 ms |
| STT (per 5 s utterance) | 0.8–2 s (`small` int8) | 0.2–0.4 s (`large-v3-turbo`) |
| Translation (per target) | 100–300 ms | 30–80 ms |
| TTS first audio (Piper) | 100–300 ms | 100–300 ms |
| Network | 50–150 ms | 50–150 ms |
| **Total** | **~2–4 s** | **~1–1.5 s** |

Tuning: emit **partial captions** from STT immediately, translate/speak only
**finalized** segments; split long utterances at punctuation to start TTS earlier.

---

## 5. Hardware tiers

| Tier | Machine | Models | Realistic capacity |
|---|---|---|---|
| **Minimum** | 4 vCPU / 8 GB RAM VPS (~$20–40/mo), no GPU | Whisper `base`/`small` int8, NLLB-600M int8 (or LibreTranslate), Piper `low/medium` voices | 1 active speaker, 3–5 target languages, dozens of listeners |
| **Recommended** | 8 cores / 16–32 GB + 1× 8–12 GB GPU (RTX 3060/4060 class) | Whisper `large-v3-turbo` fp16, NLLB-1.3B, Piper | 3–6 concurrent speakers/rooms, 10+ target languages, hundreds of listeners via LiveKit |
| **Scale-out** | Add GPU nodes | Run STT/MT as separate containers behind a queue | Horizontal: STT workers per room, MT/TTS workers per language |

Disk: ~3–6 GB for models (Whisper small ≈ 0.5 GB, turbo ≈ 1.6 GB, NLLB-600M int8 ≈ 0.6 GB, Piper ≈ 50 MB/voice).

---

## 6. Deployment layout (Docker Compose)

```yaml
services:
  caddy:        # HTTPS + serves static frontend
    image: caddy:2
  livekit:      # optional; WebRTC fan-out for many listeners
    image: livekit/livekit-server
  stt:          # WhisperLive (faster-whisper backend)
    image: ghcr.io/collabora/whisperlive-cpu   # or -gpu
  mt:           # either LibreTranslate, or a tiny CTranslate2 NLLB wrapper
    image: libretranslate/libretranslate
  tts:          # Piper HTTP server, voices mounted as a volume
    build: ./tts
  orchestrator: # the ~400-line FastAPI glue service
    build: ./orchestrator
volumes:
  models:       # shared model cache, downloaded once
```

Image names should be pinned to specific versions when implemented.

---

## 7. Language coverage reality check

- **STT:** Whisper ~99 languages (quality strong for top ~30; weaker for low-resource languages).
- **MT:** NLLB 200 / MADLAD 400 / LibreTranslate ~40.
- **TTS:** Piper ~30+ languages — **this is the bottleneck**. For languages without a
  Piper voice: fall back to eSpeak NG, or offer **captions only**.
- Effective "speak-and-hear" set = intersection of all three; publish this list in the UI.

---

## 8. Build phases

| Phase | Deliverable | Custom code |
|---|---|---|
| **0. Spike (1–2 days)** | Run WhisperLive + LibreTranslate + Piper in Compose; CLI script: mic → text → translated text → wav | ~50 lines |
| **1. MVP (1 week)** | Orchestrator + single HTML page; one room, WebSocket transport, live captions in N languages + TTS audio | ~400 lines |
| **2. Multi-room (1 week)** | Room codes/QR join links, per-language lazy pipelines, caching, back-pressure | +150 lines |
| **3. Scale (as needed)** | LiveKit for audio fan-out, GPU STT, NLLB/MADLAD on CTranslate2, Prometheus metrics | +100 lines |
| **4. Polish** | Glossary/term overrides (pre/post-replace), speaker diarization labels, transcript export (SRT/TXT), simple auth (room passwords) | +150 lines |

---

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Model licenses (NLLB, XTTS, Seamless are non-commercial) | Use MADLAD-400 / Opus-MT + Piper for commercial deployments |
| Whisper hallucinations on silence/noise | Gate with Silero VAD; drop segments with low avg log-prob / high no-speech prob |
| Sentence fragments translate badly | Translate only finalized segments; merge short fragments (< 3 words) with the next |
| Missing TTS voices | Captions-only fallback per language |
| CPU saturation | Lazy per-language pipelines, int8 quantization, drop stale audio, cap languages per room |
| Browser mic requires HTTPS | Caddy automatic TLS |

---

## 10. Success metrics for validation

- End-to-end latency p50 < 3 s (CPU tier) / < 1.5 s (GPU tier).
- Translation quality acceptable to native speakers in ≥ 5 pilot languages (quick 1–5 rating).
- One 8 GB CPU box sustains 1 speaker → 5 languages → 50 listeners without dropped captions.
- Total custom code < 1,000 lines.
