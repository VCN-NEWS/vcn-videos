"""6 idées de photo de profil VCN (1080x1080), + planche d'aperçu en rond."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 1080
FD = "/usr/share/fonts/opentype/inter/"
F = lambda n, s: ImageFont.truetype(FD + n + ".otf", s)
OUT = "/home/claude/brand/idees"
os.makedirs(OUT, exist_ok=True)

PINK, VIOLET, CYAN, PEACH, GOLD = (255, 70, 160), (130, 60, 230), (60, 230, 255), (255, 190, 120), (255, 214, 92)


def vgrad(c1, c2, w=S, h=S, stops=None):
    y = np.linspace(0, 1, h)[:, None, None]
    a, b = np.array(c1, float), np.array(c2, float)
    g = a + (b - a) * y
    return Image.fromarray(np.repeat(g, w, 1).astype(np.uint8), "RGB").convert("RGBA")


def multigrad(cols, w=S, h=S):
    y = np.linspace(0, 1, h)
    out = np.zeros((h, 3))
    n = len(cols) - 1
    for i in range(h):
        t = y[i] * n; k = min(int(t), n - 1); f = t - k
        out[i] = np.array(cols[k]) * (1 - f) + np.array(cols[k + 1]) * f
    return Image.fromarray(np.repeat(out[:, None, :], w, 1).astype(np.uint8), "RGB").convert("RGBA")


def text_mask(txt, font, size=(S, S), xy=None, anchor="mm", stroke=0):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.text(xy or (size[0] // 2, size[1] // 2), txt, font=font, fill=255, anchor=anchor, stroke_width=stroke, stroke_fill=255)
    return m


def fill(mask, src):
    im = src.copy(); im.putalpha(mask); return im


def glow(img, mask, col, radius, strength=1.0):
    g = Image.new("RGBA", img.size, col + (0,))
    g.putalpha(mask.filter(ImageFilter.GaussianBlur(radius)).point(lambda p: min(255, int(p * strength))))
    img.alpha_composite(g)


def gta_grad(w=S, h=S):
    return multigrad([PEACH, PINK, VIOLET], w, h)


# 1. Néon ---------------------------------------------------------------
def neon():
    im = vgrad((22, 6, 40), (8, 2, 18))
    d = ImageDraw.Draw(im)
    for y in range(0, S, 54):  # briques discrètes
        off = 0 if (y // 54) % 2 else 60
        for x in range(-60 + off, S, 120):
            d.rectangle([x + 3, y + 3, x + 117, y + 51], outline=(40, 16, 60, 255), width=2)
    m = text_mask("VCN", F("InterDisplay-Black", 380), xy=(S // 2, 470))
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(13))
    glow(im, edge, PINK, 40, 2.2); glow(im, edge, PINK, 14, 2.0)
    im.alpha_composite(fill(edge, Image.new("RGBA", (S, S), (255, 200, 235, 255))))
    m2 = text_mask("NEWS · FR", F("InterDisplay-Bold", 110), xy=(S // 2, 760))
    e2 = m2.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(7))
    glow(im, e2, CYAN, 26, 2.2)
    im.alpha_composite(fill(e2, Image.new("RGBA", (S, S), (210, 250, 255, 255))))
    return im


# 2. Synthwave coucher de soleil ------------------------------------------
def palm(d, x, y, h, col):
    # tronc courbé
    pts = [(x + 18 * math.sin(t / 10) , y - t * h / 100) for t in range(0, 101, 5)]
    d.line(pts, fill=col, width=int(h * 0.05))
    tx, ty = pts[-1]
    for ang in (-170, -140, -110, -70, -40, -10, 20):
        a = math.radians(ang)
        pts2 = []
        for k in range(0, 11):
            r = k / 10 * h * 0.42
            pts2.append((tx + r * math.cos(a), ty + r * math.sin(a) + (k / 10) ** 2 * h * 0.16))
        d.line(pts2, fill=col, width=int(h * 0.04), joint="curve")


def synthwave():
    im = multigrad([(40, 10, 90), (150, 40, 160), (255, 90, 140), (255, 170, 110)])
    sun = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sun).ellipse([240, 200, 840, 800], fill=255)
    sd = ImageDraw.Draw(sun)
    for i, y in enumerate(range(560, 800, 44)):
        sd.rectangle([0, y, S, y + 8 + i * 3], fill=0)
    glow(im, sun, (255, 120, 80), 50, 1.2)
    im.alpha_composite(fill(sun, multigrad([(255, 240, 150), (255, 120, 120)])))
    # sol
    d = ImageDraw.Draw(im)
    d.rectangle([0, 760, S, S], fill=(25, 6, 50, 255))
    for k in range(-12, 13):
        d.line([(S / 2 + k * 30, 760), (S / 2 + k * 160, S)], fill=(255, 70, 200, 255), width=3)
    for i in range(8):
        y = 760 + (i / 8) ** 1.8 * 320
        d.line([(0, y), (S, y)], fill=(255, 70, 200, 255), width=3)
    palm(d, 140, 790, 520, (20, 4, 35, 255))
    palm(d, 930, 790, 430, (20, 4, 35, 255))
    m = text_mask("VCN", F("InterDisplay-BlackItalic", 300), xy=(S // 2, 900))
    st = m.filter(ImageFilter.MaxFilter(23))
    im.alpha_composite(fill(st, Image.new("RGBA", (S, S), (20, 4, 35, 255))))
    im.alpha_composite(fill(m, multigrad([(255, 255, 255), (190, 220, 255), (90, 120, 200), (255, 255, 255)])))
    return im


# 3. Mini-carte GTA-like ---------------------------------------------------
def minimap():
    im = Image.new("RGBA", (S, S), (14, 20, 34, 255))
    d = ImageDraw.Draw(im)
    d.ellipse([60, 60, 1020, 1020], fill=(36, 44, 58, 255))
    mp = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    md = ImageDraw.Draw(mp)
    md.polygon([(60, 640), (380, 560), (520, 700), (380, 1020), (60, 1020)], fill=(40, 110, 190, 255))  # mer
    md.rectangle([640, 180, 860, 380], fill=(60, 120, 70, 255))  # parc
    for x in range(140, 1000, 120):
        md.line([(x, 60), (x - 60, 1020)], fill=(120, 130, 145, 255), width=14)
    for y in range(150, 1000, 130):
        md.line([(60, y), (1020, y + 40)], fill=(120, 130, 145, 255), width=14)
    md.line([(100, 260), (1000, 860)], fill=(230, 200, 90, 255), width=26)  # autoroute
    circ = Image.new("L", (S, S), 0); ImageDraw.Draw(circ).ellipse([60, 60, 1020, 1020], fill=255)
    mp.putalpha(Image.fromarray(np.minimum(np.array(mp.split()[3]), np.array(circ))))
    im.alpha_composite(mp)
    # anneau + jauges vie/armure
    d.ellipse([60, 60, 1020, 1020], outline=(10, 12, 20, 255), width=34)
    d.arc([46, 46, 1034, 1034], 100, 210, fill=(90, 210, 110, 255), width=26)
    d.arc([46, 46, 1034, 1034], 215, 300, fill=(80, 170, 255, 255), width=26)
    # épingle VCN
    pin = Image.new("L", (S, S), 0); pd = ImageDraw.Draw(pin)
    pd.ellipse([330, 230, 750, 650], fill=255); pd.polygon([(380, 560), (700, 560), (540, 860)], fill=255)
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sh.putalpha(pin.filter(ImageFilter.GaussianBlur(25)).point(lambda p: p * 0.7))
    im.alpha_composite(sh, (12, 24))
    im.alpha_composite(fill(pin, gta_grad()))
    ImageDraw.Draw(im).ellipse([375, 275, 705, 605], fill=(255, 255, 255, 255))
    t = text_mask("VCN", F("InterDisplay-Black", 130), xy=(540, 440))
    im.alpha_composite(fill(t, multigrad([PINK, VIOLET])))
    return im


# 4. Micro de reporter -----------------------------------------------------
def micro():
    im = multigrad([(60, 10, 90), (200, 40, 140)])
    rays = Image.new("L", (S, S), 0); rd = ImageDraw.Draw(rays)
    for k in range(0, 360, 15):
        a1, a2 = math.radians(k), math.radians(k + 7)
        rd.polygon([(540, 470), (540 + 1500 * math.cos(a1), 470 + 1500 * math.sin(a1)), (540 + 1500 * math.cos(a2), 470 + 1500 * math.sin(a2))], fill=40)
    im.alpha_composite(fill(rays, Image.new("RGBA", (S, S), (255, 255, 255, 255))))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([490, 560, 590, 1000], 40, fill=(30, 30, 40, 255))  # manche
    head = Image.new("L", (S, S), 0); ImageDraw.Draw(head).ellipse([340, 150, 740, 550], fill=255)
    im.alpha_composite(fill(head, multigrad([(235, 235, 245), (130, 130, 150)])))
    hd = ImageDraw.Draw(im)
    for k in range(-200, 201, 34):
        hd.line([(540 + k - 200, 150), (540 + k + 200, 550)], fill=(90, 90, 110, 120), width=4)
        hd.line([(540 + k + 200, 150), (540 + k - 200, 550)], fill=(90, 90, 110, 120), width=4)
    hd.ellipse([340, 150, 740, 550], outline=(60, 60, 80, 255), width=10)
    # cube logo (flag)
    cube = Image.new("RGBA", (S, S), (0, 0, 0, 0)); cd = ImageDraw.Draw(cube)
    cd.polygon([(370, 560), (710, 560), (750, 600), (750, 800), (410, 800), (370, 760)], fill=(20, 8, 36, 255))
    cd.rectangle([370, 600, 710, 800], fill=(255, 255, 255, 255))
    im.alpha_composite(cube)
    t = text_mask("VCN", F("InterDisplay-Black", 150), xy=(540, 700))
    im.alpha_composite(fill(t, gta_grad()))
    return im


# 5. « En direct » chaîne d'info -------------------------------------------
def live():
    im = gta_grad()
    d = ImageDraw.Draw(im)
    t = text_mask("VCN", F("InterDisplay-Black", 360), xy=(540, 470))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sh.putalpha(t.filter(ImageFilter.GaussianBlur(20)).point(lambda p: p * 0.5))
    im.alpha_composite(sh, (0, 14))
    im.alpha_composite(fill(t, Image.new("RGBA", (S, S), (255, 255, 255, 255))))
    d.rounded_rectangle([250, 700, 830, 830], 30, fill=(20, 6, 38, 255))
    d.ellipse([295, 740, 345, 790], fill=(255, 60, 70, 255))
    ImageDraw.Draw(im).text((370, 765), "EN DIRECT", font=F("InterDisplay-Black", 76), fill=(255, 255, 255, 255), anchor="lm")
    return im


# 6. Monogramme « V » chromé ------------------------------------------------
def monogram():
    im = vgrad((16, 6, 30), (40, 10, 70))
    d = ImageDraw.Draw(im)
    ring = Image.new("L", (S, S), 0); ImageDraw.Draw(ring).ellipse([110, 110, 970, 970], outline=255, width=26)
    glow(im, ring, PINK, 30, 1.6)
    im.alpha_composite(fill(ring, gta_grad()))
    v = text_mask("V", F("InterDisplay-BlackItalic", 700), xy=(560, 520))
    st = v.filter(ImageFilter.MaxFilter(25))
    glow(im, v, VIOLET, 40, 1.5)
    im.alpha_composite(fill(st, Image.new("RGBA", (S, S), (10, 4, 20, 255))))
    im.alpha_composite(fill(v, multigrad([(255, 255, 255), (255, 200, 230), (255, 90, 170), (150, 80, 230)])))
    t = text_mask("CITY NEWS", F("InterDisplay-Black", 70), xy=(540, 860))
    im.alpha_composite(fill(t, Image.new("RGBA", (S, S), (255, 255, 255, 255))))
    return im


IDEAS = [("1_neon", "Néon", neon), ("2_synthwave", "Coucher de soleil", synthwave), ("3_minicarte", "Mini-carte", minimap),
         ("4_micro", "Micro reporter", micro), ("5_direct", "En direct", live), ("6_monogramme", "Monogramme V", monogram)]

if __name__ == "__main__":
    circ = Image.new("L", (S, S), 0); ImageDraw.Draw(circ).ellipse([0, 0, S - 1, S - 1], fill=255)
    sheet = Image.new("RGB", (3 * 400, 2 * 520), (245, 245, 248))
    sd = ImageDraw.Draw(sheet)
    for i, (k, lab, fn) in enumerate(IDEAS):
        im = fn().convert("RGB"); im.save(f"{OUT}/{k}.png")
        c = im.copy(); c.putalpha(circ)
        x, y = (i % 3) * 400, (i // 3) * 520
        sheet.paste(c.resize((320, 320), Image.LANCZOS), (x + 40, y + 30), c.resize((320, 320), Image.LANCZOS))
        sm = c.resize((72, 72), Image.LANCZOS)  # taille réelle sur un profil
        sheet.paste(sm, (x + 60, y + 380), sm)
        sd.text((x + 150, y + 395), f"{i + 1}. {lab}", font=F("InterDisplay-Bold", 30), fill=(20, 20, 30))
        sd.text((x + 150, y + 432), "← taille réelle", font=F("Inter-Regular", 22), fill=(120, 120, 130))
    sheet.save(f"{OUT}/planche_idees.png")
    print("ok")
