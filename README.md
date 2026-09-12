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
* **Fenêtre « Aides de jeu »** consultable sans quitter VASSAL : Personality
  Actions, Regional Actions, The Laws, Regime Cycles, et une page par courant
  pour les Factions (en anglais).
* **11 aides de jeu PDF** dans le menu Aide, dont les règles complètes et les
  événements aléatoires (FR et EN), qui s'ouvrent dans le lecteur du système.
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

## Version 2 : suivis, non-suppression, notes secrètes, anglais

Corrections et ajouts demandés après relecture du premier module :

- **Bug corrigé — les 2 dés (2d6).** Le message n'affichait que le total
  (« 2d6 = 9 »), donnant l'impression qu'un seul dé avait été lancé alors que
  les deux l'étaient bien. Le format montre maintenant le détail
  (« 2d6 = 4 + 5 = 9 »).
- **Note secrète sur le plateau.** Remplace la fenêtre Notes (retirée) par un
  pion « Secret Note » : `Hideable` (Ctrl+H masque/révèle, visible du seul
  camp qui l'a masqué) + `Labeler` éditable (clic droit « Edit Text »).
  Validé par test direct : masqué après un Ctrl+H, revisible après le second.
- **Pistes tracées sur le plateau, pas de chiffre sur le pion.** Les 4 pistes
  verticales (Coalition, Clergé, Économie, Commune) et la piste de Fame sont
  découpées en zones : 5 `Zone` portant chacune une `RegionGrid` de 20 régions
  nommées « 1 » … « 20 ». La géométrie a été **mesurée sur le plateau** par
  détection des traits de séparation (20 cases de 83,2 px de y=87,5 à
  y=1751,5 pour les colonnes verticales ; 20 cases de 83,25 px de x=1018 à
  x=2683 pour la rangée de Fame ; cases extrêmes recadrées pour vérifier
  qu'elles portent bien « 1 » et « 20 »). Déplacer un marqueur d'une case à
  l'autre écrit donc « Economy: Economy 4 → Economy 6 » dans le journal, sans
  qu'aucun compteur ne s'affiche sur le pion. `snapto` cale le marqueur au
  centre de la case.
  La carte passe à `onlyReportChangedLocation="true"` : hors des pistes le
  plateau n'a pas de grille, la position vaut toujours « Offboard », donc
  déplacer une personnalité ou un député n'encombre pas le journal.
- **Mise en place des marqueurs de piste au centre exact de leur case.**
  Les positions issues du mod TTS étaient approximatives et rejetaient même
  Sans-Culotte et Gouvernement sur une seconde rangée *sous* la piste de
  Fame. Les 11 marqueurs sont maintenant posés par calcul ; les camps qui
  partagent une valeur de départ (Royaliste et Sans-Culotte à 8, Marais et
  Gouvernement à 10) sont réunis dans une **même `SetupStack`**, donc dans
  une vraie pile sur la case.
- **Étiquette « Government »** sur le compteur de trésorerie du
  gouvernement, pour ne pas le confondre avec ceux des six courants.
- **Marqueurs de contrôle transformables.** Les six marqueurs de parti
  portent une couche de six images et un « Change Party » au clic droit.
  Leur propriété `Current` n'est plus figée dans un `Marker`, qui aurait
  menti dès la première transformation : c'est le nom de la pièce, porté par
  le niveau de la couche, qui dit à quel parti elle appartient. Coalition
  Control et Revolt, qui n'appartiennent à aucun parti, restent inchangés.
- **Députés : parti *et* valeur modifiables.** Une pièce ne peut porter
  qu'une seule couche d'image, or il faut ici deux axes. La couche suit donc
  une propriété `Face` (1–24) au lieu de défiler, et deux commandes la
  recalculent par table de correspondance (`components.deputy_next_*_table`) :
  * « Change Value » passe à la valeur suivante **du même parti** ;
  * « Change Party » passe au parti suivant **qui possède cette valeur**.
  Le jeu ne contient que 24 pions de député : les valeurs 2 et 10 n'existent
  que chez Montagne, Gironde et Marais (compté sur les images). Le cycle des
  valeurs d'un député Sans-Culotte, Feuillant ou Royaliste est donc 1‑3‑5, et
  « Change Party » sur un pion de valeur 2 ou 10 ne visite que les trois
  partis qui l'ont.
- **Fenêtre « Events ».** La table des événements aléatoires (9 pages :
  quatre régimes de deux pages, plus les notes du traducteur) a son propre
  bouton, placé avant Charts — l'ordre des boutons est celui des composants
  dans le `buildFile.xml`.
- **La note est désormais visible de tous mais illisible quand masquée.**
  `Hideable` escamotait la pièce entière ; `Obscurable` avec le style
  d'affichage `'G'` montre aux autres joueurs la fiche vierge à la place du
  contenu. Le trait est placé à l'extérieur de l'étiquette, donc c'est bien
  le texte qui disparaît. Une note est posée dans chaque encart de camp, sous
  la trésorerie, et la fiche n'a plus de texte par défaut.
- **Menu contextuel entièrement en anglais.** Les traits Delete et Clone
  portaient encore les libellés français « Supprimer » et « Dupliquer ».
- **Bug corrigé — le journal restait muet.** Tout l'auto-report de VASSAL est
  conditionné par `GlobalOptions.autoReportEnabled()`
  (`PieceMover.java:1177`). Le module déclarait
  `autoReport="Use Preferences Setting"`, ce qui en faisait une case à cocher
  que chaque joueur devait activer lui-même — l'aimantation sur les cases
  fonctionnait, mais aucun déplacement n'était écrit. Passé à `"Always"`
  (la valeur par défaut de VASSAL), donc forcé pour tous les joueurs.
- **Actions journalisées sur les pièces.** Trois `ReportState`, placés en
  dehors des traits qu'ils observent (`ReportState.java:122` : les traits
  intérieurs sont exécutés d'abord « so that their effects will be reported »,
  donc le message porte l'état à jour) :
  * personnalités — « Robespierre is arrested and sent to the Prison du
    Temple », « … is sent to Madame Guillotine », et le changement de courant
    (« Carnot (Montagne) changes current ») ;
  * trésoreries — « Treasury Government now holds 2350 assignats » à chaque
    +/- ou saisie directe.
- **Non-suppression.** Les 11 pièces ci-dessus et les 31 personnalités n'ont
  plus de trait Delete.
- **Menu contextuel des personnalités : Arrest / Guillotine.** Deux
  `SendToLocation` qui envoient la pièce sur les encarts « Prison du Temple »
  (§3.2.3.2) et « Madame Guillotine » (§3.2.3.3) du plateau — validé par test
  direct (la pièce se déplace bien aux coordonnées exactes).
- **Assemblée nationale : députés dissimulés dans la même pile que leur
  hôte**, mais en dessous (donc visuellement séparés) plutôt que dans des
  colonnes séparées — validé sur l'ordre réel des pièces dans le fichier
  généré.
- **Barre d'outils** : Notes retirée, Save Text et Recenter retirés. Ordre
  confirmé dans le XML généré : Side, Pieces, 1d6, 2d6, Inventory, Charts,
  puis le plateau (dont Save Image est l'unique bouton restant) en dernier.
- **Bug corrigé — l'infobulle au survol ne s'affichait jamais.** L'attribut
  `display` du `CounterDetailViewer` n'est pas un booléen : il porte le mode
  de sélection des pièces et doit valoir l'une des cinq chaînes littérales du
  composant (`from top-most layer only`, `from all layers`, …). Avec
  `display="true"`, aucune branche de `selectPiece()` ne correspondait et la
  méthode retombait sur son `return false` final : **toutes** les pièces
  étaient rejetées, l'infobulle n'avait donc jamais rien à dessiner — ni les
  réglages de zoom ni les préférences n'y pouvaient quoi que ce soit.
  Corrigé en `display="from top-most layer only"`, avec `version="4"`
  (`LATEST_VERSION`, sinon `upgrade()` écrase `borderColor` à la première
  ouverture dans l'éditeur), le dessin de la pièce agrandi 2× et son nom
  sous l'image.
- **Interface entièrement en anglais** (boutons, onglets, propriétés,
  entrées de palette, mise en place, menu Help), à l'exception des six noms
  de courants et « assignat », qui sont le vocabulaire du jeu lui-même
  (utilisé tel quel dans les règles anglaises).

## Version 3 : corrections de mise en place, notes vraiment privées

- **Bug corrigé — un marqueur Feuillant en trop à Strasbourg.** Vérifié
  contre les règles (§4.6, liste des régions par courant : « Feuillant :
  Clermont, Dijon, Metz, Montpellier, Orléans, Rouen, Strasbourg et
  Toulouse ») : la région Strasbourg ne doit porter qu'un seul marqueur de
  contrôle. L'extraction du mod TTS en posait deux (confirmé visuellement :
  les deux tombent bien dans le même contour imprimé). Le second est
  écarté, à la fois dans `assets/setup.json` et dans `extract_setup()` (liste
  `KNOWN_DUPLICATES`) pour qu'une future extraction reste corrigée. Un audit
  plus large reste à faire : le décompte total des marqueurs de contrôle par
  courant (36 posés) ne correspond pas à celui des règles (23 régions
  nommées + Brest/Nîmes neutres + Bourges en révolte) ; ce n'est traité ici
  que pour Strasbourg.
- **Assemblée nationale : piles bien séparées, avec un marqueur de parti en
  face.** Les six ancrages (`ASSEMBLY_ANCHORS`) étaient espacés d'à peine
  ~123 px, alors qu'une pile hôte (Marais avec le Royaliste dissimulé, par
  exemple) peut compter jusqu'à 12 pions et déborder sur sa voisine une fois
  dépliée. Réespacés à ~148 px, dans les limites mesurées du cadre de la
  gravure « Assemblée Nationale » (x=120 à 918). Un exemplaire du marqueur
  de contrôle régional du même courant est posé juste au-dessus de chaque
  pile visible (Gironde, Marais, Feuillant), pour l'identifier au premier
  coup d'œil sans avoir à l'ouvrir.
- **Notes des joueurs : vraiment privées, pas seulement « masquables ».**
  Trois manques corrigés :
  * Le texte n'était protégé qu'à moitié : `Obscurable` (accès `side:`)
    n'empêchait que sa propre commande Hide/Reveal, pas le « Edit Text » du
    `Labeler`, un trait indépendant. N'importe quel joueur pouvait donc
    éditer la note d'un autre camp tant qu'elle n'avait pas encore été
    masquée. Ajout du trait `Restricted` (« Accès restreint »), posé à
    l'extérieur de tout le reste et fixé au camp propriétaire : lui seul
    voit désormais la moindre commande sur sa note (vérifié contre
    `VASSAL.counters.Restricted.java` - `getKeyCommands()` renvoie
    `KeyCommand.NONE` pour tout autre camp).
  * La note naissait visible par défaut (état `null`) et n'était masquée
    qu'après un premier Ctrl+H : `Obscurable` prend maintenant directement
    l'état « masquée par son propriétaire » dès la mise en place
    (`masked_by=<parti>`), donc son texte n'est jamais exposé avant que le
    joueur n'écrive quoi que ce soit.
  * Chaque note a maintenant un `ReportState` qui annonce dans le journal
    « <Parti> Note was edited » à chaque Ctrl+E, sans jamais faire fuiter le
    texte lui-même (le format ne cite que `$PieceName$`).
  * Le texte « Secret Note » imprimé sur le pion est retiré ; à la place,
    une étiquette fixe donne le nom du parti propriétaire, dessinée
    par-dessus (même principe que « Government » sur la trésorerie) - donc
    toujours visible de tous, y compris quand le texte est masqué.
  * Validé par un test Java direct (masquage par défaut, commandes
    invisibles avant d'avoir rejoint le bon camp, aucune commande visible
    sur la note d'un autre camp, format du rapport sans fuite).

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
