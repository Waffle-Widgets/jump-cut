"""Does the mesh in UNREAL match the mesh Blender last built?

    py <repo>/tools/unreal_city_mesh_audit.py          report
    py <repo>/tools/unreal_city_mesh_audit.py reimport  re-import every mesh whose triangle count disagrees

Writes JumpCut/Saved/jcpy/city_mesh_audit.txt

WHY. Art/Blender/export/City/city_models.json records the triangle count of every model as Blender built
it. The Unreal asset is a separate thing that only changes when something re-imports the FBX. A de-blocking
pass can therefore be finished, committed and merged in the kit, and the GAME can still be showing the old
boxes, with nothing anywhere saying so. This compares the two and names the difference.
"""
import os, sys, json, traceback
import unreal

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.join(REPO, 'Art', 'Blender', 'export', 'City', 'city_models.json')
SRC = os.path.join(REPO, 'JumpCut', 'Content', 'Game', 'Imported', 'City')
DEST = '/Game/Game/Imported/City'
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'city_mesh_audit.txt')
out = []
def P(*a): out.append(' '.join(str(x) for x in a))


def main():
    want = json.load(open(MODELS, encoding='utf-8'))
    stale, missing, ok = [], [], 0
    P('%-26s %8s %8s   %s' % ('model', 'blender', 'unreal', ''))
    for name in sorted(want):
        a = unreal.load_asset('%s/%s' % (DEST, name))
        if a is None:
            missing.append(name)
            P('%-26s %8d %8s   NO ASSET' % (name, want[name]['tris'], '-'))
            continue
        tris = a.get_num_triangles(0)
        if tris != want[name]['tris']:
            stale.append(name)
            P('%-26s %8d %8d   STALE  (%+d)' % (name, want[name]['tris'], tris, tris - want[name]['tris']))
        else:
            ok += 1
    P('')
    P('IN STEP: %d   STALE: %d   MISSING: %d' % (ok, len(stale), len(missing)))
    if stale:
        P('STALE LIST: %s' % ', '.join(stale))

    if len(sys.argv) > 1 and sys.argv[1] == 'reimport' and (stale or missing):
        at = unreal.AssetToolsHelpers.get_asset_tools()
        tasks = []
        for name in stale + missing:
            fbx = os.path.join(SRC, name + '.fbx')
            if not os.path.exists(fbx):
                P('NO FBX IN CONTENT: %s' % fbx)
                continue
            # LFS read-only trap: clear it first, or the import raises a modal Check Out Assets
            # dialog that freezes the editor's game thread AND the MCP with it.
            ua = os.path.join(SRC, name + '.uasset')
            if os.path.exists(ua) and not os.access(ua, os.W_OK):
                P('READ-ONLY, SKIPPED (clear it outside the editor first): %s' % ua)
                continue
            t = unreal.AssetImportTask()
            t.set_editor_property('filename', fbx)
            t.set_editor_property('destination_path', DEST)
            t.set_editor_property('destination_name', name)
            t.set_editor_property('replace_existing', True)
            t.set_editor_property('automated', True)
            t.set_editor_property('save', False)
            tasks.append(t)
        if tasks:
            at.import_asset_tasks(tasks)
            P('IMPORTED %d tasks' % len(tasks))
            pkgs = []
            for name in stale + missing:
                a = unreal.load_asset('%s/%s' % (DEST, name))
                if a is not None:
                    pk = a.get_outermost()
                    if pk not in pkgs:
                        pkgs.append(pk)
            okv = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
            P('SAVED %d packages ok=%s' % (len(pkgs), okv))
            P('')
            P('--- after ---')
            for name in sorted(stale + missing):
                a = unreal.load_asset('%s/%s' % (DEST, name))
                P('%-26s %8d %8s' % (name, want[name]['tris'],
                                     a.get_num_triangles(0) if a else 'NO ASSET'))


try:
    main()
except Exception:
    P('EXCEPTION'); P(traceback.format_exc())
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
