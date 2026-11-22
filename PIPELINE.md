# Pipeline quotidien VCN (1 vidéo/jour)

1. **Veille** : recherche web + vidIQ (tendances GTA 6). Éviter les sujets déjà listés dans `sujets.md`.
2. **Vérification** : chaque chiffre recoupé sur 2 sources ; mention « non confirmé » si Rockstar n'a pas confirmé.
3. **Script** : 250-280 mots en français (la voix est accélérée de 10 % et ses blancs retirés au montage v3, soit ~85 % de sa durée brute : il faut ≥ 84 s de voix brute pour ≥ 72 s de vidéo), accroche en 1 phrase, une info par phrase, question finale + « abonne-toi ».
   **DURÉE MINIMALE : 1 min 10 s (70 s) de vidéo finale, exigée par le créateur pour la monétisation** — viser 72-80 s. Si la voix traitée est trop courte, ajouter du contenu (phrase supplémentaire régénérée), jamais du silence ni un écran figé.
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
   **Limite vidIQ (plan gratuit) : 3 envois YouTube par jour** (remise à zéro à minuit heure du Pacifique = 9 h Paris). Au-delà, publier TikTok + Instagram (publicationIds) et envoyer le YouTube par lots de 3 les jours suivants, avant leur créneau. vidIQ affiche l'heure YouTube à null dans draft_get/list, mais YouTube la respecte (vérifier avec vidiq_user_videos : private + scheduledPublishAt).
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
- Durée : au moins 70 s, viser 72-80 s (décision du créateur, monétisation).
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
- Durée finale ≥ 70 s (1 min 10), viser 72-80 s — contrôle BLOQUANT.
- Script original avec un angle et une explication (pas une simple lecture d'article) — règle YouTube contre le contenu « inauthentique ».
- Varier d'une vidéo à l'autre : thème de fond (`theme` = night / sunset / day), couleurs des titres, types de cartes, structure (liste, duel, explication, chronologie).
- Aucun extrait, image, logo ni musique de Rockstar ou de tiers ; musique générée par le moteur uniquement.
- Faits vérifiés sur 2 sources, « non confirmé » quand c'est le cas ; aucune info qui deviendra fausse avant l'heure de publication.
- Mention « contenu IA » activée (TikTok isAiGenerated).

**Contrôle technique**
- Regarder une planche d'images (1 toutes les 4 s) : chaque carte correspond à la phrase dite.
- Synchro : > 95 % des mots affichés pendant que la voix parle.
- Volume : voix nettement au-dessus de la musique (moyenne autour de -16 dB).
- **Narration complète dans la vidéo finale (obligatoire)** : `audiocheck.voice_cut_in_video(video, voix, lead)` doit renvoyer None.
  Cause trouvée le 18/11 : l'ancien mixage (loudnorm sans apad) coupait les ~3 dernières secondes de voix de TOUTES les vidéos
  (A, B, C, D publiées avec la fin coupée). Corrigé dans finish.mix (apad avant loudnorm, sortie à la durée de la vidéo).
- **Analyse de la voix AVANT chaque rendu (obligatoire, `engine/audiocheck.py`)** — je ne peux pas écouter, donc tout est mesuré :
  1. Fin coupée : Hedra (ElevenLabs v3) coupe souvent les derniers mots, même avec « [pause] ». Toujours terminer le texte envoyé à Hedra
     par une phrase sacrifiée séparée par une pause : « … [pause] Allez, ciao. » (choix du créateur).
     La phrase sacrifiée est coupée au montage et ne doit JAMAIS s'entendre dans la vidéo. Puis couper le MP3 au début du DERNIER blanc (silencedetect)
     et vérifier que le dernier segment parlé retiré dure moins de 1 s (c'est bien « Allez, ciao ») et que `tail_db` < -40 dB.
  2. Raccord (régénération d'une fin) : localiser le point de coupe avec `best_match(début_du_nouveau_clip, original)` (similarité > 0,55 =
     même phrase ; ~0,4 = sans rapport), couper l'original dans le blanc juste AVANT cette position, puis revérifier qu'aucune phrase
     n'est répétée (`best_match` < 0,5 sur les 6 s avant le raccord).
  3. Mots avalés : comparer la durée parlée de chaque phrase courte à sa durée attendue (caractères / débit du fichier) ; > 25 % trop court = régénérer.
  4. Envoyer au créateur la fin de la vidéo (10 dernières secondes) à écouter avant validation : il est le seul à pouvoir entendre. Sinon, régénérer seulement la dernière phrase (~2 crédits, avec accord) et la recoller au blanc qui la précède.

## Programme (décidé par le créateur le 18/11/2026, 2 vidéos par jour à partir du 19/11)

- **Cadence : 2 vidéos par jour, à 12 h 30 et 18 h 30 (Europe/Paris)**, sur les 3 comptes.
- **Priorité absolue du créateur : des vidéos très attrayantes et virales, sans aucune coupure de son ni de narration.**
  On ne réduit JAMAIS la qualité pour économiser des crédits : toujours une voix off complète, durée ≥ 70 s (viser 72-80 s), format v3.
- **Dimanche 14 h 12 (tâche « production de la semaine »)** : produire les 14 vidéos du lundi au dimanche suivants (12 h 30 et 18 h 30).
  Contenu qui reste vrai toute la semaine : épisodes « Qui est… ? » (ordre de reserve.md), explications, astuces, secrets, guides, et les clips de gameplay du créateur.
  Pas d'info qui peut devenir fausse avant sa date de publication. Budget : ~23 crédits Hedra par vidéo (~320/semaine) ; prévenir le créateur si le solde passe sous 300.
  Pour chaque vidéo : brouillon vidIQ (3 comptes, publishAt = son créneau), puis écrire `semaine.md` (date, heure, sujet, titre, légende, hashtags, lien brut, postId, revision, contrôles audio).
- **Dimanche 20 h 30 (tâche « validation du dimanche »)** : présenter `semaine.md` au créateur avec les vidéos ET les 10 dernières secondes de chacune à écouter, appliquer ses changements,
  et ne programmer (vidiq_social_post_publish) qu'après son « ok » explicite dans la session. Un silence n'est jamais un accord.
- **Tâche quotidienne (13 h 47)** : jusqu'au samedi 21/11 inclus, préparer les 2 vidéos du LENDEMAIN (12 h 30 et 18 h 30, sauf créneau déjà pris).
  À partir du dimanche 22/11 : mode alerte — seulement en cas de grosse actu GTA 6, une vidéo bonus à 15 h 30 le lendemain, avec l'accord du créateur ; sinon ne rien faire.
- **Contrôles bloquants avant tout brouillon** (sinon on corrige, on n'envoie pas) : `audiocheck.voice_cut_in_video(...)` = None (narration entière),
  aucune phrase répétée, aucune phrase sacrifiée audible, fin de voix sur un silence, synchro > 95 %, volume ≈ -16 dB, durée ≥ 70 s.

## Mélange de contenus (validé par le créateur le 18/11/2026)

- 4 types en alternance : **actus**, **secrets & astuces**, **portraits « Qui est… ? »**, **lieux** (dossier `bibliotheque/lieus/` : Vice City jour/nuit, Leonida Keys, Grassrivers, Port Gellhorn, Mount Kalaga, Ambrosia).
- Semaine type de 14 : ~4 portraits, ~4 lieux, ~3 actus, ~3 secrets ; jamais deux du même type à la suite ; les plus fortes à 18 h 30 ; une grosse actu passe devant tout.
- Même direction artistique pour tout (format v3, couvertures : visage pour un perso, carte postale pour un lieu/une actu). Toujours viral, attrayant, une image qui donne envie de cliquer.
- Vidéo de lieu : angle « X choses à faire / à voir » ou « le secret de… », un plan par photo de la zone, pastilles d'info, question finale (« tu iras où en premier ? »).

## Secrets & astuces : sources

- On récupère les **informations** (pas les vidéos) : chaînes YouTube GTA (vidiq_youtube_search, vidiq_video_transcript à 5 crédits — budget vidIQ 150/mois), Rockstar Newswire et support officiel, guides presse (jeuxvideo.com, Millenium, IGN), Reddit r/GTA6.
- Chaque secret est vérifié sur au moins 2 sources (ou montré dans un clip du créateur), et la découverte est créditée dans la légende (« Découverte : @chaîne »).
- On refait la vidéo entièrement avec notre direction artistique : images officielles, clips du créateur, cartes, voix VCN.
- **Jamais** d'images, d'extraits ni de miniatures d'autres créateurs, même modifiés : réclamations de droits, contenu « réutilisé » non monétisable sur YouTube, risque d'avertissement.

## Clips de gameplay du créateur (à partir de la sortie, 19/11/2026)

- Le créateur joue au mode histoire et envoie 3 à 5 clips par semaine (15-60 s), chacun avec une phrase d'explication.
- Priorité à ces clips pour la série « Secrets de GTA 6 » : détails cachés, easter eggs, astuces, réactions du monde, lieux, comparaisons GTA 5, moments drôles. Histoire : sans spoiler, ou « ⚠️ spoiler » dans le titre.
- Vérifier l'info avant d'écrire le script ; couper la radio du jeu (risque de réclamation de droits) et mettre la musique du moteur ; pas de violence graphique dans les 7 premières secondes (règle YouTube).
- Jamais de clips d'autres créateurs sans leur accord écrit et un crédit.

## Série « mission par mission » (décision du créateur le 22/11/2026 : plus tard)

- Le créateur termine d'abord le jeu, puis enregistrera lui-même le mode histoire mission par mission (nouvelle partie dans un autre emplacement de sauvegarde, 15 emplacements manuels ; GTA 6 n'a pas de « Rejouer la mission »).
- Titre = « Mission N : <nom de la mission> », dans l'ordre de l'histoire, format v3 + voix VCN, radio du jeu coupée, sans spoiler (pas de fin, pas de montage de cinématiques : Rockstar les fait retirer).
- Jamais d'extraits de gameplay d'autres youtubeurs, même connus ou crédités, sans leur accord écrit.
- En attendant, on garde le mélange habituel (portraits, lieux, secrets & astuces, explications).
