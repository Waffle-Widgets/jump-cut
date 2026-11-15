"""The two __ExternalActors__ packages whose actors were destroyed by b1_opening_wire.py are
still DIRTY IN MEMORY after the files were git rm-ed. Saving them is how you make the deletion
real on both sides; leaving them dirty means any later Save All writes the orphans back, and
World Partition would then load a SECOND BP_OpeningDirector and run beat 1 twice.

    py <repo>/tools/b1v_orphanflush.py
Checks the package really has no actor in the level first, then saves it (which deletes the file
for a one-file-per-actor package whose actor is gone). Reads back what is on disk afterwards.
"""
import unreal, os, json

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
TARGETS = ['/Game/__ExternalActors__/Game/Maps/Lvl_JumpCut/0/ZF/GVL9MXRUS5VCAI3BB1Q8O9',
           '/Game/__ExternalActors__/Game/Maps/Lvl_JumpCut/7/WF/3600UB17MS45O60CI8BE97']
L = []
def say(s):
    L.append(str(s)); print(str(s))

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
live = set(a.get_outermost().get_name() for a in eas.get_all_level_actors())
pkgs = []
for t in TARGETS:
    if t in live:
        say('%s STILL HAS A LIVE ACTOR - refusing' % t)
        continue
    p = unreal.find_object(None, t)
    if p is None:
        say('%s not loaded (nothing to flush)' % t)
        continue
    pkgs.append(p)
    say('%s dirty, no live actor -> flushing' % t)
if pkgs:
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
    say('save_packages -> %s (%d)' % (ok, len(pkgs)))
proj = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
for t in TARGETS:
    f = os.path.join(proj, 'Content' + t[len('/Game'):] + '.uasset')
    say('on disk after: %s  %s' % (os.path.isfile(f), f))
with open(os.path.join(OUT, 'b1v_orphanflush.txt'), 'w') as fh:
    fh.write('\n'.join(L))
print('B1V_ORPHANFLUSH done')
