# Crest & Caliper — Logo Intro Animation

A 14.6-second brand intro that follows one bean from **green to roasted**, then resolves on the official logo frame.

| File | What it is |
|---|---|
| `crest-caliper-intro-1080x1920.mp4` | Vertical 9:16, 60fps (Reels / Stories / Shorts / TikTok) |
| `crest-caliper-intro-1920x1080.mp4` | Landscape 16:9, 60fps (YouTube, website hero, presentations) |
| `intro.html` | Source animation. Open it in a browser for a live preview (click to replay). Fonts are embedded. |
| `render.js` | Frame-accurate renderer (Playwright → PNG frames → ffmpeg) |

## Storyboard: the bean's journey

| Time | Stage | What happens |
|---|---|---|
| 0.0–2.2s | **GREEN**: raw · dense · unroasted | Fade up from black. A lilac outline draws the bean, which fills with raw green-coffee colour under a cool halo. |
| 1.9–4.1s | **DRYING**: moisture escapes | The heat comes on: embers rise and white vapour lifts off the bean. Green fades to straw. A roast-curve graph starts drawing, with a live bean-temperature readout. |
| 4.1–6.0s | **BROWNING**: sugars caramelise | The bean moves through yellow and tan to cinnamon (the Maillard stage). It swells, its crease opens and smoke starts to build. |
| 6.0–7.0s | **FIRST CRACK**: the bean expands and pops | A run of pops: warm flashes, the bean jolts and chaff bursts off. The graph crosses the first-crack marker. |
| 7.0–8.7s | **ROASTED**: developed · aromatic | The bean deepens to a rich coffee brown with a soft oil sheen. The curve finishes at about 215°C. |
| 8.5–10.1s | Reveal | The roasted bean shrinks into its place in the mark and turns brand plum. The lilac disc bursts out from it, and the roastery fades into the café-bokeh background. |
| 9.5–11.1s | Logo build | The outer ring traces. The icon draws itself around the bean (bulb, then shoulders, then funnel) and the base plate snaps in. |
| 10.9–12.6s | Wordmark | **CREST & CALIPER** rises letter by letter. **COFFEE ROASTERS** settles in. |
| 12.6–14.6s | End card | One soft light sheen crosses the disc, then the frame holds on the final logo. |

## Brand values used
- Lilac `#D4C0DC`, ink/plum `#29152F` (sampled from the supplied logo)
- Montserrat 600 / 500 for type (the logo's typeface)
- The logo mark is rebuilt as vector paths that trace the original, so it stays sharp at any resolution.

## Re-rendering
```bash
node render.js 1080 1920 60 frames/          # any size works: w h fps outdir
ffmpeg -framerate 60 -i frames/f%05d.png -c:v libx264 -crf 22 -pix_fmt yuv420p out.mp4
node render.js 1080 1080 30 stills/ 14.6     # single still of the end frame (e.g. a 1:1 end card)
```
Timings live in the `render(t)` function in `intro.html`. Every beat is a `seg(t, start, end)` window, so retiming means changing those numbers.
