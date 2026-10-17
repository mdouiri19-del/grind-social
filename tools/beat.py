"""Generate a soft royalty-free lo-fi beat (original, synthesized) for GRIND. reels.

Usage: python3 beat.py OUT.wav DURATION_SECONDS [SEED]
Seed picks key, chord loop, tempo and texture so each day sounds a bit different.
"""
import sys, wave
import numpy as np

SR = 44100

def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def env(n, a=0.02, r=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e

def pad(freqs, n):
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t + 0.3) for f in freqs)
    a = np.minimum(1, t / 0.25) * np.minimum(1, (n / SR - t) / 0.3)
    return s * a / len(freqs)

def kick(n):
    t = np.arange(n) / SR
    f = 50 + 70 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def hat(n, rng):
    return rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 60) * 0.25

def snare(n, rng):
    t = np.arange(n) / SR
    return (rng.standard_normal(n) * 0.5 + np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 18) * 0.5

def main(out, dur, seed=0):
    rng = np.random.default_rng(seed)
    bpm = [82, 86, 90, 94][seed % 4]
    root = 53 + [0, 2, -2, 3, 5][seed % 5]  # around F3
    loops = [
        [[0, 4, 7, 11], [-1, 2, 7, 10], [-3, 0, 5, 9], [-5, -1, 4, 7]],
        [[0, 3, 7, 10], [-4, 0, 3, 7], [-7, -3, 0, 4], [-2, 2, 5, 9]],
        [[0, 4, 7, 11], [-3, 0, 4, 7], [-8, -5, -1, 2], [-5, -1, 2, 5]],
    ]
    loop = loops[seed % len(loops)]
    beat = 60 / bpm
    N = int(dur * SR)
    mix = np.zeros(N + SR * 2)
    bar = int(4 * beat * SR)
    i = 0
    pos = 0
    while pos < N:
        ch = loop[i % 4]
        mix[pos:pos + bar] += 0.22 * pad([note(root + c) for c in ch], bar)
        bass = note(root + ch[0] - 12)
        bn = int(beat * 1.8 * SR)
        tt = np.arange(bn) / SR
        mix[pos:pos + bn] += 0.28 * np.sin(2 * np.pi * bass * tt) * env(bn, 0.01, 0.6)
        for b in range(8):
            p = pos + int(b * beat / 2 * SR)
            if b in (0, 5):
                k = kick(int(0.4 * SR)); mix[p:p + len(k)] += 0.55 * k
            if b in (2, 6):
                s = snare(int(0.25 * SR), rng); mix[p:p + len(s)] += 0.25 * s
            h = hat(int(0.08 * SR), rng); mix[p:p + len(h)] += 0.12 * h * (1 if b % 2 else 0.6)
        pos += bar
        i += 1
    mix = mix[:N]
    # low-pass-ish smoothing + vinyl noise
    k = np.ones(6) / 6
    mix = np.convolve(mix, k, mode="same")
    mix += rng.standard_normal(N) * 0.0025
    fade = int(1.2 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix[:int(0.15 * SR)] *= np.linspace(0, 1, int(0.15 * SR))
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.8
    st = np.stack([mix, np.roll(mix, 220)], axis=1)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)
