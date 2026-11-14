"""Promote a chosen take from Art/Refs/gen into Art/UI at the size the game imports.

    py -3 tools/promote_ui.py UI-TITLE-3 T_UI_Title
    py -3 tools/promote_ui.py UI-COVER-1 T_UI_Cover --size 1328x1056
    py -3 tools/promote_ui.py UI-TITLE-3 T_UI_Title --patch-out 404,616,40,48,76,10,8

Art/Refs/gen is gitignored, so a take only reaches the repo by being promoted. This existed
only as a hand step before; it is a script because the aspect ratio is a trap. Qwen draws the
16:9 prompts at 1664 x 928, which is 1.793:1, not 1.778:1. Resizing that straight to 1920x1080
squashes the picture by 0.8% - invisible on its own, but it is a different squash every time the
generator's size changes, and two screens in the same game squashed differently is exactly the
kind of drift docs/character-locks.json exists to stop. So: centre-crop to the target aspect
first, then resize. Nothing is stretched.

--patch-out removes a small unwanted thing from our own picture by copying the neighbouring pixels
over it: give it cx,cy,rx,ry,dx,dy,feather and it fills an ellipse at (cx,cy) with whatever sits
dx,dy away, blended over `feather` pixels. It exists because of section 15d. The model keeps drawing
a manufacturer-style emblem on the car's grille no matter how the prompt is worded - positive
description cut the rate but did not end it (1 of 3 clean, then 0 of 3) - and the title card has to
be badge-free, not probably-badge-free. Painting out a 40x48 px disc with the grille either side of
it is deterministic and takes a second; re-rolling the dice is neither. Any use of it must be written
into the PREJAM.md declaration row for that picture, with the exact numbers, because it is an edit to
a generated image and the entry has to say so.

The UI textures in Unreal are imported from Art/UI (see tools/unreal_import_ui_fx.py). Replacing
a file here does NOT update the .uasset - that is a builder step in the editor.
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, 'Art', 'Refs', 'gen')
UI = os.path.join(ROOT, 'Art', 'UI')

# The size each screen is imported at. 16:9 for anything that fills the screen; the itch.io
# cover is 630x500 by itch's own rule, drawn larger and scaled down on upload.
SIZES = {
    'T_UI_Title': (1920, 1080), 'T_UI_Win': (1920, 1080), 'T_UI_Lose': (1920, 1080),
    'T_UI_ToBeContinued': (1920, 1080), 'T_UI_Cover': (1328, 1056),
}


def patch_out(im, cx, cy, rx, ry, dx, dy, feather):
    """Fill an ellipse with the pixels dx,dy away from it, feathered at the edge."""
    donor = Image.new('RGB', im.size)
    donor.paste(im, (dx, dy))
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    return Image.composite(donor, im, m.filter(ImageFilter.GaussianBlur(feather)))


def promote(take, name, size, patch=None):
    src = os.path.join(GEN, take + '.png')
    if not os.path.exists(src):
        sys.exit('no such take: ' + src)
    im = Image.open(src).convert('RGB')
    if patch:
        im = patch_out(im, *patch)
        print('patched out an ellipse at (%d,%d) r=(%d,%d) from %+d,%+d, feather %d' % patch)
    w, h = im.size
    tw, th = size
    # centre-crop to the target aspect, then resize. Never stretch.
    want = tw / th
    have = w / h
    if have > want:
        nw = int(round(h * want)); box = ((w - nw) // 2, 0, (w - nw) // 2 + nw, h)
    else:
        nh = int(round(w / want)); box = (0, (h - nh) // 2, w, (h - nh) // 2 + nh)
    cropped = im.crop(box)
    out = cropped.resize((tw, th), Image.LANCZOS)
    dst = os.path.join(UI, name + '.png')
    out.save(dst)
    lost = (w - box[2] + box[0], h - box[3] + box[1])
    print('%s (%dx%d) -> %s (%dx%d), cropped %d x %d px to reach %.4f:1'
          % (take, w, h, name, tw, th, lost[0], lost[1], want))
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('take'); ap.add_argument('name')
    ap.add_argument('--size', help='WxH, if the name is not in the table')
    ap.add_argument('--patch-out', dest='patch',
                    help='cx,cy,rx,ry,dx,dy,feather - copy neighbouring pixels over an ellipse')
    a = ap.parse_args()
    patch = None
    if a.patch:
        try:
            patch = tuple(int(x) for x in a.patch.split(','))
        except ValueError:
            sys.exit('--patch-out wants seven integers: cx,cy,rx,ry,dx,dy,feather')
        if len(patch) != 7:
            sys.exit('--patch-out wants seven integers: cx,cy,rx,ry,dx,dy,feather')
    if a.size:
        size = tuple(int(x) for x in a.size.lower().split('x'))
    elif a.name in SIZES:
        size = SIZES[a.name]
    else:
        sys.exit('unknown screen %s - pass --size WxH. Known: %s' % (a.name, ', '.join(sorted(SIZES))))
    promote(a.take, a.name, size, patch)


if __name__ == '__main__':
    main()
