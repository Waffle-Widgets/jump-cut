"""Give a character's apron skirt its own two bones, so it hangs from the waist instead of being painted on the thighs.

    blender -b --factory-startup --python Art/Blender/apron_bones.py -- IN.fbx TEXTURE.png OUT.fbx [RENDER.png]

WHY (Sun Nov 15, GameStation, Blender 5.3.0). The Team Owner, after playing: "The apron looks stuck to the character
instead of being its own thing." It is: the skirt is a real two-sided sheet hanging in front of his legs (a ray from
the front crosses the apron twice and THEN the thigh), but 84 % of its skin weight is on the two thigh bones, so it
copies every stride like paint. No clip can fix that, and no re-weighting onto existing bones can either: cloth is
pushed out by a thigh that swings forward and is NOT pulled back by one that swings behind, and a fixed weight
cannot tell those apart.

So the skirt gets bones of its own: Apron_L and Apron_R, children of the hip, hinged at the waist tie, one for each
half. Art/Blender/cw_clip.py swings each one forward only as far as that leg needs to pass behind it and lets it
fall back slowly. A clip that has no track for them (every retargeted one) leaves the skirt hanging straight from
the hips, which is still better than following the legs.

Which vertices are "the skirt" comes from the TEXTURE, because nothing in the mesh says so: every vertex whose
baked colour is apron green (or the white of the towel tucked at the hip), below the waist tie, with small holes
closed by a neighbour vote. Above the tie the weight ramps from the body's own to the apron's over about 9 cm, so
the bib and the bow stay on the chest and hips.

Bones are only ADDED, as leaves under the hip. Every existing bone, its rest pose, the vertices and the UVs are
untouched, so every existing clip still fits. It prints what it found and refuses if the skirt looks wrong.
"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
IN, TEX, OUT = argv[0], argv[1], argv[2]
RENDER = argv[3] if len(argv) > 3 else None
TIE_HI, TIE_LO = 100.0, 98.0       # cm above the floor: the body's own weights above, all apron below. The skirt is cut
                                   # free below TIE_LO; a 9 cm ramp left 500 stretched edges at the waist in a plain walk
BLEND_X = 15.0                     # cm either side of the centre line over which the two bones share the skirt:
                                   # nearly its whole width, so one raised knee TWISTS the sheet instead of tearing it in two

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IN)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me = mesh.data
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
if 'Apron_L' in arm.data.bones:
    raise SystemExit('REFUSING: this body already has apron bones')
MW = mesh.matrix_world
Vw = np.array([MW @ v.co for v in me.vertices])
s = float(Vw[:, 2].max() - Vw[:, 2].min()) / 174.0          # scene units per centimetre (he is 174 cm)
V = Vw / s

# ---------- which vertices are the skirt ----------
img = bpy.data.images.load(TEX)
w, h = img.size
px = np.empty(w * h * 4, np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)
uv = me.uv_layers.active.data
col = np.zeros((len(V), 3))
cnt = np.zeros(len(V))
for l in me.loops:
    u, v_ = uv[l.index].uv
    col[l.vertex_index] += px[min(h - 1, max(0, int(v_ * h))), min(w - 1, max(0, int(u * w))), :3]
    cnt[l.vertex_index] += 1
col /= np.maximum(cnt, 1)[:, None]
green = (col[:, 1] > col[:, 0] * 1.12) & (col[:, 1] > col[:, 2] * 1.12)
white = (col.min(1) > 0.55) & ((col.max(1) - col.min(1)) < 0.12)
front = V[:, 1] < 4.0                                        # he faces -Y: nothing behind his side seam
cloth = (green | (white & (V[:, 0] < -6))) & (np.abs(V[:, 0]) < 24) & (V[:, 2] > 40) & (V[:, 2] < TIE_HI + 6) & front
# the bow's tails hang in front of the skirt and are too dark to pass as green; nothing else is that far forward
cloth = cloth | ((V[:, 1] < -14.5) & (V[:, 2] > 50) & (V[:, 2] < TIE_HI - 4) & (np.abs(V[:, 0]) < 24))
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
NB = [[e.other_vert(v).index for e in v.link_edges] for v in bm.verts]
zone = (V[:, 2] > 40) & (V[:, 2] < TIE_HI + 6) & front & (np.abs(V[:, 0]) < 24)
for _ in range(3):                                           # close the holes dark seams and stains leave in the mask
    vote = np.array([np.mean(cloth[n]) if n else 0.0 for n in NB])
    cloth = (cloth | (vote >= 0.6)) & zone
n_cloth = int(cloth.sum())
print('APRON cloth vertices: %d (green %d, towel white %d), z %.1f..%.1f, x %.1f..%.1f'
      % (n_cloth, int((cloth & green).sum()), int((cloth & white & ~green).sum()),
         V[cloth, 2].min(), V[cloth, 2].max(), V[cloth, 0].min(), V[cloth, 0].max()))
if n_cloth < 500 or V[cloth, 2].min() > 70:
    raise SystemExit('REFUSING: that does not look like an apron skirt')

# ---------- the two bones ----------
band = cloth & (V[:, 2] > TIE_LO) & (V[:, 2] < TIE_HI)
hinge_y = float(np.percentile(V[band, 1], 30))               # the front of the waist, where the skirt starts to hang
hip = [b for b in arm.data.bones if b.parent and b.parent.parent is None][0].name
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
AI = arm.matrix_world.inverted()
bot = float(V[cloth, 2].min())
for side, sx in (('L', 1.0), ('R', -1.0)):
    eb = arm.data.edit_bones.new('Apron_' + side)
    eb.parent = arm.data.edit_bones[hip]
    eb.use_connect = False
    eb.head = AI @ Vector((sx * 8.0 * s, hinge_y * s, (TIE_HI - 2.0) * s))
    eb.tail = AI @ Vector((sx * 8.0 * s, hinge_y * s, bot * s))
    eb.roll = 0.0
bpy.ops.object.mode_set(mode='OBJECT')
print('APRON bones Apron_L / Apron_R under %s, hinge at y %.1f z %.1f, %.1f cm long' % (hip, hinge_y, TIE_HI - 2.0, TIE_HI - 2.0 - bot))

# ---------- cut the skirt free where the generator stitched it to the trousers ----------
# The model is one connected surface: along its side edges and under the towel the skirt shares vertices with the
# trouser leg behind it. A skirt that swings while those stay on the thigh drags webs of cloth 30 cm long. So every
# face that is wholly skirt, below the waist tie, is split away from its non-skirt neighbours. The shared vertices
# are duplicated: the skirt keeps one copy, the trousers keep the other with the weights they always had. Above
# the tie nothing is cut - there the two sides carry the same weights, so the surface stays whole.
fl = bm.verts.layers.int.new('cloth')
ft = bm.faces.layers.int.new('skirt')
for v in bm.verts:
    v[fl] = int(cloth[v.index])
free = []
for f in bm.faces:
    if all(v[fl] for v in f.verts) and f.calc_center_median().z * (1.0 if abs(MW.to_scale().z - 1) < 1e-6 else MW.to_scale().z) / s < TIE_LO:
        f[ft] = 1
        free.append(f)
n0 = len(bm.verts)
bmesh.ops.split(bm, geom=free)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
in_skirt = np.zeros(len(bm.verts), bool)
for f in bm.faces:
    if f[ft]:
        for v in f.verts:
            in_skirt[v.index] = True
flag = np.array([v[fl] for v in bm.verts], bool)
bm.verts.layers.int.remove(fl)
bm.faces.layers.int.remove(ft)
bm.to_mesh(me)
me.update()
Vw = np.array([MW @ v.co for v in me.vertices])
V = Vw / s
cloth = flag & (in_skirt | (V[:, 2] >= TIE_LO))
NB = [[e.other_vert(v).index for e in v.link_edges] for v in bm.verts]
print('APRON cut free: %d skirt faces, %d seam vertices duplicated (%d -> %d vertices)' % (len(free), len(bm.verts) - n0, n0, len(bm.verts)))

# ---------- the weights ----------
def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# No ramp. A ramp from "all apron" into the body's own weights was tried twice (9 cm, then 5 cm) and both left
# hundreds of stretched edges at the waist in a plain walk, because the body there is weighted to the THIGHS. The
# free skirt is wholly the apron bones'; its top edge sits within a few centimetres of the hinge, so it barely
# moves, and the waistband above it keeps the weights it always had.
share = np.where(in_skirt & cloth, 1.0, 0.0)
left = smooth(V[:, 0], -BLEND_X, BLEND_X)
_gn = {g.index: g.name for g in mesh.vertex_groups}
def gname_all(i): return _gn[i]
gL = mesh.vertex_groups.new(name='Apron_L')
gR = mesh.vertex_groups.new(name='Apron_R')
before = {}
gname = {g.index: g.name for g in mesh.vertex_groups}
# The waistband and the top of the skirt were weighted to the THIGHS by the generator, like the rest of it. Whatever
# part of a cloth vertex the apron bones do not take belongs to the hips, never to a leg: a ramp from apron to hip
# is a hinge, a ramp from apron to thigh is a tear every time that leg swings back.
hip_g = mesh.vertex_groups[hip]
legs = set()
def _under(b):
    legs.add(b.name)
    for c in b.children: _under(c)
for c in arm.data.bones[hip].children:
    if (arm.matrix_world @ c.tail_local).z < (arm.matrix_world @ c.head_local).z - 0.2 * s and not c.name.startswith('Apron_'):
        _under(c)
moved = 0.0
for i in np.where(cloth & in_skirt)[0]:                     # only the part that was cut free: above it the cloth is still
    v = me.vertices[int(i)]                                 # one surface with the trousers and must move as they do
    t = 0.0
    for g in v.groups:
        if gname_all(g.group) in legs:
            t += g.weight; g.weight = 0.0
    if t > 0:
        hip_g.add([int(i)], t, 'ADD'); moved += t
print('APRON cloth weight moved from the legs to the hips: %.1f (leg bones: %d)' % (moved, len(legs)))
for i in np.where(share > 1e-4)[0]:
    v = me.vertices[int(i)]
    a = float(share[i])
    for g in v.groups:
        before[gname[g.group]] = before.get(gname[g.group], 0.0) + g.weight * a
        g.weight *= (1.0 - a)
    if a * left[i] > 1e-5:
        gL.add([int(i)], a * float(left[i]), 'REPLACE')
    if a * (1.0 - left[i]) > 1e-5:
        gR.add([int(i)], a * float(1.0 - left[i]), 'REPLACE')
bad = 0
for v in me.vertices:
    t = sum(g.weight for g in v.groups)
    if abs(t - 1.0) > 1e-3:
        bad += 1
print('APRON re-weighted %d vertices; weight taken from: %s' % (int((share > 1e-4).sum()), sorted(((round(x, 1), k) for k, x in before.items()), reverse=True)[:6]))
print('APRON vertices whose weights no longer sum to 1: %d' % bad)

if RENDER:
    # the mask, painted on the model, to LOOK at: skirt share in red over grey
    cl = me.color_attributes.new('ApronShare', 'FLOAT_COLOR', 'POINT')
    for i, c in enumerate(cl.data):
        a = float(share[i])
        c.color = (0.45 + 0.55 * a, 0.45 * (1 - a), 0.45 * (1 - a), 1)
    me.color_attributes.active_color = cl
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'FLAT'
    sc.display.shading.color_type = 'VERTEX'
    sc.render.resolution_x, sc.render.resolution_y = 520, 700
    cam = bpy.data.objects.new('C', bpy.data.cameras.new('C'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 120 * s
    cam.data.clip_end = 5000 * s
    import os
    for tag, d in (('front', (0, -1, 0)), ('side', (1, 0, 0)), ('back', (0, 1, 0))):
        ctr = Vector((0, 0, 75 * s))
        cam.location = ctr + Vector(d) * 800 * s
        cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.splitext(RENDER)[0] + '_' + tag + '.png'
        bpy.ops.render.render(write_still=True)
    me.color_attributes.remove(cl)

bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=False,
                         mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
print('APRON exported %s (%d bones)' % (OUT, len(arm.data.bones)))
