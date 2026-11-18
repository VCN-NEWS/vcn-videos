import sys, os
from PIL import Image, ImageDraw
import v2
from v2 import *
from scripts import TEXTS, DUR


def card_seg_full(builder, y=880):
    def fn(fr, lt, dur, tout):
        p = clamp((lt - 0.1) / max(1.0, dur * 0.6))  # listes : chaque ligne arrive avec la voix
        place(fr, shadowed(builder(p)), W / 2, y, lt, 0.0, tout, scale_from=0.9)
    return fn


def H_(txt, c1=(255, 150, 110), c2=(255, 70, 120)):
    return headline(txt, c1, c2, size=124)


def video_A():
    segs = [
        (0, "LA NOTE", H_("DÉJÀ MAL NOTÉ ?!"), card_seg(lambda p: score_badge("6.5", "Note des joueurs · Metacritic"))),
        (3, "LE PIÈGE", H_("PAS ENCORE SORTI !", (255, 230, 120), (255, 160, 60)), static_seg(calendar_card(19, "Sortie jeudi"))),
        (5, "LE PIÈGE", None, card_seg(users_card)),
        (6, "LE PIÈGE", H_("DÉJÀ DISPARUE", (255, 140, 150), (255, 60, 90)), card_seg(lambda p: score_badge("6.5", "Note des joueurs · Metacritic", stamp=clamp(p * 2.5 - 0.3)))),
        (7, "LA PRESSE", H_("LES VRAIES NOTES", (190, 160, 255), (255, 92, 170)), card_seg(lambda p: source_card("Notes de la presse", ["Attendues aujourd’hui", "la veille de la sortie"], p, warn="Date non confirmée par Rockstar"))),
        (10, "LES PARIS", H_("3 CHANCES SUR 4", (150, 255, 170), (60, 200, 140)), card_seg(gauge_card)),
        (11, "LE RECORD", H_("LE RECORD À BATTRE", (255, 220, 120), (255, 150, 80)),
         card_seg_full(lambda p: bars_card([("GTA 5", 17, BLUE, "97"), ("Red Dead Redemption 2", 17, (255, 160, 90), "97"), ("GTA 4 · record", 18, GOLD, "98")], p, title="Metascore (sur 100)", maxv=20))),
        (14, "LE DUEL", H_("GTA 6 VA-T-IL LE BATTRE ?", (255, 150, 110), (255, 70, 140)), card_seg(versus_card)),
        (16, "TON AVIS", None, card_seg(lambda p: comment_card("Ta note sur 100 ?", p, typed="97, facile"))),
    ]
    return Video("A", TEXTS["A"], DUR["A"], segs, PINK)


def video_B():
    segs = [
        (0, "LA TAILLE", H_("TA PS5 EST PRÊTE ?"), card_seg(lambda p: big_stat_card("210 Go", "le poids annoncé sur PS5"))),
        (2, "LA SOURCE", None, card_seg(lambda p: source_card("PlayStation Game Size", ["a trouvé ce chiffre dans", "les données du PlayStation Store"], p))),
        (4, "COMPARAISON", H_("PLUS DU DOUBLE", (255, 220, 120), (255, 150, 80)),
         card_seg_full(lambda p: bars_card([("GTA 5 (PS5)", 100, BLUE, "≈ 100 Go"), ("Red Dead Redemption 2", 105, (255, 160, 90), "≈ 105 Go"), ("GTA 6", 210, PINK, "210 Go")], p, maxv=210))),
        (6, "TA CONSOLE", H_("UN TIERS DE TA PS5", (190, 160, 255), (255, 92, 170)), card_seg(storage_card)),
        (8, "LE DISQUE", H_("PAS DE DISQUE !", (255, 140, 150), (255, 60, 90)), card_seg(box_card)),
        (10, "LE TÉLÉCHARGEMENT", H_("COMBIEN DE TEMPS ?", (150, 255, 170), (60, 200, 140)), card_seg_full(times_card)),
        (15, "PRÉCHARGEMENT", H_("FAIS-LE MAINTENANT", (255, 220, 120), (255, 150, 80)), card_seg(preload_card)),
        (17, "TON AVIS", None, card_seg(lambda p: comment_card("Il te reste combien de Go ?", p, typed="312 Go, ça passe"))),
    ]
    return Video("B", TEXTS["B"], DUR["B"], segs, (120, 230, 150))


SHOPS = [("Electric Fang Tattoo", "Salon de tatouage", PINK), ("Rideout Customs", "Garage de personnalisation", (255, 160, 90)),
         ("One-Eyed Willie’s", "Garage de personnalisation", (255, 160, 90)), ("Sara’s Unisex Salon", "Coiffeur", VIOLET), ("Stock 305", "Boutique de vêtements", BLUE)]


def video_C():
    segs = [
        (0, "LA STANDARD", H_("5 BOUTIQUES FERMÉES"), card_seg(map_pins_card)),
        (1, "LE PRIX", H_("20 DE PLUS", (255, 220, 120), (255, 150, 80)), card_seg(price_card)),
        (2, "LES BOUTIQUES", None, card_seg_full(lambda p: list_card(SHOPS, p, title="Réservé à l’Ultimate"))),
        (6, "LE DÉBLOCAGE", H_("CHAPITRE PAR CHAPITRE", (190, 160, 255), (255, 92, 170)), card_seg(chapters_card)),
        (7, "LES BONUS", H_("ET CE N’EST PAS TOUT", (255, 220, 120), (255, 150, 80)), card_seg(lambda p: chips_card(["Véhicules", "Armes", "Tenues", "Mission exclusive"], p, "Aussi dans l’Ultimate"))),
        (8, "À SAVOIR", H_("PAS DE PANIQUE", (150, 255, 170), (60, 200, 140)),
         card_seg_full(lambda p: list_card([("Histoire principale", "Identique dans les 2 éditions", GREEN), ("Boutiques classiques", "Probablement ouvertes à tous", GOLD)], p, icon="check"))),
        (12, "LES JOUEURS", H_("9 SUR 10", (255, 150, 110), (255, 70, 140)), card_seg(donut_card)),
        (15, "TON AVIS", None, card_seg(lambda p: comment_card("Standard ou Ultimate ?", p, typed="Ultimate, évidemment"))),
    ]
    return Video("C", TEXTS["C"], DUR["C"], segs, PINK)


def video_D():
    import math
    def clock_fn(p):
        sp = ease_out_cubic(clamp(p * 1.3))
        m = (1 - sp) * 4.5 * 2 * math.pi
        return clock_card(-m / 12, -m)
    segs = [
        (0, "LA SORTIE", H_("AUJOURD’HUI ?!"), static_seg(calendar_card(18, "Mercredi"))),
        (2, "LA SORTIE", None, card_seg(lambda p: calendar_card(19, "Jeudi"))),
        (3, "L’HEURE", H_("MINUIT, HEURE LOCALE", (190, 160, 255), (255, 92, 170)), card_seg(clock_fn)),
        (5, "LE MONDE", H_("NOUVELLE-ZÉLANDE"), card_seg(lambda p: big_stat_card("12 h", "d’avance sur la France"))),
        (8, "LE MONDE", H_("HEURE DE PARIS", (255, 255, 255), (205, 175, 255)), card_seg_full(lambda p: timeline_card(p * 4.6))),
        (12, "ASTUCE XBOX", H_("ASTUCE XBOX", (150, 255, 170), (60, 200, 140)), card_seg(lambda p: xbox_card(clamp(p * 1.5 - 0.3)))),
        (13, "SUR PS5", H_("ET SUR PS5 ?", (140, 190, 255), (90, 120, 255)), card_seg(lambda p: ps_card(clamp(p * 2 - 0.2), clamp(p * 2 - 1)))),
        (14, "ATTENTION", None, card_seg(lambda p: source_card("Horaires non officiels", ["Source : PlayStation Store", "Vérifie ton store ce soir"], p))),
        (15, "TON AVIS", None, card_seg(lambda p: comment_card("Minuit pile ou demain ?", p, typed="Minuit pile !"))),
    ]
    return Video("D", TEXTS["D"], DUR["D"], segs, VIOLET)


VIDEOS = {"A": video_A, "B": video_B, "C": video_C, "D": video_D}


# ---------- vidéo « notes » : GTA 6 à 99 sur Metacritic ----------
def crossed_badge(p):
    """6.5 barré en rouge, remplacé par 99."""
    im = score_badge("6.5", "L’ancienne note fantôme", col=(150, 140, 170))
    d = ImageDraw.Draw(im)
    a = ease_out_cubic(clamp(p * 2.2 - 0.4))
    if a > 0:
        x0, y0, x1, y1 = 120, 70, 440, 370
        d.line([(x0, y0), (x0 + (x1 - x0) * a, y0 + (y1 - y0) * a)], fill=RED + (255,), width=26)
    return im


def record_badge(p):
    im = score_badge("99", "Metascore · jour des tests", col=(255, 205, 90))
    a = ease_out_back(clamp(p * 2 - 0.6))
    if a > 0:
        c = chip("RECORD DU SITE", col=GREEN, size=40, h=84)
        c = c.resize((max(1, int(c.width * a)), max(1, int(c.height * a))), Image.BILINEAR)
        big = Image.new("RGBA", (im.width, im.height + 60), (0, 0, 0, 0))
        big.alpha_composite(im, (0, 0))
        big.alpha_composite(c, ((big.width - c.width) // 2, big.height - c.height))
        return big
    return im


def duel99_card(p):
    w, h = 900, 560
    im = card(w, h)
    d = ImageDraw.Draw(im)
    cols = [("Zelda", "Ocarina of Time", "Nintendo 64 · 1998", (110, 200, 255)), ("GTA 6", "Grand Theft Auto VI", "PS5 · Xbox · 2026", PINK)]
    for i, (n, sub, plat, col) in enumerate(cols):
        a = ease_out_back(clamp(p * 3 - i * 0.8))
        cx = 225 + i * 450
        s = int(220 * a)
        if s > 4:
            d.rounded_rectangle([cx - s / 2, 70, cx + s / 2, 70 + s], 34, fill=col + (255,))
            draw_center(d, cx, 70 + s * 0.17, "99", font("InterDisplay-Black", max(10, int(130 * a))), (20, 12, 30))
        if a > 0.5:
            draw_center(d, cx, 320, n, font("InterDisplay-Black", 58), WHITE)
            draw_center(d, cx, 395, sub, font("Inter-SemiBold", 32), MUTED)
            draw_center(d, cx, 445, plat, font("Inter-Bold", 30), col + (255,))
    draw_center(d, w / 2, 140, "=", font("InterDisplay-Black", 110), (255, 255, 255, int(255 * clamp(p * 3 - 1.4))))
    return im


def defect_card(n, title, sub, p, col=RED, note=None):
    w, h = 900, 500 if note else 420
    im = card(w, h)
    d = ImageDraw.Draw(im)
    a = ease_out_back(clamp(p * 2.5))
    r = int(80 * a)
    if r > 2:
        d.ellipse([w / 2 - r, 120 - r, w / 2 + r, 120 + r], fill=col + (255,))
        draw_center(d, w / 2, 120 - 62 * a, str(n), font("InterDisplay-Black", max(10, int(110 * a))), (20, 12, 30))
    b = clamp(p * 3 - 0.8)
    draw_center(d, w / 2, 230, title, font("InterDisplay-Black", 60), (255, 255, 255, int(255 * b)))
    draw_center(d, w / 2, 315, sub, font("Inter-SemiBold", 38), (220, 210, 255, int(255 * b)))
    if note:
        c = clamp(p * 3 - 1.6)
        f = font("Inter-Bold", 32)
        tw = d.textbbox((0, 0), note, font=f)[2]
        d.rounded_rectangle([w / 2 - tw / 2 - 30, 400, w / 2 + tw / 2 + 30, 458], 29, fill=(255, 205, 90, int(50 * c)), outline=(255, 205, 90, int(255 * c)), width=3)
        draw_center(d, w / 2, 411, note, f, (255, 205, 90, int(255 * c)))
    return im


def video_notes():
    G1, G2 = (255, 230, 120), (255, 150, 60)
    segs = [
        (0, "LE PIÈGE", H_("DE 6,5 À 99 ?!", G1, G2), card_seg(lambda p: score_badge("6.5", "L’ancienne note fantôme", col=(150, 140, 170)))),
        (2, "LE PIÈGE", H_("LE PIÈGE S’EST REFERMÉ", (255, 140, 150), (255, 60, 90)), card_seg(crossed_badge)),
        (3, "LES TESTS", H_("LES TESTS SONT TOMBÉS", (190, 160, 255), (255, 92, 170)), static_seg(calendar_card(18, "Mercredi midi"))),
        (4, "LA NOTE", H_("99 SUR 100", G1, G2), card_seg(record_badge)),
        (7, "LE RECORD", H_("UN SEUL AUTRE JEU", (140, 210, 255), (90, 130, 255)), card_seg(duel99_card)),
        (11, "LA SÉRIE", H_("L’ANCIEN ROI DÉTRÔNÉ", G1, G2),
         card_seg_full(lambda p: bars_card([("GTA 5", 7, BLUE, "97"), ("GTA 4 · ancien record", 8, (255, 160, 90), "98"), ("GTA 6", 9, GOLD, "99")], p, title="Metascore (sur 100)", maxv=9))),
        (13, "EN FRANCE", H_("LA CLAQUE EN FRANCE", (150, 255, 170), (60, 200, 140)), card_seg(lambda p: big_stat_card("19/20", "jeuxvideo.com"))),
        (15, "EN FRANCE", None, card_seg(lambda p: big_stat_card("9,5/10", "ActuGaming"))),
        (16, "MAIS…", H_("MAIS ATTENDS…", (255, 140, 150), (255, 60, 90)), card_seg(lambda p: big_stat_card("3", "défauts pointés par les tests"))),
        (19, "DÉFAUT N°1", H_("DÉFAUT N°1", (255, 140, 150), (255, 60, 90)), card_seg(lambda p: defect_card(1, "Missions scriptées", "Les missions principales, trop guidées", p))),
        (20, "DÉFAUT N°2", H_("DÉFAUT N°2", (255, 140, 150), (255, 60, 90)), card_seg(lambda p: defect_card(2, "Un début lent", "Il faut tenir tout le 1er chapitre", p, col=(255, 160, 90)))),
        (21, "DÉFAUT N°3", H_("LE PLUS GROS", (255, 140, 150), (255, 60, 90)), card_seg(lambda p: defect_card(3, "30 images/s", "Sur toutes les consoles", p, col=(255, 205, 90), note="Constaté par les tests"))),
        (22, "DÉFAUT N°3", H_("MÊME SUR PS5 PRO", (255, 140, 150), (255, 60, 90)), card_seg(lambda p: big_stat_card("30 FPS", "même sur la PS5 Pro"))),
        (23, "TON AVIS", H_("MÉRITÉ ?", G1, G2), card_seg(lambda p: score_badge("99", "Mérité… ou effet GTA ?", col=(255, 205, 90)))),
        (25, "TON AVIS", None, card_seg(lambda p: comment_card("Ta note sur 100 ?", p, typed="98, à cause des 30 fps"))),
    ]
    return Video("notes", TEXTS["notes"], DUR["notes"], segs, GOLD, tail=2.2, theme="sunset")


VIDEOS["notes"] = video_notes


# ---------------- format v3 (plein écran) ----------------
DUR["notes3"] = 61.780  # voix_notes3.mp3 = voix_notes.mp3 sans les blancs, x1.1


def video_notes3():
    from v3 import FullVideo
    L, P = "lieus/", "personnages/"
    G1, G2 = (255, 230, 120), (255, 150, 60)
    shots = [
        (0, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: score_badge("6.5", "L’ancienne note fantôme", col=(150, 140, 170))), "DE 6,5 À 99 ?!", None),
        (1, 0.0, ("photo", P + "lucia_caminos_04.jpg", 0.33, 0.4, 1.1), None, "LE PIÈGE"),
        (2, 0.0, ("card", L + "vice_city_17.jpg", 0.5, crossed_badge), "LE PIÈGE S’EST REFERMÉ", None),
        (3, 0.0, ("photo", L + "vice_city_11.jpg", 0.5, 0.5, 1.0), "LES TESTS SONT TOMBÉS", None),
        (4, 0.0, ("card", L + "vice_city_11.jpg", 0.5, record_badge), "99 SUR 100", None),
        (5, 0.0, ("photo", P + "jason_and_lucia_13.jpg", 0.46, 0.4, 1.0), "99 !", None),
        (6, 0.0, ("photo", P + "jason_and_lucia_01.jpg", 0.35, 0.4, 1.0), None, "RECORD ABSOLU"),
        (7, 0.0, ("card", L + "vice_city_08.jpg", 0.5, duel99_card), "UN SEUL AUTRE JEU", None),
        (9, 0.0, ("photo", L + "vice_city_24.jpg", 0.5, 0.5, 1.0), None, "EN 1998 !"),
        (11, 0.0, ("card", L + "vice_city_03.jpg", 0.5, lambda p: bars_card([("GTA 5", 7, BLUE, "97"), ("GTA 4 · ancien record", 8, (255, 160, 90), "98"), ("GTA 6", 9, GOLD, "99")], p, title="Metascore (sur 100)", maxv=9)), "L’ANCIEN ROI DÉTRÔNÉ", None),
        (13, 0.0, ("photo", L + "vice_city_05.jpg", 0.5, 0.5, 1.0), "LA CLAQUE EN FRANCE", None),
        (14, 0.0, ("card", L + "vice_city_10.jpg", 0.5, lambda p: big_stat_card("19/20", "jeuxvideo.com")), None, None),
        (15, 0.0, ("card", L + "vice_city_15.jpg", 0.5, lambda p: big_stat_card("9,5/10", "ActuGaming")), None, None),
        (16, 0.0, ("photo", P + "lucia_caminos_11.jpg", 0.76, 0.4, 1.1), "MAIS ATTENDS…", None),
        (17, 0.0, ("photo", P + "jason_and_lucia_12.jpg", 0.62, 0.4, 1.0), None, "MÊME UN 99…"),
        (18, 0.0, ("card", L + "vice_city_22.jpg", 0.5, lambda p: big_stat_card("3", "défauts pointés par les tests")), "3 DÉFAUTS", None),
        (19, 0.0, ("card", L + "vice_city_17.jpg", 0.5, lambda p: defect_card(1, "Missions scriptées", "Les missions principales, trop guidées", p)), "DÉFAUT N°1", None),
        (20, 0.0, ("card", L + "port_gellhorn_06.jpg", 0.5, lambda p: defect_card(2, "Un début lent", "Il faut tenir tout le 1er chapitre", p, col=(255, 160, 90))), "DÉFAUT N°2", None),
        (21, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: defect_card(3, "30 images/s", "Sur toutes les consoles", p, col=(255, 205, 90), note="Constaté par les tests")), "LE PLUS GROS", None),
        (21, 0.6, ("photo", P + "jason_and_lucia_09.jpg", 0.5, 0.4, 1.0), None, "30 IMAGES/S"),
        (22, 0.0, ("card", L + "vice_city_08.jpg", 0.5, lambda p: big_stat_card("30 FPS", "même sur la PS5 Pro")), "MÊME SUR PS5 PRO", None),
        (23, 0.0, ("photo", P + "lucia_caminos_14.jpg", 0.22, 0.38, 1.2), "ALORS, CE 99…", None),
        (24, 0.0, ("split", P + "jason_and_lucia_13.jpg", (0.46, 0.35), L + "vice_city_17.jpg", (0.5, 0.5), "MÉRITÉ", "EFFET GTA"), None, None),
        (25, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: comment_card("Ta note sur 100 ?", p, typed="98, à cause des 30 fps")), "TA NOTE ?", None),
        (26, 0.0, ("photo", L + "vice_city_08.jpg", 0.5, 0.5, 1.0), "ABONNE-TOI !", None),
    ]
    labels = {0: "LE PIÈGE", 4: "LA NOTE", 7: "LE RECORD", 10: "EN FRANCE", 13: "MAIS…", 16: "LES DÉFAUTS", 22: "TON AVIS"}
    return FullVideo("notes3", TEXTS["notes"], DUR["notes3"], shots, GOLD, labels=labels)


VIDEOS["notes3"] = video_notes3

if __name__ == "__main__":
    mode = sys.argv[1]
    keys = sys.argv[2].split(",")
    for k in keys:
        v = VIDEOS[k]()
        if mode == "preview":
            for (a, b), seg in zip(v.seg_times, v.segments):
                t = min(b - 0.4, a + 2.2)
                v.frame(t).convert("RGB").save(f"{D}/pv_{k}_{a:05.1f}.jpg", quality=85)
        elif mode == "render":
            v.render(f"{D}/silent_{k}.mp4")
        elif mode == "info":
            print(k, round(v.total, 2), [(round(a, 1), round(b, 1)) for a, b in v.seg_times], "audio" if v.has_audio else "estim")
