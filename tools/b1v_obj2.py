"""Does objective 2's beacon actually point at the coworker now that she has moved?

    py <repo>/tools/b1v_obj2.py
Runs in PIE. Drives the real BP_CrashDriver.DriverTryTouch (gated on range, so the player is
teleported into range first), then reads the objective state and where the beacon went.
"""
import unreal, os, json, math, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
L = []; res = {}
def say(s):
    L.append(str(s)); print(str(s))
def v3(x):
    return [round(x.x, 2), round(x.y, 2), round(x.z, 2)]

DIR = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector_C'
PLY = '/Game/Game/Blueprints/BP_Player.BP_Player_C'
DRV = '/Game/Game/Blueprints/BP_CrashDriver.BP_CrashDriver_C'
CW = '/Game/Game/Blueprints/BP_Coworker.BP_Coworker_C'

try:
    gw = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if gw is None:
        raise RuntimeError('PIE is not running')
    g = unreal.GameplayStatics
    pawn = g.get_all_actors_of_class(gw, unreal.load_object(None, PLY))[0]
    d = g.get_all_actors_of_class(gw, unreal.load_object(None, DIR))[0]
    drv = g.get_all_actors_of_class(gw, unreal.load_object(None, DRV))[0]
    cw = g.get_all_actors_of_class(gw, unreal.load_object(None, CW))[0]
    beacon = None
    for a in g.get_all_actors_of_class(gw, unreal.StaticMeshActor):
        if a.get_actor_label().startswith('B1_Objective_Beacon'):
            beacon = a; break

    say('before: objective=%s player=%s beacon=%s' % (
        d.get_editor_property('ObjectiveState'), v3(pawn.get_actor_location()),
        v3(beacon.get_actor_location())))

    # walk him into TouchRange of the body the way the game would, then run the real gate
    dl = drv.get_actor_location()
    pawn.set_actor_location(unreal.Vector(dl.x + 90.0, dl.y + 40.0, 94.15), False, True)
    drv.call_method('DriverTryTouch')
    d.call_method('CineDirectorStep', args=(0.016,))
    st = d.get_editor_property('ObjectiveState')
    spot = d.call_method('CineObjectiveSpot')
    say('after touch: objective=%s  CineObjectiveSpot=%s' % (st, spot))
    say('  HasFreezeFrame=%s  FireLit=%s' % (
        pawn.get_editor_property('HasFreezeFrame') if 'HasFreezeFrame' else '?',
        cw.get_editor_property('FireLit')))
    # a few more director steps so the beacon lerps to the new spot
    for _ in range(40):
        d.call_method('CineDirectorStep', args=(0.05,))
    res = {'objective': st,
           'spot': v3(spot) if hasattr(spot, 'x') else str(spot),
           'coworker': v3(cw.get_actor_location()),
           'beacon': v3(beacon.get_actor_location()),
           'beacon_hidden': beacon.get_editor_property('hidden')}
    res['beacon_vs_coworker_xy'] = round(math.hypot(
        beacon.get_actor_location().x - cw.get_actor_location().x,
        beacon.get_actor_location().y - cw.get_actor_location().y), 2)
    say(json.dumps(res))
except Exception as e:
    say('ERROR %r' % e); say(traceback.format_exc()); res['error'] = repr(e)

with open(os.path.join(OUT, 'b1v_obj2.txt'), 'w') as fh:
    fh.write('\n'.join(L))
print('b1v_obj2 done')
