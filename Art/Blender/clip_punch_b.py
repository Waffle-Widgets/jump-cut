# PunchB: the RIGHT cross that follows the jab, 12 frames at 30 fps, in place. Hips and chest turn hard to his left,
# the right heel lifts and pivots, full extension on frame 4, held on 5.
#   blender -b --factory-startup --python Art/Blender/clip_punch_b.py [-- norender noexport]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}
AL = C.ARMLEN['R']

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


GUARD_L = (-4, 17, -4, 80, 1.0, 0)
GUARD_E = (0.45, -0.25, -1.0)
# hand() works in WORLD directions from the shoulder. With the chest turned 60 degrees the left shoulder has swung
# back, so the same guard has to be asked for further out and less far forward or the fist ends up inside his neck.
GUARD_T = (12, 13, -4, 80, 1.0, 0)

# wind-up: a hair of counter-turn, the right fist comes up by the ribs
LOAD = P(body=(-1.0, 0, -3.0, 2, 0, -6), spine=(2, 0, -6), neck=(-1, 0, 10),
         hR=(4, 4, -24, 80, 1.0, 0), eR=(0.5, -1.0, -0.4),
         hL=(0, 14, -12, 76, 0.9, 0), eL=GUARD_E)
OUT = P(body=(1.5, 3, -4.0, 4, 0, 14), spine=(3, 0, 12), neck=(-2, 0, -22),
        fR=(-10.5, 1.0, 4.9, 16, -4),
        cR=(15, -2), cL=(15, 4),
        hR=(-3, AL * 0.62, -8, 100, 1.0, 0), eR=(0.9, -0.3, -0.7),
        hL=(4, 17, -4, 80, 1.0, 0), eL=GUARD_E)
HIT = P(body=(3.0, 6, -5.0, 7, 0, 30), spine=(4, 0, 30), neck=(-4, 0, -50),
        fR=(-10.5, 2.0, 9.4, 32, -18),
        cR=(17, -8), cL=(16, 6),
        hR=(-12, AL * 0.985, -1, 118, 1.0, 0), eR=(1.0, 0.0, -0.55),
        hL=GUARD_T, eL=GUARD_E)
HOLD = P(body=(3.2, 6.5, -5.2, 7.5, 0, 32), spine=(4, 0, 31), neck=(-4, 0, -52),
         fR=(-10.5, 2.0, 9.7, 33, -19),
         cR=(17, -8), cL=(16, 6),
         hR=(-12, AL * 0.975, -1.5, 118, 1.0, 0), eR=(1.0, 0.0, -0.55),
         hL=GUARD_T, eL=GUARD_E)
BACK = P(body=(1.8, 3, -3.6, 4, 0, 12), spine=(2, 0, 10), neck=(-2, 0, -18),
         fR=(-10.5, 1.0, 4.9, 16, -6),
         cR=(15, 0), cL=(15, 4),
         hR=(1, 20, -12, 82, 1.0, 0), eR=(0.5, -0.5, -1.0),
         hL=(-3, 15, -9, 80, 1.0, 0), eL=GUARD_E)
SETTLE = P(body=(0.5, 0.8, -2.0, 1, 0, 2), spine=(1, 0, 2), neck=(-1, 0, -4),
           hL=(8, 7, -40, 64, 0.65, 0), eL=(0.4, -0.9, -0.35),
           hR=(8, 7, -39, 64, 0.65, 0), eR=(0.4, -0.9, -0.35))

KEYS = [(1, NEUTRAL), (2, LOAD), (3, OUT), (4, HIT), (5, HOLD), (7, BACK), (10, SETTLE), (12, NEUTRAL)]


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


C.author('PunchB', frames=12, build=build, loop=False, sheet_frames=12)
