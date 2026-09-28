import json
import sys
from collections import Counter

from lpd_data import CURRENTS, SHORT

sc = sys.argv[1]
res = json.load(open('results_%s.json' % sc))
n = len(res)
print('=== %s : %d games ===' % (sc, n))
print('\nRANK DISTRIBUTION (%)  1..6')
for c in CURRENTS:
    d = Counter(r['ranks'][c] for r in res)
    print('  %-12s' % c, ' '.join('%5.1f' % (100 * d[k] / n) for k in range(1, 7)))
print('\nVP COMPONENTS (avg): fame / regions / deputies / Paris held')
for c in CURRENTS:
    f = sum(r['final_fame'][c] for r in res) / n
    g = sum(r['final_regions'][c] for r in res) / n
    d = sum(r['deputies'][c] for r in res) / n
    p = sum(1 for r in res if r['paris'] == c) / n
    print('  %-12s %5.1f  %5.1f  %5.1f  %5.1f%%' % (c, f, g, d, 100 * p))
print('  Coalition regions (Royalist VP): %.2f' % (sum(r['coal'] for r in res) / n))
print('\nFAME BY TURN (avg)')
print('  %-12s' % '', ' '.join('  T%d' % (t + 1) for t in range(8)))
for c in CURRENTS + ['Government']:
    row = []
    for t in range(8):
        vals = [r['fame'][t][c] for r in res if len(r['fame']) > t]
        row.append(sum(vals) / max(1, len(vals)))
    print('  %-12s' % c, ' '.join('%4.1f' % x for x in row))
print('\nREGIONS BY TURN (avg)')
for c in CURRENTS:
    row = []
    for t in range(8):
        vals = [r['regions'][t][c] for r in res if len(r['regions']) > t]
        row.append(sum(vals) / max(1, len(vals)))
    print('  %-12s' % c, ' '.join('%4.1f' % x for x in row))
print('\nWIN RATE BY FINAL REGIME')
by = Counter(r['regime'] for r in res)
for reg, k in by.most_common():
    w = Counter(r['winner'] for r in res if r['regime'] == reg)
    print('  %-12s (%4.1f%%): %s' % (reg, 100 * k / n, ', '.join('%s %d%%' % (SHORT[c], round(100 * v / k)) for c, v in w.most_common())))
print('\nKING', Counter(r['king'] for r in res))
laws = Counter()
for r in res:
    laws.update(r['laws'])
print('\nLAWS PASSED per game:', ', '.join('%s %.2f' % (k, v / n) for k, v in laws.most_common()))
dead = Counter()
for r in res:
    dead.update(r['dead'])
print('\nMOST OFTEN DEAD:', ', '.join('%s %d%%' % (k, round(100 * v / n)) for k, v in dead.most_common(10)))
print('\nFINAL GOV HOLDER', Counter(r['gov_holder'] for r in res))
