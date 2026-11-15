# The player's run: in place, 18 frames at 30 fps, one cycle = two steps. The game moves the capsule at 600 cm/s,
# so a planted foot travels back 20 cm per frame.
#   blender -b --factory-startup --python Art/Blender/clip_run.py [-- norender noexport]
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

N = 18
SPEED = 20.0          # cm per frame while planted
TRACK = 9.0           # each foot this far from the centre line

# One leg through the cycle. t = frames since that foot touched down. (t, fwd, up, pitch); pitch + = toes down.
LEG = [                             # note: fwd = 0 is where the ankle rests, 6 cm BEHIND the hip joint
    (0.0,  34.0,  0.0,   0.0),      # contact ahead of the body, flat
    (1.0,  14.0,  0.0,   0.0),
    (2.0,  -6.0,  0.0,   0.0),
    (3.0, -26.0,  0.0,   0.0),      # last planted frame
    (4.0, -40.0, 11.0,  32.0),      # push-off, heel peels
    (5.5, -44.0, 24.0,  68.0),      # trails behind, toes down
    (7.5, -32.0, 44.0,  85.0),      # heel kicks up
    (9.5,  -8.0, 47.0,  62.0),      # folded, knee coming through
    (11.5, 14.0, 39.0,  34.0),      # knee drives forward
    (13.5, 32.0, 27.0,  10.0),
    (15.5, 43.0, 12.5,  -8.0),      # shin reaches
    (17.0, 42.0,  3.5,  -8.0),      # coming back onto the floor
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
    """sw = +1 this arm fully forward, -1 fully back."""
    L = C.ARMLEN[s]
    k = (sw + 1) / 2
    ang = math.radians(-8.0 + 86.0 * k)               # wrist direction from the shoulder: 0 = straight down, 90 = forward
    R = L * (0.74 - 0.08 * k)                         # elbow a little past 90 at the back, tighter in front
    C.hand(s, out=4.0 - 7.0 * k, fwd=R * math.sin(ang), up=-R * math.cos(ang),
           pron=70.0 + 25.0 * k, curl=0.75, elbow=(0.12, -0.75, -0.65))
    C.wrist(s, bend=0.0, side=0.0)


def build(f, u):
    t = u * N                                         # left foot lands at t = 0, right at t = 9
    c1 = math.cos(2 * math.pi * t / N)                # +1 when the left foot is in front
    bob = -10.5 + 7.0 * (0.5 - 0.5 * math.cos(2 * math.pi * (t - 1.5) / 9.0))      # lowest just after each contact
    C.body(dz=bob, pitch=6.0, twist=-5.0 * math.cos(2 * math.pi * (t + 1.0) / N), dx=-0.8 * math.sin(2 * math.pi * (t - 0.5) / N))
    C.spine(x=5.0, z=10.0 * math.cos(2 * math.pi * (t + 1.0) / N))
    C.neck(x=-11.0, z=-4.0 * math.cos(2 * math.pi * (t + 1.0) / N))
    for s, off in (('L', 0.0), ('R', 9.0)):
        fw, up, pt = spline(LEG, t + off, N)
        C.foot(s, x=C.SGN[s] * TRACK, fwd=fw, up=max(up, 0.0), pitch=pt, yaw=3.0, knee_out=0.04)
    # arms opposite the legs: the left arm is forward when the right leg is
    swL = math.cos(2 * math.pi * (t - 9.0 + 1.5) / N)
    arm('L', swL)
    arm('R', -swL)
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


print('CWDIM', {'leglen': C.LEGLEN, 'armlen': C.ARMLEN, 'hip_z': C.HIP_Z, 'ank_z': {s: C.ANK[s].z for s in 'LR'}, 'drop': C.DROP,
               'ank_y': C.ANK_Y, 'hip_y': {s: C.RH[C.LEG[s][0]].y for s in 'LR'}})
C.author('Run', frames=N, build=build, loop=True)
