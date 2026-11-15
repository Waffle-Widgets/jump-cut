"""Save exactly what the 2026-11-15 car-flicker / ragdoll-landing pass touched, and nothing else.

Never save_dirty_packages: it saves EVERY dirty package in the project, including another lane's,
and has already cost this repo a working editor and a floor of .tmp files in Saved/.

    py <repo>/tools/b1w_save.py
Writes Saved/jcpy/b1w_save.txt.
"""
import unreal, os, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
ASSETS = ['/Game/Game/Blueprints/BP_OpeningDirector',
          '/Game/Game/Blueprints/BP_CrashDriver',
          '/Game/Game/Blueprints/BP_Coworker',
          '/Game/Game/Cinematics/LS_Beat1_Opening']
# re-placed by b1_opening_wire.py (new packages), plus the driver, who moved
ACTORS = ['B1_Cine_Director', 'B1_Objective_Beacon', 'C1_Cafe_CrashDriver']

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
        say('asset %-44s -> %s' % (p, o.get_outermost().get_name()))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    for lbl in ACTORS:
        a = by.get(lbl)
        if a is None:
            say('MISSING actor %s' % lbl); continue
        pkgs.append(a.get_outermost())
        say('actor %-44s -> %s' % (lbl, a.get_outermost().get_name()))
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
        say('   %s  %s' % (p.get_name(), f))
except Exception:
    say(traceback.format_exc())

with open(os.path.join(OUT, 'b1w_save.txt'), 'w') as f:
    f.write('\n'.join(log))
print('B1W_SAVE done')
