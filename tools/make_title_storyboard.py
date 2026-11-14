"""Draw the title-screen animation's four beats as one sheet, from the real assets.

Why a script and not a one-off. The storyboard is how the Team Owner sees the animation
before anyone builds it, so it has to show the CURRENT art - not a picture of what the
art was two takes ago. Every time the title pair is redrawn the sheet has to be redrawn
with it, and a sheet drawn by hand quietly goes stale. This draws it from
`Art/UI/T_UI_Title*.png` every time, so it cannot disagree with what is committed.

    python tools/make_title_storyboard.py docs/media/<date>-title-animation-storyboard.jpg

The four beats are the animation in `docs/ticket #64`: the barista half fades in (half a
man), the director half completes him, the clapperboard fades in over both, and the snap
wipes through to the level behind.
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont

UI = 'Art/UI'
CAPTIONS = [
    '1  the barista half fades in - half a man',
    '2  the director half fades in - he is whole, split down the centre',
    '3  the clapperboard fades in over him',
    '4  SNAP - the crack plays, and the shut board wipes through to the level',
]


def load(name):
    p = os.path.join(UI, name)
    if not os.path.exists(p):
        sys.exit('missing %s - run tools/split_title_pair.py first' % p)
    return Image.open(p).convert('RGBA')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--bg', default=None, help='background colour as R,G,B; default read from the pair')
    a = ap.parse_args()

    pair = load('T_UI_TitlePair.png')
    bar, dire = load('T_UI_TitleBarista.png'), load('T_UI_TitleDirector.png')
    open_b, shut_b = load('T_UI_Clapper_Open.png'), load('T_UI_Clapper_Shut.png')
    w, h = pair.size
    bg = tuple(int(v) for v in a.bg.split(',')) if a.bg else pair.convert('RGB').getpixel((4, 4))
    print('background: rgb%s  #%02X%02X%02X' % (bg, bg[0], bg[1], bg[2]))

    def frame(layers, dim=None):
        base = Image.new('RGBA', (w, h), bg + (255,))
        if dim:
            base = Image.new('RGBA', (w, h), dim + (255,))
        for im, alpha in layers:
            if alpha < 1.0:
                im = im.copy()
                im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
            base.alpha_composite(im)
        return base.convert('RGB')

    board = open_b.resize((int(h * 0.62), int(h * 0.62)))
    bx, by = (w - board.size[0]) // 2, int(h * 0.30)
    b3 = Image.new('RGBA', (w, h), (0, 0, 0, 0)); b3.alpha_composite(board, (bx, by))
    shut = shut_b.resize((int(h * 0.70), int(h * 0.70)))
    sx, sy = (w - shut.size[0]) // 2, int(h * 0.28)
    b4 = Image.new('RGBA', (w, h), (0, 0, 0, 0)); b4.alpha_composite(shut, (sx, sy))

    frames = [
        frame([(bar, 1.0)]),
        frame([(bar, 1.0), (dire, 1.0)]),
        frame([(bar, 1.0), (dire, 1.0), (b3, 0.55)]),
        frame([(bar, 1.0), (dire, 1.0), (b4, 1.0)], dim=(203, 198, 182)),
    ]

    pad, bar_h = 12, 26
    sheet = Image.new('RGB', (w * 2 + pad, (h + bar_h) * 2 + pad), (255, 255, 255))
    try:
        font = ImageFont.truetype('seguisb.ttf', 15)
    except OSError:
        font = ImageFont.load_default()
    for i, f in enumerate(frames):
        cx, cy = (i % 2) * (w + pad), (i // 2) * (h + bar_h + pad)
        sheet.paste(f, (cx, cy))
        d = ImageDraw.Draw(sheet)
        d.rectangle([cx, cy + h, cx + w, cy + h + bar_h], fill=(26, 26, 26))
        d.text((cx + 8, cy + h + 5), CAPTIONS[i], font=font, fill=(255, 255, 255))
    sheet.save(a.out, quality=92)
    print('wrote %s  %dx%d' % (a.out, sheet.size[0], sheet.size[1]))


if __name__ == '__main__':
    main()
