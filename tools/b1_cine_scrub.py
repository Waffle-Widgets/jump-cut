"""Scrub LS_Beat1_Opening in the editor and read back what each binding's transform track
actually puts on screen. This is how to check a Sequencer track without PIE: an 11 s cinematic
is over before a second MCP round trip lands, so sampling it live cannot work.

    py <repo>/tools/b1_cine_scrub.py

Writes Saved/jcpy/b1_cine_scrub.txt. Opens the sequence editor and closes it again.
"""
import unreal, os
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
SEQ = '/Game/Game/Cinematics/LS_Beat1_Opening'
FPS = 30
TIMES = [0.0, 2.0, 4.0, 4.6, 4.9, 5.1, 5.4, 5.8, 6.1, 6.45, 8.0, 10.5]
log = []
def say(s): log.append(str(s)); print(str(s))

try:
    L = unreal.LevelSequenceEditorBlueprintLibrary
    seq = unreal.load_asset(SEQ)
    L.open_level_sequence(seq)
    say('opened %s' % SEQ)
    say('bindings: %s' % [b.get_name() for b in seq.get_bindings()])
    say('')
    say('%6s  %-14s %-34s %s' % ('t', 'binding', 'location', 'rotation(r,p,y)'))
    for t in TIMES:
        L.set_current_time(int(round(t * FPS)))
        for b in seq.get_bindings():
            nm = b.get_name()
            if nm.startswith('CineCam'):
                continue
            # GetBoundObjects wants a MovieSceneObjectBindingID, not the binding proxy.
            objs = []
            try:
                objs = list(L.get_bound_objects(seq.get_binding_id(b)) or [])
            except Exception as e:
                say('   (get_bound_objects: %s)' % type(e).__name__)
            if not objs:
                # fall back: while the sequence editor is open the spawnables are real actors
                eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
                objs = [a for a in eas.get_all_level_actors()
                        if nm in a.get_actor_label() or nm in a.get_name()]
            if not objs:
                say('%6.2f  %-14s (nothing bound in the editor)' % (t, nm))
                continue
            for o in objs:
                try:
                    loc = o.get_actor_location(); rot = o.get_actor_rotation()
                    say('%6.2f  %-14s %-34s (r%7.1f p%7.1f y%7.1f)' % (
                        t, nm, '%.0f %.0f %.0f' % (loc.x, loc.y, loc.z), rot.roll, rot.pitch, rot.yaw))
                except Exception as e:
                    say('%6.2f  %-14s <%s>' % (t, nm, e))
    # camera cut: which camera is live
    say('')
    for t in [0.0, 4.5, 7.0, 10.0]:
        L.set_current_time(int(round(t * FPS)))
        cam = L.get_current_camera() if hasattr(L, 'get_current_camera') else None
        say('t=%4.1f  camera=%s' % (t, cam))
    L.close_level_sequence()
    say('')
    say('closed the sequence editor')
except Exception as e:
    import traceback
    say('ERROR %r' % e); say(traceback.format_exc())
with open(os.path.join(OUT, 'b1_cine_scrub.txt'), 'w') as fh:
    fh.write('\n'.join(log))
