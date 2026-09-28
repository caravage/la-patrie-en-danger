# -*- coding: utf-8 -*-
"""Tables d'evenements aleatoires, traduction v7 (assets/pdf/random_events_v7.pdf).
Chaque table : (fonction modificateur(g) -> int, {jet: fonction(g)}).
Les evenements "une seule fois" utilisent g.once(cle)."""
from lpd_data import R, F, M, G, MT, SC, GOV, level


def seq(*fns):
    def run(g):
        for f in fns:
            f(g)
    return run


def need(pid, fn):
    """Evenement souligne : le personnage doit etre vivant et hors de prison."""
    def run(g):
        if g.available(pid):
            fn(g)
    return run


def once(key, fn):
    def run(g):
        if g.once(key):
            fn(g)
    return run


def when(cond, fn):
    def run(g):
        if cond(g):
            fn(g)
    return run


fame = lambda who, d: (lambda g: g.fame_adj(who, d, 'event'))
track = lambda t, d: (lambda g: g.track(t, d, 'event'))
neutral = lambda r: (lambda g: g.ev_neutral(r))
nrevolt = lambda r: (lambda g: g.ev_neutral_revolt(r))
pays = lambda r, a, exempt=None: (lambda g: g.ev_controller_pays(r, a, exempt))
crevolt = lambda c, r: (lambda g: g.ev_control_revolt(c, r))
riot = lambda r: (lambda g: g.ev_royalist_riot(r))
rrevolt = lambda r: (lambda g: g.ev_control_revolt(R, r))
control = lambda c, r: (lambda g: g.ev_control(c, r))
gov_pay = lambda a: (lambda g: g.gov_pay(a))
bonus = lambda k, v: (lambda g: g.add_bonus(k, v))
neutral_pay = lambda r, a: seq(pays(r, a), neutral(r))
war = lambda g: g.foreign_war
peace = lambda g: not g.foreign_war


def lv(g, t):
    return level(g.tracks[t])


def bread(g):
    g.gov_decide('bread', yes=seq(fame(GOV, +1), gov_pay(300)),
                 no=seq(lambda g: g.paris_neutral(), gov_pay(200)))


def peace_asked(g):
    g.gov_decide('peace_asked', yes=seq(fame(GOV, +1), gov_pay(300)),
                 no=seq(fame(GOV, -1), track('commune', +3)))


def terror_econ():
    t = {12: nrevolt('Marseille')}
    for a, b, r, amt in ((2, 3, 'Dijon', 100), (4, 5, 'Tours', 100), (6, 7, 'Orleans', 200),
                         (8, 9, 'Metz', 200), (10, 11, 'Amiens', 300)):
        t[a] = t[b] = neutral_pay(r, amt)
    return (lambda g: (2 if lv(g, 'economy') == 2 else 3 if lv(g, 'economy') == 3 else 0), t)


def terror_cr(mod):
    t = {}
    for rolls, fn in (((2, 3), riot('Angers')), ((4, 5), riot('Nantes')),
                      ((6, 7), rrevolt('Marseille')), ((8, 9), rrevolt('Cholet')),
                      ((10, 11, 12), rrevolt('Lyon'))):
        for x in rolls:
            t[x] = fn
    return (mod, t)


def thermidor_econ(mod):
    return (mod, {
        2: neutral('Nimes'), 3: neutral('Strasbourg'), 4: neutral('Lyon'), 5: neutral('Marseille'),
        6: control(F, 'Strasbourg'), 7: control(F, 'Nimes'), 8: control(F, 'Marseille'),
        9: control(F, 'Lyon'),
        10: seq(neutral('Orleans'), gov_pay(200)), 11: seq(neutral('Rouen'), gov_pay(300)),
        12: seq(track('commune', +5), track('economy', +5)),
    })


def basel(g):
    if g.foreign_war and g.once('basel'):
        g.discard_allied(['spain1', 'spain2', 'brunswick'])
        g.track('coalition', -5, 'event')
        g.track('clergy', -2, 'event')


def jaunaye(g):
    if g.catholic_on_map():
        g.track('clergy', -5, 'event')


def thermidor_cr():
    return (lambda g: 2 if lv(g, 'coalition') == 3 else 0, {
        2: track('clergy', -4), 3: track('clergy', -4), 4: basel, 5: basel,
        6: jaunaye, 7: jaunaye, 8: once('louis17', track('clergy', +2)),
        9: track('clergy', +4), 10: track('clergy', +4),
        11: rrevolt('Brest'), 12: rrevolt('Cholet'),
    })


def econ_mod(a, b, c=None):
    """modificateurs selon niveau d'economie (I, II, III)"""
    def m(g):
        l = lv(g, 'economy')
        return {1: a or 0, 2: b or 0, 3: c or 0}[l]
    return m


def conv_econ(extra_mod=None):
    def mod(g):
        return econ_mod(1, 2, 3)(g) + (extra_mod(g) if extra_mod else 0)
    return (mod, {
        2: crevolt(SC, 'Lyon'), 3: crevolt(SC, 'Orleans'), 4: crevolt(SC, 'Tours'),
        5: pays('Orleans', 200, SC), 6: pays('Tours', 100, SC), 7: pays('Montpellier', 200, SC),
        8: pays('Amiens', 300, SC),
        9: nrevolt('Dijon'), 10: nrevolt('Montpellier'), 11: nrevolt('Metz'), 12: nrevolt('Rouen'),
    })


def betrayal(regions, allied_back):
    def run(g):
        g.discard_rev_army(regions)
        if allied_back:
            g.allied_return()
    return run


def catholic_back(fn):
    def run(g):
        fn(g)
        g.catholic_return()
    return run


def forfeiture(g):
    g.assembly_decide('forfeiture',
                      yes=seq(track('commune', -2), fame(F, -1), fame(M, -1)),
                      no=seq(track('commune', +2), fame(F, +1)))


def pikes(g):
    g.gov_decide('pikes', yes=seq(track('commune', -1), fame(GOV, +1)),
                 no=seq(track('commune', +1), fame(GOV, -1)))


def feed_people(g):
    g.gov_decide('feed', yes=seq(track('commune', -2), gov_pay(300)),
                 no=seq(track('commune', +2), fame(GOV, -2)))


def conv_bread(g):
    g.gov_decide('bread_conv', yes=gov_pay(300),
                 no=seq(track('commune', +2), fame(GOV, -1), fame(G, -1)))


def marie_antoinette(g):
    g.gov_decide('marie_antoinette', yes=seq(fame(GOV, +2), track('commune', -3)),
                 no=seq(fame(GOV, -1), track('commune', +3)))


def unless(cond, fn):
    """penalite appliquee en fin de tour sauf si la condition est remplie"""
    def run(g):
        g.end_checks.append((cond, fn))
    return run


EVENTS = {}

EVENTS['Legislative'] = {
    'economy': (econ_mod(0, 1, 2), {
        2: seq(nrevolt('Marseille'), track('clergy', -2)), 3: nrevolt('Marseille'),
        4: neutral('Bordeaux'), 5: neutral('Cahors'), 6: neutral('Limoges'),
        7: pays('Nimes', 200), 8: pays('Rouen', 300), 9: neutral('Amiens'), 10: neutral('Lille'),
        11: nrevolt('Orleans'), 12: nrevolt('Dijon')}),
    'politics': (lambda g: (5 if g.foreign_war else -4) + (2 if g.gov_holder == G else 0), {
        2: need('brissot', seq(fame(G, +1), track('coalition', +2))),
        3: need('marat', fame(G, -1)),
        4: need('robespierre', seq(fame(G, -1), track('coalition', -1))),
        5: need('lafayette', seq(fame(F, +1), track('coalition', +1))),
        6: need('lameth', seq(fame(F, -1), track('coalition', -1))),
        7: bonus(('persuade', F), 2), 8: bonus(('persuade', G), 2),
        9: need('roux', fame(SC, +1)),
        10: need('robespierre', seq(fame(MT, +1), fame(G, -1))),
        11: bonus('lille_nofight', 1),
        12: seq(fame(G, +1), fame(MT, +1))}),
    'counter': (lambda g: -lv(g, 'coalition') + (5 if g.foreign_war else -2), {
        2: track('coalition', +2), 3: track('coalition', +2),
        4: seq(track('coalition', +1), track('clergy', +1), track('commune', -1)),
        5: once('austro_prussian', track('coalition', +2)),
        6: seq(track('coalition', -2), lambda g: g.reset_once('austro_prussian')),
        7: riot('Brest'), 8: riot('Nimes'), 9: track('clergy', +2),
        10: seq(crevolt(R, 'Marseille'), track('clergy', +1)),
        11: lambda g: g.discard_rev_army(None),
        12: once('brunswick_manifesto', seq(track('commune', +3), track('clergy', +3)))}),
    'commune': (lambda g: lv(g, 'economy') + (-3 if g.foreign_war else 2) + (-3 if g.gironde_ousted else 0), {
        2: once('tuileries', lambda g: g.commune_rise(G, force=True)),
        3: forfeiture, 4: pikes, 5: track('commune', +2), 6: track('commune', +1),
        7: track('commune', -2), 8: track('commune', +1), 9: track('economy', +2),
        10: feed_people, 11: gov_pay(500),
        12: lambda g: (g.paris_neutral(), g.commune_rise(None, force=True))}),
}

EVENTS['Convention'] = {
    'economy': conv_econ(lambda g: -5 if g.fame[SC] > 9 else 0),
    'politics': (lambda g: 4 if g.king == 'dead' else -4, {
        2: need('saint_just', bonus('trial_vote', 4)),
        3: bonus('trial_vote', -2),
        4: when(war, once('lafayette_desertion', lambda g: (g.add_bonus(('combat', 'Metz'), -1),
                                                           g.exile(['lafayette', 'lameth'])))),
        5: seq(fame(G, -1), track('commune', -2)),
        6: seq(track('commune', +2), bonus(('arrest', 'marat'), 2)),
        7: need('roland', fame(MT, -1)), 8: need('roux', fame(MT, -1)),
        9: need('robespierre', fame(G, -1)), 10: need('marat', fame(G, -1)),
        11: track('commune', -3),
        12: seq(lambda g: g.commune_rise(SC, force=True), track('commune', +3))}),
    'counter': (lambda g: lv(g, 'clergy') + (1 if g.king == 'dead' else -5), {
        2: crevolt(R, 'Cholet'), 3: bonus('trial_vote', -2),
        4: lambda g: g.ev_retreat(), 5: lambda g: g.discard_allied(['sardinia']),
        6: when(war, once('montesquiou', betrayal(['Marseille'], False))),
        7: riot('Marseille'), 8: riot('Lyon'), 9: riot('Rouen'),
        10: crevolt(R, 'Nimes'), 11: once('regent', track('clergy', +2)),
        12: when(war, once('dumouriez', lambda g: (g.discard_rev_army(['Lille', 'Amiens'], strict=True),
                                                   g.allied_return(['cobourg']))))}),
    'commune': (lambda g: lv(g, 'economy') + (0 if g.king == 'dead' else -5), {
        2: bonus('trial_vote', 2), 3: lambda g: g.kill_prisoners({R, F}, spare_king=True),
        4: lambda g: g.kill_prisoners({R, F}, spare_king=True), 5: track('clergy', +2),
        6: when(lambda g: 'tuileries' in g.used_once, track('commune', +1)),
        7: track('commune', -1), 8: track('commune', -1), 9: conv_bread, 10: gov_pay(200),
        11: lambda g: g.paris_neutral(), 12: track('commune', +3)}),
}

EVENTS['Terror'] = {
    'economy': terror_econ(),
    'politics': (lambda g: (-4 if g.alive('marat') else 0) + (2 if g.faction_outlawed('hebertist') else 0)
                 + (2 if g.faction_outlawed('merciful') else 0), {
        2: once('corday', lambda g: g.kill('marat')),
        3: crevolt(G, 'Caen'),
        4: need('roux', unless(lambda g: g.status('roux') in ('prison', 'dead'), fame(MT, -1))),
        5: need('hebert', unless(lambda g: g.faction_outlawed('hebertist'), fame(MT, -2))),
        6: need('hebert', unless(lambda g: g.faction_outlawed('hebertist'), fame(MT, -2))),
        7: need('danton', seq(unless(lambda g: g.faction_outlawed('hebertist'), fame(MT, -2)),
                              bonus(('outlaw', 'hebertist'), 2))),
        8: need('danton', seq(unless(lambda g: g.faction_outlawed('hebertist'), fame(MT, -2)),
                              bonus(('outlaw', 'hebertist'), 2))),
        9: seq(bonus('gov_police', 2), bonus(('outlaw', 'hebertist'), 2), bonus(('outlaw', 'merciful'), 2)),
        10: seq(bonus('gov_police', 2), bonus(('outlaw', 'hebertist'), 2), bonus(('outlaw', 'merciful'), 2)),
        11: seq(fame(MT, +1), bonus('votes', 2)), 12: bonus('votes', -4)}),
    'counter': terror_cr(lambda g: {1: 0, 2: 2, 3: 3}[lv(g, 'clergy')]),
    'commune': (lambda g: {1: 0, 2: 2, 3: 3}[lv(g, 'economy')] + (2 if lv(g, 'commune') == 3 else 0), {
        2: track('commune', +2), 3: track('commune', +2), 4: track('commune', -2), 5: track('commune', -2),
        6: lambda g: g.temp_army(), 7: marie_antoinette,
        8: bonus(('outlaw', 'merciful'), 2), 9: bonus(('outlaw', 'merciful'), 2),
        10: bread, 11: bread, 12: seq(lambda g: g.paris_neutral(), gov_pay(200))}),
}

EVENTS['Thermidor'] = {
    'economy': thermidor_econ(econ_mod(0, 2, 3)),
    'politics': (lambda g: (2 if lv(g, 'clergy') >= 2 else 0) + (3 if lv(g, 'economy') == 3 else 0), {
        2: bonus(('persuade', F), 2), 3: bonus(('persuade', F), 2),
        4: bonus(('persuade', MT), 2), 5: bonus(('persuade', MT), 2),
        6: track('commune', +2), 7: bonus(('outlaw', 'terrorist'), 2), 8: bonus(('outlaw', 'terrorist'), 2),
        9: bonus('gov_police', 2),
        10: seq(unless(lambda g: g.faction_outlawed('terrorist'), fame(M, -2)),
                lambda g: g.switch_event('barere', MT)),
        11: bonus('feuillant_commune', 1),
        12: need('barras', seq(track('commune', -5), lambda g: g.commune_calm()))}),
    'counter': thermidor_cr(),
    'commune': (econ_mod(0, 2, 3), {
        2: bonus('arrest_terrorists', 2), 3: bonus('arrest_terrorists', 2),
        4: when(lambda g: g.king == 'dead', track('commune', -2)),
        5: when(lambda g: g.king == 'dead', track('commune', -2)),
        6: track('commune', -4), 7: track('commune', -4),
        8: peace_asked, 9: peace_asked, 10: peace_asked,
        11: lambda g: g.commune_rise(None, force=True), 12: lambda g: g.commune_rise(None, force=True)}),
}

EVENTS['Mercy'] = {
    'economy': (econ_mod(2, 3, 0), {
        2: neutral_pay('Tours', 200), 3: neutral_pay('Orleans', 200), 4: neutral_pay('Metz', 200),
        5: neutral_pay('Nimes', 200), 6: neutral_pay('Amiens', 300), 7: nrevolt('Lyon'),
        8: nrevolt('Marseille'), 9: control(F, 'Strasbourg'), 10: neutral_pay('Bordeaux', 200),
        11: neutral_pay('Rouen', 300), 12: seq(track('commune', +5), track('economy', +5))}),
    'politics': (lambda g: {1: 0, 2: 1, 3: 2}[lv(g, 'clergy')] + (5 if lv(g, 'economy') == 3 else 0)
                 + (0 if g.foreign_war else -3), {
        2: crevolt(G, 'Bordeaux'), 3: need('barnave', fame(MT, -2)), 4: bonus(('persuade', MT), 2),
        5: need('roux', unless(lambda g: g.status('roux') in ('prison', 'dead'), fame(MT, -1))),
        6: bonus('gov_police', 1), 7: bonus(('rally', M), 2),
        8: need('barras', bonus(('persuade', M), 2)), 9: bonus(('coup_popular', MT), 2),
        10: need('robespierre', fame(M, -2)),
        11: seq(fame(MT, +1), bonus('votes', 2), lambda g: g.switch_event('barere', MT)),
        12: need('barras', seq(track('commune', -5), lambda g: g.commune_calm()))}),
    'counter': (lambda g: (-2 if not g.civil_war() else 0) + (0 if g.foreign_war else 2), {
        2: riot('Angers'), 3: riot('Brest'), 4: rrevolt('Marseille'), 5: rrevolt('Lyon'),
        6: jaunaye, 7: jaunaye, 8: once('louis17', track('clergy', +2)), 9: track('clergy', +4),
        10: rrevolt('Angers'), 11: rrevolt('Nantes'), 12: rrevolt('Cholet')}),
    'commune': (econ_mod(0, 1, 2), {
        2: track('commune', -2), 3: track('commune', +2),
        4: when(lambda g: g.king == 'dead', track('commune', -2)), 5: lambda g: g.temp_army(),
        6: track('commune', -2), 7: bread, 8: bread, 9: track('commune', +3),
        10: seq(lambda g: g.paris_neutral(), gov_pay(200)), 11: seq(lambda g: g.paris_neutral(), gov_pay(200)),
        12: lambda g: g.commune_rise(None, force=True)}),
}

EVENTS['Wrath'] = {
    'economy': terror_econ(),
    'politics': (lambda g: (1 if lv(g, 'clergy') >= 2 else 0) + (1 if lv(g, 'coalition') >= 2 else 0)
                 + (1 if lv(g, 'economy') == 3 else 0) + (0 if g.foreign_war else -2), {
        2: crevolt(G, 'Bordeaux'), 3: crevolt(MT, 'Orleans'), 4: crevolt(MT, 'Dijon'),
        5: need('barras', seq(fame(M, +1), fame(SC, -1), track('commune', -2))),
        6: need('hebert', fame(M, -2)),
        7: seq(bonus('gov_police', 2), bonus(('outlaw', 'merciful'), 2)),
        8: seq(bonus('gov_police', 2), bonus(('outlaw', 'merciful'), 2)),
        9: seq(bonus('gov_police', 2), bonus(('outlaw', 'merciful'), 2)),
        10: bonus(('coup_popular', M), 2),
        11: when(lambda g: g.holder('collot_dherbois') == SC,
                 seq(lambda g: g.commune_rise(SC, force=True), track('commune', +3))),
        12: seq(fame(SC, +1), bonus('votes', 2), lambda g: g.switch_event('marat', SC))}),
    'counter': terror_cr(lambda g: {1: 0, 2: 2, 3: 3}[lv(g, 'clergy')]),
    'commune': (lambda g: {1: 0, 2: 1, 3: 2}[lv(g, 'commune')], {
        2: track('commune', -2), 3: track('commune', -2), 4: track('commune', +2), 5: track('commune', +2),
        6: bonus(('outlaw', 'merciful'), 2), 7: bonus(('outlaw', 'merciful'), 2),
        8: lambda g: g.temp_army(), 9: bread,
        10: seq(track('commune', +1), fame(SC, +1), fame(GOV, +1), track('economy', +1)),
        11: seq(track('commune', +2), fame(GOV, +1)),
        12: seq(lambda g: g.give(SC, 500), bonus(('paris_action', SC), 2), track('economy', +2))}),
}

EVENTS['Directorate'] = {
    'economy': thermidor_econ(econ_mod(0, 2, 3)),
    'politics': (lambda g: {1: 0, 2: 1, 3: 2}[lv(g, 'clergy')] + (5 if lv(g, 'economy') == 3 else 0)
                 + (0 if g.foreign_war else -3), {
        2: crevolt(MT, 'Orleans'), 3: bonus(('persuade', MT), 2), 4: bonus(('coup_limited', G), 2),
        5: bonus(('persuade', F), 2), 6: bonus('gov_police', 2), 7: bonus(('coup_popular', MT), 2),
        8: when(lambda g: g.holder('barras') == M, bonus(('persuade', M), 2)),
        9: bonus(('coup_limited', F), 2), 10: bonus(('coup_popular', R), 2),
        11: seq(lambda g: g.move_deputies(R, M, half_up=True), track('commune', +3), fame(GOV, -2)),
        12: need('barras', seq(track('commune', -5), lambda g: g.commune_calm()))}),
    'counter': thermidor_cr(),
    'commune': (econ_mod(0, 1, 2), {
        2: bonus('arrest_terrorists', 2), 3: bonus('arrest_terrorists', 2),
        4: when(lambda g: g.king == 'dead', track('commune', -2)), 5: track('commune', +2),
        6: track('commune', -4), 7: gov_pay(200), 8: peace_asked,
        9: seq(lambda g: g.commune_calm(), bonus('royalist_commune', 1)),
        10: seq(lambda g: g.commune_calm(), bonus('royalist_commune', 1)),
        11: seq(lambda g: g.paris_neutral(), gov_pay(200)),
        12: lambda g: g.commune_rise(None, force=True)}),
}

EVENTS['Prairial'] = {
    'economy': terror_econ(),
    'politics': (lambda g: (1 if 3 in (lv(g, 'clergy'), lv(g, 'coalition')) else 0)
                 + (2 if lv(g, 'economy') == 3 else 0) + (0 if g.foreign_war else -3), {
        2: crevolt(G, 'Bordeaux'), 3: crevolt(M, 'Toulouse'), 4: crevolt(M, 'Rouen'),
        5: fame(SC, -2), 6: seq(fame(MT, -1), track('commune', +1)),
        7: bonus('gov_police', 2), 8: bonus('gov_police', 2),
        9: bonus(('coup_popular', R), 2), 10: bonus(('coup_popular', R), 2),
        11: when(lambda g: g.holder('collot_dherbois') == SC,
                 seq(lambda g: g.commune_rise(SC, force=True), track('commune', +3))),
        12: seq(track('commune', +3), lambda g: g.commune_rise(SC, force=True), bonus('gov_all', 2))}),
    'counter': terror_cr(lambda g: {1: 0, 2: 2, 3: 3}[lv(g, 'clergy')]),
    'commune': (econ_mod(0, 2, 3), {
        2: track('commune', +2), 3: track('commune', +2),
        4: lambda g: g.kill_prisoners({R, F}, spare_king=False),
        5: lambda g: g.temp_army(), 6: lambda g: g.temp_army(),
        7: seq(track('commune', +2), fame(GOV, +1)), 8: seq(track('commune', +2), fame(GOV, +1)),
        9: seq(lambda g: g.give(SC, 500), bonus(('paris_action', SC), 2), track('economy', +2)),
        10: bread, 11: bread, 12: seq(lambda g: g.paris_neutral(), gov_pay(200))}),
}

EVENTS['FFR'] = {
    'economy': conv_econ(lambda g: -econ_mod(1, 2, 3)(g) + econ_mod(0, 1, 2)(g)),
    'politics': (lambda g: (1 if lv(g, 'economy') >= 2 else 0) + (2 if g.foreign_war else 0)
                 + (1 if g.gov_holder == G else 0), {
        2: lambda g: g.free_all_prisoners(), 3: need('desmoulins', fame(G, -1)),
        4: need('barras', bonus(('persuade', M), 2)), 5: bonus('gov_police', 1),
        6: need('roland', fame(MT, -1)), 7: bonus(('persuade', G), 2), 8: need('roland', fame(M, -1)),
        9: seq(bonus(('coup_popular', MT), 2), bonus(('coup_popular', M), 2)),
        10: track('commune', -3),
        11: need('danton', seq(fame(GOV, -1), fame(G, -1), track('commune', +2))),
        12: need('vergniaud', seq(track('commune', -3), lambda g: g.commune_calm()))}),
    'counter': (lambda g: {1: 0, 2: 1, 3: 2}[lv(g, 'clergy')], {
        2: rrevolt('Lyon'),
        3: once('peace_england', lambda g: (g.discard_allied(['york', 'fleet', 'brunswick']),
                                            g.track('coalition', -5, 'event'), g.track('clergy', -2, 'event'))),
        4: track('clergy', -2), 5: riot('Lyon'), 6: riot('Nimes'),
        7: when(lambda g: g.foreign_war or g.civil_war(), betrayal(['Marseille'], False)),
        8: when(lambda g: g.foreign_war or g.civil_war(), betrayal(['Amiens', 'Lille'], True)),
        9: when(lambda g: g.foreign_war or g.civil_war(), betrayal(['Metz', 'Strasbourg'], True)),
        10: riot('Rouen'), 11: catholic_back(rrevolt('Cholet')), 12: catholic_back(rrevolt('Brest'))}),
    'commune': (econ_mod(0, 1, 2), {
        2: seq(lambda g: g.paris_neutral(), track('commune', -3)), 3: track('commune', -1),
        4: seq(fame(G, +2), track('commune', -2)), 5: seq(fame(GOV, +1), fame(G, +1), track('commune', -2)),
        6: gov_pay(200), 7: bread, 8: bread,
        9: seq(lambda g: g.commune_rise(SC, force=True), track('commune', +3), fame(GOV, -1)),
        10: seq(lambda g: g.paris_neutral(), gov_pay(400)), 11: track('commune', -1),
        12: lambda g: g.commune_rise(None, force=True)}),
}

EVENTS['FROI'] = {
    'economy': (econ_mod(0, 1, 2), terror_econ()[1]),
    'politics': (lambda g: (1 if lv(g, 'economy') >= 2 else 0) + (2 if g.foreign_war else 0)
                 + (1 if g.gov_holder == SC else 0), {
        2: crevolt(G, 'Bordeaux'), 3: crevolt(F, 'Montpellier'),
        4: need('barnave', lambda g: g.fame_adj(g.gov_holder, -1, 'event')),
        5: bonus('gov_police', 2), 6: bonus('gov_police', 2),
        7: lambda g: g.add_bonus(('coup_limited', SC if g.gov_holder == MT else MT), 2),
        8: lambda g: g.froi_split_marais(), 9: bonus(('coup_popular', M), 2),
        10: need('robespierre', fame(SC, -2)),
        11: when(lambda g: g.holder('collot_dherbois') == SC, seq(fame(MT, -1), track('commune', +1))),
        12: bonus('gov_all', 1)}),
    'counter': (lambda g: (-3 if g.foreign_war else 0) + (2 if lv(g, 'clergy') == 1 else 0), {
        2: rrevolt('Nimes'), 3: rrevolt('Lyon'),
        4: when(lambda g: g.foreign_war or g.civil_war(), betrayal(['Metz', 'Strasbourg'], True)),
        5: when(lambda g: g.foreign_war or g.civil_war(), betrayal(['Amiens', 'Lille'], True)),
        6: when(lambda g: g.foreign_war or g.civil_war(), betrayal(['Marseille'], False)),
        7: when(war, lambda g: g.allied_return(['fleet'])),
        8: once('subsidies', lambda g: (g.give(R, 500), setattr(g, 'english_subsidies', True))),
        9: riot('Montpellier'), 10: riot('Brest'), 11: riot('Nantes'),
        12: catholic_back(rrevolt('Cholet'))}),
    'commune': (econ_mod(0, 1, 2), {
        2: track('commune', -1), 3: track('commune', +2), 4: lambda g: g.temp_army(),
        5: bread, 6: bread, 7: seq(track('commune', +2), fame(GOV, +1)),
        8: seq(lambda g: g.paris_neutral(), gov_pay(200)),
        9: seq(track('commune', -1), track('economy', +2), fame(SC, +1), fame(MT, +1), fame(GOV, +1)),
        10: seq(lambda g: g.give(SC, 500), bonus(('paris_action', GOV), 2), track('economy', +2)),
        11: when(lambda g: g.holder('collot_dherbois') == SC,
                 seq(lambda g: g.commune_rise(SC, force=True), track('commune', +3))),
        12: seq(lambda g: g.paris_neutral(), gov_pay(500), fame(GOV, -1),
                lambda g: g.commune_rise(None, force=True))}),
}
