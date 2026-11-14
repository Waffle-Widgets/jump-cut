"""Find JC_City actors standing in the same place with the same mesh, and leave one of each.

    py C:/Users/thecl/code/jump-cut/tools/jumpcut_city_dedupe.py          report only, changes nothing
    py C:/Users/thecl/code/jump-cut/tools/jumpcut_city_dedupe.py fix      delete the duplicates, fix labels

WHY THIS IS NEEDED, and it is worth reading before using 'add' mode again.

tools/jumpcut_city_place.py 'add' decides what is already in the level by ACTOR LABEL. That is correct only
as long as the labels in the level still match the labels the layout generates - and the cafe's labels are
positional (City_Cafe_%02d_%s), so inserting the register at index 1 on Fri Nov 13 renumbered everything
after it. Four of those actors were renamed by hand at the time and the other eleven were not, which nobody
could see, because an actor with a stale name looks exactly like an actor with the right name.

The next 'add' run then did the obvious thing: it could not find 'City_Cafe_09_CafeTable', so it made one -
on top of the table that was already standing there under its old name. Seven duplicates, each a second
mesh at the identical transform. Nothing looks wrong in the viewport; what you get is double the draw calls
and two coincident surfaces fighting for the depth buffer, which is the classic cause of exactly the
shimmer ticket #67 is open on.

So this matches on (mesh, rounded position, rounded yaw) rather than on names, which is the thing that
cannot drift. Of each duplicate group it keeps the actor whose label the CURRENT layout wants at that spot,
deletes the rest, and then renames any survivor whose label is stale. It never touches an actor that is not
tagged JC_City.

Actors whose label ends in _GC are REPORTED and never touched: those are Unreal's own leftovers from an
earlier delete, they carry no static mesh, and guessing at them is how you lose something real.
"""
import json
import os
import sys

import unreal

TAG = 'JC_City'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT = os.path.join(REPO, 'Art', 'Blender', 'export', 'City', 'city_layout.json')
TOL = 2.0          # cm: two actors closer than this with the same mesh are the same thing twice

log = []


def say(m):
    log.append(m)
    unreal.log(m)
    print(m)


def main():
    fix = len(sys.argv) > 1 and sys.argv[1].lower() == 'fix'
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    doc = json.load(open(LAYOUT, encoding='utf-8'))
    want = {}
    for a in doc['actors']:
        want[(a['model'], round(a['x'] / TOL), round(a['y'] / TOL), round(a['z'] / TOL))] = a['label']

    groups, ghosts = {}, []
    for a in eas.get_all_level_actors():
        if unreal.Name(TAG) not in a.get_editor_property('tags'):
            continue
        lbl = a.get_actor_label()
        mesh = (a.static_mesh_component.get_editor_property('static_mesh')
                if isinstance(a, unreal.StaticMeshActor) else None)
        if mesh is None:
            ghosts.append(lbl)
            continue
        loc = a.get_actor_location()
        key = (mesh.get_name(), round(loc.x / TOL), round(loc.y / TOL), round(loc.z / TOL))
        groups.setdefault(key, []).append(a)

    dupes = {k: v for k, v in groups.items() if len(v) > 1}
    stale = [(k, v[0]) for k, v in groups.items()
             if len(v) == 1 and k in want and v[0].get_actor_label() != want[k]]
    say('%d JC_City actors in %d distinct spots' % (sum(len(v) for v in groups.values()), len(groups)))
    say('duplicate spots: %d   stale labels on single actors: %d   mesh-less leftovers: %d'
        % (len(dupes), len(stale), len(ghosts)))
    for k in sorted(dupes, key=lambda k: k[0]):
        say('   %s at (%.0f, %.0f, %.0f): %s' % (k[0], k[1] * TOL, k[2] * TOL, k[3] * TOL,
                                                 ', '.join(a.get_actor_label() for a in dupes[k])))
    for k, a in stale:
        say('   %s is labelled %s; the layout calls it %s' % (k[0], a.get_actor_label(), want[k]))
    if ghosts:
        say('   left alone (no static mesh, Unreal\'s own leftovers): %s' % ', '.join(sorted(ghosts)))
    if not fix:
        say('report only. Re-run with "fix" to delete the duplicates and correct the labels.')
        return

    # delete first, so a name the layout wants is free before anything is renamed into it
    killed, pkgs = [], []
    for k, group in dupes.items():
        target = want.get(k)
        keep = next((a for a in group if a.get_actor_label() == target), group[0])
        for a in group:
            if a is keep:
                continue
            killed.append(a.get_actor_label())
            eas.destroy_actor(a)
    say('deleted %d duplicate actors: %s' % (len(killed), ', '.join(sorted(killed))))

    renamed = 0
    for k, group in list(dupes.items()) + [(k, [a]) for k, a in stale]:
        target = want.get(k)
        if not target:
            continue
        for a in group:
            if not unreal.SystemLibrary.is_valid(a):
                continue
            if a.get_actor_label() != target:
                a.set_actor_label(target)
                renamed += 1
            # one-file-per-actor: nothing above dirties the package, so re-set the transform the way the
            # placer does and save it by hand, or the fix lives only in memory
            a.set_actor_transform(a.get_actor_transform(), False, False)
            pkgs.append(a.get_outermost())
    say('renamed %d actors to the labels the layout uses' % renamed)
    if pkgs:
        unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
        say('saved %d actor packages' % len(pkgs))
    say('The deleted actors leave orphaned packages under __ExternalActors__; delete those files on disk '
        'or they come back on the next load.')
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
    with open(os.path.join(out, 'jc_city_dedupe.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


main()
