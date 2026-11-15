"""Give the placed coworker (Coworker_Cafe) her idle clip, without touching BP_Coworker.

    py <repo>/tools/unreal_coworker_idle.py [measure|apply]        (editor console box, Play mode stopped)
Result: <project>/Saved/jcpy/coworker_idle.txt

WHY (Sun Nov 15). She has no anim blueprint: the placed actor's body component plays one clip in Single Node
mode, and that clip (SK_CafeCoworkerArmature_Idle) holds the pose she was sculpted in, arms held out. This points
the PLACED actor at the authored idle instead (import it first with unreal_import_authored_clip.py). BP_Coworker
itself is not touched - it was locked by another teammate, and the clip was never set there anyway.
The opening script (b1_opening_wire.py) looks Coworker_Cafe up by label and does not re-place her, so this stays.
`measure` changes nothing and prints the actor's package, which must be `git lfs lock`ed and writable before `apply`.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'coworker_idle.txt')
CLIP = '/Game/Game/Imported/CafeCoworker/Authored/A_CafeCoworker_Idle_Authored'      # Art/Blender/coworker_idle.py
LABEL = 'Coworker_Cafe'
log = []


def say(s):
    log.append(str(s))
    unreal.log('[coworker-idle] %s' % s)


def state(c, tag):
    d = c.get_editor_property('animation_data')
    a = d.get_editor_property('anim_to_play')
    say('%s mode %s  clip %s  looping %s playing %s  anim_class %s' % (
        tag, c.get_editor_property('animation_mode'), a.get_path_name() if a else None,
        d.get_editor_property('saved_looping'), d.get_editor_property('saved_playing'), c.get_editor_property('anim_class')))


def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else 'measure'
    clip = unreal.EditorAssetLibrary.load_asset(CLIP)
    if clip is None:
        say('REFUSING: no clip %s' % CLIP); return
    for k in ('enable_root_motion', 'force_root_lock', 'root_motion_root_lock'):
        try: say('clip %s = %s' % (k, clip.get_editor_property(k)))
        except Exception as e: say('clip %s unreadable: %s' % (k, e))
    say('clip length %.2f s, skeleton %s' % (clip.get_play_length(), clip.get_skeleton().get_path_name()))
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    hits = [a for a in sub.get_all_level_actors() if a.get_actor_label() == LABEL]
    if len(hits) != 1:
        say('REFUSING: %d actors labelled %s' % (len(hits), LABEL)); return
    a = hits[0]
    say('actor %s  package %s' % (a.get_path_name(), a.get_outermost().get_name()))
    comps = a.get_components_by_class(unreal.SkeletalMeshComponent)
    say('skeletal components: %s' % [c.get_name() for c in comps])
    if len(comps) != 1:
        say('REFUSING: expected one skeletal mesh component'); return
    c = comps[0]
    mesh = c.get_editor_property('skeletal_mesh_asset')
    say('mesh %s  skeleton %s' % (mesh.get_path_name(), mesh.get_editor_property('skeleton').get_path_name()))
    state(c, 'BEFORE')
    if mode != 'apply':
        return
    if mesh.get_editor_property('skeleton') is not clip.get_skeleton():
        say('REFUSING: the clip is for a different skeleton'); return
    c.set_editor_property('animation_mode', unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    d = unreal.SingleAnimationPlayData()
    d.set_editor_property('anim_to_play', clip)
    d.set_editor_property('saved_looping', True)
    d.set_editor_property('saved_playing', True)
    d.set_editor_property('saved_play_rate', 1.0)
    c.set_editor_property('animation_data', d)
    a.set_actor_transform(a.get_actor_transform(), False, False)          # dirties the actor's own package
    a.modify()
    state(c, 'AFTER ')
    ok = unreal.EditorLoadingAndSavingUtils.save_packages([a.get_outermost(), clip.get_outermost()], False)
    say('SAVED %s and %s ok=%s' % (a.get_outermost().get_name(), clip.get_outermost().get_name(), ok))


try:
    main()
except Exception:
    import traceback
    say(traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
