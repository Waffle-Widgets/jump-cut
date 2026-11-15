"""Where should the thrown driver LAND? ("the ragdoll went to a place that was hard to get to")

The old spot (-395, -215) is INSIDE City_Cafe_00_CafeCounter's footprint (x -584..-76,
y -285..-196): the body was landing on the service side of the bar, which is why reaching it was
awkward. This picks a spot with a real capsule's worth of room on the open floor, on the car's
RIGHT side (-Y, which is screen-right from where the player stands), as close to the wreck as is
actually clear, and with a clean capsule sweep from the middle of the room.

Bounds are useless here - City_CafeShell's box covers the whole room and the cameras' boxes cover
20 m - so every test below is a real collision trace, not a box test.

    py <repo>/tools/b1w_spot.py          report only
    py <repo>/tools/b1w_spot.py typetest also check CineRealCar will accept a StaticMeshActor
Writes Saved/jcpy/b1w_spot.json.
"""
import unreal, os, sys, json, math, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'report'
res = {'mode': MODE}

XMIN, XMAX, YMIN, YMAX = -560.0, 500.0, -420.0, 420.0
CAR = unreal.Vector(-520.0, 0.0, 0.0)
FROM = unreal.Vector(150.0, 0.0, 94.0)     # the middle of the room, player capsule height
R, HH = 34.0, 88.0                         # the player capsule
CLEAR_R = 100.0                            # a sprawled body plus someone standing over it


def hitinfo(h):
    try:
        d = h.to_dict()
        a = d.get('hit_actor')
        return {'actor': a.get_actor_label() if a else None,
                'loc': [round(d['location'].x, 1), round(d['location'].y, 1),
                        round(d['location'].z, 1)],
                'initial_overlap': bool(d.get('initial_overlap'))}
    except Exception as e:
        return {'err': str(e)}


try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    assert ues.get_game_world() is None, 'PIE is running - stop it first'
    w = ues.get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    acts = eas.get_all_level_actors()
    IGNORE = []
    for a in acts:
        n = a.get_actor_label()
        if n.startswith('Marker_') or n in ('Player_Main', 'Coworker_Cafe', 'C1_Cafe_CrashDriver'):
            IGNORE.append(a)
    TQ = unreal.TraceTypeQuery.TRACE_TYPE_QUERY1          # Visibility

    def floor_z(x, y):
        h = unreal.SystemLibrary.line_trace_single(
            w, unreal.Vector(x, y, 220.0), unreal.Vector(x, y, -30.0), TQ, False, IGNORE,
            unreal.DrawDebugTrace.NONE, True)
        if h is None:
            return None
        return h.to_dict()['location'].z

    def free_at(x, y, z):
        """a player capsule standing here touches nothing"""
        h = unreal.SystemLibrary.capsule_trace_single(
            w, unreal.Vector(x, y, z + HH + 2.0), unreal.Vector(x, y, z + HH + 1.0), R, HH,
            TQ, False, IGNORE, unreal.DrawDebugTrace.NONE, True)
        return h is None

    def clear_radius(x, y, z, want):
        """nothing solid within `want` cm, tested on 12 spokes"""
        for i in range(12):
            a = i * math.pi / 6.0
            h = unreal.SystemLibrary.line_trace_single(
                w, unreal.Vector(x, y, z + 40.0),
                unreal.Vector(x + math.cos(a) * want, y + math.sin(a) * want, z + 40.0),
                TQ, False, IGNORE, unreal.DrawDebugTrace.NONE, True)
            if h is not None:
                return False
        return True

    def walkable(x, y, z):
        h = unreal.SystemLibrary.capsule_trace_single(
            w, FROM, unreal.Vector(x, y, z + HH + 2.0), R, HH, TQ, False, IGNORE,
            unreal.DrawDebugTrace.NONE, True)
        return h is None

    cands = []
    rejected = {'no_floor': 0, 'high_floor': 0, 'occupied': 0, 'tight': 0, 'unreachable': 0,
                'range': 0}
    x = XMIN
    while x <= XMAX:
        y = YMIN
        while y <= YMAX:
            d_car = math.hypot(x - CAR.x, y - CAR.y)
            if not (250.0 <= d_car <= 700.0) or y > -20.0:
                rejected['range'] += 1
                y += 20.0
                continue
            z = floor_z(x, y)
            if z is None:
                rejected['no_floor'] += 1
            elif z > 20.0:
                rejected['high_floor'] += 1
            elif not free_at(x, y, z):
                rejected['occupied'] += 1
            elif not clear_radius(x, y, z, CLEAR_R):
                rejected['tight'] += 1
            elif not walkable(x, y, z):
                rejected['unreachable'] += 1
            else:
                cands.append({'x': x, 'y': y, 'z': round(z, 2), 'from_car': round(d_car, 1),
                              'from_room': round(math.hypot(x - FROM.x, y - FROM.y), 1)})
            y += 20.0
        x += 20.0

    cands.sort(key=lambda r: r['from_car'])
    res['rejected'] = rejected
    res['n_candidates'] = len(cands)
    res['candidates'] = cands[:15]
    if cands:
        res['best'] = cands[0]
        b = cands[0]
        res['best_roomy'] = {str(r): clear_radius(b['x'], b['y'], b['z'], r)
                             for r in (100.0, 130.0, 160.0, 200.0)}

    # ---------------- can CineRealCar hold a plain StaticMeshActor? ---------------------------
    by = {a.get_actor_label(): a for a in acts}
    d = by.get('B1_Cine_Director')
    stat = by.get('City_CafeCrashCar')
    t = {'director': bool(d), 'static_car': bool(stat)}
    if d is not None:
        cur = d.get_editor_property('CineRealCar')
        t['CineRealCar_now'] = cur.get_actor_label() if cur else None
        if MODE == 'typetest' and stat is not None:
            try:
                d.set_editor_property('CineRealCar', stat)
                back = d.get_editor_property('CineRealCar')
                t['accepts_static_mesh_actor'] = (back == stat)
                if cur is not None:
                    d.set_editor_property('CineRealCar', cur)
                    t['restored'] = d.get_editor_property('CineRealCar').get_actor_label()
            except Exception as e:
                t['accepts_static_mesh_actor'] = False
                t['assign_error'] = str(e)
    res['cine_real_car'] = t

    # where the body is now, and what is under the OLD spot
    old = unreal.Vector(-395.0, -215.0, 0.0)
    res['old_spot'] = {'floor_z': floor_z(old.x, old.y),
                       'free': free_at(old.x, old.y, 0.0),
                       'clear_100': clear_radius(old.x, old.y, 0.0, 100.0),
                       'walkable': walkable(old.x, old.y, 0.0)}
except Exception:
    res['error'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1w_spot.json'), 'w') as f:
    json.dump(res, f, indent=1, default=str)
print('B1W_SPOT %s n=%s best=%s' % (MODE, res.get('n_candidates'), res.get('best')))
