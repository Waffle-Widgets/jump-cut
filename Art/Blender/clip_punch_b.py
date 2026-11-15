# PunchB: hit two of the combo - a RIGHT FRONT THRUST KICK (push kick) to the stomach, 15 frames at 30 fps. (The clip
# keeps the name PunchB so the game's montage still finds it.) IMPACT IS FRAME 4, held on 5 (unchanged).
# It was a roundhouse: "his leg looks very odd when he kicks" (owner, Nov 15). That move turned the hips 84 degrees
# and rolled the foot 72, and this body has no twist bones to carry it. A front kick keeps the hips square: the
# weight goes onto the left foot, the right knee drives up in front (2-3), the leg thrusts straight out heel first
# with the knee on top and the toes pulled back (4), the torso leans back against it, the left fist stays at the
# chin and the right arm drives down beside the hip. Then the shin snaps back under a knee that is still high (6),
# the foot comes down beside the other (8) and he settles.
#
# HOW IT MOVES (the engine of the Nov 15 rework, kept):
#   * the key poses are joined by a spline that runs THROUGH them (no stop at a key unless the value turns round
#     there);
#   * each part has its own clock (OFFSET): the pelvis runs early, the chest on time, the kicking leg on time (so
#     the hit stays on frame 4), the guard arm late and the balancing arm later still;
#   * the head is not keyed against the chest. GAZE is where he looks in the world and the neck is solved from
#     whatever the pelvis and chest are doing on that frame, so his eyes stay on the target while he leans back;
#   * the kicking leg is never asked for its last few degrees (STRETCH), so the knee keeps a soft bend on top;
#   * on frame 5 the hips and the heel push a little further (follow-through) before the shin snaps back;
#   * he lands soft on 10, rises a touch past the stand on 13 and is in it on 15.
# The pelvis is in place on frames 1 and 15. The planted left foot never moves (it only turns out, about its ankle).
#   blender -b --factory-startup --python Art/Blender/clip_punch_b.py [-- norender noexport]
# Debug: POSE=4 poses every frame as frame 4 (to look at one pose). DBG=1 prints the kicking leg on frames 2-8.
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


GUARD_E = (0.45, -0.15, -1.0)                             # guard: elbow down, a little out
BACK_E = (0.5, -1.0, 0.25)                                # balancing arm: elbow back
LOOK = (T('LOOK_DOWN', 5.0), 0.0, 0.0)                    # chin tucked, eyes on the target straight ahead
KP = T('KICK_PITCH', -74.0)                               # toes pulled back: the sole faces the target
KX = T('KICK_X', -15.0)                                   # the heel a little outside the hip, so the back view sees it
KF = T('KICK_FWD', 92.0)
KU = T('KICK_UP', 88.0)
LB = T('LEAN_BACK', 8.0)                                  # pelvis tipped back at the hit; the spine adds SB more
SB = T('SPINE_BACK', 5.0)
TW = T('HIP_TWIST', 8.0)                                  # the right hip goes in with the kick
STRETCH = T('STRETCH', 0.9975)                            # the most of its length a leg is asked for (~8 degrees of knee)
KPX = T('KNEE_X', 0.15)                                  # which way the kicking knee leans off straight up (toward his left +)
YAW_L = T('PLANT_YAW', 24.0)                              # the planted foot turns out

LIFT = P(body=(4.5, 0.5, -2.5, -2, -2, 2), spine=(2, 0, -2), gaze=(2, 0, 0),      # 2: weight over the left, knee rising
         fL=(10.5, 0, 0, 0, 14, 0), kL=(0.3, 1.0, 0.0),
         fR=(-11, 10, 22, 24, 4, 0), kR=(-0.1, 1.0, 0.5),
         hL=(2, 14, -18, 76, 0.9, 0), eL=GUARD_E,
         hR=(5, 12, -24, 70, 0.9, 0), eR=GUARD_E)
CHAMBER = P(body=(6.5, 1.0, -3.0, -4, -3, 4), spine=(5, 0, -4), gaze=LOOK,        # 3: knee at the waist, shin hanging,
            fL=(10.5, 0, 0, 0, YAW_L * 0.8, 0), kL=(0.4, 1.0, 0.0),               #    pelvis tucked, both fists up
            fR=(-10, 30, 44, -12, 2, 0), kR=(KPX - 0.05, 0.5, 1.0),
            hL=(-3, 17, -6, 80, 0.95, 0), eL=GUARD_E,
            hR=(1, 15, -12, 76, 0.95, 0), eR=GUARD_E)
HIT = P(body=(7.0, 4.5, -3.5, -LB, -3, TW), spine=(-SB, 0, -TW * 0.6), gaze=LOOK, # 4: IMPACT - the leg thrust straight
        fL=(10.5, 0, 0, 0, YAW_L, 0), kL=(0.5, 1.0, 0.0),
        fR=(KX, KF, KU, KP, 3, 0), kR=(KPX, 0.0, 1.0),
        hL=(-4, 15, -3, 80, 0.95, 0), eL=GUARD_E,
        hR=(11, -15, -38, 62, 0.95, 0), eR=BACK_E)
HOLD = P(body=(7.2, 5.5, -3.5, -LB - 2, -3, TW + 2), spine=(-SB - 1, 0, -TW * 0.6 - 1), gaze=LOOK,   # 5: the panel
         fL=(10.5, 0, 0, 0, YAW_L, 0), kL=(0.5, 1.0, 0.0),                        #    hips and heel push on
         fR=(KX, KF + 3, KU + 1, KP - 4, 3, 0), kR=(KPX, 0.0, 1.0),
         hL=(-4, 15, -3.5, 80, 0.95, 0), eL=GUARD_E,
         hR=(12, -17, -37, 62, 0.95, 0), eR=BACK_E)
RECOIL = P(body=(6.5, 1.5, -3.0, -4, -3, 4), spine=(2, 0, -3), gaze=LOOK,         # 6: the shin snaps back, knee still high
           fL=(10.5, 0, 0, 0, YAW_L * 0.9, 0), kL=(0.4, 1.0, 0.0),
           fR=(-11, 32, 45, -8, 2, 0), kR=(KPX - 0.05, 0.5, 1.0),
           hL=(-3, 16, -6, 80, 0.95, 0), eL=GUARD_E,
           hR=(7, -4, -36, 64, 0.9, 0), eR=BACK_E)
DOWN = P(body=(2.0, 0.6, -3.0, 1, -1, 1), spine=(2.5, 0, -1), gaze=(2, 0, 0),     # 8: the foot down beside the other
         fL=(10.5, 0, 0, 0, 13, 0), kL=(0.3, 1.0, 0.0),
         fR=(-10.5, 1, 0, 0, 8, 0), kR=(-0.2, 1.0, 0.0),
         hL=(4, 11, -26, 72, 0.8, 0), eL=(0.4, -0.5, -0.8),
         hR=(7, 2, -42, 62, 0.75, 0), eR=(0.4, -1.0, 0.0))
LAND = P(body=(0.5, 0.3, -4.6, 2.5, 0, 0), spine=(1.5, 0, 0), gaze=(1, 0, 0),     # 10: knees soaking it up
         fL=(10.5, 0, 0, 0, 10, 0),
         hL=(7.5, 6, -39, 64, 0.55, 0), eL=(0.38, -0.95, -0.2),
         hR=(8.5, 4, -40, 63, 0.55, 0), eR=(0.38, -0.95, -0.2))
SETTLE = P(body=(-0.2, -0.3, -0.5, -0.6, 0, 0), spine=(-0.5, 0, 0),               # 13: up a touch past the stand
           hL=(7.2, 2.2, HANG['L'] + 1.0, 62, 0.42, 0),
           hR=(7.3, 2.0, HANG['R'] + 1.2, 62, 0.42, 0))

KEYS = [(1, NEUTRAL), (2, LIFT), (3, CHAMBER), (4, HIT), (5, HOLD), (6, RECOIL), (8, DOWN), (10, LAND), (13, SETTLE),
        (FRAMES, NEUTRAL)]
KT = [k[0] for k in KEYS]

# Each part's own clock, in frames: + runs EARLY (leads), - runs LATE (drags). Leads fade in over frame 1-2 so frame
# 1 is the neutral stand; drags fade out over the last three frames so the last frame is the neutral stand too.
PART = dict(body='pelvis', spine='chest', gaze='head', fL='legL', kL='legL', fR='legR', kR='legR',
            hL='armL', eL='armL', hR='armR', eR='armR')
OFFSET = dict(pelvis=T('LEAD', 0.3), chest=0.0, head=0.3, legL=0.0, legR=0.0,
              armL=-T('LAG_GUARD', 0.3), armR=-T('LAG', 0.35))


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
    h = C.head(th); d = t - h                                 # never the last few degrees: a leg at full stretch
    if d.length > C.LEGLEN[s] * STRETCH: t = h + d.normalized() * (C.LEGLEN[s] * STRETCH)     # snaps and loses its knee
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
    if os.environ.get('DBG') and 2 <= f <= 8:
        th, sh, ft = C.LEG['R']; a_, b_, c_ = C.head(th), C.head(sh), C.head(ft)
        ln = (c_ - a_).normalized(); off = (b_ - a_) - ln * (b_ - a_).dot(ln)
        r = lambda v: [round(q, 1) for q in v]
        up = C.head(_NECK[0]) - C.head('Bone_001')
        print('LEGR', f, 'knee_bend %.1f' % math.degrees((b_ - a_).angle(c_ - b_)), 'hip', r(a_), 'knee', r(b_), 'ankle', r(c_),
              'knee_off', r(off), 'torso_back %.1f' % math.degrees(math.atan2(up.y, up.z)),
              'spin', {k: round(v) for k, v in C.SPIN.items()}, 'wL', r(C.head(C.ARM['L'][2])), 'wR', r(C.head(C.ARM['R'][2])), 'head', r(C.head(_NECK[-1])))
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


C.author('PunchB', frames=FRAMES, build=build, loop=False, sheet_frames=FRAMES)
