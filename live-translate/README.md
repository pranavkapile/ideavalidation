# Live Translate

Speak in one language; everyone else hears and reads it live in their own language.
Runs fully on your own computer — free, open source, no accounts, no cloud.

**Before you start:** check [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md)
(in short: 4+ CPU cores, 8 GB RAM, 10 GB free disk, Docker).

## Quick start

1. Install **Docker Desktop**: https://docs.docker.com/get-docker/ and start it.
2. Copy this whole `live-translate` folder to your computer.
3. Start it:
   - **Windows:** double-click `start.bat`
   - **macOS / Linux:** open a terminal in this folder and run `./start.sh`
4. Your browser opens **http://localhost:8000** when it is ready.
   The first start downloads 2–4 GB of models and can take 10–30 minutes; later starts take under a minute.

To stop: `stop.bat` (Windows) or `./stop.sh`. Downloaded models are kept.

## Using it

1. Everyone uses the same **Room** name.
2. Listeners pick their language under **Listen** → **Start listening**.
3. The speaker clicks **Start speaking**, allows the microphone, talks and pauses briefly between sentences.
4. Listeners see the translated caption (with the original underneath) and hear it spoken.

Languages without a voice show "(captions only)". Listeners who pick the speaker's own language get captions only.

## Settings

Edit `.env` (created from `.env.example` on first start), then run the start script again.

| Setting | Default | What it does |
|---|---|---|
| `PORT` | `8000` | Web page port |
| `WHISPER_MODEL` | `base` | Speech recognition size: `small` is more accurate on 8+ core machines |
| `LANGUAGES` | `en,es,fr,de,hi` | Languages loaded for translation |
| `VOICES` | 5 voices | Spoken voice per language; voice list: https://huggingface.co/rhasspy/piper-voices |

To add Italian, for example: add `it` to `LANGUAGES` and `it=it_IT-paola-medium` to `VOICES`.

## Using it across devices

Other devices on the same network can **listen** at `http://<this-computer's-IP>:8000`.
To **speak** from another device the page must be served over HTTPS (browser microphone rule) — put it
behind a reverse proxy with a certificate (e.g. Caddy) or an HTTPS tunnel.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Docker is not running" | Open Docker Desktop and wait until it says it is running |
| Stuck on "Waiting for the app" | Run `docker compose logs -f` in this folder to watch progress; first start is slow |
| Port already in use | Change `PORT` in `.env` |
| Captions arrive late or pile up | Use `WHISPER_MODEL=base` or `tiny`, load fewer languages |
| Containers stop / out of memory | Raise Docker Desktop's memory limit to 6 GB+ or load fewer languages |
| Wrong language detected | Choose your language under "I speak" instead of auto-detect |

## Without Docker (developers)

Python 3.10–3.13:

```bash
# translation server, in a separate terminal
pip install libretranslate && libretranslate --load-only en,es,fr,de,hi

# app
cd app
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```

On an NVIDIA GPU set `WHISPER_DEVICE=cuda WHISPER_COMPUTE=float16 WHISPER_MODEL=large-v3-turbo`
(requires CUDA 12 + cuDNN 9 installed).

## Folder contents

```
live-translate/
  start.sh / start.bat     start (and first-time setup)
  stop.sh  / stop.bat      stop
  .env.example             settings template
  compose.yaml             the two containers: app + translation
  app/                     server (Python) and web page
  docs/                    plan, architecture, sharing plan
  SYSTEM_REQUIREMENTS.md
```

Built with faster-whisper (MIT), LibreTranslate (AGPL-3.0), Piper (GPL-3.0). Check those licenses
before redistributing or selling.
