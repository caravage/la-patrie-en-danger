# La Révolution française : La patrie en danger 1791-1795 — module VASSAL

Conversion du mod Tabletop Simulator (Workshop 2631264736) en module VASSAL.
Jeu © 1995 Azure Wish Enterprise, illustrations © 2021 Ilya Kudriashov. Usage privé.

## État actuel (analyse, pas de module livrable pour l'instant)

Aucun `.vmod` n'est encore généré dans ce dépôt. Ce qui est présent :

- `assets/images/` — pions, plateau et versos extraits du `.ttsmod` source et
  redimensionnés à l'échelle du plateau (92 px pour les pions, 250 px pour
  l'assignat). Extraits via `tools/extract_assets.py`.
- `assets/pdf/` — les 11 aides de jeu (règles, résumés, tableaux de factions/
  lois/régimes, événements aléatoires FR+EN) extraites du `.ttsmod`.
- `tools/components.py` — table de correspondance (index TTS → nom, catégorie,
  tendance) établie par inspection visuelle du contact-sheet des 84 images
  distinctes du mod.
- `tools/tts_assets.py` — index déterministe (index → ugc_id/hash/extension)
  généré une fois depuis le JSON du mod TTS, pour retrouver les fichiers
  `Mods/Images/...` sans avoir à refaire l'inspection.
- `tools/extract_assets.py` — script d'extraction/mise à l'échelle à partir
  d'un fichier `.ttsmod` (non fourni dans ce dépôt).

Une première ébauche de `buildFile.xml`/`.vmod` a été fournie séparément et
analysée en profondeur (chargement réel dans le moteur VASSAL, pas seulement
lecture du XML). Deux bugs bloquants et indépendants y ont été identifiés :

1. Aucun `<VASSAL.build.module.BasicCommandEncoder/>` n'est déclaré → **aucun
   pion ne se décode** (361/361 slots invalides, confirmé par test direct).
2. Même après correction du point 1, l'assemblage des traits empilés
   (Embellishment/Marker/Delete/BasicPiece, joints par tabulations) n'échappe
   pas correctement les délimiteurs imbriqués comme le fait le vrai
   `SequenceEncoder` de VASSAL : tout pion à 2 traits ou plus (119 pièces) ou
   3 traits ou plus (62 pièces, dont les 31 personnalités recto/verso) perd
   son image et son nom réels lors du décodage — confirmé par test direct
   après ajout de l'encodeur manquant.

Conclusion : l'architecture (plateau, palette, mise en place, aides de jeu,
dés) est réutilisable, mais la fonction de sérialisation des pièces doit être
réécrite avec les règles d'échappement réelles de VASSAL avant qu'un module
jouable puisse être produit.

Le fichier `.ttsmod` source n'est pas versionné ici (fourni hors dépôt).
