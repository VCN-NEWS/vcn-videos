# Pipeline quotidien VCN (1 vidéo/jour)

1. **Veille** : recherche web + vidIQ (tendances GTA 6). Éviter les sujets déjà listés dans `sujets.md`.
2. **Vérification** : chaque chiffre recoupé sur 2 sources ; mention « non confirmé » si Rockstar n'a pas confirmé.
3. **Script** : 150-190 mots en français, accroche en 1 phrase, une info par phrase, question finale + « abonne-toi ». Durée voix 60-70 s.
4. **Voix** : Hedra `generate_speech`, modèle elevenlabs-v3, voix « Simon P. » `voice_f416ff19-9a7d-40f4-9a21-9b703c4d54ae`, langue fr (~15 crédits).
   Télécharger le MP3 dans `engine/voix_<clé>.mp3`.
5. **Montage** : ajouter le texte dans `engine/scripts.py` (TEXTS + DUR = durée audio en s) et une fonction `video_<clé>()` dans `engine/videos.py`
   (segments = (index de phrase, LABEL, headline, carte)). Cartes dispo dans `engine/v2.py` et `engine/render.py`.
   Puis : `cd engine && python3 videos.py render <clé> && python3 finish.py mix <clé> && python3 finish.py cover <clé>`
   (ajouter l'entrée correspondante dans `COVERS` de finish.py).
6. **Hébergement** : copier `GTA6_<clé>.mp4` dans `videos/`, commit + push. Lien brut :
   `https://raw.githubusercontent.com/VCN-NEWS/vcn-videos/main/videos/<fichier>.mp4`
7. **Brouillon** : vidIQ `vidiq_video_upload` (url brute) puis `vidiq_social_post_draft_create` vers
   YouTube `UChDCsyx5Z3dYBgHCjhJlr_g`, TikTok `_000C3p2_f0EOgI0x3l-7QIDg9RN927wqzmC`, Instagram `28582956308046477`,
   à 18 h 30 (Europe/Paris). Réglages choisis par le créateur : YouTube public, catégorie 20 ;
   TikTok PUBLIC_TO_EVERYONE, commentaires ouverts, confirmation musique acceptée, isAiGenerated true.
8. **Validation** : montrer le brouillon et attendre le « ok » du créateur avant `vidiq_social_post_publish`.
9. Ajouter le sujet publié à `sujets.md`.

## Exigences de qualité (à vérifier avant chaque brouillon)

**Attrayant et viral**
- L'accroche est visible dès la 1re image (titre choc + première carte) et la 1re phrase crée une surprise ou une question.
- Un sujet = une promesse claire ; un chiffre ou un fait étonnant dans les 5 premières secondes.
- Une info par phrase, une carte par info ; pas plus de 6-7 s sans changement visuel.
- Fin sur une question simple qui pousse à commenter, puis « abonne-toi ».
- Titre court avec écart de curiosité (sans mentir), 1-2 emojis, #shorts ; légende avec 6-10 hashtags (dont #GTA6 #GTAVI #VCN).
- Couverture : 3 lignes max de texte géant + 1 carte.

**Monétisable**
- Durée finale > 60 s (TikTok Creator Rewards) — viser 62-75 s.
- Script original avec un angle et une explication (pas une simple lecture d'article) — règle YouTube contre le contenu « inauthentique ».
- Varier d'une vidéo à l'autre : thème de fond (`theme` = night / sunset / day), couleurs des titres, types de cartes, structure (liste, duel, explication, chronologie).
- Aucun extrait, image, logo ni musique de Rockstar ou de tiers ; musique générée par le moteur uniquement.
- Faits vérifiés sur 2 sources, « non confirmé » quand c'est le cas ; aucune info qui deviendra fausse avant l'heure de publication.
- Mention « contenu IA » activée (TikTok isAiGenerated).

**Contrôle technique**
- Regarder une planche d'images (1 toutes les 4 s) : chaque carte correspond à la phrase dite.
- Synchro : > 95 % des mots affichés pendant que la voix parle.
- Volume : voix nettement au-dessus de la musique (moyenne autour de -16 dB).
