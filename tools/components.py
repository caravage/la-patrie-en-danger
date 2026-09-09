# -*- coding: utf-8 -*-
"""Catalogue des composants du jeu.

Etabli a partir du module Tabletop Simulator (Workshop 2631264736) et verifie
contre les regles anglaises (rules_en.pdf) : §3.1 (pions), §4.2 a §4.7 (mise en
place), §7.3.2 (changement de courant).

Les index renvoient a tools/tts_assets.py (TTS_IMAGES).
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

# --- Autres pions : (fichier, libelle, categorie, courant, index) -----------
PIECES = [
    # Marqueurs de controle regional : fournis en nombre illimite
    ('marqueur_feuillant',    'Controle Feuillant',    'controle', 'Feuillant',    2),
    ('marqueur_gironde',      'Controle Gironde',      'controle', 'Gironde',      5),
    ('marqueur_montagne',     'Controle Montagne',     'controle', 'Montagne',     8),
    ('marqueur_sansculotte',  'Controle Sans-Culotte', 'controle', 'Sans-Culotte', 9),
    ('marqueur_marais',       'Controle Marais',       'controle', 'Marais',       3),
    ('marqueur_royaliste',    'Controle Royaliste',    'controle', 'Royaliste',    4),
    ('coalition_controle',    'Controle Coalition',    'controle', None,          47),
    ('revolte',               'Revolte',               'controle', None,          28),


    # Armees francaises
    ('armee_francaise',       'Armee (volontaires)',   'armee', None, 1),
    ('armee_lille',           'Armee de Lille',        'armee', None, 64),
    ('armee_metz',            'Armee de Metz',         'armee', None, 62),
    ('armee_strasbourg',      'Armee de Strasbourg',   'armee', None, 61),
    ('armee_marseille',       'Armee de Marseille',    'armee', None, 63),
    ('commune',               'Commune de Paris',      'armee', None, 76),
    # Armees vendeennes
    ('armee_du_centre',       'Armee du Centre',       'armee', None, 71),
    ('armee_catholique',      'Armee catholique et royale', 'armee', None, 72),
    ('armee_pays_de_retz',    'Armee du Pays de Retz', 'armee', None, 73),
    # Coalition
    ('brunswick',             'Brunswick (Prussiens)', 'armee', None, 68),
    ('cobourg',               'Cobourg (Autrichiens)', 'armee', None, 69),
    ('wurmser',               'Wurmser (Autrichiens)', 'armee', None, 74),
    ('york',                  'York (Anglais)',        'armee', None, 75),
    ('flotte_anglaise',       'La Flotte (Anglais)',   'armee', None, 12),
    ('armee_espagnole_1',     'Armee espagnole 1',     'armee', None, 66),
    ('armee_espagnole_2',     'Armee espagnole 2',     'armee', None, 67),
    ('armee_sarde',           'Armee sarde',           'armee', None, 65),
    ('quiberon',              'Quiberon (Emigres)',    'armee', None, 70),

    # Marqueurs de piste
    ('tour',                  'Tour',                  'piste', None, 48),
    ('economie',              'Economie',              'piste', None, 50),
    ('clerge',                'Clerge refractaire',    'piste', None, 51),
    ('coalition_piste',       'Armees coalisees',      'piste', None, 52),
    ('commune_piste',         'Commune de Paris (piste)', 'piste', None, 49),
    ('regime_politique',      'Regime politique',      'piste', None, 53),
    ('elections',             'Elections',             'piste', None, 83),
    ('renommee_gouvernement', 'Renommee - Gouvernement', 'piste', None,          54),
    ('renommee_feuillant',    'Renommee - Feuillant',    'piste', 'Feuillant',    59),
    ('renommee_gironde',      'Renommee - Gironde',      'piste', 'Gironde',      57),
    ('renommee_montagne',     'Renommee - Montagne',     'piste', 'Montagne',     58),
    ('renommee_sansculotte',  'Renommee - Sans-Culotte', 'piste', 'Sans-Culotte', 60),
    ('renommee_marais',       'Renommee - Marais',       'piste', 'Marais',       56),
    ('renommee_royaliste',    'Renommee - Royaliste',    'piste', 'Royaliste',    55),

    # Argent
    ('assignat_50',           'Assignat de 50 livres', 'assignat', None, 0),
]

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

# Ancrages des six colonnes de l'Assemblee, en pixels du plateau
# (releves sur la mise en place du mod TTS).
ASSEMBLY_ANCHORS = {
    'Sans-Culotte': (232, 2185), 'Montagne': (354, 2185),
    'Gironde': (475, 2187), 'Marais': (599, 2182),
    'Feuillant': (724, 2186), 'Royaliste': (844, 2185),
}

# --- Tresorerie de depart (regles §4.6), en livres --------------------------
TREASURY = {
    'Sans-Culotte': 350, 'Montagne': 350, 'Gironde': 1400,
    'Marais': 800, 'Feuillant': 1400, 'Royaliste': 400,
}
TREASURY_GOVERNMENT = 2300

# --- Aides de jeu -----------------------------------------------------------
# (fragment de hash du fichier TTS, nom de fichier, titre affiche)
PDFS = [
    ('DA9849', 'regles_completes_en',       'Regles completes (EN)'),
    ('BFB24F', 'resume_regles_en',          'Resume des regles (EN)'),
    ('E6D3C8', 'actions_en',                'Tableau des actions (EN)'),
    ('0909A9', 'lois_en',                   'Tableau des lois (EN)'),
    ('FC0ED9', 'tendances_en',              'Les tendances et conditions de victoire (EN)'),
    ('F565F2', 'cycles_regimes_en',         'Cycles des regimes (EN)'),
    ('351FAF', 'regimes_fr',                'Tableau des regimes (FR)'),
    ('615ED8', 'cycles_regimes_fr',         'Cycle des regimes (FR)'),
    ('EA7731', 'cycles_regimes_ouverts_fr', 'Cycle des regimes - version ouverte (FR)'),
    ('C8F881', 'evenements_aleatoires_fr',  'Evenements aleatoires (FR)'),
    ('3D915F', 'evenements_aleatoires_en',  'Evenements aleatoires (EN)'),
]

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
