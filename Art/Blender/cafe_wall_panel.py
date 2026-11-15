"""SM_CafeWallPanel - the intact west wall of the cafe, the piece the car drives through.

WHY THIS EXISTS. The cafe's hole is modelled INTO SM_CafeShell, so there is no intact state to show
before the crash. Beat 1's opening covered it with B1_Cine_WallPatch: an engine Cube scaled flat and
painted M_CafeWall. On screen that reads as exactly what it is - a block - which is what the Team
Owner reported on 2026-11-15. This is the real thing in its place: a wall section with a brick street
face, the cafe's own plaster on the inside, a skirting, the same dado rail the north wall carries at
the same height, and two framed panels. Cut into a Geometry Collection it is also the thing the car
can break, so the wall comes apart instead of vanishing on a frame.

MEASURED, NOT ASSUMED. The opening in SM_CafeShell was read back out of the shipped mesh
(tools/b1z_wallgeo.py, Saved/jcpy/b1z_wallgeo.json): the brick on the wall plane stops at
UNREAL y -165.0 and restarts at y +135.0, and the lintel above the hole sits at z 255.0. Blender +Y
is Unreal -Y (jumpcut_city_kit.main), so a 300 x 255 cm opening at Unreal x -630..-615.
A trace cannot find it: C1_Cafe_WallW, a grey-box collider from the Thursday build, still stands
30 cm thick across the whole wall.

The panel is built CENTRED ON ITS OWN ORIGIN, unlike the kit's room-sized pieces, so one placement
number puts it in the hole: Unreal (-622.1, -15.0, 127.3).

INSET BY 4 mm, deliberately. Every face of this panel is offset 4 mm from the shell's own faces
rather than flush with them. Flush is the exact z-fight that caused issue #67 and was fixed in the
kit the day before; adding a new one here would have put it straight back.

    blender -b -P Art/Blender/cafe_wall_panel.py
Writes Art/Blender/export/Beat1/SM_CafeWallPanel.fbx and prints WALLPANEL_REPORT <json>.
Touches neither jumpcut_city_kit.py nor city_models.json: the city kit is GameStation's lane.
"""
import bpy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jumpcut_city_kit as kit

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(REPO, 'Art', 'Blender', 'export', 'Beat1')
NAME = 'SM_CafeWallPanel'

# the opening, in UNREAL centimetres, read out of SM_CafeShell
HOLE_X = (-630.0, -615.0)
HOLE_Y = (-165.0, 135.0)
HOLE_Z = (0.0, 255.0)
INSET = 0.4          # cm; 4 mm, the kit's own PROUD distance

T = (HOLE_X[1] - HOLE_X[0]) / 100.0                                  # 0.15 m thick
W = (HOLE_Y[1] - HOLE_Y[0] - 2 * INSET) / 100.0                      # 2.992 m wide
H = (HOLE_Z[1] - HOLE_Z[0] - INSET) / 100.0                          # 2.546 m tall


def build():
    kit.fresh()
    b = kit.B(seed=71)
    hx, hy, hz = T / 2.0, W / 2.0, H / 2.0
    # -x is the street face, +x is the room. Brick box with its room face left open.
    b.box((-hx, -hy, -hz), (hx, hy, hz), 'MS_CityBrick', 1.0, skip=('xhi',))
    # the room face: the cafe's own plaster, wound to face +x
    b.quad([(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)], 'MS_CafeWall', 0.95)
    # skirting board, 12 cm tall, 2 cm proud
    b.box((hx, -hy, -hz), (hx + 0.02, hy, -hz + 0.12), 'MS_CityWood', 0.8)
    # the dado rail, at the SAME height as the north wall's (world z 0.95..1.03), 4 cm proud
    b.box((hx, -hy, 0.95 - hz), (hx + 0.04, hy, 1.03 - hz), 'MS_CityWood', 0.8)
    # two framed panels above the rail, same idea as the north wall's six
    for cy in (-0.6, 0.6):
        b.box((hx, cy - 0.5, 1.25 - hz), (hx + 0.03, cy + 0.5, min(2.45, H) - hz), 'MS_CityWood', 0.7)
    o = b.finish(NAME)
    return o, b


def main():
    o, b = build()
    os.makedirs(OUT, exist_ok=True)
    for x in bpy.context.scene.objects:
        x.select_set(x is o)
    bpy.context.view_layer.objects.active = o
    fbx = os.path.join(OUT, NAME + '.fbx')
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={'MESH'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
                             axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE',
                             add_leaf_bones=False, bake_anim=False, embed_textures=False,
                             colors_type='SRGB')
    me = o.data
    me.calc_loop_triangles()
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    rep = {
        'name': NAME,
        'fbx': fbx,
        'verts': len(me.vertices),
        'tris': len(me.loop_triangles),
        'slots': [m.name for m in me.materials],
        'local_cm': {'x': [round(min(xs) * 100, 2), round(max(xs) * 100, 2)],
                     'y': [round(min(ys) * 100, 2), round(max(ys) * 100, 2)],
                     'z': [round(min(zs) * 100, 2), round(max(zs) * 100, 2)]},
        # where the actor goes in Unreal; local Blender +Y maps to Unreal -Y, and the panel's
        # content is symmetric in y, so the flip changes nothing about the shape.
        'unreal_place': [round((HOLE_X[0] + HOLE_X[1]) / 2.0 + INSET, 2),
                         round((HOLE_Y[0] + HOLE_Y[1]) / 2.0, 2),
                         round(HOLE_Z[0] + (HOLE_Z[1] - HOLE_Z[0] - INSET) / 2.0, 2)],
        'proud_faces': b.proud,
    }
    print('WALLPANEL_REPORT ' + json.dumps(rep))


if __name__ == '__main__':
    main()
