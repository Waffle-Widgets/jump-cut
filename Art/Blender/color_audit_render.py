"""Render a character's BAKED BASE COLOUR flat (unlit, orthographic, front and back).

Why unlit: a lit render mixes the light rig into every pixel, so you end up judging
the lighting instead of the texture. With an Emission shader and the Standard view
transform, a rendered pixel IS the texture colour, and colours can be compared.

It also reports where the skeleton puts the head, the hands and the feet in image
space, so the analyser in tools/color_audit.py can say "this is hair" rather than
"this is whatever was at that pixel". No bone-name guessing: in an A-pose the hands
are the most lateral bone tips, the feet the lowest, the scalp the highest.

    blender -b -P Art/Blender/color_audit_render.py -- <mesh.fbx> <basecolour.png> <Name> <outdir>

Prints one line of JSON prefixed FLATRENDER_JSON.
"""
import bpy, sys, os, json, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index('--') + 1:]
FBX, TEX, NAME, OUTDIR = argv[0], argv[1], argv[2], argv[3]
RX, RY = 768, 1024

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
for r in rigs:
    r.data.pose_position = 'REST'     # judge the figure as drawn, not part-way through a walk
bpy.context.view_layer.update()

img = bpy.data.images.load(TEX)
img.colorspace_settings.name = 'sRGB'
mat = bpy.data.materials.new(NAME + '_flat')
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img
em = nt.nodes.new('ShaderNodeEmission')
ou = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(tx.outputs['Color'], em.inputs['Color'])
nt.links.new(em.outputs['Emission'], ou.inputs['Surface'])
for o in meshes:
    o.data.materials.clear()
    o.data.materials.append(mat)

pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
lo_z, hi_z = min(zs), max(zs)
H = hi_z - lo_z
cz = (lo_z + hi_z) / 2
span = max(xs) - min(xs)

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 1                 # emission needs no sampling; 1 is exact and instant
sc.cycles.use_denoising = False
try: sc.cycles.device = 'GPU'
except Exception: pass
sc.render.film_transparent = True
sc.view_settings.view_transform = 'Standard'   # NOT Filmic/AgX - those would shift every colour
sc.render.resolution_x, sc.render.resolution_y = RX, RY
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'

cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'
# ortho_scale maps to the LONGER render axis, so a prop wider than it is tall
# needs the aspect factor or it renders cropped.
cam.data.ortho_scale = max(H, span * RY / RX) * 1.08
cam.data.clip_start, cam.data.clip_end = 0.001, H * 100
dist = max(H, span) * 10

out = {'name': NAME, 'height_blender_units': round(H, 5), 'width_blender_units': round(span, 5),
       'res': [RX, RY], 'bones': sum(len(r.data.bones) for r in rigs), 'views': {}}

for view, (pos, rot) in {
    'front': ((cx, cy - dist, cz), (math.radians(90), 0, 0)),
    'back':  ((cx, cy + dist, cz), (math.radians(90), 0, math.radians(180))),
}.items():
    cam.location = pos
    cam.rotation_euler = rot
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUTDIR, '%s_%s_flat.png' % (NAME, view))
    bpy.ops.render.render(write_still=True)
    marks = {}
    if rigs:
        tips = [(r.matrix_world @ b.tail_local, b.name) for r in rigs for b in r.data.bones]
        picks = {'head_top': [max(tips, key=lambda t: t[0].z)],
                 'feet': sorted(tips, key=lambda t: t[0].z)[:2]}
        lat = sorted(tips, key=lambda t: -abs(t[0].x))
        for k, want in (('hand_l', lambda t: t[0].x < 0), ('hand_r', lambda t: t[0].x > 0)):
            hit = next((t for t in lat if want(t)), None)
            picks[k] = [hit] if hit else []
        for k, lst in picks.items():
            marks[k] = [{'px': round(world_to_camera_view(sc, cam, p).x * RX, 1),
                         'py': round((1 - world_to_camera_view(sc, cam, p).y) * RY, 1),
                         'bone': bn} for p, bn in lst]
    out['views'][view] = marks

print('FLATRENDER_JSON ' + json.dumps(out))
