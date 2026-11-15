"""Save exactly what beat 1 round 6 touched (the coworker's side, the double driver, the camera
snap), and nothing else.

Never save_dirty_packages: it saves EVERY dirty package in the project, including another lane's,
and has already cost this repo a working editor and a floor of .tmp files in Saved/.

    py <repo>/tools/b1v_save.py
Writes Saved/jcpy/b1v_save.txt.
"""
import unreal, os, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
ASSETS = ['/Game/Game/Blueprints/BP_OpeningDirector',
          '/Game/Game/Blueprints/BP_Player',
          '/Game/Game/Cinematics/LS_Beat1_Opening']
ACTORS = ['B1_Cine_Director',      # re-placed by b1_opening_wire.py: new package
          'B1_Objective_Beacon',   # re-placed: new package
          'B1_Cine_HandCam',       # new this round
          'Coworker_Cafe',         # moved to the car's +Y side
          'C1_Cafe_Car',           # hidden grey box: collision off
          'C1_Cafe_CarCab',        # hidden grey box: collision off
          'C1_Cafe_CrashDriver']   # TouchRange / mesh collision re-set by the wire script

log = []
def say(s):
    log.append(str(s)); print(str(s))

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    assert ues.get_game_world() is None, 'PIE is running - stop it first'
    pkgs = []
    for p in ASSETS:
        o = unreal.load_asset(p)
        if o is None:
            say('MISSING %s' % p); continue
        pkgs.append(o.get_outermost())
        say('asset %-42s -> %s' % (p, o.get_outermost().get_name()))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    for lbl in ACTORS:
        a = by.get(lbl)
        if a is None:
            say('MISSING actor %s' % lbl); continue
        pkgs.append(a.get_outermost())
        say('actor %-42s -> %s' % (lbl, a.get_outermost().get_name()))
    uniq = []
    for p in pkgs:
        if p not in uniq:
            uniq.append(p)
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(uniq, False)
    say('save_packages -> %s (%d packages)' % (ok, len(uniq)))
    for p in uniq:
        f = ''
        try:
            f = unreal.SystemLibrary.get_system_path(p) or ''
        except Exception:
            pass
        say('   %-28s %s' % (p.get_name().split('/')[-1], f))
except Exception:
    say(traceback.format_exc())

with open(os.path.join(OUT, 'b1v_save.txt'), 'w') as f:
    f.write('\n'.join(log))
print('B1V_SAVE done')
