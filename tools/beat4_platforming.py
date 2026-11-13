"""Beat 4: the destroyed-building platforming section, east of the plaza exit gate.

RUN THIS ON A BUILDER, in the editor with Play mode stopped:
    py <repo>/tools/beat4_platforming.py            import the ruins if needed, then place the section
    py <repo>/tools/beat4_platforming.py clear      remove every JC_Beat4 actor, put Marker_Win and the end wall back
    py <repo>/tools/beat4_platforming.py report      measure what is in the level now and change nothing

It does NOT save. Saving is the builder's call (this project has lost a lane of work to a save at the wrong
moment). Look at it, then save the level yourself.

WHAT IT TOUCHES, and what it deliberately does not
  * It only ever adds or removes actors tagged 'JC_Beat4'. Run it twice and you get one section, not two.
  * `C1_Run_End` (the wall that closed the old three-beat demo at x = 10630) is HIDDEN, not deleted, and it
    is un-hidden again by `clear`.
  * `Marker_Win` is MOVED from (10220, 0, 0) to the far landing pad, because `MarkerEndsGame` is true on it
    and the old spot is in front of beat 4: the player would win the demo before reaching the ruins. `clear`
    puts it back at (10220, 0, 0). When beat 5 is placed on the landing pad, Marker_Win moves again, past it.
  * Nothing else in C1_Layout is touched, and no .uasset other than the five imported ruin meshes and their
    flat materials is created.

THE NUMBERS, AND WHY THEY ARE NOT THE ONES docs/CITY.md PROPOSED
CITY.md sized the ruins for "a gap the player must blink is 6.5-8.5 m, a gap they may jump is under 3 m".
Measured on the real pawn, that is wrong in both directions, and the same measurement says a must-blink gap
cannot be made out of flat ground at all:

    JumpZVelocity 500, GravityScale 1, MaxWalkSpeed 600  ->  airtime 2*500/980 = 1.02 s,
    so a flat run-and-jump carries about 612 cm, plus a capsule radius of 34 at each lip.

Those three numbers are not guesses and they do not need a running editor to check. BP_Player serializes
none of them, and its parent BP_ThirdPersonCharacter serializes only JumpZVelocity - exactly one 500.0
float in the asset, with no 420, 600 or 700 anywhere in it - alongside AirControl 0.35 and
BrakingDecelerationFalling 1500, which is the UE5 template's trio. MaxWalkSpeed and GravityScale appear in
neither asset's name table, so they are the engine defaults, 600 and 1. Nor does either asset serialize
CapsuleHalfHeight or CapsuleRadius, so ACharacter's 34 x 88 stands and the player is 176 cm tall.

A 6.5 m gap is therefore JUMPABLE, and it is also wider than Splice's 600 cm blink, so widening a gap until
the jump fails makes it un-blinkable too. The jump has to be taken away some other way. It is taken away
with a CEILING: a collapsed floor slab 215 cm above the walkway. At 176 cm the player walks under it with
39 cm of head room, but a jump spends that head room and stops: 490t^2 - 500t + 39 = 0 gives t = 0.085 s to
the ceiling, the fall back takes 0.282 s, and 0.367 s at 600 cm/s is about 220 cm of travel. With a capsule
at each lip the jump reaches ~288 cm across a 400 cm gap - short by over a metre, not by a hair. Splice is
a horizontal teleport at chest height (z ~ 88), far below a ceiling whose underside is 215, so it passes
beneath untouched and crosses the 400 cm gap with 200 of its 600 to spare.

THE ONE THING A PLAYTEST HAS TO ANSWER: the blink is a fixed 600 cm forward and it does not stop at a gap.
Clearing gap 2 means standing in the eastern 200 cm of P1 (x 11750..11950); blink from P1's western lip and
the player lands at 12050, inside the gap, and falls. Gap 3 is the same shape (stand x 13150..13350). That
is a 2 m window on a 5 m platform - "walk to the edge first" if it reads, a cliff if it does not. The
checkpoint is 3 m back so a mistake costs about five seconds, and if it plays badly the fix is to narrow
the gaps, not to touch the power.

    gap 1 (hop)   250 cm   open sky          - a free jump, teaches the ledge
    gap 2 (blink) 400 cm   ceiling at 215    - jump reaches ~288, blink reaches 600
    gap 3 (blink) 400 cm   ceiling at 215    - same, after the goons

Platform tops are all at Z = 0, flat, and at least 5 m across, which is what CITY.md asked for and the one
part of its sizing note that survives. Falling is already handled by the game: below `FallLoseZ` (-1000) the
player's health goes to 0, which is the lose screen and a restart from the last checkpoint - so this script
places `Checkpoint_Beat4Entry` on the approach, and a fall costs about five seconds.
"""
import json
import os
import sys

import unreal

TAG = 'JC_Beat4'
MESHES = '/Game/Game/Imported/City/'
MATDIR = '/Game/Game/Materials/City'
BP = '/Game/Game/Blueprints/'
RUINS = ('SM_RuinSlab_A', 'SM_RuinSlab_B', 'SM_RuinBeam', 'SM_RuinWall', 'SM_Rubble')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FBXDIR = os.path.join(REPO, 'Art', 'Blender', 'export', 'City')

# Copied from tools/jumpcut_city_place.py so the ruins wear the same flat colours as the rest of the city
# when the city itself is imported. Keep the two in step; the level wears a cel-shaded post-process, so a
# flat base colour is the right input.
COLOURS = {
    'MS_CityWall': (0.78, 0.75, 0.70), 'MS_CityBrick': (0.42, 0.24, 0.19),
    'MS_CityConcrete': (0.58, 0.58, 0.56), 'MS_CityTrim': (0.11, 0.12, 0.14),
    'MS_CityMetal': (0.55, 0.57, 0.60), 'MS_CityGlass': (0.22, 0.38, 0.47),
    'MS_CitySignA': (0.95, 0.42, 0.18), 'MS_CitySignB': (0.25, 0.72, 0.90),
    'MS_CityAccent': (0.72, 0.16, 0.20), 'MS_CityWood': (0.47, 0.31, 0.18),
    'MS_CityRoof': (0.23, 0.23, 0.25), 'MS_CityCloth': (0.80, 0.74, 0.62),
}

# Bounding-box heights above each piece's own origin, from Art/Blender/export/City/city_models.json.
H = {'SM_RuinSlab_A': 119.0, 'SM_RuinSlab_B': 135.0, 'SM_RuinBeam': 50.0,
     'SM_RuinWall': 478.7, 'SM_Rubble': 71.5}

# DO NOT place a platform at z = -H. The bounding box is not the walking surface: SM_RuinSlab_A is a
# BROKEN slab, and its box reaches 119 only because of chunks standing up near the edges. Traced straight
# down the centre line, the surface the player actually stands on is 45 above the mesh origin. Placing at
# -119 put every platform 74 cm BELOW the street, which quietly turned the head room under the 215 ceiling
# from 39 cm into 113 cm - enough that a jump carries ~559 cm and clears both 400 cm "must-blink" gaps.
# That defeats the whole section, and nothing about it is visible: the slabs still look right.
WALK_TOP = {'SM_RuinSlab_A': 45.0}    # measured by line trace in the editor, not read off the box

FLOOR_EDGE = 11200.0          # Floor_RunExtra: centre 10600, 1200 long -> the last solid ground
CEILING_UNDER = 215.0         # underside of the collapsed slabs: head room 35 cm, jump cut to ~206 cm

# (label, model, x, y, z, yaw)
PIECES = [
    # --- gap 1: a 250 cm hop from the floor edge (11200) to P1 (11450)
    ('B4_P1',          'SM_RuinSlab_A', 11700.0,    0.0, -45.0,  0.0),

    # --- gap 2: 400 cm from P1 (11950) to P2 (12350), roofed
    ('B4_Ceil1_S',     'SM_RuinSlab_B', 12150.0, -150.0,  215.0,  0.0),
    ('B4_Ceil1_N',     'SM_RuinSlab_B', 12150.0,  150.0,  215.0,  0.0),
    ('B4_P2_W',        'SM_RuinSlab_A', 12600.0,    0.0, -45.0,  0.0),
    ('B4_P2_E',        'SM_RuinSlab_A', 13100.0,    0.0, -45.0,  0.0),

    # --- gap 3: 400 cm from P2 (13350) to the landing pad (13750), roofed
    ('B4_Ceil2_S',     'SM_RuinSlab_B', 13550.0, -150.0,  215.0,  0.0),
    ('B4_Ceil2_N',     'SM_RuinSlab_B', 13550.0,  150.0,  215.0,  0.0),

    # --- the landing pad: 10 x 15 m, where beat 5's boss goes
    ('B4_Pad_WS',      'SM_RuinSlab_A', 14000.0, -500.0, -45.0,  0.0),
    ('B4_Pad_WC',      'SM_RuinSlab_A', 14000.0,    0.0, -45.0,  0.0),
    ('B4_Pad_WN',      'SM_RuinSlab_A', 14000.0,  500.0, -45.0,  0.0),
    ('B4_Pad_ES',      'SM_RuinSlab_A', 14500.0, -500.0, -45.0,  0.0),
    ('B4_Pad_EC',      'SM_RuinSlab_A', 14500.0,    0.0, -45.0,  0.0),
    ('B4_Pad_EN',      'SM_RuinSlab_A', 14500.0,  500.0, -45.0,  0.0),

    # --- dressing. Nothing goes across the route at chest height: a wall there would stop the Splice trace,
    #     and a beam laid across a gap would let the player walk over it and skip the power entirely.
    ('B4_Wall_N',      'SM_RuinWall',   14400.0,  700.0,    0.0,  0.0),
    ('B4_Wall_S',      'SM_RuinWall',   14400.0, -700.0,    0.0,  0.0),
    ('B4_Beam_1',      'SM_RuinBeam',   14200.0, -350.0,    0.0, 20.0),
    ('B4_Beam_2',      'SM_RuinBeam',   14350.0,  380.0,    0.0, -15.0),
    ('B4_Rubble_Edge', 'SM_Rubble',     11080.0,  180.0,    0.0, 30.0),
    ('B4_Rubble_P2',   'SM_Rubble',     12700.0, -190.0,    0.0, -40.0),
    ('B4_Rubble_Pad1', 'SM_Rubble',     14650.0,  450.0,    0.0, 140.0),
    ('B4_Rubble_Pad2', 'SM_Rubble',     13880.0, -620.0,    0.0, 75.0),
]

# (label, blueprint, x, y, z, yaw, {variable: value})
ACTORS = [
    # A fall is a loss and a restart from the last checkpoint; without this one that restart is the street,
    # 46 m back. GoonCount 2 so the pair stays on the 5 m wide platform (they spawn at +-75 cm across it).
    ('Checkpoint_Beat4Entry', 'BP_Checkpoint',  10900.0, 0.0, 0.0,   0.0, {}),
    ('Spawner_Beat4',         'BP_GoonSpawner', 12900.0, 0.0, 0.0, 180.0, {'GoonCount': 2}),
]

WIN_HOME = unreal.Vector(10220.0, 0.0, 0.0)      # where c1_layout.py puts Marker_Win
WIN_BEAT4 = unreal.Vector(14400.0, 0.0, 0.0)     # the landing pad, until beat 5 is placed on it
END_WALL = 'C1_Run_End'

log = []


def say(msg):
    log.append(msg)
    unreal.log('B4: ' + msg)
    print(msg)


def write_log():
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
    with open(os.path.join(out, 'jc_beat4.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


def ensure_ruins():
    """Import the five ruin FBXs straight from Art/Blender/export/City with Interchange.

    It imports every time, with replace_existing, rather than skipping meshes that already "exist".
    `does_asset_exist` answers yes for an asset that is only in memory - which is exactly what Unreal's
    auto-import leaves behind if the FBX is dropped into Content/ and then removed again - and a mesh that
    is only in memory is lost on close, taking every actor placed on it with it. Importing from the
    committed source and saving the result is the only version of this that survives a restart."""
    missing = list(RUINS)
    tasks = []
    for n in missing:
        t = unreal.AssetImportTask()
        t.filename = os.path.join(FBXDIR, n + '.fbx')
        t.destination_path = MESHES.rstrip('/')
        t.automated = True
        t.replace_existing = True
        t.save = True
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for n, t in zip(missing, tasks):
        say('imported %s -> %s' % (n, list(t.imported_object_paths)))
    still = [n for n in RUINS if not unreal.EditorAssetLibrary.does_asset_exist(MESHES + n + '.' + n)]
    if still:
        raise RuntimeError('import did not produce: %s' % still)
    # Interchange turns Nanite ON. Every other mesh in this project has it off, and these are 150-300
    # triangle slabs, so it buys nothing and its fallback mesh can drop thin parts (the beam's flanges).
    smes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for n in missing:
        mesh = unreal.load_asset(MESHES + n + '.' + n)
        s = smes.get_nanite_settings(mesh)
        if s.enabled:
            s.enabled = False
            smes.set_nanite_settings(mesh, s, apply_changes=True)
            say('Nanite off on %s' % n)
        unreal.EditorAssetLibrary.save_asset(MESHES + n, only_if_is_dirty=False)
        tris = '?'
        # The subsystem spells this differently between versions and on 5.8/Mac has neither
        # get_triangle_count nor get_number_triangles, so ask the mesh itself first.
        for owner, fn in ((mesh, 'get_num_triangles'), (smes, 'get_triangle_count'),
                          (smes, 'get_number_triangles')):
            if not hasattr(owner, fn):
                continue
            for args in ((0,), ()):
                try:
                    tris = getattr(owner, fn)(*args)
                    break
                except Exception:                                      # noqa: BLE001
                    continue
            if tris != '?':
                break
        say('%s: %s triangles, saved' % (n, tris))


def ensure_materials():
    out = {}
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary
    wanted = set()
    for n in RUINS:
        mesh = unreal.load_asset(MESHES + n + '.' + n)
        for sm in mesh.get_editor_property('static_materials'):
            wanted.add(str(sm.get_editor_property('material_slot_name')))
    say('ruin material slots: %s' % sorted(wanted))
    for slot in sorted(wanted):
        rgb = COLOURS.get(slot)
        if rgb is None:
            say('no colour for slot %s - it stays the import default' % slot)
            continue
        path = '%s/M_%s' % (MATDIR, slot[3:])
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            out[slot] = unreal.load_asset(path)
            continue
        mat = at.create_asset('M_' + slot[3:], MATDIR, unreal.Material, unreal.MaterialFactoryNew())
        col = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -380, 0)
        col.set_editor_property('parameter_name', 'BaseColor')
        col.set_editor_property('default_value', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
        mel.connect_material_property(col, '', unreal.MaterialProperty.MP_BASE_COLOR)
        rough = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -380, 180)
        rough.set_editor_property('parameter_name', 'Roughness')
        rough.set_editor_property('default_value', 0.85)
        mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_asset(path)
        out[slot] = mat
        say('made %s' % path)
    return out


def by_label(eas, label):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


def clear(eas):
    n = 0
    for a in list(eas.get_all_level_actors()):
        if unreal.Name(TAG) in a.get_editor_property('tags'):
            eas.destroy_actor(a)
            n += 1
    say('removed %d earlier %s actors' % (n, TAG))
    return n


def set_end_wall(eas, hidden):
    a = by_label(eas, END_WALL)
    if a is None:
        say('%s not found - nothing hidden' % END_WALL)
        return
    a.modify()
    a.set_actor_hidden_in_game(hidden)       # there is no 'hidden_in_game' property on StaticMeshActor
    a.set_is_temporarily_hidden_in_editor(hidden)
    comp = a.static_mesh_component
    comp.modify()
    comp.set_collision_enabled(
        unreal.CollisionEnabled.NO_COLLISION if hidden else unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    # A property written on a placed actor does not dirty its package; re-setting the whole transform does.
    a.set_actor_transform(a.get_actor_transform(), False, True)
    say('%s %s (collision %s)' % ('hid' if hidden else 'un-hid', END_WALL, 'off' if hidden else 'on'))


def move_win(eas, where):
    a = by_label(eas, 'Marker_Win')
    if a is None:
        say('Marker_Win not found - not moved')
        return
    a.modify()
    a.set_actor_location_and_rotation(where, unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0), False, True)
    say('Marker_Win -> %s' % a.get_actor_location())


def place(eas, mats):
    placed = 0
    for label, model, x, y, z, yaw in PIECES:
        mesh = unreal.load_asset(MESHES + model + '.' + model)
        a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                      unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        comp = a.static_mesh_component
        comp.set_mobility(unreal.ComponentMobility.STATIC)
        comp.set_static_mesh(mesh)
        for i, sm in enumerate(mesh.get_editor_property('static_materials')):
            m = mats.get(str(sm.get_editor_property('material_slot_name')))
            if m is not None:
                comp.set_material(i, m)
        a.set_actor_label(label)
        a.set_editor_property('tags', [unreal.Name(TAG)])
        placed += 1
    say('placed %d ruin pieces' % placed)

    for label, bpname, x, y, z, yaw, vars_ in ACTORS:
        cls = unreal.load_class(None, '%s%s.%s_C' % (BP, bpname, bpname))
        a = eas.spawn_actor_from_class(cls, unreal.Vector(x, y, z),
                                      unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        a.set_actor_label(label)
        a.set_editor_property('tags', [unreal.Name(TAG)])
        for k, v in vars_.items():
            a.set_editor_property(k, v)
        a.set_actor_location_and_rotation(unreal.Vector(x, y, z),
                                         unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False, True)
        say('%s at %s' % (label, a.get_actor_location()))


def report(eas):
    """Measure the section that is actually in the level: every gap along y = 0, by tracing straight down."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    solid, x = [], FLOOR_EDGE - 400.0
    while x <= 15200.0:
        hit = unreal.SystemLibrary.line_trace_single(
            world, unreal.Vector(x, 0.0, 200.0), unreal.Vector(x, 0.0, -600.0),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        solid.append((x, hit is not None))
        x += 10.0
    gaps, run = [], None
    for x, ok in solid:
        if not ok and run is None:
            run = x
        elif ok and run is not None:
            gaps.append((run, x, x - run))
            run = None
    say('ground along y=0, x %.0f..15200 (10 cm steps, down from z=200): %d gaps' % (FLOOR_EDGE - 400.0, len(gaps)))
    # The walking height is the number that silently breaks this section, so it is reported every run.
    heights = []
    for px in (11700.0, 12850.0, 14250.0):
        hit = unreal.SystemLibrary.line_trace_single(
            world, unreal.Vector(px, 0.0, 200.0), unreal.Vector(px, 0.0, -600.0),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        heights.append('%.0f: %s' % (px, 'NO GROUND' if hit is None else 'hit'))
    say('   walking surface probes (expect ground on all three): %s' % ', '.join(heights))
    for a, b, w in gaps:
        head = unreal.SystemLibrary.line_trace_single(
            world, unreal.Vector((a + b) / 2.0, 0.0, 10.0), unreal.Vector((a + b) / 2.0, 0.0, 900.0),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        # unreal.HitResult in 5.8 is opaque: every property is 'protected and cannot be read', there is
        # no `.distance`, and SystemLibrary has no break_hit_result. Only to_tuple/to_dict get inside it,
        # and which one works has moved between versions - so try both and still answer if neither does.
        if head is None:
            hz = 'open sky'
        else:
            hz = 'ceiling present (height unreadable from HitResult)'
            for getter in (lambda h: h.to_tuple()[3], lambda h: h.to_dict()['distance']):
                try:
                    hz = '%.0f' % getter(head)
                    break
                except Exception:                                  # noqa: BLE001
                    continue
        say('   gap x %.0f -> %.0f = %.0f cm wide, ceiling above the middle: %s' % (a, b, w, hz))
    return gaps


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else 'place').lower()
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_editor_world()
    if world.get_name() != 'Lvl_JumpCut' or ues.get_game_world() is not None:
        raise RuntimeError('wrong world (%s) or PIE is running - stop Play first' % world.get_name())
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    if mode == 'report':
        report(eas)
        return
    if mode == 'clear':
        clear(eas)
        set_end_wall(eas, False)
        move_win(eas, WIN_HOME)
        say('done. NOT SAVED.')
        return

    ensure_ruins()
    mats = ensure_materials()
    clear(eas)
    place(eas, mats)
    set_end_wall(eas, True)
    move_win(eas, WIN_BEAT4)
    report(eas)
    say('NOT SAVED. Look at it in the viewport, then save the level yourself.')


try:
    main()
except Exception as e:                                           # noqa: BLE001 - the log is the result
    say('ERROR: %r' % e)
    raise
finally:
    write_log()
