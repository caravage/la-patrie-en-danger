# -*- coding: utf-8 -*-
"""Table des composants du jeu, etablie a partir du module Tabletop Simulator
"La Revolution francaise : La patrie en danger 1791-1795" (Workshop 2631264736).

Chaque entree associe l'index de l'image dans le module TTS a un nom de fichier
propre, un libelle francais, une categorie et (si pertinent) une tendance.
"""

# categories : perso, armee, marqueur, depute, assignat, verso
# (idx TTS, fichier, libelle, categorie, tendance, index_verso)
COMPONENTS = [
    (0,  'assignat_50',              'Assignat de 50 livres',        'assignat',  None,           None),

    # --- Tendances : marqueurs de controle (disponibles en nombre illimite) ---
    (2,  'marqueur_feuillant',       'Marqueur Feuillant',           'marqueur',  'Feuillant',    None),
    (5,  'marqueur_gironde',         'Marqueur Gironde',             'marqueur',  'Gironde',      None),
    (8,  'marqueur_montagne',        'Marqueur Montagne',            'marqueur',  'Montagne',     None),
    (9,  'marqueur_sansculotte',     'Marqueur Sans-Culotte',        'marqueur',  'Sans-Culotte', None),
    (3,  'marqueur_marais',          'Marqueur Marais',              'marqueur',  'Marais',       None),
    (4,  'marqueur_royaliste',       'Marqueur Royaliste',           'marqueur',  'Royaliste',    None),
    (28, 'revolte',                  'Revolte',                      'marqueur',  None,           None),
    (47, 'coalition_avance',         'Coalition (avance)',           'marqueur',  None,           None),

    # --- Personnalites recto seul ---
    (13, 'barere',                   'Barere',                       'perso',     'Marais',       None),
    (14, 'barras',                   'Barras',                       'perso',     'Marais',       None),
    (15, 'billaud_varenne',          'Billaud-Varenne',              'perso',     'Sans-Culotte', None),
    (16, 'boissy_danglas',           "Boissy d'Anglas",              'perso',     'Marais',       None),
    (17, 'carnot',                   'Carnot',                       'perso',     'Marais',       None),
    (18, 'collot_dherbois',          "Collot d'Herbois",             'perso',     'Sans-Culotte', None),
    (19, 'dandre',                   "d'Andre",                      'perso',     'Feuillant',    None),
    (20, 'danton',                   'Danton',                       'perso',     'Montagne',     None),
    (21, 'desmoulins',               'Desmoulins',                   'perso',     'Montagne',     None),
    (22, 'laclos',                   'Laclos',                       'perso',     'Feuillant',    None),
    (23, 'louis_xvi',                'Louis XVI',                    'perso',     'Feuillant',    None),
    (24, 'marat',                    'Marat',                        'perso',     'Montagne',     None),
    (25, 'petion',                   'Petion',                       'perso',     'Gironde',      None),
    (27, 'sieyes',                   'Sieyes',                       'perso',     'Marais',       None),

    # --- Personnalites recto/verso (verso = dos neutre de la tendance) ---
    (30, 'barnave',                  'Barnave',                      'perso',     'Feuillant',    10),
    (40, 'lafayette',                'Lafayette',                    'perso',     'Feuillant',    10),
    (41, 'lameth',                   'Lameth',                       'perso',     'Feuillant',    10),
    (31, 'barbaroux',                'Barbaroux',                    'perso',     'Gironde',      7),
    (32, 'brissot',                  'Brissot',                      'perso',     'Gironde',      7),
    (42, 'roland',                   'Roland',                       'perso',     'Gironde',      7),
    (43, 'vergniaud',                'Vergniaud',                    'perso',     'Gironde',      7),
    (45, 'robespierre',              'Robespierre',                  'perso',     'Montagne',     26),
    (46, 'saint_just',               'Saint-Just',                   'perso',     'Montagne',     26),
    (35, 'chaumette',                'Chaumette',                    'perso',     'Sans-Culotte', 11),
    (39, 'hebert',                   'Hebert',                       'perso',     'Sans-Culotte', 11),
    (44, 'roux',                     'Roux',                         'perso',     'Sans-Culotte', 11),
    (33, 'cadoudal',                 'Cadoudal',                     'perso',     'Royaliste',    6),
    (34, 'cathelineau',              'Cathelineau',                  'perso',     'Royaliste',    6),
    (36, 'charette',                 'Charette',                     'perso',     'Royaliste',    6),
    (37, 'chouan',                   'Chouan',                       'perso',     'Royaliste',    6),
    (38, 'dantraigues',              "d'Antraigues",                 'perso',     'Royaliste',    6),

    # --- Armees ---
    (1,  'armee_francaise',          'Armee francaise',              'armee',     None,           None),
    (61, 'armee_strasbourg',         'Armee de Strasbourg',          'armee',     None,           None),
    (62, 'armee_metz',               'Armee de Metz',                'armee',     None,           None),
    (63, 'armee_marseille',          'Armee de Marseille',           'armee',     None,           None),
    (64, 'armee_lille',              'Armee de Lille',               'armee',     None,           None),
    (71, 'armee_du_centre',          'Armee du Centre',              'armee',     None,           None),
    (72, 'armee_catholique_royale',  'Armee catholique et royale',   'armee',     None,           None),
    (73, 'armee_pays_de_retz',       'Armee du Pays de Retz',        'armee',     None,           None),
    (70, 'quiberon',                 'Quiberon (Emigres)',           'armee',     None,           None),
    (66, 'armee_espagnole_1',        'Armee espagnole 1',            'armee',     None,           None),
    (67, 'armee_espagnole_2',        'Armee espagnole 2',            'armee',     None,           None),
    (65, 'armee_sarde',              'Armee sarde',                  'armee',     None,           None),
    (68, 'brunswick',                'Brunswick (Prussiens)',        'armee',     None,           None),
    (69, 'cobourg',                  'Cobourg (Autrichiens)',        'armee',     None,           None),
    (74, 'wurmser',                  'Wurmser (Autrichiens)',        'armee',     None,           None),
    (75, 'york',                     'York (Anglais)',               'armee',     None,           None),
    (12, 'flotte_anglaise',          'La Flotte (Anglais)',          'armee',     None,           None),

    # --- Deputes ---
    (81, 'depute_feuillant',         'Depute Feuillant',             'depute',    'Feuillant',    None),
    (79, 'depute_gironde',           'Depute Gironde',               'depute',    'Gironde',      None),
    (80, 'depute_montagne',          'Depute Montagne',              'depute',    'Montagne',     None),
    (82, 'depute_sansculotte',       'Depute Sans-Culotte',          'depute',    'Sans-Culotte', None),
    (78, 'depute_marais',            'Depute Marais',                'depute',    'Marais',       None),
    (77, 'depute_royaliste',         'Depute Royaliste',             'depute',    'Royaliste',    None),

    # --- Marqueurs de piste et divers ---
    (48, 'tour',                     'Tour',                         'marqueur',  None,           None),
    (50, 'economie',                 'Economie',                     'marqueur',  None,           None),
    (51, 'clerge',                   'Clerge refractaire',           'marqueur',  None,           None),
    (52, 'coalition',               'Armees coalisees',             'marqueur',  None,           None),
    (49, 'commune_de_paris',         'Commune de Paris (piste)',     'marqueur',  None,           None),
    (76, 'commune',                  'Commune',                      'marqueur',  None,           None),
    (53, 'regime_politique',         'Regime politique',             'marqueur',  None,           None),
    (83, 'elections',                'Elections',                    'marqueur',  None,           None),
    (54, 'renommee_gouvernement',    'Renommee - Gouvernement',      'marqueur',  None,           None),
    (59, 'renommee_feuillant',       'Renommee - Feuillant',         'marqueur',  'Feuillant',    None),
    (57, 'renommee_gironde',         'Renommee - Gironde',           'marqueur',  'Gironde',      None),
    (58, 'renommee_montagne',        'Renommee - Montagne',          'marqueur',  'Montagne',     None),
    (60, 'renommee_sansculotte',     'Renommee - Sans-Culotte',      'marqueur',  'Sans-Culotte', None),
    (56, 'renommee_marais',          'Renommee - Marais',            'marqueur',  'Marais',       None),
    (55, 'renommee_royaliste',       'Renommee - Royaliste',         'marqueur',  'Royaliste',    None),
]

# Dos neutres, utilises comme deuxieme face des personnalites
VERSOS = {
    6:  'verso_blanc',
    7:  'verso_bleu',
    10: 'verso_jaune',
    11: 'verso_gris',
    26: 'verso_rouge',
}

# Plateau : image de la carte de France (index hors contact-sheet, gere a part)
BOARD_UGC = ('1687147350559794172', 'AD967B112E1328CD6AF1496F464FBF143C60F04E')

# Aides de jeu PDF : (fragment du nom de fichier TTS, nom propre, titre affiche)
PDFS = [
    ('DA9849', 'regles_completes_en',      'Regles completes (EN) - Decimal v1.0'),
    ('BFB24F', 'resume_regles_en',         'Resume des regles (EN)'),
    ('E6D3C8', 'actions_en',               'Tableau des actions (EN)'),
    ('0909A9', 'lois_en',                  'Tableau des lois (EN)'),
    ('FC0ED9', 'factions_en',              'Les tendances / factions (EN)'),
    ('F565F2', 'cycles_regimes_en',        'Cycles des regimes (EN)'),
    ('351FAF', 'regimes_fr',               'Tableau des regimes (FR)'),
    ('615ED8', 'cycles_regimes_fr',        'Cycle des regimes (FR)'),
    ('EA7731', 'cycles_regimes_ouverte_fr','Cycle des regimes - version ouverte (FR)'),
    ('C8F881', 'evenements_aleatoires_fr', 'Evenements aleatoires (FR)'),
    ('3D915F', 'evenements_aleatoires_en', 'Evenements aleatoires (EN)'),
]

SIDES = ['Feuillant', 'Gironde', 'Montagne', 'Sans-Culotte', 'Marais', 'Royaliste']

COUNTER_SIZE = 92      # pixels, ajuste a l'echelle du plateau (cases de piste ~93 px)
ASSIGNAT_WIDTH = 250   # pixels
