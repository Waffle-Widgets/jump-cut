"""Check renders for the Meshy street models: each baked FBX + PNG from two angles beside a 1.75 m figure.
    blender -b --factory-startup --python Art/Blender/street_models_sheet.py -- <out_dir> Name[:Folder] ...
Reads Art/Meshy/<Folder>/SM_<Folder>.fbx and T_<Folder>.png - the files Unreal will import, not the raw
download - so what this shows is what the game gets. Unlit texture colour (Workbench, flat), because a lit
render makes you judge the light rig instead of the bake. Also prints the lowest canopy point over the
walking line for a tree, which is what decides whether the player's head goes through it."""
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
OUT, NAMES = argv[0], argv[1:]
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'FLAT'; sh.color_type = 'TEXTURE'; sh.show_object_outline = False
sc.render.resolution_x, sc.render.resolution_y = 900, 700
sc.render.film_transparent = False
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.62, 0.65, 0.70)
sc.view_settings.view_transform = 'Standard'
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam)
cam.data.lens = 50; sc.camera = cam

for name in NAMES:
    folder = name.split(':')[-1]
    d = os.path.join(REPO, 'Art', 'Meshy', folder)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(d, 'SM_%s.fbx' % folder))
    obj = [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]
    bpy.context.view_layer.update()
    img = bpy.data.images.load(os.path.join(d, 'T_%s.png' % folder))
    mat = bpy.data.materials.new('chk'); mat.use_nodes = True
    tn = mat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = img
    mat.node_tree.links.new(tn.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    mat.node_tree.nodes.active = tn
    obj.data.materials.clear(); obj.data.materials.append(mat)
    ws = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = Vector((min(v.x for v in ws), min(v.y for v in ws), min(v.z for v in ws)))
    hi = Vector((max(v.x for v in ws), max(v.y for v in ws), max(v.z for v in ws)))
    size = hi - lo
    # a 1.75 m figure standing just off the model's -Y side, for scale
    bpy.ops.mesh.primitive_cube_add(size=1, location=(hi.x + 0.45, lo.y - 0.1, lo.z + 0.875))
    fig = bpy.context.active_object; fig.scale = (0.42, 0.25, 1.75)
    fm = bpy.data.materials.new('fig'); fm.diffuse_color = (0.15, 0.55, 0.6, 1); fig.data.materials.append(fm)
    span = max(size.x + 1.0, size.z, size.y)
    ctr = Vector(((lo.x + hi.x) / 2 + 0.3, (lo.y + hi.y) / 2, lo.z + size.z * 0.48))
    info = {'size_m': [round(v, 2) for v in size], 'tris': sum(len(p.vertices) - 2 for p in obj.data.polygons)}
    if size.z > 3:
        # lowest geometry more than 0.9 m out from the trunk line, i.e. the underside of the canopy
        outer = [v.z for v in ws if abs(v.x) > 0.9 or abs(v.y) > 0.9]
        info['canopy_underside_m'] = round(min(outer), 2) if outer else None
        base = [v for v in ws if v.z < 0.08]
        info['base_centre_m'] = [round(sum(v.x for v in base) / len(base), 2), round(sum(v.y for v in base) / len(base), 2)]
    # STREET_VIEWS=front: the first view is from straight down -Y, which is the side the kit calls the FRONT
    # of a prop (it is what faces the street). If the model's front is not what that view shows, it needs a PROP_YAW.
    views = (('f', 0, 10), ('a', -40, 16)) if os.environ.get('STREET_VIEWS') == 'front' else (('a', -35, 14), ('b', 105, 14))
    for tag, yaw, pitch in views:
        dist = span * 2.3
        y, p = math.radians(yaw), math.radians(pitch)
        cam.location = ctr + Vector((math.sin(y) * math.cos(p) * dist, -math.cos(y) * math.cos(p) * dist, math.sin(p) * dist))
        cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(OUT, 'street_%s_%s.png' % (name.split(':')[0], tag))
        bpy.ops.render.render(write_still=True)
    print('STREET_SHEET', name, info)
    for o in (obj, fig):
        bpy.data.objects.remove(o)
