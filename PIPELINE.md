# Pipeline quotidien VCN (1 vidéo/jour)

1. **Veille** : recherche web + vidIQ (tendances GTA 6). Éviter les sujets déjà listés dans `sujets.md`.
2. **Vérification** : chaque chiffre recoupé sur 2 sources ; mention « non confirmé » si Rockstar n'a pas confirmé.
3. **Script** : 150-190 mots en français, accroche en 1 phrase, une info par phrase, question finale + « abonne-toi ». Durée voix 60-70 s.
4. **Voix** : Hedra `generate_speech`, modèle elevenlabs-v3, voix « Simon P. » `voice_f416ff19-9a7d-40f4-9a21-9b703c4d54ae`, langue fr (~15 crédits).
   **Ton raconté, pas lu** (demande du créateur) : `model_specific_parameters = {"stability": 0.4}` (la valeur par défaut 1.0 donne un ton de lecture),
   script écrit à l'oral (phrases courtes, « tu sais quoi ? », « et là… », apartés, suspense), et 2 à 4 balises d'expression ElevenLabs v3
   placées avec parcimonie : [excited], [curious], [whispers], [laughs], [dramatic pause]. Le texte affiché en sous-titres ne contient pas les balises.
   Télécharger le MP3 dans `engine/voix_<clé>.mp3` (le domaine Hedra est autorisé).
5. **Montage** (série « Qui est… ? » : `engine/series.py` + `engine/photo.py`, médias de `bibliotheque/`) : ajouter le texte dans `engine/scripts.py` (TEXTS + DUR = durée audio en s) et une fonction `video_<clé>()` dans `engine/videos.py`
   (segments = (index de phrase, LABEL, headline, carte)). Cartes dispo dans `engine/v2.py` et `engine/render.py`.
   Puis : `cd engine && python3 videos.py render <clé> && python3 finish.py mix <clé> && python3 finish.py cover <clé>`
   (ajouter l'entrée correspondante dans `COVERS` de finish.py).
5b. **Couverture de profil (OBLIGATOIRE, toutes les vidéos)** : TikTok et Instagram affichent la 1re image de la vidéo
   sur la grille du profil. Ajouter une entrée dans `COVERS` de `engine/cover.py` puis
   `cd engine && python3 cover.py <clé> apply` (incruste la couverture sur les 0,35 premières secondes, durée et son inchangés ;
   pour une vidéo d'actu, adapter le chemin dans `__main__` à `videos/GTA6_<clé>.mp4`).
   Style validé par le créateur (couverture de Lucia = référence, `covers/cover_lucia.jpg`) :
   - **Personnage** : TOUJOURS un gros plan du visage (regard caméra ou expression intense), le visage remplit le haut de l'image ;
     choisir dans `bibliotheque/` la photo où le visage est le plus grand et net, régler `focus`/`zoom` sur le visage.
   - **Lieu** : le même style en plan « carte postale » : le point le plus spectaculaire du lieu (monument, plage, skyline, néons)
     en grand dans le haut de l'image, couleurs vives.
   Règles : grande photo officielle,
   2 lignes de titre géant au dégradé GTA, 1 pastille jaune d'accroche (3-4 mots), logo VCN en haut ;
   tout le texte dans la zone 3:4 de la grille (y 240 → 1680). Vérifier l'image 0 de la vidéo finale et la grille recadrée 3:4.
   Pour YouTube, téléverser aussi `covers/cover_<clé>.jpg` (`vidiq_upload_image`) et le passer en `thumbnailImageId`.
6. **Hébergement** : copier `GTA6_<clé>.mp4` dans `videos/`, commit + push. Lien brut :
   `https://raw.githubusercontent.com/VCN-NEWS/vcn-videos/main/videos/<fichier>.mp4`
7. **Brouillon** : vidIQ `vidiq_video_upload` (url brute) puis `vidiq_social_post_draft_create` vers
   YouTube `UChDCsyx5Z3dYBgHCjhJlr_g`, TikTok `_000C3p2_f0EOgI0x3l-7QIDg9RN927wqzmC`, Instagram `28582956308046477`,
   à 18 h 30 (Europe/Paris). Réglages choisis par le créateur : YouTube public, catégorie 20 ;
   TikTok PUBLIC_TO_EVERYONE, commentaires ouverts, confirmation musique acceptée, isAiGenerated true.
8. **Validation** : montrer le brouillon et attendre le « ok » du créateur avant `vidiq_social_post_publish`.
9. Ajouter le sujet publié à `sujets.md`.

## Format standard : v3 « plein écran » (validé par le créateur le 18/11/2026)

Toutes les vidéos se montent avec `engine/v3.py` (classe `FullVideo`). Exemples : `video_lucia3` (engine/series.py, série) et `video_notes3` (engine/videos.py, actu).
- Images officielles de `bibliotheque/` en plein cadre (dossiers `personnages/`, `lieus/`, `clips/`), un plan toutes les ~2 s ; cadrer `fx` sur les visages (planche avec repères verticaux pour estimer).
- Actu chiffrée : médias `("card", photo_de_fond, fx, builder)` = carte animée sur photo assombrie. Duel/choix final : `("split", ...)`.
- Coupes « punch » (zoom + flash + son), titres qui claquent, pastilles jaunes d'info, écran partagé pour la question finale.
- Voix dès la 1re image : traiter le MP3 Hedra avec
  `ffmpeg -i voix_<clé>.mp3 -af "silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-35dB:stop_silence=0.22,atempo=1.1" voix_<clé>3.mp3`
  et mettre sa durée dans DUR.
- Accroche de moins de 8 mots, promesse + révélations numérotées, relance vers 50 %, question finale qui pousse aux commentaires.
- Durée : phase de croissance = 45-65 s (la rétention compte plus que le seuil des 60 s tant que la monétisation TikTok n'est pas accessible).
- Puis couverture (étape 5b) : `cover.add_cover(video, covers/cover_<clé>.jpg)`.

## Exigences de qualité (à vérifier avant chaque brouillon)

**Attrayant et viral**
- L'accroche est visible dès la 1re image (titre choc + première carte) et la 1re phrase crée une surprise ou une question.
- Un sujet = une promesse claire ; un chiffre ou un fait étonnant dans les 5 premières secondes.
- Une info par phrase, une carte par info ; pas plus de 6-7 s sans changement visuel.
- Fin sur une question simple qui pousse à commenter, puis « abonne-toi ».
- Titre court avec écart de curiosité (sans mentir), 1-2 emojis, #shorts ; légende avec 6-10 hashtags (dont #GTA6 #GTAVI #VCN).
- Couverture de profil (étape 5b) : l'image 0 de la vidéo est une vraie miniature — photo forte + 2 lignes de titre géant + pastille d'accroche. Jamais un fond vide.

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
- **Analyse de la voix AVANT chaque rendu (obligatoire, `engine/audiocheck.py`)** — je ne peux pas écouter, donc tout est mesuré :
  1. Fin coupée : Hedra (ElevenLabs v3) coupe souvent les derniers mots, même avec « [pause] ». Toujours terminer le texte envoyé à Hedra
     par une phrase sacrifiée séparée par une pause : « … [pause] Voilà, voilà. ». Puis couper le MP3 au début du DERNIER blanc (silencedetect)
     et vérifier que le dernier segment parlé retiré dure moins de 1 s (c'est bien « Voilà, voilà ») et que `tail_db` < -40 dB.
  2. Raccord (régénération d'une fin) : localiser le point de coupe avec `best_match(début_du_nouveau_clip, original)` (similarité > 0,55 =
     même phrase ; ~0,4 = sans rapport), couper l'original dans le blanc juste AVANT cette position, puis revérifier qu'aucune phrase
     n'est répétée (`best_match` < 0,5 sur les 6 s avant le raccord).
  3. Mots avalés : comparer la durée parlée de chaque phrase courte à sa durée attendue (caractères / débit du fichier) ; > 25 % trop court = régénérer.
  4. Envoyer au créateur la fin de la vidéo (10 dernières secondes) à écouter avant validation : il est le seul à pouvoir entendre. Sinon, régénérer seulement la dernière phrase (~2 crédits, avec accord) et la recoller au blanc qui la précède.

## Programme hebdomadaire (décidé par le créateur le 18/11/2026)

- **Dimanche après-midi (tâche « production de la semaine »)** : produire les 7 vidéos du lundi au dimanche suivants, une par jour à 18 h 30 (Europe/Paris).
  Contenu qui reste vrai toute la semaine : épisodes « Qui est… ? » (ordre de reserve.md), explications, astuces, secrets et guides GTA 6.
  Pas d'info qui peut devenir fausse avant sa date de publication.
  Pour chaque vidéo : brouillon vidIQ (3 comptes, publishAt = son jour à 18 h 30), puis écrire `semaine.md` (date, sujet, titre, légende, hashtags, lien brut de la vidéo, postId, revision).
- **Dimanche 20 h 30 (tâche « validation du dimanche »)** : présenter le programme de `semaine.md` au créateur, appliquer ses changements, et ne programmer (vidiq_social_post_publish) qu'après son « ok » explicite dans la session. Un silence n'est jamais un accord.
- **En semaine (tâche quotidienne, mode alerte)** : seulement en cas de grosse actu GTA 6, préparer une vidéo bonus et demander l'accord du créateur ; sinon ne rien faire.

## Clips de gameplay du créateur (à partir de la sortie, 19/11/2026)

- Le créateur joue au mode histoire et envoie 3 à 5 clips par semaine (15-60 s), chacun avec une phrase d'explication.
- Priorité à ces clips pour la série « Secrets de GTA 6 » : détails cachés, easter eggs, astuces, réactions du monde, lieux, comparaisons GTA 5, moments drôles. Histoire : sans spoiler, ou « ⚠️ spoiler » dans le titre.
- Vérifier l'info avant d'écrire le script ; couper la radio du jeu (risque de réclamation de droits) et mettre la musique du moteur ; pas de violence graphique dans les 7 premières secondes (règle YouTube).
- Jamais de clips d'autres créateurs sans leur accord écrit et un crédit.
