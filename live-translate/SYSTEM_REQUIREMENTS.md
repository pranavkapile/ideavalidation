# System Requirements

Live Translate runs entirely on your own computer in Docker. Nothing is sent to a cloud service.

## At a glance

| | Minimum | Recommended | Best (advanced) |
|---|---|---|---|
| CPU | 4 cores, 64-bit (Intel/AMD x86-64 or ARM64 incl. Apple Silicon) | 8+ cores | 8+ cores + NVIDIA GPU (6 GB+ VRAM) |
| RAM | 8 GB | 16 GB | 16 GB+ |
| Free disk | 10 GB (SSD preferred) | 20 GB SSD | 20 GB SSD |
| `WHISPER_MODEL` | `base` (default) | `small` | `large-v3-turbo` (GPU, non-Docker install only for now) |
| Delay after you stop talking | ~3–5 s | ~2–3 s | ~1–1.5 s |
| Good for | 1 speaker, a few languages, testing | 1–2 speakers, 5+ languages, small events | several rooms |

Delays are estimates. Measured on a 4-core 2.1 GHz Xeon: `base` transcribed 3.8 s of speech in 2.6 s
(415 MB peak RAM); `small` took 3.5 s (1 GB peak RAM), too slow to keep up with continuous speech on 4 cores.

## Operating system

| OS | Supported with | Notes |
|---|---|---|
| Windows 10 (22H2) / 11, 64-bit | Docker Desktop (WSL 2 backend) | Virtualization must be enabled in BIOS. Use `start.bat`. |
| macOS on Apple Silicon or Intel | Docker Desktop | Any macOS version current Docker Desktop supports. Use `start.sh`. |
| Linux, 64-bit (Ubuntu 22.04+, Debian 12+, Fedora, …) | Docker Engine + Compose plugin, or Docker Desktop | Use `start.sh`. |

Required software: **Docker with Compose v2** (`docker compose version` must work). Nothing else; Python is
not needed for the Docker setup.

## Docker Desktop memory setting

Docker Desktop limits how much RAM containers may use. Give it **at least 6 GB**
(Settings → Resources → Memory on macOS; on Windows/WSL 2 it defaults to half of system RAM, which is
enough on a 12 GB+ machine).

## Where the memory goes (approximate)

| Part | RAM | Disk |
|---|---|---|
| Speech-to-text, `base` / `small` / `large-v3-turbo` | 0.4 / 1 / 2–3 GB | 0.15 / 0.5 / 1.6 GB |
| Text-to-speech (Piper), per language voice | ~0.1 GB | ~65 MB |
| Translation (LibreTranslate), 5 languages | ~1.5–2.5 GB (estimate) | ~1 GB |
| Docker images | — | ~2–3 GB |
| Docker Desktop VM (Windows/macOS) | ~1–2 GB | — |

Each extra language in `LANGUAGES` adds roughly 0.2–0.4 GB RAM and ~200 MB disk.

## Network

- **First start:** internet required to download images and models (about 2–4 GB). Allow 10–30 minutes.
- **After that:** the speech-to-text model and voices load from disk with no internet (verified). LibreTranslate
  is expected to work offline once its models are downloaded (not yet verified).
- **Port:** the web page uses port `8000` on this computer. Change `PORT` in `.env` if it is taken.

## Browser and microphone

- Chrome, Edge, Firefox or Safari (current versions).
- Browsers only allow the microphone on `http://localhost` or an `https://` address. Speaking from **another
  device** (phone, second laptop) needs HTTPS — see "Using it across devices" in `README.md`.
- Listening only (no microphone) works from any device that can reach the computer.
- Headphones for listeners in the same room as the speaker, so translated speech isn't picked up again.

## Quick self-check

```bash
docker --version            # Docker installed
docker compose version      # Compose v2 available
docker info                 # Docker is running
```
