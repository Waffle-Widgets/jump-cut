"""Read-only. After re-running a batch retarget into a folder that already held its output, do the
montages and blend spaces still point at real animation?

`IKRetargetBatchOperation.duplicate_and_retarget` makes `_SG1` copies and renames them over the
originals. If a rename ever misses, the montage keeps a reference to an object that is gone and the
character plays nothing - which looks exactly like a finished job from the Blueprint side.

Writes Saved/jcpy/montage_refs.json.
"""
import json
import os
import traceback

import unreal

FOLDERS = ['/Game/Game/Imported/CafeWalker/MeshyAnims',
           '/Game/Game/Imported/StreetGoon/MeshyAnims',
           '/Game/Game/Imported/StreetGoon/Loco']

out = {'montages': [], 'blendspaces': [], 'bad': []}
eal = unreal.EditorAssetLibrary

try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for folder in FOLDERS:
        ar.scan_paths_synchronous([folder], True)
        for p in eal.list_assets(folder, True, False):
            a = unreal.load_asset(p)
            if a is None:
                out['bad'].append({'asset': p, 'why': 'will not load'})
                continue
            if isinstance(a, unreal.AnimMontage):
                segs, missing = 0, 0
                for tr in a.get_editor_property('slot_anim_tracks'):
                    for sg in tr.get_editor_property('anim_track').get_editor_property('anim_segments'):
                        segs += 1
                        ref = sg.get_editor_property('anim_reference')
                        if ref is None:
                            missing += 1
                        else:
                            # a stale reference resolves to an object with no frames
                            if ref.get_editor_property('sequence_length') <= 0.0:
                                missing += 1
                row = {'montage': str(a.get_name()), 'segments': segs, 'missing': missing,
                       'skeleton': str(a.get_editor_property('skeleton').get_name())
                       if a.get_editor_property('skeleton') else None,
                       'length': round(a.get_editor_property('sequence_length'), 3)}
                out['montages'].append(row)
                if missing or segs == 0 or row['length'] <= 0:
                    out['bad'].append(row)
            elif isinstance(a, unreal.BlendSpace) or isinstance(a, unreal.BlendSpace1D):
                samples = a.get_editor_property('sample_data')
                n = len(samples)
                miss = sum(1 for s in samples if s.get_editor_property('animation') is None)
                row = {'blendspace': str(a.get_name()), 'samples': n, 'missing': miss}
                out['blendspaces'].append(row)
                if miss or n == 0:
                    out['bad'].append(row)
except Exception:
    out['ERROR'] = traceback.format_exc()

d = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy')
if not os.path.isdir(d):
    os.makedirs(d)
with open(os.path.join(d, 'montage_refs.json'), 'w') as fh:
    json.dump(out, fh, indent=1)
unreal.log('MONTAGE-REFS bad=%d' % len(out.get('bad', [])))
