# PunchA: a fast straight LEFT jab, 12 frames at 30 fps, in place. Full extension on frame 3, held on 4, back by 7.
#   blender -b --factory-startup --python Art/Blender/clip_punch_a.py [-- norender noexport]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}
AL = C.ARMLEN['L']

# A pose is a dict of tuples. Anything left out is taken from NEUTRAL.
#   body  (dx, fwd, dz, pitch, lean, twist)      spine / neck (x, y, z)
#   fL/fR (x, fwd, up, pitch, yaw)               cL/cR (up, back)
#   hL/hR (out, fwd, up, pron, curl, bend)       eL/eR elbow pole (outward, forward, up)
NEUTRAL = dict(body=(0, 0, -1.2, 0, 0, 0), spine=(0, 0, 0), neck=(0, 0, 0),
               fL=(10.5, 0, 0, 0, 8), fR=(-10.5, 0, 0, 0, 8), cL=(14, 3), cR=(14, 3),
               hL=(7, 3, HANG['L'], 62, 0.34, 0), eL=(0.35, -1.0, -0.1),
               hR=(7, 3, HANG['R'], 62, 0.34, 0), eR=(0.35, -1.0, -0.1))


def P(**kw):
    d = dict(NEUTRAL); d.update(kw); return d


GUARD_R = (-4, 18, -4, 80, 1.0, 0)
GUARD_E = (0.45, -0.25, -1.0)

HIT = P(body=(1.5, 5, -4.0, 5, 0, -16), spine=(3, 0, -20), neck=(-3, 0, 30),
        cL=(16, -6), cR=(16, 5),
        hL=(-9, AL * 0.985, -1, 118, 1.0, 0), eL=(1.0, 0.0, -0.55),
        hR=GUARD_R, eR=GUARD_E)
OUT = P(body=(1.0, 3, -3.0, 3, 0, -9), spine=(2, 0, -10), neck=(-2, 0, 16),
        cL=(15, -2), cR=(15, 4),
        hL=(-2, AL * 0.60, -10, 100, 1.0, 0), eL=(0.9, -0.3, -0.7),
        hR=(-2, 13, -16, 76, 0.9, 0), eR=GUARD_E)
HOLD = P(body=(1.5, 5.5, -4.2, 5.5, 0, -17), spine=(3, 0, -21), neck=(-3, 0, 31),
         cL=(16, -6), cR=(16, 5),
         hL=(-9, AL * 0.975, -1.5, 118, 1.0, 0), eL=(1.0, 0.0, -0.55),
         hR=GUARD_R, eR=GUARD_E)
BACK = P(body=(0.8, 2.5, -3.2, 3, 0, -5), spine=(2, 0, -6), neck=(-2, 0, 9),
         cL=(15, 1), cR=(15, 4),
         hL=(1, 20, -12, 82, 1.0, 0), eL=(0.5, -0.5, -1.0),
         hR=(-4, 16, -10, 80, 1.0, 0), eR=GUARD_E)
SETTLE = P(body=(0.3, 0.8, -2.0, 1, 0, -1), spine=(1, 0, -2), neck=(-1, 0, 3),
           hL=(8, 7, -40, 64, 0.65, 0), eL=(0.4, -0.9, -0.35),
           hR=(8, 7, -39, 64, 0.65, 0), eR=(0.4, -0.9, -0.35))

KEYS = [(1, NEUTRAL), (2, OUT), (3, HIT), (4, HOLD), (6, BACK), (9, SETTLE), (12, NEUTRAL)]


def pose_at(f):
    if f <= KEYS[0][0]: return KEYS[0][1]
    if f >= KEYS[-1][0]: return KEYS[-1][1]
    for (f0, a), (f1, b) in zip(KEYS, KEYS[1:]):
        if f0 <= f <= f1:
            t = (f - f0) / float(f1 - f0)
            if f1 - f0 > 1: t = t * t * (3 - 2 * t)
            return {k: tuple(p + (q - p) * t for p, q in zip(a[k], b[k])) for k in a}


def apply(p):
    b = p['body']; C.body(dx=b[0], fwd=b[1], dz=b[2], pitch=b[3], lean=b[4], twist=b[5])
    C.spine(*p['spine']); C.neck(*p['neck'])
    for s in 'LR':
        x, fw, up, pt, yw = p['f' + s]; C.foot(s, x=x, fwd=fw, up=up, pitch=pt, yaw=yw)
    for s in 'LR':
        C.clav(s, *p['c' + s])
        o, fw, up, pr, cu, bd = p['h' + s]
        C.hand(s, out=o, fwd=fw, up=up, pron=pr, curl=cu, elbow=p['e' + s])
        if abs(bd) > 1e-6: C.wrist(s, bend=bd)


def build(f, u):
    apply(pose_at(f))


C.author('PunchA', frames=12, build=build, loop=False, sheet_frames=12)
