"""Save named ASSETS (not level actors - use jc_save_actors.py for those).

    py <repo>/tools/b1y_save.py /Game/Game/FX/NS_CarFire /Game/Game/Materials/M_FlameParticle3D ...
Never calls save_dirty_packages (that has cost this project a lane of work before); it saves only
the paths you name, and reports each one.
"""
import unreal, os, sys, json

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
res = {'asked': sys.argv[1:], 'rows': {}}
for p in sys.argv[1:]:
    try:
        if not unreal.EditorAssetLibrary.does_asset_exist(p):
            res['rows'][p] = 'MISSING'
            continue
        ok = unreal.EditorAssetLibrary.save_asset(p, only_if_is_dirty=False)
        res['rows'][p] = 'saved' if ok else 'SAVE RETURNED FALSE'
    except Exception as e:
        res['rows'][p] = 'ERR ' + str(e)[:120]
with open(os.path.join(OUT, 'b1y_save.json'), 'w') as f:
    json.dump(res, f, indent=1)
print('B1Y_SAVE_DONE ' + json.dumps(res['rows']))
