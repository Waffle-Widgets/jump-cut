"""Print the on-disk file of every package the beat-1 explosion work touches, so the right files
can be `git lfs lock`ed before saving. A committed .uasset is read-only under LFS and the editor's
save then fails SILENTLY."""
import unreal, os, json
LABELS = ['B1_Cafe_CrashCar_GC', 'B1_Cafe_Explosion', 'B1_Cine_ExplCam', 'B1_Cafe_DebrisFloor',
          'City_CafeCrashCar', 'B1_Cine_Director', 'B1_Objective_Beacon', 'Coworker_Cafe',
          'C1_Cafe_CrashDriver', 'B1_Cine_WallPatch', 'B1_Cine_Seq']
ASSETS = ['/Game/Game/Blueprints/BP_OpeningDirector', '/Game/Game/Blueprints/BP_Coworker',
          '/Game/Game/Destruction/GC_CrashCar', '/Game/Game/Materials/M_FXExplosion',
          '/Game/Game/Maps/Lvl_JumpCut']
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
res = {'actors': {}, 'assets': {}}
by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
for l in LABELS:
    a = by.get(l)
    if a is None:
        res['actors'][l] = None
        continue
    pkg = a.get_outermost()
    res['actors'][l] = {'pkg': pkg.get_name(),
                        'file': unreal.PackageTools.package_name_to_filename(pkg.get_name(), '.uasset')}
for p in ASSETS:
    o = unreal.load_asset(p)
    pkg = o.get_outermost() if o else None
    res['assets'][p] = None if pkg is None else {
        'file': unreal.PackageTools.package_name_to_filename(pkg.get_name(), '.uasset')}
with open(os.path.join(OUT, 'b1x_pkgs.json'), 'w') as fh:
    json.dump(res, fh, indent=1)
print('PKGS OK')
