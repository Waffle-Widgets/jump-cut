"""How closely does a poured cup match its goal?   python tools/latte_match.py [heart rosetta tulip]

Reads JumpCut/Saved/jcpy/latte_cup_<name>.txt (written by `latte_pie.py auto <name>`: the cup's surface read back out
of the game, 64 x 64) and lays it over the goal shape from tools/latte_goals.py.
  SHAPE    = the same after thickening both by 2 cells: compares outlines, so a striped rosetta is judged fairly
  overlap  = foam the two share / foam in either      (1.00 = identical)
  covered  = how much of the goal's foam the pour put foam on
  spill    = how much of the pour's foam is outside the goal
Prints both as a small picture: # both, g goal only, p pour only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
import latte_goals as G
sys.stdout = _stdout

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'JumpCut', 'Saved', 'jcpy')
GOAL = {'heart': G.goal_heart, 'rosetta': G.goal_rosetta, 'tulip': G.goal_tulip}
N = 64
for name in ([a for a in sys.argv[1:] if not a.startswith('-')] or ['heart', 'rosetta', 'tulip']):
    path = os.path.join(HERE, 'latte_cup_%s.txt' % name)
    if not os.path.exists(path):
        print('%-8s no cup file' % name); continue
    rows = open(path).read().split()
    gm = [[False] * N for _ in range(N)]
    pm = [[False] * N for _ in range(N)]
    for u in range(N):
        for v in range(N):
            x, y = (u + 0.5) / N - 0.5, (v + 0.5) / N - 0.5
            gm[u][v] = x * x + y * y < 0.2116 and bool(GOAL[name](x, y))
            pm[u][v] = rows[v][u] >= '4'

    def thick(m, r=2):
        return [[any(m[i][j] for i in range(max(0, u - r), min(N, u + r + 1)) for j in range(max(0, v - r), min(N, v + r + 1)))
                 for v in range(N)] for u in range(N)]
    tg, tp = thick(gm), thick(pm)
    sb = sum(tg[u][v] and tp[u][v] for u in range(N) for v in range(N))
    su = sum(tg[u][v] or tp[u][v] for u in range(N) for v in range(N))
    both = goal = pour = 0
    art = []
    for u in range(N - 1, -1, -1):                                   # print with x (u) up the page, y (v) across
        line = ''
        for v in range(N):
            x, y = (u + 0.5) / N - 0.5, (v + 0.5) / N - 0.5
            g = x * x + y * y < 0.2116 and GOAL[name](x, y)
            p = rows[v][u] >= '4'
            both += g and p; goal += bool(g); pour += p
            line += '#' if (g and p) else ('g' if g else ('p' if p else '.'))
        art.append(line[::1])
    union = goal + pour - both
    print('%-8s SHAPE %.2f   exact overlap %.2f   covered %.2f   spill %.2f   (goal %d, pour %d cells)' % (
        name, sb / max(1, su), both / max(1, union), both / max(1, goal), (pour - both) / max(1, pour), goal, pour))
    if '-q' not in sys.argv:
        print('\n'.join(a[8:56] for a in art[6:58:2]))
