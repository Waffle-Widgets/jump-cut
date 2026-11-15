# PunchB: hit two of the combo - a RIGHT ROUNDHOUSE KICK to chest height, 12 frames at 30 fps. (The clip keeps the
# name PunchB so the game's montage still finds it.)
# He pivots on the planted left foot, the hips turn over to his left, the right knee whips up and through and the leg
# snaps out straight at chest height on frame 4 (overshoot) and is held on 5. The body tips away from the kick, the
# left fist guards in front of the chest, the right arm is flung down and back behind him. Then the leg folds, comes
# down, and he is back in the neutral stand on frame 12. The pelvis is in place on frames 1 and 12.
#   blender -b --factory-startup --python Art/Blender/clip_punch_b.py [-- norender noexport]
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C
from mathutils import Vector

HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}

# A pose is a dict of tuples. Anything left out is taken from NEUTRAL.
#   body  (dx, fwd, dz, pitch, lean, twist)      spine / neck (x, y, z)   (spine and neck turn about WORLD axes)
#   fL/fR (x, fwd, up, pitch, yaw)               kL/kR knee pole (toward his left, forward, up)
#   hL/hR (out, fwd, up, pron, curl, bend)       eL/eR elbow pole (outward, forward, up)
#   cL/cR (up, back) collarbone, or None to leave it to cw_clip's own default
NEUTRAL = dict(body=(0, 0, -1.2, 0, 0, 0), spine=(0, 0, 0), neck=(0, 0, 0),
               fL=(10.5, 0, 0, 0, 8), fR=(-10.5, 0, 0, 0, 8), kL=(0.22, 1.0, 0.0), kR=(-0.22, 1.0, 0.0),
               cL=None, cR=None,
               hL=(7, 3, HANG['L'], 62, 0.34, 0), eL=(0.35, -1.0, -0.1),
               hR=(7, 3, HANG['R'], 62, 0.34, 0), eR=(0.35, -1.0, -0.1))


def P(**kw):
    d = dict(NEUTRAL); d.update(kw); return d


GUARD_E = (0.4, -0.2, -1.0)
FLING_E = (1.0, -0.2, 0.4)

LIFT = P(body=(4, 1, -3, 0, -8, 28), spine=(2, 0, -6), neck=(2, 0, -20),          # 2: weight over the left, knee up
         fL=(10.5, 0, 0, 0, 30), kL=(0.5, 1.0, 0.0),
         fR=(-10, 2, 26, 30, 0), kR=(-0.1, 1.0, 0.5),
         hL=(6, 14, -16, 76, 0.9, 0), eL=GUARD_E,
         hR=(8, 4, -34, 62, 0.9, 0), eR=(0.5, -1.0, 0.0))
WHIP = P(body=(6.5, 2, -3, 0, -22, 58), spine=(0, 0, -14), neck=(4, 0, -38),      # 3: knee through, shin still folded
         fL=(10.5, 0, 0, 0, 55), kL=(1.0, 0.8, 0.0),
         fR=(-4, 26, 62, 20, 0), kR=(0.3, 1.0, 0.9),
         hL=(10, 20, -8, 80, 0.9, 0), eL=GUARD_E,
         hR=(14, -10, -36, 62, 0.9, 0), eR=FLING_E)
HIT = P(body=(7.5, 3, -4, 0, -38, 84), spine=(0, 0, -22), neck=(8, 0, -52),     # 4: the overshoot
        fL=(10.5, 0, 0, 0, 78), kL=(1.0, 0.45, 0.0),
        fR=(2, 80, 99, -12, 0), kR=(0.7, 0.2, 0.7),
        hL=(12, 22, -6, 80, 0.9, 0), eL=GUARD_E,
        hR=(22, -30, -30, 62, 0.9, 0), eR=FLING_E)
HOLD = P(body=(7.5, 2.5, -4, 0, -36, 80), spine=(0, 0, -21), neck=(8, 0, -50),  # 5: the panel
         fL=(10.5, 0, 0, 0, 78), kL=(1.0, 0.45, 0.0),
         fR=(2, 78, 96, -12, 0), kR=(0.7, 0.2, 0.7),
         hL=(12, 22, -6, 80, 0.9, 0), eL=GUARD_E,
         hR=(22, -29, -31, 62, 0.9, 0), eR=FLING_E)
FOLD = P(body=(6.5, 2, -3, 0, -22, 58), spine=(0, 0, -14), neck=(4, 0, -38),      # 6-7: the shin snaps back
         fL=(10.5, 0, 0, 0, 60), kL=(1.0, 0.7, 0.0),
         fR=(-4, 30, 66, 15, 0), kR=(0.3, 1.0, 0.9),
         hL=(10, 20, -9, 80, 0.9, 0), eL=GUARD_E,
         hR=(14, -12, -37, 62, 0.9, 0), eR=FLING_E)
DOWN = P(body=(3.5, 1, -3, 0, -7, 24), spine=(2, 0, -5), neck=(2, 0, -17),        # 9: the foot coming back under him
         fL=(10.5, 0, 0, 0, 28), kL=(0.5, 1.0, 0.0),
         fR=(-10, 4, 16, 22, 2), kR=(-0.1, 1.0, 0.4),
         hL=(7, 14, -22, 74, 0.8, 0), eL=(0.4, -0.5, -0.8),
         hR=(9, 2, -36, 62, 0.8, 0), eR=(0.5, -1.0, 0.0))
LAND = P(body=(0.5, 0.3, -4.5, 2, 1, 4), spine=(1, 0, -1), neck=(0, 0, -3),      # 11: down, knees soaking it up
         fL=(10.5, 0, 0, 0, 11), fR=(-10.5, 0, 0, 0, 8),
         hL=(7.5, 6, -40, 64, 0.55, 0), eL=(0.38, -0.95, -0.2),
         hR=(7.5, 5, -41, 63, 0.55, 0), eR=(0.38, -0.95, -0.2))

KEYS = [(1, NEUTRAL), (2, LIFT), (3, WHIP), (4, HIT), (5, HOLD), (7, FOLD), (9, DOWN), (11, LAND), (12, NEUTRAL)]


def _mix(a, b, t):
    if a is None or b is None:
        if a is None and b is None: return None
        a = a or (14.0, 3.0); b = b or (14.0, 3.0)
    return tuple(p + (q - p) * t for p, q in zip(a, b))


def pose_at(f):
    if f <= KEYS[0][0]: return KEYS[0][1]
    if f >= KEYS[-1][0]: return KEYS[-1][1]
    for (f0, a), (f1, b) in zip(KEYS, KEYS[1:]):
        if f0 <= f <= f1:
            t = (f - f0) / float(f1 - f0)
            return {k: _mix(a[k], b[k], t) for k in a}


def foot(s, x, fwd, up, pitch, yaw, pole):
    """cw_clip.foot() with the knee's direction given outright, as (toward his left, forward, up)."""
    th, sh, ft = C.LEG[s]
    t = Vector((x, C.ANK_Y - fwd, C.ANK[s].z - C.DROP[s] + up))
    C.ik2('leg' + s, th, sh, ft, t, Vector((pole[0], -pole[1], pole[2])), -C.Y)
    yw = math.radians(yaw) * C.SGN[s]; p = math.radians(pitch)
    f = Vector((math.sin(yw) * math.cos(p), -math.cos(yw) * math.cos(p), -math.sin(p)))
    u = Vector((math.sin(yw) * math.sin(p), -math.cos(yw) * math.sin(p), math.cos(p)))
    C.orient(ft, f, u - f * u.dot(f), C.FOOT_F0[s], C.Z)


def apply(p):
    b = p['body']; C.body(dx=b[0], fwd=b[1], dz=b[2], pitch=b[3], lean=b[4], twist=b[5])
    C.spine(*p['spine']); C.neck(*p['neck'])
    for s in 'LR':
        x, fw, up, pt, yw = p['f' + s]; foot(s, x, fw, up, pt, yw, p['k' + s])
    for s in 'LR':
        if p['c' + s] is not None: C.clav(s, *p['c' + s])
        o, fw, up, pr, cu, bd = p['h' + s]
        C.hand(s, out=o, fwd=fw, up=up, pron=pr, curl=cu, elbow=p['e' + s])
        if abs(bd) > 1e-6: C.wrist(s, bend=bd)


def build(f, u):
    apply(pose_at(f))


C.author('PunchB', frames=12, build=build, loop=False, sheet_frames=12)
