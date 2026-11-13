"""Check that every character model's colours land where they are meant to.

The failure this exists to catch: image-to-3D bakes one texture for the whole
body, and nothing in the pipeline knows that a pixel is "hair" or "sleeve". So a
model can come back with skin-coloured hair, or a shirt the same colour as the
arm inside it, and every status line still reads green. The contact sheet in
meshy_character.py will not show it either - it is lit, small, and grey.

What it does, per model:
  1. renders the baked base colour UNLIT, front and back (Art/Blender/color_audit_render.py)
  2. takes the skin colour from the middle of the face
  3. paints every pixel within dE76 < 14 of that colour:
       GREEN where skin belongs (the head, and a disc around each hand)
       RED   anywhere else  <- the defect
  4. samples named zones (hair / face / chest / waist / thigh / shin / hands / feet)
     and reports hex and HSV for each.

Run:  python tools/color_audit.py [--only Name]
Writes Art/Refs/gen/audit/ (ignored) and docs/media/COLOUR-AUDIT.jpg.
"""
import os, re, sys, json, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'Art', 'Refs', 'gen', 'audit')
RENDER = os.path.join(ROOT, 'Art', 'Blender', 'color_audit_render.py')
SHEET = os.path.join(ROOT, 'docs', 'media', 'COLOUR-AUDIT.jpg')
BLENDER = os.environ.get('BLENDER', 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe')
SKIN_DE = 14.0          # below this, two colours read as the same colour to a player


def lab(a):
    c = np.asarray(a, float) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], -1)


def hexs(c):
    return '#%02X%02X%02X' % tuple(int(round(v)) for v in c)


def hsv(c):
    r, g, b = [x / 255.0 for x in c]
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        h = 0.0
    elif mx == r:
        h = (60 * ((g - b) / d)) % 360
    elif mx == g:
        h = 60 * ((b - r) / d) + 120
    else:
        h = 60 * ((r - g) / d) + 240
    return [round(h, 1), round(0 if mx == 0 else d / mx, 3), round(mx, 3)]


def find_models():
    out = []
    for fbx in sorted(glob.glob(os.path.join(ROOT, 'Art/Blender/export/Characters/*/SK_*.fbx'))):
        tex = glob.glob(os.path.join(os.path.dirname(fbx), 'T_*_BaseColor.png'))
        if tex:
            out.append((os.path.basename(fbx)[3:-4], fbx, tex[0], True))
    for fbx in sorted(glob.glob(os.path.join(ROOT, 'Art/Meshy/*/SM_*.fbx'))):
        tex = glob.glob(os.path.join(os.path.dirname(fbx), 'T_*.png'))
        if tex:
            out.append((os.path.basename(fbx)[3:-4], fbx, tex[0], False))
    return out


def render(name, fbx, tex):
    r = subprocess.run([BLENDER, '-b', '-P', RENDER, '--', fbx, tex, name, OUT],
                       capture_output=True, text=True)
    m = re.search(r'FLATRENDER_JSON (.*)', r.stdout)
    if not m:
        raise SystemExit('render failed for %s\n%s' % (name, r.stdout[-2000:] + r.stderr[-2000:]))
    return json.loads(m.group(1))


def analyse(name, meta, is_char):
    res = {'name': name, 'bones': meta['bones'], 'zones': {}, 'flags': []}
    tiles = []
    for view in ('front', 'back'):
        im = Image.open(os.path.join(OUT, '%s_%s_flat.png' % (name, view))).convert('RGBA')
        a = np.asarray(im).astype(float)
        rgb, op = a[..., :3], a[..., 3] > 128
        ys = np.where(op.any(axis=1))[0]
        y0, y1 = int(ys.min()), int(ys.max())
        h = y1 - y0
        yy, xx = np.ogrid[:op.shape[0], :op.shape[1]]

        def band(t0, t1):
            m = np.zeros_like(op)
            m[int(y0 + t0 * h):int(y0 + t1 * h), :] = True
            return m & op

        def mid(m, frac):
            cols = np.where(m.any(axis=0))[0]
            if not len(cols):
                return m
            c = (cols.min() + cols.max()) / 2
            half = (cols.max() - cols.min()) * frac / 2
            keep = np.zeros_like(m)
            keep[:, int(c - half):int(c + half) + 1] = True
            return m & keep

        def disc(px, py, r):
            return op & (((xx - px) ** 2 + (yy - py) ** 2) <= r * r)

        if is_char:
            zones = {'hair_top': band(0.015, 0.055), 'face': mid(band(0.115, 0.155), 0.30),
                     'chest': mid(band(0.26, 0.33), 0.28), 'waist': mid(band(0.43, 0.50), 0.28),
                     'thigh': band(0.62, 0.70), 'shin': band(0.80, 0.87)}
            mk = meta['views'][view]
            for k in ('hand_l', 'hand_r'):
                for m_ in mk.get(k, []):
                    zones[k] = disc(m_['px'], m_['py'], 11)
            if mk.get('feet'):
                fm = np.zeros_like(op)
                for m_ in mk['feet']:
                    fm |= disc(m_['px'], m_['py'] - 14, 13)
                zones['foot'] = fm
        else:
            warm = op & (rgb[..., 0] > rgb[..., 2] + 18)
            zones = {'warm_part': warm, 'cool_part': op & ~warm}

        for zn, m in zones.items():
            if int(m.sum()) < 40:
                continue
            col = np.median(rgb[m], axis=0)
            res['zones'].setdefault(zn, {})[view] = {'hex': hexs(col), 'hsv': hsv(col),
                                                     'px': int(m.sum())}
        if not is_char:
            tiles.append(im)
            continue

        if view == 'front':
            res['skin_ref'] = hexs(np.median(rgb[mid(band(0.115, 0.155), 0.30)], axis=0))
        skin = np.array([int(res['skin_ref'][i:i + 2], 16) for i in (1, 3, 5)], float)
        d = np.linalg.norm(lab(rgb) - lab(skin.reshape(1, 1, 3))[0, 0], axis=-1)
        skinpx = op & (d < SKIN_DE)
        allowed = np.zeros_like(op)
        allowed[:int(y0 + 0.20 * h), :] = True
        for k in ('hand_l', 'hand_r'):
            for m_ in meta['views'][view].get(k, []):
                allowed |= ((xx - m_['px']) ** 2 + (yy - m_['py']) ** 2) <= 150 ** 2
        leak = skinpx & ~allowed
        pct = round(100.0 * int(leak.sum()) / max(int(op.sum()), 1), 2)
        res.setdefault('skin_leak_pct', {})[view] = pct
        if pct >= 1.0:
            res['flags'].append('%s: %.2f%% of the body is within dE %g of the face skin tone '
                                'and is neither head nor hand' % (view, pct, SKIN_DE))
        base = (rgb * 0.35 + 255 * 0.25).astype(np.uint8)
        o = np.dstack([base, (op * 255).astype(np.uint8)])
        o[skinpx & allowed] = [60, 200, 90, 255]
        o[leak] = [255, 0, 0, 255]
        tiles += [im, Image.fromarray(o, 'RGBA')]
    return res, tiles


def main():
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    rows, report = [], []
    for name, fbx, tex, is_char in find_models():
        if only and only != name:
            continue
        print('rendering', name, flush=True)
        meta = render(name, fbx, tex)
        res, tiles = analyse(name, meta, is_char)
        report.append(res)
        rows.append((res, tiles))
    if not rows:
        raise SystemExit('no models found')
    TW, TH = 300, 400
    cols = max(len(t) for _, t in rows)
    sheet = Image.new('RGB', (TW * cols + 20, (TH + 34) * len(rows) + 10), (250, 250, 250))
    d = ImageDraw.Draw(sheet)
    for i, (res, tiles) in enumerate(rows):
        y = i * (TH + 34) + 28
        leak = res.get('skin_leak_pct', {})
        d.text((10, y - 18), '%s   skin %s   skin-colour outside head/hands: front %s%%  back %s%%   %s' % (
            res['name'], res.get('skin_ref', '-'), leak.get('front', '-'), leak.get('back', '-'),
            'FLAG' if res['flags'] else 'ok'), fill=(170, 0, 0) if res['flags'] else (0, 0, 0))
        for j, t in enumerate(tiles):
            t = t.copy()
            t.thumbnail((TW, TH))
            bg = Image.new('RGBA', (TW, TH), (255, 255, 255, 255))
            bg.alpha_composite(t, ((TW - t.width) // 2, (TH - t.height) // 2))
            sheet.paste(bg.convert('RGB'), (10 + j * TW, y))
    sheet.save(SHEET, quality=92)
    json.dump(report, open(os.path.join(OUT, 'colour-audit.json'), 'w'), indent=1)
    print('\n' + json.dumps(report, indent=1))
    print('\nsheet ->', SHEET)
    bad = [r['name'] for r in report if r['flags']]
    print('FLAGGED:', ', '.join(bad) if bad else 'none')


if __name__ == '__main__':
    main()
