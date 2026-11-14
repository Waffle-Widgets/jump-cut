# Bake a Meshy character's base colour onto the REMESHED, RIGGED body. Headless:
#   blender -b --factory-startup --python Art/Blender/bake_meshy_basecolor.py -- <textured.glb> <rigged.fbx> <out.png> [res]
#
# WHY THIS EXISTS. Meshy's remesh step DISCARDS the texture. Rigging runs on the remeshed
# asset, so the asset you can actually animate is untextured - it renders plain grey in
# Meshy's own viewer, and its FBX export embeds only a tangent-space normal map
# (texture_0_normal.png) with no colour map at all. That is not a download that was missed;
# there is no colour map on that asset to download.
#
# THE TRAP, measured on Sat 2026-11-14. The colour DOES exist on the pre-remesh 365k asset,
# and its GLB export carries it (glTF image `texture_0`, wired to baseColorTexture). But the
# remesh regenerates UVs, so that map and the rigged mesh are in DIFFERENT UV spaces.
# Dropping the high-poly texture straight onto the rigged mesh renders as camouflage noise -
# a plausible-looking atlas, a ruined character, and nothing in the pipeline errors. Proven
# by rendering it: jc-run/walker_uvtest_front.png.
#
# SO: bake high-poly -> low-poly, the standard retopology transfer. The high-poly is made to
# EMIT its base colour and baked with `EMIT` selected-to-active, which copies the colour
# exactly rather than re-lighting it (a DIFFUSE bake would fold in a light rig nobody chose).
# Cycles, 1 sample - with emission there is nothing to converge.
#
# ALIGNMENT IS THE ONE THING THAT CAN SILENTLY GO WRONG. Meshy's two exports are not in the
# same units or origin: the textured GLB comes out 1.902 m tall centred on the origin, the
# rigged FBX 1.75 m with its feet at z = 0. So the source is uniformly scaled by the height
# ratio and moved onto the target's XY centre and floor before baking. The script PRINTS the
# per-axis residual afterwards - on CafeWalkerV2 it is under 2 mm. If that number is large,
# the ray cast misses and you get bald patches, so read it; do not assume it.
#
# LOOK AT THE RESULT. Re-render the rigged FBX with the baked map front and back before
# believing it. The back is the half Meshy invents from a front-only reference, and it is
# where CafeCoworkerV2's forbidden cross-back X straps (#101) show up.

import bpy
import sys
import os

argv = sys.argv[sys.argv.index('--') + 1:]
glb, fbx, outpng = argv[0], argv[1], argv[2]
res = int(argv[3]) if len(argv) > 3 else 2048

bpy.ops.wm.read_factory_settings(use_empty=True)


def bounds(o):
    xs = []
    ys = []
    zs = []
    for v in o.data.vertices:
        w = o.matrix_world @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


# --- source: the textured high-poly, the only asset that has the colour
bpy.ops.import_scene.gltf(filepath=glb)
src = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
sb = bounds(src)
print('SRC %s verts=%d bounds=%s' % (src.name, len(src.data.vertices),
                                     [round(v, 3) for v in sb]))

# --- target: the remeshed, rigged body, whose UVs the game will sample
before = set(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=fbx)
tgt = [o for o in bpy.context.scene.objects if o not in before and o.type == 'MESH'][0]
tb = bounds(tgt)
print('TGT %s verts=%d bounds=%s' % (tgt.name, len(tgt.data.vertices),
                                     [round(v, 3) for v in tb]))

sh, th = sb[5] - sb[4], tb[5] - tb[4]
s = th / sh
src.scale = (s, s, s)
bpy.context.view_layer.update()
sb2 = bounds(src)
src.location = (src.location.x + ((tb[0] + tb[1]) / 2 - (sb2[0] + sb2[1]) / 2),
                src.location.y + ((tb[2] + tb[3]) / 2 - (sb2[2] + sb2[3]) / 2),
                src.location.z + (tb[4] - sb2[4]))
bpy.context.view_layer.update()
sb3 = bounds(src)
resid = [round(sb3[i] - tb[i], 4) for i in range(6)]
print('HEIGHTS src=%.4f tgt=%.4f scale=%.4f' % (sh, th, s))
print('ALIGN residual per axis (m): %s   <- READ THIS' % resid)
if max(abs(r) for r in resid) > 0.02:
    print('WARNING: source and target are more than 2 cm apart somewhere. The bake rays '
          'will miss and leave bald patches. Check the two exports are the same character.')

# --- make the source emit its base colour, so the bake copies rather than relights
smat = src.data.materials[0]
nt = smat.node_tree
texnode = None
for n in nt.nodes:
    if n.type == 'TEX_IMAGE':
        for l in n.outputs['Color'].links:
            if l.to_socket.name == 'Base Color':
                texnode = n
if texnode is None:
    texnode = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
print('SRC colour map: %s %s' % (texnode.image.name, tuple(texnode.image.size)))
emit = nt.nodes.new('ShaderNodeEmission')
out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
nt.links.new(texnode.outputs['Color'], emit.inputs['Color'])
nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])

# --- blank image on the target's own UVs
img = bpy.data.images.new('BakeTex', res, res, alpha=False)
tmat = bpy.data.materials.new('BakeMat')
tmat.use_nodes = True
bakenode = tmat.node_tree.nodes.new('ShaderNodeTexImage')
bakenode.image = img
tmat.node_tree.nodes.active = bakenode
bakenode.select = True
tgt.data.materials.clear()
tgt.data.materials.append(tmat)

scn = bpy.context.scene
scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = 1
scn.render.bake.use_selected_to_active = True
scn.render.bake.cage_extrusion = 0.05
scn.render.bake.max_ray_distance = 0.10
scn.render.bake.margin = 16          # bleed past the island edge, or seams show as dark lines
scn.render.bake.use_clear = True

bpy.ops.object.select_all(action='DESELECT')
src.select_set(True)
tgt.select_set(True)
bpy.context.view_layer.objects.active = tgt
print('BAKING %d x %d ...' % (res, res))
bpy.ops.object.bake(type='EMIT')

img.filepath_raw = outpng
img.file_format = 'PNG'
img.save()
print('WROTE %s (%d bytes)' % (outpng, os.path.getsize(outpng)))
