"""Génère une carte de ville fictive stylisée (originale), en 3 ambiances."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, zoom as ndzoom

MW, MH = 1600, 3000
SS = 2  # supersampling
rng = np.random.default_rng(7)


def noise(shape, sigma, seed):
    r = np.random.default_rng(seed).standard_normal(shape)
    n = gaussian_filter(r, sigma)
    return n / (np.abs(n).max() + 1e-9)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def land_mask():
    h, w = MH // 4, MW // 4
    v, u = np.mgrid[0:h, 0:w]
    u = u / w
    v = v / h
    n1 = noise((h, w), 18, 1) * 0.06 + noise((h, w), 7, 2) * 0.035 + noise((h, w), 2.5, 5) * 0.012
    n2 = noise((h, w), 22, 3) * 0.07 + noise((h, w), 6, 4) * 0.035 + noise((h, w), 2, 6) * 0.01
    n3 = noise((h, w), 4, 8)
    east = 0.80 - 0.18 * smoothstep(0.62, 0.98, v) + n1
    west = -0.1 + 0.42 * smoothstep(0.55, 1.0, v) + n2
    land = (u < east) & (u > west) & (v < 0.95 + n1 * 0.4)
    # baie à l'est
    bay = ((u - 0.80) / 0.13) ** 2 + ((v - 0.50) / 0.05) ** 2 + n3 * 0.8 < 1
    land &= ~bay
    # lac central
    lake = ((u - 0.40) / 0.12) ** 2 + ((v - 0.40) / 0.06) ** 2 + n3 * 0.9 < 1
    land &= ~lake
    lake2 = ((u - 0.28) / 0.07) ** 2 + ((v - 0.70) / 0.03) ** 2 + n3 * 1.2 < 1
    land &= ~lake2
    # îles-barrières
    strip = (np.abs(u - (0.885 + n1 * 0.3)) < 0.013) & (v > 0.06) & (v < 0.62)
    gaps = (np.abs(v - 0.22) < 0.008) | (np.abs(v - 0.41) < 0.01)
    land |= strip & ~gaps
    # petites îles au sud-est
    for cx, cy, r in [(0.70, 0.86, 0.025), (0.76, 0.90, 0.018), (0.82, 0.93, 0.014), (0.66, 0.66, 0.02)]:
        land |= ((u - cx) / r) ** 2 + ((v - cy) / (r * 0.55)) ** 2 + n2 * 2 < 1
    m = ndzoom(land.astype(float), 4 * SS, order=1)
    m = gaussian_filter(m, 2.5)
    return (m > 0.5).astype(np.uint8) * 255


def roads(mask_img):
    W, H = MW * SS, MH * SS
    minor = Image.new("L", (W, H), 0)
    major = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(minor)
    dM = ImageDraw.Draw(major)
    r = np.random.default_rng(11)

    def grid(x0, y0, x1, y1, step, ang, width, prob=0.85):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ca, sa = np.cos(ang), np.sin(ang)
        L = max(x1 - x0, y1 - y0)
        for k in np.arange(-L, L, step):
            if r.random() > prob:
                continue
            # lignes "horizontales" et "verticales" tournées
            for (dx, dy, px, py) in [(ca, sa, -sa, ca), (-sa, ca, ca, sa)]:
                ox, oy = cx + px * k, cy + py * k
                a = (ox - dx * L, oy - dy * L)
                b = (ox + dx * L, oy + dy * L)
                dm.line([a, b], fill=255, width=width)

    S = SS
    # centre-ville dense (est)
    grid(800 * S, 100 * S, 1450 * S, 1900 * S, 30 * S, 0.0, 2 * S, 0.92)
    grid(0, 0, 900 * S, 1200 * S, 46 * S, 0.12, 2 * S, 0.8)
    grid(0, 1200 * S, 1200 * S, 3000 * S, 42 * S, -0.08, 2 * S, 0.8)
    # masques de quartiers irréguliers (bruit)
    dn = noise((MH // 10, MW // 10), 6, 21)
    dn = Image.fromarray(((dn + 1) * 127.5).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    east = Image.linear_gradient("L").rotate(90).resize((W, H))  # 0 à droite -> 255 à gauche
    zm = Image.fromarray(np.where(np.asarray(dn) > 115, 255, 0).astype(np.uint8))
    minor = Image.composite(minor, Image.new("L", (W, H), 0), zm)
    def catmull(pts, n=30):
        pts = np.array(pts, float)
        out = []
        p = np.vstack([pts[0], pts, pts[-1]])
        for i in range(1, len(p) - 2):
            for t in np.linspace(0, 1, n, endpoint=False):
                t2, t3 = t * t, t * t * t
                out.append(0.5 * ((2 * p[i]) + (-p[i - 1] + p[i + 1]) * t + (2 * p[i - 1] - 5 * p[i] + 4 * p[i + 1] - p[i + 2]) * t2 + (-p[i - 1] + 3 * p[i] - 3 * p[i + 1] + p[i + 2]) * t3))
        out.append(p[-2])
        return [tuple(q * S) for q in out]

    highways = [
        [(1080, -50), (1050, 600), (1000, 1200), (930, 1900), (860, 2500), (820, 3050)],
        [(-50, 520), (500, 560), (900, 640), (1250, 620), (1420, 600)],
        [(-50, 1350), (450, 1300), (800, 1250), (1100, 1180)],
        [(300, -50), (380, 700), (520, 1250), (600, 1900), (560, 2600)],
        [(150, 2050), (600, 2000), (1000, 2150), (1150, 2400)],
        [(1100, 300), (1300, 330), (1440, 360)],
        [(1050, 950), (1250, 980), (1430, 1000)],
    ]
    for hw in highways:
        dM.line(catmull(hw), fill=255, width=7 * S, joint="curve")
    return minor, major


def build():
    land = Image.fromarray(land_mask())
    minor, major = roads(land)
    landb = land
    minor_m = Image.composite(minor, Image.new("L", minor.size, 0), landb)
    # les autoroutes peuvent traverser l'eau (ponts) mais pas trop loin
    near = landb.filter(ImageFilter.GaussianBlur(40 * SS)).point(lambda p: 255 if p > 40 else 0)
    major_m = Image.composite(major, Image.new("L", major.size, 0), near)
    coast = landb.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    out = {}
    for name in ["minor", "major", "land", "coast"]:
        pass
    small = lambda im: im.resize((MW, MH), Image.LANCZOS)
    return small(landb), small(minor_m), small(major_m), small(coast)


THEMES = {
    "night": dict(w1=(9, 16, 40), w2=(6, 10, 28), land=(20, 24, 50), minor=(78, 80, 140), major=(206, 190, 255), glow=(140, 110, 255), coast=(90, 120, 220)),
    "sunset": dict(w1=(88, 40, 120), w2=(52, 22, 84), land=(232, 178, 196), minor=(150, 92, 130), major=(70, 28, 70), glow=(255, 120, 200), coast=(255, 200, 230)),
    "day": dict(w1=(22, 150, 180), w2=(10, 80, 120), land=(160, 205, 170), minor=(222, 215, 240), major=(250, 248, 255), glow=(200, 240, 255), coast=(230, 250, 255)),
}


def paint(theme, land, minor, major, coast):
    t = THEMES[theme]
    W, H = MW, MH
    g = np.linspace(0, 1, H)[:, None, None]
    water = (np.array(t["w1"]) * (1 - g) + np.array(t["w2"]) * g) * np.ones((H, W, 1))
    wn = noise((H // 8, W // 8), 3, 9)
    wn = ndzoom(wn, 8, order=1)[:H, :W, None]
    water = water * (1 + 0.08 * wn)
    img = water
    L = np.asarray(land, float)[..., None] / 255
    img = img * (1 - L) + np.array(t["land"]) * L
    # halo côtier dans l'eau
    cg = np.asarray(land.filter(ImageFilter.GaussianBlur(26)), float)[..., None] / 255
    halo = np.clip(cg * (1 - L) * 1.6, 0, 1) * 0.55
    img = img * (1 - halo) + np.array(t["coast"]) * halo
    mi = np.asarray(minor, float)[..., None] / 255 * 0.9
    img = img * (1 - mi) + np.array(t["minor"]) * mi
    gl = np.asarray(major.filter(ImageFilter.GaussianBlur(10)), float)[..., None] / 255
    img = img + np.array(t["glow"]) * gl * 0.55
    ma = np.asarray(major, float)[..., None] / 255
    img = img * (1 - ma) + np.array(t["major"]) * ma
    co = np.asarray(coast, float)[..., None] / 255 * 0.5
    img = img * (1 - co) + np.array(t["coast"]) * co
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    layers = build()
    for th in THEMES:
        paint(th, *layers).save(f"/home/claude/proto/map_{th}.png")
    print("ok")
