"""Original, synthesized, royalty-free background music for GRIND. reels. A NEW track every reel.

Usage:
  python3 tools/music.py OUT.wav DURATION --seed <any int> [--genre auto] [--bpm auto]
         [--cuts 2.0,4.5,...] [--impacts 13.2,...] [--brk 9.0,11.0] [--end 19.4] [--log log.md]

  --genre   house | futurebass | trap | synthpop | afro | dnb | boombap | electro | auto (default)
  --bpm     tempo; default picks one inside the genre's range. Build the reel timeline on B = 60/bpm.
  --cuts    scene-cut times: riser into each cut, crash + kick on it, new section after it
  --impacts boom hits (stamp, number reveal, logo)
  --brk     start,end of a breakdown (pattern interrupt): drums drop, filter sweep, riser into the drop
  --end     drums stop here and the last chord rings out (default DURATION - 1.0)
  --log     log.md path: recent "music:" signatures are avoided (genre not used in the last 3 rows,
            same genre+key+progression never within the last 30 rows)

Prints the signature line to put in log.md, e.g.  music: futurebass/F#m/p3/146bpm/s29210
Mix: ffmpeg ... -af "volume=0.5"  (track is normalized to about -1 dBFS peak, gently limited).

Every section after a cut changes something (drum pattern, melody variation, octave, filter), so the
track never sounds like one bar on repeat. Melody, rhythm and sound design all come from the seed.
"""
import argparse, re, sys, wave
import numpy as np

GENRES = {
    #            bpm range     swing
    "house":      ((118, 126), 0.0),
    "futurebass": ((140, 150), 0.0),
    "trap":       ((136, 148), 0.0),
    "synthpop":   ((108, 118), 0.0),
    "afro":       ((102, 112), 0.08),
    "dnb":        ((168, 176), 0.0),
    "boombap":    ((86, 96), 0.16),
    "electro":    ((124, 130), 0.0),
}
KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MINOR = [0, 2, 3, 5, 7, 8, 10]
MAJOR = [0, 2, 4, 5, 7, 9, 11]
# progressions as scale degrees (0-based) in the chosen mode
PROGS = [
    ("m", [0, 5, 2, 6]), ("m", [0, 6, 5, 6]), ("m", [0, 3, 5, 4]), ("m", [5, 6, 0, 0]),
    ("m", [0, 5, 3, 4]), ("m", [3, 4, 0, 5]), ("M", [0, 4, 5, 3]), ("M", [5, 3, 0, 4]),
    ("M", [0, 5, 3, 4]), ("M", [3, 0, 4, 5]), ("M", [0, 3, 4, 3]), ("m", [0, 2, 3, 4]),
]

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("dur", type=float)
ap.add_argument("--seed", type=int, default=0); ap.add_argument("--genre", default="auto")
ap.add_argument("--bpm", type=float, default=0)
ap.add_argument("--cuts", default=""); ap.add_argument("--impacts", default="")
ap.add_argument("--brk", default=""); ap.add_argument("--end", type=float, default=None)
ap.add_argument("--log", default="")
A = ap.parse_args()
fl = lambda x: [float(v) for v in x.split(",") if v.strip()]

SR = 44100
DUR = A.dur
N = int(DUR * SR) + SR * 3

# ---------- choose a fresh signature ----------
recent = []
if A.log:
    try:
        recent = re.findall(r"music:\s*([a-z]+)/([A-G]#?m?)/p(\d+)", open(A.log).read())
    except OSError:
        recent = []
last3 = {g for g, _, _ in recent[-3:]}
last30 = {(g, k, p) for g, k, p in recent[-30:]}

def pick(seed):
    r = np.random.default_rng(seed)
    g = A.genre if A.genre != "auto" else r.choice([x for x in GENRES if x not in last3] or list(GENRES))
    pi = int(r.integers(len(PROGS)))
    root = int(r.integers(12))
    return r, g, pi, root

seed = A.seed
for _ in range(200):
    rng, GENRE, PI, ROOTPC = pick(seed)
    mode, degs = PROGS[PI]
    kname = KEYS[ROOTPC] + ("m" if mode == "m" else "")
    if (GENRE, kname, str(PI)) not in last30:
        break
    seed += 7919
(lo, hi), SWING = GENRES[GENRE]
BPM = A.bpm if A.bpm else float(rng.integers(lo, hi + 1))
B = 60.0 / BPM
S16 = B / 4
SCALE = MINOR if mode == "m" else MAJOR
ROOT = 48 + ROOTPC  # C3 area
CUTS = sorted(fl(A.cuts)); IMPACTS = fl(A.impacts)
BRK = tuple(fl(A.brk)) if A.brk else (-1.0, -1.0)
END = A.end if A.end is not None else DUR - 1.0

L = np.zeros(N); R = np.zeros(N)
def ts(sec): return np.arange(max(1, int(sec * SR))) / SR
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def add(t, sig, g=1.0, pan=0.0):
    if t < 0: sig = sig[int(-t * SR):]; t = 0
    p = int(t * SR)
    if p >= N or len(sig) == 0: return
    n = min(len(sig), N - p)
    L[p:p + n] += g * sig[:n] * np.sqrt(0.5 * (1 - pan))
    R[p:p + n] += g * sig[:n] * np.sqrt(0.5 * (1 + pan))
def lp(x, cut):  # one-pole lowpass, cut may be array
    a = np.exp(-2 * np.pi * np.asarray(cut, dtype=float) / SR) * np.ones(len(x))
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def hp(x, k=6): return x - np.convolve(x, np.ones(k) / k, mode="same")
def noise(n): return rng.standard_normal(n)
def chord_notes(deg, octv=0, size=3, inv=0):
    out = []
    for j in range(size):
        d = deg + 2 * j
        out.append(ROOT + 12 * octv + SCALE[d % 7] + 12 * (d // 7))
    for _ in range(inv): out = out[1:] + [out[0] + 12]
    return out

# ---------- sound design (seeded variations) ----------
KTUNE = rng.uniform(42, 58); KDROP = rng.uniform(25, 45); KCLICK = rng.uniform(0.15, 0.5)
SNTONE = rng.uniform(160, 240); HATDEC = rng.uniform(55, 110)
LEADH = int(rng.integers(3, 9)); DETUNE = rng.uniform(0.003, 0.012)
def kick(g=1.0):
    t = ts(0.5); f = KTUNE + 140 * np.exp(-t * KDROP)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5) + KCLICK * hp(noise(len(t))) * np.exp(-t * 400)) * g
def snare():
    t = ts(0.32)
    return 0.5 * np.sin(2 * np.pi * SNTONE * t) * np.exp(-t * 30) + 0.8 * hp(noise(len(t)), 3) * np.exp(-t * 18)
def clap():
    t = ts(0.3); n = hp(noise(len(t)), 4)
    e = sum(np.exp(-np.maximum(t - d, 0) * 60) * (t >= d) for d in (0, 0.009, 0.018)) / 2 + 0.5 * np.exp(-t * 14)
    return n * e * 0.7
def hat(op=False):
    t = ts(0.3 if op else 0.07)
    return hp(noise(len(t)), 2) * np.exp(-t * (12 if op else HATDEC)) * 0.5
def shaker():
    t = ts(0.09); return hp(noise(len(t)), 2) * np.sin(np.pi * t / 0.09) ** 2 * 0.35
def tom(f):
    t = ts(0.35); ff = f * (1 + 0.6 * np.exp(-t * 30))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 9)
def crash():
    t = ts(1.6); return hp(noise(len(t)), 2) * np.exp(-t * 2.8) * 0.35
def saw(f, t, h=LEADH):
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, h + 1))
def supersaw(fs, sec, bright=6):
    t = ts(sec); s = 0
    for f in fs:
        for d in (-DETUNE, 0, DETUNE):
            s = s + saw(f * (1 + d), t, bright)
    s = s / (3 * len(fs))
    return s * np.minimum(1, t / 0.01) * np.minimum(1, np.maximum(sec - t, 0) / 0.05)
def pluck(f, sec, bright=6):
    t = ts(sec); return saw(f, t, bright) * np.exp(-t * 11) * np.minimum(1, t / 0.002)
def bell(f, sec):
    t = ts(sec)
    return (np.sin(2 * np.pi * f * t + 2.0 * np.exp(-t * 6) * np.sin(2 * np.pi * f * 3.5 * t))) * np.exp(-t * 4)
def lead(f, sec, glide_from=None):
    t = ts(sec)
    ff = f if glide_from is None else f + (glide_from - f) * np.exp(-t * 40)
    ph = 2 * np.pi * np.cumsum(np.ones(len(t)) * ff) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.2)
    s = sum(np.sin(ph * k * vib) / k for k in range(1, 6))
    return s * np.minimum(1, t / 0.01) * np.minimum(1, np.maximum(sec - t, 0) / 0.04)
def bass(f, sec, kind):
    t = ts(sec)
    if kind == "808":
        ff = f * (1 + 0.5 * np.exp(-t * 30))
        s = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(ff) / SR)) * np.exp(-t * 1.2)
    elif kind == "reese":
        s = (saw(f, t, 5) + saw(f * 1.007, t, 5)) * 0.5
    elif kind == "log":  # log-drum style
        ff = f * (1 + 0.25 * np.exp(-t * 25))
        s = np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 7)
    else:
        s = np.sin(2 * np.pi * f * t) + 0.35 * np.tanh(3 * np.sin(2 * np.pi * f * t))
    return s * np.minimum(1, t / 0.005) * np.minimum(1, np.maximum(sec - t, 0) / 0.02)
def pad(fs, sec):
    t = ts(sec)
    s = sum(np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 1.004 * t) + 0.2 * np.sin(4 * np.pi * f * t) for f in fs) / len(fs)
    return s * np.minimum(1, t / 0.12) * np.minimum(1, np.maximum(sec - t, 0) / 0.2)
def riser(sec):
    t = ts(sec); n = hp(noise(len(t)), 3)
    tone = np.sin(2 * np.pi * np.cumsum(300 + 1800 * (t / sec) ** 2) / SR)
    return (n * 0.6 + tone * 0.25) * (t / sec) ** 2.2
def downlifter(sec=1.2):
    t = ts(sec); return hp(noise(len(t)), 3) * np.exp(-t * 3) * 0.5
def impact():
    t = ts(1.3); f = 34 + 70 * np.exp(-t * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) + hp(noise(len(t))) * np.exp(-t * 20) * 0.5
def chop(f, sec):  # vocal-ish formant chop, no words
    t = ts(sec); s = saw(f, t, 12)
    form = np.sin(2 * np.pi * 800 * t) * 0.5 + np.sin(2 * np.pi * 1200 * t) * 0.3
    return np.tanh(s * (1 + form)) * np.exp(-t * 8) * np.minimum(1, t / 0.004)

# ---------- patterns per genre (16 steps), several variants each ----------
def P(s): return [i for i, c in enumerate(s) if c == "x"]
DR = {
    "house":      dict(k=["x...x...x...x..."], s=["....x.......x..."], h=["..x...x...x...x.", "x.xxx.x.x.xxx.x."], bass="sub", boff=True),
    "electro":    dict(k=["x.....x...x.....", "x..x..x...x..x.."], s=["....x.......x..."], h=["x.x.x.x.x.x.x.x.", "xxxxxxxxxxxxxxxx"], bass="reese", boff=False),
    "futurebass": dict(k=["x.........x.....", "x.....x...x....."], s=["........x......."], h=["x.x.x.x.x.x.x.x.", "x.xxx.x.x.xxx.xx"], bass="808", boff=False),
    "trap":       dict(k=["x......x..x.....", "x.....x...x..x.."], s=["........x......."], h=["x.x.x.x.x.x.x.x.", "xxxxx.xxx.xxxxxx"], bass="808", boff=False),
    "synthpop":   dict(k=["x...x...x...x...", "x...x...x..xx..."], s=["....x.......x..."], h=["x.x.x.x.x.x.x.x."], bass="sub", boff=False),
    "afro":       dict(k=["x..x..x...x..x..", "x...x..x..x....."], s=["...x......x....."], h=["x.xx.xx.x.xx.xx."], bass="log", boff=False),
    "dnb":        dict(k=["x.........x.....", "x.......x.x....."], s=["....x.......x...", "....x..x....x..x"], h=["x.x.x.x.x.x.x.x."], bass="reese", boff=False),
    "boombap":    dict(k=["x......x..x.....", "x.x....x..x....."], s=["....x.......x..."], h=["x.x.x.x.x.x.x.x."], bass="sub", boff=False),
}[GENRE]
HALF = GENRE in ("futurebass", "trap", "dnb")  # snare on beat 3 feel already in pattern

# section boundaries: start, cuts, break, end
bounds = sorted(set([0.0] + [c for c in CUTS if 0 < c < DUR] + [b for b in BRK if b > 0]))
def section_of(t):
    i = 0
    for j, b in enumerate(bounds):
        if t >= b: i = j
    return i
def in_brk(t): return BRK[0] <= t < BRK[1]

# melody motif from the seed, varied per section
motif_len = 8
motif = [int(x) for x in rng.choice([0, 1, 2, 3, 4, 5, 6, 7, 9], motif_len)]
rhythm = sorted(rng.choice(range(16), size=int(rng.integers(5, 9)), replace=False).tolist())
lead_kind = rng.choice(["pluck", "bell", "lead", "chop"]) if GENRE not in ("boombap",) else "bell"
arp_shape = rng.choice([[0, 1, 2, 1], [0, 2, 1, 2], [0, 1, 2, 3], [2, 1, 0, 1]])
chord_inv = int(rng.integers(0, 3))

def scale_note(d, octv):
    return ROOT + 12 * octv + SCALE[d % 7] + 12 * (d // 7)

bar = 16 * S16
nbars = int(np.ceil(DUR / bar)) + 1
step = 0
for bi in range(nbars):
    t_bar = bi * bar
    deg = degs[bi % 4]
    for s in range(16):
        t = t_bar + s * S16 + (SWING * S16 if s % 2 else 0)
        if t >= DUR + 0.5: break
        sec = section_of(t)
        brk = in_brk(t)
        drums_on = t < END and not brk
        v = sec % 2  # pattern variant
        energy = min(1.0, 0.55 + 0.15 * sec) if not brk else 0.3
        # --- chords: style depends on genre ---
        if s == 0:
            fs = [hz(m) for m in chord_notes(deg, 1, 3 + (sec % 2), chord_inv)]
            if GENRE in ("futurebass",):
                for k in range(4 if not brk else 1):  # pumped supersaw chord stabs
                    add(t + k * 4 * S16, supersaw(fs, 4 * S16 * (0.95 if not brk else 3.8), 7), 0.13 * energy, rng.uniform(-.3, .3))
            elif GENRE in ("house", "electro"):
                pass  # offbeat stabs below
            else:
                add(t, pad(fs, bar), 0.10 if not brk else 0.16, 0.0)
        if GENRE in ("house", "electro") and s % 4 == 2 and t < END:
            fs = [hz(m) for m in chord_notes(deg, 1, 4, chord_inv)]
            add(t, pluck(fs[0], 0.25, 5) + pluck(fs[1], 0.25, 5) + pluck(fs[2], 0.25, 5), 0.07 * (0.5 if brk else 1), 0.2)
        if brk and s == 0:
            add(t, pad([hz(m) for m in chord_notes(deg, 1, 4)], bar), 0.18)
        # --- drums ---
        if drums_on:
            kp = P(DR["k"][v % len(DR["k"])]); sp = P(DR["s"][v % len(DR["s"])]); hpn = P(DR["h"][(v + sec // 2) % len(DR["h"])])
            if s in kp: add(t, kick(), 0.8)
            if s in sp: add(t, snare() if GENRE in ("dnb", "boombap", "synthpop") else clap(), 0.5, 0.05)
            if s in hpn: add(t, hat(op=(GENRE == "house" and s % 4 == 2)), 0.13 if s % 2 else 0.09, 0.35)
            if GENRE == "trap" and sec >= 1 and s in (14, 15):  # hat rolls
                for r in range(3): add(t + r * S16 / 3, hat(), 0.08, 0.35)
            if GENRE == "afro": add(t, shaker(), 0.12, -0.4)
            if GENRE == "afro" and s in (6, 11): add(t, tom(hz(ROOT + 19)), 0.25, 0.4)
            # fill on the last bar before a cut
            nxt = [c for c in CUTS if c > t]
            if nxt and 0 < nxt[0] - t < 4 * S16 + 1e-6 and s % 2 == 0:
                add(t, tom(hz(ROOT + 12 + (s % 8))), 0.22, rng.uniform(-.5, .5))
        elif brk and t < END:
            if s % 4 == 0: add(t, hat(), 0.07, 0.3)
        # --- bass ---
        if t < END and not brk:
            bk = DR["bass"]
            broot = scale_note(deg, -1)
            if bk == "808":
                if s in P(DR["k"][v % len(DR["k"])]): add(t, bass(hz(broot - 12 + (12 if s > 8 and sec % 2 else 0)), 6 * S16, "808"), 0.42)
            elif bk == "log":
                if s in (0, 3, 6, 10, 13): add(t, bass(hz(broot + (7 if s in (6, 13) else 0)), 2 * S16, "log"), 0.5)
            elif DR["boff"]:
                if s % 4 == 2: add(t, bass(hz(broot), 1.6 * S16, "sub"), 0.4)
            else:
                if s % 2 == 0: add(t, bass(hz(broot + (12 if s in (6, 14) else 0)), 1.8 * S16, bk), 0.3 if bk == "reese" else 0.36)
        # --- arp / lead: changes per section ---
        if t < END + bar:
            if s % 2 == 0 and not brk:
                ns = chord_notes(deg, 2, 4)
                m = ns[arp_shape[(s // 2) % 4] % len(ns)] + (12 if sec % 3 == 2 else 0)
                add(t, pluck(hz(m), 0.18, 4), 0.045 * energy, 0.45 if (s // 2) % 2 else -0.45)
            if sec >= 1 and s in rhythm and t < END:
                d = motif[(rhythm.index(s) + (sec * 2 if sec % 2 else 0)) % motif_len] + (deg if sec >= 3 else 0)
                m = scale_note(d, 2 + (1 if sec % 3 == 1 else 0))
                dur = S16 * 2
                if lead_kind == "pluck": sig = pluck(hz(m), 0.3, 8)
                elif lead_kind == "bell": sig = bell(hz(m), 0.5)
                elif lead_kind == "chop": sig = chop(hz(m), 0.22)
                else: sig = lead(hz(m), dur)
                add(t, sig, (0.09 if lead_kind != "lead" else 0.06) * (1.6 if brk else 1), rng.uniform(-.25, .25))

# ---------- transitions ----------
for c in CUTS:
    add(c - 2 * B if c - 2 * B > 0 else 0, riser(min(2 * B, c)), 0.22, 0)
    add(c, crash(), 0.5, 0.2); add(c, kick(), 0.6)
if BRK[0] > 0:
    add(BRK[0], downlifter(), 0.5)
    add(BRK[1] - 2 * B, riser(2 * B), 0.35)
    add(BRK[1], impact(), 0.5); add(BRK[1], crash(), 0.5)
for t in IMPACTS: add(t, impact(), 0.55)
# opening hit so motion from frame 0 has sound
add(0, impact(), 0.35); add(0, crash(), 0.3)
# ending: last chord rings with a bell
fs = [hz(m) for m in chord_notes(degs[0], 1, 4)]
add(END, pad(fs, DUR - END + 1.0), 0.2)
add(END, bell(hz(chord_notes(degs[0], 2, 1)[0]), 1.5), 0.15)


L = L[:int(DUR * SR)]; R = R[:int(DUR * SR)]
# ---------- simple reverb (noise IR) on a send ----------
irn = int(0.9 * SR); ir = noise(irn) * np.exp(-np.arange(irn) / SR * 5.5); ir /= np.sqrt(np.sum(ir ** 2))
def conv(x):
    n = len(x) + irn; F = 1 << int(np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + 0.12 * conv(L); R = R + 0.12 * conv(np.roll(R, 97))
# master: glue, normalize, fades
def master(x):
    x = np.tanh(x * 1.4) / np.tanh(1.4)
    return x
L = master(L); R = master(R)
pk = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
L = L / pk * 0.89; R = R / pk * 0.89
fo = int(0.6 * SR); L[-fo:] *= np.linspace(1, 0, fo) ** 1.4; R[-fo:] *= np.linspace(1, 0, fo) ** 1.4
st = np.stack([L, R], axis=1)
with wave.open(A.out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print(f"music: {GENRE}/{kname}/p{PI}/{int(BPM)}bpm/s{seed}")
print(f"beat: {B:.4f}s  bar: {bar:.4f}s")
