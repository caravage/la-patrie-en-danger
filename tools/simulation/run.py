# -*- coding: utf-8 -*-
"""Lance N parties et agrege les statistiques. Usage : python3 run.py HS 1000"""
import json
import os
import sys
import time
import traceback
from collections import Counter, defaultdict

from lpd_data import CURRENTS, SHORT
from lpd_engine import Game

if os.environ.get('PYTHONHASHSEED') != '0':
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)

scenario = sys.argv[1] if len(sys.argv) > 1 else 'HS'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 500
t0 = time.time()
res = []
errors = 0
for seed in range(N):
    try:
        g = Game(seed=seed, scenario=scenario).play()
    except Exception:
        errors += 1
        if errors <= 3:
            traceback.print_exc()
        continue
    fr = getattr(g, 'final_ranks', None)
    if g.winner == 'Royaliste' and g.ended_early:
        fr = {c: r for c, r in zip(CURRENTS, [1, 5, 6, 6, 6, 6])}
    res.append(dict(
        seed=seed, winner=g.winner, regime=g.regime, early=g.ended_early,
        history=g.regime_history, vp=getattr(g, 'final_vp', g.vp()), ranks=fr,
        majority=getattr(g, 'majority', None), king=g.king, tracks=dict(g.tracks),
        war=g.stats['war_turn'], stats=dict(g.stats), coups=g.coup_log,
        fame=g.fame_history, regions=g.regions_history,
        laws=dict(g.laws_passed), dead=[p for p, s in g.p.items() if s['status'] == 'dead'],
        deputies=dict(g.deputies), final_fame=dict(g.fame), final_regions={c: len(g.regions_of(c)) for c in CURRENTS},
        paris=g.paris_holder(), commune=(g.commune_raised, g.commune_ctrl), coal=len(g.coal),
        gov_holder=g.gov_holder,
    ))
json.dump(res, open('results_%s.json' % scenario, 'w'))
print('%d games in %.1fs, %d errors' % (len(res), time.time() - t0, errors))
n = len(res)
w = Counter(r['winner'] for r in res)
print('\nWINNERS')
for c in CURRENTS:
    print('  %-12s %5.1f%%' % (c, 100 * w[c] / n))
print('\nAVERAGE RANK (1 = winner, 6 = last)')
for c in CURRENTS:
    print('  %-12s %.2f' % (c, sum(r['ranks'][c] for r in res) / n))
print('\nFINAL REGIME')
for k, v in Counter(r['regime'] for r in res).most_common():
    print('  %-12s %5.1f%%' % (k, 100 * v / n))
print('\nAVERAGE VP / median')
for c in CURRENTS:
    vals = sorted(r['vp'][c] for r in res)
    print('  %-12s avg %5.1f  med %3d  >=25: %4.1f%%' % (c, sum(vals) / n, vals[n // 2],
                                                     100 * sum(1 for v in vals if v >= 25) / n))
print('\nMAJORITY', Counter(r['majority'] for r in res))
print('KING', Counter(r['king'] for r in res))
print('WAR declared: %.1f%%, avg turn %.1f' % (
    100 * sum(1 for r in res if r['war']) / n,
    sum(r['war'] for r in res if r['war']) / max(1, sum(1 for r in res if r['war']))))
first = defaultdict(list)
for r in res:
    seen = set()
    for t, reg in r['history']:
        if reg not in seen:
            first[reg].append(t)
            seen.add(reg)
print('\nREGIMES REACHED (share of games, avg first turn)')
for reg, ts in sorted(first.items(), key=lambda x: -len(x[1])):
    print('  %-12s %5.1f%%  T%.1f' % (reg, 100 * len(ts) / n, sum(ts) / len(ts)))
print('\nWINNER x REGIME')
wr = Counter((r['regime'], r['winner']) for r in res)
for (reg, c), v in sorted(wr.items(), key=lambda x: -x[1])[:20]:
    print('  %-12s %-12s %5.1f%%' % (reg, c, 100 * v / n))
tot = Counter()
for r in res:
    tot.update(r['stats'])
print('\nPER-GAME AVERAGES')
for k in sorted(tot):
    if k in ('war_turn', 'kidnap', 'king_executed_turn', 'bankrupt_turn'):
        continue
    print('  %-28s %6.2f' % (k, tot[k] / n))
print('\nFINAL TRACKS avg', {t: round(sum(r['tracks'][t] for r in res) / n, 1) for t in res[0]['tracks']})
cl = Counter()
for r in res:
    for (t, reg, c, kind, tgt, ok) in r['coups']:
        cl[(kind, SHORT[c], reg, tgt, ok)] += 1
if cl:
    print('\nCOUPS (kind, who, regime, target, success): count')
    for k, v in cl.most_common(25):
        print('  ', k, v)
