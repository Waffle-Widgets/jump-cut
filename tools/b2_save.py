"""Save exactly the assets the Sun Nov 15 polish touched, by path (never save_dirty_packages).

    py <repo>/tools/b2_save.py

`git lfs lock` the four committed ones first: a committed .uasset is read-only and the save fails
silently. Writes Saved/jcpy/b2_save.txt; confirm with `git status`.
"""
import os, traceback
import unreal

PATHS = ['/Game/Game/Blueprints/BP_OpeningDirector', '/Game/Game/Blueprints/BP_Coworker',
         '/Game/Game/Blueprints/BP_BossFreeze', '/Game/Game/UI/WBP_CineOverlay',
         '/Game/Game/Audio/SFX_Clapper',
         '/Game/Game/UI/Textures/T_UI_Clapper_Open', '/Game/Game/UI/Textures/T_UI_Clapper_Shut']
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy', 'b2_save.txt')
L = []
try:
    pk = []
    for p in PATHS:
        a = unreal.load_asset(p)
        if a is None:
            L.append('MISSING ' + p)
            continue
        if isinstance(a, unreal.Blueprint):
            unreal.BlueprintEditorLibrary.compile_blueprint(a)
        pk.append(a.get_outermost())
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(pk, False)
    L.append('saved %d packages ok=%s' % (len(pk), ok))
except Exception:
    L.append('EXC ' + traceback.format_exc())
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
