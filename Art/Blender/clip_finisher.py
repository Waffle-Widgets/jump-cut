# Finisher: hit three of the combo - a LEAPING RISING RIGHT UPPERCUT, 22 frames at 30 fps. THE APEX IS FRAME 8,
# held to 10 (unchanged).
# He drops into a deep coil to his right on frames 2-4 with the fist cocked behind his hip, drives up through 5-7
# and leaves the floor; at the apex the pelvis is ~22 cm up, the right fist is punched skyward past his head with the
# body arched and turned into it, the left knee is tucked high, the right leg trails long and the left arm is thrown
# down and back. He comes down toes first on 13 (the trailing right foot a beat after the left), soaks it up, rises
# a touch past the stand on 20 and is in it on 22.
#
# HOW IT MOVES (Nov 15 rework: "the attack animations look cheap"):
#   * the key poses are joined by a spline that runs THROUGH them (no stop at a key unless the value turns round
#     there), instead of a blend that changed speed abruptly at every key;
#   * each part has its own clock (OFFSET): the pelvis runs early, the chest on time, the punching arm on time (so
#     the apex stays on frame 8), the trailing leg a little late, the thrown left arm a frame late;
#   * the head is not keyed against the chest. GAZE is where he looks in the world and the neck is solved from
#     whatever the pelvis and chest are doing on that frame, so his eyes stay on the target through the coil;
#   * a foot rolling up onto its toes is lifted by what the roll needs, so the toes stay ON the floor instead of
#     dipping through it half way up (frame 5 was 0.8 cm under);
#   * through 9-10 the hips keep turning and the back keeps arching (follow-through) while the fist hangs.
# The pelvis is in place on frames 1 and 22.
#   blender -b --factory-startup --python Art/Blender/clip_finisher.py [-- norender noexport]
# Debug: POSE=8 poses every frame as frame 8 (to look at one pose).
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C
from mathutils import Vector, Matrix

FRAMES = 22
HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}


def T(name, default):
    return float(os.environ.get(name, default))


# A pose is a dict of tuples. Anything left out is taken from NEUTRAL.
#   body  (dx, fwd, dz, pitch, lean, twist)      spine (x, y, z)   (the spine turns about WORLD axes)
#   gaze  (down, tilt, left): where the HEAD points in the world, degrees; (0, 0, 0) is straight ahead
#   fL/fR (x, fwd, up, pitch, yaw, roll)         kL/kR knee pole (toward his left, forward, up)
#   hL/hR (out, fwd, up, pron, curl, bend)       eL/eR elbow pole (outward, forward, up)
NEUTRAL = dict(body=(0, 0, -1.2, 0, 0, 0), spine=(0, 0, 0), gaze=(0, 0, 0),
               fL=(10.5, 0, 0, 0, 8, 0), fR=(-10.5, 0, 0, 0, 8, 0), kL=(0.22, 1.0, 0.0), kR=(-0.22, 1.0, 0.0),
               hL=(7, 3, HANG['L'], 62, 0.34, 0), eL=(0.35, -1.0, -0.1),
               hR=(7, 3, HANG['R'], 62, 0.34, 0), eR=(0.35, -1.0, -0.1))


def P(**kw):
    d = dict(NEUTRAL); d.update(kw); return d


GUARD_E = (0.4, -0.2, -1.0)
COCK_E = (T('CK_OUT', 0.0), -1.0, T('CK_UP', 0.3))
UP_E = (T('UP_OUT', 0.35), T('UP_FWD', -0.3), -1.0)
FLING_E = (T('FL_OUT', -0.5), T('FL_FWD', -0.6), T('FL_UP', 1.0))  # the thrown left arm: elbow UP and a little IN,
#   which is where the joint's own hinge is with the arm behind him. Out to the side wrung the upper arm 139 degrees.
EYES = (T('LOOK_DOWN', -4.0), 0.0, 3.0)                    # on the target, a little above the horizon

COIL = P(body=(-2, -2, -21, 22, 0, -26), spine=(10, 0, -14), gaze=(6, 0, -4),         # 3: down and wound up
         hR=(8, -14, -40, 90, 0.9, 0), eR=COCK_E,
         hL=(-4, 22, -20, 80, 0.9, 0), eL=GUARD_E)
COIL2 = P(body=(-2.5, -2.5, -24, 24, 0, -30), spine=(11, 0, -16), gaze=(5, 0, -3),     # 4: the bottom
          hR=(8, -16, -41, 90, 0.9, 0), eR=COCK_E,
          hL=(-4, 22, -20, 80, 0.9, 0), eL=GUARD_E)
DRIVE = P(body=(0, 3, 1.5, 6, 0, 4), spine=(2, 0, 4), gaze=EYES,                      # 6: legs straight, on the toes
          fL=(10.5, 0, 10.5, 38, 8, 0), fR=(-10.5, 0, 10.5, 38, 8, 0),
          hR=(-2, 22, -24, 30, 0.9, 0), eR=(0.5, -0.8, -0.7),
          hL=(6, 4, -30, 70, 0.9, 0), eL=(0.6, -0.8, -0.4))
OFF = P(body=(0.5, 6, 13, -2, 0, 18), spine=(-5, 0, 14), gaze=EYES,                   # 7: off the floor
        fL=(10, 8, 32, 40, 4, 0), kL=(0.2, 1.0, 0.3), fR=(-11, -4, 21, 60, 4, 0),
        hR=(6, 18, 16, 16, 0.9, 0), eR=UP_E,
        hL=(10, -10, -38, 64, 0.9, 0), eL=FLING_E)
APEX = P(body=(1, 8, 23, -8, 0, 30), spine=(-10, 0, 22), gaze=EYES,                   # 8: THE HIT - fist at the top
         fL=(9, 18, 63, 30, 0, 0), kL=(0.2, 1.0, 0.4), fR=(-11, -10, 31, 62, 2, 0),
         hR=(3, 16, 44, 12, 1.0, 0), eR=UP_E,
         hL=(8, -24, -42, 62, 0.9, 0), eL=FLING_E)
FLOAT = P(body=(1, 8.6, 22, -10, 0, 34), spine=(-12, 0, 24), gaze=EYES,               # 10: the panel; hips and back
         fL=(9, 19, 61, 30, 0, 0), kL=(0.2, 1.0, 0.4), fR=(-11, -13, 29, 64, 2, 0),   #     still carrying round
         hR=(3, 15, 42.5, 12, 1.0, 0), eR=UP_E,
         hL=(8, -25, -40, 62, 0.9, 0), eL=FLING_E)
FALL = P(body=(0.6, 5, 7, 0, 0, 14), spine=(-2, 0, 10), gaze=(0, 0, 2),               # 12: coming down, feet reaching
         fL=(10, 6, 14, 30, 6, 0), kL=(0.2, 1.0, 0.1), fR=(-10.8, -3, 11, 38, 6, 0),
         hR=(6, 15, -6, 50, 0.9, 0), eR=(0.6, -0.6, -1.0),
         hL=(11, -4, -34, 64, 0.8, 0), eL=(0.8, -0.7, 0.0))
LAND = P(body=(0.2, 2, -13, 12, 0, 4), spine=(6, 0, 3), gaze=(4, 0, 0),               # 13: feet flat
         hR=(9, 8, -30, 60, 0.8, 0), eR=(0.6, -0.8, -0.3),
         hL=(10, 6, -34, 64, 0.7, 0), eL=(0.6, -0.8, -0.2))
SINK = P(body=(0, 1, -18, 15, 0, 1), spine=(7, 0, 1), gaze=(6, 0, 0),                 # 15: knees soak it up
         hR=(10, 10, -34, 62, 0.7, 0), eR=(0.6, -0.8, -0.3),
         hL=(10, 10, -34, 62, 0.7, 0), eL=(0.6, -0.8, -0.3))
RISE = P(body=(0, 0.3, -5, 3, 0, 0), spine=(1.5, 0, 0), gaze=(1, 0, 0),               # 18
         hR=(8, 5, -41, 63, 0.5, 0), eR=(0.4, -0.95, -0.2),
         hL=(8, 5, -41, 63, 0.5, 0), eL=(0.4, -0.95, -0.2))
OVER = P(body=(0, -0.3, -0.5, -0.7, 0, 0), spine=(-0.5, 0, 0),                        # 20: up a touch past the stand
         hR=(7.3, 2.2, HANG['R'] + 1.0, 62, 0.4, 0),
         hL=(7.3, 2.2, HANG['L'] + 1.0, 62, 0.4, 0))

KEYS = [(1, NEUTRAL), (3, COIL), (4, COIL2), (6, DRIVE), (7, OFF), (8, APEX), (10, FLOAT), (12, FALL), (13, LAND),
        (15, SINK), (18, RISE), (20, OVER), (FRAMES, NEUTRAL)]
KT = [k[0] for k in KEYS]

# Each part's own clock, in frames: + runs EARLY (leads), - runs LATE (drags). Leads fade in over frame 1-2 so frame
# 1 is the neutral stand; drags fade out over the last three frames so the last frame is the neutral stand too.
PART = dict(body='pelvis', spine='chest', gaze='head', fL='legL', kL='legL', fR='legR', kR='legR',
            hL='armL', eL='armL', hR='armR', eR='armR')
OFFSET = dict(pelvis=T('LEAD', 0.4), chest=0.0, head=0.3, legL=0.0, legR=-T('LAG_LEG', 0.25),
              armL=-T('LAG', 1.0), armR=0.0)
TOE, ANKLE_H = 20.0, 8.6                                   # ball of the foot ahead of the ankle; ankle above the sole


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
    """cw_clip.foot() with the knee's direction given outright, as (toward his left, forward, up), and a roll.
    A foot pitched onto its toes is lifted by at least what the roll onto the ball of the foot needs."""
    th, sh, ft = C.LEG[s]
    if pitch > 0:                                          # heel up: the toes stay ON the floor, not in it
        p = math.radians(min(pitch, 60.0)); up = max(up, TOE * math.sin(p) + ANKLE_H * (math.cos(p) - 1.0))
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
    keep = dict(C.TWIST); C.TWIST.clear()
    apply(pose_at(T('POSE', f)))
    if T('DBG', 0): print('TWISTF', f, {k: round(v) for k, v in C.TWIST.items()})
    for k, v in keep.items(): C.TWIST[k] = max(C.TWIST.get(k, 0.0), v)
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


C.author('Finisher', frames=FRAMES, build=build, loop=False, sheet_frames=FRAMES, stance=(0.12, 0.72))
