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
