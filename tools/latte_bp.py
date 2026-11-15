"""Latte-art mini game: make BP_LatteGame's shell (the actor and its parts). The graphs are written with the MCP.

    py <repo>/tools/latte_bp.py make      create the Blueprint and its components (refuses if it exists)
    py <repo>/tools/latte_bp.py parts     re-apply every part's mesh, size and position (safe to repeat)
Result: <project>/Saved/jcpy/latte_bp.txt.  Play mode must be stopped.

The actor's origin is the centre of the coffee's surface. +X is "up the screen", +Y is "right on screen".
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'latte_bp.txt')
BP = '/Game/Game/Blueprints/BP_LatteGame'
log = []
eal = unreal.EditorAssetLibrary
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
R = unreal.Rotator
V = unreal.Vector


def say(s):
    log.append(str(s))
    unreal.log('[latte-bp] %s' % s)


def mesh(n):
    return eal.load_asset(n if n.startswith('/') else '/Engine/BasicShapes/%s' % n)


# name: (class, mesh, material, location, rotation(roll,pitch,yaw), scale)
PARTS = [
    ('Cam', unreal.CameraComponent, None, None, V(-34, 0, 74), R(roll=0, pitch=-68, yaw=0), V(1, 1, 1)),
    ('Cup', unreal.StaticMeshComponent, '/Game/Game/Imported/Latte/SM_LatteCup', '/Game/Game/Materials/Latte/M_LatteCup', V(0, 0, 0), R(roll=0, pitch=0, yaw=0), V(1, 1, 1)),
    ('Saucer', unreal.StaticMeshComponent, '/Game/Game/Imported/Latte/SM_LatteSaucer', '/Game/Game/Materials/Latte/M_LatteCup', V(0, 0, 0), R(roll=0, pitch=0, yaw=0), V(1, 1, 1)),
    ('Surface', unreal.StaticMeshComponent, 'Plane', '/Game/Game/Materials/Latte/MI_LatteSurface_A', V(0, 0, 0), R(roll=0, pitch=0, yaw=0), V(0.12, 0.12, 1)),
    ('Pitcher', unreal.StaticMeshComponent, '/Game/Game/Imported/Latte/SM_LattePitcher', '/Game/Game/Materials/Latte/M_LatteSteel', V(0, 0, 8), R(roll=0, pitch=0, yaw=0), V(1, 1, 1)),
    ('Stream', unreal.StaticMeshComponent, '/Game/Game/Imported/Latte/SM_LatteStream', '/Game/Game/Materials/Latte/M_LatteMilk', V(0, 0, 0), R(roll=0, pitch=0, yaw=0), V(0.6, 0.6, 8)),
    ('Guide', unreal.StaticMeshComponent, 'Plane', '/Game/Game/Materials/Latte/MI_LatteSurface_A', V(1.5, -17.5, 0.2), R(roll=0, pitch=0, yaw=0), V(0.075, 0.075, 1)),
    ('GuideLabel', unreal.TextRenderComponent, None, None, V(-4.2, -17.5, 0.4), R(roll=0, pitch=68, yaw=180), V(1, 1, 1)),
    ('FillBar', unreal.StaticMeshComponent, 'Cube', '/Game/Game/Materials/Latte/M_LatteBar', V(-4.2, -10, 0), R(roll=0, pitch=0, yaw=0), V(0.036, 0.008, 0.004)),
    ('FillMark', unreal.StaticMeshComponent, 'Cube', '/Game/Game/Materials/Latte/M_LatteMilk', V(2.0, -10.9, 0), R(roll=0, pitch=0, yaw=0), V(0.004, 0.03, 0.004)),
    ('Prompt', unreal.TextRenderComponent, None, None, V(-15.0, 0, 2), R(roll=0, pitch=68, yaw=180), V(1, 1, 1)),
    ('WorldText', unreal.TextRenderComponent, None, None, V(0, 0, 48), R(roll=0, pitch=0, yaw=0), V(1, 1, 1)),
    ('Status', unreal.TextRenderComponent, None, None, V(10.5, 0, 2), R(roll=0, pitch=68, yaw=180), V(1, 1, 1)),
]


def handles(bp):
    out = {}
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        o = lib.get_object(lib.get_data(h))
        if o is not None:
            out.setdefault(o.get_name().replace('_GEN_VARIABLE', ''), []).append((h, o))
    return out


def apply(bp):
    hs = handles(bp)
    for name, cls, m, mat, loc, rot, scale in PARTS:
        for h, o in hs.get(name, []):
            if m:
                o.set_editor_property('static_mesh', mesh(m))
                o.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                o.set_editor_property('cast_shadow', False)
                if mat:
                    o.set_editor_property('override_materials', [eal.load_asset(mat)])     # set_material() does not stick on a template
            if cls is unreal.TextRenderComponent:
                o.set_editor_property('horizontal_alignment', unreal.HorizTextAligment.EHTA_CENTER)
                o.set_editor_property('vertical_alignment', unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
                o.set_editor_property('world_size', {'Prompt': 1.05, 'WorldText': 11.0, 'GuideLabel': 1.3}.get(name, 1.9))
                if name == 'WorldText':
                    o.set_editor_property('text_render_color', unreal.Color(b=10, g=16, r=30, a=255))
                if name != 'WorldText':
                    o.set_editor_property('text_render_color', unreal.Color(b=12, g=22, r=48, a=255))
                o.set_editor_property('text', unreal.Text('GOAL' if name == 'GuideLabel' else ' '))
            if cls is unreal.CameraComponent:
                o.set_editor_property('field_of_view', 42.0)
            o.set_editor_property('relative_location', loc)
            o.set_editor_property('relative_rotation', rot)
            o.set_editor_property('relative_scale3d', scale)
        say('%-8s handles %d' % (name, len(hs.get(name, []))))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'parts'
    bp = eal.load_asset(BP)
    if mode == 'make':
        if bp is not None:
            say('REFUSING: %s exists' % BP); return
        f = unreal.BlueprintFactory()
        f.set_editor_property('parent_class', unreal.Actor)
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_LatteGame', '/Game/Game/Blueprints', unreal.Blueprint, f)
    if bp is None:
        say('no blueprint'); return
    if True:
        root = sds.k2_gather_subobject_data_for_blueprint(bp)[0]
        have = handles(bp)
        for name, cls, *_ in PARTS:
            if name in have:
                continue
            p = unreal.AddNewSubobjectParams()
            p.set_editor_property('parent_handle', root)
            p.set_editor_property('new_class', cls)
            p.set_editor_property('blueprint_context', bp)
            h, fail = sds.add_new_subobject(p)
            sds.rename_subobject(h, unreal.Text(name))
            say('added %s %s' % (name, fail))
    apply(bp)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    say('SAVED %s' % unreal.EditorLoadingAndSavingUtils.save_packages([bp.get_outermost()], False))


try:
    main()
except Exception:
    import traceback
    say(traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
