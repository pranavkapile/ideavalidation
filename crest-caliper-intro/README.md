# Crest & Caliper — Logo Intro Animation

An 11-second brand intro that tells the roaster's story (**Sourced → Measured → Roasted**) and lands on the official logo frame.

| File | What it is |
|---|---|
| `crest-caliper-intro-1080x1920.mp4` | Vertical 9:16, 60fps (Reels / Stories / Shorts / TikTok) |
| `crest-caliper-intro-1920x1080.mp4` | Landscape 16:9, 60fps (YouTube, website hero, presentations) |
| `intro.html` | Source animation. Open it in a browser for a live preview (click to replay). Fonts are embedded. |
| `render.js` | Frame-accurate renderer (Playwright → PNG frames → ffmpeg) |

## Storyboard

| Time | Beat |
|---|---|
| 0.0–1.6s | Fade up from black. Roaster embers drift up; a lilac outline of the bean draws itself. **SOURCED** |
| 1.0–3.3s | The *caliper* moment: a precision ruler draws across, the jaws close on the green bean and the readout counts down to `8.42 MM`. **MEASURED** |
| 3.2–5.0s | The jaws retract, the fire intensifies, smoke rises and the bean roasts from green → cinnamon → brown, while the drum temperature climbs to `218°C`. At 4.35s **first crack**: a warm flash, the bean jolts and chaff bursts off. **ROASTED** |
| 5.0–6.5s | The bean shrinks to its place in the mark and turns brand plum. The lilac disc bursts out from it and settles to centre, and the dark roastery fades into the soft café-bokeh background. |
| 5.9–7.5s | The thin outer ring traces clockwise. The icon draws itself *around* the bean: the flask bulb, then the bell shoulders, then the funnel, with the two halves meeting at the top. The base plate snaps in. |
| 7.3–9.0s | **CREST & CALIPER** rises letter by letter from the centre outward. **COFFEE ROASTERS** fades in as its tracking settles. |
| 9.0–10.0s | A single soft light sheen crosses the disc. |
| 10.0–11.0s | Holds on the final logo frame. |

## Brand values used
- Lilac `#D4C0DC`, ink/plum `#29152F` (sampled from the supplied logo)
- Montserrat 600 / 500 for type (the logo's typeface)
- The logo mark is rebuilt as vector paths that trace the original, so it stays sharp at any resolution.

## Re-rendering
```bash
node render.js 1080 1920 60 frames/          # any size works: w h fps outdir
ffmpeg -framerate 60 -i frames/f%05d.png -c:v libx264 -crf 22 -pix_fmt yuv420p out.mp4
node render.js 1080 1080 30 stills/ 11       # single still at t=11s (e.g. a 1:1 end card)
```
Timings live in the `render(t)` function in `intro.html`. Every beat is a `seg(t, start, end)` window, so retiming means changing those numbers.
