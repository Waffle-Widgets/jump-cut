# Finisher: hit three of the combo - a LEAPING RISING RIGHT UPPERCUT, 20 frames at 30 fps.
# He drops into a deep coil to his right on frames 2-4 with the fist cocked behind his hip, drives up through 5-7
# and leaves the floor; at the apex (frame 8, held to 10) the pelvis is ~22 cm up, the right fist is punched skyward
# past his head with the body arched and turned into it, the left knee is tucked high, the right leg trails long and
# the left arm is thrown down and back. He lands on 13, soaks it up, and is back in the neutral stand on frame 20.
# The pelvis is in place on frames 1 and 20.
#   blender -b --factory-startup --python Art/Blender/clip_finisher.py [-- norender noexport]
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
COCK_E = (0.6, -1.0, 0.3)
UP_E = (0.35, -0.3, -1.0)
FLING_E = (1.0, -0.3, 0.4)

COIL = P(body=(-2, -2, -21, 22, 0, -26), spine=(10, 0, -14), neck=(-24, 0, 34),       # 3: down and wound up
         hR=(8, -14, -40, 90, 0.9, 0), eR=COCK_E,
         hL=(-4, 22, -20, 80, 0.9, 0), eL=GUARD_E)
COIL2 = P(body=(-2.5, -2.5, -24, 24, 0, -30), spine=(11, 0, -16), neck=(-26, 0, 38),   # 4: the bottom
          hR=(8, -16, -41, 90, 0.9, 0), eR=COCK_E,
          hL=(-4, 22, -20, 80, 0.9, 0), eL=GUARD_E)
DRIVE = P(body=(0, 3, 1.5, 6, 0, 4), spine=(2, 0, 4), neck=(-6, 0, -6),               # 6: legs straight, on the toes
          fL=(10.5, 0, 10.5, 38, 8), fR=(-10.5, 0, 10.5, 38, 8),
          hR=(-2, 22, -24, 30, 0.9, 0), eR=(0.5, -0.8, -0.7),
          hL=(6, 4, -30, 70, 0.9, 0), eL=(0.6, -0.8, -0.4))
OFF = P(body=(0.5, 6, 13, -2, 0, 18), spine=(-5, 0, 14), neck=(5, 0, -26),            # 7: off the floor
        fL=(10, 8, 32, 40, 4), kL=(0.2, 1.0, 0.3), fR=(-11, -4, 18, 60, 4),
        hR=(6, 18, 16, 16, 0.9, 0), eR=UP_E,
        hL=(10, -10, -38, 64, 0.9, 0), eL=FLING_E)
APEX = P(body=(1, 8, 23, -8, 0, 30), spine=(-10, 0, 22), neck=(14, 0, -44),           # 8: the overshoot
         fL=(9, 18, 63, 30, 0), kL=(0.2, 1.0, 0.4), fR=(-11, -10, 31, 62, 2),
         hR=(3, 16, 44, 12, 0.9, 0), eR=UP_E,
         hL=(8, -24, -42, 62, 0.9, 0), eL=FLING_E)
FLOAT = P(body=(1, 8.5, 21.5, -9, 0, 31), spine=(-10, 0, 22), neck=(15, 0, -45),       # 10: the panel
         fL=(9, 19, 62, 30, 0), kL=(0.2, 1.0, 0.4), fR=(-11, -11, 29.5, 62, 2),
         hR=(3, 16, 43, 12, 0.9, 0), eR=UP_E,
         hL=(8, -25, -42, 62, 0.9, 0), eL=FLING_E)
FALL = P(body=(0.6, 5, 7, 0, 0, 14), spine=(-2, 0, 10), neck=(2, 0, -20),             # 12: coming down, feet reaching
         fL=(10, 6, 14, 30, 6), kL=(0.2, 1.0, 0.1), fR=(-10.8, -3, 11, 38, 6),
         hR=(4, 14, -4, 50, 0.9, 0), eR=(0.5, -0.5, -1.0),
         hL=(11, -4, -34, 64, 0.8, 0), eL=(0.8, -0.7, 0.0))
LAND = P(body=(0.2, 2, -13, 12, 0, 4), spine=(6, 0, 3), neck=(-14, 0, -6),            # 13: feet flat
         fL=(10.5, 0, 0, 0, 8), fR=(-10.5, 0, 0, 0, 8),
         hR=(9, 8, -30, 60, 0.8, 0), eR=(0.6, -0.8, -0.3),
         hL=(10, 6, -34, 64, 0.7, 0), eL=(0.6, -0.8, -0.2))
SINK = P(body=(0, 1, -18, 15, 0, 1), spine=(7, 0, 1), neck=(-17, 0, -2),              # 15: knees soak it up
         hR=(10, 10, -34, 62, 0.7, 0), eR=(0.6, -0.8, -0.3),
         hL=(10, 10, -34, 62, 0.7, 0), eL=(0.6, -0.8, -0.3))
RISE = P(body=(0, 0.3, -6, 4, 0, 0), spine=(2, 0, 0), neck=(-5, 0, 0),                # 18
         hR=(8, 6, -41, 63, 0.5, 0), eR=(0.4, -0.95, -0.2),
         hL=(8, 6, -41, 63, 0.5, 0), eL=(0.4, -0.95, -0.2))

KEYS = [(1, NEUTRAL), (3, COIL), (4, COIL2), (6, DRIVE), (7, OFF), (8, APEX), (10, FLOAT), (12, FALL), (13, LAND),
        (15, SINK), (18, RISE), (20, NEUTRAL)]


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


C.author('Finisher', frames=20, build=build, loop=False, sheet_frames=12)
