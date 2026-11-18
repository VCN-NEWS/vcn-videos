"""Moteur v2 : format reel d'actu (barre de progression, sous-titres mot à mot, cartes)."""
import math, os, re, subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import render as R
from render import (W, H, FPS, font, clamp, ease_out_cubic, ease_out_back, ease_in_out, card_base, shadowed,
                    text_size, draw_center, gradient_text, headline, chip, calendar_card, clock_card, timeline_card,
                    big_stat_card, xbox_card, ps_card, donut_card, preload_card, WHITE, MUTED, PINK, VIOLET, GOLD, ACCENT)

D = os.path.dirname(os.path.abspath(__file__))
GREEN = (120, 230, 150)
RED = (255, 90, 110)
BLUE = (110, 200, 255)

# ---------------- fond ----------------
TINT = None


def tint():
    global TINT
    if TINT is None:
        y, x = np.mgrid[0:H, 0:W]
        r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.45) / H) ** 2)
        a = np.clip(0.35 + r * 0.9, 0, 0.88)
        arr = np.zeros((H, W, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = 34, 10, 60
        arr[..., 3] = (a * 255).astype(np.uint8)
        TINT = Image.fromarray(arr, "RGBA")
    return TINT


def bg(gt):
    img = R.background(gt, R.camera, [(0, "night")])
    img.alpha_composite(tint())
    return img


# ---------------- barre de progression (haut) ----------------
def progress_bar(fr, label, pct, col=PINK):
    w, h = 900, 96
    x0, y0 = (W - w) // 2, 120
    d = ImageDraw.Draw(fr)
    f = font("InterDisplay-Black", 38)
    d.ellipse([x0, y0 + 4, x0 + 40, y0 + 44], fill=col + (255,))
    d.ellipse([x0 + 12, y0 + 16, x0 + 28, y0 + 32], fill=(255, 255, 255, 255))
    d.text((x0 + 56, y0 + 2), label, font=f, fill=WHITE)
    t = f"{int(pct)}%"
    tw = d.textbbox((0, 0), t, font=font("Inter-Bold", 32))[2]
    d.text((x0 + w - tw, y0 + 8), t, font=font("Inter-Bold", 32), fill=(255, 255, 255, 200))
    yb = y0 + 66
    d.rounded_rectangle([x0, yb, x0 + w, yb + 16], 8, fill=(255, 255, 255, 50))
    xe = x0 + max(16, w * pct / 100)
    d.rounded_rectangle([x0, yb, xe, yb + 16], 8, fill=col + (255,))
    d.ellipse([xe - 16, yb - 8, xe + 16, yb + 24], fill=(255, 255, 255, 255))


# ---------------- sous-titres mot à mot ----------------
CAP_F = font("InterDisplay-Black", 92)


def caption(fr, words, idx, y=1470):
    """words: liste de mots du groupe ; idx: mot courant (dégradé GTA VI)."""
    if not words:
        return
    d = ImageDraw.Draw(fr)
    space = 26
    f, scale = CAP_F, 1.0
    sizes = [d.textbbox((0, 0), w_, font=f, anchor="ls") for w_ in words]
    widths = [b[2] - b[0] for b in sizes]
    total = sum(widths) + space * (len(words) - 1)
    if total > 980:
        scale = 980 / total
        f = font("InterDisplay-Black", int(92 * scale))
        sizes = [d.textbbox((0, 0), w_, font=f, anchor="ls") for w_ in words]
        widths = [b[2] - b[0] for b in sizes]
        total = sum(widths) + space * scale * (len(words) - 1)
    yb = y + int(70 * scale)
    x = (W - total) / 2
    sw = int(9 * scale) + 1
    for i, (w_, b) in enumerate(zip(words, sizes)):
        if i == idx:
            d.text((x - b[0], yb), w_, font=f, anchor="ls", fill=(10, 4, 20, 255), stroke_width=sw, stroke_fill=(10, 4, 20, 255))
            pad = 4
            ww, hh = b[2] - b[0] + pad * 2, b[3] - b[1] + pad * 2
            m = Image.new("L", (ww, hh), 0)
            ImageDraw.Draw(m).text((pad - b[0], pad - b[1]), w_, font=f, anchor="ls", fill=255)
            fr.paste(gta_gradient(ww, hh), (int(x) - pad, int(yb + b[1]) - pad), m)
        else:
            d.text((x - b[0], yb), w_, font=f, anchor="ls", fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=(10, 4, 20, 255))
        x += widths[i] + space * scale


_GRAD = {}


def gta_gradient(w, h):
    key = (w, h)
    if key not in _GRAD:
        stops = [(0.0, (255, 196, 120)), (0.45, (255, 92, 160)), (1.0, (150, 80, 230))]
        t = np.linspace(0, 1, h)[:, None]
        cols = np.zeros((h, 3))
        for (a, ca), (b_, cb) in zip(stops[:-1], stops[1:]):
            msk = (t[:, 0] >= a) & (t[:, 0] <= b_)
            u = ((t[msk, 0] - a) / (b_ - a))[:, None]
            cols[msk] = np.array(ca) * (1 - u) + np.array(cb) * u
        arr = np.repeat(cols[:, None, :], w, axis=1).astype(np.uint8)
        _GRAD[key] = Image.fromarray(arr, "RGB").convert("RGBA")
    return _GRAD[key]


# ---------------- alignement texte / audio ----------------
def split_sentences(text):
    s = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [x for x in s if x]


def silences(audio):
    out = subprocess.run(["ffmpeg", "-i", audio, "-af", "silencedetect=noise=-32dB:d=0.16", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(st, en))


def align(sentences, total, sil=None, lead=0.0):
    """Renvoie [(start, end)] par phrase."""
    lens = [len(s) + 8 for s in sentences]
    cum = np.cumsum([0] + lens) / sum(lens)
    speech0, speech1 = 0.05, total - 0.1
    if sil:
        if sil[0][0] < 0.05:
            speech0 = sil[0][1]
        if sil[-1][1] >= total - 0.05:
            speech1 = sil[-1][0]
    b = list(speech0 + cum * (speech1 - speech0))
    if sil:
        mids = [((s + e) / 2, e - s) for s, e in sil if s > speech0 + 0.1 and e < speech1 - 0.1]
        used = set()
        for i in range(1, len(b) - 1):
            cands = [(abs(m - b[i]), j) for j, (m, dur) in enumerate(mids) if abs(m - b[i]) < 1.6 and j not in used]
            if cands:
                _, j = min(cands)
                used.add(j)
                b[i] = mids[j][0]
        for i in range(1, len(b)):
            b[i] = max(b[i], b[i - 1] + 0.3)
    return [(b[i] + lead, b[i + 1] + lead) for i in range(len(sentences))]


def align_clauses(sentences, total, sil, lead=0.0):
    """Découpe en propositions (ponctuation) et cale chaque frontière sur une pause réelle (DP monotone).
    Renvoie (liste de (phrase_idx, texte, start, end))."""
    clauses = []
    for si, s in enumerate(sentences):
        parts = re.split(r"(?<=[,;:])\s+", s)
        for p in parts:
            if p:
                clauses.append((si, p))
    lens = np.array([len(c[1]) + 6 for c in clauses], float)
    speech0 = sil[0][1] if sil and sil[0][0] < 0.05 else 0.05
    speech1 = sil[-1][0] if sil and sil[-1][1] >= total - 0.05 else total - 0.1
    est = speech0 + np.cumsum(lens)[:-1] / lens.sum() * (speech1 - speech0)
    mids = [(a + b) / 2 for a, b in sil if a > speech0 + 0.1 and b < speech1 - 0.1] if sil else []
    n, m = len(est), len(mids)
    INF = 1e9
    # dp[i][j] : coût pour placer les i premières frontières, la i-ème sur la pause j-1 (j=0 : pas de pause)
    best = [0.0] + [INF] * m  # coût minimal en ayant utilisé jusqu'à la pause j
    choice = []
    prev_cost = np.zeros(m + 1)  # coût minimal avec dernière pause utilisée <= j
    bounds = []
    # algorithme glouton monotone avec fenêtre, suffisant ici
    prev = speech0
    j0 = 0
    for i in range(n):
        rem = lens[i:].sum()
        e = prev + lens[i] / rem * (speech1 - prev)
        minlen = 0.055 * lens[i]
        cands = [(abs(mids[j] - e), j) for j in range(j0, m) if abs(mids[j] - e) < 1.3 and mids[j] > prev + minlen]
        if cands:
            _, j = min(cands)
            bounds.append(mids[j])
            j0 = j + 1
        else:
            bounds.append(e)
        prev = bounds[-1]
    b = [speech0] + bounds + [speech1]
    for i in range(1, len(b)):
        b[i] = max(b[i], b[i - 1] + 0.25)
    return [(clauses[i][0], clauses[i][1], b[i] + lead, b[i + 1] + lead) for i in range(len(clauses))]


def align_dp(sentences, total, sil, lead=0.0):
    """Alignement par programmation dynamique : groupes de propositions <-> groupes de segments parlés."""
    clauses = []
    for si, s in enumerate(sentences):
        for p in re.split(r"(?<=[,;:])\s+", s):
            if p:
                clauses.append((si, p))
    # segments parlés
    voiced, cur = [], 0.0
    for a, b in sil:
        if a - cur > 0.08:
            voiced.append((cur, a))
        cur = b
    if total - cur > 0.08:
        voiced.append((cur, total))
    ch = np.array([len(c[1]) for c in clauses], float)
    du = np.array([b - a for a, b in voiced])
    rate = ch.sum() / du.sum()
    n, m = len(ch), len(du)
    INF = 1e18
    dp = np.full((n + 1, m + 1), INF)
    bk = {}
    dp[0, 0] = 0
    K = 4
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            for a in range(1, min(K, i) + 1):
                c = ch[i - a:i].sum()
                for b in range(1, min(K, j) + 1):
                    if dp[i - a, j - b] >= INF:
                        continue
                    d = du[j - b:j].sum()
                    cost = (c - rate * d) ** 2 / (c + 10) + 3.0 * (a - 1) + 3.0 * (b - 1)
                    v = dp[i - a, j - b] + cost
                    if v < dp[i, j]:
                        dp[i, j] = v
                        bk[(i, j)] = (a, b)
    i, j = n, m
    groups = []
    while i > 0:
        a, b = bk[(i, j)]
        groups.append((i - a, i, j - b, j))
        i, j = i - a, j - b
    groups.reverse()
    out = []
    for c0, c1, v0, v1 in groups:
        st, en = voiced[v0][0], voiced[v1 - 1][1]
        cs = ch[c0:c1]
        cum = np.concatenate([[0], np.cumsum(cs)]) / cs.sum()
        for k in range(c1 - c0):
            out.append((clauses[c0 + k][0], clauses[c0 + k][1], st + cum[k] * (en - st) + lead, st + cum[k + 1] * (en - st) + lead))
    return out


def word_times(sentence, st, en):
    words = sentence.split()
    lens = np.array([len(w) + 3 for w in words], float)
    cum = np.cumsum(np.concatenate([[0], lens])) / lens.sum()
    return [(w, st + cum[i] * (en - st), st + cum[i + 1] * (en - st)) for i, w in enumerate(words)]


def chunk_words(wt, maxw=3, maxc=16):
    groups, cur = [], []
    for w in wt:
        cur.append(w)
        n = sum(len(x[0]) for x in cur)
        if len(cur) >= maxw or n >= maxc or w[0][-1] in ".!?,:…":
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


# ---------------- éléments graphiques ----------------
def place(fr, img, cx, cy, t, t_in=0.0, t_out=None, scale_from=0.85, rise=40):
    R.place(fr, img, cx, cy, t_in, t, t_out, scale_from=scale_from, rise=rise)


def card(w, h):
    return card_base(w, h)


def bars_card(rows, p, title=None, unit="", maxv=None, hl=None):
    """rows: [(label, value, color, value_text)]"""
    w = 900
    h = 140 + len(rows) * 120
    im = card(w, h)
    d = ImageDraw.Draw(im)
    y = 50
    if title:
        d.text((56, 40), title, font=font("Inter-SemiBold", 36), fill=MUTED)
        y = 110
    mv = maxv or max(r[1] for r in rows)
    for i, (lab, v, col, vt) in enumerate(rows):
        a = ease_out_cubic(clamp(p * len(rows) * 0.9 - i * 0.7))
        d.text((56, y), lab, font=font("Inter-Bold", 38), fill=WHITE)
        bw = (w - 112) * (v / mv) * a
        d.rounded_rectangle([56, y + 52, w - 56, y + 84], 16, fill=(255, 255, 255, 30))
        if bw > 32:
            d.rounded_rectangle([56, y + 52, 56 + bw, y + 84], 16, fill=col + (255,))
        if a > 0.3:
            tw = d.textbbox((0, 0), vt, font=font("InterDisplay-Black", 40))[2]
            d.text((w - 56 - tw, y - 4), vt, font=font("InterDisplay-Black", 40), fill=col + (int(255 * a),))
        y += 120
    return im


def list_card(rows, p, title=None, icon="lock"):
    """rows: [(titre, sous-titre, couleur)] apparaissant un par un."""
    w = 900
    h = 120 + len(rows) * 116 + (60 if title else 0)
    im = card(w, h)
    d = ImageDraw.Draw(im)
    y = 56
    if title:
        d.text((56, 44), title, font=font("Inter-SemiBold", 36), fill=MUTED)
        y = 120
    n = p * (len(rows) + 0.5)
    for i, (t1, t2, col) in enumerate(rows):
        a = ease_out_cubic(clamp(n - i))
        if a <= 0:
            continue
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        cx, cy = 92, y + 40
        dl.ellipse([cx - 36, cy - 36, cx + 36, cy + 36], fill=col + (60,), outline=col + (255,), width=4)
        if icon == "lock":
            dl.rounded_rectangle([cx - 16, cy - 4, cx + 16, cy + 20], 5, fill=col + (255,))
            dl.arc([cx - 12, cy - 24, cx + 12, cy + 4], 180, 360, fill=col + (255,), width=6)
        elif icon == "check":
            dl.line([(cx - 16, cy), (cx - 4, cy + 13), (cx + 17, cy - 12)], fill=col + (255,), width=8, joint="curve")
        else:
            dl.text((cx, cy), icon[i] if isinstance(icon, list) else str(i + 1), font=font("InterDisplay-Black", 38), fill=col + (255,), anchor="mm")
        dl.text((150, y + 4), t1, font=font("Inter-Bold", 42), fill=WHITE)
        dl.text((150, y + 56), t2, font=font("Inter-Medium", 32), fill=MUTED)
        dx = int((1 - a) * 50)
        layer = layer.transform(layer.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0))
        layer.putalpha(layer.split()[3].point(lambda q: int(q * a)))
        im.alpha_composite(layer)
        y += 116
    return im


def score_badge(score, sub, col=(255, 150, 60), p=1.0, stamp=0.0):
    w, h = 560, 560
    im = card(w, h)
    d = ImageDraw.Draw(im)
    s = 330
    x0, y0 = (w - s) // 2, 50
    d.rounded_rectangle([x0, y0, x0 + s, y0 + s], 40, fill=col + (255,))
    val = score
    draw_center(d, w / 2, y0 + 80, val, font("InterDisplay-Black", 160), (20, 12, 30))
    draw_center(d, w / 2, y0 + s + 40, sub, font("Inter-SemiBold", 40), MUTED)
    if stamp > 0:
        st = Image.new("RGBA", (520, 150), (0, 0, 0, 0))
        ds = ImageDraw.Draw(st)
        ds.rounded_rectangle([6, 6, 514, 144], 20, outline=RED + (255,), width=10)
        draw_center(ds, 260, 38, "SUPPRIMÉE", font("InterDisplay-Black", 84), RED)
        st = st.rotate(-14, expand=True, resample=Image.BICUBIC)
        k = 1.6 - 0.6 * ease_out_cubic(stamp)
        st = st.resize((int(st.width * k), int(st.height * k)), Image.BILINEAR)
        st.putalpha(st.split()[3].point(lambda q: int(q * clamp(stamp * 3))))
        im.alpha_composite(st, ((w - st.width) // 2, (h - st.height) // 2 - 20)) if st.width < w else None
        if st.width >= w:
            big = Image.new("RGBA", (max(w, st.width), max(h, st.height)), (0, 0, 0, 0))
            big.alpha_composite(im, ((big.width - w) // 2, (big.height - h) // 2))
            big.alpha_composite(st, ((big.width - st.width) // 2, (big.height - st.height) // 2 - 20))
            return big
    return im


def users_card(p):
    w, h = 900, 440
    im = card(w, h)
    d = ImageDraw.Draw(im)
    d.text((56, 44), "Notes d’utilisateurs", font=font("Inter-SemiBold", 36), fill=MUTED)
    for i in range(5):
        a = ease_out_back(clamp(p * 6 - i * 0.6))
        if a <= 0:
            continue
        cx, cy = 130 + i * 160, 200
        r = 56 * a
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 46, 120, 255), outline=VIOLET + (255,), width=4)
        d.ellipse([cx - r * 0.38, cy - r * 0.62, cx + r * 0.38, cy + r * 0.12], fill=(220, 210, 255, 255))
        d.pieslice([cx - r * 0.7, cy + r * 0.1, cx + r * 0.7, cy + r * 1.2], 180, 360, fill=(220, 210, 255, 255))
    a = clamp(p * 3 - 1.6)
    if a > 0:
        draw_center(d, w / 2, 300, "5 joueurs · 0 avis écrit", font("InterDisplay-Black", 56), (255, 200, 90, int(255 * a)))
    return im


def gauge_card(p, value=0.76, label="> 96 sur Metacritic", sub="Probabilité selon les paris en ligne"):
    S = 2
    w, h = 900, 560
    im = card(w, h)
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    cx, cy, Rr = w * S / 2, 330 * S, 220 * S
    d.arc([cx - Rr, cy - Rr, cx + Rr, cy + Rr], 180, 360, fill=(255, 255, 255, 40), width=46 * S)
    v = value * ease_in_out(p)
    if v > 0.01:
        d.arc([cx - Rr, cy - Rr, cx + Rr, cy + Rr], 180, 180 + 180 * v, fill=(120, 230, 150, 255), width=46 * S)
    draw_center(d, cx, cy - 130 * S, f"{int(round(v * 100))} %", font("InterDisplay-Black", 110 * S), (255, 255, 255))
    draw_center(d, cx, cy + 40 * S, label, font("Inter-Bold", 46 * S), (120, 230, 150))
    draw_center(d, cx, cy + 110 * S, sub, font("Inter-Medium", 32 * S), (200, 190, 230))
    im.alpha_composite(big.resize((w, h), Image.LANCZOS))
    return im


def versus_card(p):
    w, h = 900, 520
    im = card(w, h)
    d = ImageDraw.Draw(im)
    a = ease_out_back(clamp(p * 3))
    for i, (name, sc, col) in enumerate([("GTA 4", "98", GOLD), ("GTA 6", "?", PINK)]):
        cx = 220 + i * 460
        s = int(260 * a)
        if s < 4:
            continue
        d.rounded_rectangle([cx - s / 2, 90, cx + s / 2, 90 + s], 36, fill=col + (255,))
        draw_center(d, cx, 90 + s * 0.2, sc, font("InterDisplay-Black", max(10, int(150 * a))), (20, 12, 30))
        draw_center(d, cx, 380, name, font("InterDisplay-Black", 56), WHITE)
    draw_center(d, w / 2, 170, "VS", font("InterDisplay-Black", 90), (255, 255, 255, int(255 * clamp(p * 3 - 1))))
    return im


def comment_card(prompt, p, typed=""):
    w, h = 900, 400
    im = card(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([w / 2 - 34, 46, w / 2 + 34, 96], 14, outline=GOLD + (255,), width=6)
    d.polygon([(w / 2 - 14, 94), (w / 2 + 2, 94), (w / 2 - 16, 114)], fill=GOLD + (255,))
    draw_center(d, w / 2, 140, prompt, font("InterDisplay-Bold", 54), WHITE)
    d.rounded_rectangle([70, 250, w - 70, 340], 45, fill=(44, 28, 80, 255), outline=(255, 255, 255, 60), width=2)
    n = int(len(typed) * clamp(p * 2))
    cur = "|" if int(p * 8) % 2 == 0 else ""
    d.text((110, 272), (typed[:n] + cur) if typed else "Écris ici…", font=font("Inter-SemiBold", 40), fill=(255, 255, 255, 230))
    return im


def storage_card(p, used=210, total=667):
    S = 2
    w, h = 900, 520
    im = card(w, h)
    d = ImageDraw.Draw(im)
    d.text((56, 44), "PS5 standard · espace utilisable", font=font("Inter-SemiBold", 36), fill=MUTED)
    x0, y0, x1, y1 = 56, 130, w - 56, 230
    d.rounded_rectangle([x0, y0, x1, y1], 30, fill=(255, 255, 255, 30))
    f = used / total * ease_in_out(p)
    xe = x0 + (x1 - x0) * f
    if xe > x0 + 40:
        d.rounded_rectangle([x0, y0, xe, y1], 30, fill=PINK + (255,))
    d.text((x0 + 26, y0 + 22), "GTA 6", font=font("InterDisplay-Black", 46), fill=WHITE)
    draw_center(d, w / 2, 290, f"{int(round(used * ease_in_out(p)))} Go sur {total} Go", font("InterDisplay-Black", 64), WHITE)
    a = clamp(p * 2 - 1)
    draw_center(d, w / 2, 400, "≈ presque un tiers de la console", font("Inter-SemiBold", 40), (255, 200, 90, int(255 * a)))
    return im


def box_card(p):
    S = 2
    w, h = 900, 560
    im = card(w, h)
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    # boîte
    bx, by = 140 * S, 90 * S
    d.rounded_rectangle([bx, by, bx + 260 * S, by + 330 * S], 20 * S, fill=(60, 40, 110, 255), outline=VIOLET + (255,), width=5 * S)
    d.rounded_rectangle([bx + 40 * S, by + 120 * S, bx + 220 * S, by + 210 * S], 14 * S, fill=(255, 255, 255, 255))
    draw_center(d, bx + 130 * S, by + 140 * S, "CODE", font("InterDisplay-Black", 48 * S), (30, 20, 50))
    # disque barré
    a = ease_out_cubic(clamp(p * 2.5))
    cx, cy, r = 640 * S, 250 * S, 120 * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 200, 220, 255))
    d.ellipse([cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25], fill=(40, 26, 70, 255))
    if a > 0:
        L = r * 1.3 * a
        d.line([(cx - L * 0.7, cy - L * 0.7), (cx + L * 0.7, cy + L * 0.7)], fill=RED + (255,), width=22 * S)
    draw_center(d, w * S / 2, 470 * S, "Version physique = un code, pas de disque", font("Inter-Bold", 38 * S), (255, 255, 255))
    im.alpha_composite(big.resize((w, h), Image.LANCZOS))
    return im


def price_card(p):
    w, h = 900, 500
    im = card(w, h)
    d = ImageDraw.Draw(im)
    for i, (name, price, col, sub) in enumerate([("Standard", "80", BLUE, "5 boutiques fermées"), ("Ultimate", "+20", PINK, "tout débloqué")]):
        a = ease_out_back(clamp(p * 3 - i * 0.5))
        if a <= 0:
            continue
        cx = 230 + i * 440
        bw, bh = int(360 * a), int(330 * a)
        d.rounded_rectangle([cx - bw / 2, 60, cx + bw / 2, 60 + bh], 34, fill=col + (50,), outline=col + (255,), width=4)
        if a > 0.6:
            draw_center(d, cx, 90, name, font("InterDisplay-Black", 56), WHITE)
            draw_center(d, cx, 175, price, font("InterDisplay-Black", 120), col)
            draw_center(d, cx, 330, sub, font("Inter-SemiBold", 32), MUTED)
    draw_center(d, w / 2, 420, "Prix de base aux États-Unis : 79,99 $ / 99,99 $", font("Inter-Medium", 30), (200, 190, 230, 200))
    return im


def chips_card(labels, p, title):
    w = 900
    im = card(w, 470)
    d = ImageDraw.Draw(im)
    d.text((56, 44), title, font=font("Inter-SemiBold", 36), fill=MUTED)
    x, y = 56, 130
    for i, lab in enumerate(labels):
        c = chip(lab, size=44, h=96)
        a = ease_out_back(clamp(p * (len(labels) + 1) - i))
        if a <= 0:
            continue
        if x + c.width > w - 40:
            x, y = 56, y + 120
        cc = c.resize((max(1, int(c.width * a)), max(1, int(c.height * a))), Image.BILINEAR)
        im.alpha_composite(cc, (int(x + (c.width - cc.width) / 2), int(y + (c.height - cc.height) / 2)))
        x += c.width + 24
    return im


def check_card(lines, p):
    rows = [(t1, t2, col) for (t1, t2, col) in lines]
    return list_card(rows, p, icon="check")


def chapters_card(p):
    w, h = 900, 420
    im = card(w, h)
    d = ImageDraw.Draw(im)
    d.text((56, 44), "Déblocage au fil de l’histoire", font=font("Inter-SemiBold", 36), fill=MUTED)
    n = 6
    for i in range(n):
        x = 110 + i * 136
        a = clamp(p * (n + 1) - i)
        col = PINK if a > 0.5 else (90, 70, 130)
        d.ellipse([x - 40, 170, x + 40, 250], fill=col + (255,))
        draw_center(d, x, 186, str(i + 1), font("InterDisplay-Black", 44), WHITE)
        if i < n - 1:
            d.line([(x + 44, 210), (x + 92, 210)], fill=(255, 255, 255, 80), width=6)
    draw_center(d, w / 2, 300, "Chapitres", font("Inter-Bold", 40), WHITE)
    return im


def map_pins_card(p, n=5):
    """Carte stylisée avec épingles cadenassées."""
    w, h = 900, 620
    m = R.MAPS["sunset"].crop((300, 300, 1500, 1127)).resize((w - 40, h - 40), Image.LANCZOS).convert("RGBA")
    im = card(w, h)
    mask = Image.new("L", m.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, m.width, m.height], 30, fill=255)
    im.paste(m, (20, 20), mask)
    d = ImageDraw.Draw(im)
    pts = [(240, 180), (560, 140), (700, 330), (330, 420), (520, 500)]
    icons = ["T", "G", "G", "C", "V"]
    for i, (x, y) in enumerate(pts[:n]):
        a = ease_out_back(clamp(p * (n + 1) - i))
        if a <= 0:
            continue
        r = 46 * a
        d.ellipse([x - r, y - r, x + r, y + r], fill=(30, 16, 50, 255), outline=(255, 205, 90, 255), width=5)
        d.polygon([(x - r * 0.5, y + r * 0.8), (x + r * 0.5, y + r * 0.8), (x, y + r * 1.6)], fill=(30, 16, 50, 255))
        d.rounded_rectangle([x - 14 * a, y - 2 * a, x + 14 * a, y + 20 * a], 4, fill=(255, 205, 90, 255))
        d.arc([x - 10 * a, y - 18 * a, x + 10 * a, y + 4 * a], 180, 360, fill=(255, 205, 90, 255), width=max(1, int(5 * a)))
    return im


def times_card(p):
    rows = [("Fibre 1 Gb/s", "≈ 30 min", GREEN), ("100 Mb/s", "≈ 4 h 40", GOLD), ("10 Mb/s", "≈ 2 jours", RED)]
    w, h = 900, 520
    im = card(w, h)
    d = ImageDraw.Draw(im)
    d.text((56, 44), "Télécharger 210 Go", font=font("Inter-SemiBold", 36), fill=MUTED)
    for i, (a_, b_, col) in enumerate(rows):
        a = ease_out_cubic(clamp(p * 3.4 - i))
        if a <= 0:
            continue
        y = 130 + i * 120
        d.rounded_rectangle([40, y - 10, w - 40, y + 90], 26, fill=col + (int(40 * a),))
        d.text((80, y + 12), a_, font=font("Inter-Bold", 44), fill=(255, 255, 255, int(255 * a)))
        tw = d.textbbox((0, 0), b_, font=font("InterDisplay-Black", 52))[2]
        d.text((w - 80 - tw, y + 6), b_, font=font("InterDisplay-Black", 52), fill=col + (int(255 * a),))
    return im


def source_card(title, lines, p, warn="Non confirmé par Rockstar"):
    w, h = 900, 460
    im = card(w, h)
    d = ImageDraw.Draw(im)
    draw_center(d, w / 2, 60, title, font("InterDisplay-Black", 60), WHITE)
    for i, l in enumerate(lines):
        a = clamp(p * 4 - i)
        draw_center(d, w / 2, 170 + i * 70, l, font("Inter-SemiBold", 40), (220, 210, 255, int(255 * a)))
    a = clamp(p * 3 - 1.5)
    if warn and a > 0:
        f = font("Inter-Bold", 34)
        tw = d.textbbox((0, 0), warn, font=f)[2]
        d.rounded_rectangle([w / 2 - tw / 2 - 30, 360, w / 2 + tw / 2 + 30, 420], 30, fill=(255, 205, 90, int(50 * a)), outline=(255, 205, 90, int(255 * a)), width=3)
        draw_center(d, w / 2, 372, warn, f, (255, 205, 90, int(255 * a)))
    return im


# ---------------- moteur ----------------
class Video:
    def __init__(self, key, text, audio_dur, segments, theme_col=PINK, lead=0.5, tail=2.6):
        self.key, self.text, self.audio_dur = key, text, audio_dur
        self.sent = split_sentences(text)
        self.segments = segments  # [(first_sentence_index, label, headline_img_or_None, draw_fn(fr, p, t, dur))]
        self.col = theme_col
        self.lead, self.tail = lead, tail
        self.total = lead + audio_dur + tail
        audio = f"{D}/voix_{key}.mp3"
        sil = silences(audio) if os.path.exists(audio) else None
        self.has_audio = sil is not None
        wt = []
        if sil:
            cl = align_dp(self.sent, audio_dur, sil, lead)
            self.st = []
            for si in range(len(self.sent)):
                mine = [c for c in cl if c[0] == si]
                self.st.append((mine[0][2], mine[-1][3]))
            for si, txt, a, b in cl:
                wt += word_times(txt, a, b)
        else:
            self.st = align(self.sent, audio_dur, sil, lead)
            for s, (a, b) in zip(self.sent, self.st):
                wt += word_times(s, a, b - 0.08)
        self.groups = chunk_words(wt)
        bounds = [self.st[s[0]][0] - 0.15 for s in segments] + [self.total]
        bounds[0] = 0.0
        self.seg_times = [(bounds[i], bounds[i + 1]) for i in range(len(segments))]

    def frame(self, t):
        fr = bg(t)
        # segment courant
        for i, ((a, b), seg) in enumerate(zip(self.seg_times, self.segments)):
            if a <= t < b or (i == len(self.segments) - 1 and t >= a):
                _, label, hl, fn = seg
                lt, dur = t - a, b - a
                last = i == len(self.segments) - 1
                tout = None if last else dur - 0.25
                if hl is not None:
                    place(fr, hl, W / 2, 330, lt, 0.0, tout, scale_from=0.7, rise=20)
                fn(fr, lt, dur, tout)
                pct = clamp(t / (self.lead + self.audio_dur)) * 100
                progress_bar(fr, label, pct, self.col)
                break
        # sous-titres
        for g in self.groups:
            if g[0][1] - 0.05 <= t < g[-1][2] + 0.12:
                idx = max([k for k, w in enumerate(g) if w[1] <= t + 0.03] or [0])
                caption(fr, [w[0].upper() for w in g], idx)
                break
        return fr

    def render(self, out, t0=None, t1=None):
        tmp = out.replace(".mp4", ".part.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        a = int((t0 or 0) * FPS)
        b = int(round((t1 if t1 is not None else self.total) * FPS))
        for i in range(a, b):
            p.stdin.write(self.frame(i / FPS).convert("RGB").tobytes())
        p.stdin.close()
        if p.wait() == 0:
            os.rename(tmp, out)


def card_seg(builder, y=880, scale_from=0.88):
    """builder(p) -> image ; p = progression dans le segment (0..1 sur ~2.5 s)."""
    def fn(fr, lt, dur, tout):
        p = clamp((lt - 0.15) / max(1.2, min(dur * 0.7, 3.0)))
        img = shadowed(builder(p))
        place(fr, img, W / 2, y, lt, 0.05, tout, scale_from=scale_from)
    return fn


def static_seg(img, y=880, scale_from=0.85):
    sh = shadowed(img)

    def fn(fr, lt, dur, tout):
        place(fr, sh, W / 2, y, lt, 0.05, tout, scale_from=scale_from)
    return fn
