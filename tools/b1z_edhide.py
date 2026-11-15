"""Hide or show actors in the EDITOR VIEWPORT ONLY, so the wall can be photographed from the
cinematic's own camera without the wreck (which is off screen at that moment in the game) in the way.

    py <repo>/tools/b1z_edhide.py hide <label> [<label> ...]
    py <repo>/tools/b1z_edhide.py show <label> [<label> ...]

set_is_temporarily_hidden_in_editor is a transient editor flag: it is not serialized, so this
cannot dirty a package or reach the game.
"""
import unreal, sys, os

mode = sys.argv[1] if len(sys.argv) > 1 else 'show'
labels = set(sys.argv[2:])
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n = 0
for a in eas.get_all_level_actors():
    if a.get_actor_label() in labels:
        a.set_is_temporarily_hidden_in_editor(mode == 'hide')
        n += 1
print('b1z_edhide %s %d actor(s)' % (mode, n))
with open(os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()),
                       'jcpy', 'b1z_edhide.txt'), 'w') as fh:
    fh.write('%s %d\n' % (mode, n))
