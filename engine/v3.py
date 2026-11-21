"""Format v3 « plein écran » : images officielles en plein cadre, un plan toutes les ~2 s,
coupes « punch » (zoom + flash), voix dès la 1re image, titres qui claquent, écran partagé pour les duels.

Plans : (index_phrase, fraction_de_la_phrase, media, titre|None, puce|None)
  media = ("photo", rel, fx, fy, zoom)   recadrage 9:16 centré sur (fx, fy) ; zoom 1 = toute la hauteur
        | ("clip", rel, fx)
        | ("split", rel_haut, (fx, fy), rel_bas, (fx, fy), "NOM HAUT", "NOM BAS")
        | ("card", rel_fond, fx, builder)   carte animée (builder(p), p 0→1) sur une photo assombrie
"""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import v2
from v2 import *
from cover import _sticker, _title_line

LIB = os.path.join(os.path.dirname(D), "bibliotheque")
_IMG, _CLIP = {}, {}


def _src(rel):
    if rel not in _IMG:
        im = Image.open(os.path.join(LIB, rel)).convert("RGB")
        im = ImageEnhance.Color(im).enhance(1.15)
        im = ImageEnhance.Contrast(im).enhance(1.08)
        _IMG[rel] = im
    return _IMG[rel]


_DARK = {}


def _src_dark(rel):
    if rel not in _DARK:
        im = _src(rel).filter(ImageFilter.GaussianBlur(5))
        _DARK[rel] = Image.blend(im, Image.new("RGB", im.size, (16, 6, 30)), 0.5)
    return _DARK[rel]


def _crop(im, fx, fy, zoom, out_w=W, out_h=H, kb=1.0):
    """Recadre im au format out_w:out_h autour de (fx, fy). kb = zoom Ken Burns supplémentaire."""
    iw, ih = im.size
    ar = out_w / out_h
    ch = ih / (zoom * kb)
    cw = ch * ar
    if cw > iw:
        cw, ch = iw / kb, iw / kb / ar
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    return im.resize((out_w, out_h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def _clip_frames(rel):
    if rel not in _CLIP:
        # garde le format d'origine (certains clips sont carrés 1920×1920 : ne pas les écraser en 16:9)
        dims = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                               "-of", "csv=p=0", os.path.join(LIB, rel)], capture_output=True, text=True).stdout.split(",")
        w = 1920
        h = int(round(1920 * int(dims[1]) / int(dims[0]) / 2) * 2)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(LIB, rel), "-vf", f"scale={w}:{h}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(raw) // (w * h * 3)
        _CLIP[rel] = [Image.frombuffer("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]) for i in range(n)]
    return _CLIP[rel]


_SHADE = None


def _shade():
    global _SHADE
    if _SHADE is None:
        y = np.linspace(0, 1, H)[:, None]
        a = np.clip((0.22 - y) / 0.22, 0, 1) * 170 + np.clip((y - 0.62) / 0.38, 0, 1) ** 1.2 * 200
        lay = np.zeros((H, W, 4), np.uint8)
        lay[..., 0], lay[..., 1], lay[..., 2] = 14, 4, 28
        lay[..., 3] = np.repeat(a, W, axis=1).astype(np.uint8)
        _SHADE = Image.fromarray(lay, "RGBA")
    return _SHADE


def _label(txt, col):
    f = font("InterDisplay-Black", 64)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw, th, b = text_size(tmp, txt, f)
    im = card_base(tw + 70, th + 40, r=30, fill=col + (235,))
    ImageDraw.Draw(im).text((35 - b[0], 20 - b[1]), txt, font=f, fill=(255, 255, 255, 255))
    return im


class FullVideo(Video):
    def __init__(self, key, text, audio_dur, shots, theme_col=PINK, lead=0.05, tail=1.6, labels=None):
        sent_idx = sorted({s[0] for s in shots})
        super().__init__(key, text, audio_dur, [(i, "", None, None) for i in sent_idx], theme_col, lead=lead, tail=tail)
        self.shots = shots
        self.labels = labels or {}
        starts = []
        for si, fr_, *_ in shots:
            a, b = self.st[si]
            starts.append(a - 0.12 + fr_ * (b - a))
        starts[0] = 0.0
        self.seg_times = [(starts[i], starts[i + 1] if i + 1 < len(starts) else self.total) for i in range(len(shots))]
        self.segments = shots
        self._cache = {}

    def _title(self, txt):
        if txt not in self._cache:
            self._cache[txt] = _title_line(txt, 150, maxw=980)
        return self._cache[txt]

    def _chip(self, txt):
        k = ("chip", txt)
        if k not in self._cache:
            self._cache[k] = _sticker(txt, size=54, angle=-3)
        return self._cache[k]

    def _media(self, i, lt, dur):
        m = self.shots[i][2]
        kb = 1.0 + 0.07 * clamp(lt / max(dur, 0.1))
        if m[0] == "photo":
            _, rel, fx, fy, zoom = m
            return _crop(_src(rel), fx, fy, zoom, kb=kb).convert("RGBA")
        if m[0] == "clip":
            fr = _clip_frames(m[1])
            k = min(len(fr) - 1, int(lt * FPS * 0.5))
            return _crop(fr[k], m[2], 0.5, 1.0, kb=kb).convert("RGBA")
        if m[0] == "card":
            _, rel, fx, builder = m
            out = _crop(_src_dark(rel), fx, 0.5, 1.0, kb=kb).convert("RGBA")
            p = clamp((lt - 0.05) / max(1.0, min(dur * 0.6, 2.5)))
            place(out, shadowed(builder(p)), W / 2, 930, lt, 0.0, None, scale_from=0.85)
            return out
        # écran partagé
        _, r1, (x1, y1), r2, (x2, y2), n1, n2 = m
        out = Image.new("RGBA", (W, H))
        hh = H // 2
        out.paste(_crop(_src(r1), x1, y1, 2.0, W, hh, kb), (0, 0))
        out.paste(_crop(_src(r2), x2, y2, 2.0, W, hh, kb), (0, hh))
        d = ImageDraw.Draw(out)
        d.rectangle([0, hh - 5, W, hh + 5], fill=(255, 255, 255, 255))
        for txt, y, col in ((n1, hh - 150, PINK), (n2, hh + 40, VIOLET)):
            lab = self._cache.setdefault(("lab", txt), _label(txt, col))
            out.alpha_composite(lab, ((W - lab.width) // 2, y))
        ou = self._cache.setdefault("ou", _sticker("OU", bgcol=(255, 214, 92), size=70, angle=0))
        out.alpha_composite(ou, ((W - ou.width) // 2, hh - ou.height // 2 - 50 + 50))
        return out

    def frame(self, t):
        cur = 0
        for i, (a, b) in enumerate(self.seg_times):
            if a <= t < b or (i == len(self.seg_times) - 1 and t >= a):
                cur = i
                break
        a, b = self.seg_times[cur]
        lt, dur = t - a, b - a
        img = self._media(cur, lt, dur)
        # coupe « punch » : léger zoom arrière + flash
        if cur > 0 and lt < 0.18:
            p = ease_out_cubic(lt / 0.18)
            s = 1.10 - 0.10 * p
            big = img.resize((int(W * s), int(H * s)), Image.BILINEAR)
            img = big.crop(((big.width - W) // 2, (big.height - H) // 2, (big.width - W) // 2 + W, (big.height - H) // 2 + H))
        fr = img
        fr.alpha_composite(_shade())
        if cur > 0 and lt < 0.12:
            fl = Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - lt / 0.12))))
            fr.alpha_composite(fl)
        si, _, m, title, chip = self.shots[cur]
        if title:
            ti = self._title(title)
            p = ease_out_back(clamp(lt / 0.22)) if lt < 0.22 else 1.0
            if p < 1.0:
                ti2 = ti.resize((max(1, int(ti.width * (0.6 + 0.4 * p))), max(1, int(ti.height * (0.6 + 0.4 * p)))), Image.BILINEAR)
            else:
                ti2 = ti
            y = 250 if m[0] != "split" else 230
            fr.alpha_composite(ti2, ((W - ti2.width) // 2, y - ti2.height // 2 + 60))
        if chip:
            c = self._chip(chip)
            if lt > 0.15:
                fr.alpha_composite(c, (60, 1240))
        label = self.labels.get(cur, None)
        if label is None:
            label = [v for k, v in sorted(self.labels.items()) if k <= cur][-1:] or [""]
            label = label[0]
        pct = clamp(t / (self.lead + self.audio_dur)) * 100
        progress_bar(fr, label, pct, self.col)
        for g in self.groups:
            if g[0][1] - 0.05 <= t < g[-1][2] + 0.12:
                idx = max([k for k, w in enumerate(g) if w[1] <= t + 0.03] or [0])
                caption(fr, [w[0].upper() for w in g], idx, y=1440)
                break
        return fr
