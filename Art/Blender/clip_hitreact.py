# HitReact: struck from the front in the chest, 12 frames at 30 fps, in place. Chest and head snap back on frame 3,
# the head whips forward again by 5-6, the right foot takes one small step back for balance (down on frame 5, still
# until 8) and comes home by 12. Hands stay half open: he is not throwing anything.
#   blender -b --factory-startup --python Art/Blender/clip_hitreact.py [-- norender noexport]
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


SNAP = P(body=(0.5, -5, -2.5, -10, 0, 6), spine=(-15, 0, 7), neck=(-20, 2, 4),
         fR=(-11.5, -7, 4.0, 10, 8),
         cL=(22, -5), cR=(23, -6),
         hL=(13, 19, -25, 40, 0.2, 0), eL=(0.9, -0.5, -0.4),
         hR=(18, 5, -37, 50, 0.3, 0), eR=(0.8, -0.8, -0.1))
BACK_FOOT = (-12.0, -19, 0, 0, 12)
STAG = P(body=(-0.5, -8.5, -4.5, -2, 0, 4), spine=(-3, 0, 4), neck=(8, 1, 0),
         fR=BACK_FOOT,
         cL=(17, 2), cR=(17, 2),
         hL=(17, 10, -35, 52, 0.3, 0), eL=(0.7, -0.8, -0.2),
         hR=(13, -3, -42, 60, 0.35, 0), eR=(0.6, -1.0, 0.0))
SINK = P(body=(-0.8, -8.0, -5.5, 5, 0, 2), spine=(6, 0, 2), neck=(5, 0, 0),
         fR=BACK_FOOT,
         cL=(13, 3), cR=(13, 3),
         hL=(9, 8, -43, 62, 0.4, 0), eL=(0.5, -1.0, -0.1),
         hR=(9, 5, -44, 62, 0.4, 0), eR=(0.5, -1.0, -0.1))
HOME = P(body=(-0.3, -3.5, -2.8, 3, 0, 1), spine=(3, 0, 1), neck=(2, 0, 0),
         fR=(-11.0, -9, 3.5, 9, 9),
         hL=(8, 5, HANG['L'] + 3, 62, 0.36, 0), hR=(8, 5, HANG['R'] + 3, 62, 0.36, 0))

KEYS = [(1, NEUTRAL), (3, SNAP), (5, STAG), (8, SINK), (10, HOME), (12, NEUTRAL)]
LINEAR = {(1, 3)}                                          # the snap back is not eased


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


C.author('HitReact', frames=12, build=build, loop=False, sheet_frames=12)
