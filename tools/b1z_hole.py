"""Where EXACTLY is the hole the car made in the cafe's west wall? Traced, not inferred.

The kit builds the hole at Blender y -1.35..1.65, and Art/Blender/jumpcut_city_kit.py's main() says
"Blender +Y is Unreal -Y", which would put it at Unreal y -165..135 - but the wreck's own bounds sit
at y -91..173, which fits the UNFLIPPED reading better. A 300 cm hole and a 4 mm tolerance is not a
thing to guess at, so this traces the wall instead.

    py <repo>/tools/b1z_hole.py
Writes Saved/jcpy/b1z_hole.json. Read only.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}
try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_editor_world()
    res['world'] = world.get_name()
    SL = unreal.SystemLibrary

    def shoot(y, z):
        a = unreal.Vector(-400.0, y, z)      # inside the room
        b = unreal.Vector(-800.0, y, z)      # out through the wall
        hit = SL.line_trace_single_by_profile(world, a, b, 'BlockAll', False, [],
                                              unreal.DrawDebugTrace.NONE, True,
                                              unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
        if hit is None:
            return None
        d = hit.to_dict()
        act = d.get('hit_actor')
        return {'x': round(d['location'].x, 2),
                'actor': act.get_actor_label() if act else None}

    # a sweep across the wall at knee height and at 2 m
    rows = {}
    for z in (40.0, 130.0, 200.0, 240.0, 250.0, 262.0):
        line = []
        for i in range(-30, 31):
            y = i * 10.0
            h = shoot(y, z)
            line.append([y, None if h is None else h['x'], None if h is None else h['actor']])
        rows['z%0.0f' % z] = line
    res['sweep'] = rows

    # summarise: at each z, the y range that is OPEN (no hit before x=-700)
    summary = {}
    for k, line in rows.items():
        open_ys = [r[0] for r in line if r[1] is None or r[1] < -700.0]
        summary[k] = [min(open_ys), max(open_ys)] if open_ys else None
    res['open_y'] = summary

    # and the exact wall faces: trace along +x from far outside at the middle of the hole
    probe = []
    for y in (-200.0, -170.0, -160.0, -140.0, -130.0, 0.0, 130.0, 140.0, 160.0, 170.0, 200.0):
        probe.append([y, shoot(y, 130.0)])
    res['edge_probe'] = probe
except Exception as e:
    res['error'] = repr(e)
    res['tb'] = traceback.format_exc()
with open(os.path.join(OUT, 'b1z_hole.json'), 'w') as fh:
    json.dump(res, fh, indent=1, default=str)
print('b1z_hole done')
