"""Print the on-disk file of every package the beat-1 WALL/FIRE/RAGDOLL work touches, so the right
files can be `git lfs lock`ed before saving. A committed .uasset is read-only under LFS and the
editor's save then fails SILENTLY.

    py <repo>/tools/b1z_pkgs.py
Writes Saved/jcpy/b1z_pkgs.json. Read only.
"""
import unreal, os, json

LABELS = ['B1_Cine_Director', 'B1_Objective_Beacon', 'B1_Cafe_WallPanel_GC',
          'C1_Cafe_CrashDriver', 'B1_Cafe_Fire', 'B1_Cafe_FireLight', 'Coworker_Cafe',
          'B1_Cine_Seq', 'B1_Cafe_CrashCar_GC']
ASSETS = ['/Game/Game/Blueprints/BP_OpeningDirector', '/Game/Game/Blueprints/BP_CrashDriver',
          '/Game/Game/Blueprints/BP_Player', '/Game/Game/Cinematics/LS_Beat1_Opening',
          '/Game/Game/Destruction/GC_CafeWallPanel',
          '/Game/Game/Imported/Beat1/SM_CafeWallPanel']

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
res = {'actors': {}, 'assets': {}}


def filefor(pkg):
    try:
        f = unreal.SystemLibrary.get_system_path(pkg)
        if f:
            return f
    except Exception:
        pass
    try:
        return unreal.Paths.convert_relative_path_to_full(
            unreal.PackageTools.package_name_to_filename(pkg.get_name()) + '.uasset')
    except Exception as e:
        return 'name:%s (%s)' % (pkg.get_name(), type(e).__name__)


eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
for l in LABELS:
    a = by.get(l)
    if a is None:
        res['actors'][l] = None
        continue
    pkg = a.get_outermost()
    res['actors'][l] = {'package': pkg.get_name(), 'file': filefor(pkg)}

for p in ASSETS:
    o = unreal.load_asset(p)
    if o is None:
        res['assets'][p] = None
        continue
    pkg = o.get_outermost()
    res['assets'][p] = {'package': pkg.get_name(), 'file': filefor(pkg)}

with open(os.path.join(OUT, 'b1z_pkgs.json'), 'w') as fh:
    json.dump(res, fh, indent=1)
print('b1z_pkgs wrote %s' % os.path.join(OUT, 'b1z_pkgs.json'))
