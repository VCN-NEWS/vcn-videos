"""Série « Qui est… ? » : personnages et lieux de GTA 6, à partir de la bibliothèque officielle."""
import os, sys, subprocess
import photo
from photo import PhotoVideo, headline, W, H
from v2 import PINK, VIOLET, GOLD, BLUE

D = os.path.dirname(os.path.abspath(__file__))

TEXTS = {
"lucia": "C'est la première héroïne de toute l'histoire de GTA… et elle sort de prison. "
         "Voici Lucia Caminos. "
         "C'est d'ailleurs le tout premier personnage que Rockstar a dévoilé, bien avant Jason. "
         "Quand GTA 6 commence, elle vient tout juste de sortir du pénitencier de Leonida. "
         "Son père lui a appris à se battre dès qu'elle a su marcher, et depuis, la vie ne lui a jamais fait de cadeau. "
         "Son rêve ? La belle vie dont sa mère parle depuis leurs années à Liberty City. "
         "Sauf que Lucia, elle, ne compte pas attendre : elle va la prendre elle-même. "
         "Pour ça, elle fait équipe avec Jason Duval. "
         "Un duo à la Bonnie et Clyde. "
         "Et Rockstar le dit clairement : dès le départ, tout est contre eux. "
         "Ils vont quand même tenter leur chance, ensemble. "
         "Bonne nouvelle : dans le jeu, tu pourras passer de Lucia à Jason quand tu veux, même en plein braquage. "
         "Alors, Lucia ou Jason, tu joues avec qui en premier ? "
         "Dis-le en commentaire, et abonne-toi pour découvrir tous les personnages de GTA 6.",
}
DUR = {"lucia": 57.469}  # durée réelle de la voix (s), à remplir quand le MP3 est là


def H_(t, c1=(255, 150, 110), c2=(255, 70, 140)):
    return headline(t, c1, c2, size=124)


def video_lucia():
    segs = [
        (0, "QUI EST-ELLE ?", H_("QUI EST LUCIA ?"), ("clip", "clips/lucia_caminos.mp4"), ("Lucia Caminos", "Protagoniste de GTA 6")),
        (3, "QUI EST-ELLE ?", H_("LA 1RE DÉVOILÉE", (190, 160, 255), (255, 92, 170)), ("photo", "personnages/lucia_caminos_10.jpg", (0.5, 0.4)), None),
        (4, "SON PASSÉ", H_("SORTIE DE PRISON", (255, 220, 120), (255, 150, 80)), ("photo", "personnages/lucia_caminos_05.jpg", (0.6, 0.4)), ("Pénitencier de Leonida", None)),
        (5, "SON PASSÉ", H_("UNE BAGARREUSE", (255, 140, 150), (255, 60, 90)), ("photo", "personnages/lucia_caminos_01.jpg", (0.5, 0.3)), None),
        (6, "SON RÊVE", H_("LA BELLE VIE", (150, 240, 255), (90, 160, 255)), ("photo", "personnages/lucia_caminos_02.jpg", (0.5, 0.5)), None),
        (8, "SON RÊVE", H_("ELLE VA LA PRENDRE", (255, 150, 110), (255, 70, 140)), ("photo", "personnages/lucia_caminos_13.jpg", (0.3, 0.4)), None),
        (9, "SON DUO", H_("BONNIE & CLYDE", (255, 150, 110), (255, 70, 140)), ("photo", "personnages/jason_and_lucia_01.jpg", (0.5, 0.3)), ("Jason & Lucia", "Le duo de GTA 6")),
        (11, "SON DUO", H_("TOUT CONTRE EUX", (190, 160, 255), (255, 92, 170)), ("photo", "personnages/jason_and_lucia_09.jpg", (0.5, 0.5)), None),
        (13, "EN JEU", H_("CHANGE DE PERSO", (150, 255, 170), (60, 200, 140)), ("photo", "personnages/jason_and_lucia_15.jpg", (0.5, 0.5)), None),
        (14, "TON AVIS", H_("LUCIA OU JASON ?"), ("photo", "personnages/jason_and_lucia_13.jpg", (0.5, 0.4)), None),
    ]
    dur = DUR["lucia"] or len(TEXTS["lucia"]) / 16.5
    return PhotoVideo("lucia", TEXTS["lucia"], dur, segs, PINK, tail=4.0)


VIDEOS = {"lucia": video_lucia}

if __name__ == "__main__":
    mode, k = sys.argv[1], sys.argv[2]
    v = VIDEOS[k]()
    if mode == "preview":
        for (a, b), s in zip(v.seg_times, v.segments):
            t = min(b - 0.3, a + 1.8)
            v.frame(t).convert("RGB").save(f"{D}/pv_{k}_{a:05.1f}.jpg", quality=85)
        print(round(v.total, 1), "s")
    elif mode == "render":
        import finish
        v.render(f"{D}/silent_{k}.mp4")
        finish.mix(k, v, f"{D}/silent_{k}.mp4", f"{D}/VCN_{k}.mp4")
        print("ok", round(v.total, 1), "s", "voix" if v.has_audio else "sans voix")
