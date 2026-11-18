"""Couvertures, musique et mixage final."""
import sys, os, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
from PIL import Image, ImageDraw
import videos
from v2 import *

SR = 44100


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)


def bpf(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def hpf(x, f):
    return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)


def music(total, hits, seed=1, root=45):
    rng = np.random.default_rng(seed)
    N = int(total * SR)
    mus, dr = np.zeros(N), np.zeros(N)

    def add(buf, s, t):
        i = int(t * SR)
        if i >= N:
            return
        j = min(N, i + len(s))
        buf[i:j] += s[: j - i]

    def saw(f, d):
        t = np.arange(int(d * SR)) / SR
        return 2 * ((t * f) % 1) - 1

    note = lambda n: 440 * 2 ** ((n - 69) / 12)
    beat = 60 / 112
    prog = [[0, 3, 7], [-4, 0, 3], [-9, -5, -2], [-2, 2, 5]]
    t, k = 0.0, 0
    while t < total:
        ch = [root + 12 + x for x in prog[k % 4]]
        r = root + prog[k % 4][0] - 12 + 12
        pad = sum(saw(note(n), beat * 4) for n in ch) * 0.02
        pad = lp(pad, 1200)
        add(mus, pad, t)
        for i in range(8):
            b = lp(saw(note(r), beat / 2 * 0.85), 420) * 0.14 * np.exp(-np.arange(int(beat / 2 * 0.85 * SR)) / (0.1 * SR))
            add(mus, b, t + i * beat / 2)
        t += beat * 4
        k += 1
    t, i = 0.0, 0
    while t < total:
        L = int(0.3 * SR)
        tt = np.arange(L) / SR
        f = 48 + 90 * np.exp(-tt * 32)
        add(dr, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 10) * 0.5, t)
        if i % 2:
            n = bpf(rng.standard_normal(int(0.18 * SR)), 900, 4000) * np.exp(-np.arange(int(0.18 * SR)) / (0.045 * SR)) * 0.25
            add(dr, n, t)
        for h in (0, 0.5):
            hn = hpf(rng.standard_normal(int(0.04 * SR)), 7000) * np.exp(-np.arange(int(0.04 * SR)) / (0.01 * SR)) * 0.08
            add(dr, hn, t + h * beat)
        t += beat
        i += 1
    out = mus + dr
    for h in hits:  # whoosh + pop à chaque changement de carte
        L = int(0.4 * SR)
        nz = rng.standard_normal(L)
        tt = np.arange(L) / L
        w = np.zeros(L)
        for a, b in [(0, .33), (.33, .66), (.66, 1)]:
            sl = slice(int(a * L), int(b * L))
            fc = 500 + 3500 * (a + b) / 2
            w[sl] = bpf(nz, fc * .6, fc * 1.6)[sl]
        add(out, w * np.sin(np.pi * tt) ** 2 * 0.2, max(0, h - 0.25))
        L2 = int(0.07 * SR)
        tt = np.arange(L2) / SR
        add(out, np.sin(2 * np.pi * np.cumsum(1100 - 4000 * tt) / SR) * np.exp(-tt * 45) * 0.15, h + 0.08)
    fade = int(1.5 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out / (np.abs(out).max() + 1e-9)


def mix(key, v, video_in, out):
    hits = [a for a, b in v.seg_times]
    m = music(v.total, hits, seed=sum(ord(c) for c in key))
    voice = f"{D}/voix_{key}.mp3"
    mpath = f"{D}/music_{key}.wav"
    if os.path.exists(voice):
        wavfile.write(mpath, SR, (m * 0.16 * 32767).astype(np.int16))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video_in, "-i", voice, "-i", mpath, "-filter_complex",
                        f"[1:a]adelay={int(v.lead*1000)}|{int(v.lead*1000)},apad=pad_dur=5,loudnorm=I=-15:TP=-1.5[vo];[2:a]volume=1.0,apad=pad_dur=5[mu];[vo][mu]amix=inputs=2:duration=longest:normalize=0[a]",
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(v.total), out], check=True)
    else:
        wavfile.write(mpath, SR, (m * 0.6 * 32767).astype(np.int16))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video_in, "-i", mpath, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)


COVERS = {
    "A": (["GTA 6", "DÉJÀ MAL", "NOTÉ ?!"], lambda: score_badge("6.5", "Note des joueurs · Metacritic"), (255, 150, 110), (255, 60, 120)),
    "B": (["210 GO", "SUR TA", "PS5 ?!"], lambda: storage_card(1.0), (255, 230, 120), (255, 140, 60)),
    "C": (["5 BOUTIQUES", "FERMÉES", "POUR TOI"], lambda: map_pins_card(1.0), (255, 150, 110), (255, 60, 140)),
    "D": (["ILS JOUENT", "AVANT TOI", "AUJOURD’HUI"], lambda: timeline_card(5), (190, 160, 255), (255, 92, 170)),
    "notes": (["GTA 6", "À 99 !", "MAIS…"], lambda: videos.record_badge(1.0), (255, 230, 120), (255, 150, 60)),
}


def cover(key):
    lines, mk, c1, c2 = COVERS[key]
    fr = bg(3.0)
    y = 230
    for l in lines:
        t = headline(l, c1, c2, maxw=1000, size=190)
        fr.alpha_composite(t, ((W - t.width) // 2, y - 60))
        y += 190
    c = shadowed(mk())
    fr.alpha_composite(c, ((W - c.width) // 2, 1020 + (560 - c.height) // 2))
    ch = chip("GTA 6 · INFO", col=PINK, size=40, h=86)
    fr.alpha_composite(ch, ((W - ch.width) // 2, 110))
    fr.convert("RGB").save(f"{D}/couverture_{key}.jpg", quality=92)


if __name__ == "__main__":
    mode, keys = sys.argv[1], sys.argv[2].split(",")
    for k in keys:
        if mode == "cover":
            cover(k)
        elif mode == "mix":
            v = videos.VIDEOS[k]()
            mix(k, v, f"{D}/silent_{k}.mp4", f"{D}/GTA6_{k}.mp4")
