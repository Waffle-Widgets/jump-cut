"""Count the director's cyan POWER RINGS inside a region, and fail if the count is wrong.

Why this exists. The rings are the only thing in the title art that says "he has
collected every power" - `docs/RULES.md` 15d bans writing it in words, so the count IS
the message. The count is also the one detail an image model gets wrong silently: it
draws rings, they look right, and there is one too few. Nobody notices until the
picture is in the game. The Team Owner corrected three rings to four on Fri Nov 13 at
10:30 PM; this is what stops the next take quietly going back to three.

How it counts, and why it needs a region. Cyan is not only on the rings - the coat's
open edges, the standing collar and the rim light down his outer edge are all the same
colour, and on a 1024 px picture the collar's cyan sits about 20 px apart in y, which
is exactly the ring spacing. No colour test can tell those apart. So you give it the
box the ring stack is in (look at the picture once, read the numbers off), and inside
that box it counts ROWS that are mostly cyan and groups the consecutive ones. Each
group is one ring, because a ring is a band and a band is a run of rows.

    python tools/count_power_rings.py Art/UI/T_UI_TitlePair.png \
        --region 620,360,700,440 --expect 4 --dump /tmp/rings.png

Exit code is 1 when the count is wrong, so it can gate a commit. --dump writes a copy
with the region and every band it found drawn on, which is how you check the script
instead of trusting it.
"""
import argparse, sys
import numpy as np
from PIL import Image


def cyan_mask(rgb):
    """Pale cyan: green and blue both clearly above red, and the pixel is light."""
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    return (g - r > 18) & (b - r > 28) & (b > 120) & (g > 120)


def count_bands(mask, min_frac=0.22, merge_gap=2, min_rows=1):
    """Rows that are at least min_frac cyan, grouped into bands."""
    w = mask.shape[1]
    hot = [y for y in range(mask.shape[0]) if mask[y].sum() >= max(3, min_frac * w)]
    bands = []
    for y in hot:
        if bands and y - bands[-1][1] <= merge_gap + 1:
            bands[-1][1] = y
        else:
            bands.append([y, y])
    return [(a, b) for a, b in bands if b - a + 1 >= min_rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--region', required=True,
                    help='x0,y0,x1,y1 box around the ring stack only - not the whole figure')
    ap.add_argument('--expect', type=int, default=4)
    ap.add_argument('--min-frac', type=float, default=0.22,
                    help='a row counts as ring if this fraction of the region width is cyan')
    ap.add_argument('--merge-gap', type=int, default=2,
                    help='rows of anti-aliasing allowed inside one ring')
    ap.add_argument('--dump', help='write a copy with the region and the bands drawn on')
    a = ap.parse_args()

    x0, y0, x1, y1 = [int(v) for v in a.region.split(',')]
    im = Image.open(a.source).convert('RGB')
    rgb = np.asarray(im)
    h, w = rgb.shape[:2]
    if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
        print('region %s is outside the %dx%d picture' % (a.region, w, h))
        return 1
    m = cyan_mask(rgb[y0:y1, x0:x1])
    bands = count_bands(m, a.min_frac, a.merge_gap)

    print('%s  %dx%d  region %d,%d-%d,%d' % (a.source, w, h, x0, y0, x1, y1))
    for i, (a0, b0) in enumerate(bands, 1):
        print('  ring %d: rows %d-%d (%d px tall)' % (i, y0 + a0, y0 + b0, b0 - a0 + 1))
    print('rings found: %d   expected: %d' % (len(bands), a.expect))

    if a.dump:
        from PIL import ImageDraw
        d = im.copy()
        dr = ImageDraw.Draw(d)
        dr.rectangle([x0, y0, x1, y1], outline=(0, 160, 255), width=2)
        for a0, b0 in bands:
            dr.rectangle([x0 - 4, y0 + a0 - 1, x1 + 4, y0 + b0 + 1], outline=(255, 0, 0), width=2)
        d.save(a.dump)
        print('dump: %s' % a.dump)

    if len(bands) != a.expect:
        print('FAIL: %d cyan forearm rings, the lock says %d '
              '(docs/character-locks.json, CafeWalker invariants)' % (len(bands), a.expect))
        return 1
    print('ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
