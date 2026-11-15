# The player's walk: in place, 26 frames at 30 fps, one cycle = two steps, one foot always on the floor.
# A planted foot travels back at SPEED cm per frame. The game walks him at 300 cm/s (10 cm per frame), which no
# leg of this length can cover for a whole stance without over-reaching, so SPEED is what the leg allows.
#   blender -b --factory-startup --python Art/Blender/clip_walk.py [-- norender noexport]
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

N = 26
STEP = N // 2         # the other foot lands this many frames later
SPEED = 6.0           # cm per frame while planted (step length = 13 * 6 = 78 cm)
F0 = 42.0             # ankle at heel strike, cm in front of where it rests (which is 6 cm behind the hip joint)
TRACK = 8.5
TOE_D, HEEL_D, ANK_H = 21.0, 6.0, 11.0       # shoe: toe tip ahead of the ankle, heel behind it, ankle above the sole


def roll_up(pitch):
    """How high the ankle must sit for the shoe to touch the floor at this pitch (toes down +, toes up -)."""
    p = math.radians(abs(pitch))
    d = TOE_D if pitch > 0 else HEEL_D
    return max(0.0, d * math.sin(p) + ANK_H * (math.cos(p) - 1.0))


def stance(t):
    if t <= 2.0: pitch = -15.0 * (1.0 - t / 2.0)                       # heel strike, then the foot rolls flat
    elif t <= 8.0: pitch = 0.0
    else: pitch = 26.0 * ((t - 8.0) / (STEP - 8.0)) ** 1.5             # heel peels, toes stay down
    return (F0 - SPEED * t, roll_up(pitch), pitch)


LEG = [(float(t),) + stance(float(t)) for t in range(0, STEP + 1)] + [
    (14.0, -38.0, 11.0,  40.0),     # toes leave the floor
    (16.0, -27.0, 14.0,  44.0),     # foot trails, knee swings through
    (19.0,   4.0,  9.0,  20.0),     # passing the other leg
    (22.0,  33.0,  6.5,  -6.0),
    (24.5,  43.5,  5.0, -17.0),     # shin reaches, toes up
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
    """sw = +1 this arm fully forward, -1 fully back. A loose swing from the shoulder, elbow a little bent."""
    L = C.ARMLEN[s]
    k = (sw + 1) / 2
    ang = math.radians(-20.0 + 40.0 * k)
    R = L * (0.965 - 0.035 * k)                       # bends a touch more as it comes forward
    C.hand(s, out=6.5 - 2.0 * k, fwd=R * math.sin(ang), up=-R * math.cos(ang), pron=62.0 + 8.0 * k, curl=0.35)
    C.wrist(s, bend=0.0, side=0.0)


def build(f, u):
    t = u * N                                         # left heel strikes at t = 0, right at t = 13
    w = 2 * math.pi * t / N
    bob = -4.7 - 2.0 * math.cos(2 * w)                # lowest with both feet down, highest passing over the planted leg
    C.body(dz=bob, pitch=2.0, twist=-4.0 * math.cos(w), dx=1.8 * math.sin(w), lean=-1.2 * math.sin(w))
    C.spine(x=2.0, z=7.5 * math.cos(w), y=1.2 * math.sin(w))
    C.neck(x=-6.0, z=-3.0 * math.cos(w))
    for s, off in (('L', 0.0), ('R', float(STEP))):
        fw, up, pt = spline(LEG, t + off, N)
        C.foot(s, x=C.SGN[s] * TRACK, fwd=fw, up=max(up, 0.0), pitch=pt, yaw=6.0, knee_out=0.10)
    swL = -math.cos(2 * math.pi * (t - 1.0) / N)      # left arm forward while the right leg is
    arm('L', swL)
    arm('R', -swL)
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})


C.author('Walk', frames=N, build=build, loop=True)
