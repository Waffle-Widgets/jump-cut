"""Bring our own clapperboard drawing into Unreal for the Freeze Frame clack (Sun Nov 15).

    py <repo>/tools/unreal_import_clapper.py

The two pictures are drawn by tools/make_clapperboard.py (blank slate, real alpha, one hinge), so
they are ours and need no credit. Imported from Art/UI, never from inside Content (CLAUDE.md: an
import from inside Content returns nothing and leaves an unsaved texture behind). Saves only the
two packages it made. Writes Saved/jcpy/import_clapper.txt.
"""
import os, traceback
import unreal

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = '/Game/Game/UI/Textures'
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy', 'import_clapper.txt')
L = []
try:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    pk = []
    for n in ('T_UI_Clapper_Open', 'T_UI_Clapper_Shut'):
        tex = unreal.load_asset(DEST + '/' + n)
        if tex is None:
            task = unreal.AssetImportTask()
            task.set_editor_property('filename', os.path.join(REPO, 'Art', 'UI', n + '.png'))
            task.set_editor_property('destination_path', DEST)
            task.set_editor_property('destination_name', n)
            task.set_editor_property('automated', True)
            task.set_editor_property('replace_existing', False)
            task.set_editor_property('save', False)
            tools.import_asset_tasks([task])
            tex = unreal.load_asset(DEST + '/' + n)
        if tex is None:
            L.append('FAILED ' + n)
            continue
        tex.modify()
        tex.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_UI)
        tex.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
        tex.set_editor_property('compression_no_alpha', False)
        tex.set_editor_property('srgb', True)
        pk.append(tex.get_outermost())
        L.append('%s %dx%d' % (n, tex.blueprint_get_size_x(), tex.blueprint_get_size_y()))
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(pk, False)
    L.append('saved %d packages ok=%s' % (len(pk), ok))
except Exception:
    L.append('EXC ' + traceback.format_exc())
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
