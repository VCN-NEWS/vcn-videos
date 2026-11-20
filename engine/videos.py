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
DUR["notes3"] = 61.884  # voix_notes3.mp3 = voix_notes.mp3 sans les blancs, x1.1


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


# ---------------- 20/11 18 h 30 : record de streaming (format v3) ----------------
DUR["stream3"] = 84.323  # voix_stream3.mp3 = voix_stream.mp3 coupée avant « Allez, ciao », sans les blancs, x1.1


def live_counter(p, value, unit, sub, col=(255, 70, 90)):
    """Compteur de spectateurs « EN DIRECT » qui grimpe jusqu'à value."""
    w, h = 900, 520
    im = card(w, h)
    d = ImageDraw.Draw(im)
    blink = 255 if int(p * 10) % 2 == 0 or p >= 1 else 120
    d.rounded_rectangle([w / 2 - 150, 40, w / 2 + 150, 110], 35, fill=col + (255,))
    d.ellipse([w / 2 - 120, 60, w / 2 - 90, 90], fill=(255, 255, 255, blink))
    d.text((w / 2 - 70, 50), "EN DIRECT", font=font("InterDisplay-Black", 44), fill=WHITE)
    v = value * ease_out_cubic(clamp(p * 1.4))
    txt = (f"{v:.1f}".replace(".", ",")) if value < 100 else f"{int(v)}"
    t = gradient_text(txt + " " + unit, font("InterDisplay-Black", 170), (255, 160, 110), (255, 70, 140))
    im.alpha_composite(t, ((w - t.width) // 2, 140))
    draw_center(d, w / 2, 420, sub, font("Inter-SemiBold", 42), MUTED)
    return im


def video_stream3():
    from v3 import FullVideo
    L, P = "lieus/", "personnages/"
    TW = (170, 120, 255)
    shots = [
        (0, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: live_counter(p, 7.9, "M", "spectateurs en même temps")), "RECORD HISTORIQUE", None),
        (1, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: score_badge("99", "Pas la note…", col=(150, 140, 170))), "PAS SA NOTE…", None),
        (2, 0.0, ("photo", P + "jason_and_lucia_01.jpg", 0.35, 0.4, 1.0), "ENCORE PLUS FOU", None),
        (3, 0.0, ("photo", P + "jason_and_lucia_14.jpg", 0.5, 0.4, 1.0), None, "4 CHIFFRES"),
        (4, 0.0, ("card", L + "vice_city_08.jpg", 0.5, lambda p: live_counter(p, 7.9, "M", "Twitch + YouTube + Kick + autres")), "N°1 : 7,9 MILLIONS", None),
        (5, 0.0, ("photo", L + "vice_city_13.jpg", 0.5, 0.5, 1.0), None, "EN LIVE, EN MÊME TEMPS"),
        (5, 0.55, ("photo", P + "jason_and_lucia_18.jpg", 0.5, 0.5, 1.0), None, "TOUTES PLATEFORMES"),
        (6, 0.0, ("card", L + "vice_city_03.jpg", 0.5, lambda p: big_stat_card("x 3,7", "la population de Paris")), "4 FOIS PARIS !", None),
        (7, 0.0, ("photo", L + "vice_city_01.jpg", 0.5, 0.5, 1.0), "JAMAIS VU", None),
        (8, 0.0, ("photo", P + "jason_and_lucia_02.jpg", 0.5, 0.4, 1.0), "N°2 : L'ANCIEN RECORD", None),
        (9, 0.0, ("card", L + "vice_city_17.jpg", 0.5, lambda p: bars_card([("Valorant · 2020", 1.74, BLUE, "1,7 M"), ("GTA 6 · 2026", 7.91, GOLD, "7,9 M")], p, title="Record de lancement (spectateurs)", maxv=7.91)), "VALORANT : 1,7 M", None),
        (10, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: big_stat_card("x 4,5", "l'ancien record")), "4,5 FOIS MIEUX !", None),
        (11, 0.0, ("photo", P + "lucia_caminos_14.jpg", 0.22, 0.38, 1.2), None, "TU AS BIEN ENTENDU"),
        (12, 0.0, ("card", L + "vice_city_25.jpg", 0.5, lambda p: live_counter(p, 3.3, "M", "rien que sur Twitch", col=(145, 70, 255))), "N°3 : TWITCH", None),
        (13, 0.0, ("photo", P + "jason_and_lucia_14.jpg", 0.3, 0.4, 1.2), "RECORD DE TWITCH", None),
        (14, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: bars_card([("GTA 6", 3.3, TW, "3,3 M"), ("League of Legends", 3.11, BLUE, "3,1 M"), ("Fortnite", 3.04, (120, 230, 150), "3,0 M")], p, title="Record Twitch d'un jeu (spectateurs)", maxv=3.3)), "LOL ET FORTNITE BATTUS", None),
        (15, 0.0, ("photo", L + "vice_city_02.jpg", 0.5, 0.45, 1.0), "ET LE JEU SOLO ?", None),
        (16, 0.0, ("card", L + "vice_city_15.jpg", 0.5, lambda p: big_stat_card("30 MIN", "pour battre Hogwarts Legacy")), "TOMBÉ EN 30 MIN", None),
        (17, 0.0, ("photo", P + "jason_and_lucia_09.jpg", 0.5, 0.4, 1.0), None, "CHRONO !"),
        (18, 0.0, ("photo", P + "jason_and_lucia_12.jpg", 0.62, 0.4, 1.0), "MAIS ATTENDS…", None),
        (19, 0.0, ("card", L + "vice_city_10.jpg", 0.5, lambda p: big_stat_card("1 MD $", "un milliard de dollars")), "N°4 : 1 MILLIARD", None),
        (20, 0.0, ("photo", P + "jason_and_lucia_02.jpg", 0.3, 0.45, 1.3), None, "ESTIMATION"),
        (20, 0.45, ("card", L + "vice_city_26.jpg", 0.5, lambda p: big_stat_card("11 M", "précommandes (estimation)")), "11 MILLIONS", None),
        (21, 0.0, ("photo", P + "jason_and_lucia_04.jpg", 0.5, 0.4, 1.0), "AVANT LA SORTIE !", None),
        (22, 0.0, ("photo", P + "jason_and_lucia_15.jpg", 0.4, 0.4, 1.1), None, "PERSONNE N'A JOUÉ"),
        (23, 0.0, ("card", L + "vice_city_15.jpg", 0.5, lambda p: bars_card([("GTA 5 · 2013", 3, BLUE, "3 jours"), ("GTA 6 · 2026", 0.3, GOLD, "avant la sortie")], p, title="Temps pour atteindre 1 milliard $", maxv=3)), "GTA 5 : 3 JOURS", None),
        (24, 0.0, ("card", L + "vice_city_22.jpg", 0.5, lambda p: source_card("Estimations", ["Ventes : Sensor Tower", "Streaming : Streams Charts"], p)), "ATTENTION", None),
        (25, 0.0, ("photo", L + "vice_city_08.jpg", 0.5, 0.5, 1.0), None, "ÇA PEUT ENCORE GRIMPER"),
        (26, 0.0, ("split", L + "vice_city_13.jpg", (0.5, 0.5), P + "jason_and_lucia_20.jpg", (0.5, 0.45), "LIVE", "MANETTE"), None, None),
        (28, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: comment_card("Live ou manette ?", p, typed="Manette en main à minuit")), "ABONNE-TOI !", None),
    ]
    labels = {0: "LE RECORD", 4: "N°1", 9: "N°2", 13: "N°3", 19: "N°4", 26: "LES SOURCES", 28: "TON AVIS"}
    return FullVideo("stream3", TEXTS["stream"], DUR["stream3"], shots, VIOLET, labels=labels)


VIDEOS["stream3"] = video_stream3


# ---------------- 21/11 : cartes communes ----------------
def stat_card(value, sub, p=1.0, c1=(255, 160, 110), c2=(255, 70, 140), sub2=None):
    """big_stat_card dont le chiffre se réduit pour tenir dans la carte."""
    w, h = 860, 560 if sub2 else 500
    im = card(w, h)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    size = 220
    while size > 90:
        f = font("InterDisplay-Black", size)
        if text_size(tmp, value, f)[0] <= w - 100:
            break
        size -= 8
    a = ease_out_back(clamp(p * 2.5))
    t = gradient_text(value, f, c1, c2)
    if a > 0.02:
        t2 = t.resize((max(1, int(t.width * a)), max(1, int(t.height * a))), Image.BILINEAR)
        im.alpha_composite(t2, ((w - t2.width) // 2, 20 + (t.height - t2.height) // 2 + (220 - size) // 2))
    d = ImageDraw.Draw(im)
    b = clamp(p * 3 - 0.6)
    draw_center(d, w / 2, 370, sub, font("Inter-SemiBold", 44), (200, 190, 230, int(255 * b)))
    if sub2:
        draw_center(d, w / 2, 440, sub2, font("Inter-Bold", 36), (255, 205, 90, int(255 * b)))
    return im


def counter_card(p, value, unit, sub, col=(255, 70, 90), dec=1, head="JOUR 1"):
    w, h = 900, 520
    im = card(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([w / 2 - 130, 40, w / 2 + 130, 110], 35, fill=col + (255,))
    draw_center(d, w / 2, 52, head, font("InterDisplay-Black", 44), WHITE)
    v = value * ease_out_cubic(clamp(p * 1.4))
    txt = f"{v:.{dec}f}".replace(".", ",") + " " + unit
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    size = 170
    while size > 90 and text_size(tmp, txt, font("InterDisplay-Black", size))[0] > w - 100:
        size -= 8
    t = gradient_text(txt, font("InterDisplay-Black", size), (255, 160, 110), (255, 70, 140))
    im.alpha_composite(t, ((w - t.width) // 2, 140 + (170 - size) // 2))
    draw_center(d, w / 2, 420, sub, font("Inter-SemiBold", 42), MUTED)
    return im


def crossed_stat(value, sub, p):
    im = stat_card(value, sub, 1.0, c1=(170, 160, 190), c2=(120, 110, 150))
    d = ImageDraw.Draw(im)
    a = ease_out_cubic(clamp(p * 2.2 - 0.3))
    if a > 0:
        x0, y0, x1, y1 = 110, 300, 750, 70
        d.line([(x0, y0), (x0 + (x1 - x0) * a, y0 + (y1 - y0) * a)], fill=RED + (255,), width=28)
    return im


def gps_card(p, stage):
    """Écran de GPS de bateau : « LEONIDA » barré (stage 0) puis « LOS SANTOS » (stage 1)."""
    w, h = 860, 600
    im = card(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 60, w - 60, h - 150], 30, fill=(10, 40, 50, 255), outline=(90, 230, 210, 255), width=5)
    for k in range(1, 6):  # grille de carte
        x = 60 + k * (w - 120) / 6
        d.line([(x, 60), (x, h - 150)], fill=(90, 230, 210, 60), width=2)
    for k in range(1, 4):
        y = 60 + k * (h - 210) / 4
        d.line([(60, y), (w - 60, y)], fill=(90, 230, 210, 60), width=2)
    d.text((90, 80), "GPS · NAVIGATION", font=font("Inter-Bold", 30), fill=(90, 230, 210, 255))
    cy = 60 + (h - 210) / 2 + 10
    if stage == 0:
        draw_center(d, w / 2, cy - 40, "LEONIDA ?", font("InterDisplay-Black", 100), (180, 200, 210, 255))
        a = ease_out_cubic(clamp(p * 2.4 - 0.6))
        if a > 0:
            d.line([(150, cy + 60), (150 + (w - 300) * a, cy - 50 - 0 * a)], fill=RED + (255,), width=22)
        sub = "Il n’affiche pas Leonida…"
    else:
        a = ease_out_back(clamp(p * 2.5))
        t = gradient_text("LOS SANTOS", font("InterDisplay-Black", 110), (150, 255, 220), (90, 200, 255))
        if a > 0.02:
            t2 = t.resize((max(1, int(t.width * a)), max(1, int(t.height * a))), Image.BILINEAR)
            im.alpha_composite(t2, ((w - t2.width) // 2, int(cy - t2.height / 2)))
        sub = "La ville de GTA 5"
    draw_center(d, w / 2, h - 110, sub, font("Inter-SemiBold", 44), MUTED)
    return im


def polaroid_card(p, ufo):
    """Polaroïd « photo mystère » : maison + palmiers, puis un OVNI qui apparaît (dessin VCN)."""
    w, h = 760, 860
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 18, fill=(248, 244, 236, 255))
    from v3 import _src, _crop
    ph = _crop(_src("lieus/port_gellhorn_06.jpg"), 0.42, 0.6, 1.6, 680, 620).convert("RGBA")
    if ufo:
        a = ease_out_cubic(clamp(p * 2.0))
        u = Image.new("RGBA", ph.size, (0, 0, 0, 0))
        ud = ImageDraw.Draw(u)
        cx, cy = 430, int(150 + 40 * (1 - a))
        al = int(255 * a)
        ud.polygon([(cx - 60, cy + 30), (cx + 60, cy + 30), (cx + 150, cy + 260), (cx - 150, cy + 260)], fill=(180, 255, 200, int(70 * a)))
        ud.ellipse([cx - 120, cy - 10, cx + 120, cy + 40], fill=(70, 75, 90, al))
        ud.ellipse([cx - 55, cy - 50, cx + 55, cy + 20], fill=(170, 230, 255, al))
        for k in range(-2, 3):
            ud.ellipse([cx + k * 42 - 8, cy + 10, cx + k * 42 + 8, cy + 26], fill=(255, 230, 120, al))
        u = u.filter(ImageFilter.GaussianBlur(0.8))
        ph.alpha_composite(u)
    im.alpha_composite(ph, (40, 40))
    draw_center(d, w / 2, 700, "Photo mystère · 2021", font("Inter-Bold", 44), (40, 30, 60, 255))
    draw_center(d, w / 2, 765, "GTA San Andreas Definitive Edition", font("Inter-SemiBold", 32), (90, 80, 110, 255))
    return im.rotate(-3, resample=Image.BICUBIC, expand=True)


def notes_card(p, lines, title="SES NOTES"):
    """Bloc-notes jaune du complotiste : lignes qui s'écrivent une par une."""
    w = 860
    h = 170 + 92 * len(lines)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=(255, 238, 150, 255))
    d.rectangle([0, 0, w, 90], fill=(240, 90, 90, 255))
    draw_center(d, w / 2, 22, title, font("InterDisplay-Black", 48), (255, 255, 255, 255))
    for i, (txt, col) in enumerate(lines):
        y = 130 + i * 92
        d.line([(40, y + 66), (w - 40, y + 66)], fill=(120, 150, 220, 120), width=2)
        a = clamp(p * (len(lines) + 0.5) - i)
        n = int(len(txt) * a)
        d.text((50, y), txt[:n], font=font("Inter-Bold", 46), fill=col + (255,))
    return im.rotate(2, resample=Image.BICUBIC, expand=True)


# ---------------- 21/11 12 h 30 : 4 secrets cachés (format v3, type « secrets ») ----------------
DUR["secrets3"] = 92.865  # voix_secrets3.mp3 = voix_secrets.mp3 coupée avant « Allez, ciao », sans les blancs, x1.1


def video_secrets3():
    from v3 import FullVideo
    L, P = "lieus/", "personnages/"
    NOTE = (40, 30, 70)
    NL = [("✗ Fuir Leonida", NOTE), ("✗ Billet pour Los Santos", NOTE), ("Passants identiques ?!", NOTE), ("Gens à travers les murs", NOTE), ("J et L…", (220, 40, 60))]
    shots = [
        (0, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: stat_card("4", "secrets cachés dans GTA 6", p, sub2="Trouvés en 48 h")), "4 SECRETS CACHÉS", None),
        (1, 0.0, ("photo", P + "jason_and_lucia_01.jpg", 0.45, 0.4, 1.05), None, "SORTI IL Y A 2 JOURS"),
        (2, 0.0, ("photo", L + "vice_city_09.jpg", 0.42, 0.5, 1.0), "DÉJÀ TROUVÉS", None),
        (3, 0.0, ("photo", P + "lucia_caminos_14.jpg", 0.22, 0.38, 1.2), "LE DERNIER EST FOU", None),
        (4, 0.0, ("photo", L + "vice_city_15.jpg", 0.62, 0.5, 1.0), "N°1 : LE BATEAU", None),
        (5, 0.0, ("photo", P + "jason_duval_03.jpg", 0.25, 0.4, 1.05), None, "DEVANT CHEZ JASON"),
        (6, 0.0, ("card", L + "leonida_keys_01.jpg", 0.5, lambda p: gps_card(0.0, 0)), "REGARDE SON GPS", None),
        (7, 0.0, ("card", L + "leonida_keys_01.jpg", 0.5, lambda p: gps_card(p, 0)), None, None),
        (8, 0.0, ("card", L + "vice_city_15.jpg", 0.5, lambda p: gps_card(p, 1)), "LOS SANTOS !", None),
        (9, 0.0, ("photo", L + "vice_city_17.jpg", 0.42, 0.6, 1.1), "CLIN D’ŒIL À GTA 5", "LE BATEAU DE MICHAEL ?"),
        (10, 0.0, ("photo", L + "vice_city_08.jpg", 0.5, 0.5, 1.0), "N°2 : DEXTER", None),
        (11, 0.0, ("photo", L + "vice_city_10.jpg", 0.36, 0.45, 1.0), "TRINITY APARTMENTS", "VICE BEACH"),
        (12, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: source_card("Série Dexter", ["Trinity : le tueur", "de la saison 4"], p, warn=None)), "RÉFÉRENCE À DEXTER", None),
        (13, 0.0, ("card", L + "vice_city_11.jpg", 0.3, lambda p: chips_card(["Corde", "Ruban adhésif", "Gants", "Seringue"], p, "Sur le toit de l’immeuble")), "SUR LE TOIT", None),
        (15, 0.0, ("photo", L + "vice_city_15.jpg", 0.85, 0.6, 1.1), "VOLE SON BATEAU", "SLICE OF LIFE"),
        (16, 0.0, ("photo", L + "mount_kalaga_national_park_02.jpg", 0.55, 0.45, 1.0), "N°3 : L’ŒUF DE PÂQUES", None),
        (17, 0.0, ("card", L + "vice_city_22.jpg", 0.55, lambda p: stat_card("7 MIN", "d’escalade", p, sub2="Tout en haut d’une tour radio")), "UNE TOUR GÉANTE", None),
        (18, 0.0, ("photo", L + "ambrosia_04.jpg", 0.46, 0.4, 1.3), None, "UN NID D’OISEAU"),
        (19, 0.0, ("photo", L + "vice_city_11.jpg", 0.3, 0.5, 1.0), None, "TU LE LANCES…"),
        (20, 0.0, ("photo", L + "vice_city_26.jpg", 0.5, 0.5, 1.0), "CINÉMATIQUE SECRÈTE", None),
        (21, 0.0, ("photo", L + "vice_city_24.jpg", 0.6, 0.5, 1.0), "SPLASH !", None),
        (22, 0.0, ("photo", L + "vice_city_01.jpg", 0.45, 0.5, 1.0), "CLIN D’ŒIL À VICE CITY", "L’ŒUF CACHÉ DE 2002"),
        (23, 0.0, ("photo", P + "jason_and_lucia_12.jpg", 0.62, 0.4, 1.0), "MAIS ATTENDS…", None),
        (24, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: stat_card("5 ANS", "de mystère", p)), "N°4 : LA PHOTO CACHÉE", None),
        (25, 0.0, ("card", L + "ambrosia_02.jpg", 0.5, lambda p: source_card("GTA San Andreas", ["Definitive Edition · 2021", "Une photo accrochée au mur…"], p, warn=None)), "EN 2021…", None),
        (25, 0.55, ("photo", L + "vice_city_08.jpg", 0.3, 0.5, 1.0), None, "UNE PHOTO MYSTÉRIEUSE"),
        (26, 0.0, ("card", L + "ambrosia_02.jpg", 0.5, lambda p: polaroid_card(p, False)), "UNE MAISON…", None),
        (27, 0.0, ("card", L + "ambrosia_02.jpg", 0.5, lambda p: polaroid_card(p, True)), "UN OVNI !", None),
        (28, 0.0, ("photo", L + "port_gellhorn_06.jpg", 0.42, 0.55, 1.0), "ELLE EXISTE !", "BELVILLE, LEONIDA"),
        (29, 0.0, ("card", L + "vice_city_22.jpg", 0.5, lambda p: notes_card(0.0, NL)), "LA PLANQUE", "UN COMPLOTISTE"),
        (30, 0.0, ("card", L + "vice_city_22.jpg", 0.5, lambda p: notes_card(p * 0.2, NL)), "FUIR LEONIDA", None),
        (31, 0.0, ("photo", L + "vice_city_01.jpg", 0.42, 0.25, 1.4), "BILLET IMPOSSIBLE", None),
        (32, 0.0, ("photo", L + "vice_city_09.jpg", 0.7, 0.5, 1.0), "PASSANTS IDENTIQUES", None),
        (32, 0.55, ("card", L + "vice_city_22.jpg", 0.5, lambda p: notes_card(0.4 + p * 0.4, NL)), "À TRAVERS LES MURS", None),
        (33, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: stat_card("J + L", "écrit dans ses notes", p)), "J ET L", None),
        (34, 0.0, ("photo", P + "jason_and_lucia_01.jpg", 0.45, 0.4, 1.0), "JASON ET LUCIA ?!", None),
        (35, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: source_card("Découvertes de joueurs", ["xGarbett · DETONATED", "GTA VI Mapping"], p)), "ATTENTION", None),
        (36, 0.0, ("card", L + "vice_city_15.jpg", 0.5, lambda p: comment_card("Tu testes lequel en 1er ?", p, typed="L’œuf, direct !")), "LEQUEL EN 1ER ?", None),
        (37, 0.0, ("photo", P + "jason_and_lucia_13.jpg", 0.46, 0.4, 1.0), "ABONNE-TOI !", None),
    ]
    lab_at = {0: "4 SECRETS", 4: "N°1 · LE BATEAU", 10: "N°2 · DEXTER", 16: "N°3 · L’ŒUF", 24: "N°4 · LA PHOTO", 35: "TON AVIS"}
    labels = {}
    for i, sh in enumerate(shots):
        if sh[0] in lab_at and sh[1] == 0.0:
            labels[i] = lab_at[sh[0]]
    return FullVideo("secrets3", TEXTS["secrets"], DUR["secrets3"], shots, (120, 230, 150), labels=labels)


VIDEOS["secrets3"] = video_secrets3


# ---------------- 21/11 18 h 30 : ventes du 1er jour (format v3, actu) ----------------
DUR["ventes3"] = 101.068  # voix_ventes3.mp3 = voix_ventes.mp3 coupée avant « Allez, ciao », sans les blancs, x1.1


def video_ventes3():
    from v3 import FullVideo
    L, P = "lieus/", "personnages/"
    G6 = GOLD
    shots = [
        (0, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: counter_card(p, 2.36, "MD $", "de ventes en un seul jour", dec=2)), "MIEUX QU’AVENGERS ?!", None),
        (1, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: stat_card("1 MD $", "de précommandes", p, sub2="Ce qu’on te disait hier")), "HIER…", None),
        (2, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: crossed_stat("1 MD $", "de précommandes", p)), "OUBLIE ÇA", None),
        (3, 0.0, ("photo", P + "jason_and_lucia_01.jpg", 0.45, 0.4, 1.05), "LE VRAI BILAN", None),
        (3, 0.5, ("photo", L + "vice_city_10.jpg", 0.36, 0.45, 1.0), None, "PREMIER JOUR"),
        (4, 0.0, ("photo", P + "jason_and_lucia_14.jpg", 0.5, 0.4, 1.0), None, "5 CHIFFRES"),
        (5, 0.0, ("card", L + "vice_city_08.jpg", 0.5, lambda p: counter_card(p, 24.6, "M", "copies vendues")), "N°1 : 24,6 MILLIONS", None),
        (6, 0.0, ("photo", L + "vice_city_13.jpg", 0.5, 0.5, 1.0), None, "EN UN SEUL JOUR"),
        (6, 0.5, ("photo", P + "jason_and_lucia_03.jpg", 0.5, 0.45, 1.0), None, "PRÉCOMMANDES COMPRISES"),
        (7, 0.0, ("card", L + "vice_city_03.jpg", 0.5, lambda p: stat_card("1 SUR 3", "comme si 1 Français sur 3", p, sub2="l’avait acheté")), "1 FRANÇAIS SUR 3 !", None),
        (8, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: counter_card(p, 2.36, "MD $", "de chiffre d’affaires", dec=2)), "N°2 : 2,36 MILLIARDS", None),
        (9, 0.0, ("card", L + "vice_city_15.jpg", 0.5, lambda p: stat_card("24 H", "chrono", p)), "EN 24 HEURES", None),
        (10, 0.0, ("photo", P + "lucia_caminos_14.jpg", 0.22, 0.38, 1.2), None, "OUI, MILLIARDS"),
        (11, 0.0, ("photo", L + "vice_city_03.jpg", 0.5, 0.5, 1.0), "N°3 : GTA 5", "LA REVANCHE"),
        (12, 0.0, ("card", L + "vice_city_17.jpg", 0.5, lambda p: stat_card("11,2 M", "copies le 1er jour", p, c1=(140, 210, 255), c2=(90, 130, 255), sub2="GTA 5 · 2013")), "GTA 5 EN 2013", None),
        (12, 0.55, ("card", L + "vice_city_17.jpg", 0.5, lambda p: stat_card("815 M $", "le 1er jour", p, c1=(140, 210, 255), c2=(90, 130, 255), sub2="GTA 5 · 2013")), None, None),
        (13, 0.0, ("card", L + "vice_city_10.jpg", 0.5, lambda p: bars_card([("GTA 5 · 2013", 11.2, BLUE, "11,2 M"), ("GTA 6 · 2026", 24.6, G6, "24,6 M")], p, title="Copies vendues le 1er jour", maxv=24.6)), "PLUS DU DOUBLE", None),
        (14, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: bars_card([("GTA 5 · 2013", 0.815, BLUE, "815 M $"), ("GTA 6 · 2026", 2.36, G6, "2,36 Md $")], p, title="Argent gagné le 1er jour", maxv=2.36)), "PRESQUE x 3", None),
        (15, 0.0, ("photo", L + "vice_city_01.jpg", 0.45, 0.5, 1.0), "N°4 : LE CINÉMA", None),
        (16, 0.0, ("photo", L + "vice_city_13.jpg", 0.35, 0.5, 1.1), None, "RECORD DU CINÉMA"),
        (16, 0.42, ("card", L + "vice_city_08.jpg", 0.5, lambda p: stat_card("1,22 MD $", "tout un week-end", p, c1=(140, 210, 255), c2=(90, 130, 255), sub2="Avengers Endgame · 2019")), "AVENGERS ENDGAME", None),
        (17, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: bars_card([("Endgame · 1 week-end", 1.22, BLUE, "1,22 Md $"), ("GTA 6 · 1 jour", 2.36, G6, "2,36 Md $")], p, title="Plus gros démarrages (monde)", maxv=2.36)), "PRESQUE LE DOUBLE", None),
        (18, 0.0, ("photo", P + "jason_and_lucia_09.jpg", 0.5, 0.4, 1.0), None, "EN UN SEUL JOUR"),
        (19, 0.0, ("photo", L + "vice_city_11.jpg", 0.62, 0.45, 1.0), "RECORD HISTORIQUE", None),
        (20, 0.0, ("photo", P + "jason_and_lucia_20.jpg", 0.62, 0.4, 1.0), "N°5 : LA CONSOLE", None),
        (21, 0.0, ("card", L + "vice_city_25.jpg", 0.5, lambda p: stat_card("3 SUR 4", "des copies sur PS5", p)), "LA PS5 ÉCRASE TOUT", None),
        (22, 0.0, ("card", L + "vice_city_08.jpg", 0.5, lambda p: bars_card([("PS5", 18.44, BLUE, "18,4 M"), ("Xbox Series", 6.15, GREEN, "6,15 M")], p, title="Copies le 1er jour (estimation)", maxv=18.44)), "PS5 VS XBOX", None),
        (22, 0.62, ("photo", P + "jason_and_lucia_11.jpg", 0.55, 0.45, 1.0), None, "6,15 M SUR XBOX"),
        (23, 0.0, ("photo", P + "jason_and_lucia_06.jpg", 0.62, 0.45, 1.0), "ET SUR PC ?", None),
        (24, 0.0, ("card", L + "vice_city_22.jpg", 0.5, lambda p: stat_card("0", "copie sur PC", p)), "ZÉRO", None),
        (25, 0.0, ("photo", L + "vice_city_22.jpg", 0.55, 0.5, 1.0), None, "PAS DE VERSION PC"),
        (26, 0.0, ("photo", P + "jason_and_lucia_12.jpg", 0.62, 0.4, 1.0), "MAIS ATTENDS…", None),
        (27, 0.0, ("card", L + "vice_city_10.jpg", 0.5, lambda p: stat_card("65 M", "copies d’ici fin mars", p, sub2="Prévision Wells Fargo")), "65 MILLIONS ?", None),
        (28, 0.0, ("card", L + "vice_city_15.jpg", 0.5, lambda p: bars_card([("Prévision d’avant", 35, BLUE, "35 M"), ("Nouvelle prévision", 65, G6, "65 M")], p, title="Wells Fargo · d’ici fin mars", maxv=65)), "PRÉVISION DOUBLÉE", None),
        (29, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: source_card("Version PC", ["Début 2027 ?", "Selon Wells Fargo"], p, warn="Non annoncée par Rockstar")), "PC : PAS ANNONCÉ", None),
        (30, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: source_card("Estimations", ["Ventes : Sensor Tower", "Prévision : Wells Fargo"], p, warn="Aucun chiffre officiel")), "ATTENTION", None),
        (31, 0.0, ("photo", L + "vice_city_10.jpg", 0.62, 0.45, 1.0), None, "TAKE-TWO SE TAIT"),
        (32, 0.0, ("split", P + "jason_and_lucia_20.jpg", (0.5, 0.45), L + "vice_city_08.jpg", (0.5, 0.5), "24 MILLIONS", "VERSION PC"), None, None),
        (34, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: comment_card("Console ou PC ?", p, typed="Déjà 10 h de jeu !")), "ABONNE-TOI !", None),
    ]
    lab_at = {0: "LE BILAN", 5: "N°1", 8: "N°2", 11: "N°3", 15: "N°4", 20: "N°5", 26: "ET APRÈS ?", 30: "LES SOURCES", 32: "TON AVIS"}
    labels = {}
    for i, sh in enumerate(shots):
        if sh[0] in lab_at and sh[1] == 0.0:
            labels[i] = lab_at[sh[0]]
    return FullVideo("ventes3", TEXTS["ventes"], DUR["ventes3"], shots, GOLD, labels=labels)


VIDEOS["ventes3"] = video_ventes3

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
