"""Find external-actor packages on disk that no actor in the loaded level claims.

b1_opening_wire.py destroys and re-spawns B1_Cine_Director and B1_Objective_Beacon every run, and
a re-spawned actor gets a NEW package hash. The old package file is not removed by a targeted
save, so it stays on disk - and World Partition loads everything in that folder, which would put a
second director in the level and run beat 1 twice.
"""
import unreal, os, json
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
root = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir())
ext = os.path.join(root, '__ExternalActors__', 'Game', 'Maps', 'Lvl_JumpCut')
claimed = {}
for a in eas.get_all_level_actors():
    p = a.get_outermost().get_name()
    if '__ExternalActors__' in p:
        claimed[p.rsplit('/', 1)[-1]] = a.get_actor_label()
ondisk = {}
for dp, dn, fn in os.walk(ext):
    for f in fn:
        if f.endswith('.uasset'):
            ondisk[f[:-7]] = os.path.join(dp, f)
orph = {k: v.replace(root, 'Content/') for k, v in ondisk.items() if k not in claimed}
res = {'actors_claiming_a_package': len(claimed), 'packages_on_disk': len(ondisk),
       'orphans': orph}
with open(os.path.join(OUT, 'b1x_orphans.json'), 'w') as fh:
    json.dump(res, fh, indent=1)
print('ORPHANS %d of %d' % (len(orph), len(ondisk)))
