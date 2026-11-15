# Finisher: the third hit, a rising RIGHT uppercut, 20 frames at 30 fps, in place. He drops and coils to his right on
# frames 2-4, drives up through 5-7, lands on frame 8 with the forearm upright and the fist at head height, holds 8-10,
# then comes down to neutral.
#   blender -b --factory-startup --python Art/Blender/clip_finisher.py [-- norender noexport]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}

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


# hand() works in WORLD directions from the shoulder, so every hand below is written for the chest turn of ITS pose.
COIL = P(body=(-2.5, -1, -10.0, 12, -2, -18), spine=(9, -4, -16), neck=(-8, 0, 30),
         cR=(10, 8), cL=(16, 0),
         hR=(13, -7, -40, 95, 1.0, 0), eR=(0.6, -1.0, 0.3),
         hL=(-11, 12, -9, 80, 1.0, 0), eL=(0.45, -0.25, -1.0))
COIL2 = P(body=(-2.8, -1.2, -11.0, 13, -2, -20), spine=(10, -4, -18), neck=(-9, 0, 33),
          cR=(9, 9), cL=(16, 0),
          hR=(13, -9, -41, 95, 1.0, 0), eR=(0.6, -1.0, 0.3),
          hL=(-11, 12, -9, 80, 1.0, 0), eL=(0.45, -0.25, -1.0))
DRIVE = P(body=(0.5, 2, -7.0, 6, 0, 6), spine=(4, 0, 4), neck=(-3, 0, -8),
          fR=(-10.5, 0.8, 4.0, 13, -4),
          cR=(12, 2), cL=(15, 3),
          hR=(-2, 20, -30, 45, 1.0, 0), eR=(0.5, -0.8, -0.7),
          hL=(2, 14, -10, 80, 1.0, 0), eL=(0.45, -0.25, -1.0))
HIT = P(body=(2.0, 4, -0.6, -3, 1, 28), spine=(-7, 0, 24), neck=(4, 0, -44),
        fR=(-10.5, 2.0, 9.4, 32, -16),
        cR=(18, -4), cL=(14, 6),
        hR=(-6, 26, 12, 12, 1.0, 0), eR=(0.35, -0.2, -1.0),
        hL=(13, 14, -30, 78, 1.0, 0), eL=(0.8, -0.6, -0.6))
HOLD = P(body=(2.2, 4.3, -0.3, -4, 1, 30), spine=(-8, 0, 25), neck=(5, 0, -46),
         fR=(-10.5, 2.0, 9.9, 34, -17),
         cR=(18.5, -4), cL=(14, 6),
         hR=(-6, 26, 14.5, 12, 1.0, 0), eR=(0.35, -0.2, -1.0),
         hL=(13, 14, -31, 78, 1.0, 0), eL=(0.8, -0.6, -0.6))
DOWN = P(body=(1.2, 2.5, -3.0, 2, 0, 12), spine=(1, 0, 10), neck=(0, 0, -18),
         fR=(-10.5, 1.0, 4.3, 14, -6),
         cR=(16, 0), cL=(15, 4),
         hR=(-2, 17, -10, 60, 1.0, 0), eR=(0.5, -0.5, -1.0),
         hL=(3, 13, -14, 78, 0.95, 0), eL=(0.45, -0.4, -0.9))
SETTLE = P(body=(0.4, 0.8, -2.2, 1, 0, 2), spine=(1, 0, 2), neck=(-1, 0, -4),
           hL=(8, 7, -40, 64, 0.65, 0), eL=(0.4, -0.9, -0.35),
           hR=(8, 7, -39, 64, 0.65, 0), eR=(0.4, -0.9, -0.35))

KEYS = [(1, NEUTRAL), (3, COIL), (4, COIL2), (6, DRIVE), (8, HIT), (10, HOLD), (13, DOWN), (17, SETTLE), (20, NEUTRAL)]
LINEAR = {(4, 6), (6, 8)}                                  # the drive up is not eased: it accelerates into the hit


def pose_at(f):
    if f <= KEYS[0][0]: return KEYS[0][1]
    if f >= KEYS[-1][0]: return KEYS[-1][1]
    for (f0, a), (f1, b) in zip(KEYS, KEYS[1:]):
        if f0 <= f <= f1:
            t = (f - f0) / float(f1 - f0)
            if f1 - f0 > 1 and (f0, f1) not in LINEAR: t = t * t * (3 - 2 * t)
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


C.author('Finisher', frames=20, build=build, loop=False, sheet_frames=12)
