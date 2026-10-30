# Live Translate (self-hosted)

Speak in one language; listeners get live captions and synthesized speech in their own language.
Open-source stack: faster-whisper (speech-to-text), LibreTranslate (translation), Piper (text-to-speech).

- Plan: `docs/live-translation-platform-plan.md`
- Architecture: `docs/architecture.md`

## Run locally — option A: Docker (easiest)

Requires Docker Desktop (Windows/macOS) or Docker Engine (Linux), ~8 GB RAM free, ~5 GB disk.

```bash
docker compose up --build
```

First start downloads models (Whisper, translation models, voices), which takes several minutes.
Then open **http://localhost:8000**.

## Run locally — option B: without Docker

Requires Python 3.10–3.13.

```bash
# 1. translation server (separate terminal) — either:
docker run -p 5000:5000 -e LT_LOAD_ONLY=en,es,fr,de,hi libretranslate/libretranslate:v1.9.6
#    or: pip install libretranslate && libretranslate --load-only en,es,fr,de,hi

# 2. app
cd app
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```

Open **http://localhost:8000**.

## Try it

1. Tab 1: room `demo`, pick a language under **Listen** → **Start listening**.
2. Tab 2 (or another device): same room → **Start speaking**, allow the microphone, talk, then pause briefly.
3. Tab 1 shows the translated caption and plays it as speech.

Use headphones when testing on one computer, or the speaker mic picks up the translated audio.

## Settings (environment variables)

| Variable | Default | Notes |
|---|---|---|
| `WHISPER_MODEL` | `small` | `base` = faster/less accurate, `large-v3-turbo` = best (use a GPU) |
| `WHISPER_DEVICE` / `WHISPER_COMPUTE` | `cpu` / `int8` | GPU: `cuda` / `float16` |
| `MT_URL` | `http://localhost:5000` | LibreTranslate address |
| `VOICES` | en, es, fr, de, hi | `lang=piper-voice,...`; languages without a voice get captions only. Voice list: https://huggingface.co/rhasspy/piper-voices |
| `SILENCE_MS` | `600` | pause length that ends a sentence |
| `MAX_UTTERANCE_S` | `12` | force a cut during long speech without pauses |

To add a language, add it to `LT_LOAD_ONLY` (compose.yaml) and, for speech, to `VOICES`.

## Notes

- Browsers only allow the microphone on `localhost` or HTTPS. To speak from a phone on your network, put
  the app behind HTTPS (e.g. Caddy) or use a tunnel.
- Translation is produced only for languages someone is listening to, and once per language, not per listener.
- Listeners who pick the speaker's own language get captions only.
