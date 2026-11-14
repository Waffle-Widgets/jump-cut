"""Re-import named city meshes, and PROVE the re-import kept their materials.

    py <repo>/tools/unreal_city_reimport_by_name.py check  SM_CafeSign SM_CafeShell ...
    py <repo>/tools/unreal_city_reimport_by_name.py apply  SM_CafeSign SM_CafeShell ...
    py <repo>/tools/unreal_city_reimport_by_name.py apply  @/tmp/jc67_changed.txt

Writes JumpCut/Saved/jcpy/city_reimport.txt

WHY THIS EXISTS AND unreal_city_mesh_audit.py IS NOT ENOUGH.
The audit decides what is stale by comparing TRIANGLE COUNTS. The issue-67 z-fight fix (the stand_proud
pass in jumpcut_city_kit.py) lifts coplanar faces 0.4 cm along their normal: it changes no triangle, no
vertex count and no bounding box, and city_models.json comes out byte-identical (md5
ac639be6211f07fbb295358063cce647 before and after). So the audit reports IN STEP: 85, STALE: 0 while every
patched mesh in the level is still the old flush geometry. That is exactly the failure that already
happened once on this ticket, where two de-blocking passes were committed, reviewed and merged, touched
zero .uasset files, and left 14 meshes as the old boxes on screen. A geometry change the audit cannot see
has to be re-imported BY NAME, which is what this does.

IT IMPORTS FROM Art/Blender/export/City, NOT FROM Content. The kit writes there, it is the source of
truth, and it is in git. Only 48 of the 85 models still have an FBX staged under Content, so driving off
Content would silently skip 37 of them. Copying FBXs into Content instead would wake Unreal's
auto-reimport watcher, which can raise a modal "Check Out Assets" dialog that freezes the game thread and
the MCP with it, minutes later, with no command of ours running.

MATERIALS ARE THE RISK, AND SLOT ORDER IS THE REAL INVARIANT. CLAUDE.md says "Re-importing a mesh resets
its materials, so don't re-import once it's set up." For the city that is less dangerous than it sounds and
more dangerous in a different way. What you actually SEE in Lvl_JumpCut does not come from the mesh asset's
slots at all: every City_* actor carries its own per-component material OVERRIDES pointing at
/Game/Game/Materials/City/M_*, while the mesh asset's slots point at the kit's flat
/Game/Game/Imported/City/MS_* placeholders. Verified by reading the actor packages under
Content/__ExternalActors__/Game/Maps/Lvl_JumpCut: City_CafeShell carries six overrides (M_CafeWall,
M_CityBrick, M_CityConcrete, M_CityGlass, M_CityTrim, M_CityWood) against the mesh's six slots,
City_CafeSign two, City_Cafe_03_CafePastryCase four. A mesh re-import does not touch an actor override.

BUT a component's material override array is indexed BY SLOT INDEX, not by slot name. So if a re-import
changes the ORDER or the COUNT of a mesh's material slots, every actor override silently lands on the wrong
slot - the cafe shell's brick and glass would swap, and it would look spectacularly wrong while every
triangle count still matched. That is why the comparison below is an ORDER-SENSITIVE list comparison of
slot names, and why it is the check that must not be relaxed.

So this records each mesh's material slot list (in order), collision and Nanite state BEFORE, re-imports,
reads them back AFTER, and REFUSES TO SAVE any mesh whose slots, collision, Nanite, LODs or triangle count
moved. `check` mode does the before-read and the FBX/lock checks and imports nothing, so you can see what
you are about to do. If the BEFORE probe cannot read what it guards, the mesh is skipped rather than
passed: a guard whose probe failed would otherwise compare equal-to-equal and wave everything through.

LFS: *.uasset is `lockable`, so these files are read-only on disk until locked. Run `git lfs lock` on them
OUTSIDE the editor first; an import onto a read-only asset raises the Check Out Assets modal. This script
reports read-only assets and skips them rather than tripping that dialog.
"""
import os, sys, json, traceback
import unreal

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, 'Art', 'Blender', 'export', 'City')
UA = os.path.join(REPO, 'JumpCut', 'Content', 'Game', 'Imported', 'City')
DEST = '/Game/Game/Imported/City'
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'city_reimport.txt')
out = []
def P(*a): out.append(' '.join(str(x) for x in a))


def state(name):
    """Everything about a mesh that a re-import could silently reset."""
    a = unreal.load_asset('%s/%s' % (DEST, name))
    if a is None:
        return None
    s = {'tris': a.get_num_triangles(0), 'lods': a.get_num_lods(),
         'mats': [], 'collision': None, 'nanite': None, 'verts': a.get_num_vertices(0)}
    try:
        b = a.get_bounding_box()
        s['box'] = [round(b.min.x, 3), round(b.min.y, 3), round(b.min.z, 3),
                    round(b.max.x, 3), round(b.max.y, 3), round(b.max.z, 3)]
    except Exception as e:
        s['probe_failed'] = 'cannot read bounds: %s' % e
        s['box'] = None
    try:
        s['mats'] = [(str(m.material_slot_name), m.material_interface.get_path_name()
                      if m.material_interface else None) for m in a.static_materials]
        if not s['mats']:
            s['probe_failed'] = 'static_materials came back EMPTY'
    except Exception as e:
        s['probe_failed'] = 'cannot read static_materials: %s' % e
        s['mats'] = None
    try:
        bc = a.get_editor_property('body_setup')
        s['collision'] = str(bc.get_editor_property('collision_trace_flag')) if bc else 'NO BODY SETUP'
    except Exception as e:
        s['probe_failed'] = 'cannot read collision: %s' % e
        s['collision'] = None
    try:
        s['nanite'] = bool(a.get_editor_property('nanite_settings').enabled)
    except Exception as e:
        s['probe_failed'] = 'cannot read nanite: %s' % e
        s['nanite'] = None
    return s


def main():
    if len(sys.argv) < 3:
        P('usage: ... check|apply <names...>|@file'); return
    mode = sys.argv[1]
    names = []
    for arg in sys.argv[2:]:
        if arg.startswith('@'):
            names += open(arg[1:], encoding='utf-8').read().split()
        else:
            names.append(arg)
    names = sorted(set(names))
    P('mode=%s  models=%d' % (mode, len(names)))
    P('src=%s' % SRC)
    P('')

    before, ready, skip = {}, [], []
    for n in names:
        fbx = os.path.join(SRC, n + '.fbx')
        ua = os.path.join(UA, n + '.uasset')
        st = state(n)
        before[n] = st
        why = None
        if st is None:
            why = 'NO ASSET IN UNREAL'
        elif not os.path.exists(fbx):
            why = 'NO FBX AT %s' % fbx
        elif os.path.exists(ua) and not os.access(ua, os.W_OK):
            why = 'READ-ONLY (git lfs lock it outside the editor first)'
        if why is None and st is not None and st.get('probe_failed'):
            # A guard that cannot read the thing it guards is not a guard. Fail loud, do not
            # let before==after pass trivially because both probes errored the same way.
            why = 'PROBE FAILED: %s' % st['probe_failed']
        if why:
            skip.append((n, why)); P('SKIP %-26s %s' % (n, why))
        else:
            ready.append(n)
    P('')
    P('READY: %d   SKIPPED: %d' % (len(ready), len(skip)))
    P('')
    P('--- before ---')
    for n in ready:
        b = before[n]
        P('%-26s tris=%-7d verts=%-7d lods=%d coll=%s nanite=%s' %
          (n, b['tris'], b['verts'], b['lods'], b['collision'], b['nanite']))
        for sl, mi in b['mats']:
            P('      slot %-22s -> %s' % (sl, mi))

    if mode != 'apply' or not ready:
        P(''); P('check only - imported nothing'); return

    # What the folder held BEFORE, so an import that makes SM_Foo_1 instead of replacing SM_Foo
    # is caught. replace_existing=True is UNPROVEN on Interchange in this project, and the MCP's own
    # StaticMeshTools.import_file is documented as never overwriting.
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    reg.scan_paths_synchronous([DEST], True)
    before_assets = set(str(x.asset_name) for x in reg.get_assets_by_path(DEST, False))

    # Per-model bounding-box growth measured in Blender, keyed by model name. 22 of the 41 grow by
    # 0.4-2.4 cm; for those, bounds MUST change or the import did not take.
    expect = {}
    ef = os.environ.get('JC67_EXPECT', '/tmp/jc67_expect.json')
    try:
        expect = json.load(open(ef, encoding='utf-8'))
        P('expected-growth table: %s (%d models)' % (ef, len(expect)))
    except Exception as e:
        P('NO EXPECTED-GROWTH TABLE (%s): cannot prove the import took on bounds alone' % e)

    at = unreal.AssetToolsHelpers.get_asset_tools()
    tasks = []
    for n in ready:
        t = unreal.AssetImportTask()
        t.set_editor_property('filename', os.path.join(SRC, n + '.fbx'))
        t.set_editor_property('destination_path', DEST)
        t.set_editor_property('destination_name', n)
        t.set_editor_property('replace_existing', True)
        t.set_editor_property('automated', True)       # no dialog; DefaultEngine.ini also sets bShowImportDialog=False
        t.set_editor_property('save', False)           # we save deliberately, and only what verified clean
        tasks.append(t)
    at.import_asset_tasks(tasks)
    P(''); P('IMPORTED %d tasks' % len(tasks))

    P(''); P('--- after, vs before ---')
    clean, dirty = [], []
    for n in ready:
        b, a = before[n], state(n)
        if a is None:
            dirty.append((n, 'ASSET GONE AFTER IMPORT')); P('%-26s ASSET GONE' % n); continue
        if a.get('probe_failed'):
            dirty.append((n, 'PROBE FAILED AFTER IMPORT: %s' % a['probe_failed']))
            P('%-26s PROBE FAILED AFTER  %s' % (n, a['probe_failed'])); continue
        d = []
        if [m[0] for m in a['mats']] != [m[0] for m in b['mats']]:
            d.append('SLOT NAMES %s -> %s' % ([m[0] for m in b['mats']], [m[0] for m in a['mats']]))
        if [m[1] for m in a['mats']] != [m[1] for m in b['mats']]:
            d.append('MATERIALS %s -> %s' % ([m[1] for m in b['mats']], [m[1] for m in a['mats']]))
        if a['collision'] != b['collision']:
            d.append('COLLISION %s -> %s' % (b['collision'], a['collision']))
        if a['nanite'] != b['nanite']:
            d.append('NANITE %s -> %s' % (b['nanite'], a['nanite']))
        if a['tris'] != b['tris']:
            d.append('TRIS %d -> %d' % (b['tris'], a['tris']))
        if a['lods'] != b['lods']:
            d.append('LODS %d -> %d' % (b['lods'], a['lods']))
        # POSITIVE proof the import actually replaced the asset.
        g = expect.get(n)
        if g is not None and g > 0.001:
            if a['box'] == b['box']:
                d.append('NO-OP: bounds unchanged %s but Blender says this mesh grew %.2f cm - '
                         'the import did not replace the asset' % (b['box'], g))
            else:
                P('%-26s bounds moved %s -> %s (expected ~%.2f cm growth)' % (n, b['box'], a['box'], g))
        if d:
            dirty.append((n, '; '.join(d))); P('%-26s CHANGED  %s' % (n, '; '.join(d)))
        else:
            clean.append(n); P('%-26s ok  (tris=%d verts=%d -> %d, mats+collision+nanite identical)'
                               % (n, a['tris'], b['verts'], a['verts']))

    reg.scan_paths_synchronous([DEST], True)
    after_assets = set(str(x.asset_name) for x in reg.get_assets_by_path(DEST, False))
    new_assets = sorted(after_assets - before_assets)
    if new_assets:
        P('')
        P('*** THE IMPORT CREATED %d NEW ASSET(S) instead of replacing: %s' % (len(new_assets), new_assets))
        dirty.append(('<folder>', 'new assets created: %s' % new_assets))

    P('')
    P('CLEAN: %d   CHANGED-BEYOND-GEOMETRY: %d' % (len(clean), len(dirty)))
    if dirty:
        P('')
        P('*** NOT SAVING ANYTHING: %d mesh(es) came back with something other than geometry changed.' % len(dirty))
        P('*** Nothing has been written to disk. Investigate, then re-run.')
        for n, w in dirty:
            P('    %-26s %s' % (n, w))
        return

    pkgs = []
    for n in clean:
        a = unreal.load_asset('%s/%s' % (DEST, n))
        if a is not None:
            pk = a.get_outermost()
            if pk not in pkgs:
                pkgs.append(pk)
    okv = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
    P('SAVED %d packages ok=%s' % (len(pkgs), okv))
    P('')
    P('SAVED LIST: %s' % ' '.join(clean))


try:
    main()
except Exception:
    P('EXCEPTION'); P(traceback.format_exc())
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote', OUT)
