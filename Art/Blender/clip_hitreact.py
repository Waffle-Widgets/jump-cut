# HitReact: struck from the front in the chest, 14 frames at 30 fps, in place. A WHIP, not a nod:
#   2   the chest is already going back and the head has not caught up (chin tucked), arms left behind in front
#   3   chest and head thrown hard back, right foot coming off the floor
#   4   the arms arrive - flung up and forward, loose, a frame after the chest that threw them (the right arm later
#       still) - while the chest is already on its way back
#   5   the right foot lands one step behind him (still until 8), the head whips forward past level
#   6-8 he folds a little forward over the step, arms swinging down and back past his sides
#   9-12 the foot comes home; 12-14 a loose settle into the neutral stand, which he reaches exactly on 14
# Hands stay half open: he is not throwing anything.
#
# HOW IT MOVES (Nov 15 rework): the key poses are joined by a spline that runs THROUGH them (it only stops where a
# value turns round), and each part has its own clock (OFFSET) so the chest goes first, the pelvis is dragged after
# it, the head whips behind the chest and the arms trail behind everything.
#   blender -b --factory-startup --python Art/Blender/clip_hitreact.py [-- norender noexport]
# Debug: POSE=3 poses every frame as frame 3 (to look at one pose).
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

FRAMES = 14
HANG = {s: -C.ARMLEN[s] * 0.965 for s in 'LR'}


def T(name, default):
    return float(os.environ.get(name, default))


# A pose is a dict of tuples. Anything left out is taken from NEUTRAL.
#   body  (dx, fwd, dz, pitch, lean, twist)      spine / neck (x, y, z)
#   fL/fR (x, fwd, up, pitch, yaw)
#   cL/cR (up, back, weight): collarbone. weight 0 leaves it to cw_clip's own default, 1 uses (up, back) outright.
#   hL/hR (out, fwd, up, pron, curl, bend)       eL/eR elbow pole (outward, forward, up)
AUTO_CLAV = (28.0, 3.0)                                    # about what cw_clip gives a hanging arm
NEUTRAL = dict(body=(0, 0, -1.2, 0, 0, 0), spine=(0, 0, 0), neck=(0, 0, 0),
               fL=(10.5, 0, 0, 0, 8), fR=(-10.5, 0, 0, 0, 8), cL=AUTO_CLAV + (0,), cR=AUTO_CLAV + (0,),
               hL=(7, 3, HANG['L'], 62, 0.34, 0), eL=(0.35, -1.0, -0.1),
               hR=(7, 3, HANG['R'], 62, 0.34, 0), eR=(0.35, -1.0, -0.1))


def P(**kw):
    d = dict(NEUTRAL); d.update(kw); return d


SX = T('SNAP_SPINE', -27.0)                                # how far the chest is thrown back
NX = T('SNAP_NECK', -30.0)                                 # and the head on top of it
BACK_FOOT = (-12.0, -20, 0, 0, 12)

JOLT = P(body=(0.3, -3.5, -2.0, -7, 0, 4), spine=(SX * 0.6, 0, 5), neck=(12, 1, 2),    # 2: chest gone, head not yet
         fR=(-11.0, -2, 1.5, 6, 8),
         cL=(33, 0, 1), cR=(34, 0, 1),
         hL=(8, 12, HANG['L'] + 4, 56, 0.25, 0), eL=(0.5, -0.9, -0.2),
         hR=(9, 10, HANG['R'] + 3, 58, 0.3, 0), eR=(0.5, -0.9, -0.1))
SNAP = P(body=(0.5, -6.5, -3.0, -13, 0, 7), spine=(SX, 0, 9), neck=(NX, 3, 5),         # 3: thrown back
         fR=(-11.5, -9, 5.0, 12, 8),
         cL=(37, -5, 1), cR=(38, -6, 1),
         hL=(9, 26, -22, 36, 0.15, -12), eL=(0.7, -0.6, -0.5),
         hR=(13, 19, -29, 44, 0.2, -10), eR=(0.7, -0.8, -0.3))
STAG = P(body=(-0.5, -9.5, -5.0, -3, 0, 4), spine=(-5, 0, 4), neck=(13, 1, 0),         # 5: foot down, head whips
         fR=BACK_FOOT,                                                                 #    forward
         cL=(31, 2, 1), cR=(31, 2, 1),
         hL=(10, 13, -35, 50, 0.25, 0), eL=(0.55, -0.8, -0.3),
         hR=(11, 8, -39, 56, 0.3, 0), eR=(0.5, -0.9, -0.2))
SINK = P(body=(-0.8, -8.5, -6.5, 6, 0, 2), spine=(8, 0, 2), neck=(6, 0, 0),            # 8: folded over the step
         fR=BACK_FOOT,
         cL=(28, 3, 1), cR=(28, 3, 1),
         hL=(8, -5, -44, 62, 0.4, 6), eL=(0.4, -1.0, -0.1),
         hR=(9, -7, -44, 62, 0.4, 6), eR=(0.4, -1.0, -0.1))
HOME = P(body=(-0.3, -4.0, -3.2, 3, 0, 1), spine=(3, 0, 1), neck=(-2, 0, 0),           # 10: the foot coming home
         fR=(-11.0, -10, 3.5, 9, 9),
         hL=(8, 2, HANG['L'] + 2.5, 62, 0.36, 0), hR=(8, 1, HANG['R'] + 2.5, 62, 0.36, 0))
LOOSE = P(body=(0.1, 0.5, -1.9, -0.6, 0, -0.4), spine=(-0.8, 0, -0.3), neck=(-1.5, 0, 0),   # 12: down, a touch past
          hL=(7.4, 4.5, HANG['L'] + 0.8, 62, 0.35, 0), hR=(7.4, 4.2, HANG['R'] + 0.8, 62, 0.35, 0))

KEYS = [(1, NEUTRAL), (2, JOLT), (3, SNAP), (5, STAG), (8, SINK), (10, HOME), (12, LOOSE), (FRAMES, NEUTRAL)]
KT = [k[0] for k in KEYS]

# Each part's own clock, in frames: + runs EARLY (leads), - runs LATE (drags). Leads fade in over frame 1-2 so frame
# 1 is the neutral stand; drags fade out over the last three frames so the last frame is the neutral stand too.
PART = dict(body='pelvis', spine='chest', neck='head', fL='legL', fR='legR',
            cL='chest', cR='chest', hL='armL', eL='armL', hR='armR', eR='armR')
OFFSET = dict(pelvis=-T('LAG_PELVIS', 0.3), chest=0.0, head=-T('LAG_HEAD', 0.3), legL=0.0, legR=0.0,
              armL=-T('LAG', 1.0), armR=-T('LAG_R', 1.5))


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


def apply(p):
    b = p['body']; C.body(dx=b[0], fwd=b[1], dz=b[2], pitch=b[3], lean=b[4], twist=b[5])
    C.spine(*p['spine']); C.neck(*p['neck'])
    for s in 'LR':
        x, fw, up, pt, yw = p['f' + s]; C.foot(s, x=x, fwd=fw, up=max(up, 0.0), pitch=pt, yaw=yw)
    for s in 'LR':
        cu_, cb, w = p['c' + s]
        if w > 0.01: C.clav(s, AUTO_CLAV[0] + (cu_ - AUTO_CLAV[0]) * w, AUTO_CLAV[1] + (cb - AUTO_CLAV[1]) * w)
        o, fw, up, pr, cu, bd = p['h' + s]
        C.hand(s, out=o, fwd=fw, up=up, pron=pr, curl=cu, elbow=p['e' + s])
        if abs(bd) > 1e-6: C.wrist(s, bend=bd)


def build(f, u):
    apply(pose_at(T('POSE', f)))
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


C.author('HitReact', frames=FRAMES, build=build, loop=False, sheet_frames=FRAMES)
