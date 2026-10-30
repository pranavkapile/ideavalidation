# Plan: Shareable, Use-Anywhere Folder

Goal: anyone can copy one folder, double-click a start script and use Live Translate on Windows,
macOS or Linux, with no programming and no cloud account.

## Principles
- **Docker is the only prerequisite.** Python, models and dependencies live inside containers.
- **One folder, no absolute paths.** Everything is relative to `live-translate/`.
- **One settings file** (`.env`) with safe defaults for a 4-core / 8 GB laptop.
- **Models download on first start** and stay in Docker volumes, so the shared folder stays small (< 1 MB).

## Phases

| # | Step | Status |
|---|---|---|
| 1 | Self-contained folder; `start`/`stop` scripts for Windows and macOS/Linux; `.env.example`; README + system requirements | Done |
| 2 | Test on a clean machine of each kind: Windows 11, macOS (Apple Silicon), Ubuntu — follow README only, time the first start, note RAM use | To do |
| 3 | Publish a prebuilt multi-arch (amd64 + arm64) app image to GitHub Container Registry via GitHub Actions, so users pull instead of build (faster, fewer failure points) | To do |
| 4 | Release: attach `live-translate.zip` (just this folder) to a GitHub Release; users download it without git | To do |
| 5 | Offline bundle for machines without internet: `docker save` both images + export model volumes into one archive with an `install-offline` script | Optional |
| 6 | HTTPS add-on (Caddy service in a compose profile) so phones/laptops on the network can also speak | Optional |
| 7 | GPU add-on: CUDA-based app image + compose profile for NVIDIA machines (`large-v3-turbo`) | Optional |

## Packaging command (phase 4)

```bash
git archive --format=zip --prefix=live-translate/ -o live-translate.zip HEAD:live-translate
```

## Clean-machine test checklist (phase 2)
- [ ] README steps work as written, without extra knowledge
- [ ] Start script detects missing / stopped Docker with a clear message
- [ ] First start completes; time and download size recorded
- [ ] Speak in one tab → caption + audio in another language in a second tab
- [ ] Stop, restart: second start < 1 minute, works without internet
- [ ] Peak RAM recorded (`docker stats`) and matches SYSTEM_REQUIREMENTS.md
