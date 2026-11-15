# The player's idle, on the shared clip tool. Replaces idle_clip.py, which was written before cw_clip.py existed and so
# had none of what came after it: the forearm's whole 62 degree roll sat on the elbow ("his arms look bent, almost
# broken, when standing still" - owner, Nov 15), the apron bones were never driven (it clipped into him while he stood),
# and the ankles sat where the A-pose model rests them, 6 cm BEHIND the hip joints, so from the side his legs slanted
# and bowed.
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
PEL_DZ = T('PEL_DZ', -0.8)         # barely unlocked knees
PEL_FWD = T('PEL_FWD', -6.5)       # cm: the PELVIS moves back over the ankles instead. The model rests with its ankles
                                   # 6 cm behind its hip joints; standing like that, his legs slant and bow from the side.
PEL_PITCH = T('PEL_PITCH', 0.0)
TILT = T('TILT', 1.6)
SPINE = T('SPINE', -1.5)
HEAD = T('HEAD', -2.0)
ARM_REACH = T('ARM_REACH', 0.99)   # of the arm's length: 0.965 bent the elbow 30 degrees
HAND_OUT = T('HAND_OUT', 8.0)
HAND_FWD = T('HAND_FWD', 2.0)
PRON = T('PRON', 55.0)
CURL = T('CURL', 0.34)


def pose(u, foot_fwd=FOOT_FWD, dz=PEL_DZ, reach=ARM_REACH, pfwd=PEL_FWD, pitch=PEL_PITCH):
    br = math.sin(2 * math.pi * u)                 # breath, once per loop
    sw = math.sin(2 * math.pi * (u + 0.18))        # sway, a little behind it
    C.body(dx=PEL_DX + 0.7 * sw, fwd=pfwd, dz=dz + 0.35 * br, pitch=pitch, lean=-(TILT + 0.5 * sw))
    C.spine(x=SPINE - 0.9 * br, y=0.5 * sw)
    C.neck(x=HEAD + 0.63 * br, y=-0.3 * sw)
    C.foot('L', x=10.5, fwd=foot_fwd + STAGGER, yaw=TOE_OUT)
    C.foot('R', x=-10.5, fwd=foot_fwd - STAGGER, yaw=TOE_OUT)
    for s in 'LR':
        C.hand(s, out=HAND_OUT, fwd=HAND_FWD, up=-C.ARMLEN[s] * reach + 0.25 * br, pron=PRON, curl=CURL, elbow=(0.3, -1.0, 0.0))


if os.environ.get('STUDY'):
    VAR = {1: dict(foot_fwd=0.0, dz=-1.2, reach=0.965),          # what the old idle did
           2: dict(foot_fwd=4.0, dz=-0.8, reach=0.99),
           3: dict(foot_fwd=7.0, dz=-0.8, reach=0.99),
           4: dict(foot_fwd=7.0, dz=-0.8, reach=0.99, pfwd=2.0, pitch=-3.0)}

    def build(f, u):
        pose(0.0, **VAR[f])

    C.author('IdleStudy', frames=4, build=build, loop=False, sheet_frames=4)
else:
    def build(f, u):
        pose(u)

    C.author('Idle', frames=120, build=build, loop=True)
