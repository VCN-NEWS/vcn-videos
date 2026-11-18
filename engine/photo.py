"""Module photo/clip : vidéos « Qui est… ? » à partir de la bibliothèque officielle."""
import os, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import v2
from v2 import *

LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bibliotheque")
CARD_W = 1000
CARD_H = int(CARD_W * 9 / 16)
_PH, _CLIP = {}, {}


def _bg_from(img):
    """Fond plein écran flouté et assombri à partir d'une image 16:9."""
    h = H
    w = int(img.width * h / img.height)
    big = img.resize((w, h), Image.BILINEAR)
    x0 = (w - W) // 2
    bg = big.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(28))
    dark = Image.new("RGB", (W, H), (18, 6, 34))
    return Image.blend(bg, dark, 0.55).convert("RGBA")


def photo(rel):
    if rel not in _PH:
        im = Image.open(os.path.join(LIB, rel)).convert("RGB")
        _PH[rel] = (im, _bg_from(im))
    return _PH[rel]


def clip(rel, slow=0.5):
    """Images d'un clip, ralenti (slow=0.5 -> 2x plus long)."""
    if rel not in _CLIP:
        path = os.path.join(LIB, rel)
        w, h = 1280, 720
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(raw) // (w * h * 3)
        frames = [Image.frombuffer("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]) for i in range(n)]
        _CLIP[rel] = (frames, slow, _bg_from(frames[n // 2]))
    return _CLIP[rel]


def framed(img, zoom=1.0, pan=(0.5, 0.5)):
    """Carte photo arrondie avec zoom lent (effet Ken Burns)."""
    iw, ih = img.size
    cw, ch = iw / zoom, ih / zoom
    x0 = (iw - cw) * pan[0]
    y0 = (ih - ch) * pan[1]
    crop = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((CARD_W, CARD_H), Image.BILINEAR).convert("RGBA")
    m = Image.new("L", (CARD_W * 2, CARD_H * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, CARD_W * 2 - 1, CARD_H * 2 - 1], 64, fill=255)
    crop.putalpha(m.resize((CARD_W, CARD_H), Image.LANCZOS))
    out = Image.new("RGBA", (CARD_W + 12, CARD_H + 12), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle([0, 0, CARD_W + 11, CARD_H + 11], 38, fill=(255, 255, 255, 70))
    out.alpha_composite(crop, (6, 6))
    return out


def name_chip(txt, sub=None, col=PINK):
    f = font("InterDisplay-Black", 52)
    f2 = font("Inter-SemiBold", 32)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = tmp.textbbox((0, 0), txt, font=f)[2]
    sw = tmp.textbbox((0, 0), sub, font=f2)[2] if sub else 0
    w = max(tw, sw) + 90
    h = 150 if sub else 100
    im = card_base(w, h, r=34, fill=(20, 8, 38, 240))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 18, 10, h - 18], fill=col + (255,))
    d.text((48, 18), txt, font=f, fill=WHITE)
    if sub:
        d.text((48, 90), sub, font=f2, fill=MUTED)
    return im


class PhotoVideo(Video):
    """segments : (index_phrase, LABEL, headline_img|None, media, (nom, sous-titre)|None)
    media = ("photo", "personnages/xxx.jpg", pan) ou ("clip", "clips/xxx.mp4")"""

    def __init__(self, key, text, audio_dur, segments, theme_col=PINK, **kw):
        segs = [(s[0], s[1], s[2], None) for s in segments]
        super().__init__(key, text, audio_dur, segs, theme_col, **kw)
        self.media = [s[3] for s in segments]
        self.chips = [s[4] for s in segments]
        self._chip_cache = {}

    def _media(self, i, lt, dur):
        kind, rel = self.media[i][0], self.media[i][1]
        if kind == "clip":
            frames, slow, bgi = clip(rel)
            n = len(frames)
            k = min(n - 1, int(lt * FPS * slow))
            return frames[k], bgi, 1.0 + 0.04 * lt / max(dur, 0.1), (0.5, 0.5)
        im, bgi = photo(rel)
        pan = self.media[i][2] if len(self.media[i]) > 2 else (0.5, 0.5)
        z = 1.0 + 0.10 * clamp(lt / max(dur, 0.1))
        return im, bgi, z, pan

    def frame(self, t):
        # segment courant
        cur = 0
        for i, (a, b) in enumerate(self.seg_times):
            if a <= t < b or (i == len(self.seg_times) - 1 and t >= a):
                cur = i
                break
        a, b = self.seg_times[cur]
        lt, dur = t - a, b - a
        if cur == 0:
            lt += 0.7
            dur += 0.7
        last = cur == len(self.segments) - 1
        tout = None if last else dur - 0.12
        img, bgi, z, pan = self._media(cur, lt, dur)
        fr = bgi.copy()
        # fondu de fond depuis le segment précédent
        if cur > 0 and lt < 0.35:
            pimg, pbg, _, _ = self._media(cur - 1, 99, 99)
            fr = Image.blend(pbg, fr, clamp(lt / 0.35))
        _, label, hl, _ = self.segments[cur]
        if hl is not None:
            place(fr, hl, W / 2, 330, lt, 0.0, tout, scale_from=0.7, rise=20)
        place(fr, shadowed(framed(img, z, pan), blur=24, off=12), W / 2, 880, lt, 0.0, tout, scale_from=0.9)
        ch = self.chips[cur]
        if ch:
            if ch not in self._chip_cache:
                self._chip_cache[ch] = name_chip(*ch, col=self.col)
            c = self._chip_cache[ch]
            place(fr, c, 40 + c.width / 2, 880 + CARD_H / 2 + 40, lt, 0.25, tout, scale_from=0.9, rise=20)
        pct = clamp(t / (self.lead + self.audio_dur)) * 100
        progress_bar(fr, label, pct, self.col)
        for g in self.groups:
            if g[0][1] - 0.05 <= t < g[-1][2] + 0.12:
                idx = max([k for k, w in enumerate(g) if w[1] <= t + 0.03] or [0])
                caption(fr, [w[0].upper() for w in g], idx, y=1530)
                break
        return fr
