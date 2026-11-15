"""After a beat-1 change: count the actors that must be unique, and compare the level's own actor
packages against what is on disk. An editor that dies with placed actors dirty restores their
packages, and World Partition loads EVERY package in __ExternalActors__ - so a stale one gives you
two of everything on the next load (we got 46 beat-4 actors from 23 once).

    py <repo>/tools/b1_beat1_audit.py     writes Saved/jcpy/b1_beat1_audit.txt
"""
import unreal, os
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
log = []
def say(s): log.append(str(s)); print(str(s))

# B1_Cine_WallPatch was the grey cube; it is B1_Cafe_WallPanel_GC, a breakable wall, since 2026-11-15.
WANT_ONE = ['B1_Cine_Director', 'B1_Cine_Seq', 'B1_Cafe_WallPanel_GC', 'B1_Objective_Beacon',
            'B1_Cafe_Fire', 'B1_Cafe_FireLight', 'B1_Cafe_BlastRing',
            'Coworker_Cafe', 'C1_Cafe_CrashDriver', 'City_CafeCrashCar', 'Player_Main']
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = list(eas.get_all_level_actors())
say('total actors: %d' % len(acts))
counts = {}
pkgs = {}
for a in acts:
    lab = a.get_actor_label()
    counts[lab] = counts.get(lab, 0) + 1
    pkgs.setdefault(lab, []).append(a.get_outermost().get_name())
bad = 0
for w in WANT_ONE:
    n = counts.get(w, 0)
    flag = '' if n == 1 else '   <<<< expected exactly 1'
    if n != 1:
        bad += 1
    say('%-22s x%d%s' % (w, n, flag))
    for p in pkgs.get(w, []):
        say('      %s' % p)
say('')
# any label appearing more than once anywhere is worth a look
dups = sorted([(k, v) for k, v in counts.items() if v > 1 and not k.startswith('City_Cafe_')])
say('labels appearing more than once: %d' % len(dups))
for k, v in dups[:25]:
    say('   %-34s x%d' % (k, v))
say('')
say('RESULT: %s' % ('OK' if bad == 0 else '%d actor(s) not unique' % bad))
with open(os.path.join(OUT, 'b1_beat1_audit.txt'), 'w') as fh:
    fh.write('\n'.join(log))
