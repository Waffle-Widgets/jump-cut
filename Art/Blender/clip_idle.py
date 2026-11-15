# The player's idle, on the shared clip tool. Replaces idle_clip.py, which was written before cw_clip.py existed and so
# had none of what came after it: the forearm's whole 62 degree roll sat on the elbow ("his arms look bent, almost
# broken, when standing still" - owner, Nov 15), the apron bones were never driven (it clipped into him while he stood),
# and the ankles sat where the A-pose model rests them, 6 cm BEHIND the hip joints, so from the side his legs slanted
# and bowed.
# The stance is tuned against photographs of people standing idle (owner, Nov 15) with Art/Blender/posture_check.py:
# ear, shoulder, hip and ankle on one vertical line, knees straight, arms hanging beside the body, head level.
#   blender -b --factory-startup --python Art/Blender/clip_idle.py [-- noexport norender]
#   STUDY=1 ... writes a 4-frame 'IdleStudy' clip of stance variants instead, to look at side by side.
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C


def T(name, default):
    return float(os.environ.get(name, default))


FOOT_FWD = T('FOOT_FWD', 0.0)      # the feet stay where every other clip plants them, so nothing slides on a blend
STAGGER = T('STAGGER', 2.5)        # cm: left foot ahead, right foot behind
TOE_OUT = T('TOE_OUT', 11.0)
PEL_DX = T('PEL_DX', -1.6)         # weight a little onto his right leg
PEL_DZ = T('PEL_DZ', 0.6)          # straight legs: the knees measured 29 degrees bent at -0.8, 19 here (the bones' own kink)
PEL_FWD = T('PEL_FWD', -6.5)       # cm: the PELVIS moves back over the ankles instead. The model rests with its ankles
                                   # 6 cm behind its hip joints; standing like that, his legs slant and bow from the side.
PEL_PITCH = T('PEL_PITCH', 5.0)    # brings the shoulders forward over the hips: they sat 5-8 cm BEHIND them
TILT = T('TILT', 1.6)
SPINE = T('SPINE', -3.0)
HEAD = T('HEAD', -14.0)           # head LEVEL: at -2 it tipped 12 degrees down and he stared at the floor
ARM_REACH = T('ARM_REACH', 0.985)  # of the arm's length: 0.965 bent the elbow 30 degrees; this is a relaxed 15
HAND_OUT = T('HAND_OUT', 2.0)      # arms hang beside the body, not out in an A (they were 13-17 cm outside the hips)
HAND_FWD = T('HAND_FWD', 5.0)      # the hand rests a little in front of the hip, as in every reference photo
CLAV_UP = T('CLAV_UP', 24.0)       # 28 squares the shoulders but reads as a shrug when he is doing nothing
CLAV_BACK = T('CLAV_BACK', 6.0)    # shoulders back, chest open
PRON = T('PRON', 55.0)
CURL = T('CURL', 0.34)


# LIFE. The first version of this stand was measured into place and then barely moved: the same pose on both sides,
# a breath of 0.9 degrees and a sway of 0.7 cm. "He looks way too stiff in his idle stance" (owner, Nov 15). A person
# standing still is never symmetric and never still: the weight sits on one leg with that hip up and the other knee
# soft, the shoulders tilt the other way to balance, the chest and shoulders rise on the breath, the weight drifts,
# the head wanders. All of it loops in the 4 seconds.
WEIGHT_DX = T('WEIGHT_DX', -3.2)   # cm: weight onto his RIGHT leg
HIP_TILT = T('HIP_TILT', 3.2)      # the free (left) hip drops
SH_TILT = T('SH_TILT', 2.6)        # shoulders tip back the other way
BREATH = T('BREATH', 2.0)          # degrees of chest on a breath
DRIFT = T('DRIFT', 1.3)            # cm the weight wanders
LOOK = T('LOOK', 5.0)              # degrees the head turns, slowly


def pose(u, foot_fwd=FOOT_FWD, dz=PEL_DZ, reach=ARM_REACH, pfwd=PEL_FWD, pitch=PEL_PITCH, life=1.0):
    two = 2 * math.pi
    br = math.sin(two * u) * life                  # breath, once per loop
    sw = math.sin(two * (u + 0.18)) * life         # the weight drifting, a little behind it
    lk = math.sin(two * (u + 0.55)) * life         # the head, on its own clock
    fid = math.sin(two * 2 * (u + 0.3)) * life     # a faster, smaller settle, twice per loop
    C.body(dx=(WEIGHT_DX if life else PEL_DX) + DRIFT * sw, fwd=pfwd + 0.5 * fid, dz=dz + 0.4 * br,
           pitch=pitch + 0.5 * br, lean=-((HIP_TILT if life else TILT) + 0.8 * sw), twist=-2.0 * life + 0.8 * sw)
    C.spine(x=SPINE - BREATH * br, y=(SH_TILT + 1.0 * sw) * (1 if life else 0) + 0.5 * sw * (0 if life else 1), z=2.0 * life - 1.2 * sw)
    C.neck(x=HEAD + 0.6 * BREATH * br + 1.0 * fid, y=-1.2 * life - 0.4 * sw, z=LOOK * lk)
    # the standing (right) leg is straight under him; the free (left) foot sits a little forward and turned out
    C.foot('L', x=11.5 if life else 10.5, fwd=foot_fwd + (5.5 if life else STAGGER), yaw=TOE_OUT + (7.0 if life else 0.0))
    C.foot('R', x=-10.0 if life else -10.5, fwd=foot_fwd - (1.5 if life else STAGGER), yaw=TOE_OUT - 2.0 * (1 if life else 0))
    for s, fw_, out_, curl_ in (('L', HAND_FWD + 2.0 * life, HAND_OUT + 1.0 * life, CURL - 0.05 * life),
                                ('R', HAND_FWD - 1.5 * life, HAND_OUT, CURL + 0.05 * life)):
        C.clav(s, up=CLAV_UP + 1.3 * br, back=CLAV_BACK)
        C.hand(s, out=out_ + 0.5 * sw * C.SGN[s], fwd=fw_ + 1.2 * sw * C.SGN[s] + 0.6 * fid, up=-C.ARMLEN[s] * (reach - (0.02 if s == 'L' else 0.0) * (1 if life else 0)) + 0.6 * br,   # his left shoulder sits higher
               pron=PRON, curl=curl_ + 0.03 * fid, elbow=(0.3, -1.0, 0.0))


if os.environ.get('STUDY'):
    VAR = {1: dict(foot_fwd=0.0, dz=-1.2, reach=0.965),          # what the old idle did
           2: dict(foot_fwd=4.0, dz=-0.8, reach=0.99),
           3: dict(foot_fwd=7.0, dz=-0.8, reach=0.99),
           4: dict(foot_fwd=7.0, dz=-0.8, reach=0.99, pfwd=2.0, pitch=-3.0)}

    def build(f, u):
        pose(0.0, life=0.0, **VAR[f])

    C.author('IdleStudy', frames=4, build=build, loop=False, sheet_frames=4)
else:
    def build(f, u):
        pose(u)

    C.author('Idle', frames=120, build=build, loop=True)
