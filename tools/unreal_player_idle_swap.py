"""Put the player's AUTHORED idle into the blend space his anim blueprint plays, in place of the retargeted one.

Run in the Unreal editor's console box, Play mode stopped, after `git lfs lock` on the blend space:
    py <repo>/tools/unreal_player_idle_swap.py            report only
    py <repo>/tools/unreal_player_idle_swap.py swap       swap the idle samples and save
    py <repo>/tools/unreal_player_idle_swap.py back       put MM_Idle_CWM back and save
Result: <project>/Saved/jcpy/player_idle_swap.txt

BS_Idle_Walk_Run_CWM has 27 samples: 9 walks at speed 300, 9 jogs at 600 and 9 copies of MM_Idle_CWM at speed 0.
Only the 9 at speed 0 change. A_CafeWalker_Idle_Authored comes from Art/Blender/idle_clip.py.

The check that matters before blending two clips made two different ways: they must agree on where the ROOT and
the HIP are. The retargeted clips keep Bone_000 at the origin and let Bone_001 carry the pelvis; a clip that keyed
the pelvis on Bone_000 instead would sink the body by (blend weight x 90 cm) on the way from idle to walk. So this
prints both bones' local transforms for both clips and refuses to swap if the root differs.

get_editor_property('sample_data') hands back COPIES of the sample structs, so the whole array is set back.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'player_idle_swap.txt')
BS = '/Game/Game/Imported/CafeWalker/MeshyAnims/BS_Idle_Walk_Run_CWM'
OLD = '/Game/Game/Imported/CafeWalker/MeshyAnims/MM_Idle_CWM'
NEW = '/Game/Game/Imported/CafeWalker/Authored/A_CafeWalker_Idle_Authored'
eal = unreal.EditorAssetLibrary
E = unreal.AnimPoseExtensions
log = []


def say(s):
    log.append(str(s))
    unreal.log('[idle-swap] %s' % s)


def local(anim, bone, t=0.0):
    o = unreal.AnimPoseEvaluationOptions()
    o.set_editor_property('extract_root_motion', False)
    return E.get_bone_pose(E.get_anim_pose_at_time(anim, t, o), bone, unreal.AnimPoseSpaces.LOCAL)


def world(anim, bone, t=0.0):
    o = unreal.AnimPoseEvaluationOptions()
    o.set_editor_property('extract_root_motion', False)
    return E.get_bone_pose(E.get_anim_pose_at_time(anim, t, o), bone, unreal.AnimPoseSpaces.WORLD)


def fmt(t):
    r = t.rotation.rotator()
    return '(%.2f %.2f %.2f) rot(p%.1f y%.1f r%.1f)' % (t.translation.x, t.translation.y, t.translation.z, r.pitch, r.yaw, r.roll)


def main():
    mode = ([a for a in sys.argv[1:] if a in ('swap', 'back')] or ['report'])[0]
    bs, old, new = eal.load_asset(BS), eal.load_asset(OLD), eal.load_asset(NEW)
    if not (bs and old and new):
        say('REFUSING: missing asset (bs %s, old %s, new %s)' % (bool(bs), bool(old), bool(new)))
        return
    for name, an in (('retargeted', old), ('authored', new)):
        say('%s %s  length %.3f s  root motion %s' % (name, an.get_name(), an.get_play_length(), an.get_editor_property('enable_root_motion')))
        for b in ('Bone_000', 'Bone_001'):
            say('    %s local %s   world %s' % (b, fmt(local(an, b)), fmt(world(an, b))))
    ro, rn = local(old, 'Bone_000'), local(new, 'Bone_000')
    d_pos = (ro.translation - rn.translation).length()
    d_rot = abs(ro.rotation.rotator().pitch - rn.rotation.rotator().pitch) + abs(ro.rotation.rotator().yaw - rn.rotation.rotator().yaw) \
        + abs(ro.rotation.rotator().roll - rn.rotation.rotator().roll)
    say('root difference between the two clips: %.2f cm, %.2f degrees (summed)' % (d_pos, d_rot))
    say('pelvis height: retargeted %.1f, authored %.1f' % (world(old, 'Bone_001').translation.z, world(new, 'Bone_001').translation.z))
    if new.get_editor_property('skeleton') != bs.get_editor_property('skeleton'):
        say('REFUSING: the authored clip is not on the blend space skeleton')
        return

    samples = bs.get_editor_property('sample_data')
    idle = [i for i, s in enumerate(samples) if abs(s.get_editor_property('sample_value').y) < 1e-3]
    say('blend space: %d samples, %d at speed 0, now playing %s' % (
        len(samples), len(idle), sorted({s.get_editor_property('animation').get_name() for i, s in enumerate(samples) if i in idle})))
    if mode == 'report':
        say('report only (pass `swap` or `back`)')
        return
    if mode == 'swap' and (d_pos > 0.5 or d_rot > 1.0):
        say('REFUSING to swap: the root is not where the retargeted clips keep it')
        return
    target = new if mode == 'swap' else old
    fresh = []
    for i, s in enumerate(samples):
        ns = unreal.BlendSample()
        ns.set_editor_property('animation', target if i in idle else s.get_editor_property('animation'))
        ns.set_editor_property('sample_value', s.get_editor_property('sample_value'))
        ns.set_editor_property('rate_scale', s.get_editor_property('rate_scale'))
        fresh.append(ns)
    bs.modify()
    bs.set_editor_property('sample_data', fresh)
    back = bs.get_editor_property('sample_data')
    names = [s.get_editor_property('animation').get_name() if s.get_editor_property('animation') else None for s in back]
    ok = len(back) == len(samples) and all(names[i] == target.get_name() for i in idle) \
        and all(names[i] == samples[i].get_editor_property('animation').get_name() for i in range(len(samples)) if i not in idle)
    say('after: %d samples, speed-0 samples play %s, the other %d unchanged: %s' % (
        len(back), sorted({names[i] for i in idle}), len(samples) - len(idle), ok))
    if not ok:
        say('FAILED: the blend space did not read back as written. NOT saved.')
        return
    pk = [bs.get_outermost(), new.get_outermost()]
    say('saved %s -> %s' % ([p.get_name().split('/')[-1] for p in pk], unreal.EditorLoadingAndSavingUtils.save_packages(pk, False)))


try:
    main()
except Exception as exc:
    import traceback
    say('ERROR ' + traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')
