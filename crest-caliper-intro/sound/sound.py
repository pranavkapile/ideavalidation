"""Procedural sound design for the Crest & Caliper roastery intro.

Everything is synthesised here (no samples), so the audio is original and royalty-free.
Every event is placed on the animation's *full* timeline (same constants as intro.html),
then mapped to output time through the cut's keypoints, so the short cut stays in sync.

Usage:  python3 sound.py full  out.wav
        python3 sound.py short out.wav
"""
import sys
import numpy as np
from scipy import signal

SR = 48000
CUTS = {  # [output time, full-timeline time]; keep in sync with CUTS in intro.html
    "full": [(0, 0), (14.6, 14.6)],
    "short": [(0, 0.3), (1.0, 2.0), (3.1, 6.5), (3.9, 7.7), (4.8, 9.35), (6.5, 11.8), (7.1, 12.7), (8.0, 14.6)],
}

# ---- animation timeline constants (mirrors intro.html) ----
R0, R1 = 2.4, 8.6
TEMP = lambda x: 25 + 190 * (1 - np.exp(-2.6 * x)) / (1 - np.exp(-2.6))
XAT = lambda T: -np.log(1 - (T - 25) / 190 * (1 - np.exp(-2.6))) / 2.6
X_DRY, X_CRACK = XAT(150), XAT(196)
tAt = lambda x: R0 + (R1 - R0) * x
T_CRACK = tAt(X_CRACK)
PULSES = [(0, 1), (.2, .7), (.38, .85), (.55, .55), (.74, .4), (.9, .3)]
STAGE_IN = [0.6, R0 + .25, tAt(X_DRY), T_CRACK - .05, T_CRACK + 1.1]
DISC_HIT = 9.92          # disc burst lands
HERO = 9.45              # roasted bean "pops" into place
TITLE_NOTES = [11.0, 11.16, 11.32, 11.52]

rng = np.random.default_rng(11)


def seg(t, a, b):
    return np.clip((t - a) / (b - a), 0, 1)


def eio(x):
    return np.where(x < .5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)


def sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output="sos")


def filt(x, kind, f, order=2):
    return signal.sosfilt(sos(kind, f, order), x)


class Mix:
    def __init__(self, dur):
        self.n = int(dur * SR) + SR // 2
        self.dry = np.zeros((2, self.n))
        self.wet = np.zeros((2, self.n))

    def add(self, x, start=0.0, gain=1.0, pan=0.0, verb=0.0):
        i0 = int(round(start * SR))
        if i0 >= self.n:
            return
        if i0 < 0:
            x, i0 = x[-i0:], 0
        x = x[: self.n - i0]
        th = (pan + 1) * np.pi / 4
        for ch, g in enumerate((np.cos(th), np.sin(th))):
            self.dry[ch, i0:i0 + len(x)] += x * gain * g
            if verb:
                self.wet[ch, i0:i0 + len(x)] += x * gain * g * verb


def env_ad(n_att, n_dec, n=None):
    a = np.linspace(0, 1, max(n_att, 1)) ** 2
    d = np.exp(-np.linspace(0, 6, max(n_dec, 1)))
    return np.concatenate([a, d])


def click(freq, dur=.012, bright=1.0):
    """A dry woody bean click."""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    nz = filt(rng.standard_normal(n), "bandpass", [freq * .6, min(freq * 1.8, 20000)])
    body = np.sin(2 * np.pi * freq * tt) * .6 + np.sin(2 * np.pi * freq * 1.73 * tt) * .3 * bright
    return (nz * .7 + body) * np.exp(-tt / (dur / 5))


def pop(freq, big=1.0):
    """First-crack pop: sharp snap + hollow resonant body + (for big ones) a little thump."""
    n = int(.09 * SR)
    tt = np.arange(n) / SR
    snap = filt(rng.standard_normal(n), "highpass", 1500) * np.exp(-tt / .0012)
    body = (np.sin(2 * np.pi * freq * tt) + .45 * np.sin(2 * np.pi * freq * 2.31 * tt)) * np.exp(-tt / .018)
    thump = np.sin(2 * np.pi * 115 * tt) * np.exp(-tt / .035) * big
    return snap * 1.2 + body * .8 + thump * .7


def mallet(f, dur=2.4):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt) * np.exp(-tt / .9)
         + .35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / .35)
         + .22 * np.sin(2 * np.pi * 3.99 * f * tt) * np.exp(-tt / .08))
    x[: int(.003 * SR)] *= np.linspace(0, 1, int(.003 * SR))
    return x


def band_sweep(noise, centers, weights_fn):
    """Approximate a time-varying bandpass by blending a bank of fixed bands."""
    out = np.zeros_like(noise)
    for k, fc in enumerate(centers):
        b = filt(noise, "bandpass", [fc / 1.5, min(fc * 1.5, 20000)])
        out += b * weights_fn(k, fc)
    return out


def build(cut, out_path):
    keys = np.array(CUTS[cut], dtype=float)
    D = keys[-1, 0]
    full_of = lambda tau: np.interp(tau, keys[:, 0], keys[:, 1])
    out_of = lambda tf: float(np.interp(tf, keys[:, 1], keys[:, 0]))
    mix = Mix(D)
    N = mix.n
    tau = np.arange(N) / SR
    t = full_of(tau)                                   # full-timeline time per sample
    rx = seg(t, R0, R1)
    c = np.clip((np.where(t < R0, 24, TEMP(rx)) - 25) / 190, 0, 1)
    heat = (1 - (1 - seg(t, 2.1, 2.8)) ** 3) * (1 - eio(seg(t, 8.55, 9.0)))
    white = lambda: rng.standard_normal(N)

    # ---------- A. warm pad: suspended while roasting, resolves to Dmaj9 on the reveal ----------
    def pad(freqs, cutoff):
        x = np.zeros(N)
        for f in freqs:
            for det in (-0.12, 0.12):
                ph = rng.random() * 2 * np.pi
                x += signal.sawtooth(2 * np.pi * f * (1 + det / 100) * tau + ph) / len(freqs)
        return filt(x, "lowpass", cutoff, 2)
    roast_pad = pad([73.42, 110.0, 146.83, 164.81, 220.0], 650)        # D A D E A  (Dsus2)
    logo_pad = pad([73.42, 146.83, 185.0, 220.0, 277.18, 329.63], 1500)  # Dmaj9
    swell = .55 + .45 * eio(seg(t, 6, 9.3))
    a_roast = eio(seg(tau, 0, 2.2)) * swell * (1 - eio(seg(t, 9.6, 10.4)))
    a_logo = eio(seg(t, 9.85, 10.6)) * (1 - eio(seg(tau, D - 1.6, D)))
    mix.add(roast_pad * a_roast, gain=.16, verb=.5)
    mix.add(logo_pad * a_logo, gain=.15, verb=.6)

    # ---------- B. drum rumble ----------
    drum_on = eio(seg(t, 1.5, 2.5)) * (1 - eio(seg(t, 8.8, 9.5)))
    rumble = filt(np.cumsum(white()) / 200, "bandpass", [28, 160], 2)
    rumble = rumble / (np.abs(rumble).max() + 1e-9)
    rot = 1 + .3 * np.sin(2 * np.pi * .62 * tau)
    hum = np.sin(2 * np.pi * 49 * tau) * .4 + np.sin(2 * np.pi * 98 * tau) * .12
    mix.add((rumble + hum) * drum_on * rot, gain=.30)

    # ---------- C. burner: ignition whump + flame roar ----------
    ign = out_of(2.15)
    n = int(1.2 * SR); tt = np.arange(n) / SR
    whump = filt(rng.standard_normal(n), "lowpass", 900) * env_ad(int(.03 * SR), n - int(.03 * SR))
    whump += np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt / .25) * 1.4
    mix.add(whump, ign, gain=.32, verb=.25)
    flick = filt(white(), "lowpass", 7) ; flick = .65 + .35 * flick / (np.abs(flick).max() + 1e-9)
    roar = filt(white(), "bandpass", [140, 950], 2) * .45 + filt(white(), "lowpass", 260) * 1.0
    crackC = np.minimum(1, sum(a * np.exp(-((t - T_CRACK - d) / .055) ** 2) for d, a in PULSES))
    mix.add(roar * heat * (.55 + .45 * c) * flick * (1 + .3 * crackC), gain=.17)
    # ember crackle riding on the fire
    for _ in range(int(D * 9)):
        s = rng.random() * D
        tf = full_of(s); h = float(np.interp(tf, t, heat))
        if rng.random() < h * .8:
            mix.add(click(rng.uniform(3500, 7000), .004), s, gain=rng.uniform(.02, .06), pan=rng.uniform(-.8, .8))

    # ---------- D. charge: beans pour through the hopper and hit the drum ----------
    for i in range(26):
        ts = 1.75 + i * .045 + rng.random() * .05
        mix.add(click(rng.uniform(1600, 2600), .02), out_of(ts + .45), gain=rng.uniform(.08, .14), pan=rng.uniform(-.25, .25), verb=.15)
        mix.add(click(rng.uniform(1100, 1900), .03), out_of(ts + .7), gain=rng.uniform(.18, .3), pan=rng.uniform(-.4, .4), verb=.2)
    # a soft hopper "pour" bed
    pour_env = eio(seg(t, 1.8, 2.1)) * (1 - eio(seg(t, 2.9, 3.4)))
    mix.add(filt(white(), "bandpass", [1500, 5000]) * pour_env, gain=.035)

    # ---------- E. tumbling rattle: beans get lighter and brighter as they roast ----------
    tumble_on = lambda tf: float(seg(tf, 2.5, 3.3) * (1 - seg(tf, 8.75, 9.25)))
    s = 0.0
    while s < D:
        tf = full_of(s)
        on = tumble_on(tf)
        rate = 4 + 60 * on * (.65 + .35 * np.sin(2 * np.pi * .62 * s))
        s += rng.exponential(1 / rate)
        if on <= 0.01:
            continue
        cc = float(np.interp(tf, t, c))
        f0 = 1300 + 2300 * cc + rng.uniform(-300, 300)
        mix.add(click(f0, .012 + .01 * (1 - cc), bright=.6 + .8 * cc), s,
                gain=on * rng.uniform(.05, .16), pan=rng.uniform(-.6, .6), verb=.08)

    # ---------- F. first crack ----------
    for d, a in PULSES:
        for k in range(1 + int(a * 3)):  # each visual pulse is a small cluster of pops
            tf = T_CRACK + d + rng.uniform(-.03, .05) * (k > 0)
            mix.add(pop(rng.uniform(750, 1400), big=a if k == 0 else .2), out_of(tf),
                    gain=(.5 if k == 0 else .25) * (.5 + .5 * a), pan=rng.uniform(-.5, .5), verb=.25)
    for _ in range(16):  # scattered pops in between, like a real first crack
        tf = T_CRACK + rng.uniform(-.2, 1.35)
        mix.add(pop(rng.uniform(900, 1700), big=.1), out_of(tf), gain=rng.uniform(.1, .25), pan=rng.uniform(-.7, .7), verb=.2)

    # ---------- G. stage ticks (subtle UI cue when each stage word lands) ----------
    n = int(.25 * SR); tt = np.arange(n) / SR
    tick = (np.sin(2 * np.pi * 2350 * tt) * .6 + np.sin(2 * np.pi * 1175 * tt)) * np.exp(-tt / .03)
    for tf in STAGE_IN:
        mix.add(tick, out_of(tf + .05), gain=.07, verb=.35)

    # ---------- H. drop: burner cut, beans gather, hero bean lands ----------
    n = int(.9 * SR); tt = np.arange(n) / SR
    puff = filt(rng.standard_normal(n), "lowpass", 600) * np.exp(-tt / .15) * np.minimum(1, tt / .01)
    mix.add(puff, out_of(8.6), gain=.22, verb=.2)
    centers = np.geomspace(300, 5000, 8)
    a0, a1 = out_of(8.7), out_of(HERO)
    n = int((a1 - a0) * SR); tt = np.linspace(0, 1, n)
    nz = rng.standard_normal(n)
    suck = band_sweep(nz, centers, lambda k, fc: np.exp(-((np.log(fc) - np.log(300 + 4700 * tt ** 2)) ** 2) / .3))
    suck *= tt ** 2.5
    mix.add(suck, a0, gain=.22, verb=.3)
    n = int(.6 * SR); tt = np.arange(n) / SR
    tock = np.sin(2 * np.pi * 420 * tt) * np.exp(-tt / .05) + np.sin(2 * np.pi * 90 * tt) * np.exp(-tt / .12)
    mix.add(tock, a1, gain=.32, verb=.35)

    # ---------- I. fold-down whoosh into the disc burst ----------
    a0, a1 = out_of(9.3), out_of(DISC_HIT)
    n = int((a1 - a0) * SR); tt = np.linspace(0, 1, n)
    nz = rng.standard_normal(n)
    sw = band_sweep(nz, centers, lambda k, fc: np.exp(-((np.log(fc) - np.log(4500 - 4000 * tt)) ** 2) / .4))
    mix.add(sw * np.sin(np.pi * tt) ** 1.5, a0, gain=.16, pan=-.15, verb=.3)
    # reverse swell that sucks into the hit
    n = int((a1 - out_of(9.45)) * SR); tt = np.linspace(0, 1, n)
    mix.add(filt(rng.standard_normal(n), "bandpass", [200, 3000]) * tt ** 4, out_of(9.45), gain=.25, verb=.4)

    # ---------- J. disc burst impact ----------
    n = int(2.6 * SR); tt = np.arange(n) / SR
    f = 62 * np.exp(-tt * .6) + 34
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / .7)
    hit = filt(rng.standard_normal(n), "lowpass", 2600) * np.exp(-tt / .09)
    mix.add(sub * .9 + hit * .55, out_of(DISC_HIT), gain=.55, verb=.35)

    # ---------- K. ring trace: airy rising shimmer ----------
    a0, a1 = out_of(10.3), out_of(11.4)
    n = int((a1 - a0 + .8) * SR); tt = np.arange(n) / SR
    span = a1 - a0
    e = np.clip(tt / span, 0, 1)
    air = (np.sin(2 * np.pi * (880 + 220 * e) * tt) * .5 + np.sin(2 * np.pi * (1320 + 330 * e) * tt) * .3)
    air *= np.sin(np.pi * np.clip(tt / (span + .8), 0, 1)) ** 2
    air += filt(rng.standard_normal(n), "bandpass", [3000, 7000]) * .1 * np.sin(np.pi * np.clip(tt / (span + .8), 0, 1)) ** 2
    mix.add(air, a0, gain=.05, pan=.2, verb=.7)

    # ---------- L. sonic logo: four mallet notes as the wordmark rises ----------
    for tf, fq, pn in zip(TITLE_NOTES, [440.0, 587.33, 739.99, 880.0], [-.3, -.1, .1, .3]):
        mix.add(mallet(fq), out_of(tf), gain=.16, pan=pn, verb=.55)
    mix.add(mallet(1174.66, 3.0) * .6 + mallet(293.66, 3.0), out_of(11.75), gain=.12, verb=.6)

    # ---------- M. sheen sparkle ----------
    for k, fq in enumerate([2349.3, 2959.96, 3520.0, 4698.6]):
        tf = 12.85 + k * .12
        n = int(1.2 * SR); tt = np.arange(n) / SR
        g = np.sin(2 * np.pi * fq * tt) * np.exp(-tt / .25) * np.minimum(1, tt / .004)
        mix.add(g, out_of(tf), gain=.035, pan=-.5 + k * .33, verb=.8)

    # ---------- reverb + master ----------
    ir_n = int(2.4 * SR); tt = np.arange(ir_n) / SR
    out = np.zeros_like(mix.dry)
    for ch in range(2):
        ir = filt(rng.standard_normal(ir_n), "lowpass", 5000) * np.exp(-tt / .55)
        ir[: int(.012 * SR)] = 0  # pre-delay
        ir /= np.sqrt((ir ** 2).sum())
        out[ch] = mix.dry[ch] + signal.fftconvolve(mix.wet[ch], ir)[: mix.n] * .9
    out = filt(out, "highpass", 28, 2)
    out = out[:, : int(D * SR)]
    fade = int(.04 * SR)
    out[:, -fade:] *= np.linspace(1, 0, fade)
    out /= np.abs(out).max()
    out = np.tanh(out * 1.6) / np.tanh(1.6)          # gentle glue / soft clip
    out *= 10 ** (-1.0 / 20) / np.abs(out).max()       # peak -1 dBFS
    from scipy.io import wavfile
    wavfile.write(out_path, SR, (out.T * 32767).astype(np.int16))
    print(f"{cut}: {D:.2f}s -> {out_path}")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
