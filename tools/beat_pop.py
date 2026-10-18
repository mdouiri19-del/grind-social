"""Punchy original pop beat for GRIND. reels, synced to the cuts (synthesized, royalty free).

Usage: python3 tools/beat_pop.py OUT.wav DURATION --bpm 94 --seed 291 \
         --cuts 2.55,6.38,9.57 --impacts 4.47 --brk 6.38,9.57 --end 19.8
  --cuts     scene-cut times (riser into each + kick on it)
  --impacts  times for a low boom hit (stamp, reveal, logo)
  --brk      start,end of a drum break (pattern interrupt), optional
  --end      time the drums stop so the last chord rings out (default: DURATION - 1.2)
Seed picks key and chord progression. Mix at volume 0.47 in ffmpeg for about -18 LUFS.
"""
import sys, wave, argparse
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("dur", type=float)
ap.add_argument("--bpm", type=float, default=94); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--cuts", default=""); ap.add_argument("--impacts", default="")
ap.add_argument("--brk", default=""); ap.add_argument("--end", type=float, default=None)
A = ap.parse_args()
fl = lambda x: [float(v) for v in x.split(",") if v.strip()]
SR = 44100
rng = np.random.default_rng(A.seed)
DUR = A.dur
BPM = A.bpm
B = 60 / BPM
N = int(DUR * SR)
mix = np.zeros(N + SR * 2)
CUTS = fl(A.cuts)
IMPACTS = fl(A.impacts)
BREAK = tuple(fl(A.brk)) if A.brk else (-1.0, -1.0)

def note(m): return 440.0 * 2 ** ((m - 69) / 12)
def add(t, sig, g=1.0):
    p = int(t * SR)
    if p >= len(mix): return
    n = min(len(sig), len(mix) - p)
    mix[p:p + n] += g * sig[:n]
def ts(sec): return np.arange(int(sec * SR)) / SR

def kick():
    t = ts(0.45); f = 45 + 110 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + 0.3 * np.tanh(rng.standard_normal(len(t)) * np.exp(-t * 300))
def clap():
    t = ts(0.3); n = rng.standard_normal(len(t))
    e = np.exp(-t * 22) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    n = n - np.convolve(n, np.ones(8) / 8, mode="same")  # rough high-pass
    return n * e * 0.6
def hat(open_=False):
    t = ts(0.25 if open_ else 0.06); n = rng.standard_normal(len(t))
    n = n - np.convolve(n, np.ones(4) / 4, mode="same")
    return n * np.exp(-t * (14 if open_ else 80)) * 0.5
def pluck(f, sec):
    t = ts(sec)
    s = sum((1 / k) * np.sin(2 * np.pi * f * k * t) for k in range(1, 7))
    return s * np.exp(-t * 9) * np.minimum(1, t / 0.003)
def sub(f, sec):
    t = ts(sec)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.tanh(3 * np.sin(2 * np.pi * f * t))) * np.minimum(1, t / 0.01) * np.minimum(1, (sec - t) / 0.03)
def pad(freqs, sec):
    t = ts(sec)
    s = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 1.003 * t) for f in freqs) / len(freqs)
    return s * np.minimum(1, t / 0.08) * np.minimum(1, (sec - t) / 0.15)
def riser(sec):
    t = ts(sec); n = rng.standard_normal(len(t))
    hp = n - np.convolve(n, np.ones(3) / 3, mode="same")
    return hp * (t / sec) ** 2.5 * 0.5
def impact():
    t = ts(1.0); f = 38 + 60 * np.exp(-t * 12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    return boom + rng.standard_normal(len(t)) * np.exp(-t * 25) * 0.4

ROOT = [57, 55, 60, 52, 59][A.seed % 5]  # A G C E B
PROG = [
    [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]],   # i VI III VII
    [[0, 3, 7], [-2, 2, 5], [-4, 0, 3], [-5, -1, 2]],  # i VII VI v
    [[0, 3, 7], [5, 8, 12], [-4, 0, 3], [-2, 2, 5]],   # i iv VI VII
][A.seed % 3]
ARP = [0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 1, 2, 1]

def in_break(t): return BREAK[0] <= t < BREAK[1]
end_drums = A.end if A.end is not None else DUR - 1.2  # drums stop near the end, chord rings out

bar = 4 * B
nb = int(np.ceil(DUR / bar)) + 1
for i in range(nb):
    t0 = i * bar
    ch = PROG[i % 4]
    add(t0, pad([note(ROOT + c) for c in ch], bar), 0.10)

    for s16 in range(16):
        t = t0 + s16 * B / 4
        if t >= DUR: break
        drums = not in_break(t) and t < end_drums
        # arp: sparse in the break, full elsewhere
        if True:
            m = ROOT + 12 + ch[ARP[s16]] + (12 if s16 in (6, 14) else 0)
            add(t, pluck(note(m), 0.3), 0.2 if in_break(t) else 0.11)
        if s16 % 2 == 0 and drums:
            m = ROOT - 24 + ch[0] + (12 if s16 in (6, 14) else 0)
            add(t, sub(note(m), B / 2 * 0.9), 0.22)
        if in_break(t):
            add(t, hat(open_=(s16 % 4 == 2)), 0.14 if s16 % 2 else 0.09)
            if s16 in (0, 8): add(t, kick(), 0.35)
            continue
        if not drums: continue
        if s16 % 4 == 0 or s16 == 10: add(t, kick(), 0.75)
        if s16 in (4, 12): add(t, clap(), 0.45)
        add(t, hat(open_=(s16 % 4 == 2)), 0.10 if s16 % 2 else 0.06)

add(BREAK[0], pad([note(ROOT + c) for c in PROG[1]], BREAK[1] - BREAK[0]), 0.22)
for c in CUTS:
    add(c - 0.5, riser(0.5), 0.35)
    add(c, kick(), 0.5)
for t in IMPACTS:
    add(t, impact(), 0.6)
if BREAK[1] > 0: add(BREAK[1], impact(), 0.45)

mix = mix[:N]
mix = np.tanh(mix * 1.3) / np.tanh(1.3)  # soft glue
fade = int(0.8 * SR); mix[-fade:] *= np.linspace(1, 0, fade) ** 1.5
mix[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.85
L = mix; R = np.roll(mix, 180) * 0.97
st = np.stack([L, R], axis=1)
with wave.open(A.out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
