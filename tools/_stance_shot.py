"""Scratch. Stand two copies of the player side by side holding the same clip frame.

Left  = the clip as it was (retargeted with ALIGN=arms, legs left on the Meshy rest pose)
Right = the clip as it is now (ALIGN=limbs:mesh:0)

Spawns high above the city so the background is empty sky and only the silhouette reads.
Run, screenshot the editor window from outside, then run again with 'clean' to remove the actors.

    py <repo>/tools/_stance_shot.py <before clip> <after clip> [time]
    py <repo>/tools/_stance_shot.py clean
"""
import sys

import unreal

MESH = '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker'
Z = 4200.0
# A Meshy character's mesh faces +Y, not +X (see tools/unreal_retarget_meshy.py). At yaw 0 an
# X-axis camera therefore sees it in PROFILE, which hides exactly the thing being judged here -
# how far apart the feet are. Yaw -90 turns its +Y forward toward +X, into the camera.
YAW = -90.0
LABELS = ['ZZ_StanceBefore', 'ZZ_StanceAfter']

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def clean():
    n = 0
    for a in eas.get_all_level_actors():
        if a.get_actor_label() in LABELS:
            eas.destroy_actor(a)
            n += 1
    return n


done = clean()

if len(sys.argv) > 1 and sys.argv[1] == 'clean':
    unreal.log('STANCE-SHOT removed %d actor(s)' % done)
else:
    before, after = sys.argv[1], sys.argv[2]
    t = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    mesh = unreal.load_asset(MESH)
    out = []
    for label, clip_path, y in [(LABELS[0], before, -120.0), (LABELS[1], after, 120.0)]:
        clip = unreal.load_asset(clip_path)
        if clip is None:
            out.append('%s MISSING %s' % (label, clip_path))
            continue
        # unreal.Rotator in Python is (roll, pitch, yaw) - passing yaw in the first slot sets ROLL
        a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0.0, y, Z),
                                       unreal.Rotator(0.0, 0.0, YAW))
        a.set_actor_label(label)
        c = a.skeletal_mesh_component
        c.set_skeletal_mesh_asset(mesh)
        # single-node mode so the editor viewport evaluates the clip without PIE
        c.set_editor_property('animation_mode', unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_animation(clip)
        c.play(False)
        c.set_position(t, False)
        c.set_play_rate(0.0)
        c.set_update_animation_in_editor(True)
        out.append('%s %s at t=%.2f' % (label, clip_path.split('/')[-1], t))
    # they now face +X, so stand off on +X looking back along -X to see them head on
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(
        unreal.Vector(430.0, 0.0, Z + 85.0), unreal.Rotator(0.0, 180.0, 0.0))
    unreal.log('STANCE-SHOT ' + ' | '.join(out))
