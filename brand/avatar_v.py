"""Photo de profil finale VCN : monogramme V (idée n°6), version peaufinée."""
import math
from PIL import Image, ImageDraw, ImageFilter
from avatars_idees import S, F, vgrad, multigrad, text_mask, fill, glow, gta_grad, PINK, VIOLET

def spaced(txt, font, y, spacing):
    m = Image.new("L", (S, S), 0); d = ImageDraw.Draw(m)
    widths = [d.textlength(c, font=font) for c in txt]
    total = sum(widths) + spacing * (len(txt) - 1)
    x = (S - total) / 2
    for c, w in zip(txt, widths):
        d.text((x, y), c, font=font, fill=255, anchor="lm"); x += w + spacing
    return m

def sparkle(d, x, y, r, col):
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22), (x, y + r), (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=col)

im = vgrad((24, 8, 44), (52, 12, 84))
# halo central
halo = Image.new("L", (S, S), 0); ImageDraw.Draw(halo).ellipse([240, 200, 840, 800], fill=120)
glow(im, halo, (255, 80, 170), 140, 1.0)
# anneau
ring = Image.new("L", (S, S), 0); ImageDraw.Draw(ring).ellipse([96, 96, 984, 984], outline=255, width=30)
glow(im, ring, PINK, 34, 1.7)
im.alpha_composite(fill(ring, gta_grad()))
# V
v = text_mask("V", F("InterDisplay-BlackItalic", 640), xy=(556, 488))
glow(im, v, VIOLET, 46, 1.6)
im.alpha_composite(fill(v.filter(ImageFilter.MaxFilter(27)), Image.new("RGBA", (S, S), (12, 4, 24, 255))))
im.alpha_composite(fill(v, multigrad([(255, 255, 255), (255, 214, 236), (255, 95, 175), (160, 85, 240)])))
# reflet
hl = Image.new("L", (S, S), 0); ImageDraw.Draw(hl).polygon([(330, 230), (470, 230), (420, 330), (285, 330)], fill=110)
hl = Image.fromarray(__import__("numpy").minimum(__import__("numpy").array(hl), __import__("numpy").array(v)))
im.alpha_composite(fill(hl, Image.new("RGBA", (S, S), (255, 255, 255, 255))))
# CITY NEWS
t = spaced("CITY NEWS", F("InterDisplay-Black", 74), 838, 14)
im.alpha_composite(fill(t.filter(ImageFilter.MaxFilter(9)), Image.new("RGBA", (S, S), (12, 4, 24, 255))))
im.alpha_composite(fill(t, Image.new("RGBA", (S, S), (255, 255, 255, 255))))
d = ImageDraw.Draw(im)
sparkle(d, 790, 250, 34, (255, 255, 255, 255)); sparkle(d, 262, 640, 22, (255, 220, 240, 255)); sparkle(d, 835, 640, 16, (255, 220, 240, 230))
im = im.convert("RGB")
im.save("vcn_profil_V_1080.png")
im.resize((800, 800), Image.LANCZOS).save("vcn_profil_V_youtube_800.png")
# aperçu
circ = Image.new("L", (S, S), 0); ImageDraw.Draw(circ).ellipse([0, 0, S - 1, S - 1], fill=255)
c = im.copy(); c.putalpha(circ)
pv = Image.new("RGB", (900, 420), (245, 245, 248)); pd = ImageDraw.Draw(pv)
for size, x in ((360, 30), (160, 440), (72, 650), (40, 770)):
    s = c.resize((size, size), Image.LANCZOS); pv.paste(s, (x, 30 + (360 - size) // 2), s)
pd.text((30, 395), "Aperçu : grand, profil, commentaires, suggestions", font=F("Inter-Regular", 20), fill=(110, 110, 120))
dark = Image.new("RGB", (900, 120), (18, 18, 22)); s = c.resize((72, 72), Image.LANCZOS); dark.paste(s, (30, 24), s)
ImageDraw.Draw(dark).text((120, 60), "vcn_news_fr · fond sombre", font=F("Inter-SemiBold", 30), fill=(240, 240, 245), anchor="lm")
full = Image.new("RGB", (900, 540)); full.paste(pv, (0, 0)); full.paste(dark, (0, 420)); full.save("apercu_profil_V.png")
print("ok")
