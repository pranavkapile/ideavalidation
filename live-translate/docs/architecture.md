# Live Translation Platform — Stack & Architecture (compact spec)

Compact on purpose: this is the file to give an AI coding assistant as context.
Background and rationale are in `live-translation-platform-plan.md`.

> **Implemented MVP (see `app/`, run instructions in `README.md`):** to keep local setup to two
> containers, speech-to-text (faster-whisper + its built-in Silero VAD) and text-to-speech (Piper)
> run inside the orchestrator process; only translation (LibreTranslate) is a separate service.
> Speaker frames are PCM16 at 16 kHz; captions are sent for final segments only (no partials yet).

## Stack (pin versions when building)

| Layer | Tool | Runs as |
|---|---|---|
| Frontend | 1 HTML file + vanilla JS + AudioWorklet | static, served by Caddy |
| Proxy/TLS | Caddy 2 | container |
| Transport | WebSocket (MVP) → LiveKit (scale) | orchestrator / container |
| Orchestrator | Python 3.12, FastAPI, uvicorn, httpx | container (custom code) |
| VAD + STT | WhisperLive (faster-whisper + Silero VAD), int8 | container |
| MT | LibreTranslate (MVP) → CTranslate2 NLLB/MADLAD (scale) | container |
| TTS | Piper HTTP server, voices in volume | container |
| State | in-memory dict (MVP) → Redis (multi-node) | — |

No database, no LLM, no frontend framework.

## Architecture

```
[Speaker browser] --PCM16 16kHz WS--> [orchestrator] --WS--> [stt:9090]
                                            |  final segment {text, lang}
                                            |--HTTP--> [mt:5000]  x active target langs
                                            |--HTTP--> [tts:5001] x active target langs
[Listener browser] <--WS captions JSON + audio(wav/opus)-- [orchestrator]
```

## Orchestrator spec (only custom code, budget ≤ 500 lines)

```
orchestrator/
  main.py      # FastAPI app, WS routes             (~120 lines)
  rooms.py     # Room state + fan-out               (~80)
  pipeline.py  # stt client, translate, tts, cache  (~150)
  config.py    # env vars                           (~20)
web/index.html # speak/listen UI                    (~150)
compose.yaml   # 5 services
```

**WS routes**
- `/ws/speak/{room}` → in: binary PCM16 frames. Out: partial captions (echo).
- `/ws/listen/{room}?lang=xx` → out: `{"t":"cap","lang","text","src","final"}` text frames + binary audio frames.

**Room state**
```python
Room = {"listeners": dict[lang, set[WebSocket]], "speakers": set[WebSocket]}
```

**On each final STT segment**
```
targets = listeners.keys() - {src}
texts   = gather(translate(text, src, t) for t in targets)   # LRU cache (text,src,tgt)
for t: broadcast caption(t)                                  # captions first
for t: audio = tts(texts[t], voice[t]); broadcast(audio)     # drop if queue > 2
```

**Config (env)**: `STT_URL, MT_URL, TTS_URL, VOICES=en:en_US-lessac-medium,es:es_ES-davefx-medium,...`

## Resource rules
1. Translate/TTS once per language per room, never per listener.
2. Only languages that currently have listeners are produced.
3. Captions always; audio is dropped when it falls behind.
4. int8 models on CPU; GPU optional.
5. Language with no Piper voice → captions only.

## Token-efficient build plan (AI-assisted development)

Keep each AI session small and focused:

| # | Session task | Context to give the assistant | Output |
|---|---|---|---|
| 1 | Write `compose.yaml` + Caddyfile | this file only | runs the 4 off-the-shelf services |
| 2 | `config.py` + `rooms.py` | this file | room state + broadcast |
| 3 | `pipeline.py` | this file + the STT/MT/TTS API notes below | clients + cache |
| 4 | `main.py` | this file + `rooms.py`, `pipeline.py` signatures only | WS routes |
| 5 | `web/index.html` | WS route section only | UI |
| 6 | Test end to end | error output only, not whole files | fixes |

Rules that save tokens:
- Put this spec in `CLAUDE.md` (or link it) so it is not re-explained every session.
- One file per session; share **function signatures**, not whole files, across modules.
- Paste the **failing trace**, not full logs; use `tail`/`grep` on logs.
- Use off-the-shelf containers — never ask the AI to write STT/MT/TTS code.
- Pin the API contracts below up front so nothing is rediscovered.

## External API contracts (verify against pinned versions)
- **LibreTranslate:** `POST /translate {"q","source","target","format":"text"}` → `{"translatedText"}`
- **Piper HTTP:** `POST / ` text body (voice selected at server start or per request depending on version) → WAV
- **WhisperLive:** WS; first message JSON `{"uid","language":null,"task":"transcribe","model","use_vad":true}`, then float32 PCM frames; receives `{"segments":[{"text","completed"}]}`
