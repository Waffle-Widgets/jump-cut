"""Beat 1 round 6, probe 2: the coworker's reach range, the player's walk speed, and whether
the +Y side of the wreck opens up once C1_Cafe_Car (the hidden grey-box placeholder) stops
colliding. Reads only.

    py <repo>/tools/b1v_probe2.py
Writes Saved/jcpy/b1v_probe2.json/.txt
"""
import unreal, os, json, math, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
log = []; res = {}
def say(s):
    log.append(str(s)); print(str(s))
def v3(v):
    if isinstance(v, unreal.Rotator):
        return [round(v.roll, 2), round(v.pitch, 2), round(v.yaw, 2)]
    return [round(v.x, 2), round(v.y, 2), round(v.z, 2)]

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by_label = {a.get_actor_label(): a for a in eas.get_all_level_actors()}

    cw = by_label['Coworker_Cafe']
    d = {}
    for k in ('InteractRange', 'RescueArmed', 'RescueDone', 'CoworkerDead', 'CoworkerDown',
              'ExplosionDelay', 'CoworkerSafeOffset', 'HoldStopDist'):
        try:
            val = cw.get_editor_property(k)
            d[k] = v3(val) if isinstance(val, (unreal.Vector, unreal.Rotator)) else val
        except Exception as e:
            d[k] = '<%s: %s>' % (type(e).__name__, e)
    res['coworker'] = d
    say('coworker: %s' % json.dumps(d))

    pl = by_label['Player_Main']
    cm = pl.get_component_by_class(unreal.CharacterMovementComponent)
    pr = {'max_walk': cm.get_editor_property('max_walk_speed'),
          'max_accel': cm.get_editor_property('max_acceleration'),
          'braking': cm.get_editor_property('braking_deceleration_walking'),
          'rot_rate_yaw': cm.get_editor_property('rotation_rate').yaw,
          'orient': cm.get_editor_property('orient_rotation_to_movement')}
    res['player_move'] = pr
    say('player move: %s' % json.dumps(pr))

    # the cine camera spawnable's filmback, so the hand-off camera can match its FOV exactly
    seq = unreal.load_asset('/Game/Game/Cinematics/LS_Beat1_Opening')
    fb = {}
    for b in seq.get_bindings():
        tpl = b.get_object_template()
        if tpl is None or not isinstance(tpl, unreal.CineCameraActor):
            continue
        cc = tpl.get_cine_camera_component()
        if cc is None:
            cl = tpl.get_components_by_class(unreal.CineCameraComponent)
            cc = cl[0] if cl else None
        if cc is None:
            fb[b.get_name()] = 'no CineCameraComponent on the template (%s)' % tpl.get_name()
            continue
        f = cc.get_editor_property('filmback')
        focal = cc.get_editor_property('current_focal_length')
        fb[b.get_name()] = {
            'sensor_w': round(f.sensor_width, 4), 'sensor_h': round(f.sensor_height, 4),
            'focal': round(focal, 3),
            'hfov': round(math.degrees(2.0 * math.atan((f.sensor_width / 2.0) / focal)), 3),
            'focal_for_hfov90': round((f.sensor_width / 2.0) / math.tan(math.radians(45.0)), 4)}
    res['cine_filmback'] = fb
    say('cine filmback: %s' % json.dumps(fb))

    # ---- the player's camera pose at the hand-off, computed from the real rig
    arm = pl.get_component_by_class(unreal.SpringArmComponent)
    cam = pl.get_component_by_class(unreal.CameraComponent)
    armlen = arm.get_editor_property('target_arm_length')
    rel = arm.get_editor_property('relative_location')
    docoll = arm.get_editor_property('do_collision_test')
    END_YAW = by_label['B1_Cine_Director'].get_editor_property('CineEndYaw')
    pawnz = 2.0 + 90.0   # floor 2.0 + capsule half height
    origin = unreal.Vector(0.0, 0.0, pawnz + rel.z)
    fw = unreal.Rotator(0.0, 0.0, END_YAW).get_forward_vector()
    campos = unreal.Vector(origin.x - fw.x * armlen, origin.y - fw.y * armlen, origin.z - fw.z * armlen)
    res['handoff'] = {'end_yaw': END_YAW, 'arm_len': armlen, 'arm_rel_z': rel.z,
                      'do_collision_test': docoll, 'pawn_z': pawnz,
                      'cam_loc_if_pawn_at_origin': v3(campos),
                      'cam_rot': [0.0, 0.0, END_YAW], 'cam_fov': cam.get_editor_property('field_of_view')}
    say('hand-off player camera (pawn at origin): %s' % json.dumps(res['handoff']))

    # ---- does the +Y side open up with C1_Cafe_Car ignored?
    ignore = [by_label['C1_Cafe_Car']]
    HH, RR = 90.0, 35.0
    sysl = unreal.SystemLibrary
    def floor_at(x, y, from_z=180.0):
        hit = sysl.line_trace_single(w, unreal.Vector(x, y, from_z), unreal.Vector(x, y, -60.0),
                                     unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
                                     unreal.DrawDebugTrace.NONE, True)
        return None if hit is None else round(hit.to_dict()['location'].z, 2)
    def stands(x, y, z, ig):
        hit = sysl.capsule_trace_single(w, unreal.Vector(x, y, z + HH + 2.0),
                                        unreal.Vector(x, y, z + HH + 2.0), RR, HH,
                                        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ig,
                                        unreal.DrawDebugTrace.NONE, True)
        if hit is None:
            return True, None
        dd = hit.to_dict(); ha = dd.get('hit_actor')
        return False, (ha.get_actor_label() if ha else '?')
    def sweep(x0, y0, x1, y1, z, ig):
        hit = sysl.capsule_trace_single(w, unreal.Vector(x0, y0, z + HH + 2.0),
                                        unreal.Vector(x1, y1, z + HH + 2.0), RR, HH,
                                        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ig,
                                        unreal.DrawDebugTrace.NONE, True)
        if hit is None:
            return True, None
        dd = hit.to_dict(); ha = dd.get('hit_actor')
        return False, (ha.get_actor_label() if ha else '?')

    carbox = by_label['City_CafeCrashCar'].get_actor_bounds(False)
    res['car_bounds'] = {'origin': v3(carbox[0]), 'extent': v3(carbox[1])}
    say('car bounds: %s' % json.dumps(res['car_bounds']))

    rows = []
    for x in (-560, -500, -440, -380, -320, -260):
        for y in (120, 160, 200, 240, 280):
            fz = floor_at(x, y)
            row = {'xy': [x, y], 'floor': fz}
            if fz is None or fz > 20.0:
                row['ok'] = False; row['why'] = 'floor %s' % fz; rows.append(row); continue
            ok, who = stands(x, y, fz, [])
            row['stands'] = ok; row['stand_hit'] = who
            okc, whoc = stands(x, y, fz, ignore)
            row['stands_no_greybox'] = okc; row['stand_hit_ign'] = whoc
            s1, w1 = sweep(0.0, 0.0, x, y, fz, [])
            s2, w2 = sweep(0.0, 0.0, x, y, fz, ignore)
            row['walk_now'] = s1; row['walk_now_hit'] = w1
            row['walk_no_greybox'] = s2; row['walk_no_greybox_hit'] = w2
            # and from the driver's body, which is where the player will be standing
            s3, w3 = sweep(-300.0, -60.0, x, y, fz, ignore)
            row['walk_from_driver'] = s3; row['walk_from_driver_hit'] = w3
            row['dist_to_blast'] = round(math.hypot(x + 520.0, y - 0.0), 1)
            row['dist_from_driver'] = round(math.hypot(x + 300.0, y + 60.0), 1)
            rows.append(row)
    res['spots'] = rows
    for r in rows:
        say('   %-13s %s' % (r['xy'], json.dumps({k: v for k, v in r.items() if k != 'xy'})))
except Exception as e:
    say('ERROR %r' % e); say(traceback.format_exc()); res['error'] = repr(e)

with open(os.path.join(OUT, 'b1v_probe2.txt'), 'w') as fh:
    fh.write('\n'.join(log))
with open(os.path.join(OUT, 'b1v_probe2.json'), 'w') as fh:
    json.dump(res, fh, indent=1, default=str)
print('WROTE b1v_probe2.json')
