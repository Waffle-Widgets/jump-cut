# The player's SPRINT (after the first power): the DRIVE PHASE of a 100 m runner, held as a loop.
# In place, 16 frames at 30 fps, one cycle = two steps (8 frames a step: faster cadence than the 18-frame run).
# Owner: "After he get's the first power he should be able to sprint like an actual sprint", with two photographs of
# sprinters driving out of the blocks. What those show, and what this clip is built to hit:
#   * the whole body on ONE line leaned ~40 degrees, from the pushing foot through hips and spine to the head;
#   * the rear leg fully extended at toe-off, the front knee driven high (thigh level, shin hanging back under it);
#   * a huge arm swing: front hand open at forehead height with a ~90 degree elbow, the other arm thrown far behind
#     and up, opened to ~125 degrees, fingers spread;
#   * eyes ahead and a little down the track, not up.
# The game moves the capsule at SPEED cm/s. He runs on the balls of his feet: the TOE is what is planted, and it
# moves straight back at SPEED/30 cm per frame for the three frames of each contact (t = 0, 1, 2); the heel rises
# through the contact, so the ankle is keyed from the toe (toe_key below). Toe-off is the fixed anchor, so a higher
# SPEED lands the foot further forward rather than over-stretching the leg behind.
#   blender -b --factory-startup --python Art/Blender/clip_sprint.py [-- norender noexport]
# Tuning without editing: any of the numbers below can be overridden from the environment, e.g. SPEED=900 KNEE_UP=40.
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C


def T(name, default):
    return float(os.environ.get(name, default))


N = 16
HALF = N / 2.0
SPEED = T('SPEED', 850.0)                # ground speed, cm/s: the one number to match to the game's sprint speed
STEP = SPEED / C.FPS                     # cm per frame while planted
TRACK = T('TRACK', 9.0)                  # each foot this far from the centre line

PELVIS_PITCH = T('PELVIS_PITCH', 37.0)   # forward lean of the pelvis
SPINE_PITCH = T('SPINE_PITCH', 7.0)      # a little more through the back; measured hip-to-neck line: 36 degrees: one line, not a hunch
NECK_UP = T('NECK_UP', 34.0)             # head lifted so the eyes look ahead and slightly down the track
DZ_LOW = T('DZ_LOW', -9.0)               # pelvis height in mid-contact
DZ_AMP = T('DZ_AMP', 6.0)                # how far he rises into the flight
PELVIS_FWD = T('PELVIS_FWD', 0.0)
HIP_TWIST = T('HIP_TWIST', 11.0)         # pelvis turns toward the knee that drives forward
CHEST_TWIST = T('CHEST_TWIST', 30.0)     # spine twist the other way (net shoulders = CHEST_TWIST - HIP_TWIST)
KNEE_UP = T('KNEE_UP', 38.0)             # ankle height at the top of the knee drive (thigh about level)
KNEE_FWD = T('KNEE_FWD', 29.0)
HEEL_UP = T('HEEL_UP', 58.0)             # ankle height when the heel whips up under the hip

# the foot as a rigid lever from the toe tip to the ankle (measured against lowest_by_frame, see the report)
FOOT_R = T('FOOT_R', 26.0)               # toe tip to ankle, cm
FOOT_A = T('FOOT_A', 31.0)               # angle of that lever above the floor with the sole flat
OFF_FWD = T('OFF_FWD', -44.0)            # ankle at toe-off (fwd = 0 is where the ankle rests, 6 cm behind the hip joint)
OFF_PITCH = T('OFF_PITCH', 50.0)
LAND_PITCH = T('LAND_PITCH', 10.0)       # lands on the ball of the foot
MID_PITCH = T('MID_PITCH', 22.0)

ARM_PH = T('ARM_PH', 2.0)                # frame (after the left foot lands) at which the LEFT hand is highest in front
A_FRONT = T('A_FRONT', 106.0)            # wrist direction from the shoulder, degrees forward of straight down
A_BACK = T('A_BACK', -74.0)
R_FRONT = T('R_FRONT', 0.73)             # shoulder-to-wrist distance, of the arm length: 0.71 is a 90 degree elbow
R_BACK = T('R_BACK', 0.89)               # 0.89 is about 125 degrees
OUT_FRONT = T('OUT_FRONT', 3.0)          # cm outside the shoulder: straight forward-back, never across the body
OUT_BACK = T('OUT_BACK', 11.0)
PRON = T('PRON', 68.0)                   # forearm roll with the hand in front
PRON_B = T('PRON_B', 45.0)               # and thrown behind (less: the upper arm's own spin adds to it there)
CURL = T('CURL', 0.10)                   # open hands, fingers spread


def toe_key(t, toe_fwd, pitch):
    """A contact key: the toe tip on the floor at toe_fwd, the heel lifted by pitch. Returns (t, fwd, up, pitch)."""
    a = math.radians(FOOT_A + pitch)
    return (t, toe_fwd - FOOT_R * math.cos(a), FOOT_R * (math.sin(a) - math.sin(math.radians(FOOT_A))), pitch)


_a_off = math.radians(FOOT_A + OFF_PITCH)
TOE_OFF = OFF_FWD + FOOT_R * math.cos(_a_off)          # where the toe leaves the floor
# One leg through the cycle. t = frames since that foot touched down. (t, fwd, up, pitch); pitch + = toes down.
LEG = [
    toe_key(0.0, TOE_OFF + 2 * STEP, LAND_PITCH),      # contact under / just behind the hips, on the ball of the foot
    toe_key(1.0, TOE_OFF + 1 * STEP, MID_PITCH),       # heel rising, knee and hip opening
    toe_key(2.0, TOE_OFF, OFF_PITCH),                  # toe-off: leg long behind him, on the body line
    (3.0, OFF_FWD - 8.0, 24.0, 78.0),                  # follow-through
    (4.5, OFF_FWD - 2.0, HEEL_UP - 12.0, 105.0),       # heel whips up
    (6.0, -22.0, HEEL_UP, 100.0),                      # tucked tight under the hip
    (8.0, 6.0, HEEL_UP - 8.0, 60.0),                   # knee leading through
    (10.0, KNEE_FWD, KNEE_UP, -8.0),                   # top of the knee drive (the other foot is at toe-off)
    (12.0, KNEE_FWD + 8.0, KNEE_UP - 5.0, -10.0),      # held high, shin starts to open
    (14.0, 30.0, 17.0, -2.0),                          # pawing back down
    (15.0, 15.0, 8.0, 5.0),
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
    """The drive. sw = +1 hand at the forehead in front, -1 arm thrown back and up behind the hip."""
    L = C.ARMLEN[s]
    k = (sw + 1) / 2
    ang = math.radians(A_BACK + (A_FRONT - A_BACK) * k)   # wrist direction from the shoulder: 0 = down, 90 = forward
    R = L * (R_BACK + (R_FRONT - R_BACK) * k)             # elbow opens at the back, closes in front
    out = OUT_BACK + (OUT_FRONT - OUT_BACK) * k
    # elbow: ABOVE the line at the back (a horizontal upper arm, forearm trailing), straight back as the hand passes
    # the hip, BELOW the line in front. Always well off the shoulder-to-wrist line, always a touch outward.
    pole = (T('PO_B', 0.30) + (T('PO_F', 0.9) - T('PO_B', 0.30)) * k, T('PF_B', -0.6) + (T('PF_F', -0.2) - T('PF_B', -0.6)) * k - 0.8 * math.sin(math.pi * k), 1.0 - 2.0 * k)
    C.hand(s, out=out, fwd=R * math.sin(ang), up=-R * math.cos(ang), pron=PRON_B + (PRON - PRON_B) * k, curl=CURL, elbow=pole)
    C.wrist(s, bend=T('WRIST', 0.0), side=T('WSIDE', 0.0))


def build(f, u):
    t = u * N                                         # left foot lands at t = 0, right at t = 8
    w = 2 * math.pi / N
    tw = math.cos(w * (t - ARM_PH + HALF))            # -1 when the RIGHT knee is up and the LEFT hand is in front
    st = math.cos(2 * math.pi * (t - 1.0) / HALF)     # +1 in mid-contact, -1 in mid-flight (both steps)
    side = math.sin(w * (t - 0.5))                    # +1 while he stands on the LEFT foot
    # Counter-rotation: the hips turn toward the knee that drives forward, the chest turns the other way and further,
    # so the shoulder of the forward arm leads. The head turns back so the face stays square to where he is going.
    C.body(dz=DZ_LOW + DZ_AMP * (0.5 - 0.5 * st), fwd=PELVIS_FWD, pitch=PELVIS_PITCH + 1.5 * st,
           twist=-HIP_TWIST * tw, dx=1.0 * side, lean=-2.0 * side)
    C.spine(x=SPINE_PITCH, y=2.0 * side, z=CHEST_TWIST * tw)
    C.neck(x=-NECK_UP, y=0.5 * side, z=-(CHEST_TWIST - HIP_TWIST) * tw * 0.9)
    for s, off in (('L', 0.0), ('R', HALF)):
        fw, up, pt = spline(LEG, t + off, N)
        C.foot(s, x=C.SGN[s] * TRACK, fwd=fw, up=max(up, 0.0), pitch=pt, yaw=2.0, knee_out=T('KNEE_OUT', 0.03) - T('KNEE_IN', 0.15) * min(1.0, max(up, 0.0) / 40.0))
    swL = math.cos(w * (t - ARM_PH))
    arm('L', swL)
    arm('R', -swL)
    if C.REACH and max(C.REACH.values()) > 0.05: print('REACH', f, {k: round(v, 1) for k, v in C.REACH.items() if v > 0.05})
    if 'dims' in C.a:                                 # where things really are, in (fwd, up) from the floor under the hips
        print('SPIN', f, {k: round(v) for k, v in C.SPIN.items()})
        P = lambda b: (round(-C.head(b).y, 1), round(C.head(b).z, 1))
        print('SPRINTDIM', f, {'hipL': P(C.LEG['L'][0]), 'ankL': P(C.LEG['L'][2]), 'shL': P(C.ARM['L'][0]),
                               'wrL': P(C.ARM['L'][2]), 'wrR': P(C.ARM['R'][2]), 'shR': P(C.ARM['R'][0]),
                               'head': P(C.NECK[1][0]), 'kneeR': P(C.LEG['R'][1]), 'hipR': P(C.LEG['R'][0])})


print('SPRINT', {'speed_cm_s': SPEED, 'cm_per_frame': round(STEP, 2), 'stride_cm_per_step': round(STEP * HALF, 1),
                 'toe_off_fwd': round(TOE_OFF, 1), 'leg_keys': [tuple(round(v, 1) for v in k) for k in LEG]})
C.author('Sprint', frames=N, build=build, loop=True)
