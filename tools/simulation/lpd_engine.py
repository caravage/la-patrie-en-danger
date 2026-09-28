# -*- coding: utf-8 -*-
"""Moteur de regles complet de "La Revolution francaise : la patrie en danger".
Negociations (6.1) volontairement exclues : pas d'alliances, pas de dons
d'argent, pas d'objectifs communs. Chaque courant est joue par une IA
heuristique (voir la section IA en bas de fichier)."""
import random
from collections import defaultdict

from lpd_data import (R, F, M, G, MT, SC, GOV, CURRENTS, SHORT, REGIONS, ADJ, VENDEE,
                      INITIAL_CONTROL, PERSO, FACTION, GENERALS, NEVER_MILITARY_COUP,
                      TREASURY, TREASURY_GOV, ASSEMBLY, TRACK_START, FAME_START, table,
                      p_result, level, LAWS, HS_REGIMES, OFFICIAL, OUTLAW_CURRENTS,
                      ARRESTABLE, LAW_PROPOSERS, LAW_VOTE, DEPUTY_SWITCH, CRITICISM,
                      PROVISIONAL, DEPUTY_TARGETS, VICTORY_FAMILY, ALSO_RANS, ALLIED,
                      REGULARS, CATHOLIC, VENDEE_ROUTE)
from lpd_events import EVENTS

IDX = {c: i for i, c in enumerate(CURRENTS)}
REVOLUTIONARY = ('regular', 'volunteer', 'temp')
ENEMY = ('allied', 'catholic')

# --- Preferences des IA (derivees des fiches "tendances") -------------------
# valeur par point de piste
PREF = {
    R:  {'coalition': 0.5, 'clergy': 0.6, 'commune': 0.1, 'economy': 0.1},
    F:  {'coalition': -0.4, 'clergy': -0.2, 'commune': -0.7, 'economy': -0.3},
    M:  {'coalition': -0.1, 'clergy': -0.1, 'commune': -0.3, 'economy': -0.5},
    G:  {'coalition': 0.3, 'clergy': 0.0, 'commune': -0.3, 'economy': -0.2},
    MT: {'coalition': 0.2, 'clergy': 0.15, 'commune': 0.6, 'economy': -0.1},
    SC: {'coalition': 0.2, 'clergy': 0.2, 'commune': 0.8, 'economy': 0.2},
}
# interet de c quand d gagne un point (Renommee/VP)
REL = {
    R:  {F: -0.2, M: -0.2, G: -0.3, MT: -0.3, SC: -0.3},
    F:  {R: -0.2, M: -0.3, G: -0.6, MT: -0.6, SC: -0.6},
    M:  {R: -0.2, F: -0.3, G: -0.5, MT: -0.5, SC: -0.5},
    G:  {R: -0.3, F: -0.6, M: -0.6, MT: -0.2, SC: -0.1},
    MT: {R: -0.3, F: -0.6, M: -0.5, G: -0.3, SC: -0.2},
    SC: {R: -0.3, F: -0.6, M: -0.5, G: -0.4, MT: -0.3},
}


# valeur par niveau de piste (I, II, III) : ce sont les paliers qui comptent
LEVEL_W = {
    R:  {'economy': (0, -1, -2.5), 'commune': (0, 0, 0), 'clergy': (0, 1.5, 4), 'coalition': (0, 0.5, 3)},
    F:  {'economy': (0, -2, -4), 'commune': (0, -1.5, -3.5), 'clergy': (0, -0.3, -1.5), 'coalition': (0, -0.3, -3)},
    M:  {'economy': (0, -2, -4), 'commune': (0, -0.5, -1.5), 'clergy': (0, 0, -1), 'coalition': (0, 0, -1.5)},
    G:  {'economy': (0, -1.5, -3), 'commune': (0, 0, -1), 'clergy': (0, 0, -0.5), 'coalition': (0, 0, 1.5)},
    MT: {'economy': (0, -1, -2), 'commune': (0, 1.5, 3), 'clergy': (0, 0, 0.8), 'coalition': (0, 0, 0.8)},
    SC: {'economy': (0, -0.5, -1), 'commune': (0, 2, 4), 'clergy': (0, 0, 0.8), 'coalition': (0, 0, 0.8)},
}


def track_value(c, tracks, regime):
    v = 0.0
    for t, x in tracks.items():
        v += PREF[c][t] * x * 0.3
        w = LEVEL_W[c][t]
        if c == G and t == 'coalition' and regime != 'Legislative':
            w = (0, 0, -1)
        if c == G and t == 'commune' and regime == 'Legislative':
            w = (0, 0.5, 1)
        v += w[level(x) - 1]
    return v


LAW_FR = {'maximum': 'Maximum des prix et salaires', 'free_prices': 'Loi économique n° 2',
          'containment': 'Limitation des assignats', 'anti_emigrants': 'Lutte contre les émigrés',
          'confiscation': 'Confiscation des biens', 'safety': 'Sûreté & abolition',
          'usages': 'Suppression des usages', 'nat_goods': 'Distribution des biens nationaux',
          'worship': 'Libertés du culte', 'civic': 'Loi civique', 'war': 'Déclaration de guerre',
          'conscription': 'Conscription', 'levee': 'Levée en masse', 'fatherland': 'Patrie en danger',
          'outlaw_hebertists': 'Hors-la-loi : hébertistes', 'outlaw_merciful': 'Hors-la-loi : indulgents',
          'outlaw_terrorists': 'Hors-la-loi : terroristes', 'trial': 'Procès de Louis XVI'}
TRACK_FR = {'economy': 'Économie', 'commune': 'Commune', 'clergy': 'Clergé', 'coalition': 'Coalisés'}


def law_label(law):
    cost, fm, tracks, _ = LAWS[law]
    bits = ['%s %+d' % (TRACK_FR[t], d) for t, d in tracks.items()]
    if fm:
        bits.insert(0, 'Renommée %+d' % fm)
    return '%s (%s)' % (LAW_FR[law], ', '.join(bits)) if bits else LAW_FR[law]


class GameOver(Exception):
    pass


class NeedInput(Exception):
    """Le moteur attend une decision du joueur humain (voir Game.ask)."""
    def __init__(self, question):
        Exception.__init__(self, question['key'])
        self.question = question


class Game:
    def __init__(self, seed=0, scenario='HS', verbose=False, rules='FR', human=None, answers=()):
        self.rng = random.Random(seed)
        self.human = human          # courant joue par un humain (None : 6 IA)
        self.answers = list(answers)  # decisions deja prises, rejouees dans l'ordre
        self.answer_i = 0
        self.rules = rules  # 'FR' : livret francais de 1995 ; 'EN' : Decimal Version 1.0
        self.seed = seed
        self.scenario = scenario
        self.verbose = verbose
        self.lines = []
        self.turn = 0
        self.regime = 'Legislative'
        self.prev_regime = None
        self.regime_turn = 1
        self.regime_history = [(1, 'Legislative')]
        self.gov_holder = F
        self.gov_partner = None
        self.sole_power_until = 0
        self.fame = dict(FAME_START)
        self.tracks = dict(TRACK_START)
        self.control = {r: INITIAL_CONTROL.get(r) for r in REGIONS}
        self.coal = set()
        self.revolt = {'Bourges'}
        self.commune_raised = False
        self.commune_ctrl = None
        self.money = dict(TREASURY)
        self.gov_money = TREASURY_GOV
        self.spent = 0
        self.spent_by = defaultdict(int)
        self.p = {pid: dict(holder=d['start'], status='free', loc=None, used=False, outlaw=False,
                            ret=0) for pid, d in PERSO.items()}
        self.armies = {}
        for aid, reg in REGULARS.items():
            self.armies[aid] = dict(kind='regular', region=reg, step=0, pinned=False, rebel=False)
        self.allied_state = {aid: 'pending' for aid in ALLIED}
        self.catholic_state = {aid: 'unraised' for aid in CATHOLIC}
        self.vol_n = 0
        self.deputies = dict(ASSEMBLY)
        self.aside = {c: 0 for c in CURRENTS}
        self.switched = []  # (from, to, n)
        self.king = 'free'   # free / prison / dead / kidnapped
        self.trials = 0
        self.gov_guilty_first = None
        self.auto_trial = False
        self.temp_outlaw = {}
        self.coup_outlaw = set()
        self.faction_outlaw = set()
        self.thermidor_outlaw = None
        self.mt_outlawed_prev = False
        self.rejected_terror = 0
        self.rejected_wrath = 0
        self.next_election = 4
        self.election_period = 4
        self.foreign_war = False
        self.war_declared_law = False
        self.war_entered = False
        self.convention_or_terror = False
        self.clergy_iii = False
        self.conscription = False
        self.levee_pending = 0
        self.fatherland = False
        self.bonus = defaultdict(int)
        self.end_checks = []
        self.used_once = set()
        self.gironde_ousted = False
        self.feuillant_coup_done = False
        self.royalist_coup_used = False
        self.marais_ffr_coup_ok = False
        self.english_subsidies = False
        self.froi_variant = None
        self.objectives = {}
        self.popular_coup_done = self.military_coup_done = self.limited_coup_done = False
        self.coup_log = []
        self.laws_passed = defaultdict(int)
        self.events_log = []
        self.order = list(CURRENTS)
        self.winner = None
        self.ended_early = False
        self.stats = defaultdict(int)
        self.fame_history = []
        self.regions_history = []

    # ================================================================ humain
    def ask(self, key, prompt, options, multi=False):
        """Renvoie la prochaine decision enregistree, sinon suspend la partie.
        options : liste de dict(label=..., ...) ; reponse : index (ou liste
        de [index, nombre de jets] si multi)."""
        if self.answer_i < len(self.answers):
            a = self.answers[self.answer_i]
            self.answer_i += 1
            return a
        raise NeedInput(dict(key=key, prompt=prompt, options=options, multi=multi))

    def ask_yes_no(self, key, prompt, yes='Oui', no='Non'):
        return self.ask(key, prompt, [dict(label=yes), dict(label=no)]) == 0

    # ================================================================ utils
    def log(self, msg):
        line = 'T%d %-11s| %s' % (self.turn, self.regime, msg)
        self.lines.append(line)
        if self.verbose:
            print(line)

    def d6(self):
        return self.rng.randint(1, 6)

    def k(self):
        return level(self.tracks['economy'])

    def turns_left(self):
        return 8 - self.turn

    def lvl(self, t):
        return level(self.tracks[t])

    def once(self, key):
        if key in self.used_once:
            return False
        self.used_once.add(key)
        return True

    def reset_once(self, key):
        self.used_once.discard(key)

    def add_bonus(self, key, v):
        self.bonus[key] += v

    def status(self, pid):
        return self.p[pid]['status']

    def holder(self, pid):
        return self.p[pid]['holder']

    def alive(self, pid):
        return self.p[pid]['status'] != 'dead'

    def available(self, pid):
        return self.p[pid]['status'] not in ('dead', 'prison')

    def free_on_map(self, pid):
        return self.p[pid]['status'] == 'free' and self.p[pid]['loc'] is not None

    def perso_of(self, c, statuses=('free',)):
        return [pid for pid, s in self.p.items() if s['holder'] == c and s['status'] in statuses]

    # ------------------------------------------------------------ fame / tracks
    def fame_adj(self, who, d, why=''):
        if who is None or d == 0:
            return
        if who == GOV and self.regime == 'Directorate':
            pass
        old = self.fame[who]
        self.fame[who] = max(1, min(20, old + d))
        if self.fame[who] != old:
            self.log('Fame %s %+d -> %d (%s)' % (SHORT[who], d, self.fame[who], why))

    def track(self, t, d, why=''):
        if d == 0:
            return
        if t == 'coalition' and self.foreign_war and why != 'event':
            return  # 9.2 : pendant la guerre, la piste ne bouge qu'aux evenements
        old = self.tracks[t]
        self.tracks[t] = max(1, min(20, old + d))
        if self.tracks[t] != old:
            self.log('%s %+d -> %d (%s)' % (t, d, self.tracks[t], why))
        if t == 'clergy' and self.tracks['clergy'] >= 17:
            self.clergy_iii = True
        if t == 'coalition':
            if not self.foreign_war and self.tracks['coalition'] >= 17:
                self.declare_war('Coalition track')
            elif self.foreign_war and self.tracks['coalition'] <= 8:
                self.end_war('Coalition track level I')

    def pay(self, c, amount):
        if amount <= 0:
            return True
        if c == GOV:
            if self.gov_money < amount:
                return False
            self.gov_money -= amount
        else:
            if self.money[c] < amount:
                return False
            self.money[c] -= amount
        self.spent += amount
        self.spent_by[c] += amount
        return True

    def give(self, c, amount):
        self.money[c] += amount

    def gov_pay(self, amount):
        self.gov_money = max(0, self.gov_money - amount)

    # ------------------------------------------------------------ roll
    def roll(self, who, fame, n=1, pref='ABC'):
        best = None
        for _ in range(max(1, n)):
            d1, d2 = self.d6(), self.d6()
            res = table(d1 + d2, fame)
            dbl = -1 if d1 == d2 == 1 else (1 if d1 == d2 == 6 else 0)
            key = (pref.index(res), -dbl)
            if best is None or key < best[0]:
                best = (key, res, dbl, d1 + d2)
        _, res, dbl, s = best
        if dbl and who is not None:
            self.fame_adj(who, dbl, 'double %d' % (1 if dbl < 0 else 6))
        return res

    # ------------------------------------------------------------ status
    def outlawed(self, c):
        if c in OUTLAW_CURRENTS[self.regime] or c in self.coup_outlaw:
            return True
        if self.temp_outlaw.get(c, 0) >= self.turn:
            return True
        if self.regime == 'Thermidor' and c == self.thermidor_outlaw:
            return True
        if self.regime == 'Directorate' and c == MT and self.mt_outlawed_prev:
            return True
        return False

    def official(self, c):
        return c in OFFICIAL[self.regime] and not self.outlawed(c) and not (
            self.regime == 'Directorate' and c == MT and self.mt_outlawed_prev)

    def p_outlaw(self, pid):
        s = self.p[pid]
        return self.outlawed(s['holder']) or s['outlaw']

    def arrestable(self, pid):
        if pid == 'louis_xvi':
            return False
        return self.p_outlaw(pid) or pid in ARRESTABLE[self.regime]

    def faction_outlawed(self, fac):
        return fac in self.faction_outlaw

    def paris_holder(self):
        if self.commune_raised:
            return self.commune_ctrl
        return self.control['Paris']

    def effective_control(self, r):
        if r == 'Paris' and self.commune_raised:
            return self.commune_ctrl
        return self.control[r]

    def regions_of(self, c):
        return [r for r in REGIONS if self.effective_control(r) == c]

    def neutral_regions(self):
        return [r for r in REGIONS if self.effective_control(r) is None and r not in self.coal]

    def armies_in(self, r, kinds):
        return [a for a, s in self.armies.items() if s['region'] == r and s['kind'] in kinds]

    def rev_armies(self):
        return [a for a, s in self.armies.items() if s['kind'] in REVOLUTIONARY]

    def enemy_armies(self):
        return [a for a, s in self.armies.items() if s['kind'] in ENEMY]

    def catholic_on_map(self):
        return any(s['kind'] == 'catholic' for s in self.armies.values())

    def civil_war(self):
        if len(self.revolt) >= 4:
            return True
        return any(s['kind'] == 'catholic' and not s.get('hiding') for s in self.armies.values())

    def paris_threatened(self):
        near = {'Paris'} | ADJ['Paris']
        for s in self.armies.values():
            if s['kind'] == 'allied' and s['region'] in near:
                return True
            if s['kind'] == 'catholic' and s['region'] == 'Paris':
                return True
        roy = sum(1 for r in REGIONS if self.control[r] == R) + len(self.coal)
        return roy >= 12

    def paris_occupied(self):
        return bool(self.armies_in('Paris', ENEMY)) and not self.armies_in('Paris', REVOLUTIONARY) \
            and not self.commune_raised

    def objective_hit(self, who, kind, target):
        o = self.objectives.get(who)
        if o and o['kind'] == kind and o['target'] == target:
            o['done'] = True
        for c, o in self.objectives.items():
            if c != who and o['kind'] == kind and o['target'] == target and kind in (
                    'revolt', 'suppress', 'commune_raise', 'commune_suppress', 'law', 'regime'):
                o['done'] = True

    # ================================================================ region events
    def ev_neutral(self, r):
        if r in self.revolt or r in self.coal:
            return
        if r == 'Paris' and self.commune_raised:
            return
        if self.control[r] is not None:
            self.log('Event: %s becomes neutral (was %s)' % (r, SHORT[self.control[r]]))
        self.control[r] = None

    def ev_neutral_revolt(self, r):
        if r in self.revolt or self.armies_in(r, list(REVOLUTIONARY) + list(ENEMY)) or r == 'Paris':
            return
        if r in self.coal:
            return
        self.control[r] = None
        self.revolt.add(r)
        self.log('Event: neutral revolt in %s' % r)

    def ev_control_revolt(self, c, r):
        if r in self.revolt:
            return
        if r == 'Paris':
            return
        if self.armies_in(r, list(REVOLUTIONARY) + list(ENEMY)) and not (
                c == R and r in self.coal):
            return
        if r in self.coal and c != R:
            return
        self.revolt.add(r)
        self.control[r] = c
        self.log('Event: %s revolt in %s (controls it)' % (SHORT[c], r))
        self.objective_hit(c, 'revolt', r)

    def ev_royalist_riot(self, r):
        if self.control[r] != R:
            self.ev_neutral(r)

    def ev_control(self, c, r):
        if r in self.revolt or r in self.coal:
            return
        self.control[r] = c
        self.log('Event: %s controls %s' % (SHORT[c], r))

    def ev_controller_pays(self, r, amount, exempt=None):
        c = self.effective_control(r)
        if c and c != exempt:
            amount *= 1
            paid = min(self.money[c], amount)
            self.money[c] -= paid
            self.log('Event: %s pays %d for %s' % (SHORT[c], paid, r))

    def paris_neutral(self):
        if self.commune_raised:
            self.commune_ctrl = None
        elif 'Paris' not in self.revolt:
            self.control['Paris'] = None
        self.log('Event: Paris becomes neutral')

    def commune_rise(self, c, force=False):
        if self.paris_occupied():
            return
        if self.commune_raised and not force:
            return
        self.commune_raised = True
        self.commune_ctrl = c
        self.log('Commune raised (%s)' % (SHORT[c] if c else 'neutral'))
        self.objective_hit(c, 'commune_raise', 'Paris')
        self.stats['commune_raised'] += 1

    def commune_calm(self):
        if self.commune_raised:
            self.commune_raised = False
            self.control['Paris'] = self.commune_ctrl if self.commune_ctrl else self.control['Paris']
            self.commune_ctrl = None
            self.log('Commune calmed down')

    def kill(self, pid):
        if self.p[pid]['status'] != 'dead':
            self.p[pid]['status'] = 'dead'
            self.p[pid]['loc'] = None
            self.log('%s dies' % PERSO[pid]['label'])

    def kill_prisoners(self, currents, spare_king=True):
        for pid, s in self.p.items():
            if s['status'] == 'prison' and s['holder'] in currents:
                if pid == 'louis_xvi' and spare_king:
                    continue
                self.kill(pid)
        if not spare_king and self.king == 'prison':
            self.king = 'dead'

    def free_all_prisoners(self):
        for pid, s in self.p.items():
            if s['status'] == 'prison' and pid != 'louis_xvi':
                s['status'] = 'free'
                s['loc'] = None

    def exile(self, pids):
        for pid in pids:
            if self.p[pid]['status'] in ('free', 'fled'):
                self.p[pid]['status'] = 'exiled'
                self.p[pid]['loc'] = None
                self.log('%s exiled' % PERSO[pid]['label'])

    def switch_event(self, pid, c):
        if self.alive(pid) and c in ({PERSO[pid]['main']} | PERSO[pid]['secondary']):
            self.p[pid]['holder'] = c
            self.log('%s switches to %s (event)' % (PERSO[pid]['label'], SHORT[c]))

    def move_deputies(self, src, dst, half_up=True):
        n = self.deputies[src]
        mv = (n + 1) // 2 if half_up else n // 2
        self.deputies[src] -= mv
        self.deputies[dst] += mv

    def froi_split_marais(self):
        n = self.deputies[M]
        other = SC if self.gov_holder == MT else MT
        self.deputies[M] = 0
        self.deputies[self.gov_holder] += (n + 1) // 2
        self.deputies[other] += n // 2

    def temp_army(self):
        self.vol_n += 1
        self.armies['temp%d' % self.vol_n] = dict(kind='temp', region='Paris', step=0, pinned=False, rebel=False)

    def discard_rev_army(self, regions, strict=False):
        cands = self.rev_armies()
        if not cands:
            return
        if regions is None:
            # choix du Royaliste : l'armee la plus genante (celle sur la route de Paris)
            a = self.rng.choice(cands)
        else:
            here = [a for a in cands if self.armies[a]['region'] in regions]
            if here:
                a = here[0]
            elif strict:
                return
            else:
                tgt = regions[0]
                a = min(cands, key=lambda x: self.dist(self.armies[x]['region'], tgt))
        self.log('Event: revolutionary army %s discarded (%s)' % (a, self.armies[a]['region']))
        del self.armies[a]

    def discard_allied(self, ids):
        for aid in ids:
            if aid in self.armies:
                del self.armies[aid]
                self.log('Event: allied %s leaves the war' % aid)
            if self.allied_state.get(aid) in ('pending', 'onmap', 'available'):
                self.allied_state[aid] = 'discarded'

    def allied_return(self, ids=None):
        ids = ids or ['cobourg', 'wurmser', 'brunswick']
        for aid in ids:
            if self.allied_state.get(aid) == 'eliminated':
                self.allied_state[aid] = 'available'
                return

    def catholic_return(self):
        for aid in CATHOLIC:
            if self.catholic_state[aid] == 'eliminated':
                self.catholic_state[aid] = 'available'
                return

    def ev_retreat(self):
        for a in self.rev_armies():
            s = self.armies[a]
            if s['region'] == 'Lille':
                s['region'] = 'Amiens'
                return
            if s['region'] == 'Amiens':
                s['region'] = 'Paris'
                return

    def gov_decide(self, key, yes, no):
        h = self.gov_holder
        # simulation grossiere de l'effet : la faction au pouvoir compare
        before = (self.fame[GOV], self.tracks['commune'], self.gov_money)
        u_yes = self._eval_branch(h, yes)
        u_no = self._eval_branch(h, no)
        (yes if u_yes >= u_no else no)(self)
        self.log('Gov decides %s: %s' % (key, 'yes' if u_yes >= u_no else 'no'))

    def assembly_decide(self, key, yes, no):
        votes = {'yes': 0, 'no': 0}
        for c in CURRENTS:
            if self.deputies[c] <= 0:
                continue
            u = self._eval_branch(c, yes) - self._eval_branch(c, no)
            votes['yes' if u >= 0 else 'no'] += self.deputies[c]
        (yes if votes['yes'] > votes['no'] else no)(self)
        self.log('Assembly decides %s: %s' % (key, 'yes' if votes['yes'] > votes['no'] else 'no'))

    def _eval_branch(self, c, fn):
        """Applique fn sur une copie legere pour mesurer son effet pour c."""
        saved = (dict(self.fame), dict(self.tracks), self.gov_money, dict(self.control),
                 self.commune_ctrl, self.verbose, list(self.lines), self.commune_raised,
                 self.foreign_war)
        self.verbose = False
        fn(self)
        u = 0.0
        for who in CURRENTS:
            d = self.fame[who] - saved[0][who]
            u += d * (1.2 if who == c else self.rel(c, who))
        dg = self.fame[GOV] - saved[0][GOV]
        u += dg * (0.6 if self.gov_holder == c else -0.1)
        u += track_value(c, self.tracks, self.regime) - track_value(c, saved[1], self.regime)
        if self.gov_holder == c:
            u += (self.gov_money - saved[2]) / 400.0
        for r in REGIONS:
            if self.control[r] != saved[3][r]:
                if saved[3][r] == c:
                    u -= 1.5
                if self.control[r] == c:
                    u += 1.5
        (self.fame, self.tracks, self.gov_money, self.control, self.commune_ctrl, self.verbose,
         self.lines, self.commune_raised, self.foreign_war) = saved
        return u

    # ================================================================ war
    def declare_war(self, why):
        if self.foreign_war:
            return
        self.foreign_war = True
        self.war_entered = False
        self.tracks['coalition'] = 20
        self.log('*** FOREIGN WAR declared (%s)' % why)
        self.stats['war_turn'] = self.stats['war_turn'] or self.turn

    def end_war(self, why):
        if not self.foreign_war:
            return
        self.foreign_war = False
        self.log('*** Foreign peace (%s)' % why)
        if not self.civil_war():
            self.conscription = False
        if self.fatherland and self.fatherland == 'allied':
            self.fatherland = False

    # ================================================================ game loop
    def play(self):
        try:
            for t in range(1, 9):
                self.turn = t
                self.play_turn()
            self.final_victory()
        except GameOver:
            pass
        return self

    def play_turn(self):
        self.start_turn()
        self.random_events()
        self.turn_order()
        self.plan_and_place()
        self.personality_actions()
        self.regional_actions()
        self.political_phase()
        self.patriot_phase()
        self.military_phase()
        self.interphase()
        self.fame_history.append(dict(self.fame))
        self.regions_history.append({c: len(self.regions_of(c)) for c in CURRENTS})

    def start_turn(self):
        self.bonus = defaultdict(int)
        self.end_checks = []
        self.switched = []
        self.popular_coup_done = self.military_coup_done = self.limited_coup_done = False
        for pid, s in self.p.items():
            s['used'] = False
            if s['status'] == 'fled' and s['ret'] <= self.turn:
                s['status'] = 'free'
            if s['status'] == 'exiled' and not self.foreign_war:
                s['status'] = 'free'
            s['loc'] = None
        for a in [a for a, s in self.armies.items() if s['kind'] == 'temp']:
            del self.armies[a]
        for a in self.armies.values():
            a['pinned'] = False
            a.pop('hiding', None)
        if self.english_subsidies and self.tracks['coalition'] >= 15 and self.turn > 1:
            pass  # verse a l'Interphase
        self.log('==================== TURN %d (%s) ====================' % (self.turn, self.regime))

    # ================================================================ events
    def random_events(self):
        table_set = EVENTS[self.regime]
        for cat in ('economy', 'politics', 'counter', 'commune'):
            if cat == 'commune' and self.paris_occupied():
                continue
            mod_fn, tbl = table_set[cat]
            s = self.d6() + self.d6() + mod_fn(self)
            s = max(2, min(12, s))
            self.events_log.append((self.turn, self.regime, cat, s))
            self.log('Event %s roll %d' % (cat, s))
            fn = tbl.get(s)
            if fn:
                fn(self)
        if self.foreign_war and self.lvl('coalition') == 1:
            self.end_war('Coalition level I')

    # ================================================================ order
    def turn_order(self):
        def key(c):
            return (-(self.fame[c] + len(self.regions_of(c))), -self.fame[c], self.rng.random())
        self.order = sorted(CURRENTS, key=key)
        self.log('Order: ' + ' > '.join(SHORT[c] for c in self.order))

    # ================================================================ placement & plan
    def compute_threat(self):
        v = self.vp()
        self.threat = {c: 0.0 for c in CURRENTS}
        self.threat[R] = max(0.0, v[R] - 15) * 0.15
        w, _, _, _ = self.outcome()
        if w != R:
            self.threat[w] += 0.25

    def rel(self, c, d):
        if c == d or d is None:
            return 0.0
        return REL[c].get(d, 0) - self.threat.get(d, 0) if hasattr(self, 'threat') else REL[c].get(d, 0)

    def plan_and_place(self):
        self.compute_threat()
        self.objectives = {}
        self.plans = {}
        # Louis XVI reste a Paris
        lx = self.p['louis_xvi']
        if lx['status'] == 'free':
            lx['loc'] = 'Paris'
        self.plan_government()
        for c in self.order:
            self.plan_current(c)

    # ================================================================ personality actions
    def personality_actions(self):
        self.gov_arrests()
        for c in self.order:
            self.do_removals(c)
        for c in self.order:
            self.do_persuasions(c)

    def gov_arrests(self):
        h = self.gov_holder
        targets = self.gov_plan.get('arrests', [])
        for pid, n in targets:
            s = self.p[pid]
            if s['status'] != 'free' or s['loc'] is None or not self.arrestable(pid):
                continue
            cost = 100 * self.k() * n
            if cost > self.gov_money - self.maint_reserve() or not self.pay(GOV, cost):
                continue
            fame = self.fame[GOV] + self.arrest_mod(pid)
            res = self.roll(GOV, fame, n)
            self.stats['arrest_attempts'] += 1
            harsh = self.regime in ('Terror', 'Wrath', 'Prairial')
            if res == 'A' or (res == 'B' and harsh):
                self.imprison(pid, 'arrested by Gov (%s)' % SHORT[h])
                self.objective_hit(GOV, 'arrest', pid)
                self.stats['arrests'] += 1
            elif res == 'B':
                self.flee(pid, 'flees arrest')

    def arrest_mod(self, pid):
        s = self.p[pid]
        r = s['loc']
        m = 0
        if self.effective_control(r) == s['holder']:
            m -= 4
        if r in PERSO[pid]['influence']:
            m -= 2
        if self.p_outlaw(pid) and r == 'Paris':
            m += 5
        m += self.bonus['gov_police'] + self.bonus['gov_all']
        m += self.bonus[('arrest', pid)]
        if self.regime in ('Terror', 'Prairial') or (self.regime == 'Prairial' and self.gov_holder == MT):
            if any(self.p[t]['loc'] == r and self.p[t]['status'] == 'free' for t in FACTION
                   if FACTION[t] == 'terrorist'):
                m += 2
        if self.regime in ('Wrath', 'Mercy') or (self.regime == 'Prairial' and self.gov_holder == SC):
            if any(self.p[t]['loc'] == r and self.p[t]['status'] == 'free' for t in FACTION
                   if FACTION[t] in ('terrorist', 'hebertist')):
                m += 2
        if self.bonus['arrest_terrorists'] and s['holder'] in (SC, MT) and self.p_outlaw(pid):
            m += 2
        if r == 'Paris':
            m += self.bonus[('paris_action', GOV)]
        return m

    def imprison(self, pid, why):
        s = self.p[pid]
        s['status'] = 'prison'
        s['loc'] = None
        self.log('%s (%s) imprisoned: %s' % (PERSO[pid]['label'], SHORT[s['holder']], why))

    def flee(self, pid, why):
        s = self.p[pid]
        if s['status'] == 'free':
            s['status'] = 'fled'
            s['ret'] = self.turn + 1
            s['loc'] = None
            self.log('%s (%s) %s' % (PERSO[pid]['label'], SHORT[s['holder']], why))

    def do_removals(self, c):
        if self.official(c):
            return
        for pid, n in self.plans[c].get('removals', []):
            s = self.p[pid]
            if pid == 'louis_xvi' or s['status'] != 'free' or s['loc'] is None or self.effective_control(s['loc']) != c:
                continue
            if not self.pay(c, 100 * self.k() * n):
                continue
            fame = self.fame[c] + self.cur_bonus(c) - (2 if s['loc'] in PERSO[pid]['influence'] else 0)
            if self.roll(c, fame, n) in 'AB':
                self.flee(pid, 'expelled from %s by %s' % (s['loc'], SHORT[c]))

    def do_persuasions(self, c):
        for pid, n in self.plans[c].get('persuade', []):
            s = self.p[pid]
            if s['status'] in ('dead', 'exiled') or s['holder'] == c:
                continue
            if pid == 'louis_xvi' and self.king == 'kidnapped':
                continue
            cost = 100 * self.k() * n
            if not self.pay(c, cost):
                continue
            mod = self.cur_bonus(c) + self.bonus[('persuade', c)]
            if c != PERSO[pid]['main']:
                mod -= 2
            res = self.roll(c, self.fame[c] + mod, n)
            self.stats['persuade_attempts'] += 1
            if res == 'A':
                old = s['holder']
                s['holder'] = c
                self.log('%s switches %s -> %s' % (PERSO[pid]['label'], SHORT[old], SHORT[c]))
                self.stats['persuade_ok'] += 1
                self.objective_hit(c, 'persuade', pid)
                if s['status'] == 'prison' and self.outlawed(old) and not self.outlawed(c):
                    s['status'] = 'free'
                    s['loc'] = None
                if s['status'] == 'free' and s['loc'] is None and c in self.order:
                    pass
            elif res == 'B' and s['status'] == 'free':
                self.flee(pid, 'leaves the map (persuasion B)')

    def cur_bonus(self, c):
        b = 0
        if c == R:
            b += {1: 0, 2: 1, 3: 2}[self.lvl('clergy')]
        if c == SC:
            b += {1: 0, 2: 1, 3: 2}[self.lvl('commune')]
        if c == MT and self.lvl('commune') == 3:
            b += 1
        return b

    # ================================================================ regional actions
    def regional_actions(self):
        for kind in ('plot', 'revolt', 'suppress', 'commune'):
            if kind == 'suppress':
                self.gov_suppressions()
            for c in self.order:
                for act in self.plans[c]['regional']:
                    if act['kind'] == kind or (kind == 'commune' and act['kind'].startswith('commune')):
                        self.do_regional(c, act)

    def act_pids_ok(self, c, act):
        return all(self.p[pid]['status'] == 'free' and self.p[pid]['loc'] == act['region']
                   and self.p[pid]['holder'] == c and not self.p[pid]['used'] for pid in act['pids'])

    def regional_mod(self, c, act):
        r = act['region']
        m = self.cur_bonus(c)
        m += sum(2 for pid in act['pids'] if r in PERSO[pid]['influence'])
        if r == 'Paris':
            m += self.bonus[('paris_action', c)]
        if c == R and r in self.coal:
            m += 2
        return m

    def do_regional(self, c, act):
        if not self.act_pids_ok(c, act):
            return
        r, kind, n = act['region'], act['kind'], act['n']
        mod = self.regional_mod(c, act)
        if kind == 'plot':
            if r in self.revolt or r in self.coal or self.control[r] == c:
                return
            if r == 'Paris' and self.commune_raised:
                return
            if self.control[r] is None:
                mod += 2
            cost = 100
        elif kind == 'revolt':
            if self.official(c) or r in self.revolt or r == 'Paris' and not (c == R and r in self.coal):
                return
            if self.armies_in(r, list(REVOLUTIONARY) + list(ENEMY)) and not (c == R and r in self.coal):
                return
            if REGIONS[r][1]:
                mod += 2
            cost = 150
        elif kind == 'suppress':
            if r not in self.revolt or self.armies_in(r, ['allied']):
                return
            mod -= 2
            cost = 150
        elif kind == 'commune_raise':
            if self.commune_raised or self.paris_occupied():
                return
            mod += self.commune_penalty(c)
            cost = 200
        elif kind == 'commune_suppress':
            if not self.commune_raised:
                return
            mod += self.commune_penalty(c) - 2
            cost = 200
        else:
            return
        if not self.pay(c, cost * self.k() * n):
            return
        for pid in act['pids']:
            self.p[pid]['used'] = True
        pref = 'ABC'
        if kind == 'commune_raise' and self.lvl('commune') == 2:
            pref = 'ABC'
        res = self.roll(c, self.fame[c] + mod, n, pref)
        self.stats['%s_attempts' % kind] += 1
        self.log('%s %s in %s (x%d, fame %d%+d): %s' % (SHORT[c], kind, r, n, self.fame[c], mod, res))
        if kind == 'plot':
            if res == 'A':
                self.control[r] = c
                self.objective_hit(c, 'plot', r)
                self.stats['plots_ok'] += 1
            elif res == 'B':
                self.control[r] = None
        elif kind == 'revolt':
            if res in 'AB':
                self.revolt.add(r)
                self.control[r] = c if res == 'A' else None
                self.objective_hit(c, 'revolt', r)
                self.stats['revolts_ok'] += 1
        elif kind == 'suppress':
            if res in 'AB':
                self.revolt.discard(r)
                self.control[r] = c if res == 'A' else None
                self.objective_hit(c, 'suppress', r)
        elif kind == 'commune_raise':
            lv = self.lvl('commune')
            if res == 'A' or (res == 'B' and lv == 3):
                self.commune_rise(c)
            elif res == 'B' and lv == 2:
                self.commune_rise(None)
        elif kind == 'commune_suppress':
            lv = self.lvl('commune')
            ok_ctrl = res == 'A' or (res == 'B' and lv == 1)
            ok_neutral = res == 'B' and lv == 2
            if ok_ctrl or ok_neutral:
                self.commune_raised = False
                self.commune_ctrl = None
                self.control['Paris'] = c if ok_ctrl else None
                self.log('Commune suppressed by %s' % SHORT[c])
                self.objective_hit(c, 'commune_suppress', 'Paris')

    def commune_penalty(self, c):
        if c == SC:
            return 0
        if c == MT:
            return 0 if (self.regime == 'FROI' and self.froi_variant == MT) else -2
        if c == G:
            return -4
        if c == F and self.bonus['feuillant_commune']:
            return 0
        if c == R and self.regime in ('Directorate', 'Prairial'):
            return 2 if self.bonus['royalist_commune'] else -4
        if c == M and self.regime == 'FROI':
            return -3
        return None

    def can_commune(self, c):
        return self.commune_penalty(c) is not None

    def gov_suppressions(self):
        for r, n in self.gov_plan.get('suppress', []):
            if r not in self.revolt or self.armies_in(r, ['allied', 'catholic']):
                continue
            if 150 * self.k() * n > self.gov_money - self.maint_reserve() or not self.pay(GOV, 150 * self.k() * n):
                continue
            mod = -2 + self.bonus['gov_police'] + self.bonus['gov_all']
            if self.regime in ('Terror',) and any(self.p[t]['loc'] == r for t in FACTION if FACTION[t] == 'terrorist'):
                mod += 2
            res = self.roll(GOV, self.fame[GOV] + mod, n)
            if res in 'AB':
                self.revolt.discard(r)
                self.log('Gov suppresses revolt in %s' % r)
                self.objective_hit(GOV, 'suppress', r)

    # ================================================================ political phase
    def political_phase(self):
        self.check_regime_change()
        self.check_elections()
        if self.regime == 'Directorate':
            self.try_coups(kinds=('limited',))
        if self.regime in DEPUTY_SWITCH:
            for c in self.order:
                self.deputy_persuasion(c)
        if self.regime == 'Legislative':
            self.king_action()
        self.law_phase()

    # ------------------------------------------------------------ deputies
    def deputy_persuasion(self, c):
        pids = [pid for pid in self.perso_of(c) if self.p[pid]['loc'] == 'Paris'
                and not self.p[pid]['used'] and pid != 'louis_xvi']
        if not pids:
            return
        want = self.deputy_want(c)
        if want <= 0 and c != self.human:
            return
        for pid in pids:
            targets = [t for t in DEPUTY_TARGETS[c] if self.switchable(t) > 0 and t != c]
            if not targets:
                return
            tgt = max(targets, key=lambda t: (self.switchable(t), -REL[c].get(t, 0)))
            cost = 100 * self.k()
            if c == self.human:
                if self.money[c] < cost:
                    return
                opts = [dict(label='Retourner des députés %s (%d disponibles)' % (t, self.switchable(t)), cost=cost,
                             p=round(p_result(self.fame[c] + self.bonus[('persuade', c)] + self.cur_bonus(c), 'AB'), 3))
                        for t in targets] + [dict(label='Ne rien faire')]
                i = self.ask('deputies', '%s est à Paris : retourner des députés (%d assignats ; A = 5, B = 3) ?'
                             % (PERSO[pid]['label'], cost), opts)
                if i >= len(targets):
                    return
                tgt = targets[i]
            elif self.money[c] < cost + self.reserve(c) * 0.5 or want * 0.35 < cost * self.mv(c):
                return
            self.pay(c, cost)
            self.p[pid]['used'] = True
            mod = self.bonus[('persuade', c)] + self.cur_bonus(c)
            res = self.roll(c, self.fame[c] + mod, 1)
            n = 5 if res == 'A' else 3 if res == 'B' else 0
            n = min(n, self.switchable(tgt))
            if n:
                self.deputies[tgt] -= n
                self.deputies[c] += n
                self.switched.append((tgt, c, n))
                self.log('%s attracts %d %s deputies' % (SHORT[c], n, SHORT[tgt]))

    def switchable(self, t):
        moved_in = sum(n for (a, b, n) in self.switched if b == t)
        return max(0, self.deputies[t] - moved_in)

    def deputy_want(self, c):
        """Interet a peser dans les votes du tour (lois, confiance)."""
        w = 0.0
        crit = CRITICISM.get(self.regime)
        if crit and c in crit:
            w += 2.0
        if self.official(c):
            w += 1.0
        if c in (R,) and self.regime == 'Legislative':
            w += 0.5
        return w

    # ------------------------------------------------------------ king
    def king_action(self):
        if self.king != 'free' or self.p['louis_xvi']['status'] != 'free':
            return
        h = self.holder('louis_xvi')
        if h == self.human and h in (F, R):
            txt = ('-1 Renommée Gironde, Coalisés -1 (100)' if h == F else '-1 Renommée Feuillant, Coalisés +1 (50)')
            if not self.ask_yes_no('king', 'Action du Roi : %s ?' % txt):
                return
        if h == F:
            if self.pay(F, 100 * self.k()):
                self.fame_adj(G, -1, 'King (Feuillant)')
                self.track('coalition', -1, 'King')
        elif h == R:
            if self.pay(R, 50 * self.k()):
                self.fame_adj(F, -1, 'King (Royalist)')
                self.track('coalition', +1, 'King')

    # ------------------------------------------------------------ laws
    def law_phase(self):
        mode = LAW_PROPOSERS[self.regime]
        if self.rules == 'FR' and self.regime == 'Legislative':
            mode = 'currents'  # VF XV-A2 / VII-E2 : pas de lois du Gouvernement
        proposals = []
        if mode in ('gov', 'both'):
            for law in self.gov_laws():
                proposals.append((GOV, law))
        if mode in ('currents', 'both'):
            for c in self.order:
                if self.official(c):
                    law = self.human_law(c) if c == self.human else self.choose_law(c)
                    if law:
                        proposals.append((c, law))
        if self.auto_trial and self.king == 'prison':
            proposals.insert(0, (GOV, 'trial'))
        proposed = set()
        for who, law in proposals:
            if law in proposed and law != 'civic':
                continue
            if self.regime_changed_this_phase:
                return
            if who == GOV and LAWS[law][0] * self.k() > self.gov_money - self.maint_reserve():
                continue
            proposed.add(law)
            self.vote_law(who, law)

    regime_changed_this_phase = False

    def law_allowed(self, who, law):
        cat = LAWS[law][3]
        reg = self.regime
        if cat in ('privilege', 'clergy') and reg in ('Thermidor', 'Directorate'):
            return False
        if cat == 'privilege' and (who == F or (who == GOV and self.gov_holder == F)):
            return False
        if law == 'war' and (self.foreign_war or self.war_declared_law):
            return False
        if law == 'conscription' and (self.conscription or (self.rules == 'FR' and self.laws_passed['conscription'])
                                      or (self.rules != 'FR' and not (self.foreign_war or self.civil_war()))):
            return False
        if law == 'levee' and reg == 'Legislative':
            return False
        if law == 'fatherland' and (self.fatherland or not self.paris_threatened_strict()):
            return False
        if law == 'outlaw_hebertists' and (who != GOV or reg not in ('Terror', 'Wrath') or 'hebertist' in self.faction_outlaw):
            return False
        if law == 'outlaw_merciful' and (who != GOV or reg != 'Terror' or 'merciful' in self.faction_outlaw):
            return False
        if law == 'outlaw_terrorists' and (who != GOV or reg not in ('Thermidor', 'Directorate') or 'terrorist' in self.faction_outlaw):
            return False
        if law == 'trial':
            if self.king != 'prison' or reg not in PROVISIONAL:
                return False
            if reg == 'Convention' and self.trials >= 1:
                return False
            if reg in ('Thermidor', 'Mercy') and (self.trials >= 2 or not self.gov_guilty_first):
                return False
        return True

    def paris_threatened_strict(self):
        near = {'Paris'} | ADJ['Paris']
        return any(s['kind'] in ENEMY and s['region'] in near for s in self.armies.values())

    def law_effects(self, who, law):
        cost, fm, tracks, cat = LAWS[law]
        eff = {'fame': defaultdict(int), 'tracks': dict(tracks), 'extra': defaultdict(float)}
        owner = self.gov_holder if who == GOV else who
        if fm:
            eff['fame'][GOV if who == GOV else who] += fm
        if law == 'war':
            eff['tracks']['coalition'] = 20 - self.tracks['coalition']
            eff['extra'][R] += 3
            eff['extra'][G] += 2.5 if self.regime == 'Legislative' else 0
            eff['extra'][MT] += 1.0
            eff['extra'][SC] += 1.0
            eff['extra'][F] -= 3
            eff['extra'][M] -= 1.5
        if law in ('conscription', 'levee') and (self.enemy_armies() or self.coal):
            base = (1.5 if law == 'levee' else 1.0) * (1 + len(self.coal) * 0.3)
            for c in CURRENTS:
                if c == R:
                    eff['extra'][R] -= base
                else:
                    eff['extra'][c] += base * (0.5 + self.threat.get(R, 0))
            eff['extra'][self.gov_holder] += base * 0.5
        if law == 'fatherland':
            eff['extra'][self.gov_holder] += 0.5
        if law == 'outlaw_hebertists':
            for pid in ('hebert', 'chaumette'):
                h = self.holder(pid)
                if self.alive(pid):
                    eff['extra'][h] -= 2
        if law == 'outlaw_merciful':
            for pid in ('danton', 'desmoulins'):
                h = self.holder(pid)
                if self.alive(pid):
                    eff['extra'][h] -= 2
        if law == 'outlaw_terrorists':
            for pid in ('barere', 'billaud_varenne', 'collot_dherbois'):
                h = self.holder(pid)
                if self.alive(pid):
                    eff['extra'][h] -= 1.5
        if law == 'trial':
            for c, d in ((SC, 3), (MT, 3), (G, -2), (F, -2)):
                eff['fame'][c] += d
            eff['tracks'] = {'coalition': 5, 'clergy': 5}
            for c in (MT, SC):
                eff['extra'][c] += max(0, 5 - self.deputies[c])
        if self.foreign_war and 'coalition' in eff['tracks'] and law != 'war':
            eff['tracks'].pop('coalition')
        cost = LAWS[law][0] * self.k()
        if cost and cost > self.gov_money:
            b = {'fame': defaultdict(int), 'tracks': {}, 'extra': defaultdict(float)}
            b['fame'][self.gov_holder] -= 5
            b['fame'][GOV] -= 2
            return b
        return eff

    def law_util(self, c, eff):
        u = 0.0
        for who, d in eff['fame'].items():
            if who == GOV:
                u += d * (0.6 if self.gov_holder == c else -0.1)
            else:
                u += d * (1.2 if who == c else self.rel(c, who))
        before = dict(self.tracks)
        after = dict(self.tracks)
        for t, d in eff['tracks'].items():
            after[t] = max(1, min(20, after[t] + d))
        u += track_value(c, after, self.regime) - track_value(c, before, self.regime)
        u += eff['extra'].get(c, 0)
        return u

    def vote_law(self, who, law):
        if not self.law_allowed(who, law):
            return
        proposer = self.gov_holder if who == GOV else who
        if who != GOV:
            if not self.pay(who, 50 * self.k()):
                return
        eff = self.law_effects(who, law)
        mode = LAW_VOTE[self.regime]
        if law == 'trial' and not (self.rules == 'FR' and mode == 'fame'):
            passed = self.trial_vote()
            self.laws_passed['trial'] += 1
            return
        if mode == 'deputies':
            yes = no = 0
            for c in CURRENTS:
                n = self.deputies[c]
                if n <= 0:
                    continue
                u = self.law_util(c, eff) if c != proposer else 1
                if c == self.human and c != proposer:
                    u = 1 if self.ask_yes_no('vote', 'Vote de tes %d députés sur « %s », proposée par %s'
                                             % (n, law_label(law), 'le Gouvernement' if who == GOV else who),
                                             'Pour', 'Contre') else -1
                if u > 0:
                    yes += n
                else:
                    no += n
                if self.fatherland and who == GOV and u <= 0 and self.official(c):
                    self.fame_adj(c, -1, 'Fatherland in Danger opposition')
            passed = yes > no
            if yes == no:
                tb = self.holder('louis_xvi') if (self.regime == 'Legislative' and self.king == 'free') else self.gov_holder
                passed = self.law_util(tb, eff) > 0 or tb == proposer
            self.log('Law %s proposed by %s: %d yes / %d no -> %s' % (
                law, SHORT[who], yes, no, 'PASSED' if passed else 'rejected'))
        else:
            base = self.fame[GOV] if who == GOV else self.fame[who]
            if self.regime == 'Convention':
                base = self.fame[who]
            mod = self.bonus['votes'] + (self.bonus['gov_all'] if who == GOV else 0)
            if law.startswith('outlaw_'):
                mod += self.bonus[('outlaw', {'outlaw_hebertists': 'hebertist', 'outlaw_merciful': 'merciful',
                                             'outlaw_terrorists': 'terrorist'}[law])]
            for c in CURRENTS:
                if c == proposer:
                    rng = 3 if self.commune_raised and self.commune_ctrl == c else (
                        2 if c == M and self.regime != 'Prairial' else (1 if self.official(c) else 0))
                    mod += rng
                    continue
                u = self.law_util(c, eff)
                sgn = 1 if u > 0.2 else (-1 if u < -0.2 else 0)
                if c == self.human and (self.official(c) or (self.commune_raised and self.commune_ctrl == c)):
                    sgn = [1, -1, 0][self.ask('vote', 'Ta position sur « %s », proposée par %s (ton soutien '
                                              'modifie le jet)' % (law_label(law), 'le Gouvernement' if who == GOV else who),
                                              [dict(label='Soutenir'), dict(label="S'opposer"), dict(label='Neutre')])]
                if self.commune_raised and self.commune_ctrl == c:
                    mod += 3 * sgn
                elif c == M and self.regime != 'Prairial' and not self.outlawed(M):
                    mod += 2 * sgn
                elif self.official(c):
                    mod += sgn
                if self.fatherland and who == GOV and sgn < 0 and self.official(c):
                    self.fame_adj(c, -1, 'Fatherland in Danger opposition')
            if who == GOV:
                mod += self.lawmaker_bonus()
            if self.regime == 'FROI' and who == SC and self.froi_variant == SC and self.commune_raised:
                mod += self.lvl('commune')
            res = self.roll(who, base + mod, 1)
            passed = res in 'AB'
            self.log('Law %s proposed by %s (fame %d%+d): %s' % (
                law, SHORT[who], base, mod, 'PASSED' if passed else 'rejected'))
            if not passed:
                self.fame_adj(GOV if who == GOV else who, -1, 'law rejected')
                if who == GOV and self.regime in ('Terror', 'Wrath'):
                    self.rejected_terror += 1
                    if self.regime == 'Wrath':
                        self.rejected_wrath += 1
                    self.stats['rejected_gov_laws'] += 1
                    self.marais_thermidor_option()
                return
            if law == 'trial':
                self.trial_vote()
                self.laws_passed['trial'] += 1
                return
        if not passed:
            return
        # veto royal
        cat = LAWS[law][3]
        if self.regime == 'Legislative' and self.king == 'free' and cat in ('privilege', 'clergy'):
            kh = self.holder('louis_xvi')
            veto_eff = {'fame': defaultdict(int), 'tracks': {'commune': 3, 'clergy': -3}, 'extra': {}}
            if cat == 'clergy':
                veto_eff['fame'][kh] -= 2
            if self.law_util(kh, veto_eff) > self.law_util(kh, eff):
                self.log('King (%s) vetoes %s' % (SHORT[kh], law))
                self.track('commune', 3, 'veto')
                self.track('clergy', -3, 'veto')
                if cat == 'clergy':
                    self.fame_adj(kh, -2, 'veto')
                self.stats['vetoes'] += 1
                return
        cost = LAWS[law][0] * self.k()
        if cost and not self.pay(GOV, cost):
            self.bankruptcy('cannot enact %s' % law)
            return
        self.apply_law(who, law, eff)

    def apply_law(self, who, law, eff):
        self.laws_passed[law] += 1
        self.objective_hit(who, 'law', law)
        for c, d in eff['fame'].items():
            self.fame_adj(c, d, 'law %s' % law)
        for t, d in LAWS[law][2].items():
            self.track(t, d, 'law %s' % law)
        if law == 'war':
            self.war_declared_law = True
            self.declare_war('law')
        elif law == 'conscription':
            self.conscription = True
        elif law == 'levee':
            self.levee_pending += 3
        elif law == 'fatherland':
            self.fatherland = 'allied' if any(s['kind'] == 'allied' for s in self.armies.values()) else 'catholic'
        elif law.startswith('outlaw_'):
            fac = {'outlaw_hebertists': 'hebertist', 'outlaw_merciful': 'merciful',
                   'outlaw_terrorists': 'terrorist'}[law]
            self.faction_outlaw.add(fac)
            for pid, f in FACTION.items():
                if f == fac:
                    self.p[pid]['outlaw'] = True
                    if self.p[pid]['status'] == 'free' and self.p[pid]['loc'] == 'Paris':
                        self.imprison(pid, 'outlawed while in Paris')

    def lawmaker_bonus(self):
        reg, h = self.regime, self.gov_holder
        names = ()
        if reg == 'Terror' or (reg == 'Prairial' and h == MT):
            names = ('robespierre', 'saint_just')
        elif reg == 'Wrath' or (reg == 'Prairial' and h == SC):
            names = ('hebert', 'chaumette')
        elif reg == 'Mercy' and h == M:
            names = ('danton', 'desmoulins')
        for pid in names:
            if self.p[pid]['status'] == 'free' and self.p[pid]['loc'] == 'Paris' and not self.p_outlaw(pid):
                if reg == 'Mercy' and self.holder(pid) not in (M,):
                    continue
                return 2
        return 0

    def marais_thermidor_option(self):
        need = self.rejected_wrath if self.regime == 'Wrath' else self.rejected_terror
        if need >= 2 and not self.outlawed(M):
            if self.prefers(M, 'Thermidor'):
                self.install('Thermidor', M, 'two laws rejected')
                self.regime_changed_this_phase = True

    def trial_vote(self):
        self.trials += 1
        guilty = innocent = 0
        eff = self.law_effects(GOV, 'trial')
        gov_vote = None
        for c in CURRENTS:
            n = self.deputies[c]
            if n <= 0:
                continue
            g = self.law_util(c, eff) > 0 and c != F
            if c == self.human:
                g = self.ask_yes_no('trial', 'Procès de Louis XVI : vote de tes %d députés' % n,
                                    'Coupable (mort)', 'Non coupable')
            if g:
                guilty += n
            else:
                innocent += n
            if c == self.gov_holder:
                gov_vote = g
        guilty += self.bonus['trial_vote'] + (4 if self.auto_trial else 0)
        self.auto_trial = False
        verdict = guilty > innocent or (guilty == innocent and self.law_util(self.gov_holder, eff) > 0)
        if self.trials == 1:
            self.gov_guilty_first = bool(gov_vote)
        self.log('TRIAL of Louis XVI: %d guilty / %d innocent -> %s' % (
            guilty, innocent, 'EXECUTED' if verdict else 'spared'))
        sign = 1 if verdict else -1
        self.track('coalition', 5 * sign, 'event')
        self.track('clergy', 5 * sign, 'trial')
        for c, d in ((SC, 3), (MT, 3), (G, -2), (F, -2)):
            self.fame_adj(c, d * sign, 'trial')
        if verdict:
            self.king = 'dead'
            self.p['louis_xvi']['status'] = 'dead'
            self.stats['king_executed_turn'] = self.turn
        return verdict

    def bankruptcy(self, why):
        if self.stats.get('bankrupt_turn') == self.turn:
            return
        self.stats['bankrupt_turn'] = self.turn
        self.stats['bankruptcies'] += 1
        self.log('!!! BANKRUPTCY (%s)' % why)
        self.fame_adj(self.gov_holder, -5, 'bankruptcy')
        if self.gov_partner:
            self.fame_adj(self.gov_partner, -5, 'bankruptcy')
        self.fame_adj(GOV, -2, 'bankruptcy')

    # ================================================================ patriot phase
    def patriot_phase(self):
        self.justice()
        self.criticism()
        for (a, b, n) in self.switched:
            self.deputies[b] -= n
            self.deputies[a] += n
        self.switched = []

    def justice(self):
        prisoners = [pid for pid, s in self.p.items() if s['status'] == 'prison' and pid != 'louis_xvi']
        reg = self.regime
        for pid in prisoners:
            h = self.holder(pid)
            if reg in ('Legislative', 'Directorate', 'FFR', 'FROI'):
                if reg == 'Legislative' and self.king == 'free' and self.holder('louis_xvi') in (h,) and h in (R, F):
                    self.release(pid, 'freed by the King')
                    continue
                guilty = innocent = 0
                for c in CURRENTS:
                    n = self.deputies[c]
                    if n <= 0:
                        continue
                    if c == h or REL[c].get(h, 0) > -0.25:
                        innocent += n
                    else:
                        guilty += n
                if guilty == innocent:
                    tb = self.holder('louis_xvi') if reg == 'Legislative' and self.king == 'free' else self.gov_holder
                    ok = tb == h or REL[tb].get(h, 0) > -0.25
                else:
                    ok = innocent > guilty
                if ok:
                    self.release(pid, 'acquitted')
            else:
                outlaw = self.p_outlaw(pid)
                res = self.roll(GOV, self.fame[GOV], 1)
                if reg in ('Terror', 'Wrath', 'Prairial') or (reg == 'Convention' and h == R) or (
                        reg in ('Thermidor', 'Mercy') and outlaw):
                    if res in 'AB':
                        self.guillotine(pid)
                elif reg == 'Mercy':
                    if res == 'A':
                        self.guillotine(pid)
                    elif res == 'C':
                        self.release(pid, 'released')
                else:
                    if res == 'C':
                        self.release(pid, 'released')

    def guillotine(self, pid):
        self.kill(pid)
        self.stats['guillotined'] += 1
        self.log('GUILLOTINE: %s' % PERSO[pid]['label'])

    def release(self, pid, why):
        self.p[pid]['status'] = 'free'
        self.p[pid]['loc'] = None
        self.log('%s released (%s)' % (PERSO[pid]['label'], why))

    def criticism(self):
        reg = self.regime
        if reg not in CRITICISM:
            return
        if self.rules == 'FR' and any(t == self.turn and k == 'limited' and ok
                                      for t, _, _, k, _, ok in self.coup_log):
            self.log('No vote of confidence (limited coup this turn)')
            return
        if reg == 'Directorate':
            if self.sole_power_until >= self.turn:
                return
            cands = [c for c in (F, G, MT) if self.official(c) and c != self.gov_partner]
            if not cands:
                return
            conf = dis = 0
            for c in CURRENTS:
                n = self.deputies[c]
                if n <= 0:
                    continue
                if c in (M, self.gov_partner):
                    conf += n
                else:
                    best = max(cands, key=lambda x: (x == c, REL[c].get(x, -1)))
                    if best == c or REL[c].get(best, -1) > REL[c].get(self.gov_partner, -1):
                        dis += n
            if dis > conf:
                old = self.gov_partner
                self.gov_partner = max(cands, key=lambda x: self.deputies[x])
                self.fame_adj(old, 0)
                self.log('Directorate partner replaced: %s -> %s' % (SHORT[old], SHORT[self.gov_partner]))
                self.objectives.pop(GOV, None)
            return
        a, b = CRITICISM[reg]
        gov = self.gov_holder
        opp = b if gov == a else a
        if self.outlawed(opp):
            return
        conf = dis = 0
        for c in CURRENTS:
            n = self.deputies[c]
            if n <= 0:
                continue
            if c == gov:
                conf += n
            elif c == opp:
                dis += n
            else:
                rg, ro = REL[c].get(gov, 0), REL[c].get(opp, 0)
                if c == R and reg == 'Legislative':
                    rg, ro = (-0.5, 0.0) if gov == F else (0.0, -0.5)
                if c == self.human:
                    keep = self.ask_yes_no('confidence', 'Vote de confiance : tes %d députés soutiennent le '
                                           'Gouvernement (%s) ou votent pour %s ?' % (n, gov, opp),
                                           'Confiance à %s' % gov, 'Défiance (pour %s)' % opp)
                    rg, ro = (1, 0) if keep else (0, 1)
                if ro > rg + 0.05:
                    dis += n
                elif rg > ro + 0.05:
                    conf += n
        if dis > conf:
            self.log('VOTE OF NO CONFIDENCE (%d vs %d): %s replaces %s' % (dis, conf, SHORT[opp], SHORT[gov]))
            if gov == G:
                self.gironde_ousted = True
            self.gov_holder = opp
            self.objectives.pop(GOV, None)
            self.stats['no_confidence'] += 1

    # ================================================================ regime changes
    def check_regime_change(self):
        self.regime_changed_this_phase = False
        reg = self.regime
        cc = self.commune_ctrl if self.commune_raised else None
        lvl = self.lvl('commune')
        os_ = self.scenario == 'OS'
        both_war = self.foreign_war and self.civil_war()
        some_peace = not self.foreign_war or not self.civil_war()
        if reg == 'Legislative' and cc in (G, MT, SC) and self.paris_threatened():
            terror_ok = (cc == SC and lvl >= 2) or (cc == MT and lvl == 3)
            options = ['Convention'] + (['Terror'] if terror_ok else [])
            best = self.best_regime(cc, options + ['Legislative'])
            if best != 'Legislative':
                self.install(best, cc, 'Commune + Paris threatened')
                return
        if reg == 'Convention' and cc:
            ok = (cc == SC and lvl >= 2) or (cc == MT and lvl == 3)
            if ok:
                if both_war and self.prefers(cc, 'Terror'):
                    self.install('Terror', cc, 'Commune during war')
                    return
                if os_ and some_peace and self.prefers(cc, 'Mercy'):
                    self.install('Mercy', cc, 'Commune during peace')
                    return
        if reg == 'Convention' and os_ and some_peace and (not self.commune_raised or cc == G):
            if self.prefers(G, 'FFR') and self.referendum(G, 'FFR'):
                self.install('FFR', G, 'referendum')
                return
        if reg == 'Terror' and os_:
            if ('hebertist' not in self.faction_outlaw and both_war and cc == SC and lvl >= 2 and
                    (self.lvl('economy') == 3 or (self.armies_in('Paris', ENEMY)) or
                     len(self.revolt | self.coal | set(self.regions_of(R))) >= 10)):
                if self.prefers(SC, 'Wrath'):
                    self.install('Wrath', SC, 'conditions')
                    return
            if ('merciful' not in self.faction_outlaw and some_peace and not self.commune_raised
                    and not self.paris_threatened_strict()):
                if self.prefers(M, 'Mercy'):
                    self.install('Mercy', M, 'conditions')
                    return
            if some_peace and cc == MT and self.prefers(MT, 'FROI') and self.referendum(MT, 'FROI'):
                self.install('FROI', MT, 'referendum')
                self.froi_variant = MT
                return
        if reg == 'Wrath' and some_peace and self.prefers(SC, 'FROI') and self.referendum(SC, 'FROI'):
            self.install('FROI', SC, 'referendum')
            self.froi_variant = SC
            return
        if reg == 'Mercy' and both_war and cc and ((cc == SC and lvl >= 2) or (cc == MT and lvl == 3)):
            if self.prefers(cc, 'Terror'):
                self.install('Terror', cc, 'Commune during war')
                return
        if reg == 'Thermidor' and os_ and getattr(self, 'directorate_pending', False):
            self.directorate_pending = False
            self.install('Directorate', M, 'referendum')
            return
        if reg == 'Prairial' and self.regime_turn < self.turn:
            if self.referendum(self.gov_holder, 'FROI'):
                v = self.gov_holder
                self.install('FROI', v, 'Prairial referendum')
                self.froi_variant = v
                return

    def referendum(self, proposer, new):
        no = 0
        for c in self.order:
            ballots = sum(1 for r in self.regions_of(c)
                          if r == 'Paris' or not (r in self.revolt or self.armies_in(r, ENEMY)))
            if c == self.gov_holder or c == proposer:
                continue
            if self.rank_under(c, new) > self.rank_under(c, self.regime):
                no += ballots
        ok = no <= 13
        self.log('Referendum for %s: %d "no" -> %s' % (new, no, 'ADOPTED' if ok else 'rejected'))
        if ok and self.rules == 'FR':
            self.fame_adj(proposer, 1, 'referendum')
            if GOV != proposer:
                self.fame_adj(GOV, 1, 'referendum')
        return ok

    def install(self, new, who, why):
        prev = self.regime
        prev_gov = self.gov_holder
        self.prev_regime = prev
        self.regime = new
        self.regime_turn = self.turn
        self.regime_history.append((self.turn, new))
        self.log('######## NEW REGIME: %s (by %s, %s)' % (new, SHORT.get(who, who), why))
        self.stats['regime_changes'] += 1
        self.objective_hit(who, 'regime', new)
        self.faction_outlaw_before = set(self.faction_outlaw)
        # outlaws individuels remis a zero (R.0), sauf ceux issus d'un coup rate
        self.faction_outlaw = set()
        for pid, s in self.p.items():
            if s['outlaw'] and not s.get('coup'):
                s['outlaw'] = False
        mt_was_outlawed = self.outlawed(MT) if prev != new else False
        self.coup_outlaw = set()
        if new == 'Vendemiaire':
            self.winner = R
            self.ended_early = True
            self.log('VENDEMIAIRE : the Royalist wins immediately')
            raise GameOver()
        if new in ('Convention', 'Terror'):
            self.convention_or_terror = True
        gov = {'Convention': G, 'Terror': MT, 'Thermidor': M, 'Wrath': SC, 'FFR': G,
               'Prairial': who, 'FROI': who, 'Directorate': M}.get(new)
        if new == 'Mercy':
            gov = who if who in (MT, M) else MT
        self.gov_holder = gov
        self.gov_partner = None
        if self.fame[GOV] < 10:
            self.fame[GOV] = 10
        if prev == 'Legislative':
            self.king = 'prison' if self.king == 'free' else self.king
            if self.king == 'prison':
                self.p['louis_xvi']['status'] = 'prison'
        # prisonniers du courant au pouvoir liberes
        for pid, s in self.p.items():
            if s['status'] == 'prison' and s['holder'] == gov and pid != 'louis_xvi':
                self.release(pid, 'new regime')
        cl_co = lambda: (self.track('clergy', 3, 'regime'), self.track('coalition', 3, 'regime'))
        if new == 'Convention':
            cl_co()
            self.hold_election('Convention')
            self.next_election = self.turn + 4
        elif new == 'Terror':
            cl_co()
            for pid, s in self.p.items():
                if s['status'] == 'prison' and s['holder'] == MT:
                    self.release(pid, 'Terror')
            for r in REGIONS:
                if self.control[r] == G and r != 'Paris':
                    self.revolt.add(r)
            self.aside[G] += self.deputies[G]
            self.deputies[G] = 0
            if prev in ('Legislative', 'FFR'):
                self.hold_election('Terror')
                self.next_election = self.turn + 4
        elif new == 'Thermidor':
            out = prev_gov if prev_gov in (MT, SC) else MT
            self.thermidor_outlaw = out
            for pid, s in self.p.items():
                if s['status'] == 'prison' and s['holder'] in (F, M, G):
                    self.release(pid, 'Thermidor')
            self.deputies[G] += self.aside[G]
            self.aside[G] = 0
            self.aside[out] += self.deputies[out]
            self.deputies[out] = 0
            self.deputies[R] = 0
            if prev == 'FROI':
                self.hold_election('Thermidor')
                self.next_election = self.turn + 4
        elif new == 'Wrath':
            cl_co()
            self.switch_event('marat', SC)
            for c in (G, MT):
                self.aside[c] += self.deputies[c]
                self.deputies[c] = 0
            self.deputies[SC] += self.aside[SC]
            self.aside[SC] = 0
        elif new == 'Mercy':
            for pid in ('danton', 'desmoulins'):
                self.switch_event(pid, M)
            self.deputies[G] += self.aside[G]
            self.aside[G] = 0
            if prev == 'FFR':
                self.hold_election('Mercy')
                self.next_election = self.turn + 4
        elif new == 'Directorate':
            self.mt_outlawed_prev = mt_was_outlawed
            self.hold_election('Directorate')
            self.next_election = self.turn + 4
            elig = [c for c in (F, G, MT) if not (c == MT and self.mt_outlawed_prev)]
            self.gov_partner = max(elig, key=lambda c: (self.deputies[c], self.rng.random()))
        elif new == 'Prairial':
            cl_co()
            for c in (F, M, G):
                self.aside[c] += self.deputies[c]
                self.deputies[c] = 0
            for c in (MT, SC):
                self.deputies[c] += self.aside[c]
                self.aside[c] = 0
            if prev == 'Directorate':
                self.hold_election('Prairial')
                self.next_election = self.turn + 4
        elif new == 'FFR':
            cl_co()
            if self.control['Bordeaux'] != G and 'Bordeaux' not in self.revolt:
                self.control['Bordeaux'] = None
            self.hold_election('FFR')
            self.next_election = self.turn + 4
        elif new == 'FROI':
            cl_co()
            if self.paris_holder() not in (MT, SC):
                if self.commune_raised:
                    self.commune_ctrl = None
                else:
                    self.control['Paris'] = None
            self.hold_election('FROI')
            self.next_election = self.turn + 2
        # outlaws presents a Paris arretes
        for pid, s in self.p.items():
            if s['status'] == 'free' and s['loc'] == 'Paris' and self.p_outlaw(pid):
                self.imprison(pid, 'outlaw in Paris at regime change')

    def hold_election(self, proc):
        n = {c: len([r for r in REGIONS if self.control[r] == c]) for c in CURRENTS}
        neutral = len([r for r in REGIONS if self.control[r] is None and r not in self.coal])
        up = lambda x: (x + 1) // 2
        dn = lambda x: x // 2
        d = {c: 0 for c in CURRENTS}
        if proc == 'Legislative':
            d[F] = n[F]; d[M] = n[M] + neutral + dn(n[R]); d[R] = up(n[R])
            d[G] = n[G] + dn(n[MT]); d[MT] = up(n[MT]) + dn(n[SC]); d[SC] = up(n[SC])
        elif proc in ('Convention', 'Mercy', 'Terror', 'Thermidor', 'Wrath', 'Prairial'):
            d[G] = n[G] + dn(n[F]); d[M] = n[M] + neutral + up(n[R]); d[F] = up(n[F])
            d[MT] = n[MT] + dn(n[R]); d[SC] = n[SC]
            if proc == 'Terror':
                d[G] = 0
            if proc == 'Wrath':
                d[G] = 0; d[MT] = 0
            if proc == 'Prairial':
                d[G] = d[M] = d[F] = 0
            if proc == 'Thermidor' and self.thermidor_outlaw:
                d[self.thermidor_outlaw] = 0
        elif proc == 'Directorate':
            d[F] = n[F]; d[M] = n[M] + neutral + dn(n[MT]); d[R] = n[R] + dn(n[SC])
            d[G] = n[G]; d[MT] = up(n[MT]); d[SC] = up(n[SC])
        elif proc == 'FFR':
            d[G] = n[G] + neutral + dn(n[F]) + dn(n[MT]); d[M] = n[M] + dn(n[R])
            d[F] = up(n[F]); d[R] = up(n[R]); d[MT] = up(n[MT]) + dn(n[SC]); d[SC] = up(n[SC])
        elif proc == 'FROI':
            d[M] = n[M] + dn(n[F]); d[F] = up(n[F]); d[R] = up(n[R]); d[G] = up(n[G])
            d[MT] = n[MT] + neutral + dn(n[G]); d[SC] = n[SC] + dn(n[R])
        if proc in ('Convention', 'Terror', 'Mercy', 'Wrath', 'Prairial', 'Thermidor'):
            d[R] = 0
        self.deputies = d
        self.aside = {c: 0 for c in CURRENTS}
        self.log('ELECTION (%s): %s' % (proc, ', '.join('%s %d' % (SHORT[c], d[c]) for c in CURRENTS)))
        self.stats['elections'] += 1

    def check_elections(self):
        if self.regime == 'Legislative':
            if self.turn in (4, 8):
                self.hold_election('Legislative')
            return
        if self.turn == self.next_election and self.regime_turn != self.turn:
            proc = self.regime
            self.hold_election(proc if proc not in ('FFR', 'FROI', 'Directorate') else proc)
            self.next_election = self.turn + self.election_period_for(self.regime)

    def election_period_for(self, reg):
        return 2 if reg == 'FROI' else 4

    # ================================================================ coups
    def try_coups(self, kinds=('popular', 'military', 'limited')):
        for c in self.order:
            for kind in kinds:
                opt = self.coup_option(c, kind)
                if opt and self.want_coup(c, kind, opt):
                    self.do_coup(c, kind, opt)

    def coup_option(self, c, kind):
        """Renvoie la cible (regime ou 'power') si le coup est permis, sinon None."""
        reg = self.regime
        os_ = self.scenario == 'OS'
        cc = self.commune_ctrl if self.commune_raised else None
        lv = self.lvl('commune')
        if self.outlawed(c):
            return None
        if kind == 'limited':
            if self.limited_coup_done or self.popular_coup_done or self.military_coup_done:
                return None
            if reg == 'Legislative' and (os_ or self.rules != 'FR'):
                if c == F and self.gov_holder == G:
                    return 'power'
                if c == G and self.gov_holder == F and (self.feuillant_coup_done or lv == 3):
                    return 'power'
            if not os_:
                return None
            if reg == 'Directorate' and c in (G, F, MT) and c != self.gov_partner:
                return 'power'
            if reg == 'FFR':
                if c == M and self.gov_holder == G:
                    return 'power'
                if c == G and self.gov_holder == M and getattr(self, 'marais_ffr_limited', False):
                    return 'power'
            if reg == 'FROI' and c in (MT, SC) and self.gov_holder != c and cc != self.gov_holder:
                return 'power'
            return None
        if not os_:
            return None
        if kind == 'popular':
            if self.popular_coup_done or not self.commune_raised:
                return None
            if reg == 'Legislative' and c == G:
                return 'Convention' if ((cc == SC and lv >= 2) or (cc in (SC, MT, G) and lv == 3)) else 'power'
            if reg == 'Convention' and c == MT and ((cc == SC) or (cc == MT and lv >= 2)):
                return 'Terror' if (self.foreign_war and self.civil_war()) else 'Mercy'
            if reg == 'Terror':
                if c == M and 'merciful' not in self.faction_outlaw and (not self.foreign_war or not self.civil_war()) and cc == SC and lv == 3:
                    return 'Mercy'
                if c == SC and 'hebertist' not in self.faction_outlaw and self.foreign_war and self.civil_war() and cc == SC and lv == 3:
                    return 'Wrath'
            if reg == 'Thermidor' and c in (MT, SC) and cc == c and lv == 3 and (self.foreign_war or self.civil_war()):
                return 'Prairial'
            if reg == 'Wrath' and c == M and cc == MT and lv >= 2:
                return 'Thermidor'
            if reg == 'Mercy' and c == MT and self.gov_holder == M and cc in (SC, MT) and lv == 3:
                return 'Terror'
            if reg == 'Directorate':
                if c == MT and cc == MT and lv == 3:
                    return 'Prairial'
                if c == SC and cc == SC and lv >= 2:
                    return 'Prairial'
                if c == R and cc == R and lv >= 2 and not self.royalist_coup_used:
                    return 'Vendemiaire'
            if reg == 'Prairial' and c == R and cc == R and lv == 3 and (self.foreign_war or self.civil_war()):
                return 'Vendemiaire'
            if reg == 'FFR' and (c == MT or (c == M and self.marais_ffr_coup_ok)):
                if (cc == SC and lv >= 2) or (cc == MT and lv == 3):
                    if self.foreign_war or self.civil_war():
                        return 'Terror'
                    return 'Mercy'
            if reg == 'FROI' and c == M and not self.commune_raised:
                return 'Thermidor'
            return None
        if kind == 'military':
            if self.military_coup_done or self.popular_coup_done:
                return None
            tgt = None
            if reg == 'Legislative' and c == G:
                tgt = 'Convention'
            elif reg == 'Convention' and c == MT:
                tgt = 'Terror' if (self.foreign_war and self.civil_war()) else 'Mercy'
            elif reg == 'Terror' and c == M and (not self.foreign_war or not self.civil_war()):
                tgt = 'Mercy'
            elif reg == 'Wrath' and c == M:
                tgt = 'Thermidor'
            elif reg == 'Mercy' and c == M:
                tgt = 'Directorate'
            elif reg == 'Mercy' and c == MT and self.gov_holder == M:
                tgt = 'Terror'
            elif reg == 'Directorate' and c == MT:
                tgt = 'Prairial'
            elif reg == 'FFR' and c == MT:
                tgt = 'Terror' if (self.foreign_war or self.civil_war()) else 'Mercy'
            elif reg == 'FROI' and c == M:
                tgt = 'Thermidor'
            if tgt is None:
                return None
            stack = self.military_stack(c)
            return tgt if stack else None
        return None

    def military_stack(self, c):
        best = None
        for r in REGIONS:
            pids = [pid for pid in self.perso_of(c) if self.p[pid]['loc'] == r and not self.p_outlaw(pid)
                    and pid not in NEVER_MILITARY_COUP]
            armies = [a for a in self.armies_in(r, ('regular', 'volunteer')) if not self.armies[a]['pinned']]
            if pids and armies and self.path_to_paris(r):
                if best is None or len(pids) > len(best[1]):
                    best = (r, pids, armies[:3])
        return best

    def coup_mods(self, c, kind, pids):
        extra = min(1, len(pids) - 1) if self.rules == 'FR' else len(pids) - 1
        mod = 2 * extra + self.bonus[('coup_%s' % kind, c)]
        if self.regime == 'FROI' and c == SC and self.froi_variant == SC and self.commune_raised and kind == 'limited':
            mod += self.lvl('commune')
        for d in self.order:
            if d in (c, self.gov_holder):
                continue
            if any(self.p[pid]['loc'] == 'Paris' and self.p[pid]['status'] == 'free' for pid in self.perso_of(d)):
                tgt = self.coup_target_regime(c, kind)
                if self.rank_under(d, tgt) > self.rank_under(d, self.regime):
                    mod -= 1
        return mod

    def coup_target_regime(self, c, kind):
        opt = self.coup_option(c, kind) if kind != 'military' else None
        return self.regime if opt in (None, 'power') else opt

    def want_coup(self, c, kind, target):
        if c == self.human:
            cost = (100 if kind == 'limited' else 200) * self.k()
            if kind != 'military' and not any(self.p[pid]['loc'] == 'Paris' for pid in self.perso_of(c)):
                return False
            if self.money[c] < cost:
                return False
            what = 'prendre le Gouvernement' if target == 'power' else 'instaurer %s' % target
            return self.ask_yes_no('coup', 'Tenter un coup d\'État %s (%d assignats) pour %s ?' % (
                {'limited': 'limité', 'popular': 'populaire', 'military': 'militaire'}[kind], cost, what))
        if kind == 'military':
            r, pids, armies = self.military_stack(c)
            p = p_result(self.fame[c] + 2 * (len(pids) - 1) - 2 * (len(armies) - 1)
                         + self.bonus[('rally', c)], 'AB') * 0.35
            pids_n = len(pids)
        else:
            pids = [pid for pid in self.perso_of(c) if self.p[pid]['loc'] == 'Paris' and pid != 'louis_xvi']
            if not pids:
                return False
            p = p_result(self.fame[c] + self.coup_mods(c, kind, pids), 'A')
            pids_n = len(pids)
        cost = (100 if kind == 'limited' else 200) * self.k()
        if self.money[c] < cost:
            return False
        V = {1: 12.0, 2: 6.0, 3: 3.0, 4: 1.5, 5: 0.5, 6: 0.0}
        now = self.rank_under(c, self.regime)
        if target == 'power':
            gain = 2.0
        elif target == 'Vendemiaire':
            gain = V[1] - V[now]
        else:
            gain = V[self.rank_under(c, target)] - V[now]
        fail = V[now] - V[min(6, now + 1)] + 0.4 * pids_n
        ev = p * gain - (1 - p) * fail - cost * self.mv(c)
        return ev > 0.2

    def do_coup(self, c, kind, target):
        cost = (100 if kind == 'limited' else 200) * self.k()
        if not self.pay(c, cost):
            return
        self.stats['coup_%s_attempts' % kind] += 1
        if kind == 'limited':
            self.limited_coup_done = True
        elif kind == 'popular':
            self.popular_coup_done = True
        else:
            self.military_coup_done = True
        if target == 'Vendemiaire':
            self.royalist_coup_used = True
        if kind == 'military':
            ok, pids = self.military_coup(c, target)
        else:
            pids = [pid for pid in self.perso_of(c) if self.p[pid]['loc'] == 'Paris' and pid != 'louis_xvi']
            if self.rules == 'FR':
                pids = pids[:2]
            mod = self.coup_mods(c, kind, pids)
            res = self.roll(c, self.fame[c] + mod, 1)
            ok = res == 'A'
        self.coup_log.append((self.turn, self.regime, c, kind, target, ok))
        self.log('COUP %s by %s -> %s : %s' % (kind, SHORT[c], target, 'SUCCESS' if ok else 'FAILURE'))
        if ok:
            self.stats['coup_%s_ok' % kind] += 1
            if kind == 'limited' or target == 'power':
                old = self.gov_holder
                if self.regime == 'Directorate':
                    self.sole_power_until = self.turn
                    self.gov_partner = None
                self.gov_holder = c
                self.objectives.pop(GOV, None)
                if kind == 'limited':
                    self.fame_adj(c, 1, 'coup')
                    self.fame_adj(old, -1, 'coup')
                    if self.regime == 'Legislative' and c == F:
                        self.feuillant_coup_done = True
                    if self.regime == 'FFR' and c == M:
                        self.marais_ffr_limited = True
                if self.regime == 'FROI':
                    if self.commune_ctrl == c and self.lvl('commune') >= 2:
                        self.froi_variant = c
                if kind == 'popular':
                    self.track('commune', 3, 'coup')
            else:
                self.track('commune', 3 if kind == 'popular' else -5, 'coup')
                self.install(target, c, '%s coup' % kind)
        else:
            for pid in pids:
                self.p[pid]['outlaw'] = True
                self.p[pid]['coup'] = True
                self.imprison(pid, 'failed coup')
            if kind == 'limited':
                self.fame_adj(c, -1, 'failed coup')
                self.temp_outlaw[c] = self.turn + 1
            else:
                marais_light = c == M
                if marais_light:
                    self.temp_outlaw[c] = self.turn + 1
                else:
                    self.coup_outlaw.add(c)
                    if c in OFFICIAL[self.regime]:
                        self.aside[c] += self.deputies[c]
                        self.deputies[c] = 0
                if self.commune_ctrl == c:
                    self.commune_ctrl = None
                self.track('commune', -3 if kind == 'popular' else 5, 'failed coup')
                if self.regime == 'FFR' and c == MT:
                    self.marais_ffr_coup_ok = True
                if self.regime == 'Legislative' and c == G:
                    self.temp_outlaw[c] = self.turn + 1
                    self.coup_outlaw.discard(c)

    def military_coup(self, c, target):
        r, pids, armies = self.military_stack(c)
        mod = 2 * (len(pids) - 1) - 2 * (len(armies) - 1) + self.bonus[('rally', c)]
        if self.regime == 'Mercy' and c == M and self.gov_holder == M:
            mod += 2
        res = self.roll(c, self.fame[c] + mod, 1)
        if res not in 'AB':
            self.log('Military coup: rally failed (%s)' % SHORT[c])
            return False, []   # "if the rally attempt fails, nothing happens"
        for pid in pids:
            self.p[pid]['outlaw'] = True
            self.p[pid]['coup'] = True
        rebels = len(armies)
        defenders = len(self.armies_in('Paris', REVOLUTIONARY))
        # interception par les armees adjacentes a Paris si le Gouvernement s'y oppose
        if self.rank_under(self.gov_holder, target) >= self.rank_under(self.gov_holder, self.regime):
            for a in self.rev_armies():
                if a not in armies and self.armies[a]['region'] in ADJ['Paris'] and not self.armies[a]['pinned']:
                    self.armies[a]['region'] = 'Paris'
                    defenders += 1
        defenders += 1  # la Commune se leve (neutre)
        att = rebels > defenders or rebels == defenders
        s = self.d6() + self.d6()
        diff = abs(rebels - defenders)
        if att:
            s = min(12, s + diff)
            res = table(s, 13)
            win = res == 'A' and defenders == 1
        else:
            s = max(2, s - diff)
            res = table(s, 13)
            win = res == 'C' and defenders == 1
        for a in armies:
            self.armies[a]['region'] = 'Paris'
        if not win:
            for pid in pids:
                self.imprison(pid, 'failed military coup')
            return False, []
        for pid in pids:
            self.p[pid]['outlaw'] = False
            self.p[pid]['coup'] = False
        return True, pids

    # ================================================================ military phase
    def military_phase(self):
        self.reinforcements()
        self.maintenance()
        self.try_coups()
        self.movement()
        self.combat()
        self.military_control()

    def reinforcements(self):
        if self.foreign_war:
            for aid, d in ALLIED.items():
                st = self.allied_state[aid]
                if st not in ('pending', 'available'):
                    continue
                if d['wave'] == 1 and st == 'pending' and self.war_entered:
                    continue
                if d['wave'] == 2 and not self.convention_or_terror:
                    continue
                if d['wave'] == 3:
                    if not self.convention_or_terror:
                        continue
                    if aid == 'fleet' and self.control['Marseille'] != R:
                        continue
                    if aid == 'quiberon' and not (self.control['Brest'] == R and self.control['Nantes'] == R):
                        continue
                self.armies[aid] = dict(kind='allied', region=d['entry'], step=0, pinned=False, rebel=False)
                self.allied_state[aid] = 'onmap'
                self.log('Allied army %s enters at %s' % (d['label'], d['entry']))
                self.stats['allied_entries'] += 1
            self.war_entered = True
        # Vendee
        if self.clergy_iii:
            for aid in CATHOLIC:
                if self.catholic_state[aid] not in ('unraised', 'available'):
                    continue
                spots = [r for r in VENDEE if any(self.p[g]['loc'] == r and self.p[g]['status'] == 'free'
                                                    and self.holder(g) == R for g in GENERALS)]
                if not spots:
                    break
                n_cath = sum(1 for s in self.armies.values() if s['kind'] == 'catholic')
                if self.money[R] < 100 * self.k() * (n_cath + 1):
                    break
                r = spots[0]
                self.armies[aid] = dict(kind='catholic', region=r, step=0, pinned=False, rebel=False)
                self.catholic_state[aid] = 'onmap'
                self.log('Catholic & Royal army raised in %s' % r)
                self.stats['catholic_raised'] += 1
        # Gouvernement
        new = self.levee_pending + (1 if self.conscription else 0)
        self.levee_pending = 0
        vols = sum(1 for s in self.armies.values() if s['kind'] == 'volunteer')
        for _ in range(min(new, 16 - vols)):
            self.vol_n += 1
            reg = self.gov_place_army()
            if reg:
                self.armies['vol%d' % self.vol_n] = dict(kind='volunteer', region=reg, step=0, pinned=False, rebel=False)
                self.stats['volunteers'] += 1

    def gov_place_army(self):
        ok = [r for r in REGIONS if self.control[r] != R and not self.armies_in(r, ENEMY) and r not in self.revolt]
        if not ok:
            return None
        enemies = [self.armies[a]['region'] for a in self.enemy_armies()]
        if enemies:
            return min(ok, key=lambda r: min(self.dist(r, e) for e in enemies) + (0 if r in ADJ['Paris'] or r == 'Paris' else 0.5))
        return 'Paris' if 'Paris' in ok else ok[0]

    def maintenance(self):
        k = self.k()
        revs = sorted(self.rev_armies(), key=lambda a: self.armies[a]['kind'] != 'volunteer')
        for a in revs:
            if self.armies[a]['kind'] == 'temp':
                continue
            if not self.pay(GOV, 100 * k):
                kind = self.armies[a]['kind']
                del self.armies[a]
                self.log('Army %s disbanded (no money)' % a)
                if kind == 'regular':
                    self.bankruptcy('regular army unpaid')
        for a in [a for a, s in self.armies.items() if s['kind'] == 'catholic']:
            if not self.pay(R, 100 * k):
                del self.armies[a]
                self.catholic_state[a] = 'eliminated'
                self.log('Catholic army %s disbanded (no money)' % a)

    def dist(self, a, b):
        if a == b:
            return 0
        seen, frontier, d = {a}, [a], 0
        while frontier:
            d += 1
            nxt = []
            for x in frontier:
                for y in ADJ[x]:
                    if y == b:
                        return d
                    if y not in seen:
                        seen.add(y)
                        nxt.append(y)
            frontier = nxt
        return 99

    def path_to_paris(self, r):
        return self.reachable(r, 'Paris')

    def reachable(self, src, dst):
        """Armee revolutionnaire : traverse les regions sans armee ennemie."""
        if src == dst:
            return True
        seen, frontier = {src}, [src]
        while frontier:
            nxt = []
            for x in frontier:
                for y in ADJ[x]:
                    if y == dst:
                        return True
                    if y not in seen and not self.armies_in(y, ENEMY):
                        seen.add(y)
                        nxt.append(y)
            frontier = nxt
        return False

    def movement(self):
        # pinning (9.5.1) : le Royaliste immobilise toujours
        for a in self.rev_armies():
            if self.armies_in(self.armies[a]['region'], ENEMY):
                self.armies[a]['pinned'] = True
        allied_moving = self.foreign_war and self.lvl('coalition') >= 2
        if allied_moving:
            for aid in [a for a, s in self.armies.items() if s['kind'] == 'allied']:
                self.move_allied(aid)
        self.royalist_move()
        self.gov_move()

    def move_allied(self, aid):
        s = self.armies[aid]
        route = ALLIED[aid]['route']
        if len(route) == 1:
            return
        if aid == 'quiberon' and not any(self.armies[a]['region'] == 'Paris' and 'Paris' in self.coal
                                         for a in self.armies if self.armies[a]['kind'] == 'allied' and a != aid):
            return
        if s['region'] not in self.coal or self.armies_in(s['region'], REVOLUTIONARY):
            return
        while s['step'] + 1 < len(route):
            nxt = route[s['step'] + 1]
            s['step'] += 1
            s['region'] = nxt
            if self.armies_in(nxt, REVOLUTIONARY) or not (nxt in self.coal or self.control[nxt] == R) or (
                    nxt in self.revolt and self.control[nxt] != R):
                break
        self.log('Allied %s moves to %s' % (aid, s['region']))

    def royalist_move(self):
        caths = [a for a, s in self.armies.items() if s['kind'] == 'catholic']
        for a in caths:
            s = self.armies[a]
            r = s['region']
            gens = [g for g in GENERALS if self.p[g]['loc'] == r and self.p[g]['status'] == 'free' and self.holder(g) == R]
            revs = len(self.armies_in(r, REVOLUTIONARY))
            if r in VENDEE and gens and revs > len(self.armies_in(r, ['catholic'])):
                s['hiding'] = True
                if self.control[r] == R:
                    self.control[r] = None
                continue
            if not gens or revs or s['pinned']:
                continue
            others = [x for x in caths if x != a and self.armies[x]['region'] in VENDEE]
            if r in VENDEE and not others:
                continue
            tgt = [n for n in ADJ[r] if self.control[n] != R and not self.armies_in(n, REVOLUTIONARY)]
            if tgt:
                n = max(tgt, key=lambda x: REGIONS[x][0] + (300 if x == 'Paris' else 0))
                s['region'] = n
                self.p[gens[0]]['loc'] = n
                self.log('Catholic army %s moves to %s with %s' % (a, n, PERSO[gens[0]]['label']))

    def gov_move(self):
        h = self.gov_holder
        free = [a for a in self.rev_armies() if not self.armies[a]['pinned'] and not self.armies[a].get('rebel')]
        # 1) cibles : armees ennemies (priorite Paris), puis revoltes
        stacks = defaultdict(int)
        for a in self.enemy_armies():
            if self.armies[a].get('hiding'):
                continue
            stacks[self.armies[a]['region']] += 1
        targets = sorted(stacks, key=lambda r: (self.dist(r, 'Paris'), -stacks[r]))
        for r in targets:
            present = len(self.armies_in(r, REVOLUTIONARY))
            need = stacks[r] + 1 - present
            cands = sorted([a for a in free if self.reachable(self.armies[a]['region'], r)],
                           key=lambda a: self.dist(self.armies[a]['region'], r))
            if len(cands) + present <= stacks[r] - 1 and r != 'Paris':
                continue
            for a in cands[:max(0, need)]:
                self.armies[a]['region'] = r
                free.remove(a)
        # 2) Commune hostile : suppression par la force
        if self.commune_raised and self.commune_ctrl not in (h, None) and REL[h].get(self.commune_ctrl, 0) <= -0.3:
            if self.gov_plan.get('suppress_commune'):
                cands = [a for a in free if self.reachable(self.armies[a]['region'], 'Paris')]
                if len(cands) >= 2:
                    for a in cands[:2]:
                        self.armies[a]['region'] = 'Paris'
                        self.armies[a]['vs_commune'] = True
                        free.remove(a)
                    self.tracks['commune'] = 20
                    self.log('Gov sends armies to crush the Commune')
        # 2b) regions de la Coalition sans armee ennemie : liberation facile
        for r in sorted(self.coal, key=lambda r: -REGIONS[r][0]):
            if self.armies_in(r, ENEMY) or self.armies_in(r, REVOLUTIONARY):
                continue
            cands = [a for a in free if self.reachable(self.armies[a]['region'], r)]
            if cands:
                a = min(cands, key=lambda a: self.dist(self.armies[a]['region'], r))
                self.armies[a]['region'] = r
                free.remove(a)
        # 3) revoltes (ramener le revenu), sauf revoltes tenues par le courant au pouvoir
        for r in sorted(self.revolt, key=lambda r: -REGIONS[r][0]):
            if self.control[r] == h or self.armies_in(r, REVOLUTIONARY):
                continue
            cands = [a for a in free if self.reachable(self.armies[a]['region'], r)]
            if cands:
                a = min(cands, key=lambda a: self.dist(self.armies[a]['region'], r))
                self.armies[a]['region'] = r
                free.remove(a)

    def combat(self):
        regions = {s['region'] for s in self.armies.values()}
        for r in regions:
            rev = self.armies_in(r, REVOLUTIONARY)
            en = [a for a in self.armies_in(r, ENEMY) if not self.armies[a].get('hiding')]
            commune_fights = r == 'Paris' and self.commune_raised and en
            if en and (rev or commune_fights):
                self.battle(r, rev, en, commune_fights)
        # Gouvernement contre la Commune
        vs = [a for a, s in self.armies.items() if s.get('vs_commune') and s['region'] == 'Paris']
        if vs and self.commune_raised:
            n = len(vs)
            att_mod = n - 1
            s = min(12, self.d6() + self.d6() + att_mod)
            res = table(s, 13)
            if res == 'A':
                self.commune_raised = False
                self.commune_ctrl = None
                self.log('Gov armies crush the Commune')
                self.objective_hit(GOV, 'crush_commune', 'Paris')
                self.stats['commune_crushed'] += 1
            elif res == 'C':
                a = vs[0]
                del self.armies[a]
                self.log('Commune destroys a government army')
            for a in vs:
                if a in self.armies:
                    self.armies[a].pop('vs_commune', None)

    def battle(self, r, rev, en, commune):
        nrev = len(rev) + (1 if commune else 0)
        nen = len(en)
        if r == 'Lille' and self.bonus['lille_nofight'] and nrev >= nen:
            return
        rev_att = nrev >= nen
        diff = abs(nrev - nen)
        s = self.d6() + self.d6()
        extra = self.bonus[('combat', r)]
        carnot = self.p['carnot']
        if carnot['status'] == 'free' and carnot['loc'] == r and self.regime in ('Terror', 'Wrath', 'Mercy') and self.holder('carnot') in (M, MT):
            extra += 1 if rev_att else -1
        if rev_att:
            s = max(2, min(12, s + diff + extra))
        else:
            s = max(2, min(12, s + diff - extra))
        res = table(s, 13)
        att_side = 'rev' if rev_att else 'enemy'
        loser = None
        if res == 'A':
            loser = 'enemy' if rev_att else 'rev'
        elif res == 'C':
            loser = 'rev' if rev_att else 'enemy'
        self.log('BATTLE %s: %d rev%s vs %d enemy -> %s' % (r, len(rev), '+Commune' if commune else '', nen,
                                                           {'rev': 'revolution loses one', 'enemy': 'enemy loses one', None: 'no effect'}[loser]))
        self.stats['battles'] += 1
        if loser == 'enemy':
            kill = min(en, key=lambda a: self.armies[a]['kind'] == 'allied')
            kind = self.armies[kill]['kind']
            del self.armies[kill]
            if kind == 'allied':
                self.allied_state[kill] = 'eliminated'
                self.stats['allied_killed'] += 1
            else:
                self.catholic_state[kill] = 'eliminated'
                self.stats['catholic_killed'] += 1
            self.objective_hit(GOV, 'army', r)
        elif loser == 'rev':
            if rev:
                kill = min(rev, key=lambda a: {'temp': 0, 'volunteer': 1, 'regular': 2}[self.armies[a]['kind']])
                del self.armies[kill]
                self.stats['rev_killed'] += 1
            elif commune:
                self.commune_raised = False
                self.commune_ctrl = None
            if not self.armies_in(r, REVOLUTIONARY) and any(self.armies[a]['kind'] == 'catholic' for a in en) \
                    and not any(self.armies[a]['kind'] == 'allied' for a in en):
                self.fame_adj(R, 1, 'Royalist spoils')

    def military_control(self):
        for r in REGIONS:
            rev = self.armies_in(r, REVOLUTIONARY)
            al = self.armies_in(r, ['allied'])
            ca = [a for a in self.armies_in(r, ['catholic']) if not self.armies[a].get('hiding')]
            if (al or ca) and not rev and not (r == 'Paris' and self.commune_raised):
                if al and r not in self.coal:
                    self.coal.add(r)
                    if self.control[r] != R:
                        self.control[r] = None
                    self.log('Coalition takes %s' % r)
                    self.stats['coalition_regions'] += 1
                if ca:
                    if r in self.coal and not al:
                        pass
                    if self.control[r] != R:
                        self.control[r] = R
                        self.revolt.discard(r) if self.control[r] != R else None
                        self.log('Royalist army takes %s' % r)
            elif rev and not al and not ca:
                if r in self.coal:
                    self.coal.discard(r)
                    self.log('Revolution frees %s' % r)
                if r in self.revolt:
                    self.revolt.discard(r)
                    self.log('Army puts down revolt in %s' % r)
                    self.stats['revolts_crushed_by_army'] += 1
        # enlevement du roi
        if self.king in ('free', 'prison') and self.paris_occupied():
            cost = 200 * self.k() if self.regime == 'Legislative' else 0
            if self.pay(R, cost):
                res = self.roll(R, self.fame[R] + self.cur_bonus(R), 1)
                if res in 'AB':
                    self.king = 'kidnapped'
                    self.p['louis_xvi']['holder'] = R
                    self.p['louis_xvi']['status'] = 'free'
                    self.log('*** THE KING IS KIDNAPPED by the Royalist')
                    self.stats['kidnap'] = self.turn
        if self.king == 'kidnapped' and not self.armies_in('Paris', ENEMY):
            self.king = 'prison'
            self.p['louis_xvi']['status'] = 'prison'
            self.auto_trial = True
            self.log('The King is recaptured')
        # fin de guerre : plus d'armee alliee en France
        if self.foreign_war and self.war_entered and not any(s['kind'] == 'allied' for s in self.armies.values()):
            pending = any(st in ('pending', 'available') and (ALLIED[a]['wave'] != 1 or not self.war_entered)
                          for a, st in self.allied_state.items() if ALLIED[a]['wave'] == 2 and not self.convention_or_terror)
            if not pending:
                self.end_war('no allied army left in France')

    # ================================================================ interphase
    def interphase(self):
        inc = self.spent // 1000
        if inc:
            self.track('economy', inc, 'spending %d' % self.spent)
        self.stats['spent_total'] += self.spent
        self.spent = 0
        # revenus
        for c in CURRENTS:
            income = sum(REGIONS[r][0] for r in REGIONS if self.control[r] == c and not (c == R and r in self.coal))
            if self.commune_raised and self.commune_ctrl == c and self.control['Paris'] != c:
                income += REGIONS['Paris'][0]
            if self.commune_raised and self.control['Paris'] == c and self.commune_ctrl != c:
                income -= REGIONS['Paris'][0]
            if c == R:
                income += {1: 50, 2: 150, 3: 100}[self.lvl('coalition')]
                if self.english_subsidies and self.tracks['coalition'] >= 15:
                    income += 100
            n_p = len([pid for pid in self.perso_of(c, ('free', 'fled')) if pid != 'louis_xvi' or self.king in ('free', 'kidnapped')])
            income = max(income, 100 + 50 * n_p)
            self.money[c] += income
        lost = sum(REGIONS[r][0] for r in REGIONS if r in self.revolt or r in self.coal or (
            self.control[r] == R and self.armies_in(r, ['catholic']) and not self.armies_in(r, REVOLUTIONARY)))
        self.gov_money = max(500, 2500 - lost)
        # objectifs
        for who, o in self.objectives.items():
            if who == GOV:
                if o.get('holder') != self.gov_holder:
                    continue
                if o['done']:
                    self.fame_adj(GOV, 1, 'objective')
                else:
                    self.fame_adj(GOV, -1, 'objective failed')
                    self.fame_adj(self.gov_holder, -1, 'gov objective failed')
                    if self.gov_partner:
                        self.fame_adj(self.gov_partner, -1, 'gov objective failed')
                self.stats['gov_obj_%s' % ('ok' if o['done'] else 'ko')] += 1
            else:
                self.fame_adj(who, 1 if o['done'] else -1, 'objective %s %s' % (o['kind'], o['target']))
                self.stats['obj_%s_%s' % (who, 'ok' if o['done'] else 'ko')] += 1
        for cond, fn in self.end_checks:
            if not cond(self):
                fn(self)
        # referendums de fin de tour (OS)
        if self.scenario == 'OS':
            if self.regime == 'Thermidor' and self.turn < 8:
                if self.referendum(M, 'Directorate'):
                    self.directorate_pending = True
            if self.regime == 'Mercy' and self.turn < 8:
                ok = ((not self.commune_raised and self.lvl('commune') == 1) or
                      (not self.foreign_war and not self.civil_war()) or MT in self.coup_outlaw)
                if ok and self.prefers(self.gov_holder, 'Directorate') and self.referendum(self.gov_holder, 'Directorate'):
                    self.install('Directorate', self.gov_holder, 'Mercy referendum')
        for c in list(self.temp_outlaw):
            if self.temp_outlaw[c] < self.turn + 1 and self.temp_outlaw[c] <= self.turn:
                pass
        if self.sole_power_until == self.turn and self.regime == 'Directorate':
            elig = [c for c in (F, G, MT) if self.official(c)]
            if elig and self.gov_holder != M:
                self.gov_partner = self.gov_holder
                self.gov_holder = M

    # ================================================================ victory
    def vp(self, regime=None):
        reg = regime or self.regime
        ph = self.paris_holder()
        n = {c: len(self.regions_of(c)) for c in CURRENTS}
        dead = self.king == 'dead'
        v = {}
        v[R] = (5 if self.king == 'kidnapped' else 0) + (5 if ph == R else 0) + self.fame[R] + n[R] + len(self.coal)
        v[F] = (5 if ph == F else 0) + (5 if reg == 'Legislative' else 0) + self.fame[F] + n[F] + self.deputies[F]
        v[M] = self.fame[M] + n[M] + self.deputies[M]
        v[G] = (5 if ph == G else 0) + (5 if reg in ('Convention', 'FFR') else 0) + self.fame[G] + n[G] + self.deputies[G]
        v[MT] = (5 if ph == MT else 0) + (5 if reg in ('Terror', 'Prairial', 'FROI') else 0) + \
            max(5 if dead else 0, self.deputies[MT]) + self.fame[MT] + n[MT]
        v[SC] = (5 if ph == SC else 0) + (5 if self.commune_raised else 0) + \
            (5 if reg in ('Terror', 'Wrath', 'Prairial', 'FROI') else 0) + \
            max(5 if dead else 0, self.deputies[SC]) + self.fame[SC] + n[SC]
        return v

    def outcome(self, regime=None):
        reg = regime or self.regime
        v = self.vp(reg)
        if reg == 'Vendemiaire' or v[R] >= 25:
            return R, v, ALSO_RANS[(R, None)], 'Royalist 25+'
        camp = {}
        for c in (F, M):
            camp[c] = 'reac' if v[c] >= 25 else 'rev'
        for c in (G, MT, SC):
            camp[c] = 'rev' if v[c] >= 25 else 'reac'
        rev = sum(1 for x in camp.values() if x == 'rev')
        majority = 'rev' if rev >= 3 else 'reac'
        fam = VICTORY_FAMILY[reg]
        if fam == 'Legislative':
            w = (F if v[F] >= v[M] else M) if majority == 'reac' else G
        elif fam == 'Convention':
            w = M if majority == 'reac' else (MT if v[MT] >= v[G] else G)
        elif fam == 'Terror':
            w = M if majority == 'reac' else (MT if v[MT] >= v[SC] else SC)
        elif fam == 'Thermidor':
            w = (F if v[F] >= v[M] else M) if majority == 'reac' else G
        else:  # Directorate
            if majority == 'reac':
                w = F if v[F] >= v[M] else M
            else:
                w = G if v[G] >= v[MT] else MT
        tfam = fam
        if fam == 'Directorate':
            tfam = 'Terror' if w == MT else 'Thermidor'
        ranks = ALSO_RANS.get((w, tfam))
        if ranks is None:
            ranks = ALSO_RANS.get((w, 'Thermidor')) or ALSO_RANS.get((w, 'Terror'))
        return w, v, ranks, majority

    def rank_under(self, c, regime):
        w, v, ranks, _ = self.outcome(regime)
        return ranks[IDX[c]]

    def prefers(self, c, regime):
        return self.rank_under(c, regime) < self.rank_under(c, self.regime) or (
            self.rank_under(c, regime) == self.rank_under(c, self.regime) and
            self.vp(regime)[c] > self.vp()[c])

    def best_regime(self, c, options):
        return min(options, key=lambda r: (self.rank_under(c, r), -self.vp(r)[c]))

    def final_victory(self):
        w, v, ranks, majority = self.outcome()
        self.winner = w
        self.final_vp = v
        self.final_ranks = dict(zip(CURRENTS, ranks))
        self.majority = majority
        self.log('FINAL: regime %s, winner %s, VP %s' % (
            self.regime, SHORT[w], ', '.join('%s %d' % (SHORT[c], v[c]) for c in CURRENTS)))

    # ================================================================ IA : planification
    def mv(self, c):
        """valeur d'un assignat en VP (decroit jusqu'a 0 au dernier tour)"""
        if c == GOV:
            return 0.0012
        return 0.004 * max(0, 8 - self.turn) / 7.0

    def maint_reserve(self):
        return 100 * self.k() * len([a for a in self.rev_armies() if self.armies[a]['kind'] != 'temp'])

    def reserve(self, c):
        r = 0 if self.turn >= 7 else 100 * self.k()
        if c == R:
            r += 100 * self.k() * sum(1 for s in self.armies.values() if s['kind'] == 'catholic')
        return r

    def regime_gain(self, c, controller):
        """gain (en VP-equivalents) pour c du regime que 'controller' pourrait
        installer grace a la Commune."""
        reg = self.regime
        lv = self.lvl('commune')
        opts = []
        if reg == 'Legislative' and controller in (G, MT, SC):
            opts = ['Convention']
            if (controller == SC and lv >= 2) or (controller == MT and lv == 3):
                opts.append('Terror')
            scale = 1.0 if self.paris_threatened() else (0.5 if self.tracks['coalition'] >= 12 or self.foreign_war else 0.25)
        elif reg in ('Convention', 'Mercy') and controller in (MT, SC):
            opts = ['Terror']
            scale = 1.0 if (self.foreign_war and self.civil_war()) else 0.4
        else:
            return 0.0
        best = self.best_regime(controller, opts)
        return 4.0 * scale * (self.rank_under(c, reg) - self.rank_under(c, best))

    def region_value(self, c, r):
        v = 1.0 + REGIONS[r][0] / 100.0 * 0.3 * max(1, self.turns_left()) / 4.0
        if r == 'Paris':
            v += 5 if c != M else 0
        if c in (F, M, G) or (c in (MT, SC) and self.regime not in ('Legislative',)):
            v += 0.5
        prev = self.effective_control(r)
        if prev and prev != c:
            v -= self.rel(c, prev) * 1.5
        return v

    def pers_value(self, pid):
        v = 2.0 + 0.4 * len(PERSO[pid]['influence'])
        if pid in GENERALS:
            v += 1.5
        if pid == 'louis_xvi':
            v = 5.0 if self.regime == 'Legislative' else 0.5
        return v

    def best_n(self, value, fame, results, cost, c):
        """nombre de jets qui maximise l'esperance"""
        best = (0, 0.0, 0.0)
        mvc = self.mv(c)
        money = self.money[c] if c != GOV else self.gov_money
        for n in (1, 2, 3):
            if cost * n > money:
                break
            p = 1 - (1 - p_result(fame, results)) ** n
            ev = value * p - mvc * cost * n
            if ev > best[1] + 0.05:
                best = (n, ev, p)
        return best

    def arrest_risk(self, c, pid, r):
        if self.gov_holder == c or not self.arrestable(pid):
            return 0.0
        s = self.p[pid]
        m = 0
        if self.effective_control(r) == c:
            m -= 4
        if r in PERSO[pid]['influence']:
            m -= 2
        if self.p_outlaw(pid) and r == 'Paris':
            m += 5
        harsh = self.regime in ('Terror', 'Wrath', 'Prairial')
        return p_result(self.fame[GOV] + m, 'AB' if harsh else 'A') * 0.6

    def plan_current(self, c):
        plan = {'regional': [], 'persuade': [], 'removals': []}
        self.plans[c] = plan
        pids = [pid for pid in self.perso_of(c) if pid != 'louis_xvi']
        k = self.k()
        human = c == self.human
        if human:
            def best_n(val, f, res, cost, c_):  # l'humain voit toutes les actions possibles
                return (1, 0.0, p_result(f, res)) if cost <= self.money[c] else (0, 0.0, 0.0)
        else:
            best_n = self.best_n
        budget = self.money[c] - self.reserve(c)
        fame = self.fame[c] + self.cur_bonus(c)
        cands = []
        official = self.official(c)
        for r in REGIONS:
            infl = [pid for pid in pids if r in PERSO[pid]['influence']]
            others = [pid for pid in pids if pid not in infl]
            choices = []
            if infl:
                choices.append(tuple(infl[:1]))
                if len(infl) >= 2:
                    choices.append(tuple(infl[:2]))
            if others:
                choices.append((others[0],))
            for group in choices:
                bonus = sum(2 for pid in group if r in PERSO[pid]['influence'])
                if r == 'Paris':
                    bonus += self.bonus[('paris_action', c)]
                if c == R and r in self.coal:
                    bonus += 2
                risk = max(self.arrest_risk(c, pid, r) for pid in group)
                ctl = self.effective_control(r)
                # complot
                if r not in self.revolt and r not in self.coal and ctl != c and not (r == 'Paris' and self.commune_raised):
                    f = fame + bonus + (2 if ctl is None else 0)
                    val = self.region_value(c, r)
                    n, ev, p = best_n(val * (1 - risk), f, 'A', 100 * k, c)
                    if n:
                        cands.append(dict(kind='plot', region=r, pids=group, n=n, cost=100 * k * n, ev=ev, p=p))
                # revolte
                if not official and r not in self.revolt and (r != 'Paris' or (c == R and r in self.coal)) and \
                        (not self.armies_in(r, list(REVOLUTIONARY) + list(ENEMY)) or (c == R and r in self.coal)) and ctl != c:
                    f = fame + bonus + (2 if REGIONS[r][1] else 0)
                    val = self.region_value(c, r) * 0.9
                    if c in (R, MT, SC):
                        val += 0.8 + (1.0 if len(self.revolt) == 3 else 0)
                    if self.gov_holder != c:
                        val += REGIONS[r][0] / 400.0
                    pa = p_result(f, 'A')
                    pb = p_result(f, 'B')
                    vv = val * pa + (0.6 + (0.5 if ctl and REL[c].get(ctl, 0) < -0.3 else 0)) * pb
                    eff_val = vv / max(0.01, (pa + pb))
                    n, ev, p = best_n(eff_val * (1 - risk), f, 'AB', 150 * k, c)
                    if n:
                        cands.append(dict(kind='revolt', region=r, pids=group, n=n, cost=150 * k * n, ev=ev, p=p))
                # suppression de revolte
                if r in self.revolt and ctl != c and not self.armies_in(r, ['allied']):
                    f = fame + bonus - 2
                    val = self.region_value(c, r)
                    n, ev, p = best_n(val * (1 - risk), f, 'A', 150 * k, c)
                    if n:
                        cands.append(dict(kind='suppress', region=r, pids=group, n=n, cost=150 * k * n, ev=ev, p=p))
                # Commune
                if r == 'Paris' and self.can_commune(c) and not self.paris_occupied():
                    lv = self.lvl('commune')
                    if not self.commune_raised:
                        f = fame + bonus + self.commune_penalty(c)
                        val = (5 if c != M else 1) + (5 if c == SC else 0) + max(0.0, self.regime_gain(c, c))
                        res = 'A' if lv == 1 else ('A' if lv == 2 else 'AB')
                        n, ev, p = best_n(val * (1 - risk), f, res, 200 * k, c)
                        if n:
                            cands.append(dict(kind='commune_raise', region=r, pids=group, n=n, cost=200 * k * n, ev=ev, p=p))
                    elif self.commune_ctrl != c:
                        f = fame + bonus + self.commune_penalty(c) - 2
                        val = (5 if c != M else 1) - self.regime_gain(c, self.commune_ctrl) - (5 if c == SC else 0)
                        res = 'AB' if lv == 1 else 'A'
                        n, ev, p = best_n(val * (1 - risk), f, res, 200 * k, c)
                        if n:
                            cands.append(dict(kind='commune_suppress', region=r, pids=group, n=n, cost=200 * k * n, ev=ev, p=p))
        # persuasion de personnalites
        pcands = []
        for pid, s in self.p.items():
            if s['holder'] == c or s['status'] in ('dead', 'exiled'):
                continue
            if c not in ({PERSO[pid]['main']} | PERSO[pid]['secondary']):
                continue
            if pid == 'louis_xvi' and (self.king != 'free' or self.regime != 'Legislative'):
                continue
            if s['status'] == 'prison' and not (self.outlawed(s['holder']) and not self.outlawed(c)):
                continue
            f = fame + self.bonus[('persuade', c)] - (0 if c == PERSO[pid]['main'] else 2)
            val = self.pers_value(pid) * (1.0 - self.rel(c, s['holder']))
            n, ev, p = best_n(val, f, 'A', 100 * k, c)
            if n:
                pcands.append(dict(kind='persuade', target=pid, n=n, cost=100 * k * n, ev=ev, p=p))
        # expulsion (courants hors Assemblee)
        rcands = []
        if not official:
            for pid, s in self.p.items():
                if s['holder'] == c or s['status'] != 'free' or pid == 'louis_xvi':
                    continue
                # position connue seulement si deja placee (les courants plus haut dans l'ordre)
                if s['loc'] and self.effective_control(s['loc']) == c:
                    f = fame - (2 if s['loc'] in PERSO[pid]['influence'] else 0)
                    val = self.region_value(c, s['loc']) * 0.4
                    n, ev, p = best_n(val, f, 'AB', 100 * k, c)
                    if n:
                        rcands.append(dict(kind='remove', target=pid, n=n, cost=100 * k * n, ev=ev, p=p))
        allc = cands + pcands + rcands
        allc.sort(key=lambda x: -x['ev'] / max(1, x['cost']) * 100 - x['ev'])
        if human:
            allc = self.human_plan(c, allc)
        used = set()
        regions_done = set()
        spent = 0
        chosen = []
        if human:
            budget = self.money[c]
        for a in allc:
            if spent + a['cost'] > budget:
                continue
            if 'pids' in a:
                if any(pid in used for pid in a['pids']) or (a['region'], a['kind']) in regions_done:
                    continue
                if a['kind'] in ('plot', 'revolt') and any(x.get('region') == a['region'] and x['kind'] in ('plot', 'revolt') for x in chosen):
                    continue
            if a['kind'] == 'persuade' and any(x.get('target') == a['target'] for x in chosen):
                continue
            if a['kind'] == 'remove' and any(x.get('target') == a['target'] for x in chosen):
                continue
            chosen.append(a)
            spent += a['cost']
            if 'pids' in a:
                used.update(a['pids'])
                regions_done.add((a['region'], a['kind']))
        # objectif : action la plus probable parmi celles choisies (ou la meilleure hors budget)
        obj = None
        cand_obj = [a for a in chosen if a['kind'] in ('plot', 'revolt', 'suppress', 'persuade', 'commune_raise', 'commune_suppress')]
        law = None if human else self.choose_law(c) if self.official(c) and (LAW_PROPOSERS[self.regime] in ('currents', 'both') or (self.rules == 'FR' and self.regime == 'Legislative')) else None
        best_p = -1
        for a in cand_obj:
            if a['p'] > best_p:
                best_p = a['p']
                obj = a
        if law:
            pl = self.law_pass_prob(c, law)
            if pl > best_p:
                obj = dict(kind='law', target=law, p=pl)
        if obj is None:
            fallback = sorted(cands + pcands, key=lambda x: -x['p'])
            obj = fallback[0] if fallback else dict(kind='plot', target='Paris', p=0)
        target = obj.get('target') or obj.get('region')
        kind = obj['kind'] if obj['kind'] != 'remove' else 'plot'
        self.objectives[c] = dict(kind=kind, target=target, done=False)
        # execution du plan : placement
        for a in chosen:
            if a['kind'] == 'persuade':
                plan['persuade'].append((a['target'], a['n']))
            elif a['kind'] == 'remove':
                plan['removals'].append((a['target'], a['n']))
            else:
                for pid in a['pids']:
                    self.p[pid]['loc'] = a['region']
                plan['regional'].append(a)
        self.place_idle(c, used)

    KIND_FR = {'plot': 'Complot', 'revolt': 'Fomenter une révolte', 'suppress': 'Calmer une révolte',
               'commune_raise': 'Soulever la Commune', 'commune_suppress': 'Réprimer la Commune',
               'persuade': 'Persuader', 'remove': 'Expulser'}

    def human_plan(self, c, allc):
        allc = sorted(allc, key=lambda a: (a['kind'] in ('persuade', 'remove'), a.get('region', ''), a['kind']))
        opts = []
        for a in allc:
            if 'pids' in a:
                who = ', '.join(PERSO[pid]['label'] for pid in a['pids'])
                label = '%s : %s (%s)' % (self.KIND_FR[a['kind']], a['region'], who)
            else:
                label = '%s : %s' % (self.KIND_FR[a['kind']], PERSO[a['target']]['label'])
            infl = 'pids' not in a or any(a['region'] in PERSO[pid]['influence'] for pid in a['pids'])
            opts.append(dict(label=label, cost=a['cost'], p=round(a['p'], 3), kind=a['kind'],
                             region=a.get('region'), pids=list(a.get('pids', ())), infl=infl))
        ans = self.ask('plan', 'Choisis tes actions du tour (budget %d assignats). Une personnalité '
                       'ne fait qu\'une action ; les autres sont placées automatiquement.' % self.money[c],
                       opts, multi=True)
        chosen = []
        for i, n in ans:
            a = dict(allc[i])
            n = max(1, min(3, int(n)))
            a['n'] = n
            a['p'] = 1 - (1 - a['p']) ** n
            a['cost'] = a['cost'] * n
            a['ev'] = 1e6 - len(chosen)  # garde l'ordre choisi
            chosen.append(a)
        return chosen

    def place_idle(self, c, used):
        idle = [pid for pid in self.perso_of(c) if pid not in used and pid != 'louis_xvi']
        if self.gov_holder == c or self.gov_partner == c:
            if not any(self.p[pid]['loc'] == 'Paris' for pid in self.perso_of(c)) and idle:
                pid = min(idle, key=lambda x: (self.arrestable(x), self.pers_value(x)))
                self.p[pid]['loc'] = 'Paris'
                idle.remove(pid)
        # generaux vendeens
        if c == R:
            for g in [x for x in idle if x in GENERALS]:
                if self.clergy_iii or any(s['kind'] == 'catholic' for s in self.armies.values()):
                    cath = [s['region'] for s in self.armies.values() if s['kind'] == 'catholic']
                    spot = cath[0] if cath and not any(self.p[x]['loc'] == cath[0] for x in GENERALS) else \
                        min(VENDEE, key=lambda r: (self.armies_in(r, REVOLUTIONARY) != [], self.control[r] != R))
                    self.p[g]['loc'] = spot
                    idle.remove(g)
        # coups militaires : placer avec une armee
        if self.scenario == 'OS':
            tgt = self.military_target(c)
            if tgt and idle:
                regs = [self.armies[a]['region'] for a in self.rev_armies() if not self.armies_in(self.armies[a]['region'], ENEMY)]
                if regs:
                    reg = min(regs, key=lambda r: self.dist(r, 'Paris'))
                    for pid in [x for x in idle if x not in NEVER_MILITARY_COUP and not self.p_outlaw(x)][:2]:
                        self.p[pid]['loc'] = reg
                        idle.remove(pid)
        for pid in idle:
            if self.regime in DEPUTY_SWITCH and self.arrest_risk(c, pid, 'Paris') < 0.08 and \
                    sum(1 for x in self.perso_of(c) if self.p[x]['loc'] == 'Paris') < 2:
                self.p[pid]['loc'] = 'Paris'
                continue
            own = self.regions_of(c)
            if self.popular_coup_plan(c) and self.arrest_risk(c, pid, 'Paris') < 0.15:
                self.p[pid]['loc'] = 'Paris'
                continue
            spots = sorted(REGIONS, key=lambda r: (self.arrest_risk(c, pid, r), r not in own,
                                                   r not in PERSO[pid]['influence'], self.rng.random()))
            self.p[pid]['loc'] = spots[0]

    def military_target(self, c):
        reg = self.regime
        table_ = {('Legislative', G), ('Convention', MT), ('Terror', M), ('Wrath', M), ('Mercy', M),
                  ('Mercy', MT), ('Directorate', MT), ('FFR', MT), ('FROI', M)}
        if (reg, c) not in table_ or self.outlawed(c):
            return None
        tgt = {'Legislative': 'Convention', 'Convention': 'Terror', 'Terror': 'Mercy', 'Wrath': 'Thermidor',
               'Directorate': 'Prairial', 'FFR': 'Terror', 'FROI': 'Thermidor'}.get(reg)
        if reg == 'Mercy':
            tgt = 'Directorate' if c == M else 'Terror'
        if tgt and self.rank_under(c, tgt) < self.rank_under(c, reg):
            return tgt
        return None

    def popular_coup_plan(self, c):
        if self.scenario != 'OS' and not (self.regime == 'Legislative' and c in (F, G)):
            return False
        for kind in ('popular', 'limited'):
            opt = self.coup_option(c, kind)
            if opt:
                return True
        return False

    def choose_law(self, c):
        best, bu = None, 0.3
        for law in LAWS:
            if law in ('trial',) and not self.law_allowed(c, law):
                continue
            if not self.law_allowed(c, law):
                continue
            eff = self.law_effects(c, law)
            u = self.law_util(c, eff)
            p = self.law_pass_prob(c, law)
            ev = u * p - (1 - p) * (1.2 if LAW_VOTE[self.regime] == 'fame' else 0) - 50 * self.k() * self.mv(c)
            cost = LAWS[law][0] * self.k()
            if cost > self.gov_money:
                continue
            if ev > bu:
                best, bu = law, ev
        return best

    def human_law(self, c):
        laws = [law for law in LAWS if law != 'trial' and self.law_allowed(c, law)]
        if self.money[c] < 50 * self.k():
            return None
        opts = [dict(label=law_label(law), p=round(self.law_pass_prob(c, law), 2)) for law in laws]
        opts.append(dict(label='Ne proposer aucune loi'))
        i = self.ask('law', 'Proposer une loi (%d assignats) ?' % (50 * self.k()), opts)
        return laws[i] if i < len(laws) else None

    def law_pass_prob(self, who, law):
        eff = self.law_effects(who, law)
        proposer = self.gov_holder if who == GOV else who
        if LAW_VOTE[self.regime] == 'deputies':
            yes = no = 0
            for c in CURRENTS:
                n = self.deputies[c]
                if c == proposer or self.law_util(c, eff) > 0:
                    yes += n
                else:
                    no += n
            if law in ('usages', 'nat_goods', 'worship', 'anti_emigrants', 'confiscation', 'safety') and \
                    self.regime == 'Legislative' and self.king == 'free':
                kh = self.holder('louis_xvi')
                if kh != proposer:
                    return 0.2 if yes > no else 0.0
            return 0.95 if yes > no else (0.5 if yes == no else 0.02)
        base = self.fame[GOV] if who == GOV and self.regime != 'Convention' else self.fame[proposer]
        mod = self.bonus['votes']
        for c in CURRENTS:
            if c == proposer:
                mod += 3 if (self.commune_raised and self.commune_ctrl == c) else (2 if c == M else 1)
                continue
            u = self.law_util(c, eff)
            sgn = 1 if u > 0.2 else (-1 if u < -0.2 else 0)
            if self.commune_raised and self.commune_ctrl == c:
                mod += 3 * sgn
            elif c == M and self.regime != 'Prairial':
                mod += 2 * sgn
            elif self.official(c):
                mod += sgn
        if who == GOV:
            mod += self.lawmaker_bonus()
        return p_result(base + mod, 'AB')

    # ------------------------------------------------------------ IA gouvernement
    def plan_government(self):
        h = self.gov_holder
        plan = {'arrests': [], 'suppress': [], 'laws': [], 'suppress_commune': False}
        self.gov_plan = plan
        k = self.k()
        n_armies = len([a for a in self.rev_armies() if self.armies[a]['kind'] != 'temp'])
        budget = self.gov_money - n_armies * 100 * k - 200 * k
        best_obj = None
        # arrestations : personnalites des rivaux, deja placees ou non (on estime l'endroit le plus probable)
        targets = []
        for pid, s in self.p.items():
            if s['status'] != 'free' or s['holder'] == h or s['holder'] == self.gov_partner:
                continue
            if not self.arrestable(pid):
                continue
            harm = -self.rel(h, s['holder']) * self.pers_value(pid)
            p = p_result(self.fame[GOV] + (5 if self.p_outlaw(pid) else -2) + self.bonus['gov_police'], 'A')
            targets.append((harm * p, pid, p))
        targets.sort(reverse=True)
        for score, pid, p in targets[:4]:
            if score < 0.3 or budget < 100 * k:
                continue
            n = 2 if budget > 600 * k and score > 1 else 1
            plan['arrests'].append((pid, n))
            budget -= 100 * k * n
            if best_obj is None or p > best_obj[2]:
                best_obj = ('arrest', pid, p)
        for r in sorted(self.revolt, key=lambda r: -REGIONS[r][0]):
            if self.control[r] == h or budget < 150 * k:
                continue
            p = p_result(self.fame[GOV] - 2 + self.bonus['gov_police'], 'AB')
            if p > 0.25:
                plan['suppress'].append((r, 1))
                budget -= 150 * k
                if best_obj is None or p > best_obj[2]:
                    best_obj = ('suppress', r, p)
        free_n = len([a for a in self.rev_armies() if not self.armies[a]['pinned']])
        for r in {self.armies[a]['region'] for a in self.enemy_armies()}:
            en = len(self.armies_in(r, ENEMY))
            if free_n > en:
                p = sum(pr for s, pr in __import__('lpd_data').P2D6.items()
                        if table(min(12, s + free_n - en), 13) == 'A')
                if best_obj is None or p > best_obj[2]:
                    best_obj = ('army', r, p)
        if self.commune_raised and self.commune_ctrl not in (h, None) and REL[h].get(self.commune_ctrl, 0) <= -0.3:
            if len([a for a in self.rev_armies() if not self.armies[a]['pinned']]) >= 3:
                plan['suppress_commune'] = True
        if LAW_PROPOSERS[self.regime] in ('gov', 'both') and self.regime in (
                'Terror', 'Thermidor', 'Wrath', 'Mercy', 'Directorate', 'Prairial'):
            laws = self.gov_laws(preview=True)
            if laws:
                p = self.law_pass_prob(GOV, laws[0])
                if best_obj is None or p > best_obj[2]:
                    best_obj = ('law', laws[0], p)
        if best_obj is None and targets:
            _, pid, p = max(targets, key=lambda t: t[2])
            best_obj = ('arrest', pid, p)
        if best_obj is None:
            best_obj = ('law', 'civic', 0)
        if best_obj[0] == 'arrest':
            plan['arrests'] = [(x, n) for x, n in plan['arrests'] if x != best_obj[1]]
            plan['arrests'].insert(0, (best_obj[1], 3 if self.gov_money > 1500 * k else 2))
        if best_obj[0] == 'suppress':
            plan['suppress'] = [(x, n) for x, n in plan['suppress'] if x != best_obj[1]]
            plan['suppress'].insert(0, (best_obj[1], 3 if self.gov_money > 1500 * k else 2))
        self.objectives[GOV] = dict(kind=best_obj[0], target=best_obj[1], done=False, holder=h)

    def gov_laws(self, preview=False):
        h = self.gov_holder
        maxn = 3
        scored = []
        for law in LAWS:
            if not self.law_allowed(GOV, law):
                continue
            eff = self.law_effects(GOV, law)
            u = self.law_util(h, eff)
            if law == 'trial':
                u = self.law_util(h, eff) + 0.5
            p = self.law_pass_prob(GOV, law)
            fail_cost = 1.0 if LAW_VOTE[self.regime] == 'fame' else 0
            if self.regime in ('Terror', 'Wrath') and h != M:
                fail_cost += 3.0 * (1 + self.rejected_terror)
            cost = LAWS[law][0] * self.k()
            if cost > self.gov_money - 100 * self.k() * len(self.rev_armies()):
                continue
            ev = u * p - (1 - p) * fail_cost
            scored.append((ev, law))
        scored.sort(reverse=True)
        chosen = [l for ev, l in scored[:maxn] if ev > 0.3]
        if not chosen and scored and self.rules == 'FR' and LAW_PROPOSERS[self.regime] == 'gov':
            chosen = [scored[0][1]]  # VF : le Gouvernement doit proposer au moins une loi
        return chosen
