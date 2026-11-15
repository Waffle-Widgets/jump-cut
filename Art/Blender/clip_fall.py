# The player's airborne loop: knees soft, toes hanging, arms out for balance, everything fluttering a little.
# In place - the game moves the capsule.
#   blender -b --factory-startup --python Art/Blender/clip_fall.py [-- noexport norender]
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

A = C.ARMLEN['L']
POLE = (0.5, -0.7, -0.7)                                   # elbows back, down and a little out


def build(f, u):
    s = math.sin(2 * math.pi * u); c = math.cos(2 * math.pi * u)
    s2 = math.sin(2 * math.pi * u + 1.1)                   # the arms lag the legs a little
    C.body(dz=2.0, pitch=6.0 + 1.5 * s, lean=1.0 * c, twist=2.0 * s)
    C.spine(x=-3.0 + 1.5 * c, z=-3.0 - 3.0 * s)
    C.neck(x=4.0 - 1.0 * c, z=1.5 * s)
    C.foot('L', fwd=11.0 + 3.0 * s, up=20.0 + 2.0 * c, pitch=30.0 + 4.0 * s)
    C.foot('R', fwd=-9.0 - 3.0 * s, up=13.0 - 2.0 * c, pitch=40.0 - 4.0 * s)
    C.hand('L', out=0.54 * A + 2.0 * s2, fwd=7.0 - 3.0 * s, up=-0.66 * A + 3.0 * s2, pron=62.0, curl=0.36 + 0.05 * s, elbow=POLE)
    C.hand('R', out=0.50 * A - 2.0 * s2, fwd=10.0 + 3.0 * s, up=-0.64 * A - 3.0 * s2, pron=62.0, curl=0.36 - 0.05 * s, elbow=POLE)


C.author('Fall', frames=24, build=build, loop=True, sheet_frames=8)
