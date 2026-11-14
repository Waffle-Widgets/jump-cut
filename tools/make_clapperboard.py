"""Draw the title animation's clapperboard, in code, with transparency.

WHY THIS IS NOT GENERATED. The title animation (docs/prompts.md UI-TITLE3) fades a clapperboard in over the
two figures and then snaps it. Three things make that a drawing job and not a prompt job:

  1. THE SLATE MUST BE BLANK. docs/character-locks.json has an invariant for it and docs/RULES.md 15d bans
     trademarks, so no lettering of any kind. A blank white panel is the single thing an image model cannot
     be talked out of filling in - every take wrote on it, the same way the car grille kept growing a badge.
  2. IT NEEDS REAL ALPHA. It sits on top of the characters, so the background has to be absent, not white.
  3. THE SNAP NEEDS TWO FRAMES THAT REGISTER EXACTLY. Open and shut are the same board with the clapper bar
     hinged at one point. Drawn twice by a model they would not share a hinge, and the snap would jump.

    python tools/make_clapperboard.py                 # writes both PNGs to Art/UI/
    python tools/make_clapperboard.py --out somewhere  # elsewhere

Output, 900x900 RGBA, same canvas for both so UMG can swap one for the other in place without moving it:
    T_UI_Clapper_Open.png   bar raised 20 degrees about the hinge - fades in like this
    T_UI_Clapper_Shut.png   bar down flush on the slate - swapped in on the snap
"""
import argparse, os
from PIL import Image, ImageDraw

SS = 4                      # supersample, then downscale once for clean edges
W = H = 900
SLATE = (100, 380, 800, 860)  # left, top, right, bottom
BAR_H = 110
HINGE = (100, 380)          # the clapper bar pivots here, in both frames
OPEN_DEG = 20.0
INK = (26, 26, 26, 255)     # the line art's dark, matching the cel-shade look
BODY = (34, 34, 36, 255)    # the board's black plastic
WHITE = (250, 250, 248, 255)
OUTLINE = 5
TEETH = 8                   # stripes along the clapper bar


def _layer():
    return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))


def _s(*v):
    return tuple(int(round(x * SS)) for x in v)


def slate_layer():
    """The white panel and the board's dark lower lip. Nothing is written on it, ever."""
    im = _layer(); d = ImageDraw.Draw(im)
    l, t, r, b = SLATE
    d.rectangle(_s(l, t, r, b), fill=WHITE, outline=INK, width=OUTLINE * SS)
    # the dark lip along the bottom, which is what makes it read as a board and not a sheet of paper
    d.rectangle(_s(l, b - 70, r, b), fill=BODY, outline=INK, width=OUTLINE * SS)
    return im


def bar_layer(angle):
    """The striped clapper bar, drawn flush and then rotated about the hinge."""
    im = _layer(); d = ImageDraw.Draw(im)
    l, t, r = SLATE[0], SLATE[1], SLATE[2]
    top = t - BAR_H
    d.rectangle(_s(l, top, r, t), fill=BODY, outline=INK, width=OUTLINE * SS)
    # white teeth: slanted so the bar reads as a clapper rather than a barcode
    step = (r - l) / float(TEETH)
    slant = step * 0.42
    for i in range(TEETH):
        if i % 2:
            continue
        x0 = l + i * step
        pts = [(x0 + slant, top), (x0 + step + slant, top), (x0 + step, t), (x0, t)]
        pts = [(max(l, min(r, x)), y) for x, y in pts]
        d.polygon([_s(*p) for p in pts], fill=WHITE)
    d.rectangle(_s(l, top, r, t), outline=INK, width=OUTLINE * SS)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, center=_s(*HINGE))
    return im


def board(angle):
    im = slate_layer()
    im.alpha_composite(bar_layer(angle))
    return im.resize((W, H), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Art', 'UI'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for name, deg in (('T_UI_Clapper_Open.png', OPEN_DEG), ('T_UI_Clapper_Shut.png', 0.0)):
        p = os.path.join(a.out, name)
        board(deg).save(p)
        print('%s  %dx%d  rotated %.0f deg about %s' % (p, W, H, deg, HINGE))


if __name__ == '__main__':
    main()
