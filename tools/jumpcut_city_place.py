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
    py ... jumpcut_city_place.py add        place ONLY the layout actors that are not in the level yet, then
                                            hide. Use this when the city is already placed and saved and
                                            the layout has grown: it leaves the existing JC_City actors and
                                            their packages alone instead of deleting and re-making all of them
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
    # Added Fri Nov 13 with the cafe dressing and the street life. MS_CityLeaf is the first green in the
    # project: until now the kit's only foliage was the planter shrub and it was painted MS_CityCloth,
    # which is beige, so nothing in the city was alive. The two MS_Cafe* slots exist so the room the
    # player spends beat 1 in can be warm without repainting the whole street with it.
    # NOTE, and it matters if you ever want to change one of these: a value here is only read when the
    # material is CREATED. There is no supported way to set a Material's default vector parameter from
    # Python in UE 5.8 - there is a getter, get_material_default_vector_parameter_value, and no setter,
    # and the 'expressions' property that would let you reach the node by hand is protected and raises.
    # So on a machine that already has the material, editing this table does nothing at all. To change a
    # colour for real: delete the M_* asset and re-run, or edit it in the material editor.
    'MS_CityLeaf': (0.29, 0.46, 0.22), 'MS_CityLantern': (0.90, 0.26, 0.19),
    'MS_CafeWall': (0.93, 0.85, 0.72), 'MS_CafeFloor': (0.58, 0.39, 0.23),
}
EMISSIVE = ('MS_CitySignA', 'MS_CitySignB', 'MS_CityLantern')

# Slots whose geometry is a THIN THING standing for a thick one: a leaf, a cloth panel, a paper lantern.
# The kit draws those as a single quad, so Unreal culls the back face and the thing disappears from one
# side. Measured on Fri Nov 13: every street tree in the lane had a full canopy seen from the south and a
# bare trunk seen from the north, with no error, no warning and correct materials on the actor. Doubling
# the geometry does NOT fix it - the kit's own weld pass merges the two windings back into one face - so
# it is fixed here, where one flag does it for every mesh that uses the slot.
TWO_SIDED = ('MS_CityLeaf', 'MS_CityCloth')

# Leaves need one more thing than two-sidedness. With a plain Default-Lit two-sided material, the face
# pointing AWAY from the sun receives nothing, and the cel pass bands "nothing" to flat black - so the
# first two-sided street tree read as a black blob with a few green cards on the sunny side, which is
# worse than the bare trunk it replaced. Unreal's Two Sided Foliage shading model is exactly this case:
# it transmits light through the sheet, so a backlit leaf comes out as a lighter green instead of a hole.
# The subsurface colour is the leaf colour lifted, which is what you see when you look up through a tree.
FOLIAGE = {'MS_CityLeaf': (0.58, 0.78, 0.38)}


# Pieces the player is supposed to pass THROUGH. Measured, not guessed: with collision set
# complex-as-simple (which is right for the rest of the kit) the cafe's noren became a solid 150 x 100 cm
# wall at (648, 0) - a cloth door curtain standing across the only exit from the cafe, which blocks the
# demo between beat 1 and beat 2. It renders correctly, so nothing about it looks wrong.
# Collision is switched off on the ACTOR, not on the shared mesh asset: bActorEnableCollision is an actor
# property and serializes, where the component-level flag silently came back after a reload in beat 4.
# The three painted pieces (paving, crossings, road lines) are pictures laid 1 cm over the real floor:
# with collision on, the player would be standing on a second floor the fight was never tuned on.
WALK_THROUGH = {'SM_Noren', 'SM_CableSpan', 'SM_PlazaPaving', 'SM_Crosswalk', 'SM_RoadLines',
                # the cafe's floorboards and its rug are the same kind of thing as the paving: a picture of
                # a surface laid over the real one. With collision on, the boards are a SECOND floor 1.2 cm
                # above the slab every fight in beat 1 was tuned on.
                'SM_CafeFloorBoards', 'SM_CafeRug',
                # a lantern string is a cable with lanterns on it, and the cable is already walk-through
                'SM_LanternString'}

# Models that must KEEP simple collision, because something simulates them. Chaos physics (PR #48,
# tools/unreal_chaos_props.py) gives these three a box and CTF_USE_DEFAULT so a punch can shove them:
# Unreal refuses to simulate a body whose collision is complex-as-simple, and says so only in the log.
# Running this placer after that silently put all three back to complex-as-simple, which would have
# killed the knockable props the next time anything saved them. Keep the two lists in step.
SIMULATED = {'SM_CafeChair', 'SM_TrafficCone', 'SM_TrashBags'}

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT = os.path.join(REPO, 'Art', 'Blender', 'export', 'City', 'city_layout.json')

log = []


def say(msg):
    log.append(msg)
    unreal.log(msg)
    print(msg)


def upgrade(mat, slot, mel, recompile=True):
    """Bring one slot's material up to what TWO_SIDED and FOLIAGE currently say.

    Idempotent, and it repairs a material made before either idea existed - which is the whole point,
    because ensure_materials() otherwise returns early for anything that already exists and a new rule
    never reaches an existing project. It deliberately does NOT touch base colour: see the note on
    COLOURS for why that cannot be done from Python in 5.8.
    Returns True if it changed anything.
    """
    done = False
    sss = FOLIAGE.get(slot)
    if sss is not None and mat.get_editor_property('shading_model') != unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE:
        mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
        ss = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -380, 540)
        ss.set_editor_property('parameter_name', 'Subsurface')
        ss.set_editor_property('default_value', unreal.LinearColor(sss[0], sss[1], sss[2], 1.0))
        mel.connect_material_property(ss, '', unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
        done = True
    if done and recompile:
        mel.recompile_material(mat)
    return done


def ensure_materials():
    """Make one flat material per slot name, once. Returns {slot name: material}, skipping any it cannot
    build - a missing material costs you a grey building, not a failed run."""
    out = {}
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary
    for slot, rgb in COLOURS.items():
        path = '%s/M_%s' % (MATDIR, slot[3:])
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            mat = unreal.load_asset(path)
            # idempotent, and it repairs a material made before TWO_SIDED existed
            if upgrade(mat, slot, mel):
                unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
                say('%s upgraded (two-sided / foliage)' % path)
            out[slot] = mat
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
            upgrade(mat, slot, mel, recompile=False)
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


def remat(eas, mats):
    """Put the right material on every JC_City actor that is already in the level, by SLOT NAME.

    'add' mode deliberately leaves existing actors alone, which is what makes it safe - but a mesh can be
    re-imported with different material slots, and then the actor is still pointing its old materials at
    the new slot indices. That is exactly what happened on Fri Nov 13: SM_CafeShell's walls moved from
    MS_CityWall to MS_CafeWall and SM_Planter's shrub from MS_CityCloth to MS_CityLeaf, so without this the
    cafe would have come back grey and the plants beige and nothing would have looked broken enough to
    investigate. Idempotent, and it only dirties an actor whose material it actually changed.
    """
    changed, pkgs = 0, []
    for a in list(eas.get_all_level_actors()):
        if unreal.Name(TAG) not in a.get_editor_property('tags'):
            continue
        if not isinstance(a, unreal.StaticMeshActor):
            continue
        comp = a.static_mesh_component
        mesh = comp.get_editor_property('static_mesh')
        if mesh is None:
            continue
        touched = False
        for i, nm in enumerate(slot_names(mesh)):
            want = mats.get(nm)
            if want is not None and comp.get_material(i) != want:
                comp.set_material(i, want)
                touched = True
        if touched:
            a.set_actor_transform(a.get_actor_transform(), False, False)   # one-file-per-actor: dirty it
            pkgs.append(a.get_outermost())
            changed += 1
    if pkgs:
        unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
    say('re-materialled %d actors already in the level' % changed)
    return changed


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
            # NOT set_editor_property('hidden_in_game', ...): AActor exposes no property of that name
            # to Python, and it raises. This is the one line the author predicted would need fixing.
            # The setter is the actor-level one, and it serializes - the same distinction beat 4 hit
            # when a component-level collision flag came back after a reload.
            a.set_actor_hidden_in_game(hidden)
            a.set_is_temporarily_hidden_in_editor(hidden)
            n += 1
    say('%s %d grey-box actors' % ('hid' if hidden else 'un-hid', n))
    # Hiding an actor does NOT mark its package dirty, and this map is one-file-per-actor - so without
    # the two lines below the hide lives only in memory and the grey boxes come back on the next load,
    # standing inside the city. Measured: after the first run all 224 new actor packages were dirty and
    # not one of the 8 grey-box packages was. Re-setting the full transform is what dirties it (the same
    # trick the project already uses after ObjectTools.set_properties on a placed actor), and the package
    # then has to be saved on its own because save_dirty_packages never saw it.
    pkgs = []
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label() in labels:
            a.set_actor_transform(a.get_actor_transform(), False, False)
            pkgs.append(a.get_outermost())
    if pkgs:
        unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
        say('saved %d grey-box actor packages so the hide survives a reload' % len(pkgs))
    return n


def set_ground(eas, doc, mats, city):
    """Put the asphalt on the level's floor slabs (city=True) or the grey-box floor back (city=False).

    Written on M Station, which has no builder role, so like the rest of this file it has never been run
    there. The floor actors are found by label; anything missing is reported and skipped, never guessed.
    Same serialization trap as set_greybox: a material set on a placed actor's component does not dirty
    its package on a one-file-per-actor map, so the transform is re-set and the package saved by hand.
    """
    g = doc.get('ground')
    if not g:
        return 0
    mat = mats.get(g['slot']) if city else unreal.load_asset(g['greybox_material'])
    if mat is None:
        say('ground: no material for %s - floor left as it is' % (g['slot'] if city else g['greybox_material']))
        return 0
    labels, pkgs = set(g['labels']), []
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label() in labels and isinstance(a, unreal.StaticMeshActor):
            a.static_mesh_component.set_material(0, mat)
            a.set_actor_transform(a.get_actor_transform(), False, False)
            pkgs.append(a.get_outermost())
            labels.discard(a.get_actor_label())
    if labels:
        say('ground: could not find %s' % ', '.join(sorted(labels)))
    if pkgs:
        unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
    say('ground: %s on %d floor actors' % (mat.get_name(), len(pkgs)))
    return len(pkgs)


def prepare_meshes(models):
    """Interchange turns Nanite ON and builds an auto convex hull. Both are wrong for this kit.

    Nanite: the whole city is 20,615 triangles, so Nanite buys nothing, and its simplified fallback drops
    thin parts - which here is the signage, the cables, the fire escapes, the noren and the bicycles, i.e.
    most of what makes the street read as Tokyo. Same reason the characters have it off.
    Collision: an auto convex hull does not match an L-shaped shophouse or a cafe interior, so the player
    collides with a box that is not the shape they can see. CTF_USE_COMPLEX_AS_SIMPLE is right for static
    level geometry and is what beat 4 settled on for the ruin slabs for exactly this reason.

    Idempotent: it reads before it writes and only saves a mesh it actually changed.
    """
    smes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    nanite_off, collision_fixed = [], []
    for n in sorted(models):
        path = MESHES + n
        mesh = unreal.load_asset(path + '.' + n)
        if mesh is None:
            raise RuntimeError('mesh not imported: %s - copy Art/Blender/export/City/*.fbx into '
                               'JumpCut/Content/Game/Imported/City/ with Unreal open first' % n)
        changed = False
        st = smes.get_nanite_settings(mesh)
        if st.enabled:
            st.enabled = False
            smes.set_nanite_settings(mesh, st, apply_changes=True)
            nanite_off.append(n)
            changed = True
        bs = mesh.get_editor_property('body_setup')
        if bs is not None and n in SIMULATED:
            pass          # leave it alone - see SIMULATED above
        elif bs is not None:
            flag = unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
            if bs.get_editor_property('collision_trace_flag') != flag:
                bs.set_editor_property('collision_trace_flag', flag)
                collision_fixed.append(n)
                changed = True
        if changed:
            unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
    say('meshes prepared: Nanite off on %d, collision set complex-as-simple on %d, of %d'
        % (len(nanite_off), len(collision_fixed), len(models)))
    return nanite_off, collision_fixed


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
        set_ground(eas, doc, {}, False)
        return

    existing = set()
    if mode == 'add':
        existing = {a.get_actor_label() for a in eas.get_all_level_actors()
                    if unreal.Name(TAG) in a.get_editor_property('tags')}
        say('add: %d %s actors already in the level are left alone' % (len(existing), TAG))
    else:
        clear(eas)
    # The Blueprint meshes (gate, checkpoint, shrapnel) are not placed by this script - they go inside
    # Blueprints, see 'blueprint_meshes' in the layout - but they need the same Nanite and collision
    # treatment, and the gate in particular is a wall: without collision the player walks out of the fight.
    bp_meshes = {m for m in doc.get('blueprint_meshes', {})
                 if unreal.EditorAssetLibrary.does_asset_exist(MESHES + m)}
    for m in sorted(set(doc.get('blueprint_meshes', {})) - bp_meshes):
        say('Blueprint mesh not imported yet, skipped: %s' % m)
    prepare_meshes({a['model'] for a in doc['actors']} | bp_meshes)
    mats = ensure_materials()

    placed, missing, by_model = 0, {}, {}
    cache = {}
    for a in doc['actors']:
        if a['label'] in existing:
            continue
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
        if a['model'] in WALK_THROUGH:
            act.set_actor_enable_collision(False)
        act.set_actor_label(a['label'])
        act.set_editor_property('tags', [unreal.Name(TAG)])
        placed += 1
        by_model[a['model']] = by_model.get(a['model'], 0) + 1

    say('placed %d actors from %d distinct meshes' % (placed, len(by_model)))
    if missing:
        say('MISSING MESHES - import Art/Blender/export/City/ into %s first:' % MESHES)
        for m in sorted(missing):
            say('   %s  (%d placements waiting on it)' % (m, missing[m]))

    if mode == 'add':
        remat(eas, mats)
    if mode in ('hide', 'add'):
        set_greybox(eas, True, set(doc['supersedes_greybox']))
        set_ground(eas, doc, mats, True)
        for m, how in sorted(doc.get('blueprint_meshes', {}).items()):
            say('STILL TO DO BY HAND: %s -> %s.%s (%s)' % (m, how['blueprint'], how['component'], how['set']))
    else:
        say('grey boxes left visible. Run with "hide" to hide the %d they replace: %s'
            % (len(doc['supersedes_greybox']), ', '.join(doc['supersedes_greybox'])))

    say('NOT SAVED. Look at it, then save the level yourself (and lock the .umap actor files first).')
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
    with open(os.path.join(out, 'jc_city_place.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


main()
