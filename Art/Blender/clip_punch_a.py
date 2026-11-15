# PunchA: hit one of the combo - an explosive LUNGING LEFT STRAIGHT, 15 frames at 30 fps. IMPACT IS FRAME 3, held
# through 4-5 (unchanged: the owner said the speed of the attacks felt fine).
# The front (left) foot stamps out into a deep bent knee, the rear leg drives straight behind on the ball of the foot,
# hips and chest turn into the line of the punch, the left fist is thrown the full length of the arm at shoulder
# height and the right fist is ripped back to the ribs.
#
# HOW IT MOVES (Nov 15 rework: "the attack animations look cheap"):
#   * the key poses are joined by a spline that runs THROUGH them (no stop at a key unless the value turns round
#     there), instead of an eased blend that came to rest at every key;
#   * the body is not posed from one clock. OFFSET gives each part its own: the pelvis runs early, the chest on
#     time, the rear foot a little early, the idle (right) arm late, so no two parts start or stop on one frame;
#   * the head is not keyed against the chest. GAZE is where he looks in the world, and the neck is solved from
#     whatever the pelvis and chest are doing on that frame, so the eyes stay on the target while the body whips;
#   * after the hit the hips and chest carry on a few degrees (frames 4-5) while the fist is already coming off;
#   * the fist comes home low, elbow first, on an arc; it only travels straight on the strike;
#   * the recovery passes a little through the neutral stand (frame 11) and settles into it by 15.
# The pelvis is in place on frames 1 and 15; in between it lunges ~26 cm.
#   blender -b --factory-startup --python Art/Blender/clip_punch_a.py [-- norender noexport]
# Debug: POSE=3 poses every frame as frame 3 (to look at one pose on the hands sheet).
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C
from mathutils import Vector

FRAMES = 15
HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}
AL = C.ARMLEN['L']

# A pose is a dict of tuples. Anything left out is taken from NEUTRAL.
#   body  (dx, fwd, dz, pitch, lean, twist)      spine (x, y, z)
#   gaze  (down, tilt, left): where the HEAD points in the world, degrees; (0, 0, 0) is straight ahead
#   fL/fR (x, fwd, up, pitch, yaw)               kL/kR knee pole (toward his left, forward, up)
#   hL/hR (out, fwd, up, pron, curl, bend)       eL/eR elbow pole (outward, forward, up)
NEUTRAL = dict(body=(0, 0, -1.2, 0, 0, 0), spine=(0, 0, 0), gaze=(0, 0, 0),
               fL=(10.5, 0, 0, 0, 8), fR=(-10.5, 0, 0, 0, 8), kL=(0.22, 1.0, 0.0), kR=(-0.22, 1.0, 0.0),
               hL=(7, 3, HANG['L'], 62, 0.34, 0), eL=(0.35, -1.0, -0.1),
               hR=(7, 3, HANG['R'], 62, 0.34, 0), eR=(0.35, -1.0, -0.1))


def P(**kw):
    d = dict(NEUTRAL); d.update(kw); return d


def T(name, default):
    return float(os.environ.get(name, default))


CHAMBER_E = (T('CH_OUT', 0.0), -1.0, T('CH_UP', 0.3))      # elbow driven straight back behind him


LOOK = (T('LOOK_DOWN', -3.0), 0.0, 0.0)                      # eyes on the target: level, chin up a touch
WB = T('WB', 8.0)                                            # punching wrist: held in line with the forearm, knuckles first

GO = P(body=(1, 11, -9, 9, 0, -16), spine=(3, 0, -12), gaze=LOOK,              # 2: already leaving, foot in the air
       fL=(12, 22, 8, -18, 5), fR=(-11.5, -6, 4.5, 14, 14),
       hL=(-1, AL * 0.55, -13, 100, 0.9, WB * 0.5), eL=(0.9, -0.3, -0.7),
       hR=(5, -6, -30, 40, 0.9, 0), eR=CHAMBER_E)
HIT = P(body=(2, 26, -20, 17, 0, -38), spine=(3, 0, -18), gaze=LOOK,           # 3: IMPACT - the fist at full reach
        fL=(13, 38, 0, 0, 3), fR=(-13, -24, 10, 34, 22),
        hL=(-7, AL * 0.99, -1, 118, 1.0, WB), eL=(1.0, 0.0, -0.55),
        hR=(6, -12, -27, 20, 0.9, 0), eR=CHAMBER_E)
HOLD = P(body=(2.2, 27.2, -20.8, 18, 0, -41), spine=(3.5, 0, -20), gaze=LOOK,  # 4: the panel; body still carrying in
         fL=(13, 38, 0, 0, 3), fR=(-13, -24, 10, 34, 22),
         hL=(-7, AL * 0.975, -1.5, 118, 1.0, WB), eL=(1.0, 0.0, -0.55),
         hR=(6, -13, -26.5, 20, 0.9, 0), eR=CHAMBER_E)
HOLD2 = P(body=(2.2, 26.4, -20.2, 17.5, 0, -40), spine=(3.5, 0, -19), gaze=LOOK,   # 5: the last of the follow-through
          fL=(13, 38, 0, 0, 3), fR=(-13, -24, 10, 34, 22),
          hL=(-6, AL * 0.92, -3.5, 116, 1.0, WB * 0.8), eL=(1.0, -0.1, -0.65),
          hR=(6, -12, -26.5, 22, 0.9, 0), eR=CHAMBER_E)
BACK = P(body=(1.5, 16, -12.5, 10, 0, -17), spine=(3, 0, -11), gaze=LOOK,      # 7: pushing off the front foot;
         fL=(12.5, 30, 3.5, -8, 5), fR=(-12, -15, 4, 12, 15),                  #    the elbow drops and leads the fist
         hL=(3, 25, -19, 88, 0.9, 0), eL=(0.75, -0.65, -1.0),
         hR=(4.5, 0, -24, 50, 0.9, 0), eR=(0.45, -0.8, -0.4))
REC = P(body=(0.5, 4.5, -5.5, 3, 0, -3), spine=(1, 0, -3), gaze=(-1, 0, 0),    # 9
        fL=(11.5, 11, 2.2, -4, 7), fR=(-11, -4, 1.0, 3, 10),
        hL=(7, 9, -35, 70, 0.75, 0), eL=(0.5, -0.9, -0.5),
        hR=(6.5, 7, -35, 64, 0.75, 0), eR=(0.4, -0.9, -0.4))
OVER = P(body=(-0.2, -1.6, -2.6, -1.2, 0, 2.5), spine=(-0.8, 0, 1.5),          # 11: carried a little past the stand
         fL=(10.5, 0, 0, 0, 8), fR=(-10.5, 0, 0, 0, 8),
         hL=(8, 1.5, HANG['L'] + 2.0, 63, 0.5, 0), eL=(0.38, -0.95, -0.2),
         hR=(7.6, 5.0, HANG['R'] + 1.5, 63, 0.5, 0), eR=(0.38, -0.95, -0.2))
SETTLE = P(body=(0, 0.35, -1.0, 0.3, 0, -0.5), spine=(0.2, 0, -0.3),           # 13: and back the other way, barely
           hL=(7.2, 3.6, HANG['L'] + 0.4, 62, 0.4, 0),
           hR=(7.2, 2.4, HANG['R'] + 0.5, 62, 0.4, 0))

KEYS = [(1, NEUTRAL), (2, GO), (3, HIT), (4, HOLD), (5, HOLD2), (7, BACK), (9, REC), (11, OVER), (13, SETTLE),
        (FRAMES, NEUTRAL)]
KT = [k[0] for k in KEYS]

# Each part's own clock, in frames: + runs EARLY (leads), - runs LATE (drags). Leads fade in over frame 1-2 so frame
# 1 is the neutral stand; drags fade out over the last three frames so the last frame is the neutral stand too.
PART = dict(body='pelvis', spine='chest', gaze='head', fL='legL', kL='legL', fR='legR', kR='legR',
            hL='armL', eL='armL', hR='armR', eR='armR')
OFFSET = dict(pelvis=T('LEAD', 0.5), chest=0.0, head=0.3, legL=0.0, legR=0.4, armL=0.0, armR=-T('LAG', 1.0))


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


def foot(s, x, fwd, up, pitch, yaw, pole):
    """cw_clip.foot() with the knee's direction given outright, as (toward his left, forward, up)."""
    x += C.SGN[s] * C.STANCE['foot_x'] * C._stance[0]      # the idle's wider feet at the ends of the clip (cw_clip.STANCE)
    th, sh, ft = C.LEG[s]
    t = Vector((x, C.ANK_Y - fwd, C.ANK[s].z - C.DROP[s] + max(up, 0.0)))
    C.ik2('leg' + s, th, sh, ft, t, Vector((pole[0], -pole[1], pole[2])), -C.Y)
    yw = math.radians(yaw) * C.SGN[s]; p = math.radians(pitch)
    f = Vector((math.sin(yw) * math.cos(p), -math.cos(yw) * math.cos(p), -math.sin(p)))
    u = Vector((math.sin(yw) * math.sin(p), -math.cos(yw) * math.sin(p), math.cos(p)))
    C.orient(ft, f, u - f * u.dot(f), C.FOOT_F0[s], C.Z)


def apply(p):
    b = p['body']; C.body(dx=b[0], fwd=b[1], dz=b[2], pitch=b[3], lean=b[4], twist=b[5])
    sp = p['spine']; C.spine(*sp)
    g = p['gaze']                                            # the neck undoes whatever the hips and chest did
    C.neck(g[0] - b[3] * math.cos(math.radians(b[5])) - sp[0], g[1] - sp[1], g[2] - b[5] - sp[2])
    for s in 'LR':
        x, fw, up, pt, yw = p['f' + s]; foot(s, x, fw, up, pt, yw, p['k' + s])
    for s in 'LR':
        o, fw, up, pr, cu, bd = p['h' + s]
        C.hand(s, out=o, fwd=fw, up=up, pron=pr, curl=cu, elbow=p['e' + s])
        if abs(bd) > 1e-6: C.wrist(s, bend=bd)


def build(f, u):
    apply(pose_at(T('POSE', f)))
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


C.author('PunchA', frames=FRAMES, build=build, loop=False, sheet_frames=FRAMES, stance=(0.14, 0.55))
