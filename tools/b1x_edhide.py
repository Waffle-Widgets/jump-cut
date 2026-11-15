"""Temporarily hide (or show) actors in the EDITOR viewport only, so a capture shows what the
game shows. set_is_temporarily_hidden_in_editor is transient: it dirties nothing and does not
persist. Usage:  py b1x_edhide.py hide Label1 Label2 ... | show Label1 ... | gamehide"""
import unreal, sys
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mode = sys.argv[1] if len(sys.argv) > 1 else 'gamehide'
labels = set(sys.argv[2:])
n = 0
for a in eas.get_all_level_actors():
    l = a.get_actor_label()
    if mode == 'gamehide':
        # mirror runtime visibility: anything hidden in game is hidden in the viewport too
        want = bool(a.get_editor_property('hidden'))
        a.set_is_temporarily_hidden_in_editor(want)
        n += 1 if want else 0
    elif l in labels:
        a.set_is_temporarily_hidden_in_editor(mode == 'hide')
        n += 1
print('EDHIDE %s n=%d' % (mode, n))
