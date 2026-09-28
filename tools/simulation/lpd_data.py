# -*- coding: utf-8 -*-
"""Donnees statiques du jeu. Reutilise tools/components.py du module VASSAL
(personnalites, courants secondaires, tresorerie, Assemblee, pistes) et
complete avec ce que le module ne modelise pas : regions (lues sur
plan_de_jeu.jpg), influences des personnalites (lues sur leurs pions)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import components as C  # noqa: E402

R, F, M, G, MT, SC = 'Royaliste', 'Feuillant', 'Marais', 'Gironde', 'Montagne', 'Sans-Culotte'
CURRENTS = [R, F, M, G, MT, SC]
GOV = 'Government'
SHORT = {R: 'Roy', F: 'Feu', M: 'Mar', G: 'Gir', MT: 'Mtn', SC: 'S-C', GOV: 'Gov'}

# region -> (revenu, "chaude")  -- plan_de_jeu.jpg + regle 3.2.1
REGIONS = {
    'Lille': (300, False), 'Amiens': (300, False), 'Paris': (600, False),
    'Rouen': (300, False), 'Caen': (300, True), 'Brest': (100, True),
    'Nantes': (100, True), 'Angers': (100, True), 'Cholet': (100, True),
    'Tours': (100, False), 'Orleans': (200, False), 'Metz': (200, False),
    'Strasbourg': (100, True), 'Dijon': (100, True), 'Bourges': (200, True),
    'Nevers': (100, False), 'Clermont': (100, False), 'Lyon': (300, True),
    'Limoges': (100, False), 'Angouleme': (200, False), 'Bordeaux': (200, True),
    'Cahors': (100, False), 'Nimes': (200, True), 'Marseille': (200, True),
    'Toulouse': (200, True), 'Montpellier': (200, True),
}
assert len(REGIONS) == 26
VENDEE = ('Cholet', 'Nantes', 'Angers')

# Adjacences approximees d'apres la carte (utiles pour : armees
# revolutionnaires, "adjacent a Paris", mouvement vendeen).
_EDGES = """Lille-Amiens Amiens-Rouen Amiens-Paris Amiens-Metz Rouen-Paris Rouen-Caen
Rouen-Orleans Caen-Nantes Caen-Angers Caen-Tours Caen-Orleans Brest-Nantes Nantes-Angers
Nantes-Cholet Angers-Tours Angers-Cholet Cholet-Tours Cholet-Bourges Cholet-Angouleme
Cholet-Limoges Tours-Orleans Tours-Bourges Paris-Orleans Paris-Metz Paris-Dijon
Metz-Strasbourg Metz-Dijon Strasbourg-Dijon Dijon-Orleans Dijon-Nevers Dijon-Lyon
Orleans-Bourges Orleans-Nevers Bourges-Nevers Bourges-Limoges Bourges-Clermont
Nevers-Clermont Nevers-Lyon Clermont-Limoges Clermont-Lyon Clermont-Cahors Clermont-Nimes
Lyon-Marseille Lyon-Nimes Limoges-Angouleme Limoges-Bordeaux Limoges-Cahors
Angouleme-Bordeaux Bordeaux-Cahors Bordeaux-Toulouse Cahors-Toulouse Cahors-Montpellier
Cahors-Nimes Nimes-Marseille Nimes-Montpellier Toulouse-Montpellier""".split()
ADJ = {r: set() for r in REGIONS}
for e in _EDGES:
    a, b = e.split('-')
    ADJ[a].add(b)
    ADJ[b].add(a)

INITIAL_CONTROL = {}
for r in ('Angers', 'Cholet', 'Nantes', 'Tours'):
    INITIAL_CONTROL[r] = R
for r in ('Clermont', 'Dijon', 'Metz', 'Montpellier', 'Orleans', 'Rouen', 'Strasbourg', 'Toulouse'):
    INITIAL_CONTROL[r] = F
for r in ('Angouleme', 'Cahors', 'Limoges', 'Lyon', 'Nevers'):
    INITIAL_CONTROL[r] = M
for r in ('Amiens', 'Bordeaux', 'Caen', 'Paris'):
    INITIAL_CONTROL[r] = G
INITIAL_CONTROL['Lille'] = MT
INITIAL_CONTROL['Marseille'] = SC
# Brest, Nimes : neutres ; Bourges : neutre en revolte

# Influences lues sur les pions (Toulon -> region de Marseille)
INFLUENCE = {
    'barbaroux': {'Marseille', 'Paris', 'Brest'}, 'barere': {'Paris', 'Marseille'},
    'barnave': {'Nimes', 'Marseille'}, 'barras': {'Paris', 'Marseille'},
    'billaud_varenne': {'Marseille', 'Paris', 'Brest'}, 'boissy_danglas': {'Nimes', 'Clermont'},
    'brissot': {'Paris', 'Rouen'}, 'cadoudal': {'Nantes', 'Brest', 'Caen'},
    'carnot': {'Lille', 'Montpellier'}, 'cathelineau': {'Cholet', 'Angers'},
    'charette': {'Cholet', 'Nantes'}, 'chaumette': {'Paris'},
    'chouan': {'Angers', 'Tours', 'Caen'}, 'collot_dherbois': {'Nevers', 'Lyon', 'Paris'},
    'dandre': {'Marseille'}, 'danton': {'Paris'},
    'dantraigues': {'Nimes', 'Marseille', 'Montpellier'}, 'desmoulins': {'Paris'},
    'hebert': {'Paris'}, 'laclos': {'Toulouse', 'Montpellier'},
    'lafayette': {'Paris', 'Orleans', 'Montpellier'}, 'lameth': {'Lille', 'Strasbourg'},
    'louis_xvi': set(), 'marat': {'Paris'}, 'petion': {'Orleans', 'Paris', 'Caen'},
    'robespierre': {'Amiens', 'Paris', 'Lille'}, 'roland': {'Lyon', 'Paris'},
    'roux': {'Paris'}, 'saint_just': {'Strasbourg', 'Paris', 'Metz'},
    'sieyes': {'Tours', 'Bourges'}, 'vergniaud': {'Paris', 'Bordeaux'},
}
FACTION = {'barere': 'terrorist', 'billaud_varenne': 'terrorist', 'collot_dherbois': 'terrorist',
           'danton': 'merciful', 'desmoulins': 'merciful',
           'hebert': 'hebertist', 'chaumette': 'hebertist'}
GENERALS = {'cadoudal', 'cathelineau', 'charette', 'chouan'}
NEVER_MILITARY_COUP = {'marat', 'chaumette', 'hebert', 'roux'}

PERSO = {}
for pid, label, start, _idx, alts in C.PERSONALITIES:
    currents = {start, *alts}
    main = R if pid == 'louis_xvi' else start  # errata : Louis XVI est Royaliste
    PERSO[pid] = dict(label=label, start=start, main=main,
                      secondary=currents - {main}, influence=INFLUENCE[pid])

TREASURY = dict(C.TREASURY)
TREASURY_GOV = C.TREASURY_GOVERNMENT
ASSEMBLY = dict(C.ASSEMBLY)
TRACK_START = {'economy': C.TRACK_START['economie'], 'clergy': C.TRACK_START['clerge'],
               'coalition': C.TRACK_START['coalition_piste'], 'commune': C.TRACK_START['commune_piste']}
FAME_START = {R: C.TRACK_START['renommee_royaliste'], F: C.TRACK_START['renommee_feuillant'],
              M: C.TRACK_START['renommee_marais'], G: C.TRACK_START['renommee_gironde'],
              MT: C.TRACK_START['renommee_montagne'], SC: C.TRACK_START['renommee_sansculotte'],
              GOV: C.TRACK_START['renommee_gouvernement']}

# Table de resolution (lignes 2..12, colonnes 1-2 .. 19-20)
TABLE = {2: 'CCCCCCCCCC', 3: 'CCCCCCCCCC', 4: 'CCCCCCCCCC', 5: 'CCCCCCCCBB',
         6: 'CCCCCCBBBB', 7: 'CCCCBBBBBA', 8: 'CCBBBBBAAA', 9: 'BBBBBAAAAA',
         10: 'BBBAAAAAAA', 11: 'BAAAAAAAAA', 12: 'AAAAAAAAAA'}


def col(fame):
    return max(0, min(9, (fame - 1) // 2))


def table(roll, fame):
    return TABLE[roll][col(fame)]


# Probabilites exactes de 2d6
P2D6 = {s: sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == s) / 36 for s in range(2, 13)}


def p_result(fame, results='A'):
    return sum(p for s, p in P2D6.items() if table(s, fame) in results)


def p_best_of(fame, n, results='A'):
    p = p_result(fame, results)
    return 1 - (1 - p) ** max(1, n)


def level(v):
    return 1 if v <= 8 else (2 if v <= 16 else 3)


# --- Lois (13.0) ---------------------------------------------------------
# cle : (cout, fame, {piste: delta}, categorie)
LAWS = {
    'maximum':      (100, -1, {'economy': -5, 'commune': +3}, 'economy'),
    'free_prices':  (150, -2, {'economy': -7, 'commune': +3}, 'economy'),
    'containment':  (100, -1, {'economy': -4, 'commune': +2}, 'economy'),
    'anti_emigrants': (50, +1, {'coalition': +3, 'clergy': +3, 'commune': -3}, 'privilege'),
    'confiscation': (100, 0, {'coalition': +4, 'clergy': +2, 'commune': -3}, 'privilege'),
    'safety':       (50, +1, {'coalition': +2, 'clergy': +2, 'commune': -2}, 'privilege'),
    'usages':       (50, +1, {'coalition': +3, 'clergy': +3, 'commune': -3}, 'clergy'),
    'nat_goods':    (100, 0, {'coalition': +2, 'clergy': +4, 'commune': -3}, 'clergy'),
    'worship':      (50, +1, {'coalition': +2, 'clergy': +2, 'commune': -2}, 'clergy'),
    'civic':        (50, +1, {}, 'civic'),
    'war':          (100, +1, {'clergy': +3}, 'military'),
    'conscription': (100, 0, {'coalition': +5}, 'military'),
    'levee':        (200, -1, {'clergy': +3}, 'military'),
    'fatherland':   (100, 0, {}, 'special'),
    'outlaw_hebertists': (100, 0, {}, 'outlaw'),
    'outlaw_merciful':   (100, 0, {}, 'outlaw'),
    'outlaw_terrorists': (100, 0, {}, 'outlaw'),
    'trial':        (0, 0, {}, 'trial'),
}

# --- Regimes ---------------------------------------------------------------
HS_REGIMES = ('Legislative', 'Convention', 'Terror', 'Thermidor')
OFFICIAL = {
    'Legislative': {G, M, F}, 'Convention': {G, M, MT}, 'Terror': {M, MT},
    'Thermidor': {M, F, G}, 'Wrath': {M, SC}, 'Mercy': {M, G, MT},
    'Directorate': {M, F, G, MT}, 'Prairial': {MT, SC}, 'FFR': {G, M, MT},
    'FROI': {SC, M, MT},
}
OUTLAW_CURRENTS = {
    'Legislative': set(), 'Convention': {R, F}, 'Terror': {R, F, G}, 'Thermidor': {R},
    'Wrath': {R, F, G, MT}, 'Mercy': {R}, 'Directorate': {R}, 'Prairial': {R, M, F, G},
    'FFR': {R}, 'FROI': {R, F},
}
_ARR4 = {'marat', 'chaumette', 'hebert', 'roux'}
ARRESTABLE = {
    'Legislative': _ARR4 | {'cadoudal', 'cathelineau', 'charette', 'chouan'},
    'Convention': _ARR4, 'Terror': {'roux'}, 'Thermidor': _ARR4, 'Wrath': set(),
    'Mercy': _ARR4, 'Directorate': _ARR4, 'Prairial': set(), 'FFR': _ARR4, 'FROI': set(),
}
# qui propose les lois : 'gov' (3 max, gratuit), 'currents' (1 chacun, 50), 'both'
LAW_PROPOSERS = {'Legislative': 'both', 'Convention': 'currents', 'Terror': 'gov',
                 'Thermidor': 'gov', 'Wrath': 'gov', 'Mercy': 'gov', 'Directorate': 'gov',
                 'Prairial': 'gov', 'FFR': 'currents', 'FROI': 'currents'}
# vote : 'deputies' ou 'fame' (fame du proposant sous la Convention, du Gouvernement sinon)
LAW_VOTE = {'Legislative': 'deputies', 'Convention': 'fame', 'Terror': 'fame',
            'Thermidor': 'deputies', 'Wrath': 'fame', 'Mercy': 'fame', 'Directorate': 'deputies',
            'Prairial': 'fame', 'FFR': 'deputies', 'FROI': 'deputies'}
DEPUTY_SWITCH = {'Legislative', 'Thermidor', 'Directorate', 'FFR', 'FROI'}
CRITICISM = {'Legislative': (F, G), 'Mercy': (MT, M), 'FFR': (G, M), 'FROI': (MT, SC),
             'Directorate': None}
PROVISIONAL = {'Convention', 'Terror', 'Thermidor', 'Wrath', 'Mercy', 'Prairial'}
DEPUTY_TARGETS = {R: (F, M), F: (R, M), M: (F, G), G: (M,), MT: (SC, M), SC: (MT, M)}
# equivalence pour le tableau des "also-rans" (14.4) et 14.3
VICTORY_FAMILY = {'Legislative': 'Legislative', 'Convention': 'Convention', 'FFR': 'Convention',
                  'Terror': 'Terror', 'Mercy': 'Terror', 'Wrath': 'Terror', 'Prairial': 'Terror',
                  'FROI': 'Terror', 'Thermidor': 'Thermidor', 'Directorate': 'Directorate'}
# 14.4 : rangs des perdants [R, F, M, G, MT, SC]
ALSO_RANS = {
    (R, None): [1, 5, 6, 6, 6, 6],
    (F, 'Legislative'): [3, 1, 2, 4, 5, 6], (F, 'Thermidor'): [3, 1, 2, 4, 6, 5],
    (M, 'Legislative'): [4, 2, 1, 3, 5, 6], (M, 'Convention'): [6, 5, 1, 2, 3, 4],
    (M, 'Terror'): [6, 3, 1, 2, 5, 4], (M, 'Thermidor'): [6, 2, 1, 3, 4, 5],
    (G, 'Legislative'): [6, 4, 2, 1, 3, 5], (G, 'Convention'): [6, 5, 2, 1, 3, 4],
    (G, 'Thermidor'): [6, 5, 2, 1, 3, 4],
    (MT, 'Convention'): [6, 5, 3, 4, 1, 2], (MT, 'Terror'): [6, 5, 3, 4, 1, 2],
    (SC, 'Terror'): [6, 5, 3, 4, 2, 1],
}

# Routes des armees alliees (9.5.2)
ALLIED = {
    'cobourg': dict(label='Cobourg', entry='Lille', route=['Lille', 'Amiens', 'Paris', 'Orleans', 'Rouen'], wave=1),
    'brunswick': dict(label='Brunswick', entry='Metz', route=['Metz', 'Paris'], wave=1),
    'wurmser': dict(label='Wurmser', entry='Strasbourg', route=['Strasbourg', 'Dijon', 'Paris', 'Dijon', 'Lyon'], wave=1),
    'sardinia': dict(label='Sardinian', entry='Marseille', route=['Marseille'], wave=2),
    'spain1': dict(label='Spanish 1', entry='Montpellier', route=['Montpellier'], wave=2),
    'spain2': dict(label='Spanish 2', entry='Toulouse', route=['Toulouse'], wave=2),
    'york': dict(label='York', entry='Lille', route=['Lille'], wave=2),
    'fleet': dict(label='English Fleet', entry='Marseille', route=['Marseille'], wave=3),
    'quiberon': dict(label='Quiberon', entry='Nantes', route=['Nantes', 'Angers', 'Tours', 'Orleans', 'Paris'], wave=3),
}
REGULARS = {'army_lille': 'Lille', 'army_metz': 'Metz', 'army_strasbourg': 'Strasbourg', 'army_marseille': 'Marseille'}
CATHOLIC = ['armee_catholique', 'armee_du_centre', 'armee_pays_de_retz']
VENDEE_ROUTE = ['Angers', 'Tours', 'Orleans', 'Paris']
