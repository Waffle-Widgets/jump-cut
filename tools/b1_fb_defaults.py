"""Beat 1 feedback pass: set the new director defaults and read the ones they depend on.

    py <repo>/tools/b1_fb_defaults.py report
    py <repo>/tools/b1_fb_defaults.py apply
"""
import unreal, os, sys

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = 'report'
for a in sys.argv[1:]:
    if a in ('report', 'apply'):
        MODE = a

L = []
def say(s): L.append(str(s)); print(str(s))

DEFAULTS = {
    'AutoBeats': True,
    'RescueMoveSpeed': 520.0,
    'RescueBlastAt': 3.0,
    'RescueEndAt': 4.8,
    'BarAlpha': 0.0,
    'BarTarget': 0.0,
    'CapLeft': 0.0,
    'CapStage': 0,
    'RescueCine': False,
}

try:
    bp = unreal.load_asset('/Game/Game/Blueprints/BP_OpeningDirector')
    cdo = unreal.get_default_object(bp.generated_class())
    cw = unreal.get_default_object(unreal.load_asset('/Game/Game/Blueprints/BP_Coworker').generated_class())

    say('-- director, the values the rescue depends on --')
    for n in ('ObjDriverLoc', 'ObjSafeLoc', 'ObjStreetLoc', 'ObjStreetDoneX', 'ObjectiveHeight',
              'CineImpactTime', 'CineBodyTime', 'CineLength'):
        say('  %-18s = %s' % (n, cdo.get_editor_property(n)))
    say('-- coworker --')
    for n in ('BlastRadius', 'BlastOrigin', 'FuseSeconds', 'HoldSpeed', 'HoldStopDist',
              'InteractRange', 'RescueRequiresFreeze', 'UseFireHazard', 'ExplosionDelay',
              'CoworkerHomeLocation', 'BlastPlayerDamage'):
        say('  %-22s = %s' % (n, cw.get_editor_property(n)))

    say('-- new director variables, now --')
    for n in sorted(DEFAULTS):
        try:
            say('  %-18s = %s' % (n, cdo.get_editor_property(n)))
        except Exception as e:
            say('  %-18s MISSING (%s)' % (n, e))

    if MODE == 'apply':
        say('\n-- applying --')
        for n, v in sorted(DEFAULTS.items()):
            cdo.set_editor_property(n, v)
            say('  %-18s -> %s' % (n, cdo.get_editor_property(n)))
        # the rescue is a cinematic now: no E first. Set on the class too, not only at
        # runtime in CineFinishOpening, so the skip-the-opening path behaves the same.
        cw.set_editor_property('RescueRequiresFreeze', False)
        say('  coworker RescueRequiresFreeze -> %s' % cw.get_editor_property('RescueRequiresFreeze'))
        # the placed director keeps its own serialized copy for anything it overrode
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for a in eas.get_all_level_actors():
            if a.get_actor_label() == 'B1_Cine_Director':
                say('\n-- placed B1_Cine_Director reads --')
                for n in sorted(DEFAULTS):
                    try:
                        say('  %-18s = %s' % (n, a.get_editor_property(n)))
                    except Exception as e:
                        say('  %-18s ERR %s' % (n, e))
except Exception as e:
    import traceback
    say('FAILED: %s' % e); say(traceback.format_exc())

open(os.path.join(OUT, 'b1_fb_defaults.txt'), 'w').write('\n'.join(L))
print('WROTE b1_fb_defaults.txt')
