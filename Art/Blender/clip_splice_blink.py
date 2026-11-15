# Splice blink, the player's short teleport-dash: a quick low lunge with the left shoulder leading and the arms
# swept back, hit by frame 3, held two frames, then back to neutral.
#   blender -b --factory-startup --python Art/Blender/clip_splice_blink.py [-- noexport norender]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw_clip as C

A = C.ARMLEN['L']


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


BACKPOLE = (0.45, -1.0, 0.5)
LUNGE = P(body=dict(fwd=12.0, dz=-15.0, pitch=28.0, twist=-10.0), spine=dict(x=8.0, z=-14.0), neck=dict(x=-22.0, z=16.0),
          footL=dict(x=9.0, fwd=32.0, yaw=4.0, knee_out=0.2),
          footR=dict(x=-11.5, fwd=-22.0, up=11.5, pitch=40.0, yaw=10.0, knee_out=0.25),
          handL=dict(out=15.0, fwd=-0.40 * A, up=-0.72 * A, curl=0.5, elbow=BACKPOLE),
          handR=dict(out=17.0, fwd=-0.50 * A, up=-0.62 * A, curl=0.5, elbow=BACKPOLE))
N = P()
STEP = mix(N, LUNGE, 0.5); STEP['footL']['up'] = 6.0       # frame 2: the leading foot is in the air, not dragged
HOLD = mix(LUNGE, LUNGE, 0.0)
HOLD['body'].update(fwd=13.5, dz=-16.0, pitch=30.0)
BACK = mix(LUNGE, N, 0.55); BACK['footL']['up'] = 5.0; BACK['footR']['up'] = 5.0; BACK['footR']['pitch'] = 12.0
TL = [(0.0, N), (1 / 9.0, STEP), (2 / 9.0, LUNGE), (4 / 9.0, HOLD), (7 / 9.0, BACK), (1.0, N)]


def build(f, u):
    pose(at(u, TL))


C.author('SpliceBlink', frames=10, build=build, loop=False, sheet_frames=10)
