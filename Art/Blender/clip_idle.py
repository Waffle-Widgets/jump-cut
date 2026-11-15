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
TOE_OUT = T('TOE_OUT', 10.0)
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
HAND_FWD = T('HAND_FWD', 3.0)      # the hand rests a little in front of the hip, as in every reference photo
CLAV_UP = T('CLAV_UP', 24.0)       # 28 squares the shoulders but reads as a shrug when he is doing nothing
CLAV_BACK = T('CLAV_BACK', 6.0)    # shoulders back, chest open
PRON = T('PRON', 55.0)
CURL = T('CURL', 0.34)


# THE STAND, third reference (owner, Nov 15, a line drawing of an anime hero standing): "His shoulders should be
# straight while his arms hang down not touching his torso." Read off the drawing: the shoulder line is level and
# square; the arms hang CLEAR of the body with daylight between arm and ribs, elbows a little out and softly bent,
# hands as loose fists at the top of the thigh; the feet are wider than the shoulders with one turned out; the chest
# is up. The stand before this one hung the arms straight down against the body, and brought down from the A-pose
# like that the shoulders slope ("drooping") and the arms press into the torso.
BREATH = T('BREATH', 2.2)          # degrees of chest on a breath
DRIFT = T('DRIFT', 1.2)            # cm the weight wanders side to side
LOOK = T('LOOK', 4.0)              # degrees the head turns, slowly
FEET_X = T('FEET_X', 14.0)         # cm either side of the centre line: wider than the shoulders
ARM_OUT = T('ARM_OUT', 9.5)        # cm the wrist hangs outside the shoulder joint: daylight between arm and ribs
ARM_FWD = T('ARM_FWD', 1.0)
ARM_BEND = T('ARM_BEND', 0.972)    # of the arm's length: a soft elbow, about 27 degrees
ELBOW_OUT = T('ELBOW_OUT', 0.6)    # how far outward the elbow points (0 is straight back)
PALM = T('PALM', 96.0)             # forearm roll: the back of the fist faces out and a little forward
FIST = T('FIST', 0.85)             # loose fists
SH_UP = T('SH_UP', 36.0)           # collarbone lift: 24 drooped; with the arms held out, 36 is level, not a shrug
SH_BACK = T('SH_BACK', 2.0)        # shoulders wide rather than pulled back
CHEST = T('CHEST', -5.0)           # chest up


def pose(u, foot_fwd=FOOT_FWD, dz=PEL_DZ, reach=ARM_REACH, pfwd=PEL_FWD, pitch=PEL_PITCH, life=1.0):
    two = 2 * math.pi
    br = math.sin(two * u) * life                  # breath, once per loop
    sw = math.sin(two * (u + 0.18)) * life         # the weight drifting, a little behind it
    lk = math.sin(two * (u + 0.55)) * life         # the head, on its own clock
    fid = math.sin(two * 2 * (u + 0.3)) * life     # a smaller, faster settle, twice per loop
    C.body(dx=-1.0 * life + DRIFT * sw, fwd=pfwd, dz=dz + 0.4 * br, pitch=pitch + 0.5 * br, lean=-(0.8 * life + 0.7 * sw), twist=0.6 * sw)
    C.spine(x=(CHEST if life else SPINE) - BREATH * br, y=0.8 * life + 0.6 * sw, z=-0.9 * sw)
    C.neck(x=HEAD + 0.6 * BREATH * br + 0.6 * fid, y=-0.4 * sw, z=LOOK * lk)
    C.foot('L', x=FEET_X, fwd=foot_fwd + 1.5 * life, yaw=TOE_OUT + 4.0 * life)
    C.foot('R', x=-FEET_X, fwd=foot_fwd - 0.5 * life, yaw=TOE_OUT + 16.0 * life)     # one foot turned out, as drawn
    for s in 'LR':
        C.clav(s, up=SH_UP + 1.2 * br, back=SH_BACK)
        o_ = ARM_OUT + 0.5 * br + 0.5 * sw * C.SGN[s]; f_ = ARM_FWD + 0.8 * sw * C.SGN[s] + 0.4 * fid
        r_ = C.ARMLEN[s] * ARM_BEND                 # the wrist sits this far from the shoulder, whichever way it hangs:
        C.hand(s, out=o_, fwd=f_, up=-math.sqrt(max(1.0, r_ * r_ - o_ * o_ - f_ * f_)) + 0.6 * br,   # out AND down would lock the elbow
               pron=PALM, curl=FIST + 0.03 * fid, elbow=(ELBOW_OUT, -1.0, 0.0))


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
