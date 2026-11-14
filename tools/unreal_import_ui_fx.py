"""Brings the screen art and the effect sheets into Unreal (#52 sections 2 and 3).

Auto-import does NOT cover these. This project's `DefaultEngine.ini` turns Interchange's import
dialog off so a dropped `.fbx` or `.wav` imports itself, but a dropped `.png` does nothing at all -
seven UI textures sat in `Content/Game/UI/Textures/` for half a minute and produced zero assets. PNGs
need an explicit import task.

It also sets the two things #52 asks for and that are wrong by default:
  * `lod_group = TEXTUREGROUP_UI` on the screens and icons.
  * `mip_gen_settings = TMGS_NO_MIPMAPS` on everything here. Obvious for UI; just as important for the
    SubUV sheets, because a mipped sprite sheet bleeds neighbouring FRAMES into each other and the
    explosion grows a halo of the frame beside it.
Alpha is preserved explicitly (`compression_no_alpha = False`) - every FX sheet is straight alpha, and
the white ones are meant to be tinted in the material, so a dropped alpha channel would make them
solid white rectangles.

Run in the editor console box with Play mode stopped:
    py <repo>/tools/unreal_import_ui_fx.py            import both sets
    py <repo>/tools/unreal_import_ui_fx.py report     report only, import nothing
Result: Saved/jcpy/import_ui_fx.json. An asset that already exists is configured and saved rather than
re-imported; delete it first if you want it genuinely replaced.

TWO TRAPS, both found the hard way and both silent:
  * **Do not copy the PNG into the destination Content folder first.** Importing a file that is already
    inside `Content/` makes the task return an EMPTY `imported_object_paths` while still creating the
    texture in memory - so it looks like a clean failure and is really an unsaved success. All nine FX
    sheets imported fine from `Art/FX`; all seven UI textures "failed" purely because they had been
    copied to `Content/Game/UI/Textures/` in an earlier attempt at auto-import. Import from `Art/`.
  * **`does_asset_exist` answers False for an imported-but-unsaved asset**, so it is the wrong test for
    "is this already here". Use `load_asset`.
"""
import json
import os
import sys
import traceback

import unreal

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (source file, destination /Game folder, is it UI?)
SETS = [
    ('Art/UI', '/Game/Game/UI/Textures', True,
     ['T_Icon_FreezeFrame', 'T_Icon_Rewind', 'T_Icon_Splice',
      'T_UI_Title', 'T_UI_Win', 'T_UI_Lose', 'T_UI_ToBeContinued']),
    ('Art/FX', '/Game/Game/FX/Textures', False,
     ['T_FX_Explosion_6x6', 'T_FX_HitFlash_4x4', 'T_FX_Telegraph_4x2', 'T_FX_Prompt_4x2',
      'T_FX_WarnRing', 'T_FX_SceneMarker', 'T_FX_FreezeFrame_Overlay',
      'T_FX_SpliceTrail_2x4', 'T_FX_SpeedLines_4x2']),
]
# T_UI_Cover / T_UI_Cover_630x500 are deliberately NOT imported: they are the itch.io page (#26),
# not the game, and an unused 1328x1056 asset in Content is just weight in the package.

REPORT_ONLY = 'report' in sys.argv[1:]
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'import_ui_fx.json')
R = {'report_only': REPORT_ONLY, 'imported': [], 'skipped': [], 'failed': [], 'textures': {}}
eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()


def configure(tex, is_ui):
    tex.modify()
    if is_ui:
        tex.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_UI)
    tex.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property('compression_no_alpha', False)
    tex.set_editor_property('srgb', True)


def describe(path):
    t = unreal.load_asset(path)
    if t is None:
        return None
    return {'size': '%dx%d' % (t.blueprint_get_size_x(), t.blueprint_get_size_y()),
            'group': str(t.get_editor_property('lod_group')).split('.')[-1],
            'mips': str(t.get_editor_property('mip_gen_settings')).split('.')[-1],
            'srgb': t.get_editor_property('srgb'),
            'no_alpha': t.get_editor_property('compression_no_alpha')}


try:
    changed = []
    for src_dir, dest, is_ui, names in SETS:
        for n in names:
            dest_path = dest + '/' + n
            src = os.path.join(REPO, src_dir, n + '.png')
            # `does_asset_exist` is NOT the test to use here: it answers False for an asset that was
            # imported but never saved, which is exactly what the first run of this script left
            # behind for all seven UI textures. `load_asset` finds those too, so this branch picks
            # them up and configures and saves them instead of trying to import over them.
            existing = unreal.load_asset(dest_path)
            if existing is not None:
                on_disk = eal.does_asset_exist(dest_path)
                R['skipped'].append('%s (already loaded, on disk: %s)' % (dest_path, on_disk))
                if not REPORT_ONLY:
                    configure(existing, is_ui)
                    changed.append(existing)
                continue
            if not os.path.isfile(src):
                R['failed'].append(src + ' (source missing)')
                continue
            if REPORT_ONLY:
                R['imported'].append(dest_path + ' (would import)')
                continue
            task = unreal.AssetImportTask()
            task.set_editor_property('filename', src)
            task.set_editor_property('destination_path', dest)
            task.set_editor_property('destination_name', n)
            task.set_editor_property('automated', True)       # never open a dialog: it freezes the MCP
            task.set_editor_property('replace_existing', False)
            task.set_editor_property('save', False)            # we save by path ourselves, below
            tools.import_asset_tasks([task])
            made = list(task.get_editor_property('imported_object_paths') or [])
            if not made and not eal.does_asset_exist(dest_path):
                R['failed'].append(dest_path + ' (import produced no assets)')
                continue
            t = unreal.load_asset(dest_path)
            configure(t, is_ui)
            changed.append(t)
            R['imported'].append(dest_path)

    if changed and not REPORT_ONLY:
        # Save by path. NEVER save_dirty_packages: another lane has read-only Blueprints dirty in this
        # editor and a project-wide save fails on them and leaves .tmp files behind.
        pkgs = list({t.get_outermost().get_name(): t.get_outermost() for t in changed}.values())
        R['saved_packages'] = len(pkgs)
        R['saved'] = bool(unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False))

    for _, dest, _, names in SETS:
        for n in names:
            R['textures'][dest + '/' + n] = describe(dest + '/' + n)
except Exception:
    R['error'] = traceback.format_exc()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w').write(json.dumps(R, indent=1))
unreal.log('IMPORT UI/FX done -> ' + OUT)
