"""Where did the body actually come to rest, and is the beat still a walk?

Two things the state sample cannot answer:
  * a ragdoll's COMPONENT transform is not where the body is - it follows the root bone through
    the mesh's own -78 deg / +18 cm offset, so it can read below the floor while the body is
    lying on it. Measure the BONES.
  * the landing spot moved 300 cm closer to where the player stands. If that is inside
    DriverTryTouch's range the power is granted on frame one and the "walk over and check on him"
    beat stops existing.

    py <repo>/tools/b1w_land.py        (PIE must be running)
Writes Saved/jcpy/b1w_land.json.
"""
import unreal, os, json, math, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
res = {}


def v(x):
    return [round(x.x, 1), round(x.y, 1), round(x.z, 1)]


try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_game_world()
    assert w is not None, 'no PIE world'
    B = '/Game/Game/Blueprints/'

    def allof(p):
        return list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_object(None, p)))

    drv = allof(B + 'BP_CrashDriver.BP_CrashDriver_C')[0]
    ply = allof(B + 'BP_Player.BP_Player_C')[0]
    d = allof(B + 'BP_OpeningDirector.BP_OpeningDirector_C')[0]

    mesh = drv.get_component_by_class(unreal.SkeletalMeshComponent)
    names = mesh.get_all_socket_names()
    bones = []
    try:
        bones = [str(b) for b in mesh.get_editor_property('skeletal_mesh_asset').get_editor_property(
            'skeleton').get_editor_property('bone_tree')]
    except Exception:
        bones = []
    # the reliable route: every bone the component knows about
    bn = []
    i = 0
    while True:
        try:
            n = mesh.get_bone_name(i)
        except Exception:
            break
        if not n or str(n) == 'None':
            break
        bn.append(str(n))
        i += 1
        if i > 400:
            break
    pts = []
    for n in bn:
        try:
            pts.append(mesh.get_socket_location(unreal.Name(n)))
        except Exception:
            pass
    res['bones'] = len(pts)
    if pts:
        res['bone_z_min'] = round(min(p.z for p in pts), 2)
        res['bone_z_max'] = round(max(p.z for p in pts), 2)
        res['bone_centroid'] = [round(sum(p.x for p in pts) / len(pts), 1),
                                round(sum(p.y for p in pts) / len(pts), 1),
                                round(sum(p.z for p in pts) / len(pts), 1)]
        res['bone_span_xy'] = [round(max(p.x for p in pts) - min(p.x for p in pts), 1),
                               round(max(p.y for p in pts) - min(p.y for p in pts), 1)]
        res['bone_x'] = [round(min(p.x for p in pts), 1), round(max(p.x for p in pts), 1)]
        res['bone_y'] = [round(min(p.y for p in pts), 1), round(max(p.y for p in pts), 1)]

    o, e = drv.get_actor_bounds(False)
    res['driver_bounds_origin'] = v(o)
    res['driver_bounds_extent'] = v(e)
    res['driver_actor_loc'] = v(drv.get_actor_location())
    res['mesh_world'] = v(mesh.get_world_location())
    res['player_loc'] = v(ply.get_actor_location())
    res['player_to_driver'] = round((ply.get_actor_location() - drv.get_actor_location()).length(), 1)
    res['objective'] = d.get_editor_property('ObjectiveState')
    for n in ('DriverTouched',):
        try:
            res[n] = drv.get_editor_property(n)
        except Exception as ex:
            res[n] = str(ex)
    for n in ('HasFreezeFrame',):
        try:
            res[n] = ply.get_editor_property(n)
        except Exception as ex:
            res[n] = str(ex)

    # the two cars, as they are drawn right now
    cars = {}
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        lbl = a.get_actor_label()
        if lbl in ('City_CafeCrashCar', 'B1_Cafe_CrashCar_GC'):
            cars[lbl] = {'hidden': bool(a.get_editor_property('hidden')), 'loc': v(a.get_actor_location())}
    res['cars'] = cars

    # is the resting place reachable? capsule sweep from the player to it
    TQ = unreal.TraceTypeQuery.TRACE_TYPE_QUERY1
    ign = [drv, ply]
    tgt = drv.get_actor_location()
    h = unreal.SystemLibrary.capsule_trace_single(
        w, ply.get_actor_location(), unreal.Vector(tgt.x, tgt.y, ply.get_actor_location().z),
        34.0, 88.0, TQ, False, ign, unreal.DrawDebugTrace.NONE, True)
    res['walk_blocked_by'] = None
    if h is not None:
        hd = h.to_dict()
        a = hd.get('hit_actor')
        res['walk_blocked_by'] = a.get_actor_label() if a else 'unknown'
    # floor under the body
    fh = unreal.SystemLibrary.line_trace_single(
        w, unreal.Vector(tgt.x, tgt.y, 220.0), unreal.Vector(tgt.x, tgt.y, -40.0), TQ, False,
        ign, unreal.DrawDebugTrace.NONE, True)
    res['floor_under_body'] = round(fh.to_dict()['location'].z, 2) if fh else None
except Exception:
    res['error'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1w_land.json'), 'w') as f:
    json.dump(res, f, indent=1, default=str)
print('B1W_LAND %s' % json.dumps({k: res[k] for k in list(res)[:6]}, default=str))
