# -*- coding: utf-8 -*-
"""Catalogue des composants du jeu.

Etabli a partir du module Tabletop Simulator (Workshop 2631264736) et verifie
contre les regles anglaises (rules_en.pdf) : §3.1 (pions), §4.2 a §4.7 (mise en
place), §7.3.2 (changement de courant).

Les index renvoient a tools/tts_assets.py (TTS_IMAGES).

Convention de langue : l'interface VASSAL (boutons, onglets, menus, noms de
pieces) est en anglais. Les six noms de courants et « assignat » restent tels
que les regles anglaises elles-memes les utilisent (ex. §2.3 « Marais »,
§2.5 « Montagne (Mountain) ») : ce sont des termes du jeu, pas des elements
d'interface a traduire.
"""

# Ordre de placement a table, de gauche a droite (regles §4.2)
CURRENTS = ['Sans-Culotte', 'Montagne', 'Gironde', 'Marais', 'Feuillant', 'Royaliste']

# Couleur de fond du pion pour chaque courant (utile pour les libelles)
CURRENT_SLUG = {
    'Feuillant': 'feuillant', 'Gironde': 'gironde', 'Montagne': 'montagne',
    'Sans-Culotte': 'sansculotte', 'Marais': 'marais', 'Royaliste': 'royaliste',
}

# --- Personnalites ----------------------------------------------------------
# (fichier, libelle, courant de depart, index image de depart,
#  [(autre courant, (ugc_id, hash)) ...])
#
# Les personnalites « bi-camp » possedent une face par courant possible : le
# pion est retourne quand elles changent de camp (§7.3.2). Ces faces existent
# dans le cache du mod TTS mais n'etaient posees sur aucun objet.

ALT = {
    ('barere', 'Montagne'):          ('1687147350559832734', '1A2AA03592F7443A98EA47FCD49A6A583E16BCCB'),
    ('barras', 'Montagne'):          ('1687147350559838319', '4350B7E6E32DE185B5197425FECA81001860F86B'),
    ('billaud_varenne', 'Montagne'): ('1687147350559841326', '02D39F8BFBA2896C8B1544C9BDD7F130473CD510'),
    ('boissy_danglas', 'Gironde'):   ('1687147350559846111', '1A4206241F727DCF8FA0C3E865EF32FADBCB42F8'),
    ('carnot', 'Montagne'):          ('1687147350559855141', 'FBACA176D18C69BB50AB8DA3C67A46AE7B73B962'),
    ('collot_dherbois', 'Montagne'): ('1687147350559866864', '7334C4FF4C396B459F7628C8A734CCACBB8AD3FB'),
    ('dandre', 'Royaliste'):         ('1687147350559869217', 'D5FCD17DBD480C45853B206C50B01BF0FBA9ADB3'),
    ('danton', 'Marais'):            ('1687147350559871321', '90585F8A3D586A34E1C7E63E618D5448B91F60E4'),
    ('desmoulins', 'Marais'):        ('1687147350559875188', '7CFD9CD6E699F3AB6DB05DA46E627548FB0035CE'),
    ('laclos', 'Gironde'):           ('1687147350559879514', 'BD6D3D4BDEFA807D355DFB66C6BC15324DBA6623'),
    ('louis_xvi', 'Royaliste'):      ('1687147350559884151', '40C0A7620C175D1959E3674937D1629B877C699C'),
    ('marat', 'Sans-Culotte'):       ('1687147350559886261', 'A8714101CDF6AEB793CEF02862DFBFED44FC973D'),
    ('petion', 'Montagne'):          ('1687147350559888846', '36DF623A3D8E40051ADD81896645B4B399563A28'),
    ('sieyes', 'Feuillant'):         ('1687147350559926442', '78FAAD5B2869CB510659407D6957C32DE80921FF'),
    ('sieyes', 'Gironde'):           ('1687147350559928326', '63A89CBF2AE13215DA81087F388BE71A2E5416BC'),
}

PERSONALITIES = [
    # Sans-Culotte
    ('roux',            'Roux',             'Sans-Culotte', 44, []),
    ('chaumette',       'Chaumette',        'Sans-Culotte', 35, []),
    ('hebert',          'Hebert',           'Sans-Culotte', 39, []),
    ('billaud_varenne', 'Billaud-Varenne',  'Sans-Culotte', 15, ['Montagne']),
    ('collot_dherbois', "Collot d'Herbois", 'Sans-Culotte', 18, ['Montagne']),
    # Montagne
    ('robespierre',     'Robespierre',      'Montagne', 45, []),
    ('saint_just',      'Saint-Just',       'Montagne', 46, []),
    ('marat',           'Marat',            'Montagne', 24, ['Sans-Culotte']),
    ('danton',          'Danton',           'Montagne', 20, ['Marais']),
    ('desmoulins',      'Desmoulins',       'Montagne', 21, ['Marais']),
    # Gironde
    ('brissot',         'Brissot',          'Gironde', 32, []),
    ('barbaroux',       'Barbaroux',        'Gironde', 31, []),
    ('roland',          'Roland',           'Gironde', 42, []),
    ('vergniaud',       'Vergniaud',        'Gironde', 43, []),
    ('petion',          'Petion',           'Gironde', 25, ['Montagne']),
    # Marais
    ('barere',          'Barere',           'Marais', 13, ['Montagne']),
    ('carnot',          'Carnot',           'Marais', 17, ['Montagne']),
    ('barras',          'Barras',           'Marais', 14, ['Montagne']),
    ('sieyes',          'Sieyes',           'Marais', 27, ['Feuillant', 'Gironde']),
    ('boissy_danglas',  "Boissy d'Anglas",  'Marais', 16, ['Gironde']),
    # Feuillant
    ('louis_xvi',       'Louis XVI',        'Feuillant', 23, ['Royaliste']),
    ('barnave',         'Barnave',          'Feuillant', 30, []),
    ('lafayette',       'La Fayette',       'Feuillant', 40, []),
    ('lameth',          'Lameth',           'Feuillant', 41, []),
    ('laclos',          'Laclos',           'Feuillant', 22, ['Gironde']),
    ('dandre',          "d'Andre",          'Feuillant', 19, ['Royaliste']),
    # Royaliste
    ('dantraigues',     "d'Antraigues",     'Royaliste', 38, []),
    ('cathelineau',     'Cathelineau',      'Royaliste', 34, []),
    ('cadoudal',        'Cadoudal',         'Royaliste', 33, []),
    ('chouan',          'Chouan',           'Royaliste', 37, []),
    ('charette',        'Charette',         'Royaliste', 36, []),
]

# Destinations sur le plateau pour les commandes "Arrest" / "Guillotine" du
# menu contextuel des personnalites (cf. §3.2.3.2 et §3.2.3.3), reperees sur
# les encarts illustres du plateau.
PRISON_XY = (3160, 1382)     # encart "Prison du Temple"
GUILLOTINE_XY = (3160, 1856)  # encart "Madame Guillotine"

# --- Autres pions : (fichier, libelle, categorie, courant, index) -----------
PIECES = [
    # Marqueurs de controle regional : fournis en nombre illimite
    ('marqueur_feuillant',    'Feuillant Control',    'controle', 'Feuillant',    2),
    ('marqueur_gironde',      'Gironde Control',      'controle', 'Gironde',      5),
    ('marqueur_montagne',     'Montagne Control',     'controle', 'Montagne',     8),
    ('marqueur_sansculotte',  'Sans-Culotte Control', 'controle', 'Sans-Culotte', 9),
    ('marqueur_marais',       'Marais Control',       'controle', 'Marais',       3),
    ('marqueur_royaliste',    'Royaliste Control',    'controle', 'Royaliste',    4),
    ('coalition_controle',    'Coalition Control',    'controle', None,          47),
    ('revolte',               'Revolt',               'controle', None,          28),

    # Armees francaises
    ('armee_francaise',       'Army (Volunteers)',      'armee', None, 1),
    ('armee_lille',           'Lille Army',             'armee', None, 64),
    ('armee_metz',            'Metz Army',              'armee', None, 62),
    ('armee_strasbourg',      'Strasbourg Army',        'armee', None, 61),
    ('armee_marseille',       'Marseille Army',         'armee', None, 63),
    ('commune',               'Commune of Paris (Army)', 'armee', None, 76),
    # Armees vendeennes
    ('armee_du_centre',       'Army of the Centre',           'armee', None, 71),
    ('armee_catholique',      'Catholic and Royal Army',      'armee', None, 72),
    ('armee_pays_de_retz',    'Army of Pays de Retz',         'armee', None, 73),
    # Coalition
    ('brunswick',             'Brunswick (Prussians)',  'armee', None, 68),
    ('cobourg',               'Cobourg (Austrians)',    'armee', None, 69),
    ('wurmser',               'Wurmser (Austrians)',    'armee', None, 74),
    ('york',                  'York (English)',         'armee', None, 75),
    ('flotte_anglaise',       'The Fleet (English)',    'armee', None, 12),
    ('armee_espagnole_1',     'Spanish Army 1',         'armee', None, 66),
    ('armee_espagnole_2',     'Spanish Army 2',         'armee', None, 67),
    ('armee_sarde',           'Sardinian Army',         'armee', None, 65),
    ('quiberon',              'Quiberon (Emigrants)',   'armee', None, 70),

    # Marqueurs de piste (4 pistes verticales + Political Regime + Turn Order
    # + Elections). Les 4 pistes ci-dessous et les 7 marqueurs de Fame (plus
    # bas) sont non supprimables et suivis par compteur : voir TRACKED.
    ('tour',                  'Turn Order Marker',  'piste', None, 48),
    ('economie',              'Economy',             'piste', None, 50),
    ('clerge',                'Dissident Clergy',    'piste', None, 51),
    ('coalition_piste',       'Coalition',           'piste', None, 52),
    ('commune_piste',         'Commune of Paris (Track)', 'piste', None, 49),
    ('regime_politique',      'Political Regime',   'piste', None, 53),
    ('elections',             'Elections',           'piste', None, 83),
    ('renommee_gouvernement', 'Fame - Government',      'piste', None,          54),
    ('renommee_feuillant',    'Fame - Feuillant',       'piste', 'Feuillant',    59),
    ('renommee_gironde',      'Fame - Gironde',         'piste', 'Gironde',      57),
    ('renommee_montagne',     'Fame - Montagne',        'piste', 'Montagne',     58),
    ('renommee_sansculotte',  'Fame - Sans-Culotte',    'piste', 'Sans-Culotte', 60),
    ('renommee_marais',       'Fame - Marais',          'piste', 'Marais',       56),
    ('renommee_royaliste',    'Fame - Royaliste',       'piste', 'Royaliste',    55),

    # Argent
    ('assignat_50',           'Assignat (50 Livres)', 'assignat', None, 0),
]

# Pieces suivies par compteur numerique (+/- avec report dans le journal) et
# non supprimables : les 4 pistes verticales de gauche et les 7 marqueurs de
# Fame. Echelle 1-20 pour toutes (regles §3.2.2 : "the markers simply remain
# at these limit points").
TRACKED_PIECES = [
    'economie', 'clerge', 'coalition_piste', 'commune_piste',
    'renommee_gouvernement', 'renommee_feuillant', 'renommee_gironde',
    'renommee_montagne', 'renommee_sansculotte', 'renommee_marais',
    'renommee_royaliste',
]
TRACK_MIN, TRACK_MAX = 1, 20

# Valeur de depart de chaque piece suivie (regles §4.3 et §4.3 fame values)
TRACK_START = {
    'economie': 4, 'clerge': 4, 'coalition_piste': 4, 'commune_piste': 4,
    'renommee_gouvernement': 10, 'renommee_feuillant': 12,
    'renommee_gironde': 11, 'renommee_montagne': 9,
    'renommee_sansculotte': 8, 'renommee_marais': 10,
    'renommee_royaliste': 8,
}

# --- Geometrie des pistes imprimees sur le plateau --------------------------
# Mesuree directement sur assets/images/plan_de_jeu.jpg en detectant les
# traits de separation des cases (balayage des pixels sombres) :
#   * les 4 pistes verticales de gauche : 21 traits horizontaux de y=87.5 a
#     y=1751.5, soit 20 cases de 83.2 px ; les colonnes utiles sont bornees
#     par les traits verticaux x = 116 / 199.5 / 283.5 / 366 / 450 / 533 /
#     617 / 700 (les colonnes intercalaires portent le titre vertical).
#   * la piste de Fame : une seule rangee y = 2283.5..2367, 21 traits
#     verticaux de x=1018 a x=2683, soit 20 cases de 83.25 px.
# La case 1 est en haut (pistes verticales) / a gauche (Fame), verifie en
# recadrant les cases extremes : elles portent bien "1" et "20".
TRACK_ROW_TOP = 87.5          # bord superieur de la case 1 des pistes
TRACK_ROW_PITCH = 83.2        # hauteur d'une case
TRACK_COLUMNS = {             # piece -> (x gauche, x droite) de sa colonne
    'coalition_piste': (116.0, 199.5),
    'clerge':          (283.5, 366.0),
    'economie':        (450.0, 533.0),
    'commune_piste':   (617.0, 700.0),
}
FAME_COL_LEFT = 1018.0        # bord gauche de la case 1 de la piste de Fame
FAME_COL_PITCH = 83.25        # largeur d'une case
FAME_ROW = (2283.5, 2367.0)   # bords haut / bas de la rangee
FAME_PIECES = [
    'renommee_gouvernement', 'renommee_feuillant', 'renommee_gironde',
    'renommee_montagne', 'renommee_sansculotte', 'renommee_marais',
    'renommee_royaliste',
]
# Marge ajoutee autour d'une piste pour dessiner sa zone : un pion fait 92 px
# de cote pour une case de 83, il deborde donc un peu ; la marge evite qu'un
# pion pose legerement de travers tombe hors de la zone. Les colonnes sont
# separees de 84 px, une marge de 20 px ne les fait pas se recouvrir.
TRACK_ZONE_MARGIN = 20

# Libelles anglais des zones ; ils apparaissent dans le journal, sous la forme
# « <zone> <case> », p.ex. « Economy 6 ».
TRACK_ZONE_NAMES = {
    'coalition_piste': 'Coalition Armies',
    'clerge': 'Dissident Clergy',
    'economie': 'Economy',
    'commune_piste': 'Commune of Paris',
}
FAME_ZONE_NAME = 'Fame'


# --- Faces de depute --------------------------------------------------------
# Le jeu ne contient pas toutes les combinaisons : seuls Montagne, Gironde et
# Marais disposent des pions 2 et 10 ; Sans-Culotte, Feuillant et Royaliste
# n'ont que 1, 3 et 5. Cela fait 24 pions distincts, et autant d'images (le
# compte a ete verifie sur assets/images/). Un depute est donc une piece a 24
# faces, numerotees dans cet ordre : courant par courant, valeurs croissantes.

def deputy_faces():
    """[(courant, valeur)] dans l'ordre des faces, indexees a partir de 1."""
    return [(c, v) for c in CURRENTS for v in deputy_values(c)]


def deputy_face_index(current, value):
    return deputy_faces().index((current, value)) + 1


def _next_in_cycle(items, current):
    """Element suivant dans une liste circulaire."""
    return items[(items.index(current) + 1) % len(items)]


def deputy_next_value_table():
    """face -> face du meme courant, valeur suivante (cyclique)."""
    faces = deputy_faces()
    out = {}
    for i, (c, v) in enumerate(faces, 1):
        vals = deputy_values(c)
        out[i] = deputy_face_index(c, _next_in_cycle(vals, v))
    return out


def deputy_next_current_table():
    """face -> face de valeur identique, courant suivant qui possede cette
    valeur. Pour les valeurs 2 et 10, le cycle ne visite donc que Montagne,
    Gironde et Marais : ce sont les seuls a avoir ces pions."""
    faces = deputy_faces()
    out = {}
    for i, (c, v) in enumerate(faces, 1):
        owners = [x for x in CURRENTS if v in deputy_values(x)]
        out[i] = deputy_face_index(_next_in_cycle(owners, c), v)
    return out


def lookup_expression(prop, table):
    """Chaine de ternaires BeanShell « {p==1?4:p==2?5:...:1} ».

    Elle est logee dans le champ propertyName de la couche, ou dans la valeur
    d'un PropertySetter. Les deux sont des FormattedString, qui acceptent une
    expression BeanShell entre accolades (FormattedString.java:48)."""
    items = sorted(table)
    body = ''.join('%s==%d?%d:' % (prop, k, table[k]) for k in items[:-1])
    return '{' + body + str(table[items[-1]]) + '}'


def track_cell(base, value):
    """Centre en pixels de la case `value` (1-20) de la piste de `base`."""
    if base in TRACK_COLUMNS:
        x0, x1 = TRACK_COLUMNS[base]
        return (int(round((x0 + x1) / 2.0)),
                int(round(TRACK_ROW_TOP + (value - 0.5) * TRACK_ROW_PITCH)))
    y0, y1 = FAME_ROW
    return (int(round(FAME_COL_LEFT + (value - 0.5) * FAME_COL_PITCH)),
            int(round((y0 + y1) / 2.0)))


def track_zone_polygon(base):
    """Rectangle englobant la piste, marge comprise : « x,y;x,y;... »."""
    m = TRACK_ZONE_MARGIN
    if base in TRACK_COLUMNS:
        x0, x1 = TRACK_COLUMNS[base]
        y0, y1 = TRACK_ROW_TOP, TRACK_ROW_TOP + TRACK_MAX * TRACK_ROW_PITCH
    else:
        x0 = FAME_COL_LEFT
        x1 = FAME_COL_LEFT + TRACK_MAX * FAME_COL_PITCH
        y0, y1 = FAME_ROW
    pts = [(x0 - m, y0 - m), (x1 + m, y0 - m), (x1 + m, y1 + m), (x0 - m, y1 + m)]
    return ';'.join('%d,%d' % (int(round(x)), int(round(y))) for x, y in pts)

# Traduction des categories internes (filtrage des panneaux, cf. PIECES
# ci-dessus) vers la valeur anglaise embarquee dans la propriete "Category"
# des pions - celle que l'Inventaire affiche pour regrouper.
CATEGORY_LABEL = {
    'armee': 'Army', 'controle': 'Control', 'piste': 'Track',
    'assignat': 'Treasury', 'depute': 'Deputy',
}

# Symboles de courant (utilises pour habiller les zones joueurs)
SYMBOLS = {
    'Feuillant': 2, 'Marais': 3, 'Royaliste': 4, 'Gironde': 5,
    'Montagne': 8, 'Sans-Culotte': 9,
}

# --- Deputes de valeur -------------------------------------------------------
# Les pions « 1 » viennent du mod TTS ; les valeurs 2, 3, 5 et 10 sont
# decoupees dans la planche countersheet_2.pdf (vectorielle).
# Toutes les valeurs n'existent pas pour tous les courants.
DEPUTY_TTS = {'Feuillant': 81, 'Gironde': 79, 'Montagne': 80,
              'Sans-Culotte': 82, 'Marais': 78, 'Royaliste': 77}

DEPUTY_SHEET = {
    ('Montagne', 2):    'p2_c14_r3', ('Montagne', 3):    'p2_c14_r4',
    ('Montagne', 5):    'p2_c14_r5', ('Montagne', 10):   'p2_c15_r2',
    ('Gironde', 2):     'p2_c02_r0', ('Gironde', 3):     'p2_c04_r0',
    ('Gironde', 5):     'p2_c06_r1', ('Gironde', 10):    'p2_c06_r0',
    ('Marais', 2):      'p2_c04_r4', ('Marais', 3):      'p2_c05_r4',
    ('Marais', 5):      'p2_c06_r4', ('Marais', 10):     'p2_c07_r5',
    ('Feuillant', 3):   'p2_c03_r8', ('Feuillant', 5):   'p2_c03_r9',
    ('Sans-Culotte', 3):'p2_c04_r8', ('Sans-Culotte', 5):'p2_c04_r9',
    ('Royaliste', 3):   'p2_c05_r8', ('Royaliste', 5):   'p2_c05_r9',
}


def deputy_values(current):
    """Valeurs de depute disponibles pour un courant, croissantes."""
    vals = [1] + sorted(v for (c, v) in DEPUTY_SHEET if c == current)
    return vals


# --- Mise en place de l'Assemblee nationale (regles §4.5) -------------------
# Aile droite : 8 Feuillants. Centre : 10 Marais + 2 Royalistes (dissimules).
# Aile gauche : 4 Girondins + 1 Montagnard + 1 Sans-Culotte (dissimules).
# On decompose chaque total en pions de valeur disponibles.
ASSEMBLY = {
    'Sans-Culotte': 1,
    'Montagne':     1,
    'Gironde':      4,
    'Marais':      10,
    'Feuillant':    8,
    'Royaliste':    2,
}

# Rattachement des courants non officiellement presents a la pile hote dans
# laquelle ils sont dissimules (§4.5 : "their deputies are therefore 'hidden'
# among another Current's deputies"). Ils sont places dans la meme pile,
# en dessous, pour que la separation reste visible a la mise en place tout en
# respectant la composition reelle des regles.
ASSEMBLY_HOST = {
    'Royaliste': 'Marais',
    'Montagne': 'Gironde',
    'Sans-Culotte': 'Gironde',
}

# Ancrages des six colonnes de l'Assemblee, en pixels du plateau. Espaces de
# ~148 px (au lieu des ~123 px releves sur la mise en place du mod TTS) : une
# pile hote peut recevoir jusqu'a 12 pions une fois les courants dissimules
# ajoutes (Marais 10 + Royaliste 2), et se deployait par-dessus sa voisine
# avec l'espacement d'origine (StackMetrics exSepX=14, jusqu'a 168 px).
# Bornes x=150..890 : cadre de la gravure « Assemblee Nationale » mesure a
# x=120..918 (detection des traits sombres du cadre), marge de 30 px pour ne
# pas empieter dessus.
ASSEMBLY_ANCHORS = {
    'Sans-Culotte': (150, 2185), 'Montagne': (298, 2185),
    'Gironde': (446, 2185), 'Marais': (594, 2185),
    'Feuillant': (742, 2185), 'Royaliste': (890, 2185),
}

# --- Tresorerie de depart (regles §4.6), en livres --------------------------
TREASURY = {
    'Sans-Culotte': 350, 'Montagne': 350, 'Gironde': 1400,
    'Marais': 800, 'Feuillant': 1400, 'Royaliste': 400,
}
TREASURY_GOVERNMENT = 2300

# --- Aides de jeu -----------------------------------------------------------
# (fragment de hash du fichier TTS, nom de fichier, titre affiche dans le menu
# Help - en anglais ; "(FR)"/"(EN)" indique la langue du contenu du PDF.)
PDFS = [
    ('DA9849', 'regles_completes_en',       'Complete Rules (EN)'),
    ('BFB24F', 'resume_regles_en',          'Rules Summary (EN)'),
    ('E6D3C8', 'actions_en',                'Actions Chart (EN)'),
    ('0909A9', 'lois_en',                   'Laws Chart (EN)'),
    ('FC0ED9', 'tendances_en',              'Factions & Victory Conditions (EN)'),
    ('F565F2', 'cycles_regimes_en',         'Regime Cycles (EN)'),
    ('351FAF', 'regimes_fr',                'Regime Chart (FR)'),
    ('615ED8', 'cycles_regimes_fr',         'Regime Cycle (FR)'),
    ('EA7731', 'cycles_regimes_ouverts_fr', 'Regime Cycle - Open Version (FR)'),
    ('C8F881', 'evenements_aleatoires_fr',  'Random Events (FR)'),
    ('3D915F', 'evenements_aleatoires_en',  'Random Events (EN)'),
]

# --- Aides de jeu consultables dans VASSAL ----------------------------------
# Onglets de la fenetre « Charts ». Uniquement les tableaux courts, en
# anglais ; les regles completes et les evenements restent en PDF (menu Help).
# (fichier PDF source, titre de l'onglet, [(page, titre du sous-onglet), ...])
CHARTS = [
    ('actions_en', 'Actions', [(1, 'Personality Actions'), (2, 'Regional Actions')]),
    ('lois_en', 'The Laws', [(1, None)]),
    ('cycles_regimes_en', 'Regime Cycles', [(1, None)]),
    ('tendances_en', 'Factions', [(1, 'Royalist'), (2, 'Feuillant'), (3, 'Marais'),
                                  (4, 'Gironde'), (5, 'Montagnard'), (6, 'Sans-Culottes')]),
]

# La table des evenements aleatoires, dans sa propre fenetre (bouton place
# avant celui des Charts). Le document en compte 9 pages : quatre regimes de
# deux pages chacun, plus les notes du traducteur. Les rubriques de chaque
# page ont ete relevees dans le PDF (ECONOMY / POLITICS d'un cote,
# COUNTER-REVOLUTION / PARIS COMMUNE de l'autre).
EVENTS_SRC = 'evenements_aleatoires_en'
EVENTS = [
    (EVENTS_SRC, 'Legislative',        [(1, 'Economy & Politics'),
                                        (2, 'Counter-Revolution & Commune')]),
    (EVENTS_SRC, 'Convention',         [(3, 'Economy & Politics'),
                                        (4, 'Counter-Revolution & Commune')]),
    (EVENTS_SRC, 'Terror',             [(5, 'Economy & Politics'),
                                        (6, 'Counter-Revolution & Commune')]),
    (EVENTS_SRC, 'First Republic',     [(7, 'Economy & Politics'),
                                        (8, 'Counter-Revolution & Commune')]),
    (EVENTS_SRC, 'Translation Notes',  [(9, None)]),
]
CHART_DPI = 150

# --- Geometrie --------------------------------------------------------------
BOARD_UGC = ('1687147350559794172', 'AD967B112E1328CD6AF1496F464FBF143C60F04E')
BOARD_PX = (3543, 2516)

# Calibration TTS -> pixels du plateau (verifiee visuellement : les 4 armees
# regulieres tombent sur Lille/Metz/Strasbourg/Marseille, les marqueurs de
# piste sur la case 4, le regime sur « Legislative », la revolte a Bourges).
WORLD_W = 59.2
BOARD_CENTER = (-7.9706, -0.5179)

COUNTER_PX = 92        # taille d'un pion (une case de piste fait ~93 px)
ASSIGNAT_PX = 250      # largeur d'un assignat

# Emprise du plan de jeu complet, en unites TTS (plateau + reserve + zones joueurs)
WORLD_BOUNDS = (-38.6, 46.0, -36.0, 21.0)   # xmin, xmax, zmin, zmax
