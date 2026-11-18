import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, FPS = 1080, 1920, 30
D = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    return ImageFont.truetype(FD + name + ".otf", size)


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.6):
    t = clamp(t)
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


# ---------- palette ----------
CARD = (24, 14, 44, 232)
CARD_BORDER = (255, 255, 255, 38)
WHITE = (255, 255, 255, 255)
MUTED = (200, 190, 230, 255)
ACCENT = (255, 122, 92)
PINK = (255, 92, 170)
VIOLET = (170, 130, 255)
GOLD = (255, 205, 90)


# ---------- map background ----------
MAPS = {k: Image.open(f"{D}/map_{k}.png").convert("RGB") for k in ["night", "sunset", "day"]}
MW, MH = MAPS["night"].size

VIGNETTE = None


def vignette():
    global VIGNETTE
    if VIGNETTE is None:
        y, x = np.mgrid[0:H, 0:W]
        d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
        a = np.clip((d - 0.45) * 1.1, 0, 0.85)
        # assombrissement haut/bas pour la lisibilité
        a = np.maximum(a, np.clip((0.27 - y / H) * 3.2, 0, 0.78))
        a = np.maximum(a, np.clip((y / H - 0.78) * 2.4, 0, 0.55))
        a = np.clip(a + 0.18, 0, 0.92)
        arr = np.zeros((H, W, 4), np.uint8)
        arr[..., 0:3] = (6, 4, 18)
        arr[..., 3] = (a * 255).astype(np.uint8)
        VIGNETTE = Image.fromarray(arr, "RGBA")
    return VIGNETTE


def theme_weights(gt, timeline):
    """timeline: list of (start_time, theme). crossfade 0.8s."""
    cur = timeline[0][1]
    prev, blend = None, 1.0
    for st, th in timeline:
        if gt >= st:
            if th != cur:
                prev, cur = cur, th
                blend = clamp((gt - st) / 0.8)
            else:
                blend = 1.0 if prev is None else blend
    return prev, cur, blend


def background(gt, cam, themes):
    prev, cur, b = theme_weights(gt, themes)
    base = MAPS[cur]
    if prev is not None and b < 1:
        base = Image.blend(MAPS[prev], MAPS[cur], ease_in_out(b))
    cx, cy, vw = cam(gt)
    vh = vw * H / W
    x0, y0 = cx - vw / 2, cy - vh / 2
    s = vw / W
    img = base.transform((W, H), Image.AFFINE, (s, 0, x0, 0, s, y0), resample=Image.BILINEAR)
    img = img.convert("RGBA")
    img.alpha_composite(vignette())
    return img


# ---------- drawing helpers ----------
def shadowed(card, radius=40, blur=28, off=14, alpha=150):
    w, h = card.size
    pad = blur * 2
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = card.split()[3].point(lambda p: alpha if p > 0 else 0)
    sh = Image.new("RGBA", card.size, (0, 0, 0, 255))
    sh.putalpha(a)
    out.alpha_composite(sh, (pad, pad + off))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(card, (pad, pad))
    return out


def card_base(w, h, r=44, fill=CARD):
    S = 2
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], r * S, fill=fill, outline=CARD_BORDER, width=2 * S)
    return im.resize((w, h), Image.LANCZOS)


def text_size(d, txt, f):
    b = d.textbbox((0, 0), txt, font=f)
    return b[2] - b[0], b[3] - b[1], b


def draw_center(d, cx, y, txt, f, fill):
    tw, th, b = text_size(d, txt, f)
    d.text((cx - tw / 2 - b[0], y - b[1]), txt, font=f, fill=fill)
    return th


def gradient_text(txt, f, c1, c2, glow=True, stroke=0):
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw, th, b = text_size(tmp, txt, f)
    pad = 60
    w, h = tw + pad * 2, th + pad * 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - b[0], pad - b[1]), txt, font=f, fill=255)
    g = np.linspace(0, 1, h)[:, None, None]
    col = (np.array(c1) * (1 - g) + np.array(c2) * g) * np.ones((h, w, 1))
    rgba = np.dstack([col.astype(np.uint8), np.asarray(mask)])
    t = Image.fromarray(rgba, "RGBA")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if glow:
        gl = Image.new("RGBA", (w, h), c1 + (0,))
        gl.putalpha(mask.filter(ImageFilter.GaussianBlur(22)).point(lambda p: int(p * 0.9)))
        out.alpha_composite(gl)
    # liseré clair
    edge = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    edge.putalpha(mask.filter(ImageFilter.MaxFilter(5)).point(lambda p: int(p * 0.5)))
    out.alpha_composite(edge)
    out.alpha_composite(t)
    return out


def headline(txt, c1=(255, 150, 110), c2=(255, 70, 120), maxw=960, size=132):
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    while size > 60:
        f = font("InterDisplay-Black", size)
        if text_size(tmp, txt, f)[0] <= maxw:
            break
        size -= 4
    return gradient_text(txt, f, c1, c2)


def pill(txt, icon_col=PINK, size=42, sub=None):
    f = font("Inter-SemiBold", size)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw, th, b = text_size(tmp, txt, f)
    h = 104
    w = tw + 150
    w = min(w, 1010)
    im = card_base(w, h, r=h // 2, fill=(20, 12, 38, 236))
    d = ImageDraw.Draw(im)
    d.ellipse([28, h / 2 - 20, 68, h / 2 + 20], fill=icon_col + (255,))
    d.ellipse([40, h / 2 - 8, 56, h / 2 + 8], fill=(255, 255, 255, 230))
    d.text((92 - b[0], (h - th) / 2 - b[1]), txt, font=f, fill=WHITE)
    return shadowed(im, blur=18, off=8, alpha=120)


def small_caption(txt, size=30):
    f = font("Inter-Medium", size)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw, th, b = text_size(tmp, txt, f)
    im = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - b[0], 10 - b[1]), txt, font=f, fill=(225, 215, 250, 210))
    return im


def chip(txt, col=VIOLET, size=36, h=76):
    f = font("Inter-SemiBold", size)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw, th, b = text_size(tmp, txt, f)
    w = tw + 64
    im = card_base(w, h, r=h // 2, fill=(40, 24, 72, 240))
    d = ImageDraw.Draw(im)
    d.text(((w - tw) / 2 - b[0], (h - th) / 2 - b[1]), txt, font=f, fill=WHITE)
    return im


# ---------- cards ----------
def calendar_card(day, weekday):
    S = 2
    w, h = 420, 460
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S, h * S], 48 * S, fill=(250, 248, 252, 255))
    d.rounded_rectangle([0, 0, w * S, 120 * S], 48 * S, fill=(232, 52, 84, 255))
    d.rectangle([0, 70 * S, w * S, 120 * S], fill=(232, 52, 84, 255))
    for x in (120, 300):
        d.ellipse([(x - 14) * S, 40 * S, (x + 14) * S, 68 * S], fill=(150, 20, 50, 255))
    draw_center(d, w * S / 2, 30 * S, "NOV.", font("InterDisplay-Bold", 52 * S), (255, 255, 255))
    draw_center(d, w * S / 2, 150 * S, str(day), font("InterDisplay-Black", 190 * S), (25, 18, 40))
    draw_center(d, w * S / 2, 385 * S, weekday, font("Inter-SemiBold", 40 * S), (110, 100, 130))
    return im.resize((w, h), Image.LANCZOS)


def clock_card(hours_angle, minutes_angle, label="00:00"):
    S = 2
    w, h = 520, 600
    im = card_base(w, h)
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    cx, cy, R = w * S / 2, 250 * S, 180 * S
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(40, 26, 70, 255), outline=(170, 130, 255, 255), width=6 * S)
    for i in range(12):
        a = i * math.pi / 6
        r1 = R - (34 if i % 3 == 0 else 22) * S
        d.line([(cx + math.sin(a) * r1, cy - math.cos(a) * r1), (cx + math.sin(a) * (R - 12 * S), cy - math.cos(a) * (R - 12 * S))], fill=(220, 210, 255, 255), width=(7 if i % 3 == 0 else 4) * S)
    for ang, ln, wd, col in [(hours_angle, 0.5, 14, (255, 255, 255, 255)), (minutes_angle, 0.78, 9, (255, 122, 92, 255))]:
        d.line([(cx, cy), (cx + math.sin(ang) * R * ln, cy - math.cos(ang) * R * ln)], fill=col, width=wd * S)
    d.ellipse([cx - 16 * S, cy - 16 * S, cx + 16 * S, cy + 16 * S], fill=(255, 255, 255, 255))
    draw_center(d, cx, 470 * S, label, font("InterDisplay-Black", 92 * S), (255, 255, 255))
    im.alpha_composite(big.resize((w, h), Image.LANCZOS))
    return im


def timeline_card(n_visible_f):
    rows = [
        ("Nouvelle-Zélande", "mer. 12 h", PINK),
        ("Australie (Sydney)", "mer. 14 h", (255, 160, 90)),
        ("France", "jeu. 0 h", GOLD),
        ("USA (New York)", "jeu. 6 h", (110, 200, 255)),
    ]
    w, h = 900, 640
    im = card_base(w, h)
    d = ImageDraw.Draw(im)
    d.text((56, 50), "Déblocage · heure de Paris", font=font("Inter-SemiBold", 36), fill=MUTED)
    f1 = font("Inter-Bold", 44)
    f2 = font("InterDisplay-Black", 50)
    for i, (name, t, col) in enumerate(rows):
        a = clamp(n_visible_f - i)
        if a <= 0:
            continue
        y = 140 + i * 118
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        hl = name == "France"
        if hl:
            dl.rounded_rectangle([30, y - 18, w - 30, y + 86], 30, fill=(255, 205, 90, 40), outline=(255, 205, 90, 160), width=2)
        dl.ellipse([60, y + 18, 92, y + 50], fill=col + (255,))
        dl.text((120, y + 8), name, font=f1, fill=WHITE)
        tw = dl.textbbox((0, 0), t, font=f2)[2]
        dl.text((w - 60 - tw, y + 4), t, font=f2, fill=col + (255,))
        if i < 3:
            dl.line([(76, y + 56), (76, y + 118)], fill=(255, 255, 255, 60), width=4)
        dx = int((1 - ease_out_cubic(a)) * 40)
        layer = layer.transform(layer.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0))
        layer.putalpha(layer.split()[3].point(lambda p: int(p * ease_out_cubic(a))))
        im.alpha_composite(layer)
    return im


def big_stat_card(value, sub):
    w, h = 820, 520
    im = card_base(w, h)
    t = gradient_text(value, font("InterDisplay-Black", 230), (255, 160, 110), (255, 70, 140))
    im.alpha_composite(t, ((w - t.width) // 2, 10))
    d = ImageDraw.Draw(im)
    draw_center(d, w / 2, 400, sub, font("Inter-SemiBold", 44), MUTED)
    return im


def gamepad(d, cx, cy, s, col=(235, 230, 255, 255)):
    # manette générique (pas de logo de marque)
    d.rounded_rectangle([cx - 150 * s, cy - 62 * s, cx + 150 * s, cy + 40 * s], 60 * s, fill=col)
    d.ellipse([cx - 175 * s, cy - 30 * s, cx - 70 * s, cy + 105 * s], fill=col)
    d.ellipse([cx + 70 * s, cy - 30 * s, cx + 175 * s, cy + 105 * s], fill=col)
    dk = (40, 26, 70, 255)
    d.rectangle([cx - 112 * s, cy - 22 * s, cx - 64 * s, cy - 6 * s], fill=dk)
    d.rectangle([cx - 96 * s, cy - 38 * s, cx - 80 * s, cy + 10 * s], fill=dk)
    for (bx, by, c) in [(95, -32, PINK), (120, -10, GOLD), (70, -10, (110, 200, 255)), (95, 12, (120, 220, 140))]:
        d.ellipse([cx + (bx - 11) * s, cy + (by - 11) * s, cx + (bx + 11) * s, cy + (by + 11) * s], fill=c + (255,))
    d.ellipse([cx - 52 * s, cy + 14 * s, cx - 14 * s, cy + 52 * s], fill=dk)
    d.ellipse([cx + 14 * s, cy + 14 * s, cx + 52 * s, cy + 52 * s], fill=dk)


def xbox_card(progress):
    S = 2
    w, h = 860, 600
    im = card_base(w, h)
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    gamepad(d, w * S / 2, 150 * S, 1.0 * S)
    d.text((60 * S, 300 * S), "Paramètres  ›  Langue et région", font=font("Inter-Medium", 34 * S), fill=MUTED)
    # ligne de réglage
    d.rounded_rectangle([50 * S, 370 * S, (w - 50) * S, 530 * S], 34 * S, fill=(44, 28, 80, 255))
    d.text((84 * S, 392 * S), "Région", font=font("Inter-SemiBold", 34 * S), fill=MUTED)
    p = ease_out_cubic(progress)
    old, new = "France", "Nouvelle-Zélande"
    f = font("Inter-Bold", 54 * S)
    yb = 446 * S
    layer = Image.new("RGBA", big.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    dl.text((84 * S, yb - p * 50 * S), old, font=f, fill=(255, 255, 255, int(255 * (1 - p))))
    dl.text((84 * S, yb + (1 - p) * 50 * S), new, font=f, fill=(255, 205, 90, int(255 * p)))
    clipm = Image.new("L", big.size, 0)
    ImageDraw.Draw(clipm).rectangle([50 * S, 425 * S, (w - 50) * S, 528 * S], fill=255)
    layer.putalpha(ImageChops.multiply(layer.split()[3], clipm))
    big.alpha_composite(layer)
    im.alpha_composite(big.resize((w, h), Image.LANCZOS))
    return im


def ps_card(cross_p, check_p):
    S = 2
    w, h = 860, 560
    im = card_base(w, h)
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    f = font("Inter-Bold", 46 * S)
    # ligne 1 : barrée
    y1 = 90 * S
    d.ellipse([60 * S, y1 - 10 * S, 140 * S, y1 + 70 * S], outline=(255, 90, 110, 255), width=7 * S)
    d.line([(100 * S, y1 + 30 * S), (100 * S, y1 + 5 * S)], fill=(255, 90, 110, 255), width=6 * S)
    d.line([(100 * S, y1 + 30 * S), (120 * S, y1 + 40 * S)], fill=(255, 90, 110, 255), width=6 * S)
    d.text((170 * S, y1 + 2 * S), "Changer l’heure", font=f, fill=(255, 255, 255, 200))
    d.text((170 * S, y1 + 62 * S), "de la console", font=f, fill=(255, 255, 255, 200))
    if cross_p > 0:
        e = ease_out_cubic(cross_p)
        x0 = 160 * S
        d.line([(x0, y1 + 34 * S), (x0 + 380 * S * e, y1 + 34 * S)], fill=(255, 90, 110, 255), width=8 * S)
        d.line([(x0, y1 + 94 * S), (x0 + 330 * S * e, y1 + 94 * S)], fill=(255, 90, 110, 255), width=8 * S)
    d.text((170 * S, y1 + 130 * S), "ne débloque rien", font=font("Inter-Medium", 36 * S), fill=(255, 140, 150, int(255 * clamp(cross_p * 2 - 0.6))))
    # ligne 2 : coche
    y2 = 340 * S
    a = ease_out_cubic(check_p)
    if a > 0:
        c = (120, 230, 150, int(255 * a))
        d.ellipse([60 * S, y2 - 10 * S, 140 * S, y2 + 70 * S], fill=(120, 230, 150, int(60 * a)), outline=c, width=7 * S)
        d.line([(80 * S, y2 + 32 * S), (96 * S, y2 + 48 * S), (124 * S, y2 + 14 * S)], fill=c, width=9 * S, joint="curve")
        d.text((170 * S, y2 + 2 * S), "C’est la région", font=f, fill=(255, 255, 255, int(255 * a)))
        d.text((170 * S, y2 + 62 * S), "du compte qui compte", font=f, fill=(255, 255, 255, int(255 * a)))
    im.alpha_composite(big.resize((w, h), Image.LANCZOS))
    return im


def preload_card(p):
    S = 2
    w, h = 820, 520
    im = card_base(w, h)
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    cx, cy = w * S / 2, 150 * S
    R = 90 * S
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(60, 36, 110, 255), outline=(170, 130, 255, 255), width=6 * S)
    bob = math.sin(p * 12) * 6 * S
    d.line([(cx, cy - 50 * S + bob), (cx, cy + 30 * S + bob)], fill=WHITE, width=14 * S)
    d.polygon([(cx - 40 * S, cy + 0 * S + bob), (cx + 40 * S, cy + 0 * S + bob), (cx, cy + 48 * S + bob)], fill=WHITE)
    d.text((70 * S, 280 * S), "Préchargement", font=font("Inter-Bold", 46 * S), fill=WHITE)
    pct = int(round(100 * ease_in_out(p)))
    t = f"{pct} %"
    tw = d.textbbox((0, 0), t, font=font("InterDisplay-Black", 46 * S))[2]
    d.text(((w - 70) * S - tw, 280 * S), t, font=font("InterDisplay-Black", 46 * S), fill=(120, 230, 150, 255))
    d.rounded_rectangle([70 * S, 370 * S, (w - 70) * S, 410 * S], 20 * S, fill=(50, 34, 84, 255))
    x1 = 70 * S + ((w - 140) * S) * ease_in_out(p)
    if x1 > 90 * S:
        d.rounded_rectangle([70 * S, 370 * S, x1, 410 * S], 20 * S, fill=(120, 230, 150, 255))
    d.text((70 * S, 440 * S), "Ouvert depuis le 12 novembre", font=font("Inter-Medium", 34 * S), fill=MUTED)
    im.alpha_composite(big.resize((w, h), Image.LANCZOS))
    return im


def donut_card(p):
    S = 2
    w, h = 860, 560
    im = card_base(w, h)
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    cx, cy, R = 230 * S, 280 * S, 170 * S
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(110, 200, 255, 255))
    frac = 0.89 * ease_in_out(p)
    if frac > 0:
        d.pieslice([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * frac, fill=(255, 92, 170, 255))
    r2 = 110 * S
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(24, 14, 44, 255))
    pct = f"{int(round(89 * ease_in_out(p)))} %"
    draw_center(d, cx, cy - 40 * S, pct, font("InterDisplay-Black", 70 * S), (255, 255, 255))
    lx = 460 * S
    d.rounded_rectangle([lx, 150 * S, lx + 36 * S, 186 * S], 10 * S, fill=(255, 92, 170, 255))
    d.text((lx + 56 * S, 140 * S), "Ultimate", font=font("Inter-Bold", 46 * S), fill=WHITE)
    d.text((lx + 56 * S, 196 * S), "100 $", font=font("Inter-Medium", 38 * S), fill=MUTED)
    d.rounded_rectangle([lx, 310 * S, lx + 36 * S, 346 * S], 10 * S, fill=(110, 200, 255, 255))
    d.text((lx + 56 * S, 300 * S), "Standard", font=font("Inter-Bold", 46 * S), fill=WHITE)
    d.text((lx + 56 * S, 356 * S), "80 $", font=font("Inter-Medium", 38 * S), fill=MUTED)
    im.alpha_composite(big.resize((w, h), Image.LANCZOS))
    return im


def cta_card(opts_p, dots_i):
    w, h = 820, 400
    im = card_base(w, h)
    d = ImageDraw.Draw(im)
    # icône bulle
    d.rounded_rectangle([w / 2 - 34, 46, w / 2 + 34, 96], 14, outline=GOLD + (255,), width=6)
    d.polygon([(w / 2 - 14, 94), (w / 2 + 2, 94), (w / 2 - 16, 114)], fill=GOLD + (255,))
    draw_center(d, w / 2, 140, "Tu lances GTA 6 quand ?", font("InterDisplay-Bold", 56), WHITE)
    a = ease_out_back(opts_p)
    if opts_p > 0:
        c1, c2 = chip("Minuit pile", size=38, h=84), chip("Demain matin", size=38, h=84)
        tot = c1.width + c2.width + 30
        x = (w - tot) // 2
        for c in (c1, c2):
            cc = c.copy()
            cc.putalpha(cc.split()[3].point(lambda q: int(q * clamp(opts_p * 2))))
            im.alpha_composite(cc, (x, int(235 + (1 - a) * 30)))
            x += c.width + 30
    for i in range(3):
        col = (255, 255, 255, 230) if i == dots_i else (255, 255, 255, 70)
        d.ellipse([w / 2 - 40 + i * 30, 355, w / 2 - 28 + i * 30, 367], fill=col)
    return im


# ---------- compositing ----------
def place(frame, img, cx, cy, t_in, t, t_out=None, scale_from=0.86, rise=40, back=True):
    """Pose img centrée en (cx, cy) avec animation d'entrée/sortie."""
    if t < t_in:
        return
    p = (t - t_in) / 0.42
    e = ease_out_back(p, 1.4) if back else ease_out_cubic(p)
    alpha = clamp(p * 2.2)
    s = scale_from + (1 - scale_from) * e
    dy = (1 - ease_out_cubic(p)) * rise
    if t_out is not None and t > t_out:
        q = clamp((t - t_out) / 0.28)
        alpha *= 1 - q
        s *= 1 - 0.06 * q
        dy -= 20 * q
    if alpha <= 0.01:
        return
    im = img
    if abs(s - 1) > 0.003:
        im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
    if alpha < 0.999:
        im = im.copy()
        im.putalpha(im.split()[3].point(lambda q: int(q * alpha)))
    frame.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2 + dy)))


HEAD_Y = 360
CARD_Y = 960
PILL_Y = 1560


def scene_defs():
    """Chaque scène : (durée, fonction draw(frame, t, dur))."""
    S = []

    hl1 = headline("AUJOURD’HUI ?!")
    cal18 = shadowed(calendar_card(18, "Mercredi"))
    p1 = pill("Certains joueront à GTA 6 dès aujourd’hui")

    def s1(fr, t, dur):
        place(fr, hl1, W / 2, HEAD_Y, 0.05, t, dur - 0.3)
        place(fr, cal18, W / 2, CARD_Y, 0.3, t, dur - 0.3)
        place(fr, p1, W / 2, PILL_Y, 0.7, t, dur - 0.3)
    S.append((3.8, s1))

    cal19 = shadowed(calendar_card(19, "Jeudi"))
    p2 = pill("Sortie officielle : jeudi 19 novembre", icon_col=GOLD)
    ch1, ch2 = chip("PS5"), chip("Xbox Series X|S")

    def s2(fr, t, dur):
        # flip de page 18 -> 19
        ft = clamp((t - 0.5) / 0.5)
        if ft <= 0:
            place(fr, cal18, W / 2, CARD_Y - 60, -1, t, dur - 0.3)
        else:
            src = cal18 if ft < 0.5 else cal19
            k = abs(math.cos(ft * math.pi))
            k = max(k, 0.02)
            im = src.resize((src.width, max(2, int(src.height * k))), Image.BILINEAR)
            if t > dur - 0.3:
                q = clamp((t - dur + 0.3) / 0.28)
                im = im.copy()
                im.putalpha(im.split()[3].point(lambda a: int(a * (1 - q))))
            fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(CARD_Y - 60 - im.height / 2)))
        place(fr, ch1, W / 2 - 170, CARD_Y + 260, 1.2, t, dur - 0.3)
        place(fr, ch2, W / 2 + 110, CARD_Y + 260, 1.35, t, dur - 0.3)
        place(fr, p2, W / 2, PILL_Y, 0.25, t, dur - 0.3)
    S.append((4.2, s2))

    p3 = pill("Déblocage à minuit, heure locale", icon_col=VIOLET)
    cap3 = small_caption("D’après les horaires affichés sur le PlayStation Store")

    def s3(fr, t, dur):
        sp = ease_out_cubic(clamp((t - 0.3) / 1.6))
        m = (1 - sp) * 4.5 * 2 * math.pi  # tours rapides vers 0
        hh = (1 - sp) * 4.5 * 2 * math.pi / 12
        ck = shadowed(clock_card(-hh, -m))
        place(fr, ck, W / 2, CARD_Y - 30, 0.1, t, dur - 0.3)
        place(fr, p3, W / 2, PILL_Y, 0.5, t, dur - 0.3)
        place(fr, cap3, W / 2, PILL_Y + 100, 0.9, t, dur - 0.3, back=False)
    S.append((4.2, s3))

    hl4 = headline("PAS TOUS EN MÊME TEMPS", (255, 255, 255), (205, 175, 255))
    p4 = pill("Plus tu es à l’est, plus tu joues tôt", icon_col=(110, 200, 255))

    def s4(fr, t, dur):
        place(fr, hl4, W / 2, HEAD_Y, 0.05, t, dur - 0.3)
        n = clamp((t - 0.5) / 0.55, 0, 10)
        tc = shadowed(timeline_card(n))
        place(fr, tc, W / 2, CARD_Y + 10, 0.2, t, dur - 0.3, scale_from=0.94)
        place(fr, p4, W / 2, PILL_Y + 40, 2.9, t, dur - 0.3)
    S.append((6.0, s4))

    hl5 = headline("NOUVELLE-ZÉLANDE")
    st5 = shadowed(big_stat_card("12 h", "d’avance sur la France"))
    p5 = pill("Première au monde : midi, heure de Paris", icon_col=PINK)

    def s5(fr, t, dur):
        place(fr, hl5, W / 2, HEAD_Y, 0.05, t, dur - 0.3)
        place(fr, st5, W / 2, CARD_Y, 0.3, t, dur - 0.3, scale_from=0.6)
        place(fr, p5, W / 2, PILL_Y, 0.8, t, dur - 0.3)
    S.append((4.4, s5))

    hl6 = headline("ASTUCE XBOX", (150, 255, 170), (60, 200, 140))
    p6 = pill("Passer la console en région Nouvelle-Zélande", icon_col=(120, 230, 150), size=38)

    def s6(fr, t, dur):
        place(fr, hl6, W / 2, HEAD_Y, 0.05, t, dur - 0.3)
        xc = shadowed(xbox_card(clamp((t - 1.3) / 0.6)))
        place(fr, xc, W / 2, CARD_Y + 10, 0.3, t, dur - 0.3, scale_from=0.92)
        place(fr, p6, W / 2, PILL_Y + 40, 0.8, t, dur - 0.3)
    S.append((4.8, s6))

    hl7 = headline("ET SUR PS5 ?", (140, 190, 255), (90, 120, 255))
    p7 = pill("Le jeu suit le pays de ton compte PSN", icon_col=(110, 200, 255))

    def s7(fr, t, dur):
        place(fr, hl7, W / 2, HEAD_Y, 0.05, t, dur - 0.3)
        pc = shadowed(ps_card(clamp((t - 0.9) / 0.5), clamp((t - 2.0) / 0.5)))
        place(fr, pc, W / 2, CARD_Y, 0.25, t, dur - 0.3, scale_from=0.92)
        place(fr, p7, W / 2, PILL_Y + 20, 2.4, t, dur - 0.3)
    S.append((4.8, s7))

    hl8 = headline("TOUT EST PRÊT ?", (255, 220, 120), (255, 150, 80))
    p8 = pill("Vérifie ton espace de stockage avant ce soir", icon_col=GOLD, size=38)

    def s8(fr, t, dur):
        place(fr, hl8, W / 2, HEAD_Y, 0.05, t, dur - 0.3)
        pl = shadowed(preload_card(clamp((t - 0.6) / 2.2)))
        place(fr, pl, W / 2, CARD_Y, 0.25, t, dur - 0.3, scale_from=0.92)
        place(fr, p8, W / 2, PILL_Y, 1.0, t, dur - 0.3)
    S.append((4.3, s8))

    hl9 = headline("9 SUR 10", (255, 150, 110), (255, 70, 140))
    p9 = pill("ont précommandé l’édition Ultimate", icon_col=PINK)
    cap9 = small_caption("Estimation Sensor Tower, PS5 et Xbox Series X|S")

    def s9(fr, t, dur):
        place(fr, hl9, W / 2, HEAD_Y, 0.05, t, dur - 0.3)
        dc = shadowed(donut_card(clamp((t - 0.5) / 1.6)))
        place(fr, dc, W / 2, CARD_Y, 0.25, t, dur - 0.3, scale_from=0.92)
        place(fr, p9, W / 2, PILL_Y, 0.9, t, dur - 0.3)
        place(fr, cap9, W / 2, PILL_Y + 100, 1.2, t, dur - 0.3, back=False)
    S.append((4.6, s9))

    sub = pill("Abonne-toi pour la suite", icon_col=PINK)

    def s10(fr, t, dur):
        dots = 0 if t < 1.2 else (1 if t < 2.4 else 2)
        cc = shadowed(cta_card(clamp((t - 0.6) / 0.5), dots))
        place(fr, cc, W / 2, CARD_Y - 80, 0.1, t, None)
        place(fr, sub, W / 2, CARD_Y + 220, 2.2, t, None)
    S.append((5.2, s10))
    return S


def camera(gt):
    # dérive lente sur la carte
    cx = 900 + 220 * math.sin(gt * 0.09) + 60 * math.sin(gt * 0.31)
    cy = 1450 + 650 * math.sin(gt * 0.05 + 0.6)
    vw = 1250 - 150 * math.sin(gt * 0.11)
    vh = vw * H / W
    cy = min(max(cy, vh / 2 + 5), MH - vh / 2 - 5)
    cx = min(max(cx, vw / 2 + 5), MW - vw / 2 - 5)
    return cx, cy, vw


def render_scene(idx, start, dur, fn, out, frames_only=None):
    themes = [(0, "night"), (12.2, "sunset"), (26.6, "day"), (40.2, "night")]
    n = int(round(dur * FPS))
    if frames_only is not None:
        for t in frames_only:
            fr = background(start + t, camera, themes)
            fn(fr, t, dur)
            fr.convert("RGB").save(f"{D}/preview_s{idx+1}_{t:.1f}.jpg", quality=90)
        return
    tmp = out.replace(".mp4", ".part.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        fr = background(start + t, camera, themes)
        fn(fr, t, dur)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.rename(tmp, out)


if __name__ == "__main__":
    mode = sys.argv[1]
    S = scene_defs()
    starts = np.cumsum([0] + [d for d, _ in S])
    if mode == "preview":
        for i, tt in [(0, [2.0]), (1, [0.75, 2.5]), (2, [2.5]), (3, [3.5]), (4, [2.0]), (5, [3.0]), (6, [3.5]), (7, [2.0]), (8, [3.0]), (9, [4.0])]:
            render_scene(i, starts[i], S[i][0], S[i][1], None, frames_only=tt)
    elif mode == "scenes":
        ids = [int(x) for x in sys.argv[2].split(",")]
        for i in ids:
            render_scene(i, starts[i], S[i][0], S[i][1], f"{D}/scene_{i:02d}.mp4")
    elif mode == "durations":
        print(list(zip([float(s) for s in starts], [d for d, _ in S])))
