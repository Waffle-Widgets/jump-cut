"""Do the jump/fall/land clips carry a track for the root bone at all? A clip with NO track for a
bone falls back to the skeleton's REFERENCE POSE for it at runtime - and this rig's reference pose
puts the root at pelvis height (90.6 cm). get_bone_pose_for_time then reads 0 either way, so the
'root_z = 0' in b1y_clips.json does not distinguish 'baked to the floor' from 'not animated'.

    py <repo>/tools/b1y_tracks.py
Reads only. Writes Saved/jcpy/b1y_tracks.json.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}
WANT = ['MM_Jump_CWM', 'MM_Fall_Loop_CWM', 'MM_Land_CWM', 'MM_Idle_CWM',
        'MF_Unarmed_Walk_Fwd_CWM', 'MF_Unarmed_Jog_Fwd_CWM', 'MM_Attack_01_CWM',
        'SK_CafeWalkerArmature_Idle', 'A_CafeWalker_Death_Authored']
BASE = '/Game/Game/Imported/CafeWalker/MeshyAnims/'
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    found = {}
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine', 'AnimSequence'), False):
        n = str(ad.asset_name)
        if n in WANT:
            found[n] = ad.get_asset()
    rows = {}
    for n in WANT:
        a = found.get(n)
        if a is None:
            rows[n] = 'NOT FOUND'
            continue
        try:
            names = [str(t) for t in unreal.AnimationLibrary.get_animation_track_names(a)]
        except Exception as e:
            rows[n] = 'track list failed: %s' % e
            continue
        root_tracks = [t for t in names if t.lower() in ('bone_000', 'root')]
        d = {'tracks': len(names), 'has_root_track': bool(root_tracks),
             'root_track_name': root_tracks[0] if root_tracks else None,
             'first5': names[:5], 'len': round(a.get_play_length(), 2)}
        if root_tracks:
            try:
                keys = unreal.AnimationLibrary.get_bone_pose_for_frame(a, root_tracks[0], 0, False)
                d['frame0_z'] = round(keys.translation.z, 2)
            except Exception as e:
                d['frame0_err'] = str(e)[:70]
        rows[n] = d
    res['clips'] = rows

    # the skeleton's own reference pose root height, read off the skeletal mesh
    for mp in ('/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker',
               '/Game/Game/Imported/CafeWalkerV2/SK_CafeWalkerV2'):
        m = unreal.load_asset(mp)
        if m is None:
            continue
        info = {'bones': None}
        try:
            info['bones'] = len(m.get_editor_property('skeleton').get_editor_property('bone_tree'))
        except Exception:
            pass
        try:
            sk = m.get_editor_property('skeleton')
            info['skeleton'] = sk.get_path_name()
        except Exception:
            pass
        res.setdefault('meshes', {})[mp.split('/')[-1]] = info
except Exception:
    res['error'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1y_tracks.json'), 'w') as f:
    json.dump(res, f, indent=1)
print('B1Y_TRACKS_DONE')
