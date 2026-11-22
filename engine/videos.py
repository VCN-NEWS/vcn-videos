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

# ---------------- 22/11 12 h 30 : Qui est Raul Bautista ? (format v3, portrait) ----------------
DUR["raul3"] = 92.082  # voix_raul3.mp3 = voix_raul.mp3 coupée avant « Allez, ciao » (108,1 s), sans les blancs, x1.1


def video_raul3():
    from v3 import FullVideo
    L, P = "lieus/", "personnages/"
    R = P + "raul_bautista_"
    shots = [
        (0, 0.0, ("photo", R + "01.jpg", 0.55, 0.3, 1.3), "QUI EST RAUL ?", None),
        (1, 0.0, ("photo", P + "jason_and_lucia_01.jpg", 0.45, 0.4, 1.05), "JASON ET LUCIA…", None),
        (2, 0.0, ("photo", P + "jason_and_lucia_02.jpg", 0.5, 0.45, 1.0), None, "LES GROS COUPS ?"),
        (2, 0.5, ("photo", R + "02.jpg", 0.44, 0.3, 1.1), "C’EST LUI", None),
        (3, 0.0, ("clip", "clips/raul_bautista.mp4", 0.58), "RAUL BAUTISTA", None),
        (4, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: stat_card("4", "choses à savoir sur lui", p)), "4 CHOSES À SAVOIR", None),
        (5, 0.0, ("photo", R + "02.jpg", 0.44, 0.3, 1.0), "N°1 : UN PRO", "BRAQUEUR DE BANQUES"),
        (6, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: source_card("Rockstar Games", ["Sa description officielle", "en trois mots…"], p, warn=None)), "SELON ROCKSTAR", None),
        (7, 0.0, ("card", L + "vice_city_08.jpg", 0.5, lambda p: chips_card(["Assurance", "Charme", "Ruse"], p, "Raul en 3 mots")), "EN 3 MOTS", None),
        (8, 0.0, ("photo", R + "03.jpg", 0.58, 0.25, 1.1), "BRAQUEUR CHEVRONNÉ", None),
        (8, 0.55, ("photo", R + "01.jpg", 0.55, 0.3, 1.0), None, "EN QUÊTE DE TALENTS"),
        (9, 0.0, ("photo", P + "jason_and_lucia_04.jpg", 0.4, 0.4, 1.0), "PRÊTS À TOUT RISQUER", None),
        (10, 0.0, ("photo", P + "jason_and_lucia_02.jpg", 0.55, 0.45, 1.15), None, "LE PLUS GROS BUTIN"),
        (11, 0.0, ("photo", R + "04.jpg", 0.5, 0.3, 1.1), "N°2 : LE MENTOR", None),
        (12, 0.0, ("photo", P + "jason_and_lucia_03.jpg", 0.55, 0.35, 1.0), None, "JEUNES ET SANS EXPÉRIENCE"),
        (13, 0.0, ("photo", P + "jason_and_lucia_02.jpg", 0.45, 0.4, 1.0), "GROS BRAQUAGES", None),
        (13, 0.5, ("photo", R + "02.jpg", 0.5, 0.35, 1.0), None, "IL LEUR OUVRE LA PORTE"),
        (14, 0.0, ("card", L + "vice_city_10.jpg", 0.5, lambda p: stat_card("CHAP. 3", "ta 1re rencontre avec Raul", p)), "CHAPITRE 3", None),
        (15, 0.0, ("card", L + "vice_city_15.jpg", 0.5, lambda p: chips_card(["First Impressions"], p, "Le nom de ta 1re mission avec lui")), "SA MISSION", None),
        (16, 0.0, ("photo", R + "03.jpg", 0.58, 0.22, 1.3), "1RES IMPRESSIONS", None),
        (17, 0.0, ("photo", P + "jason_and_lucia_08.jpg", 0.45, 0.5, 1.0), "N°3 : LE FEU", None),
        (18, 0.0, ("card", L + "vice_city_22.jpg", 0.5, lambda p: source_card("Rockstar Games", ["Son imprudence fait monter", "les enchères à chaque coup"], p, warn=None)), "SON IMPRUDENCE", None),
        (18, 0.55, ("photo", R + "02.jpg", 0.44, 0.25, 1.25), None, "À CHAQUE COUP"),
        (19, 0.0, ("photo", P + "jason_and_lucia_06.jpg", 0.5, 0.4, 1.0), "IL FAUDRA CHOISIR", None),
        (20, 0.0, ("split", R + "04.jpg", (0.5, 0.3), P + "jason_and_lucia_07.jpg", (0.5, 0.35), "DOUBLER LA MISE", "TOUT ARRÊTER"), None, None),
        (22, 0.0, ("photo", R + "01.jpg", 0.55, 0.3, 1.15), "SA PHRASE CULTE", None),
        (23, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: source_card("Raul Bautista", ["« La vie est pleine", "de surprises, mon ami. »"], p, warn=None)), "« MON AMI… »", None),
        (24, 0.0, ("photo", R + "03.jpg", 0.58, 0.2, 1.4), "MAIS ATTENDS…", None),
        (25, 0.0, ("photo", R + "01.jpg", 0.4, 0.3, 1.0), "N°4 : SA VOIX", None),
        (26, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: stat_card("MANNY PEREZ", "la voix de Raul", p, sub2="Acteur dominicain · crédits du jeu")), "MANNY PEREZ", None),
        (27, 0.0, ("photo", P + "lucia_caminos_14.jpg", 0.22, 0.38, 1.2), "ET LUCIA ?", None),
        (28, 0.0, ("card", L + "vice_city_08.jpg", 0.5, lambda p: stat_card("MANNI PEREZ", "la voix de Lucia", p, c1=(190, 160, 255), c2=(255, 92, 170), sub2="Crédits du jeu")), "MANNI PEREZ", None),
        (29, 0.0, ("split", R + "01.jpg", (0.55, 0.3), P + "lucia_caminos_14.jpg", (0.22, 0.35), "MANNY", "MANNI"), None, None),
        (30, 0.0, ("photo", P + "jason_and_lucia_01.jpg", 0.5, 0.35, 1.0), "2 PEREZ !", None),
        (31, 0.0, ("photo", L + "vice_city_01.jpg", 0.45, 0.5, 1.0), "BONUS POUR LES FANS", None),
        (32, 0.0, ("photo", R + "04.jpg", 0.5, 0.35, 1.0), "COSTUME BLANC", None),
        (32, 0.55, ("clip", "clips/raul_bautista.mp4", 0.58), None, "CHEMISE VIOLETTE"),
        (33, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: source_card("Lance Vance", ["GTA Vice City · 2002", "Costume blanc, chemise violette"], p, warn=None)), "COMME LANCE VANCE", None),
        (34, 0.0, ("photo", L + "vice_city_17.jpg", 0.42, 0.5, 1.0), "ET LANCE…", None),
        (35, 0.0, ("card", L + "vice_city_17.jpg", 0.5, lambda p: source_card("GTA Vice City · 2002", ["Lance Vance trahit", "Tommy Vercetti"], p, warn=None)), "A TRAHI TOMMY", None),
        (36, 0.0, ("photo", R + "04.jpg", 0.5, 0.25, 1.4), "RAUL AUSSI ?", "THÉORIE DE FANS"),
        (37, 0.0, ("card", L + "vice_city_11.jpg", 0.5, lambda p: source_card("Théorie de joueurs", ["Raul, futur traître ?", "Indice : la jaquette du jeu"], p)), "ATTENTION", None),
        (38, 0.0, ("split", R + "03.jpg", (0.58, 0.25), R + "04.jpg", (0.5, 0.3), "MENTOR", "TRAÎTRE"), None, None),
        (40, 0.0, ("card", L + "vice_city_27.jpg", 0.5, lambda p: comment_card("Mentor ou traître ?", p, typed="Traître, c’est sûr !")), "ABONNE-TOI !", None),
    ]
    lab_at = {0: "QUI EST-IL ?", 5: "N°1 · LE PRO", 11: "N°2 · LE MENTOR", 17: "N°3 · LE FEU", 25: "N°4 · SA VOIX", 31: "BONUS", 38: "TON AVIS"}
    labels = {}
    for i, sh in enumerate(shots):
        if sh[0] in lab_at and sh[1] == 0.0:
            labels[i] = lab_at[sh[0]]
    return FullVideo("raul3", TEXTS["raul"], DUR["raul3"], shots, VIOLET, labels=labels)


VIDEOS["raul3"] = video_raul3


# ---------------- 22/11 18 h 30 : Vice City de jour, 5 lieux à voir (format v3, lieu) ----------------
DUR["vicecity3"] = 87.040  # voix_vicecity3.mp3 = voix_vicecity.mp3 coupée avant « Allez, ciao » (100,4 s), sans les blancs, x1.1


def video_vicecity3():
    from v3 import FullVideo
    L, P = "lieus/", "personnages/"
    V = L + "vice_city_"
    SKY = dict(c1=(150, 240, 255), c2=(90, 160, 255))
    shots = [
        (0, 0.0, ("photo", V + "10.jpg", 0.4, 0.5, 1.0), "VICE CITY", None),
        (1, 0.0, ("card", V + "03.jpg", 0.5, lambda p: stat_card("x 2", "la taille de Los Santos", p, sub2="Selon Rockstar North")), "2X LOS SANTOS !", None),
        (2, 0.0, ("photo", V + "11.jpg", 0.62, 0.45, 1.0), None, "SIGNÉ ROCKSTAR NORTH"),
        (3, 0.0, ("card", V + "15.jpg", 0.5, lambda p: stat_card("5", "lieux à voir de jour", p, **SKY)), "5 LIEUX À VOIR", None),
        (3, 0.55, ("photo", V + "03.jpg", 0.5, 0.5, 1.0), None, "EN PLEIN JOUR"),
        (4, 0.0, ("photo", V + "05.jpg", 0.5, 0.5, 1.0), "N°1 : OCEAN BEACH", None),
        (5, 0.0, ("photo", V + "02.jpg", 0.35, 0.4, 1.0), None, "LE CŒUR DE LA VILLE"),
        (6, 0.0, ("photo", V + "02.jpg", 0.25, 0.35, 1.2), "ART DÉCO PASTEL", None),
        (6, 0.5, ("photo", V + "02.jpg", 0.12, 0.3, 1.3), None, "SABLE BLANC"),
        (7, 0.0, ("photo", V + "26.jpg", 0.5, 0.5, 1.0), "SOUTH BEACH, MIAMI", None),
        (8, 0.0, ("photo", V + "24.jpg", 0.6, 0.5, 1.0), None, "CE NOM, TU LE CONNAIS"),
        (9, 0.0, ("card", V + "01.jpg", 0.5, lambda p: stat_card("2002", "Ocean Beach existait déjà", p, sub2="dans GTA Vice City")), "DÉJÀ EN 2002 !", None),
        (10, 0.0, ("photo", V + "06.jpg", 0.15, 0.32, 1.4), "N°2 : L’OCEAN VIEW", None),
        (11, 0.0, ("card", V + "27.jpg", 0.5, lambda p: source_card("GTA Vice City · 2002", ["Ocean View Hotel :", "1re planque de Tommy Vercetti"], p, warn=None)), "1ER HÔTEL DE TOMMY", None),
        (12, 0.0, ("photo", V + "06.jpg", 0.2, 0.35, 1.0), "LE NÉON ROSE", None),
        (13, 0.0, ("photo", V + "02.jpg", 0.6, 0.4, 1.0), "SUR LE TOIT", "UN APPLE MARTINI"),
        (14, 0.0, ("card", V + "02.jpg", 0.5, lambda p: stat_card("TROPHÉE", "« In The Beginning… »", p, sub2="Un verre au rooftop de l’Ocean View")), "TROPHÉE DÉBLOQUÉ", None),
        (15, 0.0, ("photo", V + "02.jpg", 0.72, 0.4, 1.3), "LE PLUS CLASSE", None),
        (16, 0.0, ("photo", V + "09.jpg", 0.5, 0.5, 1.0), "N°3 : STOCKYARD", None),
        (17, 0.0, ("photo", V + "09.jpg", 0.12, 0.4, 1.0), "LES FRESQUES", None),
        (17, 0.5, ("photo", V + "09.jpg", 0.85, 0.4, 1.0), None, "INSPIRÉ DE WYNWOOD"),
        (18, 0.0, ("card", V + "09.jpg", 0.5, lambda p: stat_card("50+", "vrais street-artistes", p, sub2="ont peint les murs du jeu")), "50 VRAIS ARTISTES", None),
        (18, 0.55, ("photo", V + "09.jpg", 0.45, 0.4, 1.35), None, "DE VRAIES ŒUVRES"),
        (19, 0.0, ("photo", V + "09.jpg", 0.7, 0.5, 1.5), "EN PLEIN VICE CITY", None),
        (20, 0.0, ("photo", V + "08.jpg", 0.58, 0.5, 1.6), "N°4 : SAHARA ARENA", None),
        (21, 0.0, ("card", V + "08.jpg", 0.5, lambda p: source_card("Inspirée de…", ["Kaseya Center, Miami", "La salle du Miami Heat"], p, warn=None)), "LA SALLE DU HEAT", None),
        (22, 0.0, ("photo", V + "11.jpg", 0.3, 0.5, 1.0), "MAIS ATTENDS…", None),
        (23, 0.0, ("photo", V + "15.jpg", 0.5, 0.5, 1.0), "N°5 : LE PORT", None),
        (24, 0.0, ("card", V + "15.jpg", 0.5, lambda p: stat_card("N°1", "mondial des croisières", p, sub2="Selon Rockstar", **SKY)), "N°1 DES CROISIÈRES", None),
        (25, 0.0, ("photo", V + "15.jpg", 0.72, 0.6, 1.2), "PAQUEBOTS GÉANTS", None),
        (25, 0.4, ("photo", V + "10.jpg", 0.4, 0.45, 1.0), None, "DOWNTOWN"),
        (25, 0.7, ("photo", V + "10.jpg", 0.75, 0.4, 1.0), None, "INSPIRÉ DE BRICKELL"),
        (26, 0.0, ("photo", P + "jason_and_lucia_03.jpg", 0.5, 0.4, 1.0), "SANS TE FATIGUER ?", None),
        (27, 0.0, ("card", V + "24.jpg", 0.5, lambda p: chips_card(["Paradise Taxi", "RydeMe"], p, "Voyage rapide")), "TAXI OU VTC", None),
        (27, 0.55, ("photo", P + "jason_and_lucia_06.jpg", 0.5, 0.4, 1.0), None, "SUR TON TÉLÉPHONE"),
        (28, 0.0, ("photo", V + "24.jpg", 0.6, 0.5, 1.2), "COMME UN VRAI VTC", None),
        (29, 0.0, ("card", V + "11.jpg", 0.5, lambda p: source_card("Lieux de Miami", ["Comparaisons de la presse", "et des joueurs"], p)), "PETIT RAPPEL", None),
        (30, 0.0, ("photo", V + "03.jpg", 0.5, 0.5, 1.0), None, "PRESSE ET JOUEURS"),
        (31, 0.0, ("split", V + "05.jpg", (0.3, 0.5), V + "09.jpg", (0.5, 0.5), "LA PLAGE", "LES FRESQUES"), None, None),
        (32, 0.0, ("card", V + "10.jpg", 0.5, lambda p: comment_card("Tu vas où en 1er ?", p, typed="Ocean Beach direct !")), "ABONNE-TOI !", None),
    ]
    lab_at = {0: "VICE CITY", 4: "N°1 · LA PLAGE", 10: "N°2 · OCEAN VIEW", 16: "N°3 · STOCKYARD", 20: "N°4 · L’ARÉNA", 23: "N°5 · LE PORT", 26: "BONUS", 31: "TON AVIS"}
    labels = {}
    for i, sh in enumerate(shots):
        if sh[0] in lab_at and sh[1] == 0.0:
            labels[i] = lab_at[sh[0]]
    return FullVideo("vicecity3", TEXTS["vicecity"], DUR["vicecity3"], shots, BLUE, labels=labels)


VIDEOS["vicecity3"] = video_vicecity3


# ======================= Semaine du 23 au 29/11 : 14 vidéos format v3 =======================
# (bloc inséré dans videos.py avant le __main__ ; voir scripts.SEMAINE pour l'ordre)
DUR.update({"boobie3": 85.107, "astuces3": 82.207, "keys3": 88.007, "duree3": 85.551, "dimez3": 88.059, "eggs3": 86.883,
            "grass3": 84.376, "nouveautes3": 84.193, "gellhorn3": 99.265, "argent3": 97.280, "drequan3": 80.039,
            "fps3": 93.100, "kalaga3": 93.780, "cal3": 86.491})
# DUR = durée de voix_<clé>3.mp3 (voix Hedra coupée dans le blanc avant « Allez, ciao », sans les blancs, x1.1 : prep_voice.py)

_L, _P = "lieus/", "personnages/"
VC, JL = _L + "vice_city_", _P + "jason_and_lucia_"
LK, GR, PG, MK = _L + "leonida_keys_", _L + "grassrivers_", _L + "port_gellhorn_", _L + "mount_kalaga_national_park_"
SKY = dict(c1=(150, 240, 255), c2=(90, 160, 255))
LIME = dict(c1=(190, 255, 150), c2=(60, 210, 120))
FIRE = dict(c1=(255, 200, 110), c2=(255, 90, 60))


def _ph(rel, fx=0.5, fy=0.5, z=1.0):
    return ("photo", rel, fx, fy, z)


def _cd(bg, builder, fx=0.5):
    return ("card", bg, fx, builder)


def _sp(r1, p1, r2, p2, n1, n2):
    return ("split", r1, p1, r2, p2, n1, n2)


def _auto_labels(shots, first):
    """Barre de progression : sujet, puis « N°k », « LE MEILLEUR » à la relance, « TON AVIS » à la fin."""
    labels, n = {0: first}, 0
    for i, sh in enumerate(shots):
        t = sh[3] or ""
        if t.startswith("N°"):
            labels[i] = t.split(":")[0].strip()
        elif t.startswith("MAIS ATTENDS"):
            labels[i] = "LE MEILLEUR"
        elif (sh[2][0] == "split" and i >= len(shots) - 3) or t == "ABONNE-TOI !":
            labels.setdefault(i, "TON AVIS")
    return labels


def _fv(key, text_key, shots, col, first, maxd=4.6):
    """Plan > maxd s (hors écran partagé et carte finale) : on insère un 2e plan au milieu (recadrage plus serré
    de la même photo, ou la photo de fond d'une carte) pour ne jamais rester > ~4,5 s sans changement visuel."""
    from v3 import FullVideo
    v = FullVideo(key, TEXTS[text_key], DUR[key], shots, col, labels=_auto_labels(shots, first))
    extra = []
    for i, ((a, b), sh) in enumerate(zip(v.seg_times, shots)):
        if b - a <= maxd or i == len(shots) - 1 or sh[2][0] == "split":
            continue
        tm = (a + b) / 2
        si = max(j for j, (sa, sb) in enumerate(v.st) if sa - 0.12 <= tm) if any(sa - 0.12 <= tm for sa, sb in v.st) else sh[0]
        sa, sb = v.st[si]
        fr = min(0.95, max(0.0, (tm + 0.12 - sa) / max(0.1, sb - sa)))
        if (si, fr) <= (sh[0], sh[1]):
            continue
        m = sh[2]
        if m[0] == "photo":
            nm = ("photo", m[1], min(0.9, max(0.1, m[2] + 0.06)), m[3], m[4] * 1.3)
        elif m[0] == "card":
            nm = ("photo", m[1], 0.5, 0.5, 1.15)
        else:
            nm = m
        extra.append((si, fr, nm, None, None))
    if not extra:
        return v
    allshots = sorted(shots + extra, key=lambda s: (s[0], s[1]))
    return FullVideo(key, TEXTS[text_key], DUR[key], allshots, col, labels=_auto_labels(allshots, first))


# ---------- 23/11 12 h 30 · Qui est Boobie Ike ? ----------
def video_boobie3():
    B = _P + "boobie_ike_"
    shots = [
        (0, 0.0, _ph(B + "03.jpg", 0.38, 0.35, 1.3), "QUI EST BOOBIE ?", None),
        (1, 0.0, _ph(B + "02.jpg", 0.32, 0.3, 1.1), None, "TOUT LE MONDE LE CONNAÎT"),
        (2, 0.0, ("clip", "clips/boobie_ike.mp4", 0.5), "BOOBIE IKE", None),
        (3, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("4", "choses à savoir sur lui", p)), "4 CHOSES À SAVOIR", None),
        (4, 0.0, _ph(VC + "01.jpg", 0.45, 0.5, 1.0), "N°1 : UNE LÉGENDE", None),
        (5, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Rockstar Games", ["Sa description officielle…"], p, warn=None)), "SELON ROCKSTAR", None),
        (6, 0.0, _ph(B + "01.jpg", 0.45, 0.3, 1.2), "LÉGENDE LOCALE", None),
        (7, 0.0, _ph(B + "02.jpg", 0.32, 0.25, 1.4), None, "ET IL LE SAIT"),
        (8, 0.0, _ph(B + "03.jpg", 0.38, 0.3, 1.5), "TOUT SOURIRE…", None),
        (9, 0.0, _ph(B + "01.jpg", 0.42, 0.35, 1.0), None, "PUIS LES AFFAIRES"),
        (10, 0.0, _ph(VC + "27.jpg", 0.5, 0.5, 1.0), "N°2 : SON EMPIRE", None),
        (11, 0.0, _ph(VC + "10.jpg", 0.35, 0.5, 1.0), None, "SOI-DISANT LÉGITIME"),
        (12, 0.0, _cd(VC + "03.jpg", lambda p: chips_card(["Immobilier", "Studio", "Club"], p, "L’empire de Boobie")), "SON EMPIRE", None),
        (12, 0.6, _ph(B + "02.jpg", 0.58, 0.15, 1.4), "JACK OF HEARTS", "CROSSTOWN"),
        (13, 0.0, _ph(B + "03.jpg", 0.38, 0.35, 1.0), "SA DEVISE ?", None),
        (14, 0.0, _cd(VC + "13.jpg", lambda p: source_card("Boobie Ike", ["« Tout est une question", "de cœur. »"], p, warn=None)), "QUESTION DE CŒUR", None),
        (15, 0.0, _ph(B + "01.jpg", 0.45, 0.3, 1.0), "MAIS ROCKSTAR…", None),
        (16, 0.0, _cd(VC + "25.jpg", lambda p: source_card("Rockstar Games", ["« L’argent du club", "paie le studio… »"], p, warn=None)), "LE CLUB PAIE LE STUDIO", None),
        (17, 0.0, _ph(B + "01.jpg", 0.42, 0.6, 1.4), "ET LE RESTE ?", "L’ARGENT SALE"),
        (18, 0.0, _ph(_P + "drequan_priest_04.jpg", 0.45, 0.4, 1.0), "N°3 : SON PARI", None),
        (19, 0.0, _cd(VC + "04.jpg", lambda p: stat_card("ONLY RAW", "son label de rap", p, sub2="Only Raw Records")), "UN LABEL DE RAP", None),
        (20, 0.0, _ph(_P + "drequan_priest_03.jpg", 0.45, 0.25, 1.2), "AVEC DRE’QUAN", None),
        (20, 0.5, ("clip", "clips/drequan_priest.mp4", 0.5), None, "LE JEUNE ASSOCIÉ"),
        (21, 0.0, _ph(_P + "drequan_priest_04.jpg", 0.75, 0.5, 1.0), "IL MANQUE… UN TUBE", None),
        (22, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("CHAP. 3", "ta rencontre avec Boobie", p)), "CHAPITRE 3", None),
        (23, 0.0, _ph(JL + "06.jpg", 0.6, 0.4, 1.0), "MISSION BOOBIE TIME", None),
        (23, 0.55, _ph(B + "02.jpg", 0.32, 0.3, 1.0), None, "TOI AU VOLANT"),
        (24, 0.0, _cd(VC + "08.jpg", lambda p: chips_card(["Dealer’s Choice", "Bricked Up"], p, "Tu le recroises dans…")), "ET ENCORE…", None),
        (25, 0.0, _ph(B + "03.jpg", 0.38, 0.3, 1.6), "MAIS ATTENDS…", None),
        (26, 0.0, _ph(B + "01.jpg", 0.45, 0.25, 1.4), "N°4 : SA VOIX", None),
        (27, 0.0, ("clip", "clips/boobie_ike.mp4", 0.5), "INTERNET ÉTAIT SÛR…", None),
        (28, 0.0, _cd(VC + "11.jpg", lambda p: source_card("La rumeur des fans", ["Johnny Ray Gill,", "vu dans Red Dead Redemption 2"], p, warn=None)), "LA RUMEUR", None),
        (29, 0.0, _cd(VC + "27.jpg", lambda p: crossed_stat("J. R. GILL", "la rumeur des fans", p)), "RATÉ !", None),
        (30, 0.0, _cd(VC + "13.jpg", lambda p: stat_card("MIKE FORBS", "la voix de Boobie", p, sub2="Crédits du jeu")), "MIKE FORBS", None),
        (31, 0.0, _ph(B + "02.jpg", 0.32, 0.3, 1.25), "INTERNET S’EST TROMPÉ", None),
        (32, 0.0, _sp(B + "01.jpg", (0.45, 0.3), B + "03.jpg", (0.38, 0.35), "HOMME D’AFFAIRES", "GANGSTER"), None, None),
        (34, 0.0, _cd(VC + "27.jpg", lambda p: comment_card("Business ou gangster ?", p, typed="Gangster en costume !")), "ABONNE-TOI !", None),
    ]
    return _fv("boobie3", "boobie", shots, PINK, "QUI EST-IL ?")


# ---------- 23/11 18 h 30 · 5 astuces cachées ----------
def video_astuces3():
    shots = [
        (0, 0.0, _ph(JL + "06.jpg", 0.62, 0.4, 1.1), "COMMANDES CACHÉES", None),
        (1, 0.0, _cd(VC + "10.jpg", lambda p: stat_card("5", "astuces que le jeu ne t’explique pas", p, **SKY)), "5 ASTUCES", None),
        (1, 0.6, _ph(JL + "11.jpg", 0.6, 0.4, 1.0), None, "LA 3E VA TE PLAIRE"),
        (2, 0.0, _ph(VC + "24.jpg", 0.5, 0.5, 1.0), "N°1 : MOTEUR ALLUMÉ", None),
        (3, 0.0, _cd(VC + "22.jpg", lambda p: chips_card(["2× Triangle", "2× Y (Xbox)"], p, "En voiture, appuie vite")), "DOUBLE APPUI", None),
        (4, 0.0, _ph(JL + "03.jpg", 0.35, 0.4, 1.0), "MOTEUR + RADIO ON", None),
        (5, 0.0, _ph(JL + "20.jpg", 0.55, 0.45, 1.0), "ELLE CONTINUE SEULE !", None),
        (6, 0.0, _ph(LK + "05.jpg", 0.35, 0.5, 1.0), "ET EN BATEAU…", None),
        (7, 0.0, _ph(VC + "15.jpg", 0.45, 0.6, 1.0), None, "IL GARDE SON CAP"),
        (8, 0.0, _ph(JL + "11.jpg", 0.75, 0.4, 1.0), "N°2 : LA PORTIÈRE", None),
        (9, 0.0, _cd(VC + "24.jpg", lambda p: chips_card(["Carré", "X (Xbox)"], p, "En conduisant")), "UNE ARME", None),
        (10, 0.0, _ph(JL + "06.jpg", 0.4, 0.4, 1.0), "COUP DE PORTIÈRE", None),
        (10, 0.5, _ph(VC + "06.jpg", 0.2, 0.5, 1.0), None, "PIÉTON, FLIC…"),
        (11, 0.0, _ph(JL + "09.jpg", 0.6, 0.5, 1.0), "À MOTO : COUP DE PIED", None),
        (12, 0.0, _ph(VC + "17.jpg", 0.5, 0.5, 1.0), "N°3 : AUTO DRIVE", None),
        (13, 0.0, _cd(VC + "03.jpg", lambda p: list_card([("Pose un point", "sur la carte", BLUE), ("Bas (croix) + Options", "= la vue cinéma", PINK),
                                                          ("Maintiens Rond / B", "quand « Auto Drive » apparaît", GOLD)], p, title="Le pilote automatique", icon="123")), "LA MANIP", None),
        (14, 0.0, _ph(JL + "20.jpg", 0.4, 0.4, 1.0), "VUE CINÉMA", None),
        (15, 0.0, _ph(JL + "03.jpg", 0.5, 0.4, 1.0), "MAINTIENS ROND", None),
        (16, 0.0, _ph(VC + "10.jpg", 0.5, 0.5, 1.0), "ELLE ROULE SEULE", "CODE DE LA ROUTE"),
        (17, 0.0, _ph(JL + "17.jpg", 0.5, 0.4, 1.0), "MAIS ATTENDS…", None),
        (18, 0.0, _ph(VC + "06.jpg", 0.15, 0.45, 1.2), "N°4 : LA POLICE", None),
        (19, 0.0, _cd(VC + "17.jpg", lambda p: chips_card(["Visage", "Tenue", "Voiture"], p, "Ce que la police sait de toi")), "ELLE SE SOUVIENT", None),
        (20, 0.0, _ph(VC + "16.jpg", 0.6, 0.45, 1.0), "TON VISAGE, TA TENUE…", None),
        (21, 0.0, _ph(JL + "15.jpg", 0.35, 0.4, 1.0), "UN MASQUE", None),
        (21, 0.4, _ph(JL + "08.jpg", 0.65, 0.5, 1.0), None, "TENUE DANS LE COFFRE"),
        (21, 0.75, _ph(VC + "24.jpg", 0.4, 0.5, 1.0), None, "CHANGE DE VOITURE"),
        (22, 0.0, _ph(JL + "02.jpg", 0.5, 0.4, 1.0), "N°5 : LE COFFRE-FORT", None),
        (23, 0.0, _ph(JL + "02.jpg", 0.45, 0.4, 1.4), "FAIS-LE SAUTER", None),
        (24, 0.0, _ph(JL + "08.jpg", 0.55, 0.6, 1.2), "GRENADE, GAZ…", None),
        (25, 0.0, _cd(VC + "22.jpg", lambda p: stat_card("BOUM", "n’importe quelle explosion l’ouvre", p, **FIRE)), "ÇA S’OUVRE", None),
        (26, 0.0, _ph(JL + "02.jpg", 0.5, 0.5, 1.0), "SAUF LES BANQUES", None),
        (27, 0.0, _ph(JL + "04.jpg", 0.5, 0.4, 1.0), "ATTENTION AU BRUIT !", None),
        (28, 0.0, _sp(JL + "11.jpg", (0.75, 0.4), JL + "20.jpg", (0.4, 0.4), "LA PORTIÈRE", "AUTO DRIVE"), None, None),
        (29, 0.0, _cd(VC + "10.jpg", lambda p: comment_card("Laquelle tu savais pas ?", p, typed="L’auto drive !")), "ABONNE-TOI !", None),
    ]
    return _fv("astuces3", "astuces", shots, BLUE, "5 ASTUCES")


# ---------- 24/11 12 h 30 · Leonida Keys ----------
def video_keys3():
    shots = [
        (0, 0.0, _ph(LK + "05.jpg", 0.75, 0.5, 1.0), "UN CHIEN EN JET-SKI ?!", None),
        (1, 0.0, _ph(LK + "06.jpg", 0.5, 0.4, 1.0), None, "OUI, DANS GTA 6"),
        (2, 0.0, _ph(LK + "01.jpg", 0.45, 0.5, 1.0), "LEONIDA KEYS", None),
        (3, 0.0, _cd(LK + "01.jpg", lambda p: source_card("Rockstar Games", ["« La porte", "du paradis »"], p, warn=None)), "LA PORTE DU PARADIS", None),
        (4, 0.0, _ph(LK + "03.jpg", 0.35, 0.5, 1.0), "TENUE DÉCONTRACTÉE", None),
        (5, 0.0, _ph(LK + "07.jpg", 0.5, 0.5, 1.0), "EAUX DANGEREUSES", None),
        (5, 0.5, _ph(LK + "04.jpg", 0.6, 0.5, 1.0), None, "ET MAGNIFIQUES"),
        (6, 0.0, _cd(LK + "01.jpg", lambda p: source_card("Selon la presse", ["Le portrait des Florida Keys"], p)), "FLORIDA KEYS", None),
        (7, 0.0, _cd(LK + "06.jpg", lambda p: stat_card("5", "choses à faire dans les Keys", p, **SKY)), "5 CHOSES À FAIRE", None),
        (8, 0.0, _ph(LK + "02.jpg", 0.5, 0.5, 1.0), "N°1 : KEY LENTO", None),
        (9, 0.0, _ph(_P + "brian_heder_02.jpg", 0.55, 0.35, 1.0), "MAISON SUR PILOTIS", "PRÊTÉE PAR BRIAN"),
        (10, 0.0, _ph(GR + "07.jpg", 0.3, 0.45, 1.0), "DOLORES, SON SERPENT", None),
        (11, 0.0, _ph(GR + "07.jpg", 0.25, 0.5, 1.4), None, "TU PEUX LA NOURRIR"),
        (12, 0.0, _ph(LK + "03.jpg", 0.55, 0.25, 1.2), "N°2 : RUSTY ANCHOR", None),
        (13, 0.0, _ph(LK + "03.jpg", 0.4, 0.55, 1.0), "LES PIEDS DANS L’EAU", None),
        (14, 0.0, _ph(LK + "05.jpg", 0.3, 0.5, 1.0), "N°3 : LA PÊCHE", None),
        (15, 0.0, _cd(LK + "01.jpg", lambda p: chips_card(["Gone Fishing"], p, "Ta 1re mission avec Cal")), "GONE FISHING", None),
        (15, 0.55, _ph(_P + "cal_hampton_02.jpg", 0.55, 0.25, 1.2), None, "AVEC CAL"),
        (16, 0.0, _cd(LK + "05.jpg", lambda p: stat_card("TROPHÉE", "bats Cal à un défi de pêche", p, sub2="« Baited My Tackle »", **SKY)), "BATS CAL", None),
        (17, 0.0, _ph(LK + "01.jpg", 0.25, 0.5, 1.0), "N°4 : BASE MILITAIRE", None),
        (18, 0.0, _cd(LK + "01.jpg", lambda p: source_card("Mile Zero Air Station", ["Goose Key", "Leonida Keys"], p, warn=None)), "MILE ZERO", None),
        (19, 0.0, _cd(LK + "06.jpg", lambda p: stat_card("RHINO", "le tank de la base", p)), "UN TANK", None),
        (20, 0.0, _cd(LK + "01.jpg", lambda p: stat_card("LAZER", "le jet de chasse", p, **SKY)), "ET UN JET !", None),
        (21, 0.0, _ph(LK + "06.jpg", 0.6, 0.4, 1.0), "MAIS ATTENDS…", None),
        (22, 0.0, _ph(LK + "05.jpg", 0.55, 0.4, 1.1), "N°5 : LE CHIEN !", None),
        (23, 0.0, _ph(LK + "01.jpg", 0.6, 0.6, 1.0), "EN PLEINE MER", None),
        (23, 0.5, _ph(LK + "04.jpg", 0.4, 0.4, 1.0), None, "COUPE LE MOTEUR, NAGE"),
        (24, 0.0, _ph(LK + "06.jpg", 0.3, 0.5, 1.0), "DES ABOIEMENTS ?!", None),
        (25, 0.0, _cd(LK + "05.jpg", lambda p: chips_card(["Gilet", "Lunettes", "Jet-ski"], p, "Le chien de GTA 6")), "LE CHIEN EN JET-SKI !", None),
        (26, 0.0, _ph(LK + "06.jpg", 0.15, 0.5, 1.0), "SON ÎLE", None),
        (26, 0.5, _cd(LK + "05.jpg", lambda p: stat_card("1 200 $", "déterrés par le chien", p, **LIME)), "1 200 $ !", None),
        (27, 0.0, _ph(LK + "05.jpg", 0.55, 0.5, 1.0), "IL EXISTE VRAIMENT", None),
        (28, 0.0, _cd(LK + "01.jpg", lambda p: source_card("Loosy", ["Une chienne de Fort Lauderdale", "qui fait du jet-ski"], p, warn=None)), "LOOSY", None),
        (29, 0.0, _cd(LK + "02.jpg", lambda p: source_card("Petit rappel", ["Florida Keys :", "comparaison de la presse"], p)), "PETIT RAPPEL", None),
        (30, 0.0, _sp(LK + "03.jpg", (0.4, 0.5), LK + "05.jpg", (0.5, 0.5), "LE BAR", "LA MER"), None, None),
        (31, 0.0, _cd(LK + "01.jpg", lambda p: comment_card("Tu fais quoi en 1er ?", p, typed="Le chien en jet-ski !")), "ABONNE-TOI !", None),
    ]
    return _fv("keys3", "keys", shots, BLUE, "LEONIDA KEYS")


# ---------- 24/11 18 h 30 · Durée de vie ----------
def video_duree3():
    shots = [
        (0, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("≈ x 2", "la durée de GTA 5", p, sub2="Selon les chronos des testeurs")), "2X GTA 5 ?!", None),
        (1, 0.0, _ph(JL + "01.jpg", 0.5, 0.35, 1.0), None, "CHRONOMÉTRÉ"),
        (2, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Rockstar Games", ["Aucune durée officielle"], p, warn=None)), "RIEN D’OFFICIEL", None),
        (3, 0.0, _ph(VC + "03.jpg", 0.5, 0.5, 1.0), "5 CHIFFRES", None),
        (4, 0.0, _cd(JL + "16.jpg", lambda p: stat_card("5", "chapitres", p, **FIRE)), "N°1 : 5 CHAPITRES", None),
        (5, 0.0, _ph(JL + "16.jpg", 0.55, 0.5, 1.0), None, "SELON TESTS ET GUIDES"),
        (6, 0.0, _cd(VC + "17.jpg", lambda p: stat_card("~ 90", "missions principales", p)), "N°2 : ~90 MISSIONS", None),
        (7, 0.0, _ph(JL + "04.jpg", 0.4, 0.4, 1.0), "MISSIONS PRINCIPALES", None),
        (8, 0.0, _cd(VC + "08.jpg", lambda p: bars_card([("PC Gamer", 91, BLUE, "91"), ("Autres sites", 93, PINK, "93")], p, title="Missions principales", maxv=100)), "91… OU 93", None),
        (9, 0.0, _cd(VC + "10.jpg", lambda p: stat_card("50-60 H", "pour finir l’histoire", p)), "N°3 : 50 À 60 H", None),
        (10, 0.0, _ph(JL + "09.jpg", 0.6, 0.45, 1.0), "EN LIGNE DROITE", None),
        (11, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("50 H 42", "le chrono de ScreenRant", p, **FIRE)), "50 H 42", None),
        (12, 0.0, _cd(VC + "15.jpg", lambda p: bars_card([("GTA 5", 32, (170, 160, 190), "32 h"), ("Red Dead 2", 50, GOLD, "50 h"), ("GTA 6", 55, PINK, "50-60 h")],
                                                          p, title="L’histoire, de bout en bout", maxv=60)), "COMPARAISON", None),
        (13, 0.0, _ph(_P + "jason_and_lucia_17.jpg", 0.5, 0.4, 1.0), "RED DEAD 2 : 50 H", None),
        (14, 0.0, _ph(JL + "01.jpg", 0.45, 0.4, 1.2), "PRESQUE LE DOUBLE !", None),
        (15, 0.0, _ph(JL + "13.jpg", 0.4, 0.4, 1.0), "MAIS ATTENDS…", None),
        (16, 0.0, _cd(VC + "11.jpg", lambda p: stat_card("80 H", "pour un dev de Rockstar", p)), "N°4 : 80 HEURES", None),
        (17, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Rob Nelson", ["Co-directeur, Rockstar North", "~80 h, avec de l’optionnel"], p, warn=None)), "CO-DIRECTEUR", None),
        (18, 0.0, _cd(VC + "27.jpg", lambda p: source_card("New York Times", ["Article de l’été 2026"], p, warn=None)), "NEW YORK TIMES", None),
        (19, 0.0, _cd(VC + "08.jpg", lambda p: stat_card("120 H +", "de jeu pour le testeur d’IGN", p, **SKY)), "IGN : 120 H+", None),
        (20, 0.0, _cd(VC + "01.jpg", lambda p: stat_card("55", "trophées", p, **FIRE)), "N°5 : 55 TROPHÉES", None),
        (21, 0.0, _ph(VC + "01.jpg", 0.5, 0.5, 1.0), "PLATINE = 100 %", None),
        (22, 0.0, _ph(VC + "03.jpg", 0.5, 0.5, 1.0), "TOUTE LA CARTE…", None),
        (22, 0.5, _ph(LK + "01.jpg", 0.5, 0.5, 1.0), None, "TOUTES LES ACTIVITÉS"),
        (23, 0.0, _ph(JL + "03.jpg", 0.35, 0.4, 1.0), "3 JOURS ? PAS ASSEZ", None),
        (24, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Attention", ["Chronos de la presse :", "ton temps dépendra de toi"], p, warn=None)), "ATTENTION", None),
        (25, 0.0, _sp(JL + "09.jpg", (0.6, 0.4), LK + "01.jpg", (0.5, 0.5), "L’HISTOIRE", "TOUT EXPLORER"), None, None),
        (27, 0.0, _cd(VC + "27.jpg", lambda p: comment_card("Histoire ou 100 % ?", p, typed="Je fais le 100 % !")), "ABONNE-TOI !", None),
    ]
    return _fv("duree3", "duree", shots, GOLD, "LA DURÉE")


# ---------- 25/11 12 h 30 · Qui sont les Real Dimez ? ----------
def video_dimez3():
    D_ = _P + "real_dimez_"
    shots = [
        (0, 0.0, _ph(D_ + "03.jpg", 0.53, 0.3, 1.3), "LES REAL DIMEZ", None),
        (1, 0.0, _ph(D_ + "04.jpg", 0.25, 0.4, 1.2), None, "DEALERS → TUBES"),
        (2, 0.0, ("clip", "clips/real_dimez.mp4", 0.5), "LE DUO RAP DE GTA 6", None),
        (3, 0.0, _cd(VC + "13.jpg", lambda p: stat_card("4", "choses à savoir sur elles", p)), "4 CHOSES À SAVOIR", None),
        (4, 0.0, _ph(D_ + "02.jpg", 0.45, 0.4, 1.0), "N°1 : LEUR DEVISE", None),
        (5, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Rockstar Games", ["Leur devise officielle…"], p, warn=None)), "SELON ROCKSTAR", None),
        (6, 0.0, _cd(VC + "13.jpg", lambda p: chips_card(["Viral videos.", "Viral hooks."], p, "Leur devise")), "VIDÉOS VIRALES", None),
        (7, 0.0, _ph(D_ + "04.jpg", 0.75, 0.3, 1.2), "REFRAINS VIRAUX", None),
        (8, 0.0, _ph(D_ + "04.jpg", 0.5, 0.4, 1.0), "AMIES DEPUIS LE LYCÉE", "BAE-LUXE ET ROXY"),
        (9, 0.0, _ph(D_ + "01.jpg", 0.5, 0.35, 1.0), "N°2 : LEUR BUSINESS", None),
        (10, 0.0, _cd(VC + "27.jpg", lambda p: source_card("Rockstar Games", ["Noir sur blanc…"], p, warn=None)), "NOIR SUR BLANC", None),
        (11, 0.0, _ph(VC + "21.jpg", 0.5, 0.4, 1.0), "LE RACKET DES DEALERS", None),
        (11, 0.55, _ph(D_ + "01.jpg", 0.45, 0.5, 1.0), None, "→ ARGENT LIQUIDE"),
        (12, 0.0, _ph(D_ + "04.jpg", 0.25, 0.4, 1.3), "DU RAP ÉPICÉ", None),
        (13, 0.0, _ph(D_ + "02.jpg", 0.5, 0.5, 1.0), "RÉSEAUX SOCIAUX", None),
        (14, 0.0, _ph(D_ + "04.jpg", 0.75, 0.35, 1.0), "N°3 : LE 1ER TUBE", None),
        (15, 0.0, _cd(VC + "04.jpg", lambda p: stat_card("DWNPLY", "le rappeur local du 1er tube", p)), "AVEC DWNPLY", None),
        (16, 0.0, _ph(VC + "04.jpg", 0.35, 0.4, 1.0), "SA VOIX ?", None),
        (16, 0.5, _cd(VC + "13.jpg", lambda p: stat_card("DENZEL CURRY", "la voix de DWNPLY", p, sub2="3 de ses morceaux dans le jeu")), "DENZEL CURRY", None),
        (17, 0.0, _ph(_P + "drequan_priest_03.jpg", 0.45, 0.25, 1.0), "5 ANS PLUS TARD", "ONLY RAW RECORDS"),
        (18, 0.0, _ph(D_ + "03.jpg", 0.53, 0.35, 1.0), "LA FOUDRE 2 FOIS ?", None),
        (19, 0.0, _ph(D_ + "02.jpg", 0.45, 0.5, 1.0), "CHAPITRE 3 : LE CLIP", "MISSION COOTIES"),
        (20, 0.0, _cd(VC + "13.jpg", lambda p: stat_card("LA BATTE", "de Bae-Luxe, à récupérer", p, **FIRE)), "LA BATTE DE BAE-LUXE", None),
        (21, 0.0, _ph(D_ + "04.jpg", 0.5, 0.35, 1.0), "MAIS ATTENDS…", None),
        (22, 0.0, ("clip", "clips/real_dimez.mp4", 0.5), "N°4 : LE CASTING", None),
        (23, 0.0, _cd(VC + "13.jpg", lambda p: stat_card("HOOD BRAT", "joue Bae-Luxe", p, sub2="Crédits du jeu")), "BAE-LUXE", None),
        (24, 0.0, _cd(VC + "25.jpg", lambda p: stat_card("KRISSY CELESS", "joue Roxy", p, sub2="Crédits du jeu", c1=(190, 160, 255), c2=(255, 92, 170))), "ROXY", None),
        (25, 0.0, _ph(D_ + "04.jpg", 0.25, 0.35, 1.3), "DE VRAIES RAPPEUSES", None),
        (26, 0.0, _ph(D_ + "04.jpg", 0.75, 0.3, 1.3), None, "QUI JOUENT DES RAPPEUSES"),
        (27, 0.0, _cd(VC + "27.jpg", lambda p: source_card("Théorie des fans", ["Une parodie des City Girls ?", "Le duo rap de Miami"], p)), "THÉORIE DE FANS", None),
        (28, 0.0, _ph(D_ + "01.jpg", 0.5, 0.35, 1.2), "PAS CONFIRMÉ", None),
        (29, 0.0, _sp(D_ + "03.jpg", (0.53, 0.3), D_ + "01.jpg", (0.5, 0.3), "FUTURES STARS", "FEU DE PAILLE"), None, None),
        (31, 0.0, _cd(VC + "13.jpg", lambda p: comment_card("Stars ou feu de paille ?", p, typed="Futures stars !")), "ABONNE-TOI !", None),
    ]
    return _fv("dimez3", "dimez", shots, PINK, "QUI SONT-ELLES ?")


# ---------- 25/11 18 h 30 · 5 easter eggs ----------
def video_eggs3():
    shots = [
        (0, 0.0, _ph(PG + "06.jpg", 0.5, 0.5, 1.0), "RED DEAD CACHÉ ?!", None),
        (1, 0.0, _ph(VC + "24.jpg", 0.5, 0.5, 1.0), None, "ET PAS QUE…"),
        (2, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("5", "easter eggs à trouver", p)), "5 EASTER EGGS", None),
        (3, 0.0, _cd(PG + "06.jpg", lambda p: source_card("Red Dead Redemption 2", ["Le chapeau d’Arthur Morgan"], p, warn=None)), "N°1 : ARTHUR MORGAN", None),
        (4, 0.0, _ph(PG + "06.jpg", 0.3, 0.55, 1.0), "SUD DE PORT GELLHORN", None),
        (4, 0.55, _ph(PG + "05.jpg", 0.6, 0.5, 1.0), None, "PANNEAUX YARD SALE"),
        (5, 0.0, _ph(PG + "06.jpg", 0.7, 0.6, 1.3), "UN VIDE-GRENIER", None),
        (6, 0.0, _cd(PG + "06.jpg", lambda p: list_card([("Le canapé", "au fond du jardin", GOLD), ("L’étui de guitare", "le chapeau est posé dessus", PINK)],
                                                         p, title="Où chercher", icon="12")), "LE CANAPÉ", None),
        (7, 0.0, _cd(PG + "06.jpg", lambda p: stat_card("COWBOY HAT", "« Genuine Cowboy Hat »", p, sub2="Le chapeau d’Arthur Morgan", **FIRE)), "LE CHAPEAU D’ARTHUR", None),
        (8, 0.0, _ph(VC + "24.jpg", 0.4, 0.6, 1.0), "N°2 : BRIAN O’CONNER", None),
        (9, 0.0, _cd(VC + "10.jpg", lambda p: stat_card("ECLIPSE 95", "Mitsubishi vert fluo, néons", p, sub2="Garage de Vespucci Island", **LIME)), "VESPUCCI ISLAND", None),
        (10, 0.0, _ph(VC + "24.jpg", 0.35, 0.55, 1.3), "FAST & FURIOUS !", None),
        (11, 0.0, _cd(VC + "22.jpg", lambda p: list_card([("Coupe l’alarme", "panneau à gauche en entrant", GOLD), ("Ouvre le garage", "et démarre", GREEN)],
                                                          p, title="La manip", icon="12")), "COUPE L’ALARME", None),
        (11, 0.6, _ph(JL + "20.jpg", 0.5, 0.5, 1.0), None, "ELLE EST À TOI"),
        (12, 0.0, _ph(VC + "13.jpg", 0.5, 0.5, 1.0), "N°3 : RADIO SECRÈTE", None),
        (13, 0.0, _cd(VC + "13.jpg", lambda p: source_card("The Vault", ["Boîte de nuit · Downtown"], p, warn=None)), "THE VAULT", None),
        (14, 0.0, _ph(VC + "13.jpg", 0.3, 0.5, 1.3), "L’AFFICHE AU MASQUE", "PRÈS DE L’EXTINCTEUR"),
        (15, 0.0, _cd(VC + "13.jpg", lambda p: chips_card(["Appli WAiNK", "Scanne l’affiche"], p, "Sur ton téléphone")), "SCANNE-LA", None),
        (16, 0.0, _cd(VC + "13.jpg", lambda p: stat_card("VAULT RADIO", "la station cachée", p, **LIME)), "STATION CACHÉE", None),
        (17, 0.0, _ph(VC + "11.jpg", 0.3, 0.5, 1.0), "MAIS ATTENDS…", None),
        (18, 0.0, _ph(JL + "16.jpg", 0.4, 0.5, 1.0), "N°4 : MONT CHILIAD", None),
        (19, 0.0, _ph(JL + "18.jpg", 0.5, 0.5, 1.0), "2 CLIENTS D’UN BAR", None),
        (19, 0.55, _cd(JL + "18.jpg", lambda p: source_card("Au bar…", ["« Un bunker sous le Chiliad »"], p, warn=None)), "UN BUNKER ?!", None),
        (20, 0.0, _cd(JL + "18.jpg", lambda p: chips_card(["Jetpacks", "Œufs"], p, "Ce qu’ils racontent")), "JETPACKS ET ŒUFS", None),
        (21, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("GTA 5", "son plus grand mystère, cité", p)), "LE MYSTÈRE DE GTA 5", None),
        (22, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Découverte", ["Un joueur sur Reddit"], p, warn=None)), "TROUVÉ SUR REDDIT", None),
        (23, 0.0, _ph(JL + "03.jpg", 0.6, 0.4, 1.0), "N°5 : LA SONNERIE", None),
        (24, 0.0, _cd(VC + "10.jpg", lambda p: chips_card(["Réglages", "Téléphone", "Wind Chimes"], p, "Le chemin")), "WIND CHIMES", None),
        (25, 0.0, _cd(VC + "11.jpg", lambda p: stat_card("MICHAEL", "sa sonnerie dans GTA 5", p, **SKY)), "LA SONNERIE DE MICHAEL", None),
        (26, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("13 ANS", "et elle est toujours là", p)), "13 ANS PLUS TARD", None),
        (27, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Attention", ["Découvertes de joueurs", "et de la presse"], p, warn="Rockstar n’a rien commenté")), "ATTENTION", None),
        (28, 0.0, _sp(VC + "24.jpg", (0.4, 0.5), VC + "13.jpg", (0.5, 0.5), "L’ECLIPSE", "LA RADIO"), None, None),
        (29, 0.0, _cd(VC + "27.jpg", lambda p: comment_card("Lequel en premier ?", p, typed="Le chapeau d’Arthur !")), "ABONNE-TOI !", None),
    ]
    return _fv("eggs3", "eggs", shots, VIOLET, "5 EASTER EGGS")


# ---------- 26/11 12 h 30 · Grassrivers ----------
def video_grass3():
    shots = [
        (0, 0.0, _ph(GR + "08.jpg", 0.55, 0.5, 1.0), "UN BIGFOOT ?!", None),
        (1, 0.0, _ph(GR + "05.jpg", 0.5, 0.6, 1.0), "GRASSRIVERS", None),
        (2, 0.0, _cd(GR + "04.jpg", lambda p: source_card("Rockstar Games", ["« Le joyau indomptable", "de Leonida »"], p, warn=None)), "LE JOYAU INDOMPTABLE", None),
        (3, 0.0, _ph(GR + "08.jpg", 0.5, 0.65, 1.0), "SOUS LA SURFACE…", None),
        (4, 0.0, _cd(GR + "05.jpg", lambda p: source_card("Selon la presse", ["Le portrait des Everglades", "« la rivière d’herbe »"], p)), "LES EVERGLADES", None),
        (5, 0.0, _ph(GR + "04.jpg", 0.5, 0.5, 1.0), "GRASS + RIVERS", None),
        (6, 0.0, _cd(GR + "02.jpg", lambda p: stat_card("4", "choses à faire dans les marais", p, **LIME)), "4 CHOSES À FAIRE", None),
        (7, 0.0, _ph(GR + "01.jpg", 0.2, 0.75, 1.3), "N°1 : LES ALLIGATORS", None),
        (8, 0.0, _ph(GR + "06.jpg", 0.25, 0.35, 1.0), "L’ATTRACTION N°1", None),
        (9, 0.0, _ph(GR + "08.jpg", 0.6, 0.7, 1.2), "PLUS MORTELS…", None),
        (10, 0.0, _ph(GR + "04.jpg", 0.75, 0.5, 1.0), "PLUS ÉTRANGES…", None),
        (11, 0.0, _ph(GR + "03.jpg", 0.5, 0.5, 1.0), "N°2 : L’AIRBOAT", None),
        (12, 0.0, _ph(GR + "03.jpg", 0.45, 0.4, 1.4), "LOISIR OFFICIEL", None),
        (13, 0.0, _ph(GR + "04.jpg", 0.3, 0.5, 1.0), "À TOUTE VITESSE", None),
        (14, 0.0, _ph(GR + "02.jpg", 0.5, 0.5, 1.0), "N°3 : HAMLET", "LE BAR SKEETER’S"),
        (15, 0.0, _ph(GR + "01.jpg", 0.6, 0.35, 1.0), "LES KINGFISHERS", "ILS TIENNENT LES MARAIS"),
        (16, 0.0, _ph(GR + "08.jpg", 0.3, 0.5, 1.0), "MAIS ATTENDS…", None),
        (17, 0.0, _ph(GR + "05.jpg", 0.3, 0.6, 1.3), "N°4 : LE SKUNK APE", None),
        (18, 0.0, _cd(GR + "05.jpg", lambda p: source_card("Skunk Ape", ["Le « Bigfoot » de Floride", "Une vraie légende locale"], p, warn=None)), "LE BIGFOOT DE FLORIDE", None),
        (19, 0.0, _ph(GR + "04.jpg", 0.15, 0.5, 1.0), "COTTONMOUTH LAKE", "TENDS L’OREILLE"),
        (20, 0.0, _cd(GR + "08.jpg", lambda p: chips_card(["L3 + R3", "Mode Focus"], p, "Suis les grognements")), "ACTIVE LE FOCUS", None),
        (21, 0.0, _ph(MK + "05.jpg", 0.6, 0.5, 1.0), "IL DÉVORE UN CERF !", None),
        (22, 0.0, _cd(GR + "05.jpg", lambda p: source_card("Une effigie en bois", ["accrochée à un arbre…"], p, warn=None)), "L’EFFIGIE EN BOIS", None),
        (23, 0.0, _ph(GR + "08.jpg", 0.5, 0.5, 1.5), "ET LÀ…", None),
        (24, 0.0, _ph(GR + "05.jpg", 0.5, 0.3, 1.0), "TU T’ÉVANOUIS", None),
        (25, 0.0, _cd(GR + "02.jpg", lambda p: source_card("Have You Seen Skunk Ape ?", ["Le tract qui lance la quête", "de Kirk, chasseur de créatures"], p, warn=None)), "LE TRACT", None),
        (25, 0.55, _ph(GR + "08.jpg", 0.4, 0.6, 1.3), None, "UN CHASSEUR DE CRÉATURES"),
        (26, 0.0, _cd(GR + "03.jpg", lambda p: stat_card("10 000 $", "jusqu’à, pour la quête de Kirk", p, **LIME)), "JUSQU’À 10 000 $", None),
        (27, 0.0, _ph(GR + "08.jpg", 0.6, 0.5, 1.0), "LA FIN…", None),
        (28, 0.0, _ph(GR + "05.jpg", 0.5, 0.5, 1.0), "DÉPEND DE TOI", None),
        (29, 0.0, _cd(GR + "05.jpg", lambda p: source_card("Petit rappel", ["Everglades :", "comparaison de la presse"], p)), "PETIT RAPPEL", None),
        (30, 0.0, _sp(GR + "08.jpg", (0.6, 0.5), GR + "03.jpg", (0.5, 0.5), "LE CHASSER", "FUIR"), None, None),
        (32, 0.0, _cd(GR + "05.jpg", lambda p: comment_card("Chasser ou fuir ?", p, typed="Je le chasse !")), "ABONNE-TOI !", None),
    ]
    return _fv("grass3", "grass", shots, GREEN, "GRASSRIVERS")


# ---------- 26/11 18 h 30 · 5 nouveautés ----------
def video_nouveautes3():
    shots = [
        (0, 0.0, _ph(JL + "09.jpg", 0.55, 0.45, 1.0), "TES CRIMES TE SUIVENT", None),
        (1, 0.0, _ph(JL + "17.jpg", 0.5, 0.4, 1.0), None, "ET CE N’EST PAS TOUT"),
        (2, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("5", "nouveautés que GTA 5 n’avait pas", p)), "5 NOUVEAUTÉS", None),
        (3, 0.0, _ph(JL + "15.jpg", 0.35, 0.4, 1.0), "N°1 : PROFIL CRIMINEL", None),
        (4, 0.0, _ph(JL + "04.jpg", 0.4, 0.4, 1.0), "SELON TON COMPORTEMENT", None),
        (4, 0.55, _ph(JL + "12.jpg", 0.6, 0.4, 1.0), None, "ET TES VICTIMES"),
        (5, 0.0, _cd(VC + "17.jpg", lambda p: list_card([("Professional", "professionnel", GREEN), ("Hardened", "endurci", BLUE), ("Violent", "violent", GOLD),
                                                          ("Psycho", "psychopathe", (255, 140, 60))], p, title="Les niveaux", icon="1234")), "5 NIVEAUX", None),
        (6, 0.0, _cd(VC + "17.jpg", lambda p: stat_card("IRREDEEMABLE", "irrécupérable", p, c1=(255, 130, 130), c2=(210, 30, 60))), "IRRÉCUPÉRABLE", None),
        (7, 0.0, _ph(JL + "08.jpg", 0.55, 0.5, 1.0), "PERMANENT", None),
        (8, 0.0, _ph(JL + "12.jpg", 0.55, 0.4, 1.1), "IL CHANGE TON HISTOIRE", None),
        (9, 0.0, _ph(VC + "06.jpg", 0.15, 0.45, 1.0), "PLUS DE REDDITION", "DÈS « PSYCHO »"),
        (10, 0.0, _ph(JL + "07.jpg", 0.5, 0.4, 1.0), "N°2 : CHANGE DE HÉROS", None),
        (11, 0.0, _sp(JL + "01.jpg", (0.47, 0.22), _P + "lucia_caminos_14.jpg", (0.22, 0.38), "JASON", "LUCIA"), None, None),
        (11, 0.55, _ph(JL + "19.jpg", 0.45, 0.4, 1.0), None, "MÊME EN PLEINE MISSION"),
        (12, 0.0, _ph(JL + "06.jpg", 0.5, 0.4, 1.0), "PARFOIS EN SOLO", None),
        (13, 0.0, _ph(VC + "06.jpg", 0.5, 0.45, 1.0), "N°3 : LES TÉMOINS", None),
        (14, 0.0, _cd(VC + "17.jpg", lambda p: chips_card(["Tenue", "Voiture", "Armes visibles"], p, "La police te reconnaît à…")), "ELLE TE RECONNAÎT", None),
        (15, 0.0, _ph(VC + "17.jpg", 0.5, 0.4, 1.3), "LES CAMÉRAS AUSSI", None),
        (16, 0.0, _cd(VC + "22.jpg", lambda p: list_card([("Efface les vidéos", "de surveillance", BLUE), ("Change de tenue", "ou de voiture", PINK),
                                                          ("Sépare-toi", "de ton partenaire", GOLD)], p, title="Pour t’en sortir", icon="check")), "LA PARADE", None),
        (17, 0.0, _ph(MK + "03.jpg", 0.2, 0.5, 1.0), "MAIS ATTENDS…", None),
        (18, 0.0, _ph(VC + "05.jpg", 0.6, 0.5, 1.0), "N°4 : PARLE À TOUS", None),
        (19, 0.0, _cd(VC + "05.jpg", lambda p: source_card("Comme dans…", ["Red Dead Redemption 2"], p, warn=None)), "COMME DANS RDR2", None),
        (20, 0.0, _ph(LK + "02.jpg", 0.5, 0.5, 1.0), "UNE ÉQUIPE DÉDIÉE", "DIALOGUES DES PASSANTS"),
        (21, 0.0, _ph(JL + "13.jpg", 0.4, 0.4, 1.0), "N°5 : TON COUPLE", None),
        (22, 0.0, _cd(JL + "16.jpg", lambda p: stat_card("RELATION", "Jason & Lucia : elle influence le récit", p)), "JAUGE DE RELATION", None),
        (23, 0.0, _ph(JL + "02.jpg", 0.5, 0.4, 1.0), "BRAQUAGE DISCRET", "= LIEN PLUS FORT"),
        (24, 0.0, _cd(VC + "27.jpg", lambda p: chips_card(["Focus (ralenti)", "Tir au genou", "Tir au coude"], p, "Pour viser")), "BONUS : NON MORTEL", None),
        (25, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Sources", ["Tests de la presse", "et Game Informer"], p, warn=None)), "SOURCES", None),
        (26, 0.0, _sp(JL + "03.jpg", (0.35, 0.4), JL + "08.jpg", (0.55, 0.5), "PROPRE", "IRRÉCUPÉRABLE"), None, None),
        (28, 0.0, _cd(VC + "27.jpg", lambda p: comment_card("Propre ou pas ?", p, typed="Irrécupérable, direct")), "ABONNE-TOI !", None),
    ]
    return _fv("nouveautes3", "nouveautes", shots, RED, "LES NOUVEAUTÉS")


# ---------- 27/11 12 h 30 · Port Gellhorn ----------
def video_gellhorn3():
    shots = [
        (0, 0.0, _ph(PG + "01.jpg", 0.25, 0.4, 1.0), "LA VILLE LA PLUS LOUCHE", None),
        (1, 0.0, _ph(PG + "06.jpg", 0.5, 0.5, 1.0), "PORT GELLHORN", None),
        (2, 0.0, _cd(PG + "06.jpg", lambda p: source_card("Rockstar Games", ["« La côte oubliée", "de Leonida »"], p, warn=None)), "LA CÔTE OUBLIÉE", None),
        (3, 0.0, _ph(PG + "01.jpg", 0.65, 0.6, 1.0), "MOTELS PAS CHERS", None),
        (3, 0.5, _ph(PG + "06.jpg", 0.3, 0.6, 1.3), None, "CENTRES COMMERCIAUX VIDES"),
        (4, 0.0, _cd(PG + "05.jpg", lambda p: chips_card(["Bière forte", "Antidouleurs", "Energy drinks"], p, "Ici, ça tourne à…")), "L’AMBIANCE", None),
        (4, 0.6, _ph(PG + "05.jpg", 0.3, 0.4, 1.0), None, "RELAIS ROUTIER"),
        (5, 0.0, _ph(PG + "05.jpg", 0.6, 0.4, 1.0), "LE CONSEIL OFFICIEL", None),
        (6, 0.0, _ph(MK + "01.jpg", 0.45, 0.5, 1.0), "MOTO TOUT-TERRAIN", None),
        (7, 0.0, _ph(PG + "03.jpg", 0.75, 0.5, 1.0), "TIENS TON PORTEFEUILLE", None),
        (8, 0.0, _cd(PG + "06.jpg", lambda p: source_card("Selon la presse", ["Le portrait de Panama City", "nord-ouest de la Floride"], p)), "PANAMA CITY ?", None),
        (9, 0.0, _cd(PG + "06.jpg", lambda p: chips_card(["Panama City", "Jacksonville", "Ocala"], p, "Étudiées par l’équipe de Rockstar")), "ÉTUDIÉES PAR ROCKSTAR", None),
        (10, 0.0, _cd(PG + "01.jpg", lambda p: stat_card("4", "choses à faire", p, **FIRE)), "4 CHOSES À FAIRE", None),
        (11, 0.0, _ph(PG + "01.jpg", 0.22, 0.35, 1.2), "N°1 : STARLET MOTEL", None),
        (12, 0.0, _ph(JL + "08.jpg", 0.5, 0.5, 1.0), "CHAPITRE 2", "LA PLANQUE"),
        (13, 0.0, _ph(PG + "01.jpg", 0.75, 0.6, 1.3), "AVIS DE DISPARITION", None),
        (14, 0.0, _ph(PG + "01.jpg", 0.5, 0.5, 1.0), "UNE ENQUÊTE…", None),
        (15, 0.0, _ph(PG + "06.jpg", 0.6, 0.5, 1.5), "TRÈS SOMBRE", None),
        (16, 0.0, _ph(VC + "22.jpg", 0.4, 0.5, 1.0), "N°2 : LE BOWLING", None),
        (17, 0.0, _cd(VC + "22.jpg", lambda p: source_card("Kingpin Bowling", ["Une opération illégale", "d’un gang"], p, warn=None)), "KINGPIN BOWLING", None),
        (18, 0.0, _cd(VC + "22.jpg", lambda p: stat_card("TROPHÉE", "« Let’s Go Bowling »", p, sub2="Vole les 3 objets de valeur", **FIRE)), "3 OBJETS À VOLER", None),
        (19, 0.0, _ph(VC + "24.jpg", 0.5, 0.5, 1.0), "N°3 : CHEZ MOSES", None),
        (20, 0.0, _ph(JL + "03.jpg", 0.3, 0.4, 1.0), "LUCIA SCANNE", "AVEC SON TÉLÉPHONE"),
        (21, 0.0, _cd(VC + "24.jpg", lambda p: stat_card("10", "véhicules à enregistrer", p, sub2="Trophée « On the Spot »")), "UN AUTRE TROPHÉE", None),
        (22, 0.0, _ph(PG + "06.jpg", 0.8, 0.4, 1.0), "MAIS ATTENDS…", None),
        (23, 0.0, _ph(PG + "06.jpg", 0.5, 0.2, 1.3), "N°4 : UN OVNI", None),
        (24, 0.0, _cd(PG + "01.jpg", lambda p: stat_card("2 H", "du matin, en pleine campagne", p, sub2="Près du Starlet Motel", **SKY)), "APRÈS 2 H DU MATIN", None),
        (25, 0.0, _cd(PG + "01.jpg", lambda p: list_card([("Une voiture abandonnée", "phares allumés", GOLD), ("Portières ouvertes", "personne autour", PINK),
                                                          ("Des vêtements", "éparpillés partout", VIOLET)], p, title="La scène", icon="123")), "LA SCÈNE", None),
        (26, 0.0, _ph(PG + "01.jpg", 0.5, 0.7, 1.5), "DES VÊTEMENTS PARTOUT", None),
        (27, 0.0, _ph(PG + "06.jpg", 0.5, 0.15, 1.6), "UN GRÉSILLEMENT…", None),
        (28, 0.0, _ph(PG + "01.jpg", 0.5, 0.15, 1.4), "UN FAISCEAU !", None),
        (29, 0.0, _cd(PG + "06.jpg", lambda p: stat_card("TROPHÉE", "« The Truth Is Out There »", p, sub2="La vérité est ailleurs", **SKY)), "THE TRUTH IS OUT THERE", None),
        (30, 0.0, _ph(PG + "06.jpg", 0.5, 0.4, 1.0), "LA VÉRITÉ EST AILLEURS", None),
        (31, 0.0, _ph(PG + "01.jpg", 0.3, 0.4, 1.0), "REVIENS UNE AUTRE NUIT", None),
        (32, 0.0, _cd(PG + "06.jpg", lambda p: source_card("Petit rappel", ["Panama City :", "comparaison de la presse"], p)), "PETIT RAPPEL", None),
        (33, 0.0, _sp(PG + "01.jpg", (0.25, 0.4), PG + "06.jpg", (0.5, 0.5), "J’OSE", "JAMAIS"), None, None),
        (34, 0.0, _cd(PG + "06.jpg", lambda p: comment_card("Tu y passes la nuit ?", p, typed="Je cherche l’OVNI !")), "ABONNE-TOI !", None),
    ]
    return _fv("gellhorn3", "gellhorn", shots, GOLD, "PORT GELLHORN")


# ---------- 27/11 18 h 30 · L'argent au début ----------
def video_argent3():
    codes = lambda p: notes_card(p, [("Ordinateur : CLEAVES", (30, 30, 60)), ("Coffre : 0072", (200, 40, 60)), ("Hangar : 0212", (40, 90, 200))], title="LES CODES")
    shots = [
        (0, 0.0, _ph(LK + "02.jpg", 0.5, 0.5, 1.0), "UN PERROQUET ?!", None),
        (1, 0.0, _cd(VC + "10.jpg", lambda p: stat_card("5", "façons de ne plus être fauché", p, **LIME)), "PLUS JAMAIS FAUCHÉ", None),
        (2, 0.0, _ph(LK + "02.jpg", 0.3, 0.5, 1.2), "N°1 : LE PERROQUET", None),
        (3, 0.0, _cd(LK + "02.jpg", lambda p: source_card("Three Sheets Liquor", ["Key Lento · chapitre 1", "après la quête de Shirley"], p, warn=None)), "KEY LENTO", None),
        (4, 0.0, _ph(JL + "12.jpg", 0.6, 0.4, 1.0), "NEUTRALISE LES GARDES", None),
        (4, 0.55, _ph(LK + "02.jpg", 0.75, 0.5, 1.0), None, "PARLE AU PERROQUET"),
        (5, 0.0, _cd(LK + "02.jpg", lambda p: comment_card("Où est le cash ?", p, typed="Where’s the cash?")), "DEMANDE-LUI", None),
        (6, 0.0, _cd(LK + "02.jpg", lambda p: stat_card("GENERATOR", "la réponse du perroquet", p, **FIRE)), "« GENERATOR »", None),
        (7, 0.0, _ph(VC + "22.jpg", 0.5, 0.6, 1.2), "LA GRILLE D’AÉRATION", "PRÈS DU GÉNÉRATEUR JAUNE"),
        (8, 0.0, _cd(VC + "22.jpg", lambda p: stat_card("1 000 $ +", "dans la grille", p, **LIME)), "PLUS DE 1 000 $", None),
        (9, 0.0, _cd(LK + "02.jpg", lambda p: stat_card("~ 2 500 $", "avec le coffre de l’arrière-boutique", p, **LIME)), "~2 500 $", None),
        (10, 0.0, _ph(GR + "01.jpg", 0.5, 0.5, 1.0), "N°2 : LE CRABE GÉANT", None),
        (11, 0.0, _ph(GR + "04.jpg", 0.5, 0.5, 1.0), "PELICAN VALLEY", "UN AVANT-POSTE"),
        (12, 0.0, _cd(GR + "02.jpg", codes), "LES CODES", None),
        (13, 0.0, _cd(GR + "02.jpg", codes), "COFFRE : 0072", None),
        (14, 0.0, _cd(GR + "02.jpg", codes), "HANGAR : 0212", None),
        (15, 0.0, _cd(GR + "03.jpg", lambda p: stat_card("10 000 $", "en billets marqués", p, sub2="+ un jet-ski", **LIME)), "10 000 $", None),
        (16, 0.0, _ph(GR + "08.jpg", 0.5, 0.7, 1.3), "UN CRABE GÉANT !", None),
        (17, 0.0, _ph(LK + "04.jpg", 0.5, 0.5, 1.0), "N°3 : LE TRÉSOR", None),
        (18, 0.0, _ph(LK + "07.jpg", 0.4, 0.5, 1.0), "ISLAND DREAMS", "KENTON TE DONNE UN SCANNER"),
        (19, 0.0, _ph(LK + "04.jpg", 0.75, 0.6, 1.2), "LES ÉPAVES", "IL RACHÈTE TOUT"),
        (20, 0.0, _ph(VC + "24.jpg", 0.5, 0.5, 1.0), "N°4 : LES VOITURES", None),
        (21, 0.0, _cd(VC + "24.jpg", lambda p: stat_card("3 / JOUR", "au Pay ’n’ Spray", p, sub2="Au début du jeu")), "PAY ’N’ SPRAY", None),
        (22, 0.0, _cd(PG + "06.jpg", lambda p: stat_card("1-2 000 $", "par vieille voiture, chez Moses", p, sub2="Port Gellhorn · sans traceur", **LIME)), "MOSES", None),
        (23, 0.0, _ph(JL + "17.jpg", 0.5, 0.4, 1.0), "MAIS ATTENDS…", None),
        (24, 0.0, _ph(JL + "02.jpg", 0.5, 0.4, 1.0), "N°5 : LA RÈGLE D’OR", None),
        (25, 0.0, _ph(JL + "09.jpg", 0.55, 0.5, 1.0), "MORT OU ARRÊTÉ ?", "TU PERDS TON CASH"),
        (26, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("20 000 $", "maximum dans ton portefeuille", p)), "20 000 $ MAX", None),
        (27, 0.0, _cd(VC + "10.jpg", lambda p: chips_card(["Distributeur", "Avant chaque coup"], p, "Dépose ton argent")), "DÉPOSE TON ARGENT", None),
        (28, 0.0, _sp(LK + "02.jpg", (0.4, 0.5), GR + "01.jpg", (0.2, 0.75), "LE PERROQUET", "LE CRABE"), None, None),
        (29, 0.0, _cd(VC + "10.jpg", lambda p: comment_card("Ton meilleur plan ?", p, typed="Le crabe géant !")), "ABONNE-TOI !", None),
    ]
    return _fv("argent3", "argent", shots, GREEN, "PLUS JAMAIS FAUCHÉ")


# ---------- 28/11 12 h 30 · Qui est Dre'Quan Priest ? ----------
def video_drequan3():
    Q = _P + "drequan_priest_"
    shots = [
        (0, 0.0, _ph(Q + "03.jpg", 0.45, 0.22, 1.3), "QUI EST DRE’QUAN ?", None),
        (1, 0.0, _ph(Q + "02.jpg", 0.7, 0.3, 1.2), None, "C’EST LUI QUI LE DIT"),
        (2, 0.0, ("clip", "clips/drequan_priest.mp4", 0.5), "DRE’QUAN PRIEST", None),
        (3, 0.0, _cd(VC + "13.jpg", lambda p: stat_card("4", "choses à savoir sur lui", p)), "4 CHOSES À SAVOIR", None),
        (4, 0.0, _ph(Q + "04.jpg", 0.4, 0.3, 1.2), "N°1 : UN DÉBROUILLARD", None),
        (5, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Rockstar Games", ["« Plus débrouillard", "que gangster »"], p, warn=None)), "SELON ROCKSTAR", None),
        (6, 0.0, _ph(Q + "04.jpg", 0.75, 0.5, 1.0), "LA MUSIQUE AVANT TOUT", None),
        (7, 0.0, _ph(_P + "boobie_ike_02.jpg", 0.32, 0.3, 1.0), "N°2 : SON LABEL", None),
        (8, 0.0, _cd(VC + "04.jpg", lambda p: stat_card("ONLY RAW", "Records, avec Boobie Ike", p)), "ONLY RAW RECORDS", None),
        (9, 0.0, _sp(_P + "boobie_ike_03.jpg", (0.38, 0.35), Q + "03.jpg", (0.45, 0.25), "L’ARGENT", "LES TALENTS"), None, None),
        (10, 0.0, _ph(_P + "real_dimez_04.jpg", 0.5, 0.35, 1.0), "LES REAL DIMEZ", None),
        (11, 0.0, _ph(Q + "02.jpg", 0.7, 0.3, 1.0), "SES JOURS AU CLUB…", None),
        (12, 0.0, _ph(Q + "03.jpg", 0.45, 0.25, 1.5), "SONT COMPTÉS", None),
        (13, 0.0, _ph(VC + "27.jpg", 0.5, 0.5, 1.0), "TOUT VICE CITY", None),
        (14, 0.0, _ph(Q + "03.jpg", 0.45, 0.3, 1.0), "N°3 : SA PHRASE CULTE", None),
        (15, 0.0, _cd(VC + "13.jpg", lambda p: source_card("Dre’Quan Priest", ["« Les danseuses, c’est mes", "directeurs artistiques »"], p, warn=None)), "SES « A&R »", None),
        (16, 0.0, _cd(VC + "13.jpg", lambda p: source_card("Dre’Quan Priest", ["« Si le son marche,", "les DJ vont le passer »"], p, warn=None)), "LES DJ VONT LE PASSER", None),
        (17, 0.0, ("clip", "clips/drequan_priest.mp4", 0.5), "BANDE-ANNONCE 2", None),
        (18, 0.0, _ph(VC + "01.jpg", 0.5, 0.5, 1.0), "MAIS ATTENDS…", None),
        (19, 0.0, _ph(VC + "27.jpg", 0.3, 0.5, 1.0), "N°4 : TON GUIDE", None),
        (20, 0.0, _cd(VC + "01.jpg", lambda p: chips_card(["Welcome to Vice City"], p, "La mission · chapitre 3")), "WELCOME TO VICE CITY", None),
        (21, 0.0, _ph(_P + "boobie_ike_02.jpg", 0.58, 0.15, 1.3), "JACK OF HEARTS", "CROSSTOWN"),
        (22, 0.0, _ph(JL + "01.jpg", 0.47, 0.3, 1.2), "UN VIEIL AMI DE JASON", None),
        (23, 0.0, _cd(VC + "08.jpg", lambda p: stat_card("~ 7", "missions avec lui", p, sub2="Chapitres 3 et 4")), "~7 MISSIONS", None),
        (24, 0.0, _ph(_P + "real_dimez_02.jpg", 0.45, 0.4, 1.0), "TOP BILLING", "LE CONCERT DES DIMEZ"),
        (25, 0.0, _cd(VC + "13.jpg", lambda p: stat_card("N. MACABROAD", "Naiqui Macabroad, la voix de Dre’Quan", p, sub2="Crédits du jeu")), "SA VOIX", None),
        (26, 0.0, _sp(Q + "04.jpg", (0.4, 0.3), Q + "02.jpg", (0.7, 0.3), "MAGNAT", "TROP LOIN"), None, None),
        (28, 0.0, _cd(VC + "27.jpg", lambda p: comment_card("Magnat ou trop loin ?", p, typed="Futur magnat !")), "ABONNE-TOI !", None),
    ]
    return _fv("drequan3", "drequan", shots, VIOLET, "QUI EST-IL ?")


# ---------- 28/11 18 h 30 · 30 fps ----------
def video_fps3():
    shots = [
        (0, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("30 FPS", "même sur PS5 Pro", p, c1=(255, 130, 130), c2=(220, 40, 80))), "30 FPS ?!", None),
        (1, 0.0, _ph(JL + "09.jpg", 0.55, 0.45, 1.0), None, "PAS UN BUG"),
        (2, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Rockstar Games", ["Confirmé le 10 novembre"], p, warn=None)), "CONFIRMÉ", None),
        (3, 0.0, _cd(VC + "10.jpg", lambda p: chips_card(["PS5", "PS5 Pro", "Xbox Series X|S"], p, "30 images/s sur…")), "TOUTES LES CONSOLES", None),
        (4, 0.0, _cd(VC + "17.jpg", lambda p: crossed_stat("MODE PERF.", "pas de mode performance", p)), "PAS DE MODE PERF", None),
        (5, 0.0, _cd(VC + "17.jpg", lambda p: crossed_stat("60 FPS", "ni 40, ni 60", p)), "NI 40, NI 60", None),
        (6, 0.0, _ph(JL + "19.jpg", 0.5, 0.4, 1.0), "POURQUOI ?", None),
        (7, 0.0, _ph(VC + "03.jpg", 0.5, 0.5, 1.0), "CE QU’IL FAUT SAVOIR", None),
        (8, 0.0, _ph(VC + "17.jpg", 0.5, 0.5, 1.0), "N°1 : LE PROCESSEUR", None),
        (9, 0.0, _cd(VC + "08.jpg", lambda p: list_card([("Processeur (CPU)", "le vrai blocage", RED), ("Carte graphique", "pas le problème", GREEN)],
                                                         p, title="Selon Digital Foundry", icon="12")), "LE CPU, PAS LE GPU", None),
        (10, 0.0, _cd(VC + "08.jpg", lambda p: crossed_stat("60 FPS", "« pas viable » selon DF", p)), "60 FPS : PAS VIABLE", None),
        (11, 0.0, _ph(VC + "06.jpg", 0.5, 0.45, 1.0), "40 FPS ? TRÈS DUR", None),
        (12, 0.0, _ph(JL + "20.jpg", 0.5, 0.4, 1.0), "N°2 : LA PS5 PRO", None),
        (13, 0.0, _ph(VC + "10.jpg", 0.5, 0.5, 1.0), "L’IMAGE, PAS LA FLUIDITÉ", None),
        (14, 0.0, _cd(VC + "10.jpg", lambda p: chips_card(["PSSR", "Ray tracing"], p, "Les bonus de la PS5 Pro")), "PSSR + RAY TRACING", None),
        (15, 0.0, _cd(VC + "11.jpg", lambda p: stat_card("« 4K »", "convaincante, selon Digital Foundry", p, **SKY)), "PRESQUE DE LA 4K", None),
        (16, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("1440P", "PS5 et Series X, en interne", p)), "N°3 : 1440P", None),
        (17, 0.0, _ph(JL + "19.jpg", 0.45, 0.45, 1.2), "~20 FPS EN FUSILLADE", "SERIES X"),
        (18, 0.0, _ph(VC + "08.jpg", 0.5, 0.5, 1.0), "MAIS ATTENDS…", None),
        (19, 0.0, _ph(VC + "17.jpg", 0.4, 0.5, 1.3), "N°4 : LA SERIES S", None),
        (20, 0.0, _cd(VC + "22.jpg", lambda p: stat_card("720P", "souvent autour de 25 fps", p, c1=(255, 130, 130), c2=(220, 40, 80))), "720P, ~25 FPS", None),
        (21, 0.0, _cd(VC + "22.jpg", lambda p: source_card("Digital Foundry", ["« Joue sur une autre console,", "pour l’instant »"], p, warn=None)), "AUTRE CONSOLE ?", None),
        (22, 0.0, _ph(VC + "01.jpg", 0.5, 0.5, 1.0), "N°5 : ROCKSTAR ASSUME", None),
        (23, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Rockstar Games", ["« Plays best on PS5 »", "Pensé pour les consoles actuelles"], p, warn=None)), "MEILLEUR SUR PS5", None),
        (24, 0.0, _cd(VC + "27.jpg", lambda p: crossed_stat("PS4 / ONE", "pas d’ancienne génération", p)), "PAS DE PS4", None),
        (25, 0.0, _cd(VC + "11.jpg", lambda p: source_card("Attention", ["Chiffres au lancement"], p, warn="Aucun patch annoncé")), "AU LANCEMENT", None),
        (26, 0.0, _ph(JL + "03.jpg", 0.35, 0.4, 1.0), "AUCUN PATCH…", None),
        (27, 0.0, _ph(JL + "03.jpg", 0.6, 0.4, 1.0), "POUR L’INSTANT", None),
        (28, 0.0, _sp(JL + "06.jpg", (0.6, 0.4), JL + "17.jpg", (0.5, 0.4), "ÇA ME GÊNE", "AUCUN SOUCI"), None, None),
        (29, 0.0, _cd(VC + "27.jpg", lambda p: comment_card("30 fps, ça te gêne ?", p, typed="Pas du tout !")), "ABONNE-TOI !", None),
    ]
    return _fv("fps3", "fps", shots, BLUE, "30 FPS")


# ---------- 29/11 12 h 30 · Mount Kalaga ----------
def video_kalaga3():
    shots = [
        (0, 0.0, _ph(MK + "04.jpg", 0.6, 0.5, 1.0), "LE SECRET DE KALAGA", None),
        (1, 0.0, _ph(MK + "02.jpg", 0.55, 0.5, 1.0), "MOUNT KALAGA", "LE GRAND NORD"),
        (2, 0.0, _cd(MK + "04.jpg", lambda p: source_card("Rockstar Games", ["« De l’espace pour respirer »"], p, warn=None)), "DE L’ESPACE", None),
        (3, 0.0, _cd(MK + "05.jpg", lambda p: chips_card(["Chasse", "Pêche", "Tout-terrain"], p, "Au programme")), "CHASSE, PÊCHE…", None),
        (4, 0.0, _ph(MK + "03.jpg", 0.25, 0.5, 1.0), "MYSTIQUES ET PARANOS", None),
        (4, 0.55, _ph(MK + "03.jpg", 0.7, 0.5, 1.0), None, "LOIN DU GOUVERNEMENT"),
        (5, 0.0, _cd(MK + "06.jpg", lambda p: stat_card("4", "choses à faire là-haut", p, **LIME)), "4 CHOSES À FAIRE", None),
        (6, 0.0, _ph(MK + "05.jpg", 0.6, 0.5, 1.0), "N°1 : LA CHASSE", None),
        (7, 0.0, _cd(MK + "05.jpg", lambda p: chips_card(["Jumelles", "Focus"], p, "Bret Vogel t’apprend à pister")), "AVEC BRET VOGEL", None),
        (7, 0.55, _ph(MK + "05.jpg", 0.35, 0.5, 1.2), None, "PISTE LE CERF"),
        (8, 0.0, _cd(MK + "05.jpg", lambda p: chips_card(["Veteran Hunted"], p, "La mission · chapitre 2")), "VETERAN HUNTED", None),
        (9, 0.0, _cd(MK + "05.jpg", lambda p: stat_card("500 $", "+ un fusil unique", p, **LIME)), "500 $ + UN FUSIL", None),
        (10, 0.0, _cd(MK + "05.jpg", lambda p: stat_card("TROPHÉE", "« Fair Game »", p, sub2="Un animal unique pour Bret")), "FAIR GAME", None),
        (11, 0.0, _ph(MK + "04.jpg", 0.7, 0.5, 1.0), "N°2 : LE CANYON ROUGE", None),
        (12, 0.0, _cd(MK + "04.jpg", lambda p: source_card("Selon les fans", ["Le portrait de Providence Canyon"], p)), "PROVIDENCE CANYON", None),
        (13, 0.0, _cd(MK + "04.jpg", lambda p: stat_card("GÉORGIE", "pas en Floride !", p, **FIRE)), "EN GÉORGIE !", None),
        (14, 0.0, _ph(MK + "01.jpg", 0.45, 0.5, 1.0), "N°3 : LES CASSE-COU", None),
        (15, 0.0, _ph(MK + "01.jpg", 0.3, 0.5, 1.0), "MOTO DANS LES CARRIÈRES", None),
        (15, 0.35, _ph(MK + "06.jpg", 0.65, 0.5, 1.0), None, "KAYAK SOUS LE PONT"),
        (15, 0.7, _ph(MK + "02.jpg", 0.6, 0.45, 1.0), None, "HÉLICO"),
        (16, 0.0, _ph(MK + "04.jpg", 0.4, 0.5, 1.0), "TERRAIN DE JEU", None),
        (17, 0.0, _ph(MK + "02.jpg", 0.3, 0.3, 1.0), "MAIS ATTENDS…", None),
        (18, 0.0, _ph(MK + "04.jpg", 0.85, 0.3, 1.0), "N°4 : LA MÉDITATION", None),
        (19, 0.0, _cd(MK + "06.jpg", lambda p: chips_card(["Spots cachés", "Partout dans Leonida"], p, "La méditation")), "DES SPOTS CACHÉS", None),
        (20, 0.0, _cd(MK + "04.jpg", lambda p: stat_card("ASCENT", "cercle de pierres au sommet", p, **SKY)), "ASCENT", None),
        (21, 0.0, _ph(MK + "04.jpg", 0.85, 0.25, 1.3), "IL APPARAÎT EN DERNIER", None),
        (22, 0.0, _cd(MK + "06.jpg", lambda p: stat_card("TROPHÉE", "« Positive Mental Attitude »", p, **LIME)), "LE TROPHÉE ZEN", None),
        (23, 0.0, _cd(MK + "04.jpg", lambda p: source_card("Petit rappel", ["Lieux réels :", "comparaisons des fans"], p)), "PETIT RAPPEL", None),
        (24, 0.0, _sp(MK + "05.jpg", (0.6, 0.5), MK + "01.jpg", (0.45, 0.5), "CHASSE", "MOTO"), None, None),
        (25, 0.0, _ph(MK + "04.jpg", 0.5, 0.3, 1.0), "OU MÉDITATION ?", None),
        (26, 0.0, _cd(MK + "04.jpg", lambda p: comment_card("Chasse, moto ou zen ?", p, typed="Méditation au sommet")), "ABONNE-TOI !", None),
    ]
    return _fv("kalaga3", "kalaga", shots, GREEN, "MOUNT KALAGA")


# ---------- 29/11 18 h 30 · Qui est Cal Hampton ? ----------
def video_cal3():
    C = _P + "cal_hampton_"
    shots = [
        (0, 0.0, _ph(C + "01.jpg", 0.71, 0.25, 1.4), "LES OISEAUX ESPIONS ?!", None),
        (1, 0.0, ("clip", "clips/cal_hampton.mp4", 0.5), "CAL HAMPTON", None),
        (2, 0.0, _cd(VC + "11.jpg", lambda p: stat_card("4", "choses à savoir sur lui", p, **SKY)), "4 CHOSES À SAVOIR", None),
        (3, 0.0, _ph(C + "02.jpg", 0.55, 0.25, 1.2), "N°1 : SA DEVISE", None),
        (4, 0.0, _cd(LK + "01.jpg", lambda p: source_card("Rockstar Games", ["Sa devise, en une question…"], p, warn=None)), "SELON ROCKSTAR", None),
        (5, 0.0, _cd(VC + "27.jpg", lambda p: source_card("Cal Hampton", ["« Et si tout ce qu’on lit", "sur Internet était vrai ? »"], p, warn=None)), "ET SI C’ÉTAIT VRAI ?", None),
        (6, 0.0, _ph(C + "04.jpg", 0.5, 0.25, 1.0), "AMI DE JASON", "ASSOCIÉ DE BRIAN"),
        (7, 0.0, _ph(C + "03.jpg", 0.4, 0.3, 1.0), "CHEZ LUI, EN SÉCURITÉ", None),
        (8, 0.0, _cd(LK + "05.jpg", lambda p: chips_card(["Radio garde-côtes", "Bières", "Navigation privée"], p, "Le passe-temps de Cal")), "IL ESPIONNE", None),
        (9, 0.0, _ph(C + "01.jpg", 0.71, 0.3, 1.0), "N°2 : SES THÉORIES", None),
        (10, 0.0, _cd(GR + "05.jpg", lambda p: source_card("Cal Hampton", ["« Beaucoup trop d’oiseaux", "en formation parfaite »"], p, warn=None)), "LES OISEAUX…", None),
        (11, 0.0, _ph(GR + "05.jpg", 0.5, 0.2, 1.3), "PHRASE OFFICIELLE", None),
        (12, 0.0, _cd(GR + "05.jpg", lambda p: stat_card("62", "espèces d’oiseaux dans le jeu", p, **SKY)), "62 ESPÈCES !", None),
        (13, 0.0, _ph(C + "03.jpg", 0.4, 0.2, 1.5), "OUVRE L’ŒIL", None),
        (14, 0.0, _ph(C + "02.jpg", 0.45, 0.3, 1.0), "N°3 : PARTOUT", None),
        (15, 0.0, _cd(LK + "05.jpg", lambda p: chips_card(["Gone Fishing"], p, "La 1re mission de Jason")), "SA 1RE MISSION", None),
        (16, 0.0, _ph(LK + "05.jpg", 0.3, 0.5, 1.0), "PÊCHE SPÉCIALE", None),
        (17, 0.0, _cd(VC + "17.jpg", lambda p: source_card("Le téléphone de Jason", ["Appli de scanner de police", "installée par Cal"], p, warn=None)), "SCANNER DE POLICE", None),
        (18, 0.0, _ph(VC + "17.jpg", 0.5, 0.4, 1.0), "LA RADIO DES FLICS !", None),
        (19, 0.0, _ph(C + "04.jpg", 0.45, 0.4, 1.0), "MISSION FENG SHUI", "CONSOLE ENTRE POTES"),
        (20, 0.0, _ph(C + "01.jpg", 0.71, 0.25, 1.6), "MAIS ATTENDS…", None),
        (21, 0.0, ("clip", "clips/cal_hampton.mp4", 0.5), "N°4 : SA VOIX", None),
        (22, 0.0, _cd(VC + "27.jpg", lambda p: stat_card("B. MOYNIHAN", "Bobby Moynihan, la voix de Cal", p, sub2="~10 ans au Saturday Night Live")), "BOBBY MOYNIHAN", None),
        (23, 0.0, _cd(VC + "11.jpg", lambda p: source_card("GameRoll", ["Insider · mars 2026", "« Moynihan, à 95 % »"], p, warn=None)), "DEVINÉ EN MARS", None),
        (24, 0.0, _cd(VC + "11.jpg", lambda p: stat_card("95 %", "sûr de lui", p, **SKY)), "SÛR À 95 %", None),
        (25, 0.0, _cd(VC + "10.jpg", lambda p: crossed_stat("JAY KLAITZ", "la voix de Lester (GTA 5)", p)), "PAS LUI", None),
        (26, 0.0, _cd(VC + "10.jpg", lambda p: source_card("Jay Klaitz", ["« Non, ce n’est pas moi »"], p, warn=None)), "« PAS MOI »", None),
        (27, 0.0, _sp(C + "02.jpg", (0.55, 0.25), C + "03.jpg", (0.4, 0.25), "GÉNIE", "PARANO"), None, None),
        (29, 0.0, _cd(VC + "27.jpg", lambda p: comment_card("Génie ou parano ?", p, typed="Parano, à 100 % !")), "ABONNE-TOI !", None),
    ]
    return _fv("cal3", "cal", shots, BLUE, "QUI EST-IL ?")


for _k in ["boobie", "astuces", "keys", "duree", "dimez", "eggs", "grass", "nouveautes", "gellhorn", "argent", "drequan", "fps", "kalaga", "cal"]:
    VIDEOS[_k + "3"] = globals()["video_" + _k + "3"]


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

