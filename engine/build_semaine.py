"""Production complète d'une vidéo v3 de la semaine : rendu, mixage, couverture incrustée, contrôles bloquants,
planche d'images (1 toutes les 4 s) et extrait des 10 dernières secondes.
Usage : python3 build_semaine.py boobie [astuces …]   (clé sans le « 3 »)"""
import sys, os, json, shutil, subprocess
import videos, finish, cover, controles
from PIL import Image

V = os.path.join(videos.D, "..", "videos")
OUT = os.path.join(videos.D, "..", "controles")


def build(base):
    k = base + "3"
    v = videos.VIDEOS[k]()
    silent = f"{videos.D}/silent_{k}.mp4"
    v.render(silent)
    mixed = f"{videos.D}/GTA6_{k}.mp4"
    finish.mix(k, v, silent, mixed)
    final = f"{V}/VCN_{base}_v3.mp4"
    shutil.copy(mixed, final)
    cfg = dict(cover.COVERS[k])
    cj = cover.make_cover(k, **cfg)
    cover.add_cover(final, cj)
    # contrôles bloquants
    res = controles.main(k, final, f"{videos.D}/voix_{base}.mp3")
    # planche : image 0 + 1 image toutes les 4 s
    d = controles.dur(final)
    ts = [0.0] + [t for t in range(4, int(d), 4)]
    thumbs = []
    for t in ts:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", final, "-frames:v", "1", "-vf", "scale=216:384", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        import io
        thumbs.append(Image.open(io.BytesIO(p)).convert("RGB"))
    cols = 8
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 216, rows * 384), (0, 0, 0))
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * 216, (i // cols) * 384))
    os.makedirs(OUT, exist_ok=True)
    sheet.save(f"{OUT}/planche_{base}.jpg", quality=80)
    # fin à écouter (10 dernières secondes)
    os.makedirs(f"{V}/fins", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-sseof", "-10", "-i", final, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", f"{V}/fins/VCN_{base}_v3_fin.mp4"], check=True)
    res["fichier"] = f"videos/VCN_{base}_v3.mp4"
    res["fin"] = f"videos/fins/VCN_{base}_v3_fin.mp4"
    res["couverture"] = f"covers/cover_{k}.jpg"
    json.dump(res, open(f"{OUT}/controles_{base}.json", "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    for f in (silent, mixed):
        if os.path.exists(f):
            os.remove(f)
    print("FINI", base, "TOUT_OK" if res["TOUT_OK"] else "ÉCHEC")


if __name__ == "__main__":
    for b in sys.argv[1:]:
        build(b)
