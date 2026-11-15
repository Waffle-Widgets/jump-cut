"""THE levitation fix. A clip with force_root_lock=True and root_motion_root_lock=REF_POSE has its
root bone pinned to the SKELETON'S REFERENCE POSE - and every Meshy rig here puts its root at pelvis
height (CafeWalker 90.58, StreetGoon 92.46, CleaverBoss 87.26). So the whole character is drawn ~90 cm
in the air for as long as that clip plays.

7ef73e1 fixed the locomotion clips by moving them to ANIM_FIRST_FRAME (lock to the clip's own first
frame, where the root is 0) and missed the jump / fall / land clips. Measured in PIE: entering
MOVE_Falling lifts the player's mesh to exactly 90.6 cm and it takes 0.9 s to blend back after
landing - at the start of the game, on every jump, and after every input unlock.

    py <repo>/tools/b1y_rootlock.py          report: every clip with the broken combination
    py <repo>/tools/b1y_rootlock.py apply    set root_motion_root_lock = ANIM_FIRST_FRAME on them
Writes Saved/jcpy/b1y_rootlock.json. 'apply' also saves the packages and reads every value back.
"""
import unreal, os, sys, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
MODE = sys.argv[1] if len(sys.argv) > 1 else 'report'
res = {'mode': MODE}
# Only the clips a LIVE anim Blueprint plays on a MESHY rig. Epic's own mannequin clips are left
# alone on purpose: the mannequin's reference pose has its root ON THE FLOOR, so REF_POSE locking is
# correct for them (60 of the 85 matches are Epic's, and changing them would be noise at best).
# Confirmed by reading the asset references of each ABP: ABP_Unarmed_CWM plays the _CWM three,
# ABP_Unarmed_SGN plays the _SGN three, ABP_CleaverBoss has no jump states, and the legacy _CW set
# is referenced by nothing.
ONLY = {'MM_Jump_CWM', 'MM_Fall_Loop_CWM', 'MM_Land_CWM',
        'MM_Jump_SGN', 'MM_Fall_Loop_SGN', 'MM_Land_SGN'}
REF = unreal.RootMotionRootLock.REF_POSE
FIRST = unreal.RootMotionRootLock.ANIM_FIRST_FRAME

try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    bad, ok, skipped = [], [], []
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine', 'AnimSequence'), False):
        pn = str(ad.package_name)
        if not pn.startswith('/Game/'):
            continue
        a = ad.get_asset()
        try:
            frl = a.get_editor_property('force_root_lock')
            lock = a.get_editor_property('root_motion_root_lock')
        except Exception as e:
            skipped.append({'clip': pn, 'why': str(e)[:70]})
            continue
        row = {'clip': pn, 'force_root_lock': bool(frl), 'lock': str(lock)}
        if frl and lock == REF and str(ad.asset_name) in ONLY:
            bad.append(row)
        else:
            ok.append(row)
    bad.sort(key=lambda r: r['clip'])
    res['broken'] = bad
    res['broken_count'] = len(bad)
    res['healthy_count'] = len(ok)
    res['skipped'] = skipped

    if MODE == 'apply':
        done, failed = [], []
        pkgs = []
        for row in bad:
            a = unreal.load_asset(row['clip'])
            if a is None:
                failed.append({'clip': row['clip'], 'why': 'load failed'})
                continue
            try:
                a.set_editor_property('root_motion_root_lock', FIRST)
            except Exception as e:
                failed.append({'clip': row['clip'], 'why': 'set: ' + str(e)[:70]})
                continue
            # READ IT BACK - a set can be accepted and not take (CLAUDE.md)
            back = a.get_editor_property('root_motion_root_lock')
            if back != FIRST:
                failed.append({'clip': row['clip'], 'why': 'did not take, reads %s' % back})
                continue
            done.append({'clip': row['clip'], 'now': str(back),
                         'force_root_lock': bool(a.get_editor_property('force_root_lock'))})
            pkgs.append(a.get_outermost())
        res['set'] = done
        res['failed'] = failed
        if pkgs:
            saved = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
            res['saved'] = bool(saved)
            res['packages'] = [p.get_name() for p in pkgs]
            # and read back off the saved assets
            res['after'] = {}
            for row in done:
                a = unreal.load_asset(row['clip'])
                res['after'][row['clip'].split('/')[-1]] = str(a.get_editor_property('root_motion_root_lock'))
except Exception:
    res['error'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1y_rootlock.json'), 'w') as f:
    json.dump(res, f, indent=1)
print('B1Y_ROOTLOCK_%s broken=%d set=%d failed=%d' % (MODE.upper(), res.get('broken_count', -1),
                                                      len(res.get('set', [])), len(res.get('failed', []))))
