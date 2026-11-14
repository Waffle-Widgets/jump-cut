"""Draws Jump Cut's effect art and HUD icons as PNG sheets, from code (issues #42, #44, #49).

Everything is drawn with numpy and Pillow from shapes and seeded noise - no downloads, no model, nothing to
credit. Run:

    python tools/make_fx.py            # writes Art/FX/*.png, Art/UI/T_Icon_*.png and Art/FX/fx_manifest.json
    python tools/make_fx.py --check    # also writes Art/FX/_check/*.png (frames on a mid-grey card, to look at)

The look follows the `niagara-fx` lesson: SOLID SHAPES WITH A DARK OUTLINE read at the game camera, soft painted
texture does not. So every sheet is a few flat tones with hard edges and a dark rim, like the cel shader.

Sheets are RGBA, straight (not premultiplied) alpha, laid out left-to-right then top-to-bottom, frame 0 top-left -
the order Unreal's SubUV / flipbook node reads. `fx_manifest.json` records each file's grid, frame count, frame
size and what it is for; the builder reads the numbers from there, not from this docstring.

Tintable pieces (rings, markers, prompts, speed lines) are WHITE on alpha so one texture serves every power
colour: multiply by the colour in the material.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FX = os.path.join(ROOT, 'Art', 'FX')
UI = os.path.join(ROOT, 'Art', 'UI')
SS = 3  # supersample: draw at 3x and shrink, so hard edges come out clean rather than stair-stepped

OUTLINE = (24, 20, 34)
CYAN = (120, 232, 255)        # Freeze Frame (HUD cyan; the pale `#DCF2F5` is its highlight)
CYAN_PALE = (220, 242, 245)
VIOLET = (158, 89, 255)       # Splice, WBP_HUD's SpliceBox (0.62, 0.35, 1.0)
VIOLET_PALE = (226, 204, 255)
AMBER = (255, 190, 70)        # Rewind (not in the demo's beats; icon only)

manifest = {}


# ---------------------------------------------------------------- helpers
def grid(size):
    """x, y in -1..1 over a square of `size` pixels (already supersampled by the caller)."""
    a = (np.arange(size) + 0.5) / size * 2.0 - 1.0
    return np.meshgrid(a, a)


def value_noise(size, cells, seed, octaves=3):
    """Smooth seeded noise 0..1, tiling-free, bilinear with smoothstep - enough for ragged cel edges."""
    rng = np.random.default_rng(seed)
    out = np.zeros((size, size))
    amp, total = 1.0, 0.0
    for _ in range(octaves):
        g = rng.random((cells + 2, cells + 2))
        t = np.linspace(0, cells, size, endpoint=False)
        i = t.astype(int)
        f = t - i
        f = f * f * (3 - 2 * f)
        a = g[np.ix_(i, i)]
        b = g[np.ix_(i, i + 1)]
        c = g[np.ix_(i + 1, i)]
        d = g[np.ix_(i + 1, i + 1)]
        fx = f[None, :]
        fy = f[:, None]
        out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
        total += amp
        amp *= 0.5
        cells *= 2
    return out / total


def layer(canvas, mask, colour, alpha=1.0):
    """Paint `colour` where `mask` is true (hard edge), straight alpha, over what is there."""
    m = mask.astype(np.float64) * alpha
    for k in range(3):
        canvas[..., k] = canvas[..., k] * (1 - m) + colour[k] * m
    canvas[..., 3] = np.maximum(canvas[..., 3], m * 255.0)


def dilate(mask, r):
    """Grow a boolean mask by r pixels (used for the dark outline). Padded, so a shape touching one edge of the
    frame does not grow an outline on the opposite edge (np.roll alone wraps around - it drew a dark line under
    every explosion frame whose cloud reached the top)."""
    h, w = mask.shape
    pad = np.pad(mask, r)
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r and (dx or dy):
                out |= pad[r + dy:r + dy + h, r + dx:r + dx + w]
    return out


def shrink(canvas, size):
    im = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), 'RGBA')
    # premultiply before the resize so transparent pixels do not bleed their (black) colour into the edge
    a = np.asarray(im, dtype=np.float64)
    pm = a.copy()
    pm[..., :3] *= a[..., 3:4] / 255.0
    small = np.asarray(Image.fromarray(pm.astype(np.uint8), 'RGBA').resize((size[0], size[1]), Image.LANCZOS),
                       dtype=np.float64)
    al = np.maximum(small[..., 3:4], 1e-6)
    small[..., :3] = np.clip(small[..., :3] * 255.0 / al, 0, 255)
    return Image.fromarray(small.astype(np.uint8), 'RGBA')


def new(size_w, size_h=None):
    return np.zeros((size_h or size_w, size_w, 4), dtype=np.float64)


def sheet(name, frames, cols, folder=FX, what='', notes=''):
    fw, fh = frames[0].size
    rows = int(math.ceil(len(frames) / cols))
    im = Image.new('RGBA', (fw * cols, fh * rows), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        im.paste(f, ((i % cols) * fw, (i // cols) * fh))
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name + '.png')
    im.save(path, optimize=True)
    manifest[name] = {'file': os.path.relpath(path, ROOT).replace('\\', '/'), 'cols': cols, 'rows': rows,
                      'frames': len(frames), 'frame_px': [fw, fh], 'sheet_px': list(im.size),
                      'for': what, 'notes': notes}
    return im


def single(name, im, folder=FX, what='', notes=''):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name + '.png')
    im.save(path, optimize=True)
    manifest[name] = {'file': os.path.relpath(path, ROOT).replace('\\', '/'), 'cols': 1, 'rows': 1, 'frames': 1,
                      'frame_px': list(im.size), 'sheet_px': list(im.size), 'for': what, 'notes': notes}


def ease_out(t, p=2.0):
    return 1.0 - (1.0 - t) ** p


# ---------------------------------------------------------------- the beat-1 explosion
def explosion():
    """36 frames, 6 x 6, 256 px. A cel explosion in three acts: a white flash that eats the frame, a fireball in
    four flat tones whose ragged edge is seeded noise, then the fire is eaten from inside by noise until only
    dark smoke puffs are left, drifting up and thinning. At 30 fps it lasts 1.2 s; in bullet time (0.25) the
    player watches it for almost five."""
    S = 256 * SS
    x, y = grid(S)
    n1 = value_noise(S, 5, 11)
    n2 = value_noise(S, 9, 12)
    n3 = value_noise(S, 4, 13)
    ang = np.arctan2(y, x)
    frames = []
    N = 36
    for i in range(N):
        t = i / (N - 1)
        c = new(S)
        rise = 0.28 * ease_out(t, 1.5)
        r = np.hypot(x, y + rise * 0.6)
        # ragged radius: spikes early (a burst), lumps later (a cloud)
        spikes = 0.10 * np.cos(ang * 9 + n1 * 6.0) * max(0.0, 1.0 - t * 3.0)
        rr = r - spikes + (n1 - 0.5) * 0.36 + (n2 - 0.5) * 0.16
        R = 0.14 + 0.52 * ease_out(min(1.0, t / 0.45), 2.6)      # stays inside the frame with its noise and its rise
        # the fire dies from the inside: a noise threshold that climbs with time opens holes in it
        die = max(0.0, (t - 0.28) / 0.72)
        alive = (n3 * 0.65 + n2 * 0.35) > (die * 1.18 - 0.08)
        smoke = (rr < R) & ((n2 * 0.6 + n1 * 0.4) > (max(0.0, (t - 0.62) / 0.38) * 1.05 - 0.02))
        fire = (rr < R * 0.90) & alive & (t < 0.92)
        hot = (rr < R * 0.66) & (n3 > die * 1.5 - 0.05) & (t < 0.72)
        core = (rr < R * (0.42 - 0.5 * die)) & (t < 0.5)
        body = smoke | fire
        layer(c, dilate(body, SS * 3) & ~body, OUTLINE)
        layer(c, smoke, (58, 50, 66))
        layer(c, smoke & ((n1 + (y * 0.5)) < 0.42), (92, 82, 98))          # lit top of the smoke
        layer(c, fire, (226, 84, 34))
        layer(c, hot, (255, 176, 46))
        layer(c, core, (255, 246, 200))
        if t < 0.09:                                                      # the flash: frames 0-3
            flash = r < (0.35 + 6.0 * t)
            layer(c, flash, (255, 255, 240), alpha=1.0 - t / 0.09 * 0.55)
        # debris: a dozen dark chips flying out on fixed bearings
        rng = np.random.default_rng(5)
        for _ in range(14):
            a = rng.uniform(0, 2 * math.pi)
            sp = rng.uniform(0.55, 1.15)
            sz = rng.uniform(0.022, 0.045)
            d = ease_out(t, 2.2) * sp
            px, py = math.cos(a) * d, math.sin(a) * d * 0.8 + 0.45 * t * t - 0.05
            chip = (np.abs(x - px) + np.abs(y - py) < sz) & (t > 0.12) & (t < 0.85) & (np.hypot(px, py) < 0.93)
            layer(c, chip, OUTLINE)
        frames.append(shrink(c, (256, 256)))
    sheet('T_FX_Explosion_6x6', frames, 6, what='Beat 1: the blast at the crashed car that opens the bullet-time window',
          notes='36 frames. Unlit, masked or translucent. Play once at ~30 fps on a camera-facing quad about 450 cm '
                'wide, centred ~150 cm above the car. Pairs with SFX_Explosion.')
    return frames


# ---------------------------------------------------------------- hit flashes
def hit_flash():
    """16 frames, 4 x 4, 256 px. A punch landing: a white star with uneven spikes that opens fast and thins to
    lines, with a hard dark rim. White and pale yellow only, so it reads on any character."""
    S = 256 * SS
    x, y = grid(S)
    ang = np.arctan2(y, x)
    r = np.hypot(x, y)
    rng = np.random.default_rng(21)
    k = 11
    lens = rng.uniform(0.55, 1.0, k)
    offs = np.sort(rng.uniform(0, 2 * math.pi, k))
    frames = []
    N = 16
    for i in range(N):
        t = (i + 1) / N                                           # frame 0 already shows the hit
        c = new(S)
        grow = ease_out(min(1.0, t / 0.3), 2.5)
        thin = max(0.03, 0.5 * (1.0 - t) ** 1.6)
        star = np.zeros_like(r, dtype=bool)
        for j in range(k):
            da = np.abs((ang - offs[j] + math.pi) % (2 * math.pi) - math.pi)
            length = 0.92 * lens[j] * grow
            inner = 0.75 * length * max(0.0, (t - 0.35) / 0.65)          # the spikes leave the centre late on
            width = thin * (1.0 - r / max(length, 1e-6))
            star |= (da * np.maximum(r, 0.05) < width * 0.42) & (r < length) & (r > inner)
        blob = r < 0.34 * grow * (1.0 - t) ** 0.8
        body = star | blob
        layer(c, dilate(body, SS * 2) & ~body, OUTLINE)
        layer(c, body, (255, 232, 130))
        layer(c, (star & (r < 0.6 * grow)) | (r < 0.26 * grow * (1.0 - t)), (255, 255, 255))
        ring_r = 0.15 + 0.8 * ease_out(t, 2.0)
        ring = (np.abs(r - ring_r) < 0.03 * (1.0 - t)) & (t > 0.1)
        layer(c, ring, (255, 255, 255))
        frames.append(shrink(c, (256, 256)))
    sheet('T_FX_HitFlash_4x4', frames, 4, what='Beats 2-3: a punch landing (player on goon, goon on player, the boss)',
          notes='16 frames. Play once at ~40 fps on a camera-facing quad ~120 cm wide at the hit point. Scale 1.6 '
                'and tint amber for the combo finisher. Pairs with SFX_PunchHit1/2/3.')
    return frames


# ---------------------------------------------------------------- speed lines
def speed_lines():
    """8 frames, 4 x 2, 960 x 540 each. Anime focus lines: white wedges from the screen edge toward the centre,
    leaving the middle clear. Each frame reshuffles the wedges, so cycling them at 12-15 fps makes the lines jitter."""
    W, H = 960 * 2, 540 * 2          # 2x supersample is enough for straight wedges
    xs = (np.arange(W) + 0.5) / W * 2 - 1
    ys = (np.arange(H) + 0.5) / H * 2 - 1
    x, y = np.meshgrid(xs * (W / H), ys)
    ang = np.arctan2(y, x)
    r = np.hypot(x, y)
    frames = []
    for i in range(8):
        rng = np.random.default_rng(100 + i)
        c = new(W, H)
        mask = np.zeros_like(r, dtype=bool)
        dark = np.zeros_like(r, dtype=bool)
        for _ in range(64):
            a = rng.uniform(0, 2 * math.pi)
            w = rng.uniform(0.004, 0.022)
            tip = rng.uniform(0.62, 1.15)
            da = np.abs((ang - a + math.pi) % (2 * math.pi) - math.pi)
            wedge = (da < w * np.clip((r - tip) / 0.9, 0, 1)) & (r > tip)
            if rng.random() < 0.22:
                dark |= wedge
            else:
                mask |= wedge
        layer(c, dark, OUTLINE, alpha=0.85)
        layer(c, mask, (255, 255, 255))
        frames.append(shrink(c, (960, 540)))
    sheet('T_FX_SpeedLines_4x2', frames, 4, what='The combo finisher (and optionally the Splice blink): a full-screen overlay',
          notes='8 frames of 960x540. A UMG Image stretched full-screen or a post-process blend; cycle at 12-15 fps '
                'for 0.25 s. White with some dark wedges; the centre 60% of the screen is clear.')
    return frames


# ---------------------------------------------------------------- Freeze Frame overlay
def freeze_overlay():
    """One 1920 x 1080 frame laid over the screen while time is stopped. It is a film frame: a pale cyan vignette,
    rounded-corner gate, corner brackets and four focus ticks. No sprocket holes on the picture area and no
    lettering - the countdown number is the HUD's."""
    W, H = 1920, 1080
    S = 2
    xs = (np.arange(W * S) + 0.5) / (W * S) * 2 - 1
    ys = (np.arange(H * S) + 0.5) / (H * S) * 2 - 1
    x, y = np.meshgrid(xs, ys)
    c = new(W * S, H * S)
    # vignette: stepped (cel), three bands
    d = np.maximum(np.abs(x) ** 2.4, np.abs(y) ** 2.4) + 0.25 * (x * x + y * y)
    layer(c, d > 0.62, CYAN_PALE, alpha=0.10)
    layer(c, d > 0.86, CYAN, alpha=0.16)
    layer(c, d > 1.08, CYAN, alpha=0.24)
    ax, ay = np.abs(x), np.abs(y)
    px = 1.0 / (W * S / 2)               # one pixel in x units
    py = 1.0 / (H * S / 2)
    # the gate line
    gate = ((np.abs(ax - 0.94) < 3 * px) & (ay < 0.90)) | ((np.abs(ay - 0.90) < 3 * py) & (ax < 0.94))
    layer(c, gate, CYAN_PALE, alpha=0.55)
    # corner brackets
    br = (((ax > 0.80) & (ax < 0.90) & (np.abs(ay - 0.82) < 5 * py)) |
          ((ay > 0.64) & (ay < 0.82) & (np.abs(ax - 0.90) < 5 * px)))
    layer(c, br, (255, 255, 255), alpha=0.9)
    # focus ticks at the middle of each edge
    tk = (((ax < 3 * px) & (ay > 0.80) & (ay < 0.90)) | ((ay < 3 * py) & (ax > 0.88) & (ax < 0.94)))
    layer(c, tk, (255, 255, 255), alpha=0.9)
    single('T_FX_FreezeFrame_Overlay', shrink(c, (W, H)), what='Freeze Frame is on: the look of stopped time',
           notes='1920x1080, straight alpha, mostly transparent. A full-screen UMG Image shown while FreezeActive; '
                 'fade in over 0.1 s. Pairs with SFX_FreezeFrameOn.')


# ---------------------------------------------------------------- Splice blink trail
def splice_trail():
    """8 frames, 1 column... laid 2 x 4, 512 x 128 each. The cut: a violet streak with a hard white core that
    snaps to full length at once and then breaks into film-frame segments that thin away. Stretch it between the
    place the player left and the place he arrived."""
    W, H = 512 * SS, 128 * SS
    xs = (np.arange(W) + 0.5) / W
    ys = (np.arange(H) + 0.5) / H * 2 - 1
    x, y = np.meshgrid(xs, ys)
    n = value_noise(W, 24, 31)[:H, :]
    frames = []
    N = 8
    for i in range(N):
        t = i / (N - 1)
        c = new(W, H)
        taper = np.sin(np.clip(x, 0, 1) * math.pi) ** 0.35           # pointed at both ends
        half = (0.62 * (1.0 - t) ** 1.3 + 0.03) * taper
        # segments: gaps open up along the streak as it dies, like frames of film pulling apart
        seg = ((x * 9.0 + t * 0.6) % 1.0) > (t * 0.78)
        ragged = half * (0.8 + 0.4 * n)
        body = (np.abs(y) < ragged) & seg & (x > 0.02) & (x < 0.98)
        core = (np.abs(y) < ragged * 0.38) & seg & (t < 0.7)
        layer(c, dilate(body, SS * 2) & ~body, OUTLINE)
        layer(c, body, VIOLET)
        layer(c, body & (np.abs(y) < ragged * 0.68), VIOLET_PALE)
        layer(c, core, (255, 255, 255))
        frames.append(shrink(c, (512, 128)))
    sheet('T_FX_SpliceTrail_2x4', frames, 2, what='Beat 3 onward: the Splice blink, and the moment the boss hands it over',
          notes='8 frames of 512x128. A quad stretched from the blink start to the blink end (600 cm long, ~90 cm '
                'tall), facing the camera, played once at ~24 fps. Pairs with SFX_SpliceBlink.')
    return frames


# ---------------------------------------------------------------- ground ring, markers, prompts (white, tintable)
def warn_ring():
    """1024 px. Replaces the engine cylinder under the cleaver boss. A film countdown leader seen from above:
    two thin rings, a broad dashed band between them, and four long cross ticks. White: tint it in the material."""
    S = 1024 * 2
    x, y = grid(S)
    r = np.hypot(x, y)
    ang = np.arctan2(y, x)
    c = new(S)
    band = (r > 0.80) & (r < 0.90) & (((ang / (2 * math.pi) * 24) % 1.0) < 0.62)
    rings = (np.abs(r - 0.96) < 0.012) | (np.abs(r - 0.74) < 0.008)
    ticks = ((np.abs(x) < 0.008) | (np.abs(y) < 0.008)) & (r > 0.60) & (r < 0.99)
    fill = r < 0.74
    layer(c, fill, (255, 255, 255), alpha=0.10)
    layer(c, band | rings | ticks, (255, 255, 255))
    single('T_FX_WarnRing', shrink(c, (1024, 1024)), what="The cleaver boss's attack area on the ground (FreezeRing)",
           notes='White on alpha, 10% fill inside. Unlit translucent on a flat plane or decal just above the '
                 'ground, tinted with the warning colour; rotate it slowly so the dashes move.')


def scene_marker():
    """512 px. Replaces the engine sphere on BP_SceneMarker: a film-slate diamond with a hollow centre and four
    corner brackets - 'your mark is here'. White: tint it per marker."""
    S = 512 * SS
    x, y = grid(S)
    c = new(S)
    d = np.abs(x) + np.abs(y)
    diamond = (d < 0.62) & (d > 0.46)
    dot = d < 0.14
    ax, ay = np.abs(x), np.abs(y)
    br = (((ax > 0.66) & (ax < 0.92) & (ay > 0.84) & (ay < 0.92)) | ((ay > 0.66) & (ay < 0.92) & (ax > 0.84) & (ax < 0.92)))
    body = diamond | dot | br
    layer(c, dilate(body, SS * 3) & ~body, OUTLINE)
    layer(c, body, (255, 255, 255))
    single('T_FX_SceneMarker', shrink(c, (512, 512)), what='BP_SceneMarker GiftMesh (five visible spheres on the route)',
           notes='White with a dark rim. A camera-facing quad ~60 cm, tinted, bobbing; or hide the marker entirely '
                 'where it only exists for the script.')


def prompt_ring():
    """512 px, 8 frames 4 x 2. The 'you can press the key here' prompt over the driver and the coworker
    (TouchPrompt, RescuePrompt): a ring that closes in on a solid disc, like a shutter. It has NO letter on it -
    the key name is a TextRender or widget on top, so rebinding never needs new art."""
    S = 256 * SS
    x, y = grid(S)
    r = np.hypot(x, y)
    ang = np.arctan2(y, x)
    frames = []
    for i in range(8):
        t = i / 8.0
        c = new(S)
        disc = r < 0.46
        outer = 0.92 - 0.26 * t
        ring = (np.abs(r - outer) < 0.045) & (((ang / (2 * math.pi) * 4 + 0.125) % 1.0) < 0.80)
        body = disc | ring
        layer(c, dilate(body, SS * 2) & ~body, OUTLINE)
        layer(c, ring, (255, 255, 255), alpha=1.0 - 0.6 * t)
        layer(c, disc, (255, 255, 255))
        layer(c, (r < 0.46) & (r > 0.39), OUTLINE)
        frames.append(shrink(c, (256, 256)))
    sheet('T_FX_Prompt_4x2', frames, 4, what='Interaction prompt over the crash driver (F) and the coworker (rescue)',
          notes='8 frames of 256. White disc with a dark inner rim and a closing ring; loop at 8 fps, tint with '
                'the power colour, put the key letter on the disc with a TextRender (dark text). Replaces the '
                'blue and cyan engine spheres.')
    return frames


def telegraph():
    """256 px, 8 frames 4 x 2. The enemy attack telegraph (WarnSign, the orange sphere over every enemy's head):
    a spiked burst with an exclamation shape cut from geometry (a tall wedge and a square dot, no typeface),
    that pops in over four frames and holds with a pulse. Orange-red baked in: it is a warning, never tinted."""
    S = 256 * SS
    x, y = grid(S)
    r = np.hypot(x, y)
    ang = np.arctan2(y, x)
    frames = []
    for i in range(8):
        t = (i + 1) / 8.0                                         # frame 0 is already visible
        pop = ease_out(min(1.0, t / 0.4), 3.0) * (1.0 + 0.06 * math.sin(t * math.pi * 4))
        c = new(S)
        spikes = 0.74 + 0.20 * np.abs(np.cos(ang * 6 + 0.4))
        burst = r < spikes * pop
        layer(c, dilate(burst, SS * 3) & ~burst, OUTLINE)
        layer(c, burst, (255, 96, 40))
        layer(c, r < spikes * pop * 0.80, (255, 196, 60))
        xs_, ys_ = x / max(pop, 1e-3), y / max(pop, 1e-3)
        wedge = (ys_ > -0.50) & (ys_ < 0.16) & (np.abs(xs_) < 0.05 + 0.10 * (0.16 - ys_) / 0.66)
        dot = (np.abs(xs_) < 0.085) & (ys_ > 0.26) & (ys_ < 0.43)
        layer(c, wedge | dot, OUTLINE)
        frames.append(shrink(c, (256, 256)))
    sheet('T_FX_Telegraph_4x2', frames, 4, what="Enemy attack telegraph (BP_EnemyBase WarnSign, the sphere over each head)",
          notes='8 frames of 256. Frames 0-3 pop in, 4-7 hold with a pulse; play once at 20 fps and hold the last '
                'frame through the windup. Camera-facing quad ~55 cm above the head. Colour is baked in.')
    return frames


# ---------------------------------------------------------------- HUD power icons
def _icon_base(S, colour):
    x, y = grid(S)
    c = new(S)
    r = np.maximum(np.abs(x), np.abs(y))
    corner = np.hypot(np.maximum(np.abs(x) - 0.62, 0), np.maximum(np.abs(y) - 0.62, 0))
    tile = (r < 0.92) & (corner < 0.30)
    inner = (r < 0.84) & (np.hypot(np.maximum(np.abs(x) - 0.60, 0), np.maximum(np.abs(y) - 0.60, 0)) < 0.24)
    layer(c, tile, OUTLINE)
    layer(c, inner, tuple(int(v * 0.30) for v in colour))
    layer(c, inner & (y < -0.05 - 0.25 * x), tuple(int(v * 0.42) for v in colour))   # one hard cel highlight band
    return c, x, y


def icons():
    """Three 256 px HUD icons, one per power, drawn from shapes so they stay sharp at 64 px.
    Freeze Frame: a pause mark inside a film frame. Splice: a strip of film cut on the diagonal, the halves
    offset. Rewind: two left-pointing triangles."""
    S = 256 * SS
    # Freeze Frame
    c, x, y = _icon_base(S, CYAN)
    ax, ay = np.abs(x), np.abs(y)
    frame = ((ax < 0.62) & (ay < 0.50)) & ~((ax < 0.52) & (ay < 0.40))
    bars = (ax > 0.10) & (ax < 0.28) & (ay < 0.27)
    layer(c, frame, CYAN)
    layer(c, bars, (255, 255, 255))
    single('T_Icon_FreezeFrame', shrink(c, (256, 256)), folder=UI, what='WBP_HUD FreezeBox icon (E)',
           notes='256 px, readable at 64. Pale cyan on a dark tile.')
    # Splice
    c, x, y = _icon_base(S, VIOLET)
    cut = (x + y * 0.55)                                   # the diagonal cut
    off = np.where(cut < 0, -0.13, 0.13)                   # the two halves slide apart along y
    yy = y - off
    strip = (np.abs(yy) < 0.30) & (np.abs(x) < 0.70) & (np.abs(cut) > 0.07)
    holes = (np.abs(np.abs(yy) - 0.22) < 0.04) & (((x * 4.5) % 1.0) < 0.5) & (np.abs(x) < 0.66)
    layer(c, strip, VIOLET)
    layer(c, strip & (np.abs(yy) < 0.15), VIOLET_PALE)
    layer(c, strip & holes, OUTLINE)
    layer(c, (np.abs(cut) < 0.022) & (np.abs(y) < 0.60), (255, 255, 255))
    single('T_Icon_Splice', shrink(c, (256, 256)), folder=UI, what='WBP_HUD SpliceBox icon (Left Shift)',
           notes='256 px. Violet film strip cut on the diagonal.')
    # Rewind
    c, x, y = _icon_base(S, AMBER)
    tri = np.zeros_like(x, dtype=bool)
    for ox in (-0.02, 0.42):
        xx = x - ox
        tri |= (xx > -0.42) & (xx < 0.0) & (np.abs(y) < (xx + 0.42) * 0.85)
    layer(c, tri, AMBER)
    layer(c, tri & (y < 0), (255, 232, 170))
    single('T_Icon_Rewind', shrink(c, (256, 256)), folder=UI, what='WBP_HUD RewindBox icon (Q)',
           notes='256 px. Amber double triangle pointing left. Rewind is parked for the demo; the icon is here so '
                 'the three boxes match if it comes back.')


# ---------------------------------------------------------------- check sheets
def check(name, frames_or_im, cols):
    """Frames laid on a mid-grey and a dark card side by side, so edges and outlines can be judged by eye."""
    out = os.path.join(FX, '_check')
    os.makedirs(out, exist_ok=True)
    src = Image.open(os.path.join(ROOT, manifest[name]['file']))
    w, h = src.size
    k = min(1.0, 1600.0 / (w * 2))
    card = Image.new('RGB', (w * 2, h), (120, 124, 132))
    card.paste(Image.new('RGB', (w, h), (26, 28, 40)), (w, 0))
    card.paste(src, (0, 0), src)
    card.paste(src, (w, 0), src)
    card = card.resize((int(w * 2 * k), int(h * k)), Image.LANCZOS)
    card.save(os.path.join(out, name + '.jpg'), quality=85)


def main():
    explosion()
    hit_flash()
    speed_lines()
    freeze_overlay()
    splice_trail()
    warn_ring()
    scene_marker()
    prompt_ring()
    telegraph()
    icons()
    with open(os.path.join(FX, 'fx_manifest.json'), 'w', newline='\n') as f:
        json.dump(manifest, f, indent=1)
    for name, m in manifest.items():
        print('%-28s %dx%d grid, %2d frames of %dx%d  (%s)' % (name, m['cols'], m['rows'], m['frames'],
                                                             m['frame_px'][0], m['frame_px'][1], m['file']))
    if '--check' in sys.argv:
        for name in manifest:
            check(name, None, manifest[name]['cols'])


if __name__ == '__main__':
    main()
