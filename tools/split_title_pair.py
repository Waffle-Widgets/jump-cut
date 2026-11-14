"""Cut the one-shot title picture down its centre into the two halves the title animation fades in.

THE POINT. docs/prompts.md UI-TITLE3 draws the barista and the director BACK TO BACK IN ONE PICTURE, on
purpose: two separately generated halves would disagree at the seam - different shoulder height, different
head height, different light - and no prompt wording fixes that. Drawn together and cut afterwards, the
seam is exact because both halves came off the same drawing.

WHAT IT WRITES. Two PNGs on the SAME canvas as the source, each holding only its own half and transparent
everywhere else, so the title widget can stack them at 0,0 and fade them in one at a time with no
positioning arithmetic and no rectangle of background appearing.

    python tools/split_title_pair.py SOURCE.png --out Art/UI
        -> T_UI_TitleBarista.png   left half  (fades in first)
        -> T_UI_TitleDirector.png  right half (fades in second)

THE BACKGROUND IS KEYED OUT, and that is not optional. A half faded in WITH its flat cream background is a
cream rectangle growing out of nothing - the seam becomes a visible vertical edge down the middle of the
screen for the whole first second. So the flat field is flood-filled away from the borders and only there:
cream reached from outside becomes transparent, anything enclosed by the figure stays opaque.

WHAT IT CHECKS, and why each one is a real failure it has seen or would not survive:
  * flat background   - the corners must agree, or the key will tear holes in the art
  * skin kept         - pale skin is close to the cream field, so the fill is seeded from the top and the two
                        sides only, never the bottom, which is where the figures leave the frame
  * a clean cut       - the centre column must be ALL figure (drawn back to back) or NONE (two figures with
                        a gap between them). Anything in between means one of them straddles the cut and will
                        lose a shoulder when it fades in - which is the one thing this whole approach exists
                        to prevent, so it is the check that matters most
  * heads level       - the two halves' top edges must agree, or the second fade visibly jumps
  * cropped at chest  - ink must reach the bottom edge, or it came back full length
  * nothing crossing  - neither half may have ink hard against its outer edge, which means a figure
                        overran the frame and will be cut off mid-shoulder
Exit 1 on a finding. It cannot tell you the picture is good; looking at it is still your job.
"""
import argparse, os, sys
import numpy as np
from PIL import Image

BG_TOL = 26          # per-channel distance that still counts as the flat background
SOFT = 38            # distance at which a pixel is fully opaque; between BG_TOL and this it ramps
LEVEL_TOL = 0.02     # head heights may differ by this fraction of image height


def key_background(rgb):
    """Alpha for the picture: flat field reached from the border becomes transparent, nothing else does."""
    h, w, _ = rgb.shape
    corners = np.concatenate([rgb[:8, :8].reshape(-1, 3), rgb[:8, -8:].reshape(-1, 3),
                              rgb[-8:, :8].reshape(-1, 3), rgb[-8:, -8:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    spread = float(np.max(np.abs(corners - bg)))
    dist = np.max(np.abs(rgb.astype(np.int16) - bg.astype(np.int16)), axis=2)

    near = dist <= BG_TOL                      # could be background by colour
    outside = np.zeros_like(near)              # ... and is actually reachable from the border
    # THE BOTTOM EDGE IS NOT A SEED, and this is not a detail. The figures are cropped at the chest, so the
    # bottom row is figure, not background. Seeding it let the fill walk up the inside of his bare forearms -
    # pale skin is within tolerance of the cream - and punched holes straight through both arms. Seeding only
    # the three edges the figures do not touch leaves skin enclosed by its own line art, where it belongs.
    outside[0, :] = near[0, :]
    outside[:, 0] = near[:, 0]; outside[:, -1] = near[:, -1]
    while True:                                # grow the border region until it stops growing
        grown = outside.copy()
        grown[1:, :] |= outside[:-1, :]; grown[:-1, :] |= outside[1:, :]
        grown[:, 1:] |= outside[:, :-1]; grown[:, :-1] |= outside[:, 1:]
        grown &= near
        if grown.sum() == outside.sum():
            break
        outside = grown

    alpha = np.full((h, w), 255, dtype=np.float32)
    ramp = np.clip((dist - BG_TOL) / float(SOFT - BG_TOL), 0.0, 1.0) * 255.0
    alpha[outside] = ramp[outside]             # soft only where we know it is outside the figure
    return alpha.astype(np.uint8), bg, spread


def ink_box(alpha, x0, x1):
    col = alpha[:, x0:x1]
    rows = np.where(col.max(axis=1) > 40)[0]
    cols = np.where(col.max(axis=0) > 40)[0]
    if not len(rows) or not len(cols):
        return None
    return int(cols[0]) + x0, int(rows[0]), int(cols[-1]) + x0, int(rows[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--out', default='Art/UI')
    ap.add_argument('--left-name', default='T_UI_TitleBarista.png')
    ap.add_argument('--right-name', default='T_UI_TitleDirector.png')
    ap.add_argument('--seam', type=int, default=None, help='x of the cut; default the exact centre')
    ap.add_argument('--erase-seam', type=int, default=0, metavar='N',
                    help='fill N columns centred on the cut with the background first. Gemini draws a thin '
                         'vertical divider line between the two panels; left in, half of it fades in with each '
                         'half and reads as a stray line down the screen')
    ap.add_argument('--force', action='store_true', help='write the halves even if a check fails')
    a = ap.parse_args()

    im = Image.open(a.source).convert('RGB')
    w, h = im.size
    seam = a.seam if a.seam is not None else w // 2
    rgb = np.asarray(im)
    alpha, bg, spread = key_background(rgb)
    seam_note = ''

    bad = []
    print('source     : %s  %dx%d' % (a.source, w, h))
    print('background : rgb(%d,%d,%d), corners agree to %d' % (bg[0], bg[1], bg[2], spread))
    if spread > BG_TOL:
        bad.append('background is not flat - corners differ by %d (limit %d); the key will tear' % (spread, BG_TOL))

    if a.erase_seam:
        half = a.erase_seam // 2
        x0, x1 = seam - half, seam - half + a.erase_seam
        rgb = rgb.copy(); rgb[:, x0:x1] = bg.astype(np.uint8)
        alpha, bg, spread = key_background(rgb)
        print('erased     : x %d..%d filled with the background - the divider line Gemini draws between panels'
              % (x0, x1 - 1))

    touch = float((alpha[:, seam] > 40).sum()) / h
    kind = 'back to back' if touch > 0.9 else ('a clean gap' if touch < 0.05 else 'STRADDLED')
    print('seam x=%-5d: %.0f%% of the centre column is figure - %s' % (seam, touch * 100, kind))
    if kind == 'STRADDLED':
        bad.append('the centre column is %.0f%% figure - somebody straddles the cut and will lose a shoulder'
                   % (touch * 100))

    lb, rb = ink_box(alpha, 0, seam), ink_box(alpha, seam, w)
    if not lb or not rb:
        print('one half has no figure in it at all'); return 2
    print('left  half : x %d..%d, top %d, bottom %d' % (lb[0], lb[2], lb[1], lb[3]))
    print('right half : x %d..%d, top %d, bottom %d' % (rb[0], rb[2], rb[1], rb[3]))

    drop = abs(lb[1] - rb[1]) / float(h)
    print('heads      : tops differ by %d px (%.1f%% of height, limit %.1f%%)' % (abs(lb[1]-rb[1]), drop*100, LEVEL_TOL*100))
    if drop > LEVEL_TOL:
        bad.append('the two heads are %d px apart vertically - the second fade will visibly jump' % abs(lb[1]-rb[1]))

    for name, b in (('left', lb), ('right', rb)):
        if b[3] < h - 4:
            bad.append('%s figure stops %d px above the bottom edge - it is not cropped at the chest' % (name, h - b[3]))
    if lb[0] <= 2:
        bad.append('the left figure touches the left edge - it will be cut off mid-shoulder')
    if rb[2] >= w - 3:
        bad.append('the right figure touches the right edge - it will be cut off mid-shoulder')

    for line in bad:
        print('  FAIL  ' + line)
    if bad and not a.force:
        print('\n%d finding(s); nothing written. Pass --force to write anyway.' % len(bad))
        return 1

    os.makedirs(a.out, exist_ok=True)
    rgba = np.dstack([rgb, alpha])
    for name, x0, x1 in ((a.left_name, 0, seam), (a.right_name, seam, w)):
        half = rgba.copy()
        half[:, :x0, 3] = 0
        half[:, x1:, 3] = 0
        p = os.path.join(a.out, name)
        Image.fromarray(half, 'RGBA').save(p)
        print('wrote %s  %dx%d, holding x %d..%d' % (p, w, h, x0, x1))
    print('\nBoth are the full %dx%d canvas, so the widget stacks them at 0,0.' % (w, h))
    return 0


if __name__ == '__main__':
    sys.exit(main())
