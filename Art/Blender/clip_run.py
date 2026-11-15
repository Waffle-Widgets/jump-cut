# The player's run: a SPRINTER. In place, 18 frames at 30 fps, one cycle = two steps. The game moves the capsule
# at 600 cm/s, so a planted foot travels back 20 cm per frame.
# History: v1 was an upright jog with a small elbow pump ("Forest Gump"); v2 was an arms-back ninja dash ("the Naruto
# run looks lame"). This one is a 100 m runner: modest forward lean with the chest proud and the head level, a big
# arm drive from the shoulder (hand from behind the hip up to the chin, open blade hands), high knee, heel tucked
# under the hip in recovery, long push-off.
#   blender -b --factory-startup --python Art/Blender/clip_run.py [-- norender noexport]
# Tuning without editing: any of the numbers below can be overridden from the environment, e.g. KNEE_UP=46.
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C


def T(name, default):
    return float(os.environ.get(name, default))


N = 18
SPEED = 20.0          # cm per frame while planted
TRACK = 9.0           # each foot this far from the centre line

PELVIS_PITCH = T('PELVIS_PITCH', 9.0)    # forward lean of the pelvis
SPINE_PITCH = T('SPINE_PITCH', 11.0)     # more lean through the back (20 in all)
NECK_UP = T('NECK_UP', 26.0)             # head lifted back level: eyes forward
DZ_LOW = T('DZ_LOW', -8.0)               # pelvis height at mid-stance
DZ_AMP = T('DZ_AMP', 5.0)                # how far he rises into the flight
PELVIS_FWD = T('PELVIS_FWD', 3.0)
HIP_TWIST = T('HIP_TWIST', 7.0)          # pelvis turns toward the leg that swings forward
CHEST_TWIST = T('CHEST_TWIST', 20.0)     # spine twist the other way (net shoulders = CHEST_TWIST - HIP_TWIST)
KNEE_UP = T('KNEE_UP', 42.0)             # ankle height at the top of the knee drive
KNEE_FWD = T('KNEE_FWD', 38.0)
HEEL_UP = T('HEEL_UP', 56.0)             # ankle height when the heel tucks under the hip

ARM_PH = T('ARM_PH', 4.0)                # frame (after the left foot lands) at which the LEFT hand is highest in front
A_FRONT = T('A_FRONT', 90.0)             # wrist direction from the shoulder, degrees forward of straight down
A_BACK = T('A_BACK', -36.0)
R_FRONT = T('R_FRONT', 0.66)             # shoulder-to-wrist distance, of the arm length: 0.68 is an 85 degree elbow
R_BACK = T('R_BACK', 0.85)               # 0.84 is 115 degrees
OUT_FRONT = T('OUT_FRONT', 1.5)         # cm outside the shoulder: straight forward-back, never across the body
OUT_BACK = T('OUT_BACK', 7.0)
PRON = T('PRON', 66.0)
CURL = T('CURL', 0.24)

# One leg through the cycle. t = frames since that foot touched down. (t, fwd, up, pitch); pitch + = toes down.
LEG = [                             # note: fwd = 0 is where the ankle rests, 6 cm BEHIND the hip joint
    (0.0,  34.0,  0.0,   0.0),      # contact just ahead of the hips
    (1.0,  14.0,  0.0,   0.0),
    (2.0,  -6.0,  0.0,   0.0),
    (3.0, -26.0,  0.0,   0.0),      # last planted frame
    (4.0, -39.0, 10.0,  30.0),      # toe-off: leg long behind him
    (5.2, -48.0, 25.0,  70.0),      # follow-through
    (6.8, -40.0, HEEL_UP - 10.0, 100.0),   # heel whips up
    (8.4, -18.0, HEEL_UP,  92.0),   # tucked tight under the hip
    (10.0, 10.0, HEEL_UP - 8.0,  62.0),    # knee leading through
    (11.6, KNEE_FWD - 6.0, KNEE_UP + 2.0,  30.0),   # knee drive, thigh close to level
    (13.2, KNEE_FWD + 4.0, KNEE_UP - 6.0,  12.0),   # top: shin hanging
    (15.0, 48.0, 14.0,  -6.0),      # shin reaches out
    (16.4, 45.0,  5.0,  -6.0),      # pawing back down
    (17.4, 39.5,  1.0,  -3.0),
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


def arm(s, sw):
    """The drive. sw = +1 hand at the chin in front, -1 hand behind the hip."""
    L = C.ARMLEN[s]
    k = (sw + 1) / 2
    ang = math.radians(A_BACK + (A_FRONT - A_BACK) * k)   # wrist direction from the shoulder: 0 = down, 90 = forward
    R = L * (R_BACK + (R_FRONT - R_BACK) * k)             # elbow opens at the back, closes in front
    out = OUT_BACK + (OUT_FRONT - OUT_BACK) * k
    # elbow: below the line in front, behind and a little above it at the back; always a touch outward
    pole = (0.30 - 0.22 * k, -1.0 + 0.7 * k, 0.25 - 1.25 * k)
    C.hand(s, out=out, fwd=R * math.sin(ang), up=-R * math.cos(ang), pron=PRON, curl=CURL, elbow=pole)
    C.wrist(s, bend=T('WRIST', 0.0), side=T('WSIDE', 0.0))


def build(f, u):
    t = u * N                                         # left foot lands at t = 0, right at t = 9
    w = 2 * math.pi / N
    tw = math.cos(w * (t - ARM_PH + 9.0))             # -1 when the RIGHT knee is up and the LEFT hand is at the chin
    st = math.cos(2 * math.pi * (t - 1.5) / 9.0)      # +1 in mid-stance, -1 in flight (both steps)
    side = math.sin(w * (t - 0.5))                    # +1 while he stands on the LEFT foot
    # Counter-rotation: the hips turn toward the knee that drives forward, the chest turns the other way and further,
    # so the shoulder of the forward arm leads. The head turns back so the face stays square to where he is going.
    C.body(dz=DZ_LOW + DZ_AMP * (0.5 - 0.5 * st), fwd=PELVIS_FWD, pitch=PELVIS_PITCH + 1.5 * st,
           twist=-HIP_TWIST * tw, dx=1.2 * side, lean=-2.5 * side)
    C.spine(x=SPINE_PITCH, y=2.0 * side, z=CHEST_TWIST * tw)
    C.neck(x=-NECK_UP, y=0.5 * side, z=-(CHEST_TWIST - HIP_TWIST) * tw * 0.9)
    for s, off in (('L', 0.0), ('R', 9.0)):
        fw, up, pt = spline(LEG, t + off, N)
        C.foot(s, x=C.SGN[s] * TRACK, fwd=fw, up=max(up, 0.0), pitch=pt, yaw=3.0, knee_out=0.04)
    swL = math.cos(w * (t - ARM_PH))
    arm('L', swL)
    arm('R', -swL)
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


if 'dims' in C.a:
    print('CWDIM', {'leglen': C.LEGLEN, 'armlen': C.ARMLEN, 'hip_z': C.HIP_Z, 'ank_z': {s: C.ANK[s].z for s in 'LR'},
                    'ank_y': C.ANK_Y})
C.author('Run', frames=N, build=build, loop=True)
