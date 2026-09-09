# La Révolution française : La patrie en danger 1791‑1795 — module VASSAL

Conversion en module VASSAL du mod Tabletop Simulator du jeu d'Azure Wish
Enterprise (1995), illustrations Ilya Kudriashov (2021).

Le module est **non automatisé** : il fournit le matériel, le plan de jeu et la
mise en place ; les joueurs appliquent les règles eux‑mêmes.

## Contenu

* **Plan de jeu** 3543 × 2996 : la carte de France d'origine, prolongée en bas
  par six zones joueurs (ordre de l'Assemblée, règles §4.2).
* **31 personnalités**. Les 14 qui peuvent changer de camp (règles §7.3.2)
  portent une face par courant possible — Carnot en Marais et en Montagne,
  Sieyès en Marais, Feuillant et Gironde — que l'on fait défiler par clic droit
  (« Changer de courant », Ctrl+F).
* **Députés de valeur 1, 2, 3, 5 et 10** selon les courants, eux aussi
  transformables d'un courant à l'autre (§7.5.2.1).
* **33 armées** : françaises, vendéennes et coalisées.
* **Marqueurs** de contrôle régional, de révolte et de piste.
* **Trésoreries** : un compteur numérique par camp plus celui du Gouvernement,
  avec +50/+100/+200, −50/−100/−200 et saisie directe du montant.
* **11 aides de jeu PDF** dans le menu Aide.
* **Notes différées** (menu Notes) : chacun peut écrire une promesse secrète,
  visible de tous seulement une fois révélée.
* Boutons de dés 1d6 et 2d6, sélecteur de camp, inventaire.

## Mise en place

Conforme aux règles §4.3 à §4.7 :

| Élément | Règle |
|---|---|
| Marqueurs Économie, Clergé, Coalition, Commune sur la case 4 | §4.3 |
| Renommée : Royaliste 8, Feuillant 12, Marais 10, Gironde 11, Montagne 9, Sans‑Culotte 8, Gouvernement 10 | §4.3 |
| Assemblée : 8 Feuillants, 10 Marais + 2 Royalistes, 4 Girondins + 1 Montagnard + 1 Sans‑Culotte | §4.5 |
| Contrôle régional des six courants, Brest et Nîmes neutres, révolte à Bourges | §4.6 |
| Trésoreries 350 / 350 / 1400 / 800 / 1400 / 400 et Gouvernement 2300 | §4.6 |
| Armées régulières à Lille, Metz, Strasbourg et Marseille | §4.7 |

Les personnalités ne sont pas placées à la mise en place : chaque joueur trouve
les siennes dans sa zone, prêtes pour la phase de placement (§6.5).

## Reconstruire le module

```bash
python3 tools/build_assets.py chemin/module.ttsmod chemin/countersheet_2.pdf
python3 tools/build_module.py
```

Le premier script extrait et met à l'échelle les images et les PDF dans
`assets/` et relève la mise en place ; le second produit le `.vmod` dans
`dist/`. Seul Pillow (et PyMuPDF pour la planche de pions) est nécessaire.

## Organisation

```
tools/vassal_encode.py   encodage des pièces VASSAL (SequenceEncoder et traits)
tools/components.py      catalogue du matériel et données de mise en place
tools/tts_assets.py      index des images du mod TTS
tools/build_assets.py    extraction des images, des PDF et du plan de jeu
tools/build_module.py    génération du buildFile.xml et du .vmod
assets/                  images et PDF prêts à l'emploi, mise en place relevée
dist/                    le module
```

## Note technique

`tools/vassal_encode.py` reproduit fidèlement `VASSAL.tools.SequenceEncoder`.
Le point sensible est l'imbrication des traits : `Decorator.getType()` réencode
la chaîne du trait intérieur, ce qui **échappe** les tabulations qu'elle
contient déjà. Sans cet échappement, VASSAL ne retrouve que les deux premiers
traits d'une pièce et perd son image et son nom. De même, le composant
`BasicCommandEncoder` doit être déclaré en premier dans le `buildFile.xml` :
il est construit après les autres composants, or les piles de mise en place
tentent de décoder leurs pièces pendant leur propre construction — sans
encodeur disponible à ce moment, chaque pièce est définitivement perdue.

Le module a été vérifié en le chargeant réellement dans le moteur VASSAL :
216 pièces décodées sans erreur, 94 images référencées toutes présentes,
110 piles de mise en place toutes dans les limites du plan.

## Droits

Jeu © 1995 Azure Wish Enterprise — illustrations © 2021 Ilya Kudriashov.
Module à usage privé.
