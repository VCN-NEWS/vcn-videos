"""Série « Qui est… ? » : personnages et lieux de GTA 6, à partir de la bibliothèque officielle."""
import os, sys, subprocess
import photo
from photo import PhotoVideo, headline, W, H
from v2 import PINK, VIOLET, GOLD, BLUE

D = os.path.dirname(os.path.abspath(__file__))

TEXTS = {
"lucia": "Tu sais qui est la toute première héroïne de l'histoire de GTA ? "
         "Elle sort de prison… et elle s'appelle Lucia Caminos. "
         "Petit détail : c'est le tout premier personnage que Rockstar a dévoilé, bien avant Jason. "
         "Au début du jeu, elle sort à peine du pénitencier de Leonida. "
         "Et franchement, elle n'a pas eu une vie facile. "
         "Son père lui a appris à se battre… dès qu'elle a su marcher. "
         "Son rêve ? La belle vie dont sa mère lui parle depuis Liberty City. "
         "Sauf que Lucia, elle, n'attend pas. Elle va la prendre. "
         "Pour ça, elle s'associe avec Jason Duval. Un vrai duo à la Bonnie et Clyde. "
         "Et Rockstar le dit cash : dès le départ, tout est contre eux. "
         "Mais ils y vont quand même, ensemble. "
         "Et le meilleur ? Tu pourras passer de Lucia à Jason quand tu veux, même en plein braquage. "
         "Alors, Lucia ou Jason : tu commences avec qui ? "
         "Dis-le en commentaire, et abonne-toi pour découvrir tous les persos de GTA 6.",
}
# Texte envoyé à Hedra (avec balises d'expression ElevenLabs v3) ; les sous-titres utilisent TEXTS
VOICE = {
"lucia": TEXTS["lucia"]
    .replace("Tu sais qui est", "[curious] Tu sais qui est")
    .replace("Elle sort de prison…", "[whispers] Elle sort de prison…")
    .replace("Et le meilleur ?", "[excited] Et le meilleur ?")
    .replace("Alors, Lucia ou Jason", "[laughs] Alors, Lucia ou Jason"),
}
DUR = {"lucia": 59.794}  # durée réelle de la voix (s), à remplir quand le MP3 est là


def H_(t, c1=(255, 150, 110), c2=(255, 70, 140)):
    return headline(t, c1, c2, size=124)


def video_lucia():
    segs = [
        (0, "QUI EST-ELLE ?", H_("QUI EST LUCIA ?"), ("clip", "clips/lucia_caminos.mp4"), ("Lucia Caminos", "Protagoniste de GTA 6")),
        (3, "QUI EST-ELLE ?", H_("LA 1RE DÉVOILÉE", (190, 160, 255), (255, 92, 170)), ("photo", "personnages/lucia_caminos_10.jpg", (0.5, 0.4)), None),
        (4, "SON PASSÉ", H_("SORTIE DE PRISON", (255, 220, 120), (255, 150, 80)), ("photo", "personnages/lucia_caminos_05.jpg", (0.6, 0.4)), ("Pénitencier de Leonida", None)),
        (5, "SON PASSÉ", H_("UNE BAGARREUSE", (255, 140, 150), (255, 60, 90)), ("photo", "personnages/lucia_caminos_01.jpg", (0.5, 0.3)), None),
        (8, "SON RÊVE", H_("LA BELLE VIE", (150, 240, 255), (90, 160, 255)), ("photo", "personnages/lucia_caminos_02.jpg", (0.5, 0.5)), None),
        (10, "SON RÊVE", H_("ELLE VA LA PRENDRE", (255, 150, 110), (255, 70, 140)), ("photo", "personnages/lucia_caminos_13.jpg", (0.3, 0.4)), None),
        (12, "SON DUO", H_("BONNIE & CLYDE", (255, 150, 110), (255, 70, 140)), ("photo", "personnages/jason_and_lucia_01.jpg", (0.5, 0.3)), ("Jason & Lucia", "Le duo de GTA 6")),
        (14, "SON DUO", H_("TOUT CONTRE EUX", (190, 160, 255), (255, 92, 170)), ("photo", "personnages/jason_and_lucia_09.jpg", (0.5, 0.5)), None),
        (16, "EN JEU", H_("CHANGE DE PERSO", (150, 255, 170), (60, 200, 140)), ("photo", "personnages/jason_and_lucia_15.jpg", (0.5, 0.5)), None),
        (18, "TON AVIS", H_("LUCIA OU JASON ?"), ("photo", "personnages/jason_and_lucia_13.jpg", (0.5, 0.4)), None),
        (19, "TON AVIS", H_("ABONNE-TOI !", (255, 220, 120), (255, 150, 80)), ("photo", "personnages/jason_and_lucia_03.jpg", (0.5, 0.5)), None),
    ]
    dur = DUR["lucia"] or len(TEXTS["lucia"]) / 16.5
    return PhotoVideo("lucia", TEXTS["lucia"], dur, segs, PINK, tail=4.0)


VIDEOS = {"lucia": video_lucia}


# ---------------- format v3 (plein écran, plans de ~2 s) ----------------
DUR["lucia3"] = 51.174  # voix_lucia3.mp3 = voix_lucia.mp3 sans les blancs et accélérée x1.1


def video_lucia3():
    from v3 import FullVideo
    P = "personnages/"
    shots = [
        (0, 0.0, ("photo", P + "lucia_caminos_14.jpg", 0.22, 0.38, 1.25), "QUI EST LUCIA ?", None),
        (0, 0.55, ("photo", P + "lucia_caminos_13.jpg", 0.22, 0.3, 1.2), None, "1RE HÉROÏNE DE GTA"),
        (1, 0.0, ("photo", P + "lucia_caminos_05.jpg", 0.6, 0.35, 1.0), "SORTIE DE PRISON", None),
        (2, 0.0, ("clip", "clips/lucia_caminos.mp4", 0.56), None, "LUCIA CAMINOS"),
        (3, 0.0, ("photo", P + "lucia_caminos_10.jpg", 0.53, 0.4, 1.15), "1RE DÉVOILÉE", None),
        (3, 0.55, ("photo", P + "jason_and_lucia_01.jpg", 0.35, 0.4, 1.0), None, "AVANT JASON"),
        (4, 0.0, ("photo", P + "lucia_caminos_04.jpg", 0.33, 0.4, 1.1), None, "PÉNITENCIER DE LEONIDA"),
        (5, 0.0, ("photo", P + "lucia_caminos_11.jpg", 0.75, 0.4, 1.1), None, None),
        (6, 0.0, ("photo", P + "lucia_caminos_01.jpg", 0.66, 0.35, 1.15), "UNE BAGARREUSE", None),
        (7, 0.0, ("photo", P + "lucia_caminos_09.jpg", 0.5, 0.35, 1.1), None, None),
        (8, 0.0, ("photo", P + "lucia_caminos_02.jpg", 0.52, 0.35, 1.1), "SON RÊVE ?", None),
        (9, 0.0, ("photo", P + "lucia_caminos_06.jpg", 0.58, 0.35, 1.1), "LA BELLE VIE", None),
        (10, 0.0, ("photo", P + "lucia_caminos_07.jpg", 0.40, 0.35, 1.1), None, None),
        (11, 0.0, ("photo", P + "lucia_caminos_13.jpg", 0.22, 0.3, 1.45), "ELLE VA LA PRENDRE", None),
        (12, 0.0, ("photo", P + "jason_and_lucia_11.jpg", 0.62, 0.4, 1.0), None, "JASON DUVAL"),
        (13, 0.0, ("photo", P + "jason_and_lucia_13.jpg", 0.5, 0.4, 1.0), "BONNIE & CLYDE", None),
        (14, 0.0, ("photo", P + "jason_and_lucia_09.jpg", 0.5, 0.4, 1.0), "TOUT CONTRE EUX", None),
        (14, 0.5, ("photo", P + "jason_and_lucia_19.jpg", 0.56, 0.4, 1.0), None, None),
        (15, 0.0, ("photo", P + "jason_and_lucia_08.jpg", 0.3, 0.5, 1.0), None, None),
        (16, 0.0, ("photo", P + "jason_and_lucia_02.jpg", 0.46, 0.4, 1.0), "LE MEILLEUR ?", None),
        (17, 0.0, ("photo", P + "jason_and_lucia_15.jpg", 0.31, 0.4, 1.0), "CHANGE DE PERSO", None),
        (17, 0.5, ("photo", P + "jason_and_lucia_15.jpg", 0.62, 0.4, 1.0), "EN PLEIN BRAQUAGE", None),
        (18, 0.0, ("split", P + "lucia_caminos_13.jpg", (0.22, 0.32), P + "jason_and_lucia_01.jpg", (0.43, 0.3), "LUCIA", "JASON"), None, None),
        (19, 0.0, ("photo", P + "jason_and_lucia_16.jpg", 0.36, 0.5, 1.0), "ABONNE-TOI !", None),
    ]
    labels = {0: "QUI EST-ELLE ?", 2: "SON PASSÉ", 10: "SON RÊVE", 14: "SON DUO", 19: "EN JEU", 22: "TON AVIS"}
    return FullVideo("lucia3", TEXTS["lucia"], DUR["lucia3"], shots, PINK, labels=labels)


VIDEOS["lucia3"] = video_lucia3

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
