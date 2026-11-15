"""Beat 1 feedback round 6 probe (2026-11-15): the coworker's side of the car, the double
driver, and the camera snap at the hand-off.

    py <repo>/tools/b1v_probe.py

Writes Saved/jcpy/b1v_probe.json + .txt. Reads only; changes nothing.
"""
import unreal, os, json, math, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
log = []
res = {}
def say(s):
    log.append(str(s)); print(str(s))

def v3(v):
    if isinstance(v, unreal.Rotator):
        return [round(v.roll, 2), round(v.pitch, 2), round(v.yaw, 2)]
    return [round(v.x, 2), round(v.y, 2), round(v.z, 2)]

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_editor_world()
    say('world=%s  pie=%s' % (w.get_name(), ues.get_game_world() is not None))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    acts = list(eas.get_all_level_actors())
    by_label = {a.get_actor_label(): a for a in acts}

    # ---------------- the actors that matter to this round
    WANT = ['Coworker_Cafe', 'City_CafeCrashCar', 'B1_Cafe_CrashCar_GC', 'C1_Cafe_CrashDriver',
            'B1_Cine_Director', 'B1_Objective_Beacon', 'B1_Cafe_Fire', 'B1_Cafe_BlastRing',
            'B1_Cafe_WallPanel_GC', 'C1_Cafe_Car', 'B1_Cafe_DebrisFloor', 'B1_Cine_Seq']
    res['actors'] = {}
    for lab in WANT:
        a = by_label.get(lab)
        if a is None:
            say('%-24s MISSING' % lab); res['actors'][lab] = None; continue
        o, e = a.get_actor_bounds(False)
        r = a.get_actor_rotation()
        d = {'loc': v3(a.get_actor_location()),
             'rot': [round(r.roll, 1), round(r.pitch, 1), round(r.yaw, 1)],
             'origin': v3(o), 'extent': v3(e), 'cls': a.get_class().get_name(),
             'hidden': a.is_hidden_ed() if hasattr(a, 'is_hidden_ed') else None,
             'hidden_game': a.get_editor_property('hidden')}
        res['actors'][lab] = d
        say('%-24s loc=%s rot=%s extent=%s %s' % (lab, d['loc'], d['rot'], d['extent'], d['cls']))

    # anything in the cafe area, so I can see what else is near a candidate spot
    say('')
    say('--- actors with origin inside the cafe box x -900..300 y -450..450')
    near = []
    for a in acts:
        o, e = a.get_actor_bounds(False)
        if -900 <= o.x <= 300 and -450 <= o.y <= 450 and o.z < 400:
            near.append({'label': a.get_actor_label(), 'origin': v3(o), 'extent': v3(e),
                         'cls': a.get_class().get_name()})
    near.sort(key=lambda d: d['origin'][0])
    res['cafe_actors'] = near
    for d in near:
        say('   %-34s o=%-26s e=%s' % (d['label'], d['origin'], d['extent']))

    # ---------------- the player's camera rig, so the cinematic can end exactly on it
    say('')
    pl = by_label.get('Player_Main')
    if pl is None:
        for a in acts:
            if 'BP_Player' in a.get_class().get_name():
                pl = a; break
    pcls = unreal.load_class(None, '/Game/Game/Blueprints/BP_Player.BP_Player_C')
    pcdo = unreal.get_default_object(pcls)
    rig = {}
    src = pl if pl is not None else pcdo
    for c in src.get_components_by_class(unreal.SpringArmComponent):
        rig['arm'] = {'name': c.get_name(),
                      'len': c.get_editor_property('target_arm_length'),
                      'socket_offset': v3(c.get_editor_property('socket_offset')),
                      'target_offset': v3(c.get_editor_property('target_offset')),
                      'rel_loc': v3(c.get_editor_property('relative_location')),
                      'use_pawn_cr': c.get_editor_property('use_pawn_control_rotation'),
                      'inherit_yaw': c.get_editor_property('inherit_yaw'),
                      'inherit_pitch': c.get_editor_property('inherit_pitch'),
                      'lag': c.get_editor_property('enable_camera_lag'),
                      'lag_speed': c.get_editor_property('camera_lag_speed'),
                      'rot_lag': c.get_editor_property('enable_camera_rotation_lag'),
                      'rot_lag_speed': c.get_editor_property('camera_rotation_lag_speed')}
    for c in src.get_components_by_class(unreal.CameraComponent):
        rig['cam'] = {'name': c.get_name(), 'rel_loc': v3(c.get_editor_property('relative_location')),
                      'fov': c.get_editor_property('field_of_view'),
                      'use_pawn_cr': c.get_editor_property('use_pawn_control_rotation')}
    cm = pcdo.character_movement
    rig['move'] = {'orient_to_movement': cm.get_editor_property('orient_rotation_to_movement'),
                   'rot_rate': v3(cm.get_editor_property('rotation_rate')),
                   'use_controller_yaw': pcdo.get_editor_property('use_controller_rotation_yaw')}
    cap = pcdo.capsule_component
    rig['capsule'] = {'half_height': cap.get_editor_property('capsule_half_height'),
                      'radius': cap.get_editor_property('capsule_radius')}
    if pl is not None:
        r = pl.get_actor_rotation()
        rig['placed'] = {'label': pl.get_actor_label(), 'loc': v3(pl.get_actor_location()),
                         'rot': [round(r.roll, 1), round(r.pitch, 1), round(r.yaw, 1)]}
    res['player_rig'] = rig
    say('player rig: %s' % json.dumps(rig, indent=1))

    # PlayerStart too - the pawn spawns there, not at the placed actor
    for a in acts:
        if isinstance(a, unreal.PlayerStart):
            r = a.get_actor_rotation()
            res['player_start'] = {'label': a.get_actor_label(), 'loc': v3(a.get_actor_location()),
                                   'rot': [round(r.roll, 1), round(r.pitch, 1), round(r.yaw, 1)]}
            say('PlayerStart %s' % res['player_start'])

    # ---------------- the sequence: which tracks exist on each binding
    say('')
    seq = unreal.load_asset('/Game/Game/Cinematics/LS_Beat1_Opening')
    sq = {'start': seq.get_playback_start_seconds(), 'end': seq.get_playback_end_seconds(),
          'bindings': []}
    for b in seq.get_bindings():
        bd = {'name': b.get_name(), 'tracks': []}
        for t in b.get_tracks():
            td = {'cls': t.get_class().get_name(), 'sections': []}
            for sec in t.get_sections():
                chans = sec.get_all_channels()
                try:
                    rng = [round(sec.get_start_frame_seconds(), 3),
                           round(sec.get_end_frame_seconds(), 3)]
                except Exception as ex:
                    rng = 'infinite (%s)' % type(ex).__name__
                cd = []
                for c in chans:
                    e = {'name': str(c.channel_name), 'keys': c.get_num_keys()}
                    try:
                        e['values'] = [[round(k.get_time().frame_number.value / 30.0, 3),
                                        k.get_value()] for k in c.get_keys()]
                    except Exception as ex:
                        e['values'] = 'ERR %s' % ex
                    cd.append(e)
                td['sections'].append({'range': rng, 'channels': cd})
            bd['tracks'].append(td)
        sq['bindings'].append(bd)
        say('binding %-20s %s' % (bd['name'], [t['cls'] for t in bd['tracks']]))
        for t in bd['tracks']:
            if 'Spawn' in t['cls']:
                say('     SPAWN %s' % json.dumps(t['sections']))
    sq['master'] = []
    for t in seq.get_tracks():
        ms = []
        for s2 in t.get_sections():
            try:
                ms.append([round(s2.get_start_frame_seconds(), 3), round(s2.get_end_frame_seconds(), 3)])
            except Exception:
                ms.append('infinite')
        md = {'cls': t.get_class().get_name(), 'sections': ms}
        sq['master'].append(md)
        say('master %-34s %s' % (md['cls'], md['sections']))
    res['sequence'] = sq

    # the last keys of CineDriver's transform, so I know where the thrown body stops
    for b in seq.get_bindings():
        if b.get_name() not in ('CineDriver', 'CineCar'):
            continue
        for t in b.get_tracks():
            if 'Transform' not in t.get_class().get_name():
                continue
            for sec in t.get_sections():
                ch = sec.get_all_channels()
                dump = {}
                for c in ch[:6]:
                    try:
                        ks = c.get_keys()
                        dump[str(c.channel_name)] = [
                            [round(k.get_time().frame_number.value / 30.0, 3), round(k.get_value(), 2)]
                            for k in ks]
                    except Exception as e:
                        dump[str(c.channel_name)] = 'ERR %s' % e
                res.setdefault('keys', {})[b.get_name()] = dump
                say('')
                say('%s keys: %s' % (b.get_name(), json.dumps(dump)))

    # ---------------- the player's clip library: is there anything that turns in place?
    say('')
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous(['/Game/Game/Imported'], True)
    f = unreal.ARFilter(class_names=['AnimSequence'], recursive_paths=True,
                        package_paths=['/Game/Game/Imported'])
    names = sorted(str(a.asset_name) for a in ar.get_assets(f))
    res['clips_all_count'] = len(names)
    hits = [n for n in names if any(k in n.lower() for k in
            ('turn', 'pivot', 'rot', 'start', 'stop', 'idle'))]
    res['clips_turnish'] = hits
    say('%d AnimSequences under /Game/Game/Imported; turn/pivot/idle-ish: %s' % (len(names), hits))
    cwm = [n for n in names if n.endswith('_CWM')]
    res['clips_cwm'] = cwm
    say('player (_CWM) clips: %s' % cwm)

    # ---------------- the coworker: her dials and where she stands
    say('')
    cw = by_label.get('Coworker_Cafe')
    if cw is not None:
        d = {}
        for k in ('CoworkerSafeOffset', 'BlastRadius', 'BlastOrigin', 'HoldSpeed',
                  'HoldStopDist', 'RescueRequiresFreeze', 'UseFireHazard'):
            try:
                val = cw.get_editor_property(k)
                d[k] = v3(val) if isinstance(val, (unreal.Vector, unreal.Rotator)) else val
            except Exception as e:
                d[k] = '<%s>' % type(e).__name__
        res['coworker'] = d
        say('coworker dials: %s' % json.dumps(d))

    # ---------------- traces: is the +Y side of the car clear for her, and is the path clear?
    say('')
    HH = rig['capsule']['half_height']; RR = rig['capsule']['radius']
    sysl = unreal.SystemLibrary
    def floor_at(x, y, from_z=180.0):
        hit = sysl.line_trace_single(w, unreal.Vector(x, y, from_z), unreal.Vector(x, y, -60.0),
                                     unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], 
                                     unreal.DrawDebugTrace.NONE, True)
        if hit is None:
            return None
        return round(hit.to_dict()['location'].z, 2)
    def stands(x, y, z):
        hit = sysl.capsule_trace_single(w, unreal.Vector(x, y, z + HH + 2.0),
                                        unreal.Vector(x, y, z + HH + 2.0), RR, HH,
                                        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
                                        unreal.DrawDebugTrace.NONE, True)
        if hit is None:
            return True, None
        dd = hit.to_dict()
        ha = dd.get('hit_actor')
        return False, (ha.get_actor_label() if ha else '?')
    def sweep(x0, y0, x1, y1, z):
        hit = sysl.capsule_trace_single(w, unreal.Vector(x0, y0, z + HH + 2.0),
                                        unreal.Vector(x1, y1, z + HH + 2.0), RR, HH,
                                        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
                                        unreal.DrawDebugTrace.NONE, True)
        if hit is None:
            return True, None, None
        dd = hit.to_dict()
        ha = dd.get('hit_actor')
        return False, (ha.get_actor_label() if ha else '?'), v3(dd['location'])

    cands = []
    for x in (-460, -400, -340, -300, -240, -180, -120):
        for y in (90, 140, 190, 240, 290):
            fz = floor_at(x, y)
            if fz is None or fz > 20.0:
                cands.append({'xy': [x, y], 'floor': fz, 'ok': False, 'why': 'floor %s' % fz})
                continue
            ok, who = stands(x, y, fz)
            if not ok:
                cands.append({'xy': [x, y], 'floor': fz, 'ok': False, 'why': 'blocked by %s' % who})
                continue
            sok, swho, sloc = sweep(0.0, 0.0, x, y, fz)
            cands.append({'xy': [x, y], 'floor': fz, 'ok': True,
                          'walkable_from_origin': sok, 'sweep_hit': swho, 'sweep_stop': sloc})
    res['coworker_candidates'] = cands
    for c in cands:
        say('   %-14s %s' % (c['xy'], json.dumps({k: v for k, v in c.items() if k != 'xy'})))

    # and prove the complaint: is the path from the origin to the CURRENT coworker spot blocked?
    if cw is not None:
        cl = cw.get_actor_location()
        fz = floor_at(cl.x, cl.y)
        sok, swho, sloc = sweep(0.0, 0.0, cl.x, cl.y, fz if fz is not None else 2.0)
        res['path_to_current_coworker'] = {'to': v3(cl), 'floor': fz, 'clear': sok,
                                           'hit': swho, 'stop': sloc}
        say('')
        say('path origin -> current coworker %s : clear=%s hit=%s stop=%s' % (v3(cl), sok, swho, sloc))
        # and from the driver's body outward, which is the leg the owner says is blocked
        dl = by_label['C1_Cafe_CrashDriver'].get_actor_location() if 'C1_Cafe_CrashDriver' in by_label else None
        if dl is not None:
            sok2, swho2, sloc2 = sweep(dl.x, dl.y, cl.x, cl.y, 2.0)
            res['path_driver_to_coworker'] = {'clear': sok2, 'hit': swho2, 'stop': sloc2}
            say('path driver -> coworker        : clear=%s hit=%s stop=%s' % (sok2, swho2, sloc2))
except Exception as e:
    say('ERROR %r' % e); say(traceback.format_exc())
    res['error'] = repr(e)

with open(os.path.join(OUT, 'b1v_probe.txt'), 'w') as fh:
    fh.write('\n'.join(log))
with open(os.path.join(OUT, 'b1v_probe.json'), 'w') as fh:
    json.dump(res, fh, indent=1, default=str)
print('WROTE %s' % os.path.join(OUT, 'b1v_probe.json'))
