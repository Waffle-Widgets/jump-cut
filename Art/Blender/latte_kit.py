"""The latte mini game's cup, saucer and milk pitcher.  Our own models, built from profiles.

    blender -b --factory-startup --python Art/Blender/latte_kit.py
Writes Art/Blender/export/Latte/SM_LatteCup.fbx, SM_LatteSaucer.fbx, SM_LattePitcher.fbx and a preview render.

Numbers are centimetres in the game. The cup's origin is the centre of the COFFEE SURFACE (z 0); the surface disc
in the game is 5.76 cm in radius, so the cup's inner wall is 5.8 at z 0. The pitcher's origin is its SPOUT TIP and it
is exported already tilted to pour, spout toward the game's -Y, so the Blueprint only has to move it.
"""
import bpy, bmesh, math, os
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'export', 'Latte')
os.makedirs(OUT, exist_ok=True)
CM = 0.01
bpy.ops.wm.read_factory_settings(use_empty=True)


def lathe(name, profile, segs=48):
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z * CM))])
        else:
            rings.append([bm.verts.new((r * CM * math.cos(2 * math.pi * i / segs), r * CM * math.sin(2 * math.pi * i / segs), z * CM)) for i in range(segs)])
    for a, b in zip(rings, rings[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                bm.faces.new((a[0], b[j], b[i]))
            elif len(b) == 1:
                bm.faces.new((a[i], a[j], b[0]))
            else:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    return bm, rings


def handle(bm, centre, major, minor, plane='YZ', arc=(-100, 100), segs=14, tube=8):
    """A C-shaped handle: a swept circle. centre in cm; the arc opens toward the body."""
    prev = None
    for s in range(segs + 1):
        a = math.radians(arc[0] + (arc[1] - arc[0]) * s / segs)
        ring = []
        for t in range(tube):
            b = 2 * math.pi * t / tube
            rr = major + minor * math.cos(b)
            if plane == 'YZ':
                p = (minor * math.sin(b), -rr * math.cos(a), rr * math.sin(a))
            else:
                p = (-rr * math.cos(a), minor * math.sin(b), rr * math.sin(a))
            ring.append(bm.verts.new(((centre[0] + p[0]) * CM, (centre[1] + p[1]) * CM, (centre[2] + p[2]) * CM)))
        if prev:
            for t in range(tube):
                u = (t + 1) % tube
                bm.faces.new((prev[t], prev[u], ring[u], ring[t]))
        prev = ring


def finish(bm, name, mat):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new(mat)
    me.materials.append(m)
    return ob


# cup: outer wall up, rolled rim, inner wall down to just under the coffee
bm, _ = lathe('cup', [(0, -8.3), (3.0, -8.3), (3.5, -7.9), (4.7, -5.0), (5.7, -2.2), (6.3, 0.35), (6.42, 0.75), (6.25, 0.92),
                      (6.0, 0.7), (5.8, -0.15), (0, -0.15)])
handle(bm, (0, -6.6, -3.4), 2.3, 0.5, 'YZ')
cup = finish(bm, 'SM_LatteCup', 'MS_LatteCup')

bm, _ = lathe('saucer', [(0, -9.0), (4.6, -9.0), (9.6, -7.95), (10.1, -7.7), (9.7, -7.55), (4.6, -8.45), (0, -8.45)])
saucer = finish(bm, 'SM_LatteSaucer', 'MS_LatteSaucer')

# pitcher: straight-sided jug, a pulled spout toward +Y (the game's -Y), a handle opposite
SEGS = 48
bm, rings = lathe('pitcher', [(0, 0), (3.7, 0), (3.95, 0.35), (4.0, 3.0), (3.35, 7.2), (3.45, 9.4), (3.3, 9.4), (3.2, 7.2), (3.85, 3.0),
                              (3.8, 0.5), (0, 0.5)], SEGS)
for ring in rings:
    for v in ring:
        z = v.co.z / CM
        if z < 6.5:
            continue
        ang = math.atan2(v.co.x, v.co.y)                       # 0 at +Y
        w = max(0.0, 1.0 - abs(ang) / math.radians(34)) ** 1.5 * min(1.0, (z - 6.5) / 2.9)
        v.co.y += w * 2.3 * CM
        v.co.z -= w * 0.25 * CM
handle(bm, (0, -3.6, 5.2), 2.6, 0.42, 'YZ')
pit = finish(bm, 'SM_LattePitcher', 'MS_LattePitcher')
tip = Vector((0, (3.45 + 2.3) * CM, (9.4 - 0.25) * CM))
tilt = Matrix.Rotation(math.radians(-42), 4, 'X')               # spout tip swings down
pit.data.transform(Matrix.Translation(-(tilt @ tip)) @ tilt)
pit.data.update()

for ob in (cup, saucer, pit):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    f = os.path.join(OUT, ob.name + '.fbx')
    bpy.ops.export_scene.fbx(filepath=f, use_selection=True, axis_forward='-Z', axis_up='Y', apply_unit_scale=True,
                             global_scale=1.0, mesh_smooth_type='FACE', object_types={'MESH'})
    d = ob.dimensions
    print('LATTEKIT %s tris %d size cm %.1f x %.1f x %.1f -> %s' % (ob.name, sum(len(p.vertices) - 2 for p in ob.data.polygons),
                                                                   d.x / CM, d.y / CM, d.z / CM, f))

# a look at it
pit.location = (0, -0.09, 0.09)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
bpy.context.scene.collection.objects.link(cam)
cam.location = (0.0, -0.42, 0.34); cam.rotation_euler = (math.radians(52), 0, 0)
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(40), math.radians(20), 0); sun.data.energy = 3.0
sc = bpy.context.scene
sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 900, 700
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.5, 0.5, 0.5)
sc.render.filepath = os.path.join(HERE, 'cache', 'latte_kit.png')
try:
    bpy.ops.render.render(write_still=True)
    print('LATTEKIT render', sc.render.filepath)
except Exception as e:
    print('LATTEKIT render failed', e)
