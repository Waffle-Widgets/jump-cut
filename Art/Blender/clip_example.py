# Smoke test and the smallest example of cw_clip: he stands, then lifts his right knee and raises his left fist.
#   blender -b --factory-startup --python Art/Blender/clip_example.py -- noexport
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C


def build(f, u):
    k = C.keys(u, [(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)])          # 0 -> 1 -> 0 over the clip
    C.body(dx=-3.0 * k, dz=-1.5, pitch=2.0 * k)                    # weight over his left... no: dx is toward his LEFT, so -3 is right
    C.spine(x=-1.0, z=6.0 * k)
    C.neck(x=-2.0)
    C.foot('L')                                                    # planted where it rests
    C.foot('R', fwd=18.0 * k, up=30.0 * k, pitch=25.0 * k)         # right knee comes up
    C.hand('L', out=4.0, fwd=3.0 + 30.0 * k, up=-50.0 + 38.0 * k, pron=62.0 - 30.0 * k, curl=0.34 + 0.66 * k, elbow=(0.5, -0.6, -0.6))
    C.hand('R')                                                    # hangs at his side


C.author('Example', frames=24, build=build, loop=True)
