# The player's run: an anime dash. In place, 18 frames at 30 fps, one cycle = two steps. The game moves the capsule
# at 600 cm/s, so a planted foot travels back 20 cm per frame.
# Torso thrown far forward, head up, body low, long bounding stride, arms swept back behind him like streamers.
#   blender -b --factory-startup --python Art/Blender/clip_run.py [-- norender noexport]
# Tuning without editing: any of the numbers below can be overridden from the environment, e.g. ARM_DROP=45.
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C


def T(name, default):
    return float(os.environ.get(name, default))


N = 18
SPEED = 20.0          # cm per frame while planted
TRACK = 9.0           # each foot this far from the centre line

PELVIS_PITCH = T('PELVIS_PITCH', 13.0)   # forward lean of the pelvis
SPINE_PITCH = T('SPINE_PITCH', 24.0)     # more lean through the back (37 in all)
NECK_UP = T('NECK_UP', 38.0)             # head lifted back so he looks where he is going
DZ_LOW = T('DZ_LOW', -15.5)              # pelvis height at mid-stance
DZ_AMP = T('DZ_AMP', 6.0)                # how far he rises into the flight
PELVIS_FWD = T('PELVIS_FWD', 2.0)
ARM_REACH = T('ARM_REACH', 0.965)        # of the arm length: nearly straight, soft elbow
ARM_DROP = T('ARM_DROP', 30.0)           # degrees below horizontal that the swept-back arm points
ARM_OUT = T('ARM_OUT', 10.0)             # cm outside the shoulder
ARM_SWING = T('ARM_SWING', 9.0)          # degrees of counter-swing in time with the legs
KNEE = T('KNEE', 12.0)                   # cm taken off the knee drive: a higher knee tears more of the apron

# One leg through the cycle. t = frames since that foot touched down. (t, fwd, up, pitch); pitch + = toes down.
LEG = [                             # note: fwd = 0 is where the ankle rests, 6 cm BEHIND the hip joint
    (0.0,  34.0,  0.0,   0.0),      # contact ahead of the body, flat
    (1.0,  14.0,  0.0,   0.0),
    (2.0,  -6.0,  0.0,   0.0),
    (3.0, -26.0,  0.0,   0.0),      # last planted frame
    (4.0, -43.0, 10.0,  30.0),      # push-off, heel peels
    (5.5, -57.0, 25.0,  72.0),      # leg thrown long behind him, toes down
    (7.5, -46.0, 52.0, 100.0),      # heel kicks up toward the seat
    (9.5, -12.0, 50.0 - KNEE,  70.0),      # folded tight, knee coming through
    (11.5, 22.0, 38.0 - KNEE,  36.0),      # knee drives forward
    (13.5, 41.0, 25.0 - KNEE * 0.6,  8.0),
    (15.5, 49.0, 11.0, -10.0),      # shin reaches out
    (17.0, 45.0,  3.0,  -8.0),      # coming back onto the floor
]


def spline(pts, t, period):
    """Periodic Catmull-Rom through (t, a, b, c) points."""
    n = len(pts); t = t % period
    i = max(k for k in range(n) if pts[k][0] <= t + 1e-9)
    def P(k):
        w = (k // n) * period; p = pts[k % n]
        return (p[0] + w,) + tuple(p[1:])
    p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
    h = p2[0] - p1[0]; s = (t - p1[0]) / h
    out = []
    for c in range(1, len(p1)):
        d1 = (p2[c] - p1[c]) / h
        m1 = 0.5 * ((p1[c] - p0[c]) / (p1[0] - p0[0]) + d1) * h
        m2 = 0.5 * (d1 + (p3[c] - p2[c]) / (p3[0] - p2[0])) * h
        s2, s3 = s * s, s * s * s
        out.append((2 * s3 - 3 * s2 + 1) * p1[c] + (s3 - 2 * s2 + s) * m1 + (-2 * s3 + 3 * s2) * p2[c] + (s3 - s2) * m2)
    return out


def arm(s, sw, lag):
    """Swept back behind the body. sw = -1..1 in time with the legs (the small counter-swing); lag = the same wave a
    little later, which the hand follows so the arm trails like a streamer instead of moving as a stick.
    The elbow points UP and a little IN: with the arm behind him that is where the joint's own hinge is. Pointing it
    down wrings the upper arm half a turn and tears the shirt at the armpit (about 200 more torn edges)."""
    L = C.ARMLEN[s]
    ang = math.radians(ARM_DROP - ARM_SWING * sw)     # lifts and drops a little
    out = ARM_OUT + 2.5 * lag
    R = L * (ARM_REACH - 0.02 * sw)
    R = math.sqrt(max(R * R - out * out, 1.0))        # so `out` does not lengthen the reach
    C.hand(s, out=out, fwd=-R * math.cos(ang), up=-R * math.sin(ang),
           pron=T('PRON', 95.0), curl=0.36, elbow=(T('EL_IN', -0.9), 0.0, 1.0))
    C.wrist(s, bend=T('WRIST', 0.0) - 8.0 * lag, side=0.0)


def build(f, u):
    t = u * N                                         # left foot lands at t = 0, right at t = 9
    w = 2 * math.pi / N
    tw = math.cos(w * (t + 1.0))                      # +1 around the left foot's contact
    st = math.cos(2 * math.pi * (t - 1.5) / 9.0)      # +1 in mid-stance, -1 in flight (both steps)
    C.body(dz=DZ_LOW + DZ_AMP * (0.5 - 0.5 * st), fwd=PELVIS_FWD, pitch=PELVIS_PITCH + 2.0 * st,
           twist=-8.0 * tw, dx=-0.8 * math.sin(w * (t - 0.5)), lean=-2.0 * math.sin(w * (t - 0.5)))
    C.spine(x=SPINE_PITCH, z=18.0 * tw)
    C.neck(x=-NECK_UP, z=-9.0 * tw)
    for s, off in (('L', 0.0), ('R', 9.0)):
        fw, up, pt = spline(LEG, t + off, N)
        C.foot(s, x=C.SGN[s] * TRACK, fwd=fw, up=max(up, 0.0), pitch=pt, yaw=3.0, knee_out=0.04)
    # arms: both trail behind; each lifts a little as its own leg drives forward, the hand a beat late
    swL = math.cos(w * (t + 1.5)); lagL = math.cos(w * (t - 0.5))
    arm('L', swL, lagL)
    arm('R', -swL, -lagL)
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


C.author('Run', frames=N, build=build, loop=True)
