"""Makes a Meshy prop game-ready: real size, few triangles, clean UVs and its colour baked from the full-detail model
(from the Deep Archive HD-2D test). Default: a fine texture (about 4 mm per texel, at most 2048).
PROP_PIXEL=1: a chunky pixel texture instead (one texel = 3 cm, to sit next to pixel-art sprites).
    blender -b --factory-startup --python Art/Blender/meshy_prop_bake.py -- <in.glb> <Name> <size_m> <height|width> <tris>
Writes Art/Meshy/<Name>/SM_<Name>.fbx and T_<Name>.png, and a check render in Art/Blender/cache/meshy_<Name>.png.
Steps: import the GLB, size it (height, or its widest side for `width`), stand it on the ground, centred; copy it,
weld and decimate the copy, give it clean big UV islands, bake the Meshy colour texture onto it (Cycles,
selected-to-active, emission), and export with our FBX settings (forward -Z, up Y: Blender +Y becomes Unreal -Y, so a
model facing Blender -Y faces the game camera)."""
import bpy, bmesh, math, os, sys
import numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
GLB, NAME, SIZE, MODE, TRIS = argv[0], argv[1], float(argv[2]), argv[3], int(argv[4])
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(REPO, 'Art', 'Meshy', NAME)
CACHE = os.path.join(REPO, 'Art', 'Blender', 'cache')
os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
TEXEL = 0.03          # metres per texel: a sprite pixel is 1.5 game units = 3 cm
# PROP_SMOOTH=1: the stylized-3D room's version (pass a <Name>3D name): a fine, smoothly filtered texture
# (about 4 mm per texel, at most 2048) instead of the 3 cm pixel one, and a wider bake margin
SMOOTH = os.environ.get('PROP_PIXEL') != '1'   # practice repo: fine texture by default
if SMOOTH:
    TEXEL = float(os.environ.get('PROP_TEXEL', '0.004'))
# PROP_CAGE: how far the bake looks outward from the low mesh, as a fraction of the prop's size. 0.05 suits a
# smooth prop; on a lumpy one (blossom clumps) a ray that long starts inside the next lump and bakes black
CAGE = float(os.environ.get('PROP_CAGE', '0.05'))
# optional 6th argument: voxel size in metres. Wraps the low copy in one closed skin before decimating, for models
# made of many thin overlapping shells (the berry bush's leaves), which otherwise decimate into spikes and bake black
VOXEL = float(argv[5]) if len(argv) > 5 else 0.0
# optional 7th argument: total height in metres for a pole-like prop (the torch post). The model is sized by its
# widest part (the bowl, with `width`), then only the part below that wide top is stretched until the whole is this
# tall, so a taller post doesn't also get a giant bowl (scaling the whole model evenly gave an 85 cm bowl).
POLE = float(argv[6]) if len(argv) > 6 else 0.0
report = {'name': NAME}

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=GLB)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in bpy.context.scene.objects:
    o.select_set(o in meshes)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
src = bpy.context.view_layer.objects.active
src.name = 'SRC'
src.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o is not src:
        bpy.data.objects.remove(o)

# PROP_CUT_BELOW=<fraction of the height>: throw away everything below that level before anything else. The
# awning was drawn standing on posts; the kit's hangs off the wall, and posts either side of the cafe door
# would be two new things to walk into.
CUT = float(os.environ.get('PROP_CUT_BELOW', '0'))
if CUT > 0:
    bm = bmesh.new(); bm.from_mesh(src.data)
    zs = [v.co.z for v in bm.verts]
    lim = min(zs) + CUT * (max(zs) - min(zs))
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < lim], context='VERTS')
    bm.to_mesh(src.data); bm.free(); src.data.update()
# size and place: base on the ground, centred
V = np.empty(len(src.data.vertices) * 3); src.data.vertices.foreach_get('co', V); V = V.reshape(-1, 3)
# PROP_YAW=<degrees>: turn the model about the up axis first, so its long side lies where the kit expects it
# (the city kit builds every vehicle with its length along X and its nose at +X)
YAW = math.radians(float(os.environ.get('PROP_YAW', '0')))
if YAW:
    c, sn = math.cos(YAW), math.sin(YAW)
    V[:, 0], V[:, 1] = V[:, 0] * c - V[:, 1] * sn, V[:, 0] * sn + V[:, 1] * c
# PROP_PRESCALE=sx,sy,sz: stretch the model before it is sized. Image to 3D sees one side of a thing, so a
# tree comes back as a fan: the sakura was 6.2 m wide and 1.9 m deep (Nov 15).
PRE = [float(x) for x in os.environ.get('PROP_PRESCALE', '1,1,1').split(',')]
V *= PRE
# PROP_KITBOX=x0,x1,y0,y1,z0,z1 (metres): fit the model EXACTLY into the box of the kit model it replaces, each
# axis scaled on its own, so a counter that other things stand on, or a shelf between two walls, keeps the kit
# piece's footprint, height and origin to the millimetre. The long side is laid along the box's long side first;
# which END is the front still has to be looked at (PROP_YAW=180 flips it). Furniture only: an uneven stretch
# of a few percent is invisible on a counter and obvious on a wheel.
KITBOX = os.environ.get('PROP_KITBOX')
if KITBOX:
    kb = [float(x) for x in KITBOX.split(',')]
    klo, khi = np.array(kb[0::2]), np.array(kb[1::2])
    lo, hi = V.min(0), V.max(0); dims = hi - lo
    if (dims[0] >= dims[1]) != ((khi - klo)[0] >= (khi - klo)[1]):
        V[:, 0], V[:, 1] = -V[:, 1].copy(), V[:, 0].copy()
        lo, hi = V.min(0), V.max(0); dims = hi - lo
    report['stretch'] = [round(float(x), 3) for x in ((khi - klo) / dims) / ((khi - klo) / dims).mean()]
    V = (V - lo) / dims * (khi - klo) + klo
else:
    lo, hi = V.min(0), V.max(0); dims = hi - lo
    s = SIZE / (dims[2] if MODE == 'height' else max(dims[0], dims[1]))
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    # PROP_ORIGIN=base: put the origin under the FOOT of the model (the middle of its lowest 2%) instead of the
    # middle of its bounding box. A street lamp's box is mostly arm; the kit's lamp has its origin at the column.
    # With it, PROP_ARM=<degrees> turns the model so the overhang points that way (180 = toward -X, like the kit).
    if os.environ.get('PROP_ORIGIN') == 'base':
        foot = V[V[:, 2] < lo[2] + 0.02 * dims[2]]
        fx, fy = float(foot[:, 0].mean()), float(foot[:, 1].mean())
        if 'PROP_ARM' in os.environ:
            a = math.radians(float(os.environ['PROP_ARM'])) - math.atan2(cy - fy, cx - fx)
            c, sn = math.cos(a), math.sin(a)
            X, Y = V[:, 0] - fx, V[:, 1] - fy
            V[:, 0], V[:, 1] = X * c - Y * sn, X * sn + Y * c
            fx = fy = 0.0
        cx, cy = fx, fy
    V = (V - [cx, cy, lo[2]]) * s
    # PROP_BACK=<metres>: slide the model so its BACK (+Y, the side that stands against a wall) is at this Y, which is
    # the kit model's own. A Meshy bench is 78 cm deep where the kit's is 50; centred, its back would be 14 cm inside
    # the shopfront. PROP_SHIFT_X=<metres>: the same for a kit model whose origin is not at its middle (SM_PotRow).
    if 'PROP_BACK' in os.environ:
        V[:, 1] += float(os.environ['PROP_BACK']) - V[:, 1].max()
    if 'PROP_SHIFT_X' in os.environ:
        V[:, 0] += float(os.environ['PROP_SHIFT_X'])
    # PROP_SHIFT=dx,dy,dz (metres): for a kit model whose origin is nowhere near it - the cafe's projecting sign
    # hangs 2.9 m above its own origin, which is on the pavement at the foot of the wall.
    if 'PROP_SHIFT' in os.environ:
        V += [float(x) for x in os.environ['PROP_SHIFT'].split(',')]
# PROP_FLAT_TOP=<metres>: everything within this much of the top is pressed onto one level plane, for a
# counter that a cup, a till and a mini game stand on.
if 'PROP_FLAT_TOP' in os.environ:
    top = V[:, 2].max()
    V[V[:, 2] > top - float(os.environ['PROP_FLAT_TOP']), 2] = top
if POLE > 0:
    # the wide top starts at the lowest height where the model is at least half as wide as its widest part
    z, r = V[:, 2], np.abs(V[:, :2]).max(1)
    bins = np.linspace(0, z.max(), 61)
    width = np.array([r[(z >= a) & (z < b)].max() if ((z >= a) & (z < b)).any() else 0 for a, b in zip(bins[:-1], bins[1:])])
    zb = float(bins[np.argmax(width >= 0.5 * width.max())])
    k = (POLE - (z.max() - zb)) / zb
    below = z < zb
    V[below, 2] *= k
    V[~below, 2] += zb * (k - 1)
    report['pole'] = {'bowl_from_m': round(zb, 3), 'stretch': round(float(k), 2)}
src.data.vertices.foreach_set('co', V.ravel()); src.data.update()
report['size_m'] = [round(float(x), 3) for x in (V.max(0) - V.min(0))]
report['src_tris'] = sum(len(p.vertices) - 2 for p in src.data.polygons)

# the low copy: weld (the glTF import splits vertices along UV seams), then decimate
low = src.copy(); low.data = src.data.copy(); low.name = 'LOW'
bpy.context.scene.collection.objects.link(low)
bm = bmesh.new(); bm.from_mesh(low.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5 * SIZE)
bm.to_mesh(low.data); bm.free()
while low.data.uv_layers:
    low.data.uv_layers.remove(low.data.uv_layers[0])
low.data.materials.clear()
for o in bpy.context.scene.objects:
    o.select_set(o is low)
bpy.context.view_layer.objects.active = low
if VOXEL > 0:
    rm = low.modifiers.new('voxel', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = VOXEL
    bpy.ops.object.modifier_apply(modifier='voxel')
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(); bpy.ops.object.mode_set(mode='OBJECT')
cur = sum(len(p.vertices) - 2 for p in low.data.polygons)
if cur > TRIS:
    mod = low.modifiers.new('dec', 'DECIMATE'); mod.ratio = TRIS / cur
    bpy.ops.object.modifier_apply(modifier='dec')
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
report['low_tris'] = sum(len(p.vertices) - 2 for p in low.data.polygons)

# clean UVs, big islands
low.data.uv_layers.new(name='UV')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.03, scale_to_bounds=False)
# A decimated Meshy vehicle comes out as several hundred islands, and a 3% margin round each one left the
# hatchback's body on about a tenth of the atlas (Nov 15). Re-pack tight: same islands, about 3x the texels.
bpy.ops.uv.select_all(action='SELECT')
bpy.ops.uv.average_islands_scale()
bpy.ops.uv.pack_islands(rotate=True, margin=0.005)
bpy.ops.object.mode_set(mode='OBJECT')

# texture size from the surface area at 3 cm per texel (smart_project fills roughly half the square)
area = sum(p.area for p in low.data.polygons)
need = math.sqrt(area / (TEXEL * TEXEL) / 0.5)
TEX = int(2 ** math.ceil(math.log2(max(need, 32))))
if SMOOTH:
    TEX = min(TEX, 2048)
report['area_m2'] = round(area, 2); report['tex_px'] = TEX

# the source shows its own colour texture as emission, for the bake
for slot in src.material_slots:
    m = slot.material
    if not m or not m.use_nodes:
        continue
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    outn = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if not bsdf or not outn or not bsdf.inputs['Base Color'].links:
        continue
    em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(bsdf.inputs['Base Color'].links[0].from_socket, em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], outn.inputs['Surface'])

img = bpy.data.images.new(f'T_{NAME}', TEX, TEX, alpha=False)
img.colorspace_settings.name = 'sRGB'
mat = bpy.data.materials.new(f'M_{NAME}'); mat.use_nodes = True; nt = mat.node_tree
tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img; tn.interpolation = 'Linear' if SMOOTH else 'Closest'
nt.links.new(tn.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color'])
nt.nodes.active = tn
low.data.materials.append(mat)

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 4
try:
    sc.cycles.device = 'GPU'
except Exception:
    pass
bk = sc.render.bake
bk.use_selected_to_active = True; bk.cage_extrusion = CAGE * SIZE; bk.max_ray_distance = 0.0; bk.margin = 8 if SMOOTH else 2   # 0 = no limit
for o in sc.objects:
    o.select_set(False)
src.select_set(True); low.select_set(True); bpy.context.view_layer.objects.active = low
bpy.ops.object.bake(type='EMIT')
tex_path = os.path.join(OUT, f'T_{NAME}.png')
img.filepath_raw = tex_path; img.file_format = 'PNG'; img.save()
px = np.empty(TEX * TEX * 4, np.float32); img.pixels.foreach_get(px)
report['tex_mean'] = round(float(px.reshape(-1, 4)[:, :3].mean()), 3)

# export the low mesh only
bpy.data.objects.remove(src)
low.name = f'SM_{NAME}'
for o in sc.objects:
    o.select_set(o is low)
fbx = os.path.join(OUT, f'SM_{NAME}.fbx')
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, axis_forward='-Z', axis_up='Y', global_scale=1.0,
                         apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='FACE',
                         path_mode='STRIP', embed_textures=False, bake_anim=False, add_leaf_bones=False)

# check render: about the game camera's angle (looking from -Y, 35 degrees down), texture shown with nearest pixels
FRAME = float((V.max(0) - V.min(0)).max())   # the prop's biggest size, so tall poles fit too
cam_d = FRAME * 3.2
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam)
cam.data.lens = 85
h = FRAME * 0.45
cam.location = (0, -cam_d * math.cos(math.radians(35)), h + cam_d * math.sin(math.radians(35)))
cam.rotation_euler = (math.radians(90 - 35), 0, 0)
sc.camera = cam
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
sc.render.resolution_x = sc.render.resolution_y = 512
sc.render.film_transparent = True
sc.render.filepath = os.path.join(CACHE, f'meshy_{NAME}.png')
bpy.ops.render.render(write_still=True)
print('MESHY_BAKE', report)
