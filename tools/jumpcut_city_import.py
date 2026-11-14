"""Import every city FBX that is on disk in Content/Game/Imported/City/ but has no mesh asset yet.

    py C:/Users/thecl/code/jump-cut/tools/jumpcut_city_import.py          import what is missing
    py C:/Users/thecl/code/jump-cut/tools/jumpcut_city_import.py force    re-import every FBX that is there

WHY THIS EXISTS, and what it turned out NOT to be for. The route the rest of this pipeline documents -
"copy the FBX into Content/Game/Imported/City/ with Unreal open and let Interchange auto-import it" - does
work, including for brand-new files; 21 FBXs copied in on Fri Nov 13 all imported on their own. This was
written because it LOOKED as though they had not: the one file that already had an asset, SM_CafeShell, was
read-only (committed .uasset, lockable under this repo's LFS rule), and re-importing over it raised a modal
"Check Out Assets" dialog that froze the editor's game thread - and every MCP call with it - until it was
dismissed. From outside, "the editor stopped answering and the asset count on disk has not moved" reads
exactly like "the import never happened". It had; the new assets were in memory, unsaved, which is why the
folder still showed the old file count.

So keep it for the two things it actually gives you: an import you can run and check from a script rather
than wait on a watcher, and the read-only clear that stops that dialog appearing in the first place. Run it
after copying FBXs in if you want the import to be deterministic; it is a no-op when the watcher got there
first, and it says so.

It does NOT save the level and it does NOT place anything - tools/jumpcut_city_place.py does that.
"""
import os
import sys

import unreal

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, 'JumpCut', 'Content', 'Game', 'Imported', 'City')
DEST = '/Game/Game/Imported/City'

log = []


def say(m):
    log.append(m)
    unreal.log(m)
    print(m)


def main():
    force = len(sys.argv) > 1 and sys.argv[1].lower() == 'force'
    if not os.path.isdir(SRC):
        raise RuntimeError('no such folder: %s' % SRC)
    fbx = sorted(f for f in os.listdir(SRC) if f.lower().endswith('.fbx'))
    if not fbx:
        say('no FBX files in %s - nothing to import' % SRC)
        return

    todo = []
    for f in fbx:
        name = os.path.splitext(f)[0]
        exists = unreal.EditorAssetLibrary.does_asset_exist('%s/%s' % (DEST, name))
        if exists and not force:
            continue
        todo.append((name, os.path.join(SRC, f), exists))
    say('%d FBX on disk, %d to import (%s)' % (len(fbx), len(todo), 'force' if force else 'missing only'))
    if not todo:
        return

    # Committed .uasset files are read-only in this repo (git LFS lockable). Re-importing over one raises a
    # modal "Check Out Assets" dialog that blocks the whole editor until somebody clicks it. Clear the
    # attribute on just the assets this run will overwrite.
    cleared = 0
    for name, _, exists in todo:
        if not exists:
            continue
        p = os.path.join(SRC, name + '.uasset')
        if os.path.exists(p) and not os.access(p, os.W_OK):
            os.chmod(p, 0o666)
            cleared += 1
    if cleared:
        say('cleared the read-only attribute on %d .uasset files this run will overwrite' % cleared)

    tasks = []
    for name, path, _ in todo:
        t = unreal.AssetImportTask()
        t.set_editor_property('filename', path)
        t.set_editor_property('destination_path', DEST)
        t.set_editor_property('destination_name', name)
        t.set_editor_property('replace_existing', True)
        t.set_editor_property('automated', True)        # no dialogs: this runs unattended
        t.set_editor_property('save', False)            # saving is the builder's call, as everywhere else
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

    ok, bad = [], []
    for name, _, _ in todo:
        (ok if unreal.EditorAssetLibrary.does_asset_exist('%s/%s' % (DEST, name)) else bad).append(name)
    say('imported %d of %d' % (len(ok), len(todo)))
    if bad:
        say('FAILED: ' + ', '.join(sorted(bad)))
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
    with open(os.path.join(out, 'jc_city_import.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


main()
