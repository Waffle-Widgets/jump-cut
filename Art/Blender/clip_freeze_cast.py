# Freeze Frame, the player's time-stop: a director calling "cut". The right arm thrusts forward at shoulder height
# with the palm open to the front, the left fist pulls back to the hip, the stance braces; hold; back to neutral.
#   blender -b --factory-startup --python Art/Blender/clip_freeze_cast.py [-- noexport norender]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C
from mathutils import Vector

A = C.ARMLEN['L']


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


BEND = 68.0                                                # how far the wrist cocks back to show the palm
CAST = P(body=dict(dz=-7.0, fwd=3.0, pitch=5.0, twist=8.0), spine=dict(x=2.0, z=14.0), neck=dict(x=-2.0, z=-18.0),
         footL=dict(x=12.0, fwd=16.0, yaw=6.0, knee_out=0.25), footR=dict(x=-14.0, fwd=-12.0, yaw=30.0, knee_out=0.5),
         handL=dict(out=9.0, fwd=-0.30 * A, up=-0.60 * A, curl=0.92, elbow=(0.4, -1.0, 0.3)),
         handR=dict(out=0.10 * A, fwd=0.90 * A, up=-5.0, curl=0.0, elbow=(0.7, 0.0, -1.0)))


def _palm(p):
    C._state.clear(); pose(p)
    return C.carried(C.HAND['R'], Vector((0, -1, 0)))


# Find the forearm roll that turns the open palm to the floor with the arm out in front, then the sign of wrist
# bend that cocks it up to face forward. Worked out on the rig instead of guessed.
best = None
for pr in range(-180, 181, 5):
    q = mix(CAST, CAST, 0.0); q['handR']['pron'] = float(pr)
    sc = _palm(q).dot(Vector((0, 0, -1)))
    if best is None or sc > best[0]: best = (sc, float(pr))
CAST['handR']['pron'] = best[1]
sg = None
for sign in (1.0, -1.0):
    q = mix(CAST, CAST, 0.0); q['handR']['bend'] = sign * BEND
    sc = _palm(q).dot(Vector((0, -1, 0)))
    if sg is None or sc > sg[0]: sg = (sc, sign)
CAST['handR']['bend'] = sg[1] * BEND
C._state.clear()
print('FREEZECAST pron', best, 'bend sign', sg)

N = P()
WIND = mix(N, CAST, 0.4)                                   # frame 2: the hand is drawn in to the chest before the thrust
WIND['handR'].update(out=6.0, fwd=10.0, up=-0.42 * A, curl=0.5, elbow=(0.7, -0.5, -0.8))
WIND['footL']['up'] = 3.0
HOLD = mix(CAST, CAST, 0.0)
HOLD['body'].update(dz=-8.0, fwd=4.0); HOLD['handR'].update(fwd=0.92 * A)
BACK = mix(CAST, N, 0.6)                                   # on the way home the feet are picked up, not dragged
BACK['footL']['up'] = 3.5; BACK['footR']['up'] = 3.0
TL = [(0.0, N), (1 / 15.0, WIND), (3 / 15.0, CAST), (8 / 15.0, HOLD), (12 / 15.0, BACK), (1.0, N)]


def build(f, u):
    pose(at(u, TL))


C.author('FreezeCast', frames=16, build=build, loop=False, sheet_frames=7, stance=(0.15, 0.6))
