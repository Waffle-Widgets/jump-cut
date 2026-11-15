"""Save ONLY the beat-1 cinematic assets, by path. Never save_dirty_packages (it saves every
dirty package in the project, including another lane's, and has already cost this repo time).
Also deliberately does NOT save /Game/Game/Cinematics/_ApiProbe, a throwaway a probe run left
in memory: it is never written to disk and vanishes when the editor closes.
"""
import unreal, os
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
PATHS = ['/Game/Game/Blueprints/BP_OpeningDirector',
         '/Game/Game/Cinematics/LS_Beat1_Opening']
log=[]
def say(s): log.append(str(s)); print(str(s))
try:
    pkgs = []
    for p in PATHS:
        o = unreal.load_asset(p)
        if o is None:
            say('MISSING %s' % p); continue
        pkgs.append(o.get_outermost())
        say('%s -> pkg %s' % (p, o.get_outermost().get_name()))
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
    say('save_packages -> %s (%d packages)' % (ok, len(pkgs)))
    for p in PATHS:
        o = unreal.load_asset(p)
        say('after: %s present=%s' % (p, o is not None))
    say('NOTE: _ApiProbe deliberately not saved.')
except Exception as e:
    import traceback
    say('ERROR %r' % e); say(traceback.format_exc())
with open(os.path.join(OUT,'b1_save_assets.txt'),'w') as f: f.write('\n'.join(log))
