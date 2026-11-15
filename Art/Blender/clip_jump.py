# The player's jump launch: two frames of push-off, then the arms sweep up and the knees tuck into a rising pose.
# In place - the game moves the capsule.
#   blender -b --factory-startup --python Art/Blender/clip_jump.py [-- noexport norender]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

A = C.ARMLEN['L']
POLE = (0.5, -0.7, -0.7)                                   # elbows back, down and a little out, all clip long


def P(**over):
    p = {'body': dict(dx=0.0, fwd=0.0, dz=-1.2, pitch=0.0, lean=0.0, twist=0.0),
         'spine': dict(x=0.0, y=0.0, z=0.0), 'neck': dict(x=0.0, y=0.0, z=0.0),
         'footL': dict(x=10.5, fwd=0.0, up=0.0, pitch=0.0, yaw=8.0, knee_out=0.22),
         'footR': dict(x=-10.5, fwd=0.0, up=0.0, pitch=0.0, yaw=8.0, knee_out=0.22),
         'handL': dict(out=7.0, fwd=3.0, up=-0.965 * A, pron=62.0, curl=0.34, elbow=(0.35, -1.0, -0.1), bend=0.0, side=0.0),
         'handR': dict(out=7.0, fwd=3.0, up=-0.965 * A, pron=62.0, curl=0.34, elbow=(0.35, -1.0, -0.1), bend=0.0, side=0.0)}
    for k, v in over.items(): p[k].update(v)
    return p


def mix(p, q, t):
    out = {}
    for k in p:
        out[k] = {}
        for n, v in p[k].items():
            w = q[k][n]
            out[k][n] = tuple(a + (b - a) * t for a, b in zip(v, w)) if isinstance(v, tuple) else v + (w - v) * t
    return out


def pose(p):
    C.body(**p['body']); C.spine(**p['spine']); C.neck(**p['neck'])
    for s in 'LR': C.foot(s, **p['foot' + s])
    for s in 'LR':
        h = dict(p['hand' + s]); b = h.pop('bend'); sd = h.pop('side')
        C.hand(s, **h); C.wrist(s, b, sd)


def at(u, tl):
    if u <= tl[0][0]: return tl[0][1]
    if u >= tl[-1][0]: return tl[-1][1]
    for (u0, p0), (u1, p1) in zip(tl, tl[1:]):
        if u0 <= u <= u1: return mix(p0, p1, C.smooth(u, u0, u1))


PUSH0 = P(body=dict(dz=8.0, pitch=5.0), spine=dict(x=-4.0), neck=dict(x=-3.0),
          footL=dict(fwd=-3.0, up=13.0, pitch=44.0), footR=dict(fwd=-4.0, up=13.0, pitch=46.0),
          handL=dict(out=10.0, fwd=-8.0, up=-0.90 * A, curl=0.45, elbow=POLE),
          handR=dict(out=10.0, fwd=-8.0, up=-0.90 * A, curl=0.45, elbow=POLE))
PUSH1 = P(body=dict(dz=8.0, pitch=4.0), spine=dict(x=-5.0), neck=dict(x=-4.0),
          footL=dict(fwd=-2.0, up=13.5, pitch=48.0), footR=dict(fwd=-5.0, up=13.5, pitch=50.0),
          handL=dict(out=12.0, fwd=2.0, up=-0.88 * A, curl=0.45, elbow=POLE),
          handR=dict(out=12.0, fwd=6.0, up=-0.86 * A, curl=0.45, elbow=POLE))
# the top of the sweep: arms a touch higher than where they settle (a little overshoot)
OVER = P(body=dict(dz=3.0, pitch=7.0), spine=dict(x=-4.0, z=-4.0), neck=dict(x=-2.0),
         footL=dict(fwd=13.0, up=24.0, pitch=28.0), footR=dict(fwd=-10.0, up=16.0, pitch=44.0),
         handL=dict(out=0.40 * A, fwd=12.0, up=-0.36 * A, curl=0.40, elbow=POLE),
         handR=dict(out=0.30 * A, fwd=0.52 * A, up=-0.18 * A, curl=0.40, elbow=POLE))
RISE = P(body=dict(dz=2.0, pitch=6.0), spine=dict(x=-3.0, z=-3.0), neck=dict(x=0.0),
         footL=dict(fwd=11.0, up=20.0, pitch=30.0), footR=dict(fwd=-9.0, up=13.0, pitch=40.0),
         handL=dict(out=0.48 * A, fwd=9.0, up=-0.52 * A, curl=0.38, elbow=POLE),
         handR=dict(out=0.40 * A, fwd=0.40 * A, up=-0.36 * A, curl=0.38, elbow=POLE))
TL = [(0.0, PUSH0), (1 / 9.0, PUSH1), (5 / 9.0, OVER), (1.0, RISE)]


def build(f, u):
    pose(at(u, TL))


C.author('Jump', frames=10, build=build, loop=False, sheet_frames=10, stance=(0.2, None))
