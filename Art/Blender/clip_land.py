# The player's landing: feet flat from the first frame, the knees take it by frame 3, then he stands up.
# The feet never move.
#   blender -b --factory-startup --python Art/Blender/clip_land.py [-- noexport norender]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

A = C.ARMLEN['L']
POLE = (0.5, -0.7, -0.7)


def P(**over):
    p = {'body': dict(dx=0.0, fwd=0.0, dz=-1.2, pitch=0.0, lean=0.0, twist=0.0),
         'spine': dict(x=0.0, y=0.0, z=0.0), 'neck': dict(x=0.0, y=0.0, z=0.0),
         'footL': dict(x=10.5, fwd=0.0, up=0.0, pitch=0.0, yaw=8.0, knee_out=0.22),
         'footR': dict(x=-10.5, fwd=0.0, up=0.0, pitch=0.0, yaw=8.0, knee_out=0.22),
         'handL': dict(out=7.0, fwd=3.0, up=-0.965 * A, pron=62.0, curl=0.34, elbow=(0.35, -1.0, -0.1), bend=0.0, side=0.0),
         'handR': dict(out=7.0, fwd=3.0, up=-0.965 * A, pron=62.0, curl=0.34, elbow=(0.35, -1.0, -0.1), bend=0.0, side=0.0)}
    for k, v in over.items(): p[k].update(v)
    return p


def mix(p, q, t):
    out = {}
    for k in p:
        out[k] = {}
        for n, v in p[k].items():
            w = q[k][n]
            out[k][n] = tuple(a + (b - a) * t for a, b in zip(v, w)) if isinstance(v, tuple) else v + (w - v) * t
    return out


def pose(p):
    C.body(**p['body']); C.spine(**p['spine']); C.neck(**p['neck'])
    for s in 'LR': C.foot(s, **p['foot' + s])
    for s in 'LR':
        h = dict(p['hand' + s]); b = h.pop('bend'); sd = h.pop('side')
        C.hand(s, **h); C.wrist(s, b, sd)


def at(u, tl):
    if u <= tl[0][0]: return tl[0][1]
    if u >= tl[-1][0]: return tl[-1][1]
    for (u0, p0), (u1, p1) in zip(tl, tl[1:]):
        if u0 <= u <= u1: return mix(p0, p1, C.smooth(u, u0, u1))


TOUCH = P(body=dict(dz=-6.0, pitch=7.0), spine=dict(x=3.0), neck=dict(x=2.0),
          handL=dict(out=0.50 * A, fwd=8.0, up=-0.70 * A, curl=0.36, elbow=POLE),
          handR=dict(out=0.48 * A, fwd=10.0, up=-0.68 * A, curl=0.36, elbow=POLE))
DEEP = P(body=dict(dz=-23.0, fwd=-6.0, pitch=22.0), spine=dict(x=14.0), neck=dict(x=-14.0),
         footL=dict(knee_out=0.34), footR=dict(knee_out=0.34),
         handL=dict(out=0.30 * A, fwd=0.46 * A, up=-0.62 * A, curl=0.45, elbow=POLE),
         handR=dict(out=0.26 * A, fwd=0.50 * A, up=-0.58 * A, curl=0.45, elbow=POLE))
SETTLE = P(body=dict(dz=-19.0, fwd=-5.0, pitch=17.0), spine=dict(x=11.0), neck=dict(x=-10.0),
           footL=dict(knee_out=0.32), footR=dict(knee_out=0.32),
           handL=dict(out=0.28 * A, fwd=0.38 * A, up=-0.70 * A, curl=0.42, elbow=POLE),
           handR=dict(out=0.25 * A, fwd=0.42 * A, up=-0.67 * A, curl=0.42, elbow=POLE))
TL = [(0.0, TOUCH), (2 / 11.0, DEEP), (4 / 11.0, SETTLE), (1.0, P())]


def build(f, u):
    pose(at(u, TL))


C.author('Land', frames=12, build=build, loop=False, sheet_frames=12)
