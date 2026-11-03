# Handoff: Crest & Caliper logo intro animation

> Paste this whole file into a new Claude Code chat. It is the context from an earlier cloud session that built this project.

## 1. Where the work lives

- **Repo:** `https://github.com/pranavkapile/ideavalidation`
- **Branch:** `ccr-e747250b-nkbm6o` (not merged into the default branch, and no PR opened)
- **Folder:** `crest-caliper-intro/`
- **Latest commit at handoff:** "Add sound design and an 8-second short cut", plus this handoff commit after it

Get it locally:
```bash
git clone https://github.com/pranavkapile/ideavalidation.git   # or cd into an existing clone
cd ideavalidation
git fetch origin ccr-e747250b-nkbm6o
git checkout ccr-e747250b-nkbm6o
cd crest-caliper-intro
```

## 2. What the project is

A professional intro animation for **Crest & Caliper Coffee Roasters**, a coffee roastery. It ends on the brand's logo frame: a lilac disc with a thin ring, a plum line-art icon (funnel, round bulb holding a coffee bean, and a base bar) and the wordmark "CREST & CALIPER / COFFEE ROASTERS".

**The user's direction, in order (later requests override earlier ones):**
1. "Creative, high-quality professional intro animation that ends with this logo frame."
2. "Show the journey from green bean through roasting/heating to coffee bean, keeping the same animation style."
3. **"The focus is on roasting, this is for a roastery."** This produced the current concept.
4. "Add sound design, plus make a 5–8 second version."

**Current concept: the logo icon IS the roaster.** The funnel is the hopper, the round bulb is the drum window and the base is the burner. One full roast plays inside it, then the roaster folds down into the logo.

## 3. Files (all in `crest-caliper-intro/`)

| File | What it is |
|---|---|
| `crest-caliper-intro-1080x1920.mp4` | Full 14.6s, vertical 9:16, 60fps, with sound |
| `crest-caliper-intro-1920x1080.mp4` | Full 14.6s, landscape 16:9, 60fps, with sound |
| `crest-caliper-intro-short-1080x1920.mp4` | Short 8s cut, vertical, with sound |
| `crest-caliper-intro-short-1920x1080.mp4` | Short 8s cut, landscape, with sound |
| `intro.html` | **Source of truth for the visuals.** A single HTML file (SVG + 2 canvases, about 500 KB because Montserrat 500/600 is embedded as base64). Open it in a browser for a live preview (click to replay). Query params: `?w=&h=` for size, `?cut=short` for the short cut, `?capture` for render mode. |
| `render.js` | Playwright renderer: `[CUT=short] node render.js <w> <h> <fps> <outdir> [t1,t2,...]`. With times given it writes stills only (`t<time>.png`); otherwise it writes every frame (`f00000.png`, ...). |
| `sound/sound.py` | Procedural sound design: everything is synthesised with numpy/scipy, no samples, royalty-free. `python3 sound/sound.py full|short out.wav` |
| `sound/full.wav`, `sound/short.wav` | Rendered soundtracks, 48 kHz stereo |
| `README.md` | User-facing docs: storyboard, sound table, re-render commands |
| `logo-reference.jpg` | The user's original logo screenshot (1080×2412 phone screenshot). The logo was traced from it. |
| `HANDOFF.md` | This file |

## 4. How `intro.html` works (read this before editing)

- It is fully deterministic: `render(t)` draws the frame at full-timeline time `t`. There is no hidden state, so any frame can be rendered in any order. `window.renderAt(t)` applies the cut remap first. `window.ready` resolves after fonts load and `build()` runs.
- **Coordinate space ("logo units"):** origin at the disc centre, and the disc radius is 566 (measured from the reference). `K = R_PX/566` maps to pixels. `R_PX = min(W,H)*0.463` in portrait and `*0.435` in landscape.
- **Icon space:** the `#icon` and `#machine` groups use icon units (top bar at y=0, drum/bulb centre at (0,388) with r=161, base at y≈604–706). Icon → logo units is `(u*iS, v*iS + iTY)`. Final logo state: `iS=0.5`, `iTY=-308.5`. Intro state: `S_I/TY_I` = 1.05/−450 in portrait and 0.74/−318 in landscape. The `morph` variable blends between them.
- **Brand values:** lilac `#D4C0DC`, ink/plum `#29152F`, Montserrat (600 for the title, 500 for the subline). Title target width is 851 units and the subline 573. Both are laid out per letter via `layoutLetters`.
- **Roast model:** `TEMP(x)` is an exponential curve from 25 to 215°C over roast progress x. `R0=2.4`, `R1=8.6` (roast start and end times). Drying ends at 150°C and first crack is at 196°C, so `T_CRACK ≈ 6.67s`. Bean colour is a gradient driven by temperature, from green through straw, yellow, cinnamon and brown to `#5b321f`.
- **Full timeline (seconds):**

| Time | Beat |
|---|---|
| 0.3–1.8 | The roaster line art draws itself; the burner plate slides in |
| 1.75–3.0 | CHARGE: 26 beans fall through the hopper into the drum |
| 2.1–2.8 | Burner ignites (blue, then orange) |
| 2.4–8.6 | Roast: tumbling beans change colour; the HUD shows bean temp and roast time (00:00 to 12:00) |
| ≈6.67 | First crack: 6 pulses, flash, chaff bursts |
| 8.55–9.0 | Flames go out |
| 8.75–9.3 | Beans gather into the centre |
| 9.0–9.45 | The hero bean appears |
| 9.25–10.15 | Fold-down `morph`: the base slides up and the icon shrinks |
| 9.85–10.8 | The lilac disc bursts out from the hero bean |
| 9.9–10.25 | The line art turns from lilac to ink |
| 9.2–11.2 | Background shifts to café bokeh |
| 10.3–11.4 | Ring traces |
| 11.0–11.7 | Title letters rise |
| 11.7–12.7 | Subline tracking settles |
| 12.75–13.7 | Sheen sweep |
| until 14.6 | Hold on the logo |

- **Stages (headline + caption):** CHARGE, DRYING, BROWNING, FIRST CRACK, DROP. They are defined in the `STAGES` array.
- **Short cut:** `CUTS.short` keypoints `[output, full]` = `[0,0.3],[1,2],[3.1,6.5],[3.9,7.7],[4.8,9.35],[6.5,11.8],[7.1,12.7],[8,14.6]`. **The same `CUTS` table is duplicated in `sound/sound.py`. Change both together** or the sound drifts out of sync.

## 5. How `sound/sound.py` works

The sound is built from the same timeline constants as the animation, with events mapped through the cut. Layers:
- a Dsus2 pad that resolves to Dmaj9 at the reveal
- drum rumble
- burner ignition *whump* and flame roar
- bean pour clicks and a tumbling rattle that gets brighter as the beans roast
- first-crack pop clusters synced to the visual pulses
- stage ticks
- drop: burner puff, suck whoosh and wooden *tock*
- fold-down whoosh, reverse swell and sub-boom disc impact (at about 9.92s)
- ring shimmer, a four-note mallet sonic logo (A4–D5–F♯5–A5, starting at 11.0s) and a sheen sparkle

It uses a synthetic convolution reverb and a tanh soft clip, normalised to a −1 dBFS peak. Final loudness is set at mux time with `loudnorm=I=-14:TP=-1.5`.

**Note:** the previous assistant could not listen to the audio. It was checked only with a spectrogram, which confirmed the events line up. The user has not yet given feedback on how it sounds, so expect possible requests to change levels or tone.

## 6. Rebuild commands

Requirements:
- Node with Playwright (run `npx playwright install chromium` once if you don't have it locally)
- ffmpeg
- Python 3 with numpy, scipy and Pillow

```bash
cd crest-caliper-intro
# stills to check a change (fast)
node render.js 1080 1920 30 /tmp/stills 2.4,6.7,9.6,14.6
# full frames (877 frames per format, about 10–13 min each)
node render.js 1080 1920 60 /tmp/f1080x1920
CUT=short node render.js 1080 1920 60 /tmp/s1080x1920      # 481 frames
python3 sound/sound.py full sound/full.wav
python3 sound/sound.py short sound/short.wav
ffmpeg -y -framerate 60 -i /tmp/f1080x1920/f%05d.png -i sound/full.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 22 -maxrate 14M -bufsize 28M -pix_fmt yuv420p \
  -af loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000 -c:a aac -b:a 256k -movflags +faststart \
  crest-caliper-intro-1080x1920.mp4
# repeat for 1920 1080 and for the short cut (crest-caliper-intro-short-*.mp4, sound/short.wav)
```

Gotchas learned:
- CRF 16 gave 80 MB files because of the film grain. CRF 22 with a 14M maxrate gives about 3–6 MB with no visible loss.
- Don't use `-shortest` when muxing. It clipped the last frames; the audio and video are already the same length.
- Check changes with a contact sheet of stills before doing a full 60fps render.

## 7. Possible next steps (offered but not yet requested)

- Use the user's **real roast profile** (charge temperature, first-crack time, drop temperature and time). The current temperatures and 12:00 roast time are illustrative only.
- Adjust the sound mix once the user has listened to it.
- Other formats: 1:1 or 4:5 for the Instagram feed. Pass any `w h` to `render.js`; check that the layout fits, since the HUD layout only switches between `W>H` and portrait.
- A silent version or separate stems for editors.

## 8. Earlier versions (in git history, superseded)

- `66335cc`: v1, a caliper concept (Sourced / Measured / Roasted) with a single bean, 11s
- `86ec96d`: v2, a single bean's journey with a roast-curve graph
- `9940514` and later: v3, the roaster concept (current)
