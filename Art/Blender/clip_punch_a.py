# PunchA: hit one of the combo - an explosive LUNGING LEFT STRAIGHT, 12 frames at 30 fps.
# The front (left) foot stamps out into a deep bent knee, the rear leg drives straight behind on the ball of the foot,
# hips and chest turn into the line of the punch, the left fist is thrown the full length of the arm at shoulder
# height and the right fist is ripped back to the ribs. Overshoot on frame 3, held on 4 (and nearly on 5), back by 12.
# The pelvis is in place on frames 1 and 12; in between it lunges ~25 cm.
#   blender -b --factory-startup --python Art/Blender/clip_punch_a.py [-- norender noexport]
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C
from mathutils import Vector

HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}
AL = C.ARMLEN['L']

# A pose is a dict of tuples. Anything left out is taken from NEUTRAL.
#   body  (dx, fwd, dz, pitch, lean, twist)      spine / neck (x, y, z)
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


CHAMBER_E = (0.35, -1.0, 0.25)                               # elbow driven straight back behind him

GO = P(body=(1, 11, -9, 9, 0, -16), spine=(3, 0, -12), neck=(-8, 0, 26),      # 2: already leaving, foot in the air
       fL=(12, 22, 8, -18, 5), fR=(-11.5, -6, 4.5, 14, 14),
       hL=(-1, AL * 0.55, -13, 100, 0.9, 0), eL=(0.9, -0.3, -0.7),
       hR=(5, -6, -30, 40, 0.9, 0), eR=CHAMBER_E)
HIT = P(body=(2, 26, -20, 17, 0, -38), spine=(3, 0, -18), neck=(-34, 0, 52),  # 3: the overshoot
        fL=(13, 38, 0, 0, 3), fR=(-13, -24, 10, 34, 22),
        hL=(-7, AL * 0.99, -1, 118, 0.9, 0), eL=(1.0, 0.0, -0.55),
        hR=(6, -12, -27, 20, 0.9, 0), eR=CHAMBER_E)
HOLD = P(body=(2, 24.5, -19, 16, 0, -36), spine=(3, 0, -17), neck=(-33, 0, 50),  # 4: the panel
         fL=(13, 38, 0, 0, 3), fR=(-13, -24, 10, 34, 22),
         hL=(-7, AL * 0.975, -1.5, 118, 0.9, 0), eL=(1.0, 0.0, -0.55),
         hR=(6, -11, -27, 20, 0.9, 0), eR=CHAMBER_E)
HOLD2 = P(body=(2, 23.5, -18.5, 15, 0, -34), spine=(3, 0, -16), neck=(-31, 0, 47),
          fL=(13, 38, 0, 0, 3), fR=(-13, -24, 10, 34, 22),
          hL=(-6, AL * 0.93, -3, 116, 0.9, 0), eL=(1.0, -0.1, -0.6),
          hR=(6, -10, -27, 22, 0.9, 0), eR=CHAMBER_E)
BACK = P(body=(1.5, 15, -12, 10, 0, -15), spine=(3, 0, -11), neck=(-10, 0, 24),  # 7: pushing off the front foot
         fL=(12.5, 30, 3.5, -8, 5), fR=(-12, -15, 4, 12, 15),
         hL=(1, 24, -12, 86, 0.9, 0), eL=(0.6, -0.5, -1.0),
         hR=(4, 4, -22, 60, 0.9, 0), eR=(0.45, -0.7, -0.6))
REC = P(body=(0.6, 5, -5, 4, 0, -5), spine=(1, 0, -4), neck=(-4, 0, 8),          # 9
        fL=(11.5, 12, 2, -4, 7), fR=(-11, -5, 1.2, 3, 10),
        hL=(5, 13, -32, 70, 0.75, 0), eL=(0.45, -0.8, -0.5),
        hR=(6, 8, -34, 64, 0.75, 0), eR=(0.4, -0.9, -0.4))
SETTLE = P(body=(0.2, 1, -2.2, 1, 0, -1), spine=(0.5, 0, -1), neck=(-1, 0, 2),   # 11
           fL=(10.5, 2, 0, 0, 8), fR=(-10.5, -0.8, 0, 0, 8),
           hL=(7.5, 5, -42, 63, 0.5, 0), eL=(0.38, -0.95, -0.2),
           hR=(7.5, 5, -42, 63, 0.5, 0), eR=(0.38, -0.95, -0.2))

KEYS = [(1, NEUTRAL), (2, GO), (3, HIT), (4, HOLD), (5, HOLD2), (7, BACK), (9, REC), (11, SETTLE), (12, NEUTRAL)]


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


C.author('PunchA', frames=12, build=build, loop=False, sheet_frames=12)
