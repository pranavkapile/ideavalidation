# Crest & Caliper — Logo Intro Animation

A 14.6-second roastery intro. **The logo icon is the roaster:** the funnel is the hopper, the round bulb is the drum window and the base is the burner. The film shows one full roast inside it, then the roaster folds down into the official logo frame.

| File | What it is |
|---|---|
| `crest-caliper-intro-1080x1920.mp4` | **Full** 14.6s, vertical 9:16, 60fps, with sound (Reels / Stories / Shorts / TikTok) |
| `crest-caliper-intro-1920x1080.mp4` | **Full** 14.6s, landscape 16:9, 60fps, with sound (YouTube, website hero, presentations) |
| `crest-caliper-intro-short-1080x1920.mp4` | **Short** 8s cut, vertical 9:16, with sound (pre-rolls, story bumpers, ad openers) |
| `crest-caliper-intro-short-1920x1080.mp4` | **Short** 8s cut, landscape 16:9, with sound |
| `intro.html` | Source animation. Open it in a browser for a live preview (click to replay); add `?cut=short` for the short cut. Fonts are embedded. |
| `render.js` | Frame-accurate renderer (Playwright → PNG frames → ffmpeg) |
| `sound/sound.py` | Procedural sound design: every sound is synthesised, so it's original and royalty-free |
| `sound/full.wav`, `sound/short.wav` | The soundtracks as lossless stereo WAV (48 kHz), for editing |

## Storyboard: one roast

| Time | Stage | What happens |
|---|---|---|
| 0.0–1.8s | (build) | Fade up from black. The roaster draws itself in lilac line art: drum window, body, hopper. The burner plate slides in below. |
| 0.6–2.6s | **CHARGE**: green beans into the drum | Green beans pour through the hopper and land tumbling in the drum. The burner lights with blue flames. A **bean temp** and **roast time** readout appears. |
| 2.6–4.6s | **DRYING**: moisture escapes | The flames turn orange and the drum window glows. White vapour rises from the hopper as the beans fade from green to straw. |
| 4.6–6.6s | **BROWNING**: sugars caramelise | The tumbling beans turn yellow, tan and then cinnamon. Embers speed up and smoke builds. |
| 6.6–7.8s | **FIRST CRACK**: the beans pop | A run of pops: warm flashes, the beans jolt, the flames flare and chaff bursts out of the drum. |
| 7.8–9.4s | **DROP**: roast complete | The beans reach a rich brown at about 215°C and 12:00. The flames go out and the beans gather into a single roasted bean in the centre of the drum. |
| 9.3–10.8s | Fold-down | The roaster shrinks into the logo icon, the burner slides up to become the base plate, and the line art turns brand plum. The lilac disc bursts out from the bean as the background shifts to café bokeh. |
| 10.3–12.7s | Wordmark | The outer ring traces, **CREST & CALIPER** rises letter by letter and **COFFEE ROASTERS** settles in. |
| 12.7–14.6s | End card | One soft sheen crosses the disc, then the frame holds on the final logo. |

## Short cut (8s)
The same film, tightened by remapping time rather than re-edited: build and charge in 1s, the roast in about 2s, first crack close to real speed, then the drop, fold-down and logo, with a 1s hold. The keypoints live in `CUTS` in both `intro.html` and `sound/sound.py`. Edit both together to retime.

## Sound design
Everything is synthesised in `sound/sound.py` and placed using the animation's own timeline constants, so it stays frame-locked in both cuts. Mixed to about −14 LUFS with a −1.5 dBTP ceiling, the social/streaming target.

| Moment | Sound |
|---|---|
| Throughout | Warm pad: a suspended D chord under the roast that swells, then resolves to Dmaj9 on the logo |
| Charge | Hopper pour and woody clicks as each bean lands in the drum |
| Ignition | Gas *whump* with a low thump, then a flickering flame roar that grows with the heat |
| Roast | Drum rumble pulsing with the rotation, plus a tumbling rattle that gets lighter and brighter as the beans dry out, and ember crackle |
| First crack | Clusters of sharp, hollow pops synced to every visual pulse, with scattered pops between them |
| Stage changes | Subtle UI tick as each stage word lands |
| Drop | Burner puff, a rising *suck* as the beans gather, and a wooden *tock* when the roasted bean lands |
| Reveal | Fold-down whoosh, a reverse swell, and a sub-boom impact as the lilac disc bursts |
| Logo | Airy shimmer as the ring traces, a four-note mallet sonic logo (A–D–F♯–A) as the wordmark rises, and a soft sparkle on the sheen |

## Brand values used
- Lilac `#D4C0DC`, ink/plum `#29152F` (sampled from the supplied logo)
- Montserrat 600 / 500 for type (the logo's typeface)
- The logo mark is rebuilt as vector paths that trace the original, so it stays sharp at any resolution.

## Re-rendering
```bash
node render.js 1080 1920 60 frames/          # any size works: w h fps outdir
CUT=short node render.js 1080 1920 60 short/  # the 8s cut
python3 sound/sound.py full full.wav          # or: short short.wav
ffmpeg -framerate 60 -i frames/f%05d.png -i full.wav -c:v libx264 -crf 22 -pix_fmt yuv420p \
  -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 256k out.mp4
node render.js 1080 1080 30 stills/ 14.6     # single still of the end frame (e.g. a 1:1 end card)
```
Timings live in the `render(t)` function in `intro.html`. Every beat is a `seg(t, start, end)` window, so retiming means changing those numbers.
