"""Live beat-1 state during PIE, plus two teleports to drive the beat without a keyboard.

    py <repo>/tools/b1_fb_pie.py state
    py <repo>/tools/b1_fb_pie.py tpdriver     put the player 190 cm from the driver
    py <repo>/tools/b1_fb_pie.py tpcoworker   put the player 190 cm from the coworker
    py <repo>/tools/b1_fb_pie.py title off|on ShowTitleOnStart on the game mode CDO

Appends to Saved/jcpy/b1_fb_pie.txt so a sequence of calls reads as one timeline.
"""
import unreal, os, sys, time

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'state'
ARG = sys.argv[2] if len(sys.argv) > 2 else ''

L = []
def say(s): L.append(str(s)); print(str(s))

def find(world, cls_path, label=None):
    cls = unreal.load_object(None, cls_path)
    got = unreal.GameplayStatics.get_all_actors_of_class(world, cls)
    return list(got)

try:
    if MODE == 'title':
        gm = unreal.load_asset('/Game/Game/Blueprints/BP_JumpCutGameMode')
        cdo = unreal.get_default_object(gm.generated_class())
        cdo.set_editor_property('ShowTitleOnStart', ARG == 'on')
        say('ShowTitleOnStart -> %s' % cdo.get_editor_property('ShowTitleOnStart'))
        raise SystemExit

    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w = ues.get_game_world()
    if w is None:
        say('NO PIE WORLD'); raise SystemExit
    say('\n===== %s  @ %s =====' % (MODE, time.strftime('%H:%M:%S')))

    dirs = find(w, '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector_C')
    cws = find(w, '/Game/Game/Blueprints/BP_Coworker.BP_Coworker_C')
    pls = find(w, '/Game/Game/Blueprints/BP_Player.BP_Player_C')
    drs = find(w, '/Game/Game/Blueprints/BP_CrashDriver.BP_CrashDriver_C')
    if not (dirs and pls):
        say('director=%d player=%d - not ready' % (len(dirs), len(pls))); raise SystemExit
    d, p = dirs[0], pls[0]
    cw = cws[0] if cws else None
    dr = drs[0] if drs else None

    if MODE == 'tpdriver' and dr is not None:
        tgt = dr.get_actor_location() + unreal.Vector(190.0, 0.0, 0.0)
        tgt.z = p.get_actor_location().z
        p.set_actor_location(tgt, False, False)
        say('player -> %s (%.0f cm from driver)' % (p.get_actor_location(),
            (p.get_actor_location() - dr.get_actor_location()).length()))
    if MODE == 'tpcoworker' and cw is not None:
        tgt = cw.get_actor_location() + unreal.Vector(180.0, 60.0, 0.0)
        tgt.z = p.get_actor_location().z
        p.set_actor_location(tgt, False, False)
        say('player -> %s (%.0f cm from coworker)' % (p.get_actor_location(),
            (p.get_actor_location() - cw.get_actor_location()).length()))

    if MODE == 'barson':
        ov = d.get_editor_property('OverlayRef')
        d.set_editor_property('BarTarget', 1.0)   # the director re-applies this every tick
        ov.call_method('CineBarsSet', (1.0,))
        ov.call_method('CineCaptionSet', (unreal.Text('LETTERBOX TEST - if you can read this the caption box works'),))
        for wn in ('BarTop', 'BarBottom', 'CapBox'):
            sub = ov.get_editor_property(wn)
            say('  %-10s vis=%s renderScale=%s desired=%s' % (
                wn, sub.get_visibility(), sub.get_editor_property('render_transform').scale,
                sub.get_desired_size()))
        say('  viewport size = %s' % str(unreal.WidgetLayoutLibrary.get_viewport_size(w)))

    for n in ('CineRunning', 'CineDone', 'CineTime', 'CineImpactTime', 'ObjectiveState',
              'BarAlpha', 'BarTarget', 'CapLeft', 'CapStage', 'RescueCine', 'RescueT', 'AutoBeats'):
        say('  dir.%-16s = %s' % (n, d.get_editor_property(n)))
    ov = d.get_editor_property('OverlayRef')
    say('  dir.OverlayRef     = %s  inViewport=%s' % (ov, ov.is_in_viewport() if ov else None))
    if ov:
        for wn in ('BarTop', 'BarBottom', 'CapBox', 'CapText'):
            sub = ov.get_editor_property(wn)
            extra = ''
            if wn == 'CapText':
                extra = ' text=%r' % str(sub.get_editor_property('text'))
            if wn in ('BarTop', 'BarBottom'):
                extra = ' renderScale=%s' % sub.get_editor_property('render_transform').scale
            say('    %-10s vis=%s%s' % (wn, sub.get_visibility(), extra))

    say('  player loc=%s  inputLocked=%s moveLocked=%s health=%s hasFreeze=%s' % (
        p.get_actor_location(), p.get_editor_property('InputLocked'),
        p.get_editor_property('MoveLocked'), p.get_editor_property('Health'),
        p.get_editor_property('HasFreezeFrame')))
    if dr is not None:
        say('  driver touched=%s  dist=%.0f' % (dr.get_editor_property('DriverTouched'),
            (p.get_actor_location() - dr.get_actor_location()).length()))
    if cw is not None:
        say('  coworker loc=%s dist=%.0f' % (cw.get_actor_location(),
            (p.get_actor_location() - cw.get_actor_location()).length()))
        for n in ('RescueArmed', 'RescueRequiresFreeze', 'FireLit', 'FuseLeft', 'Holding',
                  'Blown', 'CoworkerDead', 'BlastRadius'):
            say('    cw.%-20s = %s' % (n, cw.get_editor_property(n)))
        say('    cw dist from blast origin = %.0f' % (
            (cw.get_actor_location() - cw.get_editor_property('BlastOrigin')).length()))
    # the two cars
    for a in unreal.GameplayStatics.get_all_actors_with_tag(w, unreal.Name('JC_City')):
        if a.get_actor_label() == 'City_CafeCrashCar':
            say('  real wreck hidden=%s' % a.get_editor_property('hidden'))
except SystemExit:
    pass
except Exception as e:
    import traceback
    say('FAILED: %s' % e); say(traceback.format_exc())

with open(os.path.join(OUT, 'b1_fb_pie.txt'), 'a') as f:
    f.write('\n'.join(L) + '\n')
print('appended b1_fb_pie.txt')
