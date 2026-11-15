"""Stops sunlit surfaces washing out to white (Sun Nov 15, GameStation).

    py tools/jc_light_fix.py <sun intensity> <exposure offset> [save]
    py tools/jc_light_fix.py 5 -0.9          the "strong" option; 10 0 puts it back

Sun_Main was 10 against a sky light of 1 with exposure left on automatic, so everything in direct sun reached the
cel look already near white. Two level settings: the sun's intensity, and an exposure bias on PP_AnimeLook (the
engine default bias is 1.0, so an offset of -0.9 is written as 0.1 with the override on). r.ExposureOffset is
reset to 0 first: the A/B test used it, and a console variable outlives the Play session it was typed in.
"""
import os, sys
import unreal
out = []
def say(s):
    out.append(s); unreal.log('[light-fix] ' + s)
sun_i, off = float(sys.argv[1]), float(sys.argv[2])
W = unreal.UnrealEditorSubsystem().get_editor_world()
unreal.SystemLibrary.execute_console_command(W, 'r.ExposureOffset 0')
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
pk = []
for a in sub.get_all_level_actors():
    lab = a.get_actor_label()
    if lab == 'Sun_Main':
        c = a.light_component
        c.set_editor_property('intensity', sun_i)
        a.set_actor_transform(a.get_actor_transform(), False, True)
        say('Sun_Main intensity now %.2f' % c.intensity); pk.append(a.get_outermost())
    elif lab == 'PP_AnimeLook':
        s = a.settings
        s.set_editor_property('override_auto_exposure_bias', off != 0.0)
        s.set_editor_property('auto_exposure_bias', 1.0 + off)
        a.set_editor_property('settings', s)
        a.set_actor_transform(a.get_actor_transform(), False, True)
        r = a.settings
        say('PP_AnimeLook exposure bias now %.2f (override %s), blendables %d' % (r.auto_exposure_bias, r.override_auto_exposure_bias, len(r.weighted_blendables.array)))
        pk.append(a.get_outermost())
if len(sys.argv) > 3 and sys.argv[3] == 'save':
    say('SAVED ok=%s' % unreal.EditorLoadingAndSavingUtils.save_packages(pk, False))
else:
    say('not saved')
open(os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'light_fix.txt'), 'w').write('\n'.join(out) + '\n')
