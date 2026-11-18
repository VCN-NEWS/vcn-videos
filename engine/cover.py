"""Couvertures « miniature » : image d'appel affichée sur la grille des profils.

TikTok et Instagram prennent la 1re image de la vidéo comme couverture : on incruste donc la
couverture sur les ~0,35 premières secondes (add_cover), puis elle s'efface pendant que la voix démarre.
La grille TikTok/Instagram recadre en 3:4 (y 240 → 1680) : tout le texte important reste dans cette zone.

Usage :
  python3 cover.py lucia            -> ../covers/cover_lucia.jpg
  python3 cover.py lucia apply      -> incruste dans ../videos/VCN_lucia.mp4
"""
import os, sys, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from render import font, text_size, W, H
from v2 import gta_gradient

D = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(D, "..", "bibliotheque")
OUT = os.path.join(D, "..", "covers")


def _bg(rel, fx=0.5, fy=0.5, zoom=1.0):
    im = Image.open(os.path.join(LIB, rel)).convert("RGB")
    iw, ih = im.size
    ch = ih / zoom
    cw = ch * W / H
    if cw > iw:
        cw, ch = iw, iw * H / W
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(3, 90, 2))
    im = ImageEnhance.Color(im).enhance(1.2)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    return im.convert("RGBA")


def _shade(fr):
    """Assombrit le haut et surtout le bas (violet nuit) pour faire ressortir le titre."""
    y = np.linspace(0, 1, H)[:, None]
    a = np.clip((y - 0.42) / 0.38, 0, 1) ** 1.3 * 235 + np.clip((0.16 - y) / 0.16, 0, 1) * 150
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., 0], lay[..., 1], lay[..., 2] = 18, 6, 34
    lay[..., 3] = np.repeat(a, W, axis=1).astype(np.uint8)
    fr.alpha_composite(Image.fromarray(lay, "RGBA"))


def _title_line(txt, size, maxw=1000):
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    while size > 80:
        f = font("InterDisplay-Black", size)
        if text_size(tmp, txt, f)[0] <= maxw:
            break
        size -= 6
    tw, th, b = text_size(tmp, txt, f)
    pad = 50
    w, h = tw + pad * 2, th + pad * 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - b[0], pad - b[1]), txt, font=f, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # ombre portée + contour épais sombre
    sh = Image.new("RGBA", (w, h), (10, 0, 20, 0))
    sh.putalpha(mask.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(10)))
    out.alpha_composite(sh, (0, 8))
    st = Image.new("RGBA", (w, h), (20, 6, 36, 0))
    st.putalpha(mask.filter(ImageFilter.MaxFilter(13)))
    out.alpha_composite(st)
    g = gta_gradient(w, h).copy()
    g.putalpha(mask)
    out.alpha_composite(g)
    return out


def _sticker(txt, bgcol=(255, 214, 92), fg=(24, 8, 40), size=58, angle=-4):
    f = font("InterDisplay-Black", size)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw, th, b = text_size(tmp, txt, f)
    w, h = tw + 70, th + 46
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], 22, fill=bgcol + (255,))
    d.text((20 + 35 - b[0], 20 + 23 - b[1]), txt, font=f, fill=fg + (255,))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(12)).point(lambda p: int(p * 0.6)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 8))
    out.alpha_composite(im)
    return out.rotate(angle, resample=Image.BICUBIC, expand=True)


def _badge():
    """Petit logo VCN en haut (dans la zone visible de la grille)."""
    f1, f2 = font("InterDisplay-Black", 46), font("Inter-SemiBold", 34)
    im = Image.new("RGBA", (420, 92), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 419, 91], 46, fill=(20, 8, 38, 225))
    g = gta_gradient(150, 92).copy()
    m = Image.new("L", (150, 92), 0)
    ImageDraw.Draw(m).text((28, 18), "VCN", font=f1, fill=255)
    g.putalpha(m)
    im.alpha_composite(g)
    d.text((150, 27), "GTA 6 · INFO", font=f2, fill=(255, 255, 255, 235))
    return im


def make_cover(key, photo, lines, sticker=None, focus=(0.5, 0.45), zoom=1.0, card=None):
    fr = _bg(photo, *focus, zoom=zoom)
    _shade(fr)
    b = _badge()
    fr.alpha_composite(b, ((W - b.width) // 2, 285))
    imgs = [_title_line(l, 230 if len(l) <= 9 else 200) for l in lines]
    step = 205
    y = 1610 - step * len(imgs) - 30          # bas du titre vers y≈1580 (dans la zone 3:4)
    if card is not None:
        fr.alpha_composite(card, ((W - card.width) // 2, y - card.height - 70))
    if sticker:
        s = _sticker(sticker)
        fr.alpha_composite(s, ((W - s.width) // 2, y - s.height + 40))
    for t in imgs:
        fr.alpha_composite(t, ((W - t.width) // 2, y))
        y += step
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"cover_{key}.jpg")
    fr.convert("RGB").save(p, quality=92)
    return p


def add_cover(video, cover_jpg, hold=0.35, fade=0.2):
    """Incruste la couverture sur les premières images (la vidéo, le son et la durée ne changent pas)."""
    tmp = video[:-4] + ".cover_tmp.mp4"
    fc = (f"[1:v]scale={W}:{H},format=rgba,fade=t=out:st={hold}:d={fade}:alpha=1[c];"
          f"[0:v][c]overlay=0:0:enable='lte(t,{hold + fade})',format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-loop", "1", "-t", str(hold + fade + 0.1),
                    "-framerate", "30", "-i", cover_jpg, "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "copy",
                    "-movflags", "+faststart", tmp], check=True)
    shutil.move(tmp, video)


COVERS = {
    "lucia": dict(photo="personnages/lucia_caminos_14.jpg", lines=["QUI EST", "LUCIA ?"],
                  sticker="1RE HÉROÏNE DE GTA", focus=(0.22, 0.4)),
}

if __name__ == "__main__":
    k = sys.argv[1]
    p = make_cover(k, **COVERS[k])
    print(p)
    if len(sys.argv) > 2 and sys.argv[2] == "apply":
        add_cover(os.path.join(D, "..", "videos", f"VCN_{k}.mp4"), p)
        print("incrustée")
