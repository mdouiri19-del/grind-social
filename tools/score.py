"""score.py: warm, simple, original background music for GRIND. reels (replaces music.py).

Why: music.py picked melody notes at random (clashed with the chords), stacked too many layers and used raw saws.
score.py keeps it musical and quiet: curated progressions, smooth voicings, consonant parts only (chord tones),
four layers max (drums, bass, keys, one top line), warm sound design (FM electric piano, Karplus-Strong pluck,
filtered pad, soft drums), sidechain pump, dark reverb, gentle master. Every reel gets a NEW track from its seed.

Usage:
  python3 tools/score.py OUT.wav DURATION --seed YYYYMMDD [--style auto|deephouse|lofi|pop] [--bpm N]
         [--cuts t1,t2,...] [--drop t] [--brk a,b] [--end t] [--log log.md]

  Build the reel ON THE GRID it prints (beat and bar). Put every cut on a bar line (or at least a beat).
  --cuts  scene cuts: a soft reverse swell into each cut and a light cymbal on it (no fills, no booms).
  --brk   start,end of the pattern interrupt: drums out, keys filtered dark, a riser into --brk end.
  --drop  one low "thump" accent (for example the big number or stamp). Optional, use once.
  --end   drums and bass stop, the last chord rings out (default DURATION - 1.2).
  --log   avoids reusing a style/key/progression signature from the last rows of log.md.
Mux: ffmpeg ... -af "loudnorm=I=-16:TP=-1.5:LRA=11" (no volume=0.5 with this track).
Prints:  score: <style>/<key>/p<prog>/<bpm>bpm/s<seed>  ->  copy it into log.md as "music: ..."
"""
import argparse, re, sys, wave
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("dur", type=float)
ap.add_argument("--seed", type=int, default=1); ap.add_argument("--style", default="auto")
ap.add_argument("--bpm", type=float, default=0); ap.add_argument("--cuts", default="")
ap.add_argument("--drop", type=float, default=-1); ap.add_argument("--brk", default="")
ap.add_argument("--end", type=float, default=None); ap.add_argument("--log", default="")
A = ap.parse_args()
fl = lambda x: [float(v) for v in x.split(",") if v.strip()]

SR = 44100
DUR = A.dur
N = int((DUR + 3) * SR)
STYLES = {"deephouse": (118, 124, 0.0), "lofi": (82, 90, 0.16), "pop": (96, 104, 0.0)}
KEYS = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
MAJOR = [0, 2, 4, 5, 7, 9, 11]
# progressions as major-scale degrees (0 = I). All diatonic, all well-worn and pleasant.
PROGS = [[0, 4, 5, 3], [5, 3, 0, 4], [3, 0, 4, 5], [1, 4, 0, 5], [0, 5, 3, 4], [5, 4, 3, 4], [3, 4, 2, 5], [0, 2, 3, 4]]

recent = []
if A.log:
    try: recent = re.findall(r"music:\s*([a-z]+)/([A-G][b#]?)/p(\d+)", open(A.log).read())
    except OSError: recent = []
last2 = {s for s, _, _ in recent[-2:]}
used = {(s, k, p) for s, k, p in recent[-30:]}
seed = A.seed
for _ in range(100):
    rng = np.random.default_rng(seed)
    style = A.style if A.style != "auto" else str(rng.choice([s for s in STYLES if s not in last2] or list(STYLES)))
    pi = int(rng.integers(len(PROGS))); key = int(rng.choice([0, 2, 3, 5, 7, 8, 9, 10]))
    if (style, KEYS[key], str(pi)) not in used: break
    seed += 7919
lo, hi, SWING = STYLES[style]
BPM = A.bpm or float(rng.integers(lo, hi + 1))
B = 60.0 / BPM; S16 = B / 4; BAR = 4 * B
ROOT = 48 + key - (12 if key > 6 else 0)          # tonic around C3
CUTS = sorted(c for c in fl(A.cuts) if 0 < c < DUR)
BRK = tuple(fl(A.brk)) if A.brk else (-1.0, -1.0)
END = A.end if A.end is not None else DUR - 1.2
prog = PROGS[pi]

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def ts(sec): return np.arange(max(1, int(sec * SR))) / SR
from scipy.signal import lfilter
def onepole(x, cut):
    a = np.exp(-2 * np.pi * cut / SR)
    return lfilter([1 - a], [1, -a], x)
def lp(x, cut, order=2):
    for _ in range(order): x = onepole(x, cut)
    return x
def hp(x, cut): return x - lp(x, cut, 1)
def env(n, a, d, sus=0.0, rel=0.03):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * (sus + (1 - sus) * np.exp(-t / max(d, 1e-4)))
    r = int(rel * SR); e[-r:] *= np.linspace(1, 0, r) if r < n else 1
    return e

buses = {k: np.zeros((2, N)) for k in ("drums", "bass", "keys", "top", "fx")}
def add(bus, t, sig, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    sig = sig[: N - i]
    buses[bus][0, i:i + len(sig)] += sig * g * np.sqrt(0.5 * (1 - pan))
    buses[bus][1, i:i + len(sig)] += sig * g * np.sqrt(0.5 * (1 + pan))

# ---------------- instruments (cached) ----------------
noise = lambda n: np.random.default_rng(7).standard_normal(n)
def kick():
    t = ts(0.42); f = 46 + 75 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    click = lp(noise(len(t)), 3000, 1) * np.exp(-t * 300) * 0.25
    return np.tanh(1.6 * (body + click)) * 0.9
def clap():
    n = int(0.35 * SR); x = noise(n); e = np.zeros(n)
    for k, d in enumerate([0, 0.011, 0.022]): i = int(d * SR); e[i:] += np.exp(-np.arange(n - i) / SR * (55 if k < 2 else 16))
    return lp(hp(x * e, 900), 5500, 1) * 0.45
def snare():
    t = ts(0.3); tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25)
    return (0.5 * tone + lp(hp(noise(len(t)), 1200), 6000, 1) * np.exp(-t * 18) * 0.6) * 0.6
def hat(open_=False):
    t = ts(0.22 if open_ else 0.06); x = hp(hp(noise(len(t)), 7000), 7000)
    return x * np.exp(-t * (14 if open_ else 70)) * 0.22
def shaker():
    t = ts(0.09); return hp(noise(len(t)), 5000) * np.sin(np.pi * np.minimum(1, t / 0.09)) * 0.12
def epiano(f, dur):          # 2-op FM electric piano, bright attack, mellow tail
    n = int((dur + 0.6) * SR); t = np.arange(n) / SR
    I = 1.8 * np.exp(-t * 6) + 0.25
    x = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * t)) + 0.18 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
    e = np.exp(-t * 1.1) * np.minimum(1, t / 0.004); rel = int(0.15 * SR); k = int(dur * SR)
    if k < n: e[k:] *= np.exp(-np.arange(n - k) / rel)
    return x * e * (1 + 0.06 * np.sin(2 * np.pi * 4.5 * t))
def pluck(f, dur=0.6):        # Karplus-Strong
    n = int(dur * SR); p = max(2, int(SR / f)); buf = lp(noise(p), 5000, 1); out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.497 * (buf[i % p] + buf[(i + 1) % p])
    return lp(out, 4500, 1) * np.exp(-np.arange(n) / SR * 2.5) * 0.8
def pad(fs, dur):             # band-limited detuned saws, dark
    n = int((dur + 0.8) * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f in fs:
        for det in (-0.08, 0.08):
            ff = f * 2 ** (det / 12)
            for h in range(1, int(2500 / ff) + 1): x += np.sin(2 * np.pi * ff * h * t + h) / h
    x = lp(x / (len(fs) * 3), 1100)
    e = np.minimum(1, t / 0.35); k = int(dur * SR)
    if k < n: e[k:] *= np.exp(-np.arange(n - k) / (0.35 * SR))
    return x * e
def subbass(f, dur):
    n = int((dur + 0.08) * SR); t = np.arange(n) / SR
    x = np.tanh(1.3 * np.sin(2 * np.pi * f * t)) * env(n, 0.008, 9, 1.0, 0.06)
    return x
def swell(dur):               # reverse cymbal-ish swell into a cut
    t = ts(dur); x = lp(hp(noise(len(t)), 3000), 9000, 1)
    return x * (t / dur) ** 3 * 0.25
def cym():
    t = ts(1.2); return lp(hp(noise(len(t)), 5000), 11000, 1) * np.exp(-t * 3.2) * 0.12
def thump():
    t = ts(0.8); f = 38 + 40 * np.exp(-t * 12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.8
def riser(dur):
    t = ts(dur); f = 300 * 2 ** (2.5 * t / dur)
    x = 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) + lp(hp(noise(len(t)), 2000), 8000, 1) * 0.3
    return x * (t / dur) ** 2 * 0.3

K, CL, SN, HC, HO, SH = kick() * 0.55, clap() * 1.6, snare() * 1.4, hat() * 2.6, hat(True) * 2.2, shaker() * 2.2
def DRUM_BAL(x): return x

# ---------------- harmony: smooth 4-voice voicings, chord tones only ----------------
def triad(deg, seventh):
    idx = [deg, deg + 2, deg + 4] + ([deg + 6] if seventh else [])
    return [ROOT + MAJOR[i % 7] + 12 * (i // 7) for i in idx]
def voice(chord, prev):
    pcs = sorted(set(n % 12 for n in chord)); best = None
    for base in range(57, 66):                       # voicing window A3..F4 for the lowest note
        v = []; cur = base
        for _ in range(len(pcs)):
            nxt = min(n for n in range(cur, cur + 13) if n % 12 in pcs and n not in v); v.append(nxt); cur = nxt + 1
        if max(v) > 79: continue
        cost = 0 if prev is None else sum(min(abs(a - b) for b in prev) for a in v)
        if best is None or cost < best[0]: best = (cost, v)
    return best[1]
SEVENTH = style in ("lofi", "deephouse")
voicings, prev = [], None
for d in prog:
    prev = voice(triad(d, SEVENTH), prev); voicings.append(prev)

# a 2-bar top motif built from chord tones of each bar (consonant by construction)
TOP_RH = {"deephouse": [0, 3, 6, 10, 12], "lofi": [2, 7, 10, 14], "pop": [0, 2, 4, 6, 8, 10, 12, 14]}[style]
shape = [int(x) for x in rng.permutation(4)]

def in_brk(t): return BRK[0] <= t < BRK[1]
nbars = int(np.ceil(DUR / BAR)) + 1
for bi in range(nbars):
    tb = bi * BAR
    ch = voicings[bi % 4]; deg = prog[bi % 4]; broot = ROOT - 12 + MAJOR[deg % 7]
    if broot < 36: broot += 12
    sec = sum(1 for c in CUTS if c <= tb + 1e-6)          # section index (adds a layer after the first cut)
    for s in range(16):
        t = tb + s * S16 + (SWING * S16 if s % 2 else 0)
        if t >= DUR + 0.5: break
        brk, live = in_brk(t), t < END
        drums = live and not brk
        # drums
        if drums:
            if style == "deephouse":
                if s % 4 == 0: add("drums", t, K, 0.85)
                if s in (4, 12): add("drums", t, CL, 0.55, 0.05)
                if s % 4 == 2: add("drums", t, HO if sec >= 1 else HC, 0.5, 0.25)
                if sec >= 1 and s % 2 == 1: add("drums", t, SH, 0.6, -0.3)
            elif style == "lofi":
                if s in (0, 7, 10): add("drums", t, K, 0.8)
                if s in (4, 12): add("drums", t, SN, 0.6, 0.05)
                if s % 2 == 0: add("drums", t, HC, 0.55 if s % 4 else 0.75, 0.3)
            else:  # pop
                if s in (0, 6, 8, 11) if sec >= 1 else s in (0, 8): add("drums", t, K, 0.85)
                if s in (4, 12): add("drums", t, CL, 0.5, 0.05)
                if s % 2 == 0: add("drums", t, HC, 0.6, 0.3)
        # bass
        if live and not brk:
            if style == "deephouse" and s in (2, 6, 10, 14): add("bass", t, subbass(hz(broot), 1.7 * S16), 0.5)
            if style == "lofi" and s in (0, 10): add("bass", t, subbass(hz(broot), (9 if s == 0 else 5) * S16), 0.5)
            if style == "pop" and s in (0, 3, 8, 11): add("bass", t, subbass(hz(broot), 2.6 * S16), 0.45)
        # keys
        if s == 0:
            if style == "lofi":
                for j, m in enumerate(ch): add("keys", t + j * 0.012, epiano(hz(m), BAR * 0.95), 0.16, (j - 1.5) * 0.15)
            elif style == "deephouse":
                pass
            else:
                add("keys", t, pad([hz(m) for m in ch], BAR), 0.22)
        if style == "deephouse" and s in (2, 7, 10) and live:     # offbeat EP stabs
            for j, m in enumerate(ch): add("keys", t, epiano(hz(m), 1.4 * S16), 0.11 * (0.6 if brk else 1), (j - 1.5) * 0.2)
        if brk and s == 0: add("keys", t, pad([hz(m) for m in ch], BAR), 0.25)
        # top line: chord tones, only after the first cut, never in the break
        if sec >= 1 and live and not brk and s in TOP_RH:
            k = TOP_RH.index(s); m = ch[shape[k % 4] % len(ch)] + 12
            if style == "pop": add("top", t, pluck(hz(m), 0.5), 0.33, 0.3 if k % 2 else -0.3)
            elif style == "deephouse": add("top", t, pluck(hz(m), 0.7), 0.24, 0.35 if k % 2 else -0.35)
            else: add("top", t, epiano(hz(m), 0.3), 0.07, 0.3)

# end: last chord rings out
add("keys", END, pad([hz(m) for m in voicings[0]], DUR - END + 0.8), 0.28)
for j, m in enumerate(voicings[0]): add("keys", END, epiano(hz(m), DUR - END), 0.12, (j - 1.5) * 0.15)
# transitions: light and sparse
for c in CUTS:
    d = min(B * 2, c); add("fx", c - d, swell(d), 0.8); add("fx", c, cym(), 0.8, 0.2)
if BRK[0] > 0: add("fx", BRK[1] - min(2 * B, BRK[1] - BRK[0]), riser(min(2 * B, BRK[1] - BRK[0])), 1.0)
if A.drop > 0: add("fx", A.drop, thump(), 0.7)
add("fx", 0.0, cym(), 0.7)

# ---------------- mix ----------------
kick_times = [bi * BAR + s * S16 for bi in range(nbars) for s in range(16)
              if (style == "deephouse" and s % 4 == 0) or (style == "lofi" and s in (0, 7, 10)) or (style == "pop" and s in (0, 8))]
duck = np.ones(N); dl = int(0.22 * SR); shape_d = 1 - 0.55 * np.exp(-np.arange(dl) / (0.06 * SR))
for kt in kick_times:
    if kt >= END or in_brk(kt): continue
    i = int(kt * SR)
    if i < N: duck[i:i + dl] = np.minimum(duck[i:i + dl], shape_d[: N - i])
for b in ("bass", "keys"): buses[b] *= duck
if BRK[0] > 0:                                     # break: keys darker (crossfaded lowpass)
    a, b2 = int(BRK[0] * SR), int(BRK[1] * SR)
    for ch_ in (0, 1):
        dark = lp(buses["keys"][ch_], 700); w = np.zeros(N); w[a:b2] = 1
        r = int(0.05 * SR); w[a:a + r] = np.linspace(0, 1, r); w[b2 - r:b2] = np.linspace(1, 0, r)
        buses["keys"][ch_] = buses["keys"][ch_] * (1 - w) + dark * w
buses["drums"] = DRUM_BAL(buses["drums"])
mix = buses["drums"] * 1.0 + buses["bass"] * 0.55 + buses["keys"] * 1.9 + buses["top"] * 1.7 + buses["fx"] * 1.2
# dark plate reverb on keys + top
irn = int(1.8 * SR); ir = lp(np.random.default_rng(3).standard_normal(irn), 3500, 1) * np.exp(-np.arange(irn) / SR * 2.8)
ir /= np.sqrt(np.sum(ir ** 2))
def conv(x):
    n = len(x) + irn; F = 1 << int(np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[: len(x)]
send = buses["keys"] + buses["top"]
mix[0] += 0.22 * conv(send[0]); mix[1] += 0.22 * conv(np.roll(send[1], 211))
mix = mix[:, : int(DUR * SR)]
for c_ in (0, 1): mix[c_] = lp(mix[c_] + 0.35 * hp(mix[c_], 4000) - 0.5 * lp(mix[c_], 60, 1) * 0.0, 15000, 1)
pk = np.max(np.abs(mix)) or 1; mix = mix / pk * 1.15
mix = np.tanh(mix) / np.tanh(1.15)                 # gentle glue
fo = int(0.6 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2
fi = int(0.004 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
mix *= 0.89
pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
with wave.open(A.out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f"score: {style}/{KEYS[key]}/p{pi}/{BPM:g}bpm/s{seed}")
print(f"beat: {B:.4f}s  bar: {BAR:.4f}s  (put cuts on bar lines: " + ", ".join(f"{i * BAR:.3f}" for i in range(1, int(DUR / BAR) + 1)) + ")")
