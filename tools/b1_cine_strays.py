"""Find (and with `clean`, remove) actors left in Lvl_JumpCut by a cinematic build script that
errored before its own cleanup line.

    py <repo>/tools/b1_cine_strays.py          list them
    py <repo>/tools/b1_cine_strays.py clean    destroy them

b1_opening_cine.py spawns a throwaway actor, copies it into the sequence as a spawnable, then
destroys it. If it raises in between - the first run did, on set_relative_transform - the
throwaway stays in the level as a real actor, untagged, and nothing else removes it. The first
b1_opening_actors.py run left an untagged LevelSequenceActor the same way.
"""
import unreal, os, sys
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
CLEAN = 'clean' in sys.argv
KEEP = {'B1_Cine_WallPatch', 'B1_Cine_Seq', 'B1_Cine_Director', 'B1_Objective_Beacon'}
NAMES = ('CineCar', 'CineDriver', 'CineCam', '_ApiProbe')
log = []
def say(s): log.append(str(s)); print(str(s))

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
found = []
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in KEEP:
        continue
    cn = a.get_class().get_name()
    hit = any(n in lab or n in a.get_name() for n in NAMES)
    if cn == 'LevelSequenceActor':
        hit = True
    if hit:
        found.append(a)
        say('%-28s %-22s %s  tags=%s' % (lab, cn, a.get_actor_location(),
                                         [str(t) for t in a.get_editor_property('tags')]))
say('%d stray actor(s)' % len(found))
if CLEAN:
    for a in found:
        lab = a.get_actor_label()
        eas.destroy_actor(a)
        say('destroyed %s' % lab)
else:
    say('(listing only - pass `clean` to remove)')
with open(os.path.join(OUT, 'b1_cine_strays.txt'), 'w') as fh:
    fh.write('\n'.join(log))
