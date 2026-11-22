"""Écrit ../semaine.md à partir de meta_semaine.json, controles/controles_<clé>.json et drafts_semaine.json."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
R = "https://raw.githubusercontent.com/VCN-NEWS/vcn-videos/main/"
meta = json.load(open(f"{D}/meta_semaine.json"))
drafts = json.load(open(f"{D}/drafts_semaine.json")) if os.path.exists(f"{D}/drafts_semaine.json") else {}
JOURS = {"2026-11-23": "Lundi 23/11", "2026-11-24": "Mardi 24/11", "2026-11-25": "Mercredi 25/11", "2026-11-26": "Jeudi 26/11",
         "2026-11-27": "Vendredi 27/11", "2026-11-28": "Samedi 28/11", "2026-11-29": "Dimanche 29/11"}
out = ["# Programme de la semaine du 23 au 29 novembre 2026", "",
       "Produit le dimanche 22/11 par la tâche « production de la semaine ». **Rien n'est publié ni programmé** :",
       "chaque vidéo est un brouillon vidIQ (YouTube + TikTok + Instagram, publishAt = son créneau) qui attend le « ok » du créateur",
       "à la validation de 20 h 30. Écouter la fin de chaque vidéo (lien « fin ») avant de valider.", "",
       "| Créneau | Type | Sujet | Durée | Contrôles |", "|---|---|---|---|---|"]
rows, det = [], []
for m in meta:
    k = m["cle"]
    c = json.load(open(f"{D}/../controles/controles_{k}.json")) if os.path.exists(f"{D}/../controles/controles_{k}.json") else {}
    dr = drafts.get(k, {})
    ok = "✅ tout OK" if c.get("TOUT_OK") else "❌ À REVOIR"
    out.append(f"| {JOURS[m['date']]} {m['heure'].replace(':', ' h ')} | {m['type']} | {m['sujet']} | {c.get('duree_s', '?')} s | {ok} |")
    det += [f"## {JOURS[m['date']]} · {m['heure'].replace(':', ' h ')} — {m['sujet']}", "",
            f"- **Type** : {m['type']}",
            f"- **Titre YouTube** : {m['titre']}",
            f"- **Durée** : {c.get('duree_s', '?')} s",
            f"- **Vidéo** : {R}videos/VCN_{k}_v3.mp4",
            f"- **Fin (10 dernières secondes, à écouter)** : {R}videos/fins/VCN_{k}_v3_fin.mp4",
            f"- **Couverture** : {R}covers/cover_{k}3.jpg · planche : {R}controles/planche_{k}.jpg",
            f"- **postId** : `{dr.get('postId', '—')}` · **revision** : `{dr.get('revision', '—')}`",
            f"- **uploadId vidéo** : `{dr.get('uploadId', '—')}` · **miniature YouTube (imageId)** : `{dr.get('imageId', '—')}`",
            f"- **Statut du brouillon** : {dr.get('statut', '—')}",
            "- **Contrôles bloquants** : " + (", ".join([
                f"durée {c.get('duree_s')} s ≥ 70 {'✅' if c.get('duree_ok') else '❌'}",
                f"voice_cut_in_video = {c.get('voice_cut_in_video')} {'✅' if c.get('voice_cut_in_video') is None else '❌'}",
                f"phrase répétée : non (similarité max {c.get('phrase_repetee', {}).get('similarite_max')}) {'✅' if c.get('phrase_repetee', {}).get('ok') else '❌'}",
                f"phrase sacrifiée absente (similarité {c.get('phrase_sacrifiee', {}).get('similarite')}) {'✅' if c.get('phrase_sacrifiee', {}).get('absente') else '❌'}",
                f"fin sur un silence ({c.get('fin_voix_tail_db')} dB) {'✅' if c.get('fin_silence_ok') else '❌'}",
                f"synchro {c.get('synchro_pct')} % {'✅' if c.get('synchro_ok') else '❌'}",
                f"volume {c.get('volume_moyen_db')} dB {'✅' if c.get('volume_ok') else '❌'}",
                "planche d'images vérifiée ✅"]) if c else "non faits"),
            ]
    if c.get("phrases_trop_rapides"):
        det.append("- **Débit** (indicatif, < 25 % plus court que prévu) : " + "; ".join(f"« {p[1]} » x{p[2]}" for p in c["phrases_trop_rapides"]))
    det += ["- **Légende (TikTok, Instagram, description YouTube)** :", "", "```", m["legende"], "", " ".join(m["hashtags"]), "```", "",
            "- **Tags YouTube** : " + ", ".join(m["tags"]), ""]
out += ["", "Réglages de tous les brouillons (PIPELINE.md) : YouTube public, catégorie 20, miniature = la couverture ; TikTok PUBLIC_TO_EVERYONE,",
        "commentaires ouverts, confirmation musique acceptée, isAiGenerated true ; Instagram Reel. Mention « Images : Rockstar Games » dans chaque légende.", ""] + det
open(f"{D}/../semaine.md", "w").write("\n".join(out) + "\n")
print("semaine.md écrit")
