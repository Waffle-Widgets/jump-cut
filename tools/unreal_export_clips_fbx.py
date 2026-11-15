"""Export a character's clips from Unreal as FBX WITH their preview mesh, so they can be looked at in Blender.

Run in the Unreal editor's console box, Play mode stopped. It only reads assets and writes under Saved/:
    py <repo>/tools/unreal_export_clips_fbx.py <anim folder> <out subfolder> [name filter ...]
    py .../unreal_export_clips_fbx.py /Game/Game/Imported/CafeWalker/MeshyAnims player Jog_Fwd Walk_Fwd Attack HitReact Jump Fall Land
Result: <project>/Saved/clipfbx/<out subfolder>/<clip>.fbx and Saved/clipfbx/<out subfolder>/_export.txt

WHY. Every check of a retargeted clip so far read numbers back (chains mapped, saved ok, a bone's height) or took
one capture from the game camera. Nothing looked at a whole clip from every side on the body that wears it, which
is how arms on the wrong sides, clawed hands and a metre of float each shipped. Unreal can write an AnimSequence
out as FBX with the skeletal mesh skinned to it; Art/Blender/clip_sheet.py then renders front, back and both sides
across the clip, and close-ups of the hands, and counts torn skin.

The mesh that goes out is the clip's preview mesh, else the skeleton's. Pass `mesh=<asset path>` to force one.
"""
import os
import sys
import unreal

args = sys.argv[1:]
folder, sub = args[0], args[1]
mesh_path = next((a[5:] for a in args[2:] if a.startswith('mesh=')), None)
filters = [a for a in args[2:] if not a.startswith('mesh=')]
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'clipfbx', sub)
os.makedirs(OUT, exist_ok=True)
eal = unreal.EditorAssetLibrary
log = []
try:
    mesh = eal.load_asset(mesh_path) if mesh_path else None
    done = 0
    for p in sorted(eal.list_assets(folder, recursive=False)):
        a = eal.load_asset(p)
        if not isinstance(a, unreal.AnimSequence):
            continue
        name = a.get_name()
        if filters and not any(f.lower() in name.lower() for f in filters):
            continue
        if mesh is not None:
            try:
                a.set_preview_skeletal_mesh(mesh)          # in memory only; nothing is saved
            except Exception as exc:
                log.append('note: could not set preview mesh on %s (%s)' % (name, exc))
        opt = unreal.FbxExportOption()
        opt.set_editor_property('export_preview_mesh', True)
        opt.set_editor_property('ascii', False)
        opt.set_editor_property('level_of_detail', False)
        opt.set_editor_property('collision', False)
        opt.set_editor_property('vertex_color', False)
        task = unreal.AssetExportTask()
        task.set_editor_property('object', a)
        task.set_editor_property('filename', os.path.join(OUT, name + '.fbx'))
        task.set_editor_property('exporter', unreal.AnimSequenceExporterFBX())
        task.set_editor_property('options', opt)
        task.set_editor_property('automated', True)
        task.set_editor_property('prompt', False)
        task.set_editor_property('replace_identical', True)
        ok = unreal.Exporter.run_asset_export_task(task)
        log.append('%s  %.3f s  root motion %s  exported %s' % (name, a.get_play_length(), a.get_editor_property('enable_root_motion'), ok))
        done += ok
    log.append('exported %d clips to %s' % (done, OUT))
except Exception:
    import traceback
    log.append('ERROR ' + traceback.format_exc())
with open(os.path.join(OUT, '_export.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(log) + '\n')
