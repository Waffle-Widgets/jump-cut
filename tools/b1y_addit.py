"""Are the jump/fall/land clips flagged ADDITIVE? An additive clip played as a normal sequence is
applied on top of the skeleton's reference pose, and this rig's reference pose puts the root at
90.58 cm - which would explain a 90.6 cm lift from a clip whose own root track reads 0.

    py <repo>/tools/b1y_addit.py
Reads only. Writes Saved/jcpy/b1y_addit.json.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}
WANT = ['MM_Jump_CWM', 'MM_Fall_Loop_CWM', 'MM_Land_CWM', 'MM_Idle_CWM', 'MF_Unarmed_Walk_Fwd_CWM',
        'MM_Attack_01_CWM', 'MM_Jump', 'MM_Fall_Loop', 'MM_Land',
        'MM_Jump_SG', 'MM_Jump_SGN']
PROPS = ['additive_anim_type', 'ref_pose_type', 'ref_pose_seq', 'ref_frame_index',
         'retarget_source', 'enable_root_motion', 'root_motion_root_lock',
         'force_root_lock', 'interpolation', 'number_of_sampled_frames']
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    rows = {}
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine', 'AnimSequence'), False):
        n = str(ad.asset_name)
        if n not in WANT:
            continue
        a = ad.get_asset()
        d = {'path': str(ad.package_name)}
        for p in PROPS:
            try:
                v = a.get_editor_property(p)
                d[p] = v.get_path_name() if hasattr(v, 'get_path_name') and v else str(v)
            except Exception as e:
                d[p] = 'ERR'
        rows[n] = d
    res['clips'] = rows
except Exception:
    res['error'] = traceback.format_exc()
with open(os.path.join(OUT, 'b1y_addit.json'), 'w') as f:
    json.dump(res, f, indent=1)
print('B1Y_ADDIT_DONE')
