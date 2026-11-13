"""Puts the city into Lvl_JumpCut from Art/Blender/export/City/city_layout.json.

RUN THIS ON THE BUILDER (GameStation, or Justin's Mac), in the editor with Play mode stopped:
    py C:/Users/thecl/code/jump-cut/tools/jumpcut_city_place.py

Steps it expects to have happened first:
  1. git pull with UNREAL CLOSED (this moves .uasset/LFS binaries - the trap this project has hit before).
  2. Copy Art/Blender/export/City/ into JumpCut/Content/Game/Imported/City/ with Unreal OPEN, and let
     Interchange auto-import the FBXs. That is the same route the characters came in by; auto-import is on
     for FBX in this project (it is only .glb that it ignores).
  3. Then run this.

WHAT IT DOES, and what it deliberately does not:
  * It only ever adds or removes actors carrying the tag 'JC_City'. Run it twice and you get one city, not
    two - it clears its own tag first, exactly the way tools/c1_layout.py does.
  * It NEVER touches a C1_Layout actor, the player, the floor, the sun, the gates, the boss or any marker.
    The grey boxes the city supersedes are HIDDEN, not deleted, and only when you ask for it
    (`py ... jumpcut_city_place.py hide`), so one line puts them back.
  * It does NOT save. Saving is the builder's call, and in this project saving the wrong thing has cost a
    whole lane of work before. Look at it in the viewport first, then save the level yourself.

HONEST STATUS: written on M Station, which is a maker and has no Unreal, so this script has NOT been run.
The geometry it places is verified (every model built, measured and rendered; every placement checked for
collisions by tools/jumpcut_city_layout.py), but the Unreal calls in here are written from this repo's own
existing editor scripts and have not been executed. Expect to fix a line, not a layout.

    py ... jumpcut_city_place.py            place the city
    py ... jumpcut_city_place.py hide       place it, and hide the grey boxes it replaces
    py ... jumpcut_city_place.py clear      remove every JC_City actor and stop
    py ... jumpcut_city_place.py show       un-hide the grey boxes and stop
"""
import json
import os
import sys

import unreal

TAG = 'JC_City'
MESHES = '/Game/Game/Imported/City/'
MATDIR = '/Game/Game/Materials/City'

# A flat base colour per material slot. The level wears a cel-shaded post-process, so a flat colour is the
# right input: it gets banded and outlined by MI_AnimeLook_JumpCut rather than fighting it. These are the
# same values the Blender check renders used, so the level should look like the sheets in Art/Blender/cache/.
COLOURS = {
    'MS_CityWall': (0.78, 0.75, 0.70), 'MS_CityBrick': (0.42, 0.24, 0.19),
    'MS_CityConcrete': (0.58, 0.58, 0.56), 'MS_CityTrim': (0.11, 0.12, 0.14),
    'MS_CityMetal': (0.55, 0.57, 0.60), 'MS_CityGlass': (0.22, 0.38, 0.47),
    'MS_CitySignA': (0.95, 0.42, 0.18), 'MS_CitySignB': (0.25, 0.72, 0.90),
    'MS_CityAccent': (0.72, 0.16, 0.20), 'MS_CityWood': (0.47, 0.31, 0.18),
    'MS_CityRoof': (0.23, 0.23, 0.25), 'MS_CityCloth': (0.80, 0.74, 0.62),
}
EMISSIVE = ('MS_CitySignA', 'MS_CitySignB')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT = os.path.join(REPO, 'Art', 'Blender', 'export', 'City', 'city_layout.json')

log = []


def say(msg):
    log.append(msg)
    unreal.log(msg)
    print(msg)


def ensure_materials():
    """Make one flat material per slot name, once. Returns {slot name: material}, skipping any it cannot
    build - a missing material costs you a grey building, not a failed run."""
    out = {}
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary
    for slot, rgb in COLOURS.items():
        path = '%s/M_%s' % (MATDIR, slot[3:])
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            out[slot] = unreal.load_asset(path)
            continue
        try:
            mat = at.create_asset('M_' + slot[3:], MATDIR, unreal.Material, unreal.MaterialFactoryNew())
            col = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -380, 0)
            col.set_editor_property('parameter_name', 'BaseColor')
            col.set_editor_property('default_value', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
            mel.connect_material_property(col, '', unreal.MaterialProperty.MP_BASE_COLOR)
            rough = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -380, 180)
            rough.set_editor_property('parameter_name', 'Roughness')
            rough.set_editor_property('default_value', 0.35 if slot == 'MS_CityGlass' else 0.85)
            mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
            if slot in EMISSIVE:
                em = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -380, 360)
                em.set_editor_property('parameter_name', 'Emissive')
                em.set_editor_property('default_value',
                                       unreal.LinearColor(rgb[0] * 2.2, rgb[1] * 2.2, rgb[2] * 2.2, 1.0))
                mel.connect_material_property(em, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
            mel.recompile_material(mat)
            # Save the material itself. The level is deliberately left unsaved for the builder to judge, but a
            # brand-new material asset that is only in memory is lost on close, and then every actor placed
            # below is pointing at nothing. Creating an asset and saving that asset is not the same act as
            # saving the level.
            unreal.EditorAssetLibrary.save_asset(path)
            out[slot] = mat
        except Exception as e:                                   # noqa: BLE001 - report and carry on
            say('could not make a material for %s: %s' % (slot, e))
    say('materials ready: %d of %d' % (len(out), len(COLOURS)))
    return out


def slot_names(mesh):
    try:
        return [str(sm.get_editor_property('material_slot_name'))
                for sm in mesh.get_editor_property('static_materials')]
    except Exception:                                            # noqa: BLE001
        return []


def clear(eas):
    n = 0
    for a in list(eas.get_all_level_actors()):
        if unreal.Name(TAG) in a.get_editor_property('tags'):
            eas.destroy_actor(a)
            n += 1
    say('removed %d earlier %s actors' % (n, TAG))
    return n


GREYBOX_HIDDEN_TAG = 'JC_CityHidGreybox'


def set_greybox(eas, hidden, labels):
    n = 0
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label() in labels:
            a.set_editor_property('hidden_in_game', hidden)
            a.set_is_temporarily_hidden_in_editor(hidden)
            n += 1
    say('%s %d grey-box actors' % ('hid' if hidden else 'un-hid', n))
    return n


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else 'place').lower()
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_editor_world()
    if world.get_name() != 'Lvl_JumpCut' or ues.get_game_world() is not None:
        raise RuntimeError('wrong world (%s) or PIE is running - stop Play first' % world.get_name())
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    doc = json.load(open(LAYOUT, encoding='utf-8'))
    say('layout: %d actors, generated %s' % (len(doc['actors']), doc.get('generated_at_pacific', '?')))

    if mode == 'clear':
        clear(eas)
        say('done. Nothing else was touched. Save the level yourself if you want this kept.')
        return
    if mode == 'show':
        set_greybox(eas, False, set(doc['supersedes_greybox']))
        return

    clear(eas)
    mats = ensure_materials()

    placed, missing, by_model = 0, {}, {}
    cache = {}
    for a in doc['actors']:
        path = MESHES + a['model'] + '.' + a['model']
        mesh = cache.get(path, 'nope')
        if mesh == 'nope':
            mesh = unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
            cache[path] = mesh
        if mesh is None:
            missing[a['model']] = missing.get(a['model'], 0) + 1
            continue
        act = eas.spawn_actor_from_class(unreal.StaticMeshActor,
                                         unreal.Vector(a['x'], a['y'], a['z']),
                                         unreal.Rotator(roll=0.0, pitch=0.0, yaw=a['yaw']))
        comp = act.static_mesh_component
        comp.set_mobility(unreal.ComponentMobility.STATIC)
        comp.set_static_mesh(mesh)
        for i, nm in enumerate(slot_names(mesh)):
            m = mats.get(nm)
            if m is not None:
                comp.set_material(i, m)
        act.set_actor_label(a['label'])
        act.set_editor_property('tags', [unreal.Name(TAG)])
        placed += 1
        by_model[a['model']] = by_model.get(a['model'], 0) + 1

    say('placed %d actors from %d distinct meshes' % (placed, len(by_model)))
    if missing:
        say('MISSING MESHES - import Art/Blender/export/City/ into %s first:' % MESHES)
        for m in sorted(missing):
            say('   %s  (%d placements waiting on it)' % (m, missing[m]))

    if mode == 'hide':
        set_greybox(eas, True, set(doc['supersedes_greybox']))
    else:
        say('grey boxes left visible. Run with "hide" to hide the %d they replace: %s'
            % (len(doc['supersedes_greybox']), ', '.join(doc['supersedes_greybox'])))

    say('NOT SAVED. Look at it, then save the level yourself (and lock the .umap actor files first).')
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
    with open(os.path.join(out, 'jc_city_place.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


main()
