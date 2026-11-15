"""Which of the player's clips still carry the Meshy pelvis-height root? And is MoveLocked's class
default the thing that drops him into MOVE_Falling on the first tick?

    py <repo>/tools/b1y_clips.py
Reads only. Writes Saved/jcpy/b1y_clips.json.

root_z = bone 0's Z in the clip's own pose at t = 0, 25%, 50%, 75% of its length. A fixed clip reads
~0; an unfixed Meshy clip reads ~90 (the reference pose puts the root at pelvis height). The player
rises 90.6 cm for 0.9 s at the start of the cinematic, so whatever plays while he is FALLING is a
floater.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
res = {}

try:
    # ---- 1. BP_Player's own bool defaults: what is true at BeginPlay?
    pbp = unreal.load_asset('/Game/Game/Blueprints/BP_Player')
    cdo = unreal.get_default_object(pbp.generated_class())
    flags = {}
    for n in ('MoveLocked', 'InputLocked', 'IsRewinding', 'IsFrozenByBoss', 'IsDowned', 'IsLost',
              'HasWon', 'HasFreezeFrame', 'HasRewind', 'HasSplice'):
        try:
            flags[n] = str(cdo.get_editor_property(n))
        except Exception as e:
            flags[n] = 'ERR ' + str(e)[:60]
    msh = cdo.get_component_by_class(unreal.SkeletalMeshComponent)
    sk = msh.get_editor_property('skeletal_mesh_asset')
    ac = msh.get_editor_property('anim_class')
    res['player'] = {'flags': flags,
                     'mesh': sk.get_path_name() if sk else None,
                     'anim_class': str(ac) if ac else None}
    cm = cdo.get_component_by_class(unreal.CharacterMovementComponent)
    if cm:
        res['player']['default_land_movement_mode'] = str(cm.get_editor_property('default_land_movement_mode'))
        res['player']['gravity_scale'] = cm.get_editor_property('gravity_scale')

    # ---- 2. every AnimSequence on the player's skeleton, and where its root sits
    skel = sk.get_editor_property('skeleton')
    res['skeleton'] = skel.get_path_name()
    bone0 = sk.get_editor_property('skeleton').get_reference_pose() if False else None
    names = []
    try:
        names = [str(b) for b in skel.get_editor_property('bone_tree')]
    except Exception:
        pass
    # bone 0 by name from the mesh
    b0 = None
    try:
        b0 = unreal.SkeletalMeshComponent  # placeholder
        b0 = str(sk.get_editor_property('skeleton').get_name())
    except Exception:
        pass
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    clips = []
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine', 'AnimSequence'), False):
        pn = str(ad.package_name)
        if not pn.startswith('/Game/'):
            continue
        a = ad.get_asset()
        try:
            if a.get_editor_property('skeleton') != skel:
                continue
        except Exception:
            continue
        clips.append(a)
    res['clip_count'] = len(clips)

    # the root bone's name: take it from the skeletal mesh's ref skeleton via a temp component
    rootname = None
    try:
        rootname = str(unreal.AnimationLibrary.get_animation_track_names(clips[0])[0]) if clips else None
    except Exception:
        pass
    if rootname is None:
        for cand in ('Bone_000', 'root', 'Root'):
            try:
                t = unreal.AnimationLibrary.get_bone_pose_for_time(clips[0], cand, 0.0, False)
                rootname = cand
                break
            except Exception:
                continue
    res['root_bone'] = rootname

    rows = []
    for a in clips:
        pn = a.get_path_name()
        try:
            L = a.get_play_length()
        except Exception:
            L = 0.0
        zs = []
        for frac in (0.0, 0.25, 0.5, 0.75):
            try:
                tr = unreal.AnimationLibrary.get_bone_pose_for_time(a, rootname, L * frac, False)
                zs.append(round(tr.translation.z, 1))
            except Exception as e:
                zs.append('ERR')
        rows.append({'clip': pn.split('.')[0], 'len': round(L, 2), 'root_z': zs})
    rows.sort(key=lambda r: -(max([z for z in r['root_z'] if isinstance(z, float)] or [0])))
    res['clips'] = rows
    res['floaters'] = [r for r in rows if any(isinstance(z, float) and z > 20.0 for z in r['root_z'])]

except Exception:
    res['error'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1y_clips.json'), 'w') as f:
    json.dump(res, f, indent=1)
print('B1Y_CLIPS_DONE floaters=%d of %d' % (len(res.get('floaters', [])), res.get('clip_count', 0)))
