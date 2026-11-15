"""Which package does each actor this round touched own? Prints repo-relative paths so they can
be git lfs locked before saving. Reads only.

    py <repo>/tools/b1v_pkgs.py
"""
import unreal, os, json

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
WANT = ('B1_Cine_Director', 'B1_Objective_Beacon', 'B1_Cine_HandCam', 'Coworker_Cafe',
        'C1_Cafe_Car', 'C1_Cafe_CarCab', 'C1_Cafe_CrashDriver')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
rows = []
for lab in WANT:
    a = by.get(lab)
    if a is None:
        rows.append({'label': lab, 'package': None, 'file': None, 'exists': False})
        continue
    pkg = a.get_outermost().get_name()           # /Game/__ExternalActors__/...
    rel = 'JumpCut/Content' + pkg[len('/Game'):] + '.uasset'
    disk = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()),
                        'Content' + pkg[len('/Game'):] + '.uasset')
    rows.append({'label': lab, 'package': pkg, 'file': rel, 'exists': os.path.isfile(disk)})
with open(os.path.join(OUT, 'b1v_pkgs.json'), 'w') as fh:
    json.dump(rows, fh, indent=1)
for r in rows:
    print('%-22s exists=%-5s %s' % (r['label'], r['exists'], r['file']))
print('b1v_pkgs done')
