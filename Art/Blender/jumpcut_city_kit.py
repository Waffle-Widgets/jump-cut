"""Jump Cut city kit: the coffee shop, the city it stands in, and the clutter that makes it look lived in.

Headless (nothing to click):
    blender -b --factory-startup --python Art/Blender/jumpcut_city_kit.py -- build
    blender -b --factory-startup --python Art/Blender/jumpcut_city_kit.py -- build sheets

Writes one FBX per model to Art/Blender/export/City/ and check renders to Art/Blender/cache/city_*.png.

WHY IT IS GEOMETRY AND NOT MESHY. Meshy is image-to-3D: the right tool for a character, where one believable
silhouette matters and nobody walks along the inside of it. A city is the opposite job. The player walks down it,
so what matters is that walls are flat and vertical, floors are at z=0, doorways are the width the character
capsule actually needs, and one facade can repeat fifteen times without reading as a repeat. Those are numbers,
not pictures, so the city is built from numbers. It also costs 0 credits and re-runs in seconds when a size turns
out wrong, which is the thing that actually happens on a jam.

UNITS AND AXES. The scene is metres (Blender 1 unit = 1 m); the FBX export writes centimetres via
apply_unit_scale, so Unreal reads plain cm. Every model stands on the ground at its own origin (z = 0). Buildings
are centred on x and sit with their FACADE on y = 0 facing -Y, so a street line is a single y value to snap to.
Props are centred on x and y. Blender -Y is the game camera's forward, matching the other kits in this folder
(axis_forward='-Z', axis_up='Y').

NO TEXTURES, ON PURPOSE. The level wears a cel-shaded anime post-process (MI_AnimeLook_JumpCut) that flattens
lighting into bands and draws an outline on every depth and normal edge. Under that, a photographic facade texture
is mostly thrown away and a flat colour is not, so this kit ships flat material slots (MS_City*) for the builder
to point at material instances, and puts its detail in GEOMETRY - recessed windows, mullions, sills, parapets,
fire escapes - where the outline pass can actually find it. The variety that would normally come from a texture is
baked into VERTEX COLOUR instead: every window pane gets its own brightness, so one material gives a facade of
lit and dark rooms.

NO TRADEMARKS (MegaJam section 15d). Every sign in this kit is a blank lit panel or an invented abstract glyph
block. No real shop name, no real logo, no readable brand, nothing traced off a photograph of a real street.
"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(REPO, 'Art', 'Blender', 'export', 'City')
CACHE = os.path.join(REPO, 'Art', 'Blender', 'cache')

# Material slot names. The builder makes one material instance per name; the cel shader does the rest.
# Keep this list short: every extra slot is another thing somebody has to hook up by hand in Unreal.
SLOTS = [
    'MS_CityWall',      # render / plaster, the default wall
    'MS_CityBrick',     # New York masonry
    'MS_CityConcrete',  # kerbs, slabs, raw structure
    'MS_CityTrim',      # dark painted metal: mullions, rails, frames
    'MS_CityMetal',     # bare galvanised metal: ducts, tanks, shutters
    'MS_CityGlass',     # windows and shopfronts
    'MS_CitySignA',     # emissive sign face, warm
    'MS_CitySignB',     # emissive sign face, cool
    'MS_CityAccent',    # painted accent: awnings, doors, vending fronts
    'MS_CityWood',      # cafe fittings, crates
    'MS_CityRoof',      # roof deck, felt
    'MS_CityCloth',     # awning canvas, noren, bin bags
]


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0


def material(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    return m


class B:
    """A small mesh builder: boxes, quads and tubes with a material slot, a vertex colour and real-scale UVs."""

    def __init__(self, seed=0):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new('UVMap')
        self.col = self.bm.loops.layers.color.new('Col')
        self.slots = []
        self.rng = random.Random(seed)

    def slot(self, name):
        if name not in self.slots:
            if name not in SLOTS:
                raise ValueError('unknown material slot: ' + name)
            self.slots.append(name)
        return self.slots.index(name)

    def _paint(self, f, c):
        if isinstance(c, (int, float)):
            rgba = (float(c), float(c), float(c), 1.0)
        else:
            rgba = (float(c[0]), float(c[1]), float(c[2]), 1.0)
        for lp in f.loops:
            lp[self.col] = rgba

    def quad(self, pts, slot, c=1.0):
        """pts: four corners in order round the face."""
        mi = self.slot(slot)
        vs = [self.bm.verts.new(Vector(p)) for p in pts]
        try:
            f = self.bm.faces.new(vs)
        except ValueError:
            return None
        f.material_index = mi
        f.smooth = False
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for lp in f.loops:                      # real-scale planar UVs, 1 unit = 1 m
            p = lp.vert.co
            if az >= ax and az >= ay:
                lp[self.uv].uv = (p.x, p.y)
            elif ax >= ay:
                lp[self.uv].uv = (p.y, p.z)
            else:
                lp[self.uv].uv = (p.x, p.z)
        self._paint(f, c)
        return f

    def box(self, p0, p1, slot, c=1.0, skip=()):
        """Axis-aligned cuboid from p0 to p1. skip: any of 'xlo','xhi','ylo','yhi','zlo','zhi'."""
        x0, y0, z0 = min(p0[0], p1[0]), min(p0[1], p1[1]), min(p0[2], p1[2])
        x1, y1, z1 = max(p0[0], p1[0]), max(p0[1], p1[1]), max(p0[2], p1[2])
        if 'ylo' not in skip:
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], slot, c)
        if 'yhi' not in skip:
            self.quad([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], slot, c)
        if 'xlo' not in skip:
            self.quad([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], slot, c)
        if 'xhi' not in skip:
            self.quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], slot, c)
        if 'zlo' not in skip:
            self.quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], slot, c)
        if 'zhi' not in skip:
            self.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], slot, c)

    def tube(self, p, h, r, slot, n=8, c=1.0, axis='z'):
        """A low-poly cylinder; p is the centre of its base."""
        mi = self.slot(slot)
        ring0, ring1 = [], []
        for i in range(n):
            a = 2 * math.pi * i / n
            dx, dy = math.cos(a) * r, math.sin(a) * r
            if axis == 'z':
                ring0.append(self.bm.verts.new((p[0] + dx, p[1] + dy, p[2])))
                ring1.append(self.bm.verts.new((p[0] + dx, p[1] + dy, p[2] + h)))
            elif axis == 'y':
                ring0.append(self.bm.verts.new((p[0] + dx, p[1], p[2] + dy)))
                ring1.append(self.bm.verts.new((p[0] + dx, p[1] + h, p[2] + dy)))
            else:
                ring0.append(self.bm.verts.new((p[0], p[1] + dx, p[2] + dy)))
                ring1.append(self.bm.verts.new((p[0] + h, p[1] + dx, p[2] + dy)))
        for i in range(n):
            j = (i + 1) % n
            try:
                f = self.bm.faces.new([ring0[i], ring0[j], ring1[j], ring1[i]])
            except ValueError:
                continue
            f.material_index = mi
            f.smooth = False
            for lp in f.loops:
                lp[self.uv].uv = (lp.vert.co.x + lp.vert.co.y, lp.vert.co.z)
            self._paint(f, c)
        for ring in (ring0, list(reversed(ring1))):
            try:
                f = self.bm.faces.new(ring)
            except ValueError:
                continue
            f.material_index = mi
            f.smooth = False
            for lp in f.loops:
                lp[self.uv].uv = (lp.vert.co.x, lp.vert.co.y)
            self._paint(f, c)

    def finish(self, name, weld=True):
        if weld:
            bmesh.ops.remove_doubles(self.bm, verts=list(self.bm.verts), dist=0.0008)
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old)
        o = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(o)
        for s in self.slots:
            o.data.materials.append(material(s))
        return o


# --------------------------------------------------------------------------- facade pieces
# A floor is 3.4 m: tall enough to read as a real storey under a 180 cm character, short enough that a 5-storey
# Tokyo pencil building still fits under the 8 m grey boxes' replacement height without dwarfing the street.
FH = 3.4


def punched_wall(b, x0, x1, y, z0, nfl, slot='MS_CityWall', mod=1.7, ww=0.95, wh=1.6, sill=0.95,
                 depth=0.18, c=0.95, lit=0.5, rng=None):
    """A wall of recessed windows on the y plane, facing -Y. Returns the top z.

    Each pane is its own quad with its own vertex-colour brightness, so one material can read a facade of lit
    and dark rooms off vertex colour alone - the thing a texture would normally do, done for free.
    """
    rng = rng or random.Random(7)
    w = x1 - x0
    n = max(1, int((w - 0.5) / mod))
    pad = (w - n * mod) / 2.0
    for fl in range(nfl):
        zb = z0 + fl * FH
        for i in range(n):
            cx = x0 + pad + mod * (i + 0.5)
            wx0, wx1 = cx - ww / 2, cx + ww / 2
            wz0, wz1 = zb + sill, zb + sill + wh
            # reveal: four thin walls going back into the building
            b.box((wx0, y, wz0), (wx1, y + depth, wz1), slot, c * 0.8, skip=('ylo', 'yhi'))
            # the pane itself, set back, brightness = whether the room is lit
            pane = 0.28 + 0.68 * rng.random() if rng.random() < lit else 0.1 + 0.08 * rng.random()
            b.quad([(wx0, y + depth, wz0), (wx1, y + depth, wz0), (wx1, y + depth, wz1), (wx0, y + depth, wz1)],
                   'MS_CityGlass', pane)
            # sill, sticking out
            b.box((wx0 - 0.07, y - 0.06, wz0 - 0.09), (wx1 + 0.07, y, wz0), 'MS_CityConcrete', 1.0)
        # The wall face, CUT ROUND the windows. Drawing one quad across the whole floor band instead would be
        # coplanar with the openings and bury every pane behind it - which is exactly what the first check
        # render caught: the windows were all there in the mesh and none of them were visible.
        wz0, wz1 = zb + sill, zb + sill + wh
        b.quad([(x0, y, zb), (x1, y, zb), (x1, y, wz0), (x0, y, wz0)], slot, c)              # below the sills
        b.quad([(x0, y, wz1), (x1, y, wz1), (x1, y, zb + FH), (x0, y, zb + FH)], slot, c)    # above the heads
        edges = [x0]
        for i in range(n):
            cx = x0 + pad + mod * (i + 0.5)
            edges += [cx - ww / 2, cx + ww / 2]
        edges.append(x1)
        for k in range(0, len(edges), 2):                                                    # the piers between
            px0, px1 = edges[k], edges[k + 1]
            if px1 - px0 > 0.004:
                b.quad([(px0, y, wz0), (px1, y, wz0), (px1, y, wz1), (px0, y, wz1)], slot, c)
    return z0 + nfl * FH


def shopfront(b, x0, x1, y, h=3.0, glass='MS_CityGlass', rng=None, door=True):
    """A ground-floor shop: full-height glazing in a dark frame, a stall riser, and a door gap."""
    rng = rng or random.Random(3)
    b.box((x0, y, 0), (x1, y + 0.12, 0.45), 'MS_CityConcrete', 1.0)          # stall riser
    bays = max(2, int((x1 - x0) / 1.5))
    step = (x1 - x0) / bays
    dbay = bays // 2 if door else -1
    for i in range(bays):
        bx0, bx1 = x0 + i * step, x0 + (i + 1) * step
        z0 = 0.0 if i == dbay else 0.45
        b.quad([(bx0 + 0.06, y + 0.1, z0), (bx1 - 0.06, y + 0.1, z0),
                (bx1 - 0.06, y + 0.1, h), (bx0 + 0.06, y + 0.1, h)],
               'MS_CityAccent' if i == dbay else glass, 0.22 if i == dbay else 0.55 + 0.3 * rng.random())
        b.box((bx0, y, z0), (bx0 + 0.06, y + 0.12, h), 'MS_CityTrim', 0.6)   # mullion
    b.box((x1 - 0.06, y, 0), (x1, y + 0.12, h), 'MS_CityTrim', 0.6)
    b.box((x0, y, h), (x1, y + 0.12, h + 0.3), 'MS_CityTrim', 0.5)           # fascia over the glazing


def parapet(b, x0, x1, y0, y1, z, h=0.95, t=0.22):
    """The low wall round a flat roof. It is what makes a roofline read as a building and not a cut-off box."""
    b.box((x0, y0, z), (x1, y0 + t, z + h), 'MS_CityConcrete', 1.0)
    b.box((x0, y1 - t, z), (x1, y1, z + h), 'MS_CityConcrete', 1.0)
    b.box((x0, y0, z), (x0 + t, y1, z + h), 'MS_CityConcrete', 1.0)
    b.box((x1 - t, y0, z), (x1, y1, z + h), 'MS_CityConcrete', 1.0)
    b.quad([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], 'MS_CityRoof', 0.8)


def band_sides(b, x0, x1, y0, y1, z0, nfl, fh=FH, slot='MS_CityConcrete', out=0.09, t=0.22):
    """A thin slab band right round the building at every floor level.

    Buildings in this kit carry their detail on the facade, because that is the face the lane sees. The first
    layout mock-up showed what that costs everywhere else: standing in the plaza, the backs and sides of the
    towers were featureless 46 m slabs. This is the cheap fix - a floor band on all four sides costs about
    50 triangles, catches the light, and gives the cel shader's outline pass an edge every 3.4 m, so a
    building reads as a building from any angle instead of as a box.
    """
    for fl in range(1, nfl + 1):
        z = z0 + fl * fh
        b.box((x0 - out, y0 - out, z - t), (x1 + out, y0, z), slot, 0.92)
        b.box((x0 - out, y1, z - t), (x1 + out, y1 + out, z), slot, 0.92)
        b.box((x0 - out, y0, z - t), (x0, y1, z), slot, 0.92)
        b.box((x1, y0, z - t), (x1 + out, y1, z), slot, 0.92)


def roof_clutter(b, x0, x1, y0, y1, z, rng, tank=False, n=3):
    """Ducts, housings and an optional New York timber water tank. The skyline's whole character is up here."""
    for _ in range(n):
        w = rng.uniform(0.7, 1.6)
        d = rng.uniform(0.6, 1.3)
        h = rng.uniform(0.5, 1.2)
        cx = rng.uniform(x0 + w, x1 - w)
        cy = rng.uniform(y0 + d, y1 - d)
        b.box((cx - w / 2, cy - d / 2, z), (cx + w / 2, cy + d / 2, z + h), 'MS_CityMetal', 0.85)
    if tank:
        cx, cy = (x0 + x1) / 2 + rng.uniform(-1, 1), (y0 + y1) / 2 + rng.uniform(-1, 1)
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.box((cx + sx * 1.0 - 0.09, cy + sy * 1.0 - 0.09, z),
                      (cx + sx * 1.0 + 0.09, cy + sy * 1.0 + 0.09, z + 2.0), 'MS_CityWood', 0.8)
        b.tube((cx, cy, z + 2.0), 2.6, 1.35, 'MS_CityWood', n=10, c=0.9)
        b.tube((cx, cy, z + 4.6), 0.75, 1.35, 'MS_CityMetal', n=10, c=0.8)   # conical-ish cap, read as a cap


# =========================================================================== THE COFFEE SHOP
# Sized off tools/c1_layout.py, so it drops onto the grey box it replaces with no re-measuring:
#   cafe interior x -6.30..6.30, y -5.15..5.15 (12.6 x 10.3 m), walls 4.0 m, door in the EAST wall
#   (x = 6.15, y -1.50..1.50). The car came through the WEST wall - its box spans x -7.20..-3.20, which
#   crosses the x = -6.15 wall line - so the hole in the west wall is where the car is, not a decoration.
# The floor top sits at z = +0.02, two centimetres above Floor_Base, so it reads as a tiled threshold
# instead of z-fighting the level floor it stands on.
CAFE_HW, CAFE_HD, CAFE_H = 6.30, 5.15, 4.00
WT = 0.15          # wall thickness
DOOR_HW, DOOR_H = 1.50, 2.40


def build_cafe_shell(name='SM_CafeShell'):
    """The whole cafe room as one mesh: floor, four walls, the door, the shopfront, the hole the car made,
    and a ceiling. Replaces five grey boxes (WallN, WallS, WallW, WallE_South, WallE_North)."""
    b = B(seed=11)
    rng = b.rng
    X, Y, H = CAFE_HW, CAFE_HD, CAFE_H
    b.box((-X - WT, -Y - WT, -0.12), (X + WT, Y + WT, 0.02), 'MS_CityConcrete', 0.92)      # floor slab
    # ---- north wall: a party wall, not a window.
    # The street only exists EAST of the cafe (the corridor runs x 630..6600); north of the cafe is the next
    # building in the row. Glazing here would look at a neighbour's brickwork one metre away. It gets a dado
    # and framed panels instead, so it is not a blank 12.6 m plane behind the seating.
    b.box((-X, Y - WT, 0), (X, Y, H), 'MS_CityWall', 1.0, skip=('ylo',))
    b.quad([(-X, Y - WT, 0), (X, Y - WT, 0), (X, Y - WT, H), (-X, Y - WT, H)], 'MS_CityWall', 0.95)
    b.box((-X, Y - WT - 0.04, 0.95), (X, Y - WT, 1.03), 'MS_CityWood', 0.8)             # dado rail
    for i in range(6):
        px = -X + 0.5 + i * (2 * X - 1.0) / 6
        b.box((px, Y - WT - 0.03, 1.25), (px + (2 * X - 1.0) / 6 - 0.35, Y - WT, 2.65), 'MS_CityWood', 0.7)
    # ---- south wall: solid, the service side. Shelving goes against it.
    b.box((-X, -Y, 0), (X, -Y + WT, H), 'MS_CityWall', 1.0)
    # ---- east wall: the shopfront. This is the cafe's street frontage and the wall the player spends beat 1
    # looking at, because he starts at (0,0) and walks east to the door at x = 6.15. Glazing it means he can
    # see the street he is about to walk into before he gets there.
    for py0, py1 in ((-Y, -DOOR_HW), (DOOR_HW, Y)):
        b.box((X - WT, py0, 0), (X, py1, 0.45), 'MS_CityConcrete', 1.0)                  # stall riser
        bays = max(2, int((py1 - py0) / 1.3))
        step = (py1 - py0) / bays
        for i in range(bays):
            by0, by1 = py0 + i * step, py0 + (i + 1) * step
            b.box((X - WT + 0.04, by0 + 0.05, 0.45), (X - WT + 0.1, by1 - 0.05, 2.90),
                  'MS_CityGlass', 0.5 + 0.3 * rng.random())
            b.box((X - WT, by0, 0.45), (X, by0 + 0.05, 2.90), 'MS_CityTrim', 0.6)        # mullion
        b.box((X - WT, py1 - 0.05, 0.45), (X, py1, 2.90), 'MS_CityTrim', 0.6)
        b.box((X - WT, py0, 2.90), (X, py1, H), 'MS_CityWall', 1.0)                      # wall over the glazing
        b.box((X - WT - 0.03, py0, 2.90), (X, py1, 3.14), 'MS_CityTrim', 0.5)            # fascia
    b.box((X - WT, -DOOR_HW, DOOR_H), (X, DOOR_HW, H), 'MS_CityWall', 1.0)               # lintel over the door
    b.box((X - WT, -DOOR_HW - 0.06, 0), (X, -DOOR_HW, DOOR_H + 0.06), 'MS_CityTrim', 0.55)
    b.box((X - WT, DOOR_HW, 0), (X, DOOR_HW + 0.06, DOOR_H + 0.06), 'MS_CityTrim', 0.55)
    b.box((X - WT, -DOOR_HW, DOOR_H), (X, DOOR_HW, DOOR_H + 0.06), 'MS_CityTrim', 0.55)
    # ---- west wall: the car came through here. A ragged opening, not a neat doorway.
    hole_z, hole_y0, hole_y1 = 2.55, -1.35, 1.65
    b.box((-X, -Y, 0), (-X + WT, hole_y0, H), 'MS_CityBrick', 1.0)
    b.box((-X, hole_y1, 0), (-X + WT, Y, H), 'MS_CityBrick', 1.0)
    b.box((-X, hole_y0, hole_z), (-X + WT, hole_y1, H), 'MS_CityBrick', 1.0)
    for i in range(9):                                   # broken brick teeth round the hole
        ty = hole_y0 + (hole_y1 - hole_y0) * (i + 0.5) / 9
        th = rng.uniform(0.12, 0.5)
        b.box((-X, ty - 0.14, hole_z - th), (-X + WT, ty + 0.14, hole_z), 'MS_CityBrick', 0.85)
        tb = rng.uniform(0.08, 0.34)
        b.box((-X + 0.01, ty - 0.12, 0), (-X + WT - 0.01, ty + 0.12, tb), 'MS_CityBrick', 0.8)
    for i in range(14):                                  # rubble spilling inward from the impact
        rx = rng.uniform(-X + 0.2, -X + 2.6)
        ry = rng.uniform(hole_y0 - 0.4, hole_y1 + 0.4)
        s = rng.uniform(0.07, 0.26)
        b.box((rx, ry, 0.02), (rx + s, ry + s * 0.8, 0.02 + s * 0.6), 'MS_CityBrick', rng.uniform(0.7, 1.0))
    # ---- ceiling, with exposed beams so the room has a top edge for the outline pass.
    # Wound to face DOWN, into the room: the player is underneath it, and a ceiling whose normal points at the
    # sky is invisible from the only side anybody ever sees it from.
    b.quad([(-X, Y, H), (X, Y, H), (X, -Y, H), (-X, -Y, H)], 'MS_CityWall', 0.7)
    for i in range(5):
        bx = -X + (2 * X) * (i + 0.5) / 5
        b.box((bx - 0.11, -Y, H - 0.26), (bx + 0.11, Y, H), 'MS_CityWood', 0.72)
    return b.finish(name)


def build_cafe_counter(name='SM_CafeCounter'):
    """5.00 x 0.80 x 1.10 m - the exact size of the C1_Cafe_Counter grey box it replaces."""
    b = B(seed=12)
    w, d, h = 5.0, 0.8, 1.1
    b.box((-w / 2, -d / 2, 0), (w / 2, d / 2, h - 0.06), 'MS_CityWood', 0.85)
    b.box((-w / 2 - 0.04, -d / 2 - 0.04, h - 0.06), (w / 2 + 0.04, d / 2 + 0.04, h), 'MS_CityConcrete', 1.0)
    b.box((-w / 2 + 0.05, -d / 2 - 0.05, 0.08), (w / 2 - 0.05, -d / 2 - 0.02, 0.18), 'MS_CityTrim', 0.5)
    for i in range(4):                                   # recessed panels on the customer side
        px = -w / 2 + 0.2 + i * (w - 0.4) / 4
        b.box((px, -d / 2 - 0.015, 0.22), (px + (w - 0.4) / 4 - 0.12, -d / 2, h - 0.2), 'MS_CityWood', 0.72)
    b.box((-w / 2 + 0.06, -d / 2 + 0.08, 0.5), (w / 2 - 0.06, d / 2 - 0.06, 0.56), 'MS_CityWood', 0.65)
    return b.finish(name)


def build_cafe_register(name='SM_CafeRegister'):
    """0.34 x 0.43 x 0.37 m - the till that stands on the counter top.

    The cafe had an espresso machine and a pastry case but no register at all, so every picture of the room
    invented one or left it out. The Team Owner asked for the register to be near the wall the car comes
    through, so that the car barely misses the coworker standing at it - which needs the thing to exist.

    ORIENTATION: the drawer, the keys and the screen all face Blender +Y, which is the SAME side as the
    counter's staff side (the counter puts its recessed customer panels on -Y). So the till and the counter
    agree at any yaw: whichever way the counter faces, the operator is looking at the keys.

    No brand and no readable text (MegaJam 15d): the keys are blank blocks, the screen is a lit panel.
    """
    b = B(seed=31)
    w, d, h = 0.34, 0.40, 0.18
    b.box((-w / 2, -d / 2, 0), (w / 2, d / 2, h), 'MS_CityTrim', 0.45)                                  # body
    b.box((-w / 2 + 0.02, d / 2, 0.03), (w / 2 - 0.02, d / 2 + 0.012, 0.11), 'MS_CityMetal', 0.6)       # drawer
    b.box((-0.04, d / 2 + 0.012, 0.06), (0.04, d / 2 + 0.03, 0.08), 'MS_CityMetal', 0.75)               # pull
    for r in range(4):                                                        # four rows of blank keys
        for i in range(5):
            kx = -w / 2 + 0.045 + i * 0.052
            ky = 0.09 - r * 0.045
            b.box((kx, ky, h), (kx + 0.038, ky + 0.033, h + 0.012), 'MS_CityMetal', 0.55 + 0.1 * ((i + r) % 2))
    # the screen on its stalk at the back of the till, tilted up toward the operator on +Y
    b.box((-0.03, -0.13, h), (0.03, -0.09, h + 0.06), 'MS_CityTrim', 0.4)
    b.box((-0.11, -0.135, h + 0.06), (0.11, -0.10, h + 0.19), 'MS_CityTrim', 0.4)
    b.quad([(0.095, -0.098, h + 0.075), (-0.095, -0.098, h + 0.075),
            (-0.095, -0.098, h + 0.175), (0.095, -0.098, h + 0.175)], 'MS_CitySignB', 1.0)
    b.box((-w / 2, -d / 2, h), (w / 2, d / 2, h + 0.008), 'MS_CityTrim', 0.5)                      # top plate
    return b.finish(name)


def build_cafe_espresso(name='SM_CafeEspresso'):
    b = B(seed=13)
    w, d, h = 0.80, 0.52, 0.46
    b.box((-w / 2, -d / 2, 0), (w / 2, d / 2, h), 'MS_CityMetal', 1.0)
    b.box((-w / 2 + 0.05, -d / 2 - 0.02, 0.0), (w / 2 - 0.05, -d / 2 + 0.1, 0.1), 'MS_CityTrim', 0.45)  # drip tray
    b.box((-w / 2 + 0.02, -d / 2 + 0.02, h), (w / 2 - 0.02, d / 2 - 0.02, h + 0.12), 'MS_CityAccent', 0.8)
    for sx in (-0.2, 0.2):                               # two group heads with portafilters
        b.box((sx - 0.07, -d / 2 - 0.04, 0.1), (sx + 0.07, -d / 2 + 0.06, 0.26), 'MS_CityMetal', 0.9)
        b.tube((sx, -d / 2 - 0.06, 0.1), 0.05, 0.055, 'MS_CityTrim', n=8, c=0.5)
    b.tube((w / 2 - 0.06, -d / 2 + 0.06, 0.08), 0.3, 0.014, 'MS_CityMetal', n=6, c=0.95)   # steam wand
    b.tube((-0.3, 0.0, h + 0.12), 0.1, 0.05, 'MS_CityMetal', n=8, c=0.9)
    return b.finish(name)


def build_cafe_pastry_case(name='SM_CafePastryCase'):
    b = B(seed=14)
    w, d, h = 1.20, 0.60, 0.74
    b.box((-w / 2, -d / 2, 0), (w / 2, d / 2, 0.1), 'MS_CityMetal', 0.9)
    for sx in (-w / 2, w / 2 - 0.05):                    # corner posts
        b.box((sx, -d / 2, 0.1), (sx + 0.05, d / 2, h), 'MS_CityTrim', 0.5)
    b.box((-w / 2, -d / 2, h - 0.05), (w / 2, d / 2, h), 'MS_CityTrim', 0.5)
    b.quad([(-w / 2, -d / 2, 0.1), (w / 2, -d / 2, 0.1), (w / 2, -d / 2, h), (-w / 2, -d / 2, h)], 'MS_CityGlass', 0.75)
    b.quad([(w / 2, d / 2, 0.1), (-w / 2, d / 2, 0.1), (-w / 2, d / 2, h), (w / 2, d / 2, h)], 'MS_CityGlass', 0.6)
    for i in range(3):                                   # trays of something
        tx = -w / 2 + 0.14 + i * 0.34
        b.box((tx, -d / 2 + 0.08, 0.38), (tx + 0.28, d / 2 - 0.08, 0.44), 'MS_CityAccent', 0.85)
    b.box((-w / 2 + 0.05, -d / 2 + 0.06, 0.34), (w / 2 - 0.05, d / 2 - 0.06, 0.38), 'MS_CityMetal', 0.8)
    return b.finish(name)


def build_cafe_shelf(name='SM_CafeShelf'):
    b = B(seed=15)
    w, d, h = 2.0, 0.34, 2.10
    for sx in (-w / 2, w / 2 - 0.06):
        b.box((sx, -d / 2, 0), (sx + 0.06, d / 2, h), 'MS_CityWood', 0.8)
    for i in range(5):
        z = 0.3 + i * 0.44
        b.box((-w / 2, -d / 2, z), (w / 2, d / 2, z + 0.045), 'MS_CityWood', 0.88)
        for j in range(b.rng.randint(3, 7)):             # cups, bags, tins
            px = b.rng.uniform(-w / 2 + 0.08, w / 2 - 0.26)
            s = b.rng.uniform(0.09, 0.2)
            b.box((px, -d / 2 + 0.06, z + 0.045), (px + s, -d / 2 + 0.06 + min(s, d - 0.14), z + 0.045 + s * 1.2),
                  'MS_CityAccent' if j % 2 else 'MS_CityWood', b.rng.uniform(0.6, 1.0))
    return b.finish(name)


def build_cafe_table(name='SM_CafeTable'):
    b = B(seed=16)
    b.tube((0, 0, 0), 0.03, 0.26, 'MS_CityTrim', n=10, c=0.5)
    b.tube((0, 0, 0.03), 0.68, 0.045, 'MS_CityTrim', n=8, c=0.55)
    b.tube((0, 0, 0.71), 0.05, 0.37, 'MS_CityWood', n=14, c=0.9)
    return b.finish(name)


def build_cafe_chair(name='SM_CafeChair'):
    b = B(seed=17)
    for sx in (-0.19, 0.19):
        for sy in (-0.19, 0.19):
            b.box((sx - 0.022, sy - 0.022, 0), (sx + 0.022, sy + 0.022, 0.44), 'MS_CityTrim', 0.5)
    b.box((-0.22, -0.22, 0.44), (0.22, 0.22, 0.48), 'MS_CityWood', 0.9)
    for i in range(4):                                   # slatted back
        z = 0.56 + i * 0.1
        b.box((-0.21, 0.17, z), (0.21, 0.21, z + 0.06), 'MS_CityWood', 0.86)
    for sx in (-0.19, 0.19):
        b.box((sx - 0.022, 0.168, 0.44), (sx + 0.022, 0.212, 0.92), 'MS_CityTrim', 0.5)
    return b.finish(name)


def build_cafe_awning(name='SM_CafeAwning'):
    """Goes outside, over the cafe door. 4.0 m wide, projects 1.3 m, underside clear at 2.5 m."""
    b = B(seed=18)
    w, pr = 4.0, 1.3
    for sx in (-w / 2 + 0.1, 0.0, w / 2 - 0.1):
        b.box((sx - 0.04, 0, 2.52), (sx + 0.04, pr, 2.56), 'MS_CityTrim', 0.5)
        b.box((sx - 0.04, pr - 0.08, 2.56), (sx + 0.04, pr, 3.1), 'MS_CityTrim', 0.5)
    b.quad([(-w / 2, 0, 3.1), (w / 2, 0, 3.1), (w / 2, pr, 2.56), (-w / 2, pr, 2.56)], 'MS_CityCloth', 0.95)
    b.quad([(-w / 2, pr, 2.56), (w / 2, pr, 2.56), (w / 2, pr, 2.3), (-w / 2, pr, 2.3)], 'MS_CityCloth', 0.8)
    for i in range(9):                                   # scalloped valance
        vx = -w / 2 + (w) * i / 9
        b.quad([(vx, pr, 2.3), (vx + w / 9, pr, 2.3), (vx + w / 9 * 0.5, pr, 2.18)], 'MS_CityCloth', 0.78)
    return b.finish(name)


def build_cafe_menu_board(name='SM_CafeMenuBoard'):
    """An A-frame chalkboard. Blank: no words, so nothing to translate and nothing to trademark."""
    b = B(seed=19)
    for sy, lean in ((-0.22, -1), (0.22, 1)):
        b.quad([(-0.35, sy, 0), (0.35, sy, 0), (0.3, sy * 0.25, 1.0), (-0.3, sy * 0.25, 1.0)], 'MS_CityWood', 0.8)
        b.quad([(-0.3, sy * 0.25, 1.0), (0.3, sy * 0.25, 1.0), (0.3, sy, 0), (-0.35, sy, 0)], 'MS_CityTrim', 0.25)
    b.box((-0.34, -0.2, 0.42), (0.34, 0.2, 0.46), 'MS_CityWood', 0.75)
    return b.finish(name)


def build_cafe_sign(name='SM_CafeSign'):
    """The cafe's own projecting sign: a lit blank panel in a bracket. No name on it - section 15d."""
    b = B(seed=20)
    b.box((-0.06, 0, 2.9), (0.06, 0.22, 3.9), 'MS_CityTrim', 0.45)
    b.box((-0.06, 0.18, 3.78), (1.55, 0.26, 3.86), 'MS_CityTrim', 0.45)
    b.box((0.16, 0.1, 2.95), (1.5, 0.34, 3.8), 'MS_CityTrim', 0.4)
    b.quad([(0.2, 0.1, 3.0), (1.46, 0.1, 3.0), (1.46, 0.1, 3.75), (0.2, 0.1, 3.75)], 'MS_CitySignA', 1.0)
    b.quad([(1.46, 0.34, 3.0), (0.2, 0.34, 3.0), (0.2, 0.34, 3.75), (1.46, 0.34, 3.75)], 'MS_CitySignA', 1.0)
    return b.finish(name)


# =========================================================================== THE CITY
# PLACEMENT RULE for every building below: the facade is on Blender y = 0 facing -Y, and the body runs back
# towards +Y. Blender +Y becomes Unreal -Y, so in the game the facade faces +Y and the body runs to -Y. That
# makes the street line one number to snap to:
#     south side of an east-west street: yaw 0,   place at the south facade line
#     north side:                        yaw 180, place at the north facade line
# Street buildings are 8.0 m deep because that is the footprint the grey boxes they replace occupy
# (C1_Street_BuildingN/S are 800 cm deep). Height is free: nothing is above the player there.
#
# TOKYO vs NEW YORK, and where each one goes. The two cities do not blend by averaging; they blend by
# ZONING, which is also what makes the layout legible in play:
#   * At street level, along the 60 m lane the player actually walks, everything is TOKYO: narrow plots
#     (4-8 m), a shop on the ground floor of every single building, flats above it, signage stacked
#     vertically because the plot is too narrow for it to go sideways, and services (AC, ducts, cable) worn
#     on the outside of the building rather than hidden in it.
#   * Above and behind that, everything is NEW YORK: masonry setback towers and curtain-wall slabs, 40-55 m,
#     timber water tanks and fire escapes. They are never walked to, so they are the skyline the lane is
#     seen against.
# The result is a narrow, cluttered, signed lane with a heavy American skyline over it - which is the actual
# look the brief asks for, and it costs nothing extra because the two families live at different distances.

def _shop_body(b, w, d, nfl, wall, seed, shutter=False, balcony=True, tank=False):
    rng = random.Random(seed)
    gh = 3.0                                              # ground floor is taller: it is a shop
    top = gh + nfl * FH
    b.box((-w / 2, 0, 0), (w / 2, d, top), wall, 1.0, skip=('ylo', 'zhi'))
    if shutter:                                           # roller shutter instead of glazing: closed unit
        b.box((-w / 2 + 0.3, -0.06, 0), (w / 2 - 0.3, 0.06, 2.6), 'MS_CityMetal', 0.9)
        for i in range(13):
            z = 0.1 + i * 0.19
            b.box((-w / 2 + 0.3, -0.09, z), (w / 2 - 0.3, -0.06, z + 0.12), 'MS_CityMetal', 0.78)
        b.box((-w / 2, -0.06, 2.6), (w / 2, 0.08, gh), 'MS_CityTrim', 0.5)
    else:
        shopfront(b, -w / 2 + 0.25, w / 2 - 0.25, -0.1, h=2.7, rng=rng)
        b.quad([(-w / 2, 0, 0), (-w / 2 + 0.25, 0, 0), (-w / 2 + 0.25, 0, gh), (-w / 2, 0, gh)], wall, 0.95)
        b.quad([(w / 2 - 0.25, 0, 0), (w / 2, 0, 0), (w / 2, 0, gh), (w / 2 - 0.25, 0, gh)], wall, 0.95)
        b.quad([(-w / 2, 0, 3.0), (w / 2, 0, 3.0), (w / 2, 0, gh), (-w / 2, 0, gh)], wall, 0.95)
    punched_wall(b, -w / 2, w / 2, 0.0, gh, nfl, slot=wall, rng=rng, lit=0.55)
    if balcony:                                           # the washing-line balcony that says "people live here"
        for fl in range(nfl):
            z = gh + fl * FH + 0.02
            if rng.random() < 0.6:
                b.box((-w / 2 + 0.2, -0.75, z), (w / 2 - 0.2, 0.0, z + 0.1), 'MS_CityConcrete', 0.95)
                for i in range(int((w - 0.4) / 0.28)):
                    rx = -w / 2 + 0.25 + i * 0.28
                    b.box((rx, -0.72, z + 0.1), (rx + 0.03, -0.69, z + 1.0), 'MS_CityTrim', 0.55)
                b.box((-w / 2 + 0.2, -0.75, z + 1.0), (w / 2 - 0.2, -0.69, z + 1.06), 'MS_CityTrim', 0.55)
    for fl in range(nfl):                                 # air conditioners bolted to the front
        if rng.random() < 0.5:
            ax = rng.uniform(-w / 2 + 0.6, w / 2 - 1.0)
            z = gh + fl * FH + 1.9
            b.box((ax, -0.38, z), (ax + 0.86, 0.0, z + 0.62), 'MS_CityMetal', 0.85)
            b.box((ax + 0.1, -0.42, z + 0.08), (ax + 0.76, -0.38, z + 0.54), 'MS_CityTrim', 0.5)
    band_sides(b, -w / 2, w / 2, 0, d, gh, nfl - 1, slot='MS_CityConcrete', out=0.07, t=0.16)
    parapet(b, -w / 2, w / 2, 0, d, top)
    roof_clutter(b, -w / 2 + 0.5, w / 2 - 0.5, 0.6, d - 0.6, top, rng, tank=tank, n=2)
    return top


def build_shophouse_a(name='SM_ShopHouse_A'):
    """6 m wide, 4 storeys over a shop. The workhorse: most of the lane is this with different signage."""
    b = B(seed=31)
    top = _shop_body(b, 6.0, 8.0, 3, 'MS_CityWall', 31, tank=False)
    b.box((-0.07, -0.3, 3.4), (0.07, 0.0, top - 0.6), 'MS_CityTrim', 0.45)          # vertical sign spine
    for i in range(4):
        z = 3.6 + i * 1.55
        b.box((-0.42, -0.34, z), (0.42, -0.06, z + 1.3), 'MS_CityTrim', 0.4)
        b.quad([(-0.38, -0.36, z + 0.05), (0.38, -0.36, z + 0.05), (0.38, -0.36, z + 1.25), (-0.38, -0.36, z + 1.25)],
               'MS_CitySignA' if i % 2 == 0 else 'MS_CitySignB', 1.0)
    return b.finish(name)


def build_shophouse_b(name='SM_ShopHouse_B'):
    """4 m wide, 5 storeys - the Tokyo pencil building. Narrow plot, so the sign has to go up."""
    b = B(seed=32)
    top = _shop_body(b, 4.0, 8.0, 4, 'MS_CityWall', 32, balcony=True)
    b.box((-0.75, -0.36, 3.3), (0.75, -0.04, top - 0.4), 'MS_CityTrim', 0.4)        # one tall sign box
    b.quad([(-0.7, -0.38, 3.45), (0.7, -0.38, 3.45), (0.7, -0.38, top - 0.55), (-0.7, -0.38, top - 0.55)],
           'MS_CitySignB', 1.0)
    for i in range(6):                                                               # invented glyph blocks
        z = 3.65 + i * (top - 4.5) / 6
        b.box((-0.44, -0.42, z), (0.44, -0.38, z + (top - 4.9) / 6 * 0.55), 'MS_CityTrim', 0.3)
    return b.finish(name)


def build_shophouse_c(name='SM_ShopHouse_C'):
    """8 m wide, 3 storeys, brick, shutter down. The closed unit - a lane of open shops reads as a set."""
    b = B(seed=33)
    top = _shop_body(b, 8.0, 8.0, 2, 'MS_CityBrick', 33, shutter=True, balcony=False)
    b.box((-3.2, -0.26, 3.1), (3.2, -0.02, 4.0), 'MS_CityTrim', 0.4)                # dead blade sign
    b.quad([(-3.1, -0.28, 3.2), (3.1, -0.28, 3.2), (3.1, -0.28, 3.9), (-3.1, -0.28, 3.9)], 'MS_CitySignA', 0.25)
    return b.finish(name)


def build_fire_escape(name='SM_FireEscape'):
    """New York, bolted on: 3 landings and zigzag stairs. Reads instantly, and it is a platforming surface."""
    b = B(seed=34)
    w = 2.6
    for fl in range(3):
        z = 3.2 + fl * 3.4
        b.box((-w / 2, -1.5, z), (w / 2, 0.0, z + 0.06), 'MS_CityMetal', 0.8)        # landing
        for i in range(int(w / 0.3)):
            rx = -w / 2 + i * 0.3
            b.box((rx, -1.48, z + 0.06), (rx + 0.03, -1.45, z + 1.0), 'MS_CityTrim', 0.55)
        b.box((-w / 2, -1.5, z + 1.0), (w / 2, -1.44, z + 1.06), 'MS_CityTrim', 0.55)
        for sx in (-w / 2, w / 2 - 0.06):                                            # stringers
            b.box((sx, -1.5, z), (sx + 0.06, -1.44, z + 1.06), 'MS_CityTrim', 0.5)
        if fl < 2:                                                                   # the flight going up
            for s in range(10):
                t = s / 10.0
                sx = -w / 2 + 0.3 + t * (w - 0.9)
                sz = z + 0.06 + t * 3.4
                b.box((sx, -1.3, sz), (sx + (w - 0.9) / 10 + 0.04, -0.5, sz + 0.05), 'MS_CityMetal', 0.72)
    for sx in (-w / 2 + 0.1, w / 2 - 0.1):                                           # hangers back to the wall
        b.box((sx - 0.04, -0.04, 3.2), (sx + 0.04, 0.0, 10.0), 'MS_CityTrim', 0.5)
    return b.finish(name)


def _setback(b, masses, d0, wall, seed, tank=True):
    """A New York setback tower: stacked masses, each narrower than the one below."""
    rng = random.Random(seed)
    z = 0.0
    for i, (w, nfl, inset) in enumerate(masses):
        d = d0 - inset * 2
        y0 = inset
        b.box((-w / 2, y0, z), (w / 2, y0 + d, z + nfl * FH), wall, 1.0, skip=('ylo', 'zhi') if i == 0 else ('ylo',))
        punched_wall(b, -w / 2, w / 2, y0, z, nfl, slot=wall, rng=rng, mod=2.1, ww=1.15, wh=1.9, lit=0.42)
        band_sides(b, -w / 2, w / 2, y0, y0 + d, z - nfl * FH, nfl - 1, slot=wall)
        z += nfl * FH
        parapet(b, -w / 2, w / 2, y0, y0 + d, z, h=1.1)
        if i < len(masses) - 1:
            roof_clutter(b, -w / 2 + 1, w / 2 - 1, y0 + 1, y0 + d - 1, z, rng, tank=False, n=2)
    roof_clutter(b, -masses[-1][0] / 2 + 1.5, masses[-1][0] / 2 - 1.5,
                 masses[-1][2] + 1.5, masses[-1][2] + d0 - masses[-1][2] * 2 - 1.5, z, rng, tank=tank, n=3)
    return z


def build_setback_tower(name='SM_SetbackTower'):
    """16 m wide, 3 masses, about 41 m. Masonry, water tank on top. Pure 1920s New York."""
    b = B(seed=35)
    _setback(b, [(16.0, 5, 0.0), (12.0, 4, 2.2), (8.0, 3, 4.2)], 14.0, 'MS_CityBrick', 35, tank=True)
    return b.finish(name)


def build_curtain_tower(name='SM_CurtainTower'):
    """14 m wide, 16 storeys, about 55 m. Mullions and spandrels - the modern slab behind the old lane."""
    b = B(seed=36)
    rng = random.Random(36)
    w, d, nfl = 14.0, 13.0, 16
    top = nfl * FH
    b.box((-w / 2, 0, 0), (w / 2, d, top), 'MS_CityConcrete', 0.95, skip=('ylo', 'zhi'))
    b.box((-w / 2, -0.25, 0), (w / 2, 0.0, 5.4), 'MS_CityConcrete', 1.0, skip=('ylo',))   # lobby base
    shopfront(b, -w / 2 + 0.6, w / 2 - 0.6, -0.3, h=4.6, rng=rng, door=True)
    mod = 1.55
    n = int(w / mod)
    pad = (w - n * mod) / 2
    for fl in range(nfl):
        z = 5.4 + fl * ((top - 5.4) / nfl)
        fh = (top - 5.4) / nfl
        b.box((-w / 2, -0.1, z), (w / 2, 0.0, z + 0.78), 'MS_CityTrim', 0.4)         # spandrel at every slab
        for i in range(n):
            cx = -w / 2 + pad + mod * (i + 0.5)
            b.box((cx - 0.06, -0.12, z), (cx + 0.06, 0.0, z + fh), 'MS_CityTrim', 0.45)   # mullion
            pane = 0.3 + 0.6 * rng.random() if rng.random() < 0.5 else 0.12 + 0.1 * rng.random()
            b.quad([(cx - mod / 2 + 0.06, -0.04, z + 0.78), (cx + mod / 2 - 0.06, -0.04, z + 0.78),
                    (cx + mod / 2 - 0.06, -0.04, z + fh), (cx - mod / 2 + 0.06, -0.04, z + fh)],
                   'MS_CityGlass', pane)
        if fl == nfl - 6:                                                            # a plant floor: louvres
            for i in range(n * 3):
                lx = -w / 2 + i * (w / (n * 3))
                b.box((lx, -0.14, z + 0.9), (lx + w / (n * 3) - 0.04, -0.06, z + fh - 0.2), 'MS_CityMetal', 0.7)
    band_sides(b, -w / 2, w / 2, 0, d, 5.4, nfl - 1, fh=(top - 5.4) / nfl, slot='MS_CityTrim', t=0.3)
    parapet(b, -w / 2, w / 2, 0, d, top, h=1.2)
    roof_clutter(b, -w / 2 + 2, w / 2 - 2, 2, d - 2, top, rng, tank=False, n=4)
    b.tube((0, d / 2, top + 1.2), 7.0, 0.22, 'MS_CityMetal', n=6, c=0.8)             # mast
    return b.finish(name)


def build_corner_block(name='SM_CornerBlock'):
    """An L-shaped corner building for the crossing west of the cafe - the road the car came down.

    Its two wings stand on the two street lines that meet, so the corner reads as a junction and not as a
    gap between two unrelated buildings. Origin is the inside corner.
    """
    b = B(seed=37)
    rng = random.Random(37)
    gh, nfl = 3.0, 4
    top = gh + nfl * FH
    b.box((0.0, 0.0, 0), (14.0, 8.0, top), 'MS_CityWall', 1.0, skip=('ylo', 'xlo', 'zhi'))   # wing along x
    b.box((0.0, 0.0, 0), (8.0, 16.0, top), 'MS_CityWall', 1.0, skip=('xlo', 'ylo', 'zhi'))   # wing along y
    shopfront(b, 0.3, 13.6, -0.1, h=2.7, rng=rng)
    punched_wall(b, 0.0, 14.0, 0.0, gh, nfl, slot='MS_CityWall', rng=rng, lit=0.5)
    parapet(b, 0.0, 14.0, 0.0, 8.0, top)
    parapet(b, 0.0, 8.0, 8.0, 16.0, top)
    roof_clutter(b, 1, 13, 1, 7, top, rng, tank=True, n=3)
    b.box((1.2, -0.3, 3.3), (2.0, 0.0, top - 1.0), 'MS_CityTrim', 0.4)
    b.quad([(1.25, -0.32, 3.4), (1.95, -0.32, 3.4), (1.95, -0.32, top - 1.1), (1.25, -0.32, top - 1.1)],
           'MS_CitySignB', 1.0)
    return b.finish(name)


def build_plaza_tower(name='SM_PlazaTower'):
    """The backdrop to the boss arena: 20 m wide, 9 storeys, a deep colonnaded base. Reads as the building
    the plaza belongs to, so the 30 x 30 m walled lot stops looking like a box with a boss in it."""
    b = B(seed=38)
    rng = random.Random(38)
    w, d, nfl = 20.0, 16.0, 9
    base = 6.2
    top = base + nfl * FH
    b.box((-w / 2, 0, 0), (w / 2, d, top), 'MS_CityConcrete', 0.95, skip=('ylo', 'zhi'))
    for i in range(7):                                      # colonnade: columns the player can see between
        cx = -w / 2 + 1.2 + i * (w - 2.4) / 6
        b.tube((cx, -1.1, 0), base, 0.42, 'MS_CityConcrete', n=10, c=1.0)
    b.box((-w / 2, -1.6, base), (w / 2, 0.0, base + 0.9), 'MS_CityConcrete', 1.0)   # entablature
    b.quad([(-w / 2 + 0.6, -0.02, 0.0), (w / 2 - 0.6, -0.02, 0.0),
            (w / 2 - 0.6, -0.02, base - 0.3), (-w / 2 + 0.6, -0.02, base - 0.3)], 'MS_CityGlass', 0.5)
    punched_wall(b, -w / 2, w / 2, 0.0, base + 0.9, nfl, slot='MS_CityConcrete', rng=rng, mod=2.2, ww=1.3,
                 wh=2.0, lit=0.4)
    band_sides(b, -w / 2, w / 2, 0, d, base + 0.9, nfl - 1)
    parapet(b, -w / 2, w / 2, 0, d, top, h=1.2)
    roof_clutter(b, -w / 2 + 2, w / 2 - 2, 2, d - 2, top, rng, tank=True, n=3)
    return b.finish(name)


def build_block_filler(name='SM_BlockFiller'):
    """A plain 12 x 8 m block with no shopfront, for the backs of things and the far side of the crossing."""
    b = B(seed=39)
    rng = random.Random(39)
    w, d, nfl = 12.0, 8.0, 4
    top = nfl * FH
    b.box((-w / 2, 0, 0), (w / 2, d, top), 'MS_CityBrick', 1.0, skip=('ylo', 'zhi'))
    punched_wall(b, -w / 2, w / 2, 0.0, 0.4, nfl, slot='MS_CityBrick', rng=rng, lit=0.45)
    band_sides(b, -w / 2, w / 2, 0, d, 0.4, nfl - 1, slot='MS_CityConcrete')
    parapet(b, -w / 2, w / 2, 0, d, top)
    roof_clutter(b, -w / 2 + 1, w / 2 - 1, 1, d - 1, top, rng, tank=True, n=2)
    return b.finish(name)


# =========================================================================== BEAT 4: THE DESTROYED BUILDINGS
# Sized against the ONE number that matters here: Splice blinks 600 cm on open ground, measured on Justin's
# Mac (ROADMAP, Nov 13). So a gap the player must blink is 6.5-8.5 m - past a run-and-jump, inside a blink -
# and a gap they may jump is under 3 m. Platform tops are flat and at least 3 m across, because landing a
# blink on a sloped or narrow surface is where this kind of section stops being fun.
def build_ruin_slab_a(name='SM_RuinSlab_A'):
    """5.0 x 5.0 m floor plate, broken on two edges. Top at z = 0.45 so it stacks predictably."""
    b = B(seed=41)
    rng = random.Random(41)
    w, d, t = 5.0, 5.0, 0.45
    b.box((-w / 2, -d / 2, 0), (w / 2, d / 2, t), 'MS_CityConcrete', 0.95, skip=('xhi', 'yhi'))
    for i in range(7):                                      # ragged east edge
        ty = -d / 2 + d * i / 7
        ex = w / 2 - rng.uniform(0.0, 0.55)
        b.box((w / 2 - 0.6, ty, 0), (ex, ty + d / 7, t), 'MS_CityConcrete', rng.uniform(0.85, 1.0))
    for i in range(7):                                      # ragged north edge
        tx = -w / 2 + w * i / 7
        ey = d / 2 - rng.uniform(0.0, 0.5)
        b.box((tx, d / 2 - 0.6, 0), (tx + w / 7, ey, t), 'MS_CityConcrete', rng.uniform(0.85, 1.0))
    for i in range(9):                                      # rebar whiskers
        rx, ry = rng.uniform(-w / 2 + 0.4, w / 2 - 0.4), rng.uniform(-d / 2 + 0.4, d / 2 - 0.4)
        b.tube((rx, ry, t - 0.05), rng.uniform(0.3, 0.8), 0.018, 'MS_CityMetal', n=4, c=0.6)
    return b.finish(name)


def build_ruin_slab_b(name='SM_RuinSlab_B'):
    """7.0 x 3.2 m plate with a tilt built in, still flat on top. The long stepping stone."""
    b = B(seed=42)
    rng = random.Random(42)
    w, d, t = 7.0, 3.2, 0.45
    b.box((-w / 2, -d / 2, 0), (w / 2, d / 2, t), 'MS_CityConcrete', 0.95, skip=('xlo',))
    for i in range(6):
        ty = -d / 2 + d * i / 6
        ex = -w / 2 + rng.uniform(0.0, 0.7)
        b.box((ex, ty, 0), (-w / 2 + 0.7, ty + d / 6, t), 'MS_CityConcrete', rng.uniform(0.85, 1.0))
    b.box((-w / 2 + 0.3, -d / 2, t), (-w / 2 + 0.55, d / 2, t + 0.9), 'MS_CityConcrete', 0.9)   # stub wall
    for i in range(6):
        rx, ry = rng.uniform(-w / 2 + 0.6, w / 2 - 0.4), rng.uniform(-d / 2 + 0.3, d / 2 - 0.3)
        b.tube((rx, ry, t - 0.05), rng.uniform(0.25, 0.7), 0.018, 'MS_CityMetal', n=4, c=0.6)
    return b.finish(name)


def build_ruin_beam(name='SM_RuinBeam'):
    """An 8 m steel I-beam, 0.42 m wide on top. The deliberately nervous crossing between two slabs."""
    b = B(seed=43)
    L, w, h = 8.0, 0.42, 0.5
    b.box((-L / 2, -w / 2, h - 0.05), (L / 2, w / 2, h), 'MS_CityMetal', 0.85)        # top flange
    b.box((-L / 2, -w / 2, 0), (L / 2, w / 2, 0.05), 'MS_CityMetal', 0.8)             # bottom flange
    b.box((-L / 2, -0.03, 0.05), (L / 2, 0.03, h - 0.05), 'MS_CityMetal', 0.7)        # web
    for i in range(9):                                                                 # bolt plates
        bx = -L / 2 + 0.4 + i * (L - 0.8) / 8
        b.box((bx - 0.06, -0.06, 0.12), (bx + 0.06, 0.06, h - 0.12), 'MS_CityMetal', 0.6)
    return b.finish(name)


def build_ruin_wall(name='SM_RuinWall'):
    """A 6 m broken wall, 5 m at its tallest. Cover, a sight-line blocker, and the thing that tells the
    player they are inside a building that used to have floors."""
    b = B(seed=44)
    rng = random.Random(44)
    w, t, h = 6.0, 0.4, 5.0
    for i in range(12):
        tx = -w / 2 + w * i / 12
        th = h * (0.45 + 0.55 * math.sin(math.pi * (i + 0.5) / 12)) - rng.uniform(0.0, 0.5)
        b.box((tx, -t / 2, 0), (tx + w / 12, t / 2, max(0.6, th)), 'MS_CityBrick', rng.uniform(0.85, 1.0))
    for i in range(5):
        rx = rng.uniform(-w / 2 + 0.5, w / 2 - 0.5)
        b.tube((rx, 0.0, 1.2), rng.uniform(0.4, 1.1), 0.02, 'MS_CityMetal', n=4, c=0.6)
    return b.finish(name)


def build_rubble(name='SM_Rubble'):
    """A 2.6 x 2.0 m heap. Dressing, and it hides where a slab meets the ground."""
    b = B(seed=45)
    rng = random.Random(45)
    for _ in range(26):
        s = rng.uniform(0.12, 0.5)
        x, y = rng.gauss(0, 0.6), rng.gauss(0, 0.45)
        z = max(0.0, 0.55 - (x * x + y * y) * 0.5) * rng.uniform(0.3, 1.0)
        b.box((x, y, 0), (x + s, y + s * 0.85, z + s * 0.5),
              'MS_CityConcrete' if rng.random() < 0.6 else 'MS_CityBrick', rng.uniform(0.7, 1.0))
    return b.finish(name)


# =========================================================================== MAKING IT FEEL ALIVE
# "Alive" is not more buildings. It is evidence that somebody was here five minutes ago and will be back:
# a machine that sells something, a bike leaning where it should not be, bags out for collection, a cone
# round a hole nobody has filled. Every one of these is small, repeats cheaply, and is readable in
# silhouette, which is what the outline pass rewards.
def build_vending_machine(name='SM_VendingMachine'):
    """1.10 x 0.75 x 1.90 m. The single most Tokyo object there is, and it is a free light source at night."""
    b = B(seed=51)
    w, d, h = 1.10, 0.75, 1.90
    b.box((-w / 2, -d / 2, 0), (w / 2, d / 2, h), 'MS_CityAccent', 0.9, skip=('ylo',))
    b.box((-w / 2, -d / 2, 0), (w / 2, -d / 2 + 0.05, h), 'MS_CityAccent', 0.95, skip=('ylo',))
    b.quad([(-w / 2, -d / 2, 0.62), (w / 2, -d / 2, 0.62), (w / 2, -d / 2, h - 0.12), (-w / 2, -d / 2, h - 0.12)],
           'MS_CityGlass', 0.8)                                                        # lit display window
    for r in range(3):                                                                 # rows of product
        for c in range(4):
            px = -w / 2 + 0.1 + c * (w - 0.2) / 4
            pz = 0.72 + r * 0.33
            b.box((px, -d / 2 + 0.04, pz), (px + (w - 0.2) / 4 - 0.04, -d / 2 + 0.14, pz + 0.22),
                  'MS_CitySignA' if (r + c) % 2 else 'MS_CitySignB', 1.0)
    b.quad([(-w / 2, -d / 2 - 0.01, h - 0.12), (w / 2, -d / 2 - 0.01, h - 0.12),
            (w / 2, -d / 2 - 0.01, h), (-w / 2, -d / 2 - 0.01, h)], 'MS_CitySignB', 1.0)   # lit header
    b.box((-w / 2 + 0.06, -d / 2 - 0.04, 0.34), (w / 2 - 0.3, -d / 2, 0.52), 'MS_CityTrim', 0.4)  # delivery flap
    b.box((w / 2 - 0.26, -d / 2 - 0.03, 0.56), (w / 2 - 0.06, -d / 2, 0.6), 'MS_CityMetal', 0.7)  # coin slot
    for sx in (-w / 2 + 0.06, w / 2 - 0.12):                                           # feet
        b.box((sx, -d / 2 + 0.06, -0.0), (sx + 0.06, d / 2 - 0.06, 0.04), 'MS_CityTrim', 0.3)
    return b.finish(name)


def build_sign_vertical(name='SM_SignVertical'):
    """A 3.4 m stacked sign on a wall bracket. Invented glyph blocks, no readable text (section 15d)."""
    b = B(seed=52)
    rng = random.Random(52)
    b.box((-0.05, 0.0, 0.0), (0.05, 0.3, 3.4), 'MS_CityTrim', 0.4)
    b.box((-0.31, 0.24, 0.0), (0.31, 0.3, 3.4), 'MS_CityTrim', 0.4)
    b.quad([(0.28, 0.32, 0.08), (-0.28, 0.32, 0.08), (-0.28, 0.32, 3.32), (0.28, 0.32, 3.32)], 'MS_CitySignA', 1.0)
    b.quad([(-0.28, 0.22, 0.08), (0.28, 0.22, 0.08), (0.28, 0.22, 3.32), (-0.28, 0.22, 3.32)], 'MS_CitySignA', 1.0)
    for i in range(7):                                      # the glyphs: solid blocks, deliberately unreadable
        z = 0.22 + i * 0.44
        for (gx0, gx1, gz0, gz1) in [(-0.18, 0.18, 0.04, 0.09), (-0.1, 0.1, 0.12, 0.3), (-0.2, 0.2, 0.2, 0.25)][
                : rng.randint(2, 3)]:
            b.box((gx0, 0.2, z + gz0), (gx1, 0.22, z + gz1), 'MS_CityTrim', 0.2)
            b.box((gx0, 0.32, z + gz0), (gx1, 0.34, z + gz1), 'MS_CityTrim', 0.2)
    return b.finish(name)


def build_sign_blade(name='SM_SignBlade'):
    """A 1.9 m sign projecting from a wall at first-floor height. Blank lit faces."""
    b = B(seed=53)
    b.box((-0.07, 0.0, 0.0), (0.07, 0.2, 1.2), 'MS_CityTrim', 0.4)
    b.box((0.0, 0.14, 1.06), (1.9, 0.2, 1.14), 'MS_CityTrim', 0.4)
    b.box((0.16, 0.06, 0.06), (1.86, 0.3, 1.02), 'MS_CityTrim', 0.35)
    b.quad([(0.2, 0.06, 0.1), (1.82, 0.06, 0.1), (1.82, 0.06, 0.98), (0.2, 0.06, 0.98)], 'MS_CitySignB', 1.0)
    b.quad([(1.82, 0.3, 0.1), (0.2, 0.3, 0.1), (0.2, 0.3, 0.98), (1.82, 0.3, 0.98)], 'MS_CitySignB', 1.0)
    return b.finish(name)


def build_ac_unit(name='SM_ACUnit'):
    b = B(seed=54)
    w, d, h = 0.90, 0.38, 0.68
    b.box((-w / 2, 0, 0), (w / 2, d, h), 'MS_CityMetal', 0.85)
    b.box((-w / 2 + 0.08, -0.04, 0.08), (w / 2 - 0.08, 0.0, h - 0.08), 'MS_CityTrim', 0.45)
    for sx in (-w / 2 + 0.05, w / 2 - 0.12):
        b.box((sx, d - 0.02, -0.0), (sx + 0.07, d + 0.22, 0.05), 'MS_CityTrim', 0.4)   # wall bracket
    return b.finish(name)


def build_utility_pole(name='SM_UtilityPole'):
    """9 m concrete pole, two crossarms, a transformer drum and a bundle of dead-ending cable. The thing
    that makes a Japanese street photograph instantly recognisable."""
    b = B(seed=55)
    b.tube((0, 0, 0), 9.0, 0.14, 'MS_CityConcrete', n=8, c=0.95)
    for z, L in ((7.1, 1.5), (8.1, 1.1)):
        b.box((-L, -0.05, z), (L, 0.05, z + 0.1), 'MS_CityTrim', 0.5)
        for sx in (-L + 0.1, 0.0, L - 0.1):
            b.tube((sx, 0, z + 0.1), 0.22, 0.035, 'MS_CityMetal', n=6, c=0.7)          # insulators
    b.tube((0.22, 0, 5.6), 0.9, 0.26, 'MS_CityMetal', n=10, c=0.8)                     # transformer
    b.box((-0.18, -0.2, 3.2), (0.18, 0.2, 4.4), 'MS_CityTrim', 0.4)                    # boxes and meters
    for i in range(5):                                                                  # cable bundle hanging off
        z = 6.4 + i * 0.14
        b.box((-0.02, -0.02, z), (0.02, 0.02, z + 0.02), 'MS_CityTrim', 0.3)
    b.tube((0, 0, 0), 0.28, 0.24, 'MS_CityConcrete', n=8, c=0.85)                       # base collar
    return b.finish(name)


def build_cable_span(name='SM_CableSpan'):
    """A 10 m sag of four cables, to hang between two poles. Overhead cable is half of why a narrow lane
    reads as Tokyo rather than as a corridor - and it draws beautifully under an outline pass."""
    b = B(seed=56)
    L, sag, n = 10.0, 0.55, 12
    for k, (oy, oz) in enumerate([(-0.18, 0.0), (-0.06, 0.06), (0.06, 0.0), (0.18, 0.06)]):
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            x0, x1 = -L / 2 + L * t0, -L / 2 + L * t1
            z0 = -sag * math.sin(math.pi * t0) + oz
            z1 = -sag * math.sin(math.pi * t1) + oz
            b.box((x0, oy - 0.016, z0 - 0.016), (x1, oy + 0.016, z1 + 0.016), 'MS_CityTrim', 0.3)
    return b.finish(name)


def build_street_lamp(name='SM_StreetLamp'):
    b = B(seed=57)
    b.tube((0, 0, 0), 0.25, 0.14, 'MS_CityConcrete', n=8, c=0.9)
    b.tube((0, 0, 0.25), 5.2, 0.075, 'MS_CityTrim', n=8, c=0.5)
    for i in range(5):                                                                  # the curved head
        t0, t1 = i / 5, (i + 1) / 5
        b.box((-0.06 - 1.2 * t0, -0.06, 5.45 + 0.45 * math.sin(t0 * math.pi / 2)),
              (-0.06 - 1.2 * t1, 0.06, 5.5 + 0.45 * math.sin(t1 * math.pi / 2)), 'MS_CityTrim', 0.5)
    b.box((-1.55, -0.16, 5.78), (-0.95, 0.16, 5.9), 'MS_CityTrim', 0.45)
    b.quad([(-1.5, -0.13, 5.78), (-1.0, -0.13, 5.78), (-1.0, 0.13, 5.78), (-1.5, 0.13, 5.78)], 'MS_CitySignA', 1.0)
    return b.finish(name)


def build_traffic_cone(name='SM_TrafficCone'):
    b = B(seed=58)
    b.box((-0.19, -0.19, 0), (0.19, 0.19, 0.035), 'MS_CityAccent', 0.9)
    for i in range(5):
        t0, t1 = i / 5, (i + 1) / 5
        r0, r1 = 0.125 * (1 - t0) + 0.028, 0.125 * (1 - t1) + 0.028
        b.tube((0, 0, 0.035 + 0.6 * t0), 0.6 / 5, (r0 + r1) / 2, 'MS_CityAccent',
               n=8, c=0.95 if i in (1, 3) else 0.55)
    return b.finish(name)


def build_bollard(name='SM_Bollard'):
    b = B(seed=59)
    b.tube((0, 0, 0), 0.86, 0.055, 'MS_CityMetal', n=8, c=0.85)
    b.tube((0, 0, 0.86), 0.06, 0.07, 'MS_CityAccent', n=8, c=0.95)
    b.tube((0, 0, 0.56), 0.1, 0.062, 'MS_CityAccent', n=8, c=0.95)
    return b.finish(name)


def build_barrier(name='SM_Barrier'):
    """A 2 m A-frame roadworks barrier. Says 'this street is mid-repair', which beat 4 needs it to."""
    b = B(seed=60)
    w = 2.0
    for sy in (-0.3, 0.3):
        for sx in (-w / 2 + 0.1, w / 2 - 0.16):
            b.box((sx, sy - 0.03, 0), (sx + 0.06, sy + 0.03, 1.0), 'MS_CityTrim', 0.5)
    b.box((-w / 2, -0.06, 0.68), (w / 2, 0.06, 0.96), 'MS_CityAccent', 0.95)
    for i in range(6):
        bx = -w / 2 + i * w / 6
        b.box((bx, -0.07, 0.68), (bx + w / 12, 0.07, 0.96), 'MS_CityAccent', 0.5)
    b.box((-w / 2 + 0.2, -0.05, 0.3), (w / 2 - 0.2, 0.05, 0.42), 'MS_CityAccent', 0.8)
    return b.finish(name)


def build_crate_stack(name='SM_CrateStack'):
    b = B(seed=61)
    rng = random.Random(61)
    for i, (x, y, z, s) in enumerate([(0, 0, 0, 0.52), (0.56, 0.04, 0, 0.48), (0.06, 0.1, 0.52, 0.44),
                                      (0.58, -0.02, 0.48, 0.4)]):
        b.box((x, y, z), (x + s, y + s * 0.9, z + s * 0.85), 'MS_CityWood', rng.uniform(0.75, 1.0))
        b.box((x + 0.03, y - 0.015, z + s * 0.3), (x + s - 0.03, y, z + s * 0.45), 'MS_CityTrim', 0.4)
    return b.finish(name)


def build_trash_bags(name='SM_TrashBags'):
    b = B(seed=62)
    rng = random.Random(62)
    for _ in range(7):
        x, y = rng.gauss(0, 0.32), rng.gauss(0, 0.26)
        r = rng.uniform(0.17, 0.27)
        b.tube((x, y, 0), r * 1.5, r, 'MS_CityCloth', n=7, c=rng.uniform(0.25, 0.45))
        b.tube((x, y, r * 1.5), r * 0.35, r * 0.45, 'MS_CityCloth', n=6, c=rng.uniform(0.25, 0.45))
    b.box((-0.6, -0.5, 0), (0.6, 0.5, 0.02), 'MS_CityConcrete', 0.8)
    return b.finish(name)


def build_planter(name='SM_Planter'):
    b = B(seed=63)
    rng = random.Random(63)
    w, d, h = 1.20, 0.50, 0.62
    b.box((-w / 2, -d / 2, 0), (w / 2, d / 2, h), 'MS_CityConcrete', 0.95, skip=('zhi',))
    b.box((-w / 2 + 0.07, -d / 2 + 0.07, h - 0.1), (w / 2 - 0.07, d / 2 - 0.07, h - 0.04), 'MS_CityWood', 0.5)
    for _ in range(11):                                     # a shrub, as crossed cards
        px, py = rng.uniform(-w / 2 + 0.15, w / 2 - 0.15), rng.uniform(-d / 2 + 0.1, d / 2 - 0.1)
        ph = rng.uniform(0.3, 0.62)
        b.quad([(px - 0.18, py, h - 0.06), (px + 0.18, py, h - 0.06), (px + 0.18, py, h - 0.06 + ph),
                (px - 0.18, py, h - 0.06 + ph)], 'MS_CityCloth', rng.uniform(0.5, 0.85))
        b.quad([(px, py - 0.18, h - 0.06), (px, py + 0.18, h - 0.06), (px, py + 0.18, h - 0.06 + ph),
                (px, py - 0.18, h - 0.06 + ph)], 'MS_CityCloth', rng.uniform(0.5, 0.85))
    return b.finish(name)


def build_bicycle(name='SM_Bicycle'):
    """A city bike to lean against a wall. Low-poly on purpose: in silhouette under an outline pass, two
    wheels and a frame is all a bicycle has ever needed."""
    b = B(seed=64)
    for wx in (-0.52, 0.52):
        b.tube((wx, 0, 0.335), 0.035, 0.335, 'MS_CityTrim', n=14, c=0.35, axis='y')
        b.tube((wx, 0.012, 0.335), 0.012, 0.055, 'MS_CityMetal', n=8, c=0.8, axis='y')
        for k in range(6):                                  # spokes
            a = math.pi * k / 6
            b.box((wx - 0.325 * math.cos(a), -0.004, 0.335 - 0.325 * math.sin(a)),
                  (wx + 0.325 * math.cos(a), 0.004, 0.335 + 0.325 * math.sin(a)), 'MS_CityMetal', 0.7)
    for (a, bb) in [((-0.52, 0.335), (0.0, 0.62)), ((0.0, 0.62), (0.3, 0.42)), ((0.3, 0.42), (-0.52, 0.335)),
                    ((0.3, 0.42), (0.52, 0.72)), ((0.0, 0.62), (0.3, 0.9)), ((0.3, 0.42), (0.52, 0.335))]:
        b.box((min(a[0], bb[0]), -0.022, min(a[1], bb[1])), (max(a[0], bb[0]) + 0.03, 0.022,
              min(a[1], bb[1]) + 0.045), 'MS_CityAccent', 0.85)
        b.box((max(a[0], bb[0]) - 0.03, -0.022, min(a[1], bb[1])), (max(a[0], bb[0]), 0.022,
              max(a[1], bb[1])), 'MS_CityAccent', 0.85)
    b.box((0.52, -0.26, 0.98), (0.6, 0.26, 1.03), 'MS_CityTrim', 0.4)                 # handlebars
    b.box((0.2, -0.07, 0.86), (0.42, 0.07, 0.92), 'MS_CityTrim', 0.3)                 # saddle
    b.box((-0.66, -0.13, 0.66), (-0.3, 0.13, 0.72), 'MS_CityMetal', 0.7)              # rear rack
    b.box((-0.62, -0.18, 0.72), (-0.34, 0.18, 0.95), 'MS_CityCloth', 0.6)             # a basket of something
    return b.finish(name)


def build_noren(name='SM_Noren'):
    """A split cloth hung in a shop doorway. Four panels, so it reads as cloth and not as a board."""
    b = B(seed=65)
    w, h = 1.5, 0.95
    b.tube((-w / 2, 0, h + 0.03), w, 0.025, 'MS_CityWood', n=6, c=0.8, axis='x')
    for i in range(4):
        px = -w / 2 + 0.03 + i * (w - 0.06) / 4
        b.quad([(px, 0, h), (px + (w - 0.06) / 4 - 0.035, 0, h),
                (px + (w - 0.06) / 4 - 0.035, 0, 0.0), (px, 0, 0.0)], 'MS_CityCloth', 0.85)
        b.quad([(px + (w - 0.06) / 4 - 0.035, 0.012, h), (px, 0.012, h),
                (px, 0.012, 0.0), (px + (w - 0.06) / 4 - 0.035, 0.012, 0.0)], 'MS_CityCloth', 0.8)
    return b.finish(name)


def build_awning(name='SM_Awning'):
    """A generic 3 m shop awning, underside clear at 2.4 m."""
    b = B(seed=66)
    w, pr = 3.0, 1.1
    for sx in (-w / 2 + 0.08, w / 2 - 0.08):
        b.box((sx - 0.035, 0, 2.42), (sx + 0.035, pr, 2.46), 'MS_CityTrim', 0.5)
        b.box((sx - 0.035, pr - 0.07, 2.46), (sx + 0.035, pr, 2.95), 'MS_CityTrim', 0.5)
    b.quad([(-w / 2, 0, 2.95), (w / 2, 0, 2.95), (w / 2, pr, 2.46), (-w / 2, pr, 2.46)], 'MS_CityCloth', 0.9)
    for i in range(8):
        vx = -w / 2 + w * i / 8
        b.quad([(vx, pr, 2.46), (vx + w / 8, pr, 2.46), (vx + w / 8, pr, 2.22), (vx, pr, 2.22)],
               'MS_CityCloth', 0.72 if i % 2 else 0.9)
    return b.finish(name)


def build_roof_tank(name='SM_RoofTank'):
    """The New York timber water tank, on its own so it can be dropped on any roof."""
    b = B(seed=67)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            b.box((sx - 0.09, sy - 0.09, 0), (sx + 0.09, sy + 0.09, 2.0), 'MS_CityWood', 0.8)
    for z in (0.6, 1.5):
        b.box((-1.1, -1.1, z), (1.1, -1.0, z + 0.08), 'MS_CityWood', 0.7)
        b.box((-1.1, 1.0, z), (1.1, 1.1, z + 0.08), 'MS_CityWood', 0.7)
    b.tube((0, 0, 2.0), 2.7, 1.35, 'MS_CityWood', n=12, c=0.9)
    for z in (2.3, 3.4, 4.4):
        b.tube((0, 0, z), 0.09, 1.38, 'MS_CityMetal', n=12, c=0.75)
    b.tube((0, 0, 4.7), 0.55, 1.1, 'MS_CityMetal', n=12, c=0.8)
    b.tube((0, 0, 5.25), 0.3, 0.45, 'MS_CityMetal', n=8, c=0.8)
    return b.finish(name)


def build_manhole(name='SM_Manhole'):
    b = B(seed=68)
    b.tube((0, 0, 0.0), 0.025, 0.36, 'MS_CityMetal', n=16, c=0.7)
    b.tube((0, 0, 0.025), 0.012, 0.3, 'MS_CityMetal', n=16, c=0.6)
    return b.finish(name)


def build_bench(name='SM_Bench'):
    b = B(seed=69)
    w = 1.8
    for sx in (-w / 2 + 0.16, w / 2 - 0.22):
        b.box((sx, -0.24, 0), (sx + 0.06, 0.24, 0.42), 'MS_CityTrim', 0.5)
        b.box((sx, 0.18, 0.42), (sx + 0.06, 0.24, 0.86), 'MS_CityTrim', 0.5)
    for i in range(4):
        b.box((-w / 2, -0.24 + i * 0.13, 0.42), (w / 2, -0.24 + i * 0.13 + 0.1, 0.47), 'MS_CityWood', 0.85)
    for i in range(3):
        b.box((-w / 2, 0.2, 0.56 + i * 0.11), (w / 2, 0.24, 0.56 + i * 0.11 + 0.08), 'MS_CityWood', 0.85)
    return b.finish(name)


def build_kerb(name='SM_Kerb'):
    """An 8 m kerb and pavement strip. The one piece that actually makes a flat floor read as a road."""
    b = B(seed=70)
    L = 8.0
    b.box((-L / 2, 0.0, 0), (L / 2, 2.4, 0.14), 'MS_CityConcrete', 0.95)        # pavement
    b.box((-L / 2, -0.16, 0), (L / 2, 0.0, 0.16), 'MS_CityConcrete', 1.0)       # kerb stone
    for i in range(int(L / 0.9)):                                               # flag joints
        jx = -L / 2 + i * 0.9
        b.box((jx, 0.02, 0.14), (jx + 0.02, 2.38, 0.15), 'MS_CityConcrete', 0.8)
    b.box((-L / 2, 1.2, 0.14), (L / 2, 1.22, 0.15), 'MS_CityConcrete', 0.8)
    return b.finish(name)


# =========================================================================== SET PIECES (beats 1 to 3)
# Made Fri Nov 13 (evening) to take the last grey boxes out of everything up to and including the cleaver boss:
# the crashed car (two red boxes), the shrapnel (a red bar), the boss lot's six walls, the exit run's two
# walls, both plaza gates (a scaled cube), the checkpoint (a post and a green sign) and the ground itself.
# Same rules as the rest of the kit: real scale, flat MS_City* slots, detail in geometry, no trademarks.
# Every wall and the gate keep the EXACT footprint of the grey box they replace, because the fight was tuned
# inside those boxes and a prettier wall that is 20 cm further in is a different arena.

def hexa(b, bot, top, slot, c=1.0):
    """A six-sided solid from two rings of four points. bot and top go round the same way: anticlockwise seen
    from above, starting at the low-x low-y corner - the order B.box uses, so the faces point outwards."""
    for i in range(4):
        j = (i + 1) % 4
        b.quad([bot[i], bot[j], top[j], top[i]], slot, c)
    b.quad([top[0], top[1], top[2], top[3]], slot, c)
    b.quad([bot[0], bot[3], bot[2], bot[1]], slot, c)


def _slice(b, x0, z00, z01, hw0, x1, z10, z11, hw1, slot, c=1.0):
    """One length of car body between two stations: (x, z bottom, z top, half width) at each end."""
    hexa(b, [(x0, -hw0, z00), (x1, -hw1, z10), (x1, hw1, z10), (x0, hw0, z00)],
         [(x0, -hw0, z01), (x1, -hw1, z11), (x1, hw1, z11), (x0, hw0, z01)], slot, c)


def build_crash_car(name='SM_CrashCar'):
    """The car that came through the cafe wall. Replaces C1_Cafe_Car and C1_Cafe_CarCab.

    4.0 x 1.76 x 1.43 m, standing on its origin, NOSE TOWARDS +X - it came down the avenue from the west and
    stopped inside the room. It stays inside the 4 x 2 m footprint of the red box it replaces, so the level's
    measured clear routes are unchanged. Right-hand drive, like the lane it crashed in: the driver's door is
    open on the Unreal +Y side, because that is the side the driver's body lies on, at (-380, 220), and a door
    hanging open next to a body is the whole story of beat 1 told without a word.
    """
    b = B(seed=81)
    P, G, T, M = 'MS_CityAccent', 'MS_CityGlass', 'MS_CityTrim', 'MS_CityMetal'
    # ---- lower body, tail to nose. The nose is short: the crash ate half a metre of it.
    st = [(-1.98, 0.34, 0.80, 0.80), (-1.80, 0.30, 0.90, 0.86), (-1.00, 0.30, 0.92, 0.88),
          (0.55, 0.30, 0.90, 0.88), (1.05, 0.30, 0.76, 0.87), (1.42, 0.32, 0.80, 0.84),
          (1.62, 0.36, 0.66, 0.80), (1.74, 0.40, 0.56, 0.72)]
    for (x0, a0, a1, w0), (x1, c0, c1, w1) in zip(st, st[1:]):
        _slice(b, x0, a0, a1, w0, x1, c0, c1, w1, P, 1.0)
    b.box((-1.80, -0.80, 0.18), (1.55, 0.80, 0.30), T, 0.4)                               # floor pan
    # ---- the glasshouse: one glass block, then a painted roof and pillars over it
    gs = [(-1.40, 0.90, 0.93, 0.82), (-0.90, 0.90, 1.39, 0.67), (0.00, 0.90, 1.39, 0.67), (0.60, 0.90, 0.93, 0.82)]
    for (x0, a0, a1, w0), (x1, c0, c1, w1) in zip(gs, gs[1:]):
        _slice(b, x0, a0, a1, w0, x1, c0, c1, w1, G, 0.6)
    b.box((-0.94, -0.70, 1.38), (0.04, 0.70, 1.43), P, 1.0)                               # roof
    for sy in (-1.0, 1.0):
        def pillar(xb0, xb1, xt0, xt1):
            yb0, yb1 = sorted((sy * 0.775, sy * 0.835))
            yt0, yt1 = sorted((sy * 0.63, sy * 0.69))
            hexa(b, [(xb0, yb0, 0.90), (xb1, yb0, 0.90), (xb1, yb1, 0.90), (xb0, yb1, 0.90)],
                 [(xt0, yt0, 1.41), (xt1, yt0, 1.41), (xt1, yt1, 1.41), (xt0, yt1, 1.41)], P, 0.95)
        pillar(0.50, 0.63, -0.08, 0.04)                                                   # A
        pillar(-0.46, -0.37, -0.46, -0.37)                                                # B
        pillar(-1.43, -1.25, -0.94, -0.80)                                                # C
    # ---- the bonnet, sprung open on its hinges over a crushed engine bay
    hexa(b, [(0.56, -0.78, 0.91), (1.36, -0.76, 1.19), (1.36, 0.76, 1.25), (0.56, 0.78, 0.91)],
         [(0.55, -0.78, 0.94), (1.35, -0.76, 1.22), (1.35, 0.76, 1.28), (0.55, 0.78, 0.94)], P, 0.92)
    b.box((0.70, -0.55, 0.76), (1.30, 0.45, 0.90), T, 0.35)                               # engine, dark
    b.box((0.85, -0.30, 0.90), (1.15, 0.10, 0.97), M, 0.8)
    # ---- bumpers and lamps. The front bumper hangs off one corner.
    b.box((-2.02, -0.84, 0.32), (-1.92, 0.84, 0.54), T, 0.45)
    hexa(b, [(1.70, -0.82, 0.38), (1.82, -0.82, 0.38), (1.86, 0.80, 0.06), (1.74, 0.80, 0.06)],
         [(1.70, -0.82, 0.54), (1.82, -0.82, 0.54), (1.86, 0.80, 0.22), (1.74, 0.80, 0.22)], T, 0.45)
    b.box((1.735, -0.68, 0.46), (1.765, -0.40, 0.56), 'MS_CitySignA', 1.0)                # the lamp still lit
    b.box((1.735, 0.40, 0.46), (1.76, 0.68, 0.56), T, 0.3)                                # the one that is not
    for sy in (-1.0, 1.0):
        y0, y1 = sorted((sy * 0.48, sy * 0.80))
        b.box((-2.00, y0, 0.62), (-1.965, y1, 0.74), 'MS_CitySignA', 0.9)                 # tail lamps
    b.box((-2.005, -0.26, 0.40), (-1.99, 0.26, 0.52), 'MS_CityWall', 0.9)                 # a blank plate
    # ---- wheels: 62 cm, the front pair shoved back by the impact
    for wx in (-1.22, 1.08):
        for sy in (-1.0, 1.0):
            y = 0.70 if sy > 0 else -0.90
            b.tube((wx, y, 0.31), 0.20, 0.31, T, n=12, c=0.3, axis='y')
            b.tube((wx, y - 0.01 if sy < 0 else y + 0.19, 0.31), 0.02, 0.17, M, n=10, c=0.9, axis='y')
    # ---- the driver's door, open. Blender -Y is Unreal +Y, the side his body is on.
    hx, hy, ang, dl, dt = 0.50, -0.88, math.radians(55), 1.00, 0.06
    ux, uy = -math.cos(ang), -math.sin(ang)             # along the door, hinge to latch
    nx, ny = -uy, ux                                    # across its thickness
    def door(z0, z1, slot, c, l0=0.0, l1=dl, t=dt):
        p = [(hx + ux * l0, hy + uy * l0), (hx + ux * l1, hy + uy * l1),
             (hx + ux * l1 + nx * t, hy + uy * l1 + ny * t), (hx + ux * l0 + nx * t, hy + uy * l0 + ny * t)]
        ring = [p[1], p[0], p[3], p[2]]
        hexa(b, [(q[0], q[1], z0) for q in ring], [(q[0], q[1], z1) for q in ring], slot, c)
    door(0.33, 0.90, P, 0.95)
    door(0.90, 1.34, T, 0.5, 0.0, 0.05)                                                   # window frame
    door(0.90, 1.34, T, 0.5, dl - 0.05, dl)
    door(1.30, 1.34, T, 0.5)
    door(0.90, 1.30, G, 0.55, 0.05, dl - 0.05, 0.02)
    b.box((-0.50, -0.885, 0.34), (0.50, -0.86, 0.89), T, 0.2)                             # the doorway, dark
    b.box((-0.30, -0.80, 0.42), (0.18, -0.40, 0.56), 'MS_CityCloth', 0.6)                 # the seat he left
    return b.finish(name)


def build_shrapnel(name='SM_Shrapnel'):
    """What flies at the coworker in beat 1: a torn strip of the car's own bodywork, 78 cm long.

    Long axis on X, centred on its origin so it can spin about its middle. BP_Shrapnel is 'a red bar' today;
    this is the same thing with a shape - red paint outside, bare metal where it tore, jagged at both ends,
    so that when Freeze Frame stops it in mid-air there is something worth looking at.
    """
    b = B(seed=82)
    P, M = 'MS_CityAccent', 'MS_CityMetal'
    # a twisted strip in three lengths: each station is (x, y centre, z centre, half width, roll in degrees)
    st = [(-0.26, 0.00, 0.00, 0.10, -28), (-0.08, 0.02, 0.02, 0.13, -8), (0.10, -0.01, 0.03, 0.12, 16),
          (0.27, 0.01, -0.01, 0.08, 40)]
    t = 0.012

    def ring(s, dz):
        x, y, z, hw, roll = s
        r = math.radians(roll)
        cy, cz = math.cos(r), math.sin(r)
        return [(x, y - hw * cy - dz * cz, z - hw * cz + dz * cy), (x, y + hw * cy - dz * cz, z + hw * cz + dz * cy)]

    for s0, s1 in zip(st, st[1:]):
        a0, a1 = ring(s0, -t), ring(s0, t)
        c0, c1 = ring(s1, -t), ring(s1, t)
        b.quad([a1[0], c1[0], c1[1], a1[1]], P, 0.95)                                     # painted face
        b.quad([a0[1], c0[1], c0[0], a0[0]], M, 0.7)                                      # torn bare back
        b.quad([a0[0], c0[0], c1[0], a1[0]], M, 0.9)
        b.quad([a1[1], c1[1], c0[1], a0[1]], M, 0.9)
    # jagged ends: bare metal teeth, wound both ways because the shard spins and Unreal culls back faces
    for s, d in ((st[0], -1.0), (st[-1], 1.0)):
        e0, e1 = ring(s, 0.0)
        mid = ((e0[0] + e1[0]) / 2, (e0[1] + e1[1]) / 2, (e0[2] + e1[2]) / 2)
        for k, (f0, f1, ln) in enumerate(((0.0, 0.45, 0.13), (0.4, 0.75, 0.07), (0.7, 1.0, 0.11))):
            p0 = tuple(e0[i] + (e1[i] - e0[i]) * f0 for i in range(3))
            p1 = tuple(e0[i] + (e1[i] - e0[i]) * f1 for i in range(3))
            tip = ((p0[0] + p1[0]) / 2 + d * ln, (p0[1] + p1[1]) / 2 + 0.02 * (k - 1), (p0[2] + p1[2]) / 2)
            b.quad([p0, p1, tip], M, 0.85)
            b.quad([p1, p0, tip], M, 0.7)         # same slot both ways: two materials on one plane z-fight
        _ = mid
    # a bent bracket still riveted to it, so it does not read as a ruler
    b.box((-0.05, -0.03, 0.02), (0.02, 0.03, 0.10), M, 0.75)
    b.box((-0.05, -0.03, 0.09), (0.09, 0.03, 0.105), M, 0.8)
    return b.finish(name, weld=False)


YARD_T = 0.40          # the plaza's grey walls are 40 cm thick and 4 m high: these are too
YARD_H = 4.00


def _yard_wall(b, L):
    """A brick yard wall L metres long, centred on its origin, standing on z = 0, body on y = -0.2..0.2.

    The dressed face is Blender -Y (Unreal +Y at yaw 0), the same way every building in this kit faces, so
    the layout turns it towards the arena with the yaws it already uses. Nothing on that face stands more
    than 15 cm proud of the wall, because the arena's keep-clear box starts 40 cm inside the wall line.
    The outside face gets piers and a coping and nothing else: nobody ever stands on that side.
    """
    rng = b.rng
    t, H = YARD_T / 2, YARD_H
    BR, CO, TR, ME = 'MS_CityBrick', 'MS_CityConcrete', 'MS_CityTrim', 'MS_CityMetal'
    b.box((-L / 2, -t, 0.5), (L / 2, t, H - 0.2), BR, 1.0)
    b.box((-L / 2, -t - 0.04, 0), (L / 2, t + 0.04, 0.5), CO, 0.9)                        # plinth
    b.box((-L / 2, -t - 0.06, H - 0.2), (L / 2, t + 0.06, H), CO, 1.0)                    # coping
    nb = max(2, int(round(L / 3.1)))
    bay = L / nb
    for i in range(nb + 1):                                                               # piers
        px = -L / 2 + i * bay
        x0, x1 = max(-L / 2, px - 0.28), min(L / 2, px + 0.28)
        b.box((x0, -t - 0.10, 0.5), (x1, t + 0.08, H - 0.2), BR, 0.88)
        b.box((x0 - 0.0, -t - 0.13, H - 0.32), (x1, t + 0.10, H - 0.2), CO, 0.95)
    kinds = ['shutter', 'posters', 'window', 'lamp', 'sign', 'window', 'shutter', 'posters', 'lamp', 'sign']
    for i in range(nb):
        cx = -L / 2 + (i + 0.5) * bay
        kind = kinds[(i + b.rng.randrange(2)) % len(kinds)] if nb > 4 else kinds[i % len(kinds)]
        f = -t                                           # the wall face; everything below sits just proud of it
        if kind == 'shutter':                            # a roller shutter: the yard's back doors
            w, h = min(2.2, bay - 0.9), 2.7
            b.box((cx - w / 2 - 0.08, f - 0.06, 0.5), (cx + w / 2 + 0.08, f, 0.5 + h + 0.3), TR, 0.5)
            b.box((cx - w / 2, f - 0.075, 0.5), (cx + w / 2, f - 0.02, 0.5 + h), ME, 0.85)
            for k in range(int(h / 0.22)):
                b.box((cx - w / 2, f - 0.088, 0.56 + k * 0.22), (cx + w / 2, f - 0.07, 0.60 + k * 0.22), ME, 0.6)
            b.box((cx - w / 2, f - 0.10, 0.5), (cx + w / 2, f - 0.02, 0.62), 'MS_CityAccent', 0.9)
        elif kind == 'posters':                          # fly-posters: blank paper, no words (section 15d)
            x = cx - bay / 2 + 0.55
            while x < cx + bay / 2 - 1.0:
                w, h = rng.uniform(0.5, 0.8), rng.uniform(0.7, 1.1)
                z0 = rng.uniform(1.0, 1.6)
                slot = rng.choice(['MS_CityCloth', 'MS_CityWall', 'MS_CitySignB', 'MS_CityCloth'])
                b.box((x, f - 0.015, z0), (x + w, f, z0 + h), slot, rng.uniform(0.7, 1.0))
                b.box((x + 0.08, f - 0.02, z0 + h * 0.55), (x + w - 0.08, f, z0 + h - 0.08), 'MS_CityAccent', 0.8)
                x += w + rng.uniform(0.06, 0.3)
        elif kind == 'window':                           # a barred window, high up
            w, h, z0 = 1.5, 1.0, 2.25
            b.box((cx - w / 2 - 0.07, f - 0.05, z0 - 0.07), (cx + w / 2 + 0.07, f, z0 + h + 0.07), CO, 0.95)
            b.box((cx - w / 2, f - 0.06, z0), (cx + w / 2, f - 0.02, z0 + h), 'MS_CityGlass', rng.uniform(0.4, 0.8))
            for k in range(6):
                bx = cx - w / 2 + (k + 0.5) * w / 6
                b.box((bx - 0.015, f - 0.09, z0), (bx + 0.015, f - 0.06, z0 + h), TR, 0.4)
            b.box((cx - w / 2 - 0.12, f - 0.12, z0 - 0.13), (cx + w / 2 + 0.12, f, z0 - 0.07), CO, 1.0)
        elif kind == 'lamp':                             # a bulkhead lamp over a service box
            b.box((cx - 0.05, f - 0.12, 3.02), (cx + 0.05, f, 3.10), TR, 0.5)
            b.box((cx - 0.16, f - 0.15, 2.84), (cx + 0.16, f - 0.03, 3.02), 'MS_CitySignA', 1.0)
            b.box((cx - 0.19, f - 0.15, 3.02), (cx + 0.19, f - 0.02, 3.05), TR, 0.5)
            b.box((cx + 0.5, f - 0.12, 0.9), (cx + 1.05, f, 1.75), ME, 0.75)
            b.box((cx + 0.53, f - 0.13, 1.25), (cx + 1.02, f - 0.12, 1.29), TR, 0.4)
            b.tube((cx + 0.78, f - 0.05, 1.75), H - 0.2 - 1.75, 0.03, ME, n=6, c=0.7)
        else:                                            # a lit sign panel, blank
            w, h, z0 = min(2.0, bay - 1.0), 0.9, 2.5
            b.box((cx - w / 2 - 0.05, f - 0.07, z0 - 0.05), (cx + w / 2 + 0.05, f, z0 + h + 0.05), TR, 0.45)
            b.box((cx - w / 2, f - 0.085, z0), (cx + w / 2, f - 0.06, z0 + h),
                  rng.choice(['MS_CitySignA', 'MS_CitySignB']), 1.0)
            for k in range(3):                           # an invented glyph block, not a word
                gx = cx - w / 2 + 0.2 + k * (w - 0.4) / 3
                b.box((gx, f - 0.095, z0 + 0.2), (gx + (w - 0.4) / 3 - 0.12, f - 0.085, z0 + h - 0.2),
                      'MS_CityTrim', 0.3)


def build_yard_wall_1250(name='SM_YardWall_1250'):
    """12.5 m. Replaces each of the four short plaza walls either side of the two gates."""
    b = B(seed=83)
    _yard_wall(b, 12.50)
    return b.finish(name)


def build_yard_wall_3040(name='SM_YardWall_3040'):
    """30.4 m. Replaces C1_Plaza_WallN and C1_Plaza_WallS."""
    b = B(seed=84)
    _yard_wall(b, 30.40)
    return b.finish(name)


def build_hoarding_990(name='SM_Hoarding_990'):
    """9.9 m of site hoarding, 4 m high, 30 cm deep at its base. Replaces C1_Run_WallN and C1_Run_WallS.

    The run past the exit gate leads to beat 4's destroyed buildings, so the wall that funnels you there is
    the fence round a demolition site. Dressed on both faces: the player runs between two of them.
    """
    b = B(seed=85)
    L, H = 9.90, 4.00
    CO, TR, ME = 'MS_CityConcrete', 'MS_CityTrim', 'MS_CityMetal'
    hexa(b, [(-L / 2, -0.15, 0), (L / 2, -0.15, 0), (L / 2, 0.15, 0), (-L / 2, 0.15, 0)],
         [(-L / 2, -0.09, 0.62), (L / 2, -0.09, 0.62), (L / 2, 0.09, 0.62), (-L / 2, 0.09, 0.62)], CO, 0.95)
    b.box((-L / 2, -0.03, 0.62), (L / 2, 0.03, H - 0.06), ME, 0.8)                        # the sheet
    n = int(L / 0.30)
    for k in range(n):                                                                    # corrugation
        x = -L / 2 + (k + 0.5) * L / n
        c = 0.9 if k % 2 else 0.68
        b.box((x - 0.05, -0.05, 0.62), (x + 0.05, 0.05, H - 0.06), ME, c)
    for k in range(5):                                                                    # posts
        x = -L / 2 + 0.06 + k * (L - 0.12) / 4
        b.box((x - 0.06, -0.075, 0.0), (x + 0.06, 0.075, H), TR, 0.5)
    b.box((-L / 2, -0.065, H - 0.10), (L / 2, 0.065, H), TR, 0.5)                         # top rail
    b.box((-L / 2, -0.06, 2.3), (L / 2, 0.06, 2.38), TR, 0.5)
    nb = 22
    for k in range(nb):                                                                   # hazard band
        x0 = -L / 2 + k * L / nb
        b.box((x0, -0.068, 1.05), (x0 + L / nb, 0.068, 1.33),
              'MS_CityAccent' if k % 2 else 'MS_CityWall', 0.95)
    return b.finish(name)


def build_plaza_gate(name='SM_PlazaGate'):
    """The plaza's roller gate: 0.4 x 5 x 4 m, exactly the scaled cube in BP_PlazaGate.

    ORIGIN AT ITS CENTRE, thin on X and wide on Y - unlike everything else in this kit - because that is how
    the cube it replaces sits: BP_PlazaGate is placed at z = 200 and slides GateMesh up by GateOpenHeight.
    Swap the mesh, set GateMesh's scale back to 1, and nothing about the gate's logic or placement moves.
    Dressed on both faces: the player sees one going in and the other when it shuts behind him.
    """
    b = B(seed=86)
    TR, ME = 'MS_CityTrim', 'MS_CityMetal'
    for sy in (-1.0, 1.0):                                                                # the two guides
        y0, y1 = sorted((sy * 2.28, sy * 2.50))
        b.box((-0.20, y0, -2.0), (0.20, y1, 2.0), TR, 0.5)
    b.box((-0.20, -2.50, 1.55), (0.20, 2.50, 2.0), ME, 0.75)                              # the roll housing
    b.box((-0.215, -2.50, 1.52), (0.215, 2.50, 1.58), TR, 0.45)
    b.box((-0.07, -2.28, -1.78), (0.07, 2.28, 1.55), ME, 0.85)                            # the curtain
    for k in range(13):                                                                   # slats
        z = -1.70 + k * 0.25
        b.box((-0.085, -2.28, z), (0.085, 2.28, z + 0.05), ME, 0.6)
    for k in range(10):                                                                   # hazard bottom bar
        y0 = -2.28 + k * 0.456
        b.box((-0.10, y0, -2.0), (0.10, y0 + 0.456, -1.78), 'MS_CityAccent' if k % 2 else 'MS_CityTrim', 0.9)
    for sx in (-1.0, 1.0):                                                                # a warning lamp each face
        x0, x1 = sorted((sx * 0.20, sx * 0.235))
        b.box((x0, -0.5, 1.70), (x1, 0.5, 1.86), 'MS_CitySignA', 1.0)
    return b.finish(name)


def build_checkpoint_post(name='SM_CheckpointPost'):
    """BP_Checkpoint's PostMesh: a film-set light stand, 2.3 m, standing on its origin.

    The game is called Jump Cut and every power is an edit, so the thing that marks 'the take restarts here'
    is a piece of set equipment: a tripod stand carrying a small lamp head and a slate.
    """
    b = B(seed=87)
    TR, ME = 'MS_CityTrim', 'MS_CityMetal'
    for k in range(3):                                                                    # tripod feet
        a = math.radians(90 + k * 120)
        ex, ey = math.cos(a) * 0.55, math.sin(a) * 0.55
        px, py = -math.sin(a) * 0.022, math.cos(a) * 0.022
        hexa(b, [(ex - px, ey - py, 0.0), (ex + px, ey + py, 0.0), (ex * 0.9 + px, ey * 0.9 + py, 0.0),
                 (ex * 0.9 - px, ey * 0.9 - py, 0.0)],
             [(-px, -py, 0.62), (px, py, 0.62), (px, py, 0.68), (-px, -py, 0.68)], TR, 0.5)
    b.tube((0, 0, 0.40), 1.55, 0.028, ME, n=8, c=0.85)
    b.tube((0, 0, 0.60), 0.10, 0.045, TR, n=8, c=0.5)
    b.tube((0, 0, 1.30), 0.08, 0.04, TR, n=8, c=0.5)
    b.box((-0.03, -0.20, 1.93), (0.03, 0.20, 1.97), TR, 0.5)                              # yoke
    b.box((-0.16, -0.17, 1.97), (0.16, 0.17, 2.29), TR, 0.45)                             # lamp head
    b.box((-0.13, -0.19, 2.00), (0.13, -0.17, 2.26), 'MS_CitySignA', 1.0)                 # its lens
    for k in range(4):                                                                    # barn doors
        z = 2.00 + k * 0.07
        b.box((-0.15, -0.22, z), (0.15, -0.19, z + 0.015), TR, 0.4)
    # the slate, hung on the stand at chest height
    b.box((-0.24, -0.06, 1.02), (0.24, -0.04, 1.36), TR, 0.35)
    b.box((-0.24, -0.065, 1.36), (0.24, -0.035, 1.43), 'MS_CityWall', 0.95)
    for k in range(5):
        x0 = -0.24 + k * 0.096
        if k % 2 == 0:
            b.box((x0, -0.07, 1.36), (x0 + 0.096, -0.03, 1.43), TR, 0.3)
    for k in range(3):                                                                    # blank chalk lines
        b.box((-0.19, -0.066, 1.08 + k * 0.08), (0.19 - 0.1 * k, -0.06, 1.10 + k * 0.08), 'MS_CityWall', 0.9)
    return b.finish(name)


def build_checkpoint_taken(name='SM_CheckpointTaken'):
    """BP_Checkpoint's TakenSign: the same slate, shut and lit, with a tick on it. Shown once the take is saved.

    Centred on its origin (60 x 50 cm), facing Blender -Y. Its face is MS_CitySignB; if the builder would
    rather keep the checkpoint green, put M_CheckGreen on that one slot.
    """
    b = B(seed=88)
    TR = 'MS_CityTrim'
    b.box((-0.30, -0.02, -0.25), (0.30, 0.02, 0.17), TR, 0.35)
    b.box((-0.27, -0.035, -0.22), (0.27, -0.02, 0.14), 'MS_CitySignB', 1.0)
    b.box((-0.30, -0.03, 0.17), (0.30, 0.03, 0.25), 'MS_CityWall', 0.95)
    for k in range(6):
        if k % 2 == 0:
            b.box((-0.30 + k * 0.1, -0.035, 0.17), (-0.20 + k * 0.1, 0.035, 0.25), TR, 0.3)
    # the tick: a short stroke down to the corner, a long one up from it, each a 5 cm bar
    def stroke(x0, z0, x1, z1, w=0.03):
        dx, dz = x1 - x0, z1 - z0
        ln = math.hypot(dx, dz)
        px, pz = -dz / ln * w, dx / ln * w
        b.quad([(x0 - px, -0.045, z0 - pz), (x0 + px, -0.045, z0 + pz), (x1 + px, -0.045, z1 + pz),
                (x1 - px, -0.045, z1 - pz)], 'MS_CityWall', 1.0)
        b.quad([(x1 - px, -0.045, z1 - pz), (x1 + px, -0.045, z1 + pz), (x0 + px, -0.045, z0 + pz),
                (x0 - px, -0.045, z0 - pz)], 'MS_CityWall', 1.0)
    stroke(-0.17, -0.02, -0.06, -0.15)
    stroke(-0.08, -0.15, 0.17, 0.09)
    return b.finish(name)


def build_plaza_paving(name='SM_PlazaPaving'):
    """The boss lot's floor: 30 x 30 m of two-tone slabs inside a brick border, 1 cm above the level floor.

    Top faces only, and NO COLLISION in the level (the placer switches it off): it is a picture of a floor
    laid on the real one, so the fight's footing does not change by a millimetre. A ring is set into it at
    the centre, which is where the boss stands - the arena tells you where to look before he moves.
    """
    b = B(seed=89)
    S, z, n = 15.0, 0.010, 12
    step = 2 * (S - 0.9) / n

    def flat(x0, y0, x1, y1, slot, c=1.0, dz=0.0):
        b.quad([(x0, y0, z + dz), (x1, y0, z + dz), (x1, y1, z + dz), (x0, y1, z + dz)], slot, c)

    flat(-S, -S, S, -S + 0.9, 'MS_CityBrick')
    flat(-S, S - 0.9, S, S, 'MS_CityBrick')
    flat(-S, -S + 0.9, -S + 0.9, S - 0.9, 'MS_CityBrick')
    flat(S - 0.9, -S + 0.9, S, S - 0.9, 'MS_CityBrick')
    for i in range(n):
        for j in range(n):
            x0, y0 = -S + 0.9 + i * step, -S + 0.9 + j * step
            flat(x0, y0, x0 + step, y0 + step, 'MS_CityConcrete' if (i + j) % 2 else 'MS_CityWall',
                 0.9 if (i + j) % 2 else 1.0)
    seg = 28                                              # the ring, 2.6 m radius, laid just above the slabs
    for k in range(seg):
        a0, a1 = 2 * math.pi * k / seg, 2 * math.pi * (k + 1) / seg
        r0, r1 = 2.35, 2.75
        b.quad([(math.cos(a0) * r0, math.sin(a0) * r0, z + 0.004), (math.cos(a0) * r1, math.sin(a0) * r1, z + 0.004),
                (math.cos(a1) * r1, math.sin(a1) * r1, z + 0.004), (math.cos(a1) * r0, math.sin(a1) * r0, z + 0.004)],
               'MS_CityBrick', 0.9)
    return b.finish(name, weld=False)


def build_crosswalk(name='SM_Crosswalk'):
    """A zebra crossing, 3 m along the road by 5 m across it, painted 1 cm above the floor. No collision."""
    b = B(seed=90)
    for k in range(6):
        y0 = -2.225 + k * 0.80
        b.quad([(-1.5, y0, 0.01), (1.5, y0, 0.01), (1.5, y0 + 0.45, 0.01), (-1.5, y0 + 0.45, 0.01)],
               'MS_CityWall', 1.0)
    return b.finish(name, weld=False)


def build_road_lines(name='SM_RoadLines'):
    """8 m of the lane's painted edge lines, at y = +/-2.1 m, 1 cm above the floor. No collision.

    The lane is 4.9 m between kerb stones (they stand at y = +/-2.44), which in Tokyo is a street with no centre line and a solid line down
    each side to mark where people walk. Laid end to end it is what turns a floor into a road.
    """
    b = B(seed=91)
    for sy in (-1.0, 1.0):
        y0, y1 = sorted((sy * 2.05, sy * 2.17))
        b.quad([(-4.0, y0, 0.01), (4.0, y0, 0.01), (4.0, y1, 0.01), (-4.0, y1, 0.01)], 'MS_CityWall', 1.0)
    for k in range(4):                                    # worn dashes, off-centre: where the bikes go
        x0 = -3.6 + k * 2.0
        b.quad([(x0, -0.06, 0.01), (x0 + 0.9, -0.06, 0.01), (x0 + 0.9, 0.06, 0.01), (x0, 0.06, 0.01)],
               'MS_CityConcrete', 0.9)
    return b.finish(name, weld=False)


# =========================================================================== REGISTRY AND DRIVER
GROUPS = {
    'cafe': [
        ('SM_CafeShell', build_cafe_shell), ('SM_CafeCounter', build_cafe_counter),
        ('SM_CafeEspresso', build_cafe_espresso), ('SM_CafePastryCase', build_cafe_pastry_case),
        ('SM_CafeRegister', build_cafe_register),
        ('SM_CafeShelf', build_cafe_shelf), ('SM_CafeTable', build_cafe_table),
        ('SM_CafeChair', build_cafe_chair), ('SM_CafeAwning', build_cafe_awning),
        ('SM_CafeMenuBoard', build_cafe_menu_board), ('SM_CafeSign', build_cafe_sign),
    ],
    'city': [
        ('SM_ShopHouse_A', build_shophouse_a), ('SM_ShopHouse_B', build_shophouse_b),
        ('SM_ShopHouse_C', build_shophouse_c), ('SM_CornerBlock', build_corner_block),
        ('SM_BlockFiller', build_block_filler), ('SM_SetbackTower', build_setback_tower),
        ('SM_CurtainTower', build_curtain_tower), ('SM_PlazaTower', build_plaza_tower),
        ('SM_FireEscape', build_fire_escape),
    ],
    'ruins': [
        ('SM_RuinSlab_A', build_ruin_slab_a), ('SM_RuinSlab_B', build_ruin_slab_b),
        ('SM_RuinBeam', build_ruin_beam), ('SM_RuinWall', build_ruin_wall), ('SM_Rubble', build_rubble),
    ],
    'props': [
        ('SM_VendingMachine', build_vending_machine), ('SM_SignVertical', build_sign_vertical),
        ('SM_SignBlade', build_sign_blade), ('SM_ACUnit', build_ac_unit),
        ('SM_UtilityPole', build_utility_pole), ('SM_CableSpan', build_cable_span),
        ('SM_StreetLamp', build_street_lamp), ('SM_TrafficCone', build_traffic_cone),
        ('SM_Bollard', build_bollard), ('SM_Barrier', build_barrier),
        ('SM_CrateStack', build_crate_stack), ('SM_TrashBags', build_trash_bags),
        ('SM_Planter', build_planter), ('SM_Bicycle', build_bicycle), ('SM_Noren', build_noren),
        ('SM_Awning', build_awning), ('SM_RoofTank', build_roof_tank), ('SM_Manhole', build_manhole),
        ('SM_Bench', build_bench), ('SM_Kerb', build_kerb),
    ],
    'set': [
        ('SM_CrashCar', build_crash_car), ('SM_Shrapnel', build_shrapnel),
        ('SM_YardWall_1250', build_yard_wall_1250), ('SM_YardWall_3040', build_yard_wall_3040),
        ('SM_Hoarding_990', build_hoarding_990), ('SM_PlazaGate', build_plaza_gate),
        ('SM_CheckpointPost', build_checkpoint_post), ('SM_CheckpointTaken', build_checkpoint_taken),
        ('SM_PlazaPaving', build_plaza_paving), ('SM_Crosswalk', build_crosswalk),
        ('SM_RoadLines', build_road_lines),
    ],
}
MODELS = [p for g in ('cafe', 'city', 'ruins', 'props', 'set') for p in GROUPS[g]]

# How the cafe is dressed, in metres relative to the cafe centre (which is the level origin: the cafe is built
# around (0,0) and the player starts inside it at (0,0,100) cm). tools/jumpcut_city_place.py places exactly this
# list in Unreal, so what the check render shows and what the level gets are the same data.
# Three lanes are kept deliberately clear and nothing is allowed into them:
#   * (0,0) -> (6.15, 0)    the player's walk from his start point to the door
#   * (-3.3, -0.6) -> (-5.4, -1.61)  the shrapnel's flight from the wreck to the coworker in beat 1
#   * (-3.8, 2.2)           the crash driver's body, which the player has to be able to reach and touch
CAFE_DRESS = [
    # Moved west Fri Nov 13: the Team Owner asked for the register to be near the wall the car comes
    # through, so that the car barely misses the coworker standing at it. The counter runs along the
    # south-west with its STAFF side (+Y) facing the car, 1.00 m from the car's flank at y = -1.00, so
    # whoever is at the register is about 0.60 m from it. It stays clear of all three protected lanes:
    # the walk is at y = 0, the shrapnel now falls from above the wreck straight onto her, and the body is
    # on the +Y side. The shrapnel's start MOVED on Fri Nov 13 (M Station, #56): from (-4.70, 0, 1.85),
    # level with the car, the flight to her new spot behind the counter was blocked by the car's own cab
    # after 0.74 m of a 2.00 m flight, so the debris could never reach her. It now starts at
    # (-3.30, -0.60, 3.70), just under the 4.00 m ceiling, giving a clear 3.64 m fall.
    # yaw 180: the counter puts its customer panels on Blender -Y, which the FBX export turns into Unreal
    # +Y, so at yaw 0 the customers would stand on the car's side and the staff would be against the south
    # wall. Turned round, the STAFF side faces the car and whoever is at the register is the one the car
    # nearly hits, which is what was asked for. Customers queue in the 2.35 m strip behind.
    ('SM_CafeCounter',   -3.30, -2.40, 0.00, 180),
    ('SM_CafeRegister',  -5.40, -2.40, 1.10, 180),
    ('SM_CafeEspresso',  -4.30, -2.40, 1.04, 180),
    ('SM_CafePastryCase',-1.60, -2.38, 1.04, 180),
    ('SM_CafeShelf',     -2.20, -4.90, 0.02,   0),
    ('SM_CafeShelf',      4.60, -4.90, 0.02,   0),
    ('SM_CafeTable',     -3.10,  3.10, 0.02,   0),
    ('SM_CafeChair',     -3.10,  2.35, 0.02,   0),
    ('SM_CafeChair',     -3.10,  3.85, 0.02, 180),
    ('SM_CafeTable',      0.10,  3.45, 0.02,   0),
    ('SM_CafeChair',      0.10,  2.70, 0.02,   0),
    ('SM_CafeChair',      0.10,  4.20, 0.02, 180),
    ('SM_CafeTable',      3.60,  3.10, 0.02,   0),
    ('SM_CafeChair',      3.60,  2.35, 0.02,   0),
    ('SM_CafeChair',      3.60,  3.85, 0.02, 180),
]


# Pieces whose origin is deliberately at their centre, not on the ground (see their docstrings).
CENTRE_ORIGIN = ('SM_PlazaGate', 'SM_Shrapnel', 'SM_CheckpointTaken')


def tri_count(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def build_all():
    fresh()
    report = {}
    for name, fn in MODELS:
        o = fn(name)
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs, ys, zs = [p.x for p in bb], [p.y for p in bb], [p.z for p in bb]
        report[name] = {
            'tris': tri_count(o),
            'verts': len(o.data.vertices),
            'size_m': [round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3), round(max(zs) - min(zs), 3)],
            'z_min': round(min(zs), 4),
            'slots': [m.name for m in o.data.materials],
        }
    return report


def export_all():
    os.makedirs(OUT, exist_ok=True)
    for name, _ in MODELS:
        o = bpy.data.objects[name]
        for x in bpy.context.scene.objects:
            x.select_set(x is o)
        bpy.context.view_layer.objects.active = o
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + '.fbx'), use_selection=True,
                                 object_types={'MESH'}, apply_unit_scale=True,
                                 apply_scale_options='FBX_SCALE_NONE', axis_forward='-Z', axis_up='Y',
                                 mesh_smooth_type='FACE', add_leaf_bones=False, bake_anim=False,
                                 embed_textures=False, colors_type='SRGB')


PREVIEW = {'MS_CityWall': (0.78, 0.75, 0.70), 'MS_CityBrick': (0.42, 0.24, 0.19),
           'MS_CityConcrete': (0.58, 0.58, 0.56), 'MS_CityTrim': (0.11, 0.12, 0.14),
           'MS_CityMetal': (0.55, 0.57, 0.60), 'MS_CityGlass': (0.22, 0.38, 0.47),
           'MS_CitySignA': (0.95, 0.42, 0.18), 'MS_CitySignB': (0.25, 0.72, 0.90),
           'MS_CityAccent': (0.72, 0.16, 0.20), 'MS_CityWood': (0.47, 0.31, 0.18),
           'MS_CityRoof': (0.23, 0.23, 0.25), 'MS_CityCloth': (0.80, 0.74, 0.62)}


def preview_colours():
    for n, c in PREVIEW.items():
        m = bpy.data.materials.get(n)
        if m:
            m.diffuse_color = (c[0], c[1], c[2], 1.0)
            if m.use_nodes:
                bsdf = m.node_tree.nodes.get('Principled BSDF')
                if bsdf:
                    bsdf.inputs['Base Color'].default_value = (c[0], c[1], c[2], 1.0)
                    if n.startswith('MS_CitySign'):
                        bsdf.inputs['Emission Color'].default_value = (c[0], c[1], c[2], 1.0)
                        bsdf.inputs['Emission Strength'].default_value = 0.9


def _stage(total, tall, target_z=None, cam_at=None, px=1600, aspect=0.5):
    """Camera, sun, ground and sky for a check render. Returns the objects to delete afterwards."""
    sc = bpy.context.scene
    cam_data = bpy.data.cameras.new('C')
    cam = bpy.data.objects.new('C', cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam_data.lens = 40
    dist = total * 1.05 + tall * 0.7
    cam.location = cam_at or (total / 2, -dist * 0.80, max(tall * 0.55, dist * 0.30))
    target = Vector((total / 2, 0.0, tall * 0.42 if target_z is None else target_z))
    cam.rotation_euler = (target - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
    sun_d = bpy.data.lights.new('S', 'SUN')
    sun_d.energy = 3.5
    sun = bpy.data.objects.new('S', sun_d)
    sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(52), math.radians(14), math.radians(205))
    gm = bpy.data.meshes.new('G')
    gbm = bmesh.new()
    bmesh.ops.create_grid(gbm, x_segments=1, y_segments=1, size=max(total, 80.0))
    gbm.to_mesh(gm)
    gbm.free()
    ground = bpy.data.objects.new('G', gm)
    sc.collection.objects.link(ground)
    ground.location = (total / 2, 0, -0.002)
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = px, int(px * aspect)
    sc.render.film_transparent = False
    sc.world = bpy.data.worlds.new('W')
    sc.world.use_nodes = True
    sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.62, 0.72, 1)
    sc.world.node_tree.nodes['Background'].inputs[1].default_value = 0.7
    return cam, sun, ground


def render_cafe(path, px=1700):
    """The coffee shop, dressed from CAFE_DRESS, with the ceiling hidden: a doll's-house view.

    This is the render that actually answers the question a tri count cannot - does the furniture fit the room,
    is the door clear, does the hole line up with where the car is.
    """
    import copy as _copy
    sc = bpy.context.scene
    for o in sc.objects:
        o.hide_render = True
    shell = bpy.data.objects['SM_CafeShell']
    shell.hide_render = False
    shell.location = (0, 0, 0)
    # Cut away the ceiling AND the south wall for the render: the counter and the shelves stand against the
    # south wall, so a view that keeps it shows an empty room and proves nothing.
    def _cut(p):
        vs = [shell.data.vertices[v].co for v in p.vertices]
        return all(c.z > CAFE_H - 0.01 for c in vs) or all(c.y < -CAFE_HD + 0.151 for c in vs)
    ceil = [p for p in shell.data.polygons if _cut(p)]
    temp = []
    for nm, x, y, z, yaw in CAFE_DRESS:
        src = bpy.data.objects[nm]
        o = src.copy()
        o.data = src.data
        sc.collection.objects.link(o)
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(yaw))
        o.hide_render = False
        temp.append(o)
    sm = shell.data
    hide = [p.index for p in ceil]
    saved = [sm.polygons[i].material_index for i in hide]
    bpy.ops.object.select_all(action='DESELECT')
    # remove the ceiling faces for the render, then put them back
    bm = bmesh.new()
    bm.from_mesh(sm)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in hide], context='FACES')
    cut = bpy.data.meshes.new('CafeShellCut')
    bm.to_mesh(cut)
    bm.free()
    for mt in sm.materials:
        cut.materials.append(mt)
    shell.data = cut
    cam, sun, ground = _stage(0.0, 7.0, target_z=1.0, cam_at=(0.5, -14.5, 14.5), px=px, aspect=0.60)
    ground.location = (0, 0, -0.002)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    shell.data = sm
    bpy.data.meshes.remove(cut)
    for o in temp:
        bpy.data.objects.remove(o)
    for o in (cam, sun, ground):
        bpy.data.objects.remove(o)
    for o in sc.objects:
        o.hide_render = False
    _ = (_copy, saved)


def render_layout(px=1700):
    """Build the whole layout from city_layout.json and render it from where the player actually stands.

    This is the check that matters. Every model can be correct on its own and the street can still be
    wrong - towers poking through shopfronts, a vending machine in the walking lane, a skyline you cannot
    see. The only way to know is to assemble it and look down it from eye height.

    Unreal -> Blender: x/100, -y/100, z/100, and the yaw negates, because Blender +Y is Unreal -Y.
    """
    import json as _json
    lay = os.path.join(OUT, 'city_layout.json')
    if not os.path.exists(lay):
        print('NO LAYOUT JSON - run tools/jumpcut_city_layout.py first')
        return
    doc = _json.load(open(lay, encoding='utf-8'))
    sc = bpy.context.scene
    temp = []
    missing = set()
    for a in doc['actors']:
        src = bpy.data.objects.get(a['model'])
        if src is None:
            missing.add(a['model'])
            continue
        o = src.copy()
        o.data = src.data
        sc.collection.objects.link(o)
        o.location = (a['x'] / 100.0, -a['y'] / 100.0, a['z'] / 100.0)
        o.rotation_euler = (0, 0, math.radians(-a['yaw']))
        temp.append(o)
    if missing:
        print('CITY_LAYOUT_MISSING ' + ', '.join(sorted(missing)))
    for o in bpy.data.objects:                       # hide the un-placed originals sitting at the origin
        o.hide_render = (o in [bpy.data.objects[n] for n, _ in MODELS])
    for o in temp:
        o.hide_render = False
    sun_d = bpy.data.lights.new('S', 'SUN')
    sun_d.energy = 3.2
    sun = bpy.data.objects.new('S', sun_d)
    sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(215))
    gm = bpy.data.meshes.new('G')
    gbm = bmesh.new()
    bmesh.ops.create_grid(gbm, x_segments=1, y_segments=1, size=400.0)
    gbm.to_mesh(gm)
    gbm.free()
    ground = bpy.data.objects.new('G', gm)
    sc.collection.objects.link(ground)
    ground.location = (50, 0, -0.01)
    gmat = bpy.data.materials.new('G_Asphalt')       # the level floor wears MS_CityRoof once the placer has run
    gmat.diffuse_color = (PREVIEW['MS_CityRoof'][0], PREVIEW['MS_CityRoof'][1], PREVIEW['MS_CityRoof'][2], 1.0)
    gmat.use_nodes = True
    gmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = gmat.diffuse_color
    gmat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
    gm.materials.append(gmat)
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.film_transparent = False
    sc.world = bpy.data.worlds.new('W')
    sc.world.use_nodes = True
    sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.58, 0.66, 0.78, 1)
    sc.world.node_tree.nodes['Background'].inputs[1].default_value = 0.85
    cam_data = bpy.data.cameras.new('C')
    cam = bpy.data.objects.new('C', cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    # (name, camera position, what it looks at, lens, aspect) - all in Blender metres
    shots = [
        ('lane',      (7.6, 0.0, 1.65),     (40.0, 0.0, 3.0),    28, 0.56),
        ('lane_back', (62.0, 0.0, 1.70),    (10.0, 0.0, 4.0),    28, 0.56),
        ('cafe_west', (3.0, 0.0, 1.60),     (-30.0, 2.0, 3.0),   30, 0.56),
        ('plaza',     (69.5, 0.0, 1.80),    (85.0, 0.0, 9.0),    30, 0.56),
        # the set pieces, from where the player stands: the car from inside the cafe, the boss lot from just
        # inside its entry gate, and the exit run from the exit gate
        ('cafe_car',  (2.6, 2.6, 1.60),     (-5.2, 0.0, 0.8),    30, 0.56),
        ('plaza_in',  (67.2, 4.0, 1.70),    (84.0, -4.0, 2.0),   26, 0.56),
        ('exit_run',  (96.6, 0.0, 1.70),    (106.0, 0.0, 2.0),   26, 0.56),
        ('overview',  (36.0, -205.0, 150.0), (52.0, 4.0, 6.0),  48, 0.42),
    ]
    for nm, pos, look, lens, asp in shots:
        cam_data.lens = lens
        cam.location = pos
        cam.rotation_euler = (Vector(look) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        sc.render.resolution_x, sc.render.resolution_y = px, int(px * asp)
        sc.render.filepath = os.path.join(CACHE, 'city_layout_%s.png' % nm)
        bpy.ops.render.render(write_still=True)
        print('rendered layout:' + nm)
    for o in temp:
        bpy.data.objects.remove(o)
    for o in (cam, sun, ground):
        bpy.data.objects.remove(o)
    for o in bpy.data.objects:
        o.hide_render = False


def render_group(group, path, px=1600):
    """Lay the group out in a row on the ground and render one 3/4 view of it."""
    names = [n for n, _ in GROUPS[group] if n != 'SM_CafeShell']
    for o in bpy.context.scene.objects:
        o.hide_render = o.name not in names
    x = 0.0
    for n in names:
        o = bpy.data.objects[n]
        bb = [Vector(c) for c in o.bound_box]
        w = max(p.x for p in bb) - min(p.x for p in bb)
        o.location = (x + w / 2 + 1.0, 0.0, 0.0)
        x += w + 2.0
    total = max(x, 6.0)
    tall = max(max(Vector(c).z for c in bpy.data.objects[n].bound_box) for n in names)
    sc = bpy.context.scene
    cam, sun, ground = _stage(total, tall, px=px)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for o in (cam, sun, ground):
        bpy.data.objects.remove(o)
    for o in bpy.context.scene.objects:
        o.hide_render = False


def render_set_pieces():
    """Close check renders of the set pieces. render_group lays a group out in one row, which is right for
    props and useless here: a 30 m floor and a 78 cm shard in the same frame shows you the floor."""
    shots = [
        # (file, [(model, x, y, yaw degrees)], camera, target)
        ('city_set_car_door.png', [('SM_CrashCar', 0, 0, 0)], (3.6, -5.2, 2.3), (0.0, -0.2, 0.7)),
        ('city_set_car_far.png', [('SM_CrashCar', 0, 0, 0)], (4.6, 4.4, 2.6), (0.0, 0.0, 0.6)),
        ('city_set_wall.png', [('SM_YardWall_1250', 0, 0, 0)], (2.0, -11.5, 3.2), (0.0, 0.0, 1.9)),
        ('city_set_wall_long.png', [('SM_YardWall_3040', 0, 0, 0)], (-9.0, -15.0, 4.5), (2.0, 0.0, 1.8)),
        ('city_set_gate_run.png', [('SM_PlazaGate', 0, 0, 2.0), ('SM_Hoarding_990', 5.2, -2.65, 0),
                                   ('SM_Hoarding_990', 5.2, 2.65, 0), ('SM_CheckpointPost', -2.2, -1.2, 60)],
         (-9.5, -3.4, 2.4), (1.0, 0.0, 1.9)),
        ('city_set_small.png', [('SM_CheckpointPost', 0, 0, 0), ('SM_CheckpointTaken', 0.9, 0, 1.3),
                                ('SM_Shrapnel', -0.9, 0, 1.2)], (0.6, -4.2, 1.7), (0.0, 0.0, 1.15)),
        ('city_set_shrapnel.png', [('SM_Shrapnel', 0, 0, 0.6)], (0.75, -0.95, 1.05), (0.0, 0.0, 0.6)),
        ('city_set_ground.png', [('SM_PlazaPaving', 0, 0, 0), ('SM_Crosswalk', -18.5, 0, 0),
                                 ('SM_RoadLines', -24.0, 0, 0)], (-30.0, -16.0, 13.0), (-4.0, 0.0, 0.0)),
    ]
    sc = bpy.context.scene
    used = {n for n, _ in GROUPS['set']}
    for fn, items, cam_at, target in shots:
        for o in sc.objects:
            o.hide_render = True
        extra = []
        seen = set()
        for it in items:
            m, x, y, third = it
            o = bpy.data.objects[m]
            if m in seen:                                   # a second copy of the same model in one shot
                o = o.copy()
                sc.collection.objects.link(o)
                extra.append(o)
            seen.add(m)
            o.hide_render = False
            if m in CENTRE_ORIGIN:
                o.location, o.rotation_euler = (x, y, third), (0, 0, 0)
            else:
                o.location, o.rotation_euler = (x, y, 0.0), (0, 0, math.radians(third))
        cam, sun, ground = _stage(8.0, 3.0, px=1500, aspect=0.6)
        ground.location = (0, 0, -0.002)
        cam.location = cam_at
        cam.rotation_euler = (Vector(target) - Vector(cam_at)).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(CACHE, fn)
        bpy.ops.render.render(write_still=True)
        for o in [cam, sun, ground] + extra:
            bpy.data.objects.remove(o)
        print('rendered ' + fn)
    for o in sc.objects:
        o.hide_render = False
        if o.name in used:
            o.location, o.rotation_euler = (0, 0, 0), (0, 0, 0)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    mode = argv[0] if argv else 'build'
    os.makedirs(CACHE, exist_ok=True)
    report = build_all()
    export_all()
    # Write each model's footprint in UNREAL-LOCAL centimetres so tools/jumpcut_city_layout.py can check
    # placements for real instead of somebody squinting at a render. Blender +Y is Unreal -Y, so the local
    # y range flips.
    import json as _j
    boxes = {}
    for name, _ in MODELS:
        o = bpy.data.objects[name]
        bb = [Vector(c) for c in o.bound_box]
        boxes[name] = {
            'x': [round(min(p.x for p in bb) * 100, 1), round(max(p.x for p in bb) * 100, 1)],
            'y': [round(-max(p.y for p in bb) * 100, 1), round(-min(p.y for p in bb) * 100, 1)],
            'z': [round(min(p.z for p in bb) * 100, 1), round(max(p.z for p in bb) * 100, 1)],
            'tris': report[name]['tris'],
        }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'city_models.json'), 'w', encoding='utf-8', newline='\n') as f:
        _j.dump(boxes, f, indent=1)
        f.write('\n')
    print('CITY_KIT_REPORT ' + __import__('json').dumps(report))
    print('CITY_KIT_TOTALS models=%d tris=%d' % (len(report), sum(r['tris'] for r in report.values())))
    bad = {n: r for n, r in report.items() if abs(r['z_min']) > 0.13 and n not in CENTRE_ORIGIN}
    print('CITY_KIT_OFFGROUND ' + __import__('json').dumps(bad))
    if 'set' in argv:
        preview_colours()
        render_set_pieces()
    if 'sheets' in argv or mode == 'sheets':
        preview_colours()
        for g in GROUPS:
            if g == 'set':
                continue                                    # see render_set_pieces
            render_group(g, os.path.join(CACHE, 'city_%s.png' % g))
            print('rendered ' + g)
        render_set_pieces()
        render_cafe(os.path.join(CACHE, 'city_cafe_interior.png'))
        print('rendered cafe_interior')
    if 'layout' in argv or mode == 'layout':
        preview_colours()
        render_layout()


if __name__ == '__main__':
    main()
