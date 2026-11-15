# PunchB: hit two of the combo - a RIGHT ROUNDHOUSE KICK to chest height, 15 frames at 30 fps. (The clip keeps the
# name PunchB so the game's montage still finds it.) IMPACT IS FRAME 4, held on 5 (unchanged).
# He pivots on the planted left foot, the hips turn over to his left, the right knee whips up and through and the leg
# snaps out straight at chest height on frame 4. The body tips away from the kick, the left fist guards in front of
# the chest, the right arm is flung down and back behind him. Then the leg folds, comes down, and he settles.
#
# HOW IT MOVES (Nov 15 rework: "the attack animations look cheap"):
#   * the key poses are joined by a spline that runs THROUGH them (no stop at a key unless the value turns round
#     there), instead of a blend that changed speed abruptly at every key;
#   * each part has its own clock (OFFSET): the pelvis and the pivoting foot run early, the chest on time, the
#     kicking leg on time (so the hit stays on frame 4), the guard arm late and the flung arm later still;
#   * the head is not keyed against the chest. GAZE is where he looks in the world and the neck is solved from
#     whatever the pelvis and chest are doing on that frame, so his eyes stay on the target while the hips whip;
#   * the kicking foot ROLLS over with the hip (it used to stay sole-down on a leg lying on its side), so the instep
#     faces the way the foot is travelling;
#   * on frame 5 the hips and the leg carry on round a few degrees (follow-through) before the shin snaps back;
#   * he lands soft on 11, rises a touch past the stand on 13 and is in it on 15.
# The pelvis is in place on frames 1 and 15.
#   blender -b --factory-startup --python Art/Blender/clip_punch_b.py [-- norender noexport]
# Debug: POSE=4 poses every frame as frame 4 (to look at one pose).
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C
from mathutils import Vector, Matrix

FRAMES = 15
HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}


def T(name, default):
    return float(os.environ.get(name, default))


# A pose is a dict of tuples. Anything left out is taken from NEUTRAL.
#   body  (dx, fwd, dz, pitch, lean, twist)      spine (x, y, z)   (the spine turns about WORLD axes)
#   gaze  (down, tilt, left): where the HEAD points in the world, degrees; (0, 0, 0) is straight ahead
#   fL/fR (x, fwd, up, pitch, yaw, roll)         kL/kR knee pole (toward his left, forward, up)
#         roll: the top of the foot tipped toward his LEFT (a leg lying on its side carries its foot over with it)
#   hL/hR (out, fwd, up, pron, curl, bend)       eL/eR elbow pole (outward, forward, up)
NEUTRAL = dict(body=(0, 0, -1.2, 0, 0, 0), spine=(0, 0, 0), gaze=(0, 0, 0),
               fL=(10.5, 0, 0, 0, 8, 0), fR=(-10.5, 0, 0, 0, 8, 0), kL=(0.22, 1.0, 0.0), kR=(-0.22, 1.0, 0.0),
               hL=(7, 3, HANG['L'], 62, 0.34, 0), eL=(0.35, -1.0, -0.1),
               hR=(7, 3, HANG['R'], 62, 0.34, 0), eR=(0.35, -1.0, -0.1))


def P(**kw):
    d = dict(NEUTRAL); d.update(kw); return d


GUARD_E = (0.4, -0.2, -1.0)
FLING_E = (T('FL_OUT', 1.0), T('FL_FWD', -0.2), T('FL_UP', 0.4))
LOOK = (T('LOOK_DOWN', 0.0), T('LOOK_TILT', -6.0), T('LOOK_LEFT', 6.0))   # eyes on the target over the right shoulder
ROLL = T('ROLL', 72.0)                                    # how far the kicking foot is rolled over at the hit
KP = T('KICK_PITCH', -14.0)                               # toes in line with the shin (the leg rises ~15 degrees)
KY = T('KICK_YAW', 6.0)

LIFT = P(body=(4, 1, -3, 0, -8, 28), spine=(2, 0, -6), gaze=(0, -2, 4),           # 2: weight over the left, knee up
         fL=(10.5, 0, 0, 0, 30, 0), kL=(0.5, 1.0, 0.0),
         fR=(-10, 2, 26, 30, 0, ROLL * 0.25), kR=(-0.1, 1.0, 0.5),
         hL=(6, 14, -16, 76, 0.9, 0), eL=GUARD_E,
         hR=(8, 4, -34, 62, 0.9, 0), eR=(0.5, -1.0, 0.0))
WHIP = P(body=(6.5, 2, -3, 0, -22, 58), spine=(0, 0, -14), gaze=LOOK,             # 3: knee through, shin still folded
         fL=(10.5, 0, 0, 0, 55, 0), kL=(1.0, 0.8, 0.0),
         fR=(-4, 26, 62, 20, 0, ROLL * 0.7), kR=(0.3, 1.0, 0.9),
         hL=(10, 20, -8, 80, 0.9, 0), eL=GUARD_E,
         hR=(14, -10, -36, 62, 0.9, 0), eR=FLING_E)
HIT = P(body=(7.5, 3, -4, 0, -38, 84), spine=(0, 0, -22), gaze=LOOK,              # 4: IMPACT - the leg snapped straight
        fL=(10.5, 0, 0, 0, 78, 0), kL=(1.0, 0.45, 0.0),
        fR=(2, 80, 99, KP, KY, ROLL), kR=(0.7, 0.2, 0.7),
        hL=(12, 22, -6, 80, 0.9, 0), eL=GUARD_E,
        hR=(22, -30, -30, 62, 0.9, 0), eR=FLING_E)
HOLD = P(body=(7.8, 2.6, -4, 0, -37, 88), spine=(0, 0, -23), gaze=LOOK,           # 5: the panel; hips and leg carry
         fL=(10.5, 0, 0, 0, 82, 0), kL=(1.0, 0.4, 0.0),                           #    on round a few degrees
         fR=(8, 78, 97, KP, KY + 6, ROLL + 4), kR=(0.7, 0.15, 0.7),
         hL=(12, 22, -6, 80, 0.9, 0), eL=GUARD_E,
         hR=(22, -31, -31, 62, 0.9, 0), eR=FLING_E)
FOLD = P(body=(6.5, 2, -3, 0, -22, 60), spine=(0, 0, -14), gaze=LOOK,             # 7: the shin snaps back
         fL=(10.5, 0, 0, 0, 60, 0), kL=(1.0, 0.7, 0.0),
         fR=(-2, 30, 66, 15, 0, ROLL * 0.7), kR=(0.3, 1.0, 0.9),
         hL=(10, 20, -9, 80, 0.9, 0), eL=GUARD_E,
         hR=(14, -12, -37, 62, 0.9, 0), eR=FLING_E)
DOWN = P(body=(3.5, 1, -3, 0, -7, 24), spine=(2, 0, -5), gaze=(0, -1, 3),         # 9: the foot coming back under him
         fL=(10.5, 0, 0, 0, 28, 0), kL=(0.5, 1.0, 0.0),
         fR=(-10, 4, 16, 22, 2, ROLL * 0.2), kR=(-0.1, 1.0, 0.4),
         hL=(7, 14, -22, 74, 0.8, 0), eL=(0.4, -0.5, -0.8),
         hR=(9, 2, -36, 62, 0.8, 0), eR=(0.5, -1.0, 0.0))
LAND = P(body=(0.5, 0.3, -5.0, 2.5, 1, 3), spine=(1.5, 0, -1), gaze=(1, 0, 0),    # 11: down, knees soaking it up
         fL=(10.5, 0, 0, 0, 11, 0),
         hL=(7.5, 6, -39, 64, 0.55, 0), eL=(0.38, -0.95, -0.2),
         hR=(8.5, 4, -40, 63, 0.55, 0), eR=(0.38, -0.95, -0.2))
SETTLE = P(body=(-0.2, -0.3, -0.5, -0.6, -0.3, -1.2), spine=(-0.5, 0, 0.6),       # 13: up a touch past the stand
           hL=(7.2, 2.2, HANG['L'] + 1.0, 62, 0.42, 0),
           hR=(7.3, 2.0, HANG['R'] + 1.2, 62, 0.42, 0))

KEYS = [(1, NEUTRAL), (2, LIFT), (3, WHIP), (4, HIT), (5, HOLD), (7, FOLD), (9, DOWN), (11, LAND), (13, SETTLE),
        (FRAMES, NEUTRAL)]
KT = [k[0] for k in KEYS]

# Each part's own clock, in frames: + runs EARLY (leads), - runs LATE (drags). Leads fade in over frame 1-2 so frame
# 1 is the neutral stand; drags fade out over the last three frames so the last frame is the neutral stand too.
PART = dict(body='pelvis', spine='chest', gaze='head', fL='legL', kL='legL', fR='legR', kR='legR',
            hL='armL', eL='armL', hR='armR', eR='armR')
OFFSET = dict(pelvis=T('LEAD', 0.5), chest=0.0, head=0.3, legL=T('LEAD', 0.5), legR=0.0,
              armL=-T('LAG_GUARD', 0.6), armR=-T('LAG', 1.0))


def clock(part, f):
    o = OFFSET[part]
    if o > 0: return f + o * min(1.0, max(0.0, f - 1.0))
    if o < 0: return f + o * min(1.0, max(0.0, (FRAMES - f) / 3.0))
    return f


def _tan(v0, v1, v2, t0, t1, t2):
    """The slope a channel passes through a key with. Zero where the value turns round (or rests) at the key, so a
    planted foot stays planted and nothing overshoots a key by accident; otherwise the Catmull-Rom slope, so the
    motion carries THROUGH the key instead of stopping on it."""
    d0 = (v1 - v0) / (t1 - t0); d1 = (v2 - v1) / (t2 - t1)
    if d0 * d1 <= 0: return 0.0
    m = (v2 - v0) / (t2 - t0)
    lim = 3.0 * min(abs(d0), abs(d1))
    return max(-lim, min(lim, m))


def chan(name, t):
    """Channel `name` (a tuple) at time t, by cubic Hermite through the keys."""
    n = len(KEYS)
    if t <= KT[0]: return KEYS[0][1][name]
    if t >= KT[-1]: return KEYS[-1][1][name]
    i = max(k for k in range(n - 1) if KT[k] <= t)
    h = KT[i + 1] - KT[i]; s = (t - KT[i]) / h; s2, s3 = s * s, s * s * s
    a, b = KEYS[i][1][name], KEYS[i + 1][1][name]
    out = []
    for c in range(len(a)):
        m1 = _tan(KEYS[i - 1][1][name][c], a[c], b[c], KT[i - 1], KT[i], KT[i + 1]) if i > 0 else 0.0
        m2 = _tan(a[c], b[c], KEYS[i + 2][1][name][c], KT[i], KT[i + 1], KT[i + 2]) if i + 2 < n else 0.0
        out.append((2 * s3 - 3 * s2 + 1) * a[c] + (s3 - 2 * s2 + s) * m1 * h + (-2 * s3 + 3 * s2) * b[c] + (s3 - s2) * m2 * h)
    return tuple(out)


def pose_at(f):
    return {k: chan(k, clock(PART[k], f)) for k in NEUTRAL}


def foot(s, x, fwd, up, pitch, yaw, roll, pole):
    """cw_clip.foot() with the knee's direction given outright, as (toward his left, forward, up), and a roll."""
    th, sh, ft = C.LEG[s]
    t = Vector((x, C.ANK_Y - fwd, C.ANK[s].z - C.DROP[s] + max(up, 0.0)))
    C.ik2('leg' + s, th, sh, ft, t, Vector((pole[0], -pole[1], pole[2])), -C.Y)
    yw = math.radians(yaw) * C.SGN[s]; p = math.radians(pitch); r = math.radians(roll)
    f = Vector((math.sin(yw) * math.cos(p), -math.cos(yw) * math.cos(p), -math.sin(p)))
    u = Vector((math.sin(yw) * math.sin(p), -math.cos(yw) * math.sin(p), math.cos(p)))
    u = u - f * u.dot(f)
    if abs(r) > 1e-6: u = u * math.cos(r) - f.cross(u) * math.sin(r)
    C.orient(ft, f, u, C.FOOT_F0[s], C.Z)


_NECK = [b for b, k in C.NECK]
_CHEST = [C.PARENT[b] for b in _NECK if C.PARENT[b] not in _NECK][0]


def look(down, tilt, left):
    """Point the head at a WORLD direction, whatever the pelvis and chest have done this frame."""
    G = Matrix.Rotation(math.radians(left), 3, 'Z') @ Matrix.Rotation(math.radians(-tilt), 3, 'Y') @ Matrix.Rotation(math.radians(down), 3, 'X')
    D = C.W[_CHEST].to_3x3().normalized() @ C.REST[_CHEST].to_3x3().normalized().inverted()
    e = (G @ D.inverted()).to_euler('XYZ')
    C.neck(math.degrees(e.x), -math.degrees(e.y), math.degrees(e.z))


def apply(p):
    b = p['body']; C.body(dx=b[0], fwd=b[1], dz=b[2], pitch=b[3], lean=b[4], twist=b[5])
    C.spine(*p['spine']); look(*p['gaze'])
    for s in 'LR':
        x, fw, up, pt, yw, rl = p['f' + s]; foot(s, x, fw, up, pt, yw, rl, p['k' + s])
    for s in 'LR':
        o, fw, up, pr, cu, bd = p['h' + s]
        C.hand(s, out=o, fwd=fw, up=up, pron=pr, curl=cu, elbow=p['e' + s])
        if abs(bd) > 1e-6: C.wrist(s, bend=bd)


def build(f, u):
    apply(pose_at(T('POSE', f)))
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


C.author('PunchB', frames=FRAMES, build=build, loop=False, sheet_frames=FRAMES)
