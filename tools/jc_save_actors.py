"""Saves ONLY the named level actors' own packages, by actor label.

Why this exists. This map is One File Per Actor, so every actor owns a package under
`Content/__ExternalActors__/Game/Maps/Lvl_JumpCut/<a>/<bb>/<hash>`. Two routes that look like
they should save one do not:

  * `SceneTools.save_actor` (MCP) resolves the actor's package and then saves it as a *registry
    asset*. An external actor package is not a registry asset, so it fails with
    "Asset does not exist: /Game/__ExternalActors__/..." for every actor. It reports the path,
    which is handy, and saves nothing.
  * `AssetTools.save_assets` on that same package path fails the same way.

And the route that must never be used is `save_dirty_packages`: it saves EVERY dirty package in
the project, which in this repo has already cost a lane of work and left `.tmp` files in `Saved/`.

So: collect the packages of exactly the actors you name, and save those.

    py <repo>/tools/jc_save_actors.py Coworker_Cafe City_Cafe_00_CafeCounter ...

Two things it does deliberately:
  * It re-sets each actor's FULL transform before saving. Some edits (notably visibility) do not
    dirty the actor's package, so the change lives in memory and is lost on reload. Re-setting the
    whole transform is the cheapest way to guarantee the package is dirty. Passing the full
    transform matters: `set_actor_transform` resets any component you leave out.
  * It writes `Saved/jcpy/jc_save_actors.json`. A committed `.uasset` is read-only under git LFS
    and the save then fails SILENTLY, so never trust the return value - read the file, and check
    `git status` afterwards. `git lfs lock` the files first.
"""
import json
import os
import sys

import unreal


def main():
    labels = [a for a in sys.argv[1:] if a.strip()]
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    result = {'asked': labels, 'matched': {}, 'missing': [], 'saved': None}
    wanted = set(labels)
    pkgs, seen = [], {}
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if lab not in wanted:
            continue
        # dirty the package: re-set the whole transform, not a part of it
        xf = a.get_actor_transform()
        a.set_actor_transform(xf, False, False)
        pkg = a.get_outermost()
        name = pkg.get_name()
        if name not in seen:
            seen[name] = True
            pkgs.append(pkg)
        result['matched'].setdefault(lab, []).append(name)
    result['missing'] = sorted(wanted - set(result['matched']))
    if pkgs:
        result['saved'] = bool(unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False))
    result['package_count'] = len(pkgs)
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
    d = os.path.join(out, 'jcpy')
    if not os.path.isdir(d):
        os.makedirs(d)
    with open(os.path.join(d, 'jc_save_actors.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=1)
    unreal.log('jc_save_actors: %s' % json.dumps(result))


main()
