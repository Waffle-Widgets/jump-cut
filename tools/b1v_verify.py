"""Beat 1 round 6: read back what the three fixes actually built. Changes nothing.

    py <repo>/tools/b1v_verify.py
Writes Saved/jcpy/b1v_verify.txt / .json
"""
import unreal, os, json, math, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
L = []; res = {}
def say(s):
    L.append(str(s)); print(str(s))
def v3(x):
    if isinstance(x, unreal.Rotator):
        return [round(x.roll, 3), round(x.pitch, 3), round(x.yaw, 3)]
    return [round(x.x, 3), round(x.y, 3), round(x.z, 3)]

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}

    # ---------- the sequence
    seq = unreal.load_asset('/Game/Game/Cinematics/LS_Beat1_Opening')
    sq = {'end': round(seq.get_playback_end_seconds(), 3), 'spawn': {}, 'lastkey': {}}
    for b in seq.get_bindings():
        for t in b.get_tracks():
            cn = t.get_class().get_name()
            for sec in t.get_sections():
                if 'Spawn' in cn:
                    ch = sec.get_all_channels()[0]
                    sq['spawn'][b.get_name()] = [[k.get_time().frame_number.value, k.get_value()]
                                                 for k in ch.get_keys()]
                elif 'Transform' in cn and b.get_name() == 'CineCam_D_Hand':
                    chs = sec.get_all_channels()[:6]
                    sq['lastkey']['CineCam_D_Hand'] = {
                        str(c.channel_name): [[k.get_time().frame_number.value, round(k.get_value(), 3)]
                                              for k in c.get_keys()] for c in chs}
    res['sequence'] = sq
    say('sequence playback end  %s s' % sq['end'])
    for k, v in sq['spawn'].items():
        say('  spawn %-16s %s' % (k, v))
    say('  cut D keys: %s' % json.dumps(sq['lastkey'].get('CineCam_D_Hand', {})))

    # ---------- the actors
    hc = by.get('B1_Cine_HandCam')
    if hc is None:
        say('!! B1_Cine_HandCam MISSING')
    else:
        cc = hc.get_component_by_class(unreal.CameraComponent)
        res['handcam'] = {'loc': v3(hc.get_actor_location()), 'rot': v3(hc.get_actor_rotation()),
                          'fov': cc.get_editor_property('field_of_view'),
                          'constrain': cc.get_editor_property('constrain_aspect_ratio')}
        say('B1_Cine_HandCam %s' % json.dumps(res['handcam']))
    cw = by.get('Coworker_Cafe')
    res['coworker'] = {'loc': v3(cw.get_actor_location()), 'rot': v3(cw.get_actor_rotation())}
    say('Coworker_Cafe   %s' % json.dumps(res['coworker']))

    d = by.get('B1_Cine_Director')
    dd = {}
    for k in ('CineTurnStart', 'CineTurnScale', 'CineTurnOn', 'CineTurnDone', 'CineHandBlend',
              'CineBodyTime', 'CineImpactTime', 'CineLength', 'CineEndYaw'):
        dd[k] = d.get_editor_property(k)
    for k in ('CineHandCam', 'CoworkerRef', 'CineSeqActor', 'CineRealDriver', 'CineRealCar'):
        a = d.get_editor_property(k)
        dd[k] = a.get_actor_label() if isinstance(a, unreal.Actor) else str(a)
    dd['ObjCoworkerLoc'] = v3(d.get_editor_property('ObjCoworkerLoc'))
    res['director'] = dd
    say('director: %s' % json.dumps(dd))

    # ---------- is the path to her clear now, and is the body out of it?
    w = ues.get_editor_world()
    HH, RR = 90.0, 35.0
    sysl = unreal.SystemLibrary
    def sweep(a, b, z, ig):
        hit = sysl.capsule_trace_single(w, unreal.Vector(a[0], a[1], z + HH + 2.0),
                                        unreal.Vector(b[0], b[1], z + HH + 2.0), RR, HH,
                                        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ig,
                                        unreal.DrawDebugTrace.NONE, True)
        if hit is None:
            return True, None
        dd2 = hit.to_dict(); ha = dd2.get('hit_actor')
        return False, (ha.get_actor_label() if ha else '?')
    drv = by.get('C1_Cafe_CrashDriver')
    cwl = (cw.get_actor_location().x, cw.get_actor_location().y)
    ok1, who1 = sweep((0.0, 0.0), cwl, 2.0, [])
    ok2, who2 = sweep((0.0, 0.0), (-300.0, -60.0), 2.0, [])
    ok3, who3 = sweep((-240.0, -40.0), cwl, 2.0, [drv])
    res['paths'] = {'origin_to_coworker': [ok1, who1],
                    'origin_to_driver': [ok2, who2],
                    'past_driver_to_coworker': [ok3, who3]}
    say('path origin -> coworker        clear=%s hit=%s' % (ok1, who1))
    say('path origin -> driver body     clear=%s hit=%s' % (ok2, who2))
    say('path past body -> coworker     clear=%s hit=%s' % (ok3, who3))
    dx = cwl[0] + 300.0; dy = cwl[1] + 60.0
    res['coworker_dist_from_body'] = round(math.hypot(dx, dy), 1)
    res['coworker_dist_from_blast'] = round(math.hypot(cwl[0] + 520.0, cwl[1]), 1)
    say('coworker: %.1f cm from the body (InteractRange %s), %.1f cm from the blast (radius %s)' % (
        res['coworker_dist_from_body'], cw.get_editor_property('InteractRange'),
        res['coworker_dist_from_blast'], cw.get_editor_property('BlastRadius')))
except Exception as e:
    say('ERROR %r' % e); say(traceback.format_exc()); res['error'] = repr(e)

with open(os.path.join(OUT, 'b1v_verify.txt'), 'w') as fh:
    fh.write('\n'.join(L))
with open(os.path.join(OUT, 'b1v_verify.json'), 'w') as fh:
    json.dump(res, fh, indent=1, default=str)
print('b1v_verify done')
