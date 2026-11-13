# One-off editor step from the first build (Nov 12), copied from the ignored JumpCut/Saved/ so the level set-up can be traced.
# Run with `py <path> <step>` in the Unreal editor console (a3_pie.py: during Play mode; the others: Play mode stopped).
# Read it before re-running: steps change placed actors in Lvl_JumpCut and some save the level.
"""G1 / E1 editor steps (NOT during PIE). py <this> <step>. Appends to Saved/e1_editor.txt.
steps:
  show      print markers, player and boss state
  markers   re-label the two markers, set MarkerGrantsFreezeFrame, place the door catch, re-set full transforms
  save      save the current level (map + external actors)
"""
import sys
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
args = sys.argv[1:] or ['show']
log = ['--- ' + ' '.join(args)]
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def by_label(lab):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == lab:
            return a
    return None


def comp(a, name):
    for c in a.get_components_by_class(unreal.SceneComponent):
        if c.get_name() == name:
            return c
    return None


def retransform(a):
    a.modify()
    a.set_actor_transform(unreal.Transform(a.get_actor_location(), a.get_actor_rotation(), a.get_actor_scale3d()), False, True)


def show():
    w = ues.get_editor_world()
    log.append('world %s, PIE %s' % (w.get_name(), ues.get_game_world() is not None))
    mk = unreal.load_class(None, '/Game/Game/Blueprints/BP_SceneMarker.BP_SceneMarker_C')
    for a in eas.get_all_level_actors():
        if a.get_class() == mk:
            ts = comp(a, 'TriggerSphere')
            extra = ''
            try:
                extra = ' grants=%s' % a.get_editor_property('MarkerGrantsFreezeFrame')
            except Exception:
                pass
            log.append('  marker %s id=%s ends=%s at %s r=%.0f pkg=%s%s' % (
                a.get_actor_label(), a.get_editor_property('MarkerId'), a.get_editor_property('MarkerEndsGame'),
                a.get_actor_location(), ts.get_scaled_sphere_radius() if ts else -1, a.get_package().get_name(), extra))
    p = by_label('Player_Main')
    if p:
        for n in ('HasRewind', 'HasFreezeFrame'):
            try:
                log.append('  Player_Main %s=%s' % (n, p.get_editor_property(n)))
            except Exception as e:
                log.append('  Player_Main %s: %s' % (n, e))
        log.append('  Player_Main at %s yaw %.1f' % (p.get_actor_location(), p.get_actor_rotation().yaw))


try:
    step = args[0]
    if step == 'markers':
        a = by_label('Marker_RewindGiven')
        b = by_label('Marker_FreezeFrameGiven')
        if a is not None and b is not None:
            # plaza one first, so the labels never clash
            b.set_actor_label('Marker_BossDefeated')
            b.set_editor_property('MarkerId', unreal.Name('Marker_BossDefeated'))
            retransform(b)
            a.set_actor_label('Marker_FreezeFrameGiven')
            a.set_editor_property('MarkerId', unreal.Name('Marker_FreezeFrameGiven'))
            a.set_editor_property('MarkerGrantsFreezeFrame', True)
            retransform(a)
            log.append('re-labelled')
        else:
            log.append('re-label skipped: RewindGiven=%s FreezeFrameGiven=%s' % (a, b))
        if len(args) > 1 and args[1] == 'door':
            d = by_label('Marker_FreezeFrameDoor')
            cls = unreal.load_class(None, '/Game/Game/Blueprints/BP_SceneMarker.BP_SceneMarker_C')
            loc = unreal.Vector(float(args[2]) if len(args) > 2 else 450.0, 0.0, 0.0)
            if d is None:
                d = eas.spawn_actor_from_class(cls, loc, unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
                d.set_actor_label('Marker_FreezeFrameDoor')
            d.set_editor_property('MarkerId', unreal.Name('Marker_FreezeFrameDoor'))
            d.set_editor_property('MarkerGrantsFreezeFrame', True)
            ts = comp(d, 'TriggerSphere')
            ts.modify()
            ts.set_sphere_radius(float(args[3]) if len(args) > 3 else 300.0, False)
            d.set_actor_transform(unreal.Transform(loc, unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0), unreal.Vector(1, 1, 1)), False, True)
            retransform(d)
            log.append('door catch at %s r=%.0f' % (d.get_actor_location(), ts.get_scaled_sphere_radius()))
    elif step == 'gifts':
        # placed markers kept a blank GiftMesh (added after they were placed): give each the class default's settings
        mk = unreal.load_class(None, '/Game/Game/Blueprints/BP_SceneMarker.BP_SceneMarker_C')
        sphere = unreal.load_asset('/Engine/BasicShapes/Sphere.Sphere')
        mat = unreal.load_asset('/Game/Game/Materials/M_WarnFreeze.M_WarnFreeze')
        for a in eas.get_all_level_actors():
            if a.get_class() != mk:
                continue
            c = comp(a, 'GiftMesh')
            c.modify()
            c.set_static_mesh(sphere)
            c.set_material(0, mat)
            c.set_editor_property('relative_location', unreal.Vector(0, 0, 100))
            c.set_editor_property('relative_scale3d', unreal.Vector(0.6, 0.6, 0.6))
            c.set_collision_profile_name('NoCollision')
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            c.set_editor_property('cast_shadow', False)
            c.set_visibility(False)
            retransform(a)
            log.append('%s gift %s at %s mesh=%s' % (a.get_actor_label(), c.get_name(), c.get_world_location(), c.static_mesh.get_name()))
    elif step == 'gifts2':
        mk = unreal.load_class(None, '/Game/Game/Blueprints/BP_SceneMarker.BP_SceneMarker_C')
        for a in eas.get_all_level_actors():
            if a.get_class() != mk:
                continue
            c = comp(a, 'GiftMesh')
            c.modify()
            c.set_relative_scale3d(unreal.Vector(0.6, 0.6, 0.6))
            c.set_collision_profile_name('NoCollision')
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            c.set_visibility(False, False)
            c.set_editor_property('cast_shadow', False)
            retransform(a)
            c = comp(a, 'GiftMesh')
            log.append('%s gift scale=%s vis=%s shadow=%s coll=%s' % (a.get_actor_label(), c.get_world_scale(), c.is_visible(),
                                                                   c.get_editor_property('cast_shadow'), c.get_collision_enabled()))
    elif step == 'save':
        log.append('save_current_level = %s' % unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
    show()
except Exception:
    import traceback
    log.append('ERROR ' + traceback.format_exc())
with open(ROOT + 'e1_editor.txt', 'a') as f:
    f.write('\n'.join(log) + '\n')
