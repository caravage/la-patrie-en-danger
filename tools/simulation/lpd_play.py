# -*- coding: utf-8 -*-
"""Partie a un joueur humain contre 5 IA.

La partie est deterministe pour une graine donnee : chaque appel a step()
rejoue la partie depuis le debut avec les decisions deja prises, jusqu'a la
prochaine question posee au joueur (ou la fin de la partie). Utilise tel quel
par la page web (Pyodide) et par le mode console :

    python3 lpd_play.py Gironde 7
"""
import json
import sys

from lpd_data import CURRENTS, GOV, PERSO, REGIONS
from lpd_engine import LAW_FR, Game, NeedInput


def snapshot(g):
    return dict(
        turn=g.turn, regime=g.regime, gov_holder=g.gov_holder, gov_partner=g.gov_partner,
        tracks=dict(g.tracks), fame={c: g.fame[c] for c in CURRENTS + [GOV]},
        money=dict(g.money), gov_money=g.gov_money, deputies=dict(g.deputies),
        control={r: g.control[r] for r in REGIONS}, revolt=sorted(g.revolt), coal=sorted(g.coal),
        commune=dict(raised=g.commune_raised, ctrl=g.commune_ctrl), king=g.king,
        war=g.foreign_war, order=list(g.order), vp=g.vp(),
        objective=g.objectives.get(g.human), gov_objective=g.objectives.get(GOV),
        law_names=LAW_FR, official=[c for c in CURRENTS if g.official(c)],
        outlawed=[c for c in CURRENTS if g.outlawed(c)],
        personalities=[dict(id=pid, label=PERSO[pid]['label'], holder=s['holder'], status=s['status'],
                            loc=s['loc']) for pid, s in g.p.items()],
        armies=[dict(id=a, kind=s['kind'], region=s['region']) for a, s in g.armies.items()],
    )


def step(seed, human, answers, rules='FR'):
    g = Game(seed=seed, human=human, answers=answers, rules=rules)
    question = None
    try:
        g.play()
    except NeedInput as e:
        question = e.question
    out = dict(question=question, log=g.lines, state=snapshot(g), over=question is None)
    if question is None:
        out['winner'] = g.winner
        m = getattr(g, 'majority', None)
        out['majority'] = m if m in ('rev', 'reac') else None
    return out


def step_json(seed, human, answers_json, rules='FR'):
    return json.dumps(step(seed, human, json.loads(answers_json), rules))


def console(human, seed):
    answers = []
    shown = 0
    while True:
        r = step(seed, human, answers)
        for line in r['log'][shown:]:
            print(line)
        shown = len(r['log'])
        if r['over']:
            print('Vainqueur :', r['winner'])
            return
        q = r['question']
        print('\n>>> ' + q['prompt'])
        for i, o in enumerate(q['options']):
            extra = []
            if 'cost' in o:
                extra.append('%d as.' % o['cost'])
            if 'p' in o:
                extra.append('%d %%' % round(100 * o['p']))
            print('  %2d. %s %s' % (i, o['label'], ('[' + ', '.join(extra) + ']') if extra else ''))
        if q['multi']:
            raw = input('numéros (ex. "0 3x2 5"), vide = rien : ').split()
            ans = []
            for tok in raw:
                i, _, n = tok.partition('x')
                ans.append([int(i), int(n or 1)])
        else:
            ans = int(input('choix : '))
        answers.append(ans)


if __name__ == '__main__':
    console(sys.argv[1] if len(sys.argv) > 1 else 'Gironde', int(sys.argv[2]) if len(sys.argv) > 2 else 1)
