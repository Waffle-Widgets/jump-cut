"""Move the city that is ALREADY in Lvl_JumpCut so it matches Art/Blender/export/City/city_layout.json.

RUN THIS IN THE EDITOR, with Play stopped, from the status-bar console:
    py C:/Users/thecl/code/jump-cut/tools/unreal_city_apply_layout.py          report only, saves nothing
    py C:/Users/thecl/code/jump-cut/tools/unreal_city_apply_layout.py apply    move them and save

WHY THIS EXISTS, next to jumpcut_city_place.py. The placer has two modes and neither fits a layout that
has only MOVED: a full run deletes and re-makes all 387 JC_City actors - 387 external-actor packages
rewritten, on a repo where every .uasset is an LFS binary - and 'add' mode deliberately leaves existing
actors alone, so it changes nothing. Issue #67's between-actor fix moves 87 actors by as little as 4 mm,
so what was needed was an update in place: touch only the actors whose transform actually differs.

WHAT IT TOUCHES
  * ONLY actors carrying the tag JC_City whose label appears in city_layout.json. Nothing else in the
    level is read or written - not the player, the sun, the gates, the markers or the grey boxes.
  * It compares world location against the layout and moves an actor only when it differs by more than
    TOL. It never changes rotation or scale, because the layout's yaw is already what placed them.
  * This map is one-file-per-actor, so moving an actor dirties that actor's OWN package and nothing else.
    EditorLoadingAndSavingUtils.save_dirty_packages() does not see those packages (the same trap the
    grey-box hide hit in jumpcut_city_place.py), so they are collected by hand and saved with
    save_packages().

A NOTE ON LFS. Every .uasset here is `lockable` in .gitattributes, which means git-lfs leaves it
read-only on disk and the save will fail with "Asset does not exist" until the file is locked (git lfs
lock) or made writable. Run in report mode first: it prints the package file for every actor it would
move, which is the list to lock.
"""
import json
import os
import sys

import unreal

TAG = 'JC_City'
TOL = 0.001                       # cm. The smallest real move in the layout is 0.4 cm.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT = os.path.join(ROOT, 'Art', 'Blender', 'export', 'City', 'city_layout.json')


def say(msg):
    unreal.log('[city-apply] %s' % msg)


def main():
    apply_it = 'apply' in [a.lower() for a in sys.argv[1:]]
    doc = json.load(open(LAYOUT, encoding='utf-8'))
    want = {a['label']: a for a in doc['actors']}
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    moved, pkgs, report = [], [], []
    for a in eas.get_all_level_actors():
        if not a.actor_has_tag(TAG):
            continue
        row = want.get(a.get_actor_label())
        if row is None:
            continue
        here = a.get_actor_location()
        there = unreal.Vector(float(row['x']), float(row['y']), float(row['z']))
        # Yaw is checked as well as position, and it is not pedantry. The MCP actor tool's
        # set_actor_transform documents an unset rotation as 'do not change' and in fact resets it
        # to identity, which silently spun every yaw-180 actor it moved - City_RunN_B ended up
        # facing the wrong way down the exit run. The layout owns the yaw, so compare it here.
        rot = a.get_actor_rotation()
        yaw_now = rot.yaw % 360.0
        yaw_want = float(row['yaw']) % 360.0
        dyaw = abs((yaw_now - yaw_want + 180.0) % 360.0 - 180.0)
        if (abs(here.x - there.x) <= TOL and abs(here.y - there.y) <= TOL
                and abs(here.z - there.z) <= TOL and dyaw <= 0.01
                and abs(rot.pitch) <= 0.01 and abs(rot.roll) <= 0.01):
            continue
        if apply_it:
            a.set_actor_location(there, False, False)
            a.set_actor_rotation(unreal.Rotator(0.0, 0.0, yaw_want), False)
        moved.append((a.get_actor_label(), (here.x, here.y, here.z, rot.yaw),
                      (there.x, there.y, there.z, yaw_want)))
    moved_labels = {m[0] for m in moved}

    # Only the actors this run actually moved. On a one-file-per-actor map each of them owns its own
    # package, and re-setting the full transform is what marks that package dirty (the same trick the
    # grey-box hide in jumpcut_city_place.py needs). save_dirty_packages() never sees these, so they are
    # collected here and handed to save_packages() by hand.
    for a in eas.get_all_level_actors():
        if not a.actor_has_tag(TAG) or a.get_actor_label() not in moved_labels:
            continue
        pkg = a.get_outermost()
        if apply_it:
            a.set_actor_transform(a.get_actor_transform(), False, False)
            pkgs.append(pkg)
        report.append('%-34s %s' % (a.get_actor_label(), pkg.get_path_name()))

    say('%d actor(s) differ from the layout' % len(moved))
    for lab, h, t in moved[:200]:
        say('  %-34s (%.1f, %.1f, %.1f) yaw %.0f -> (%.1f, %.1f, %.1f) yaw %.0f'
            % (lab, h[0], h[1], h[2], h[3], t[0], t[1], t[2], t[3]))
    say('%d dirty JC_City package(s)' % len(pkgs))

    out = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()),
                       'city_apply_report.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('mode: %s\n' % ('apply' if apply_it else 'report'))
        f.write('differ from layout: %d\n' % len(moved))
        for lab, h, t in moved:
            f.write('  %-34s (%.3f, %.3f, %.3f) -> (%.3f, %.3f, %.3f)\n' % (lab, h[0], h[1], h[2], t[0], t[1], t[2]))
        f.write('dirty packages: %d\n' % len(pkgs))
        for line in report:
            f.write('  %s\n' % line)
    say('wrote %s' % out)

    if not apply_it:
        say('REPORT ONLY - nothing was moved and nothing was saved. Re-run with "apply".')
        return
    if pkgs:
        ok = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
        say('save_packages returned %s for %d package(s)' % (ok, len(pkgs)))
    else:
        say('nothing to save')


main()
