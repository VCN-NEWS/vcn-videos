import sys, os
from PIL import Image
import v2
from v2 import *
from scripts import TEXTS, DUR


def card_seg_full(builder, y=880):
    def fn(fr, lt, dur, tout):
        p = clamp((lt - 0.1) / max(1.0, dur * 0.85))
        place(fr, shadowed(builder(p)), W / 2, y, lt, 0.05, tout, scale_from=0.9)
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
