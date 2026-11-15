"""Point the player at his authored clips: the blend space's walk and run, and the fight montages.

Run in the Unreal editor's console box, Play mode stopped, after `git lfs lock` (and clearing read-only) on
BS_Idle_Walk_Run_CWM and BP_Player:
    py <repo>/tools/unreal_player_authored_wire.py [blend] [montages] [save]
Result: <project>/Saved/jcpy/player_authored_wire.txt

The clips themselves come in first with tools/unreal_import_authored_clip.py (mode `anim`) as
/Game/Game/Imported/CafeWalker/Authored/A_CafeWalker_<Clip>_Authored. Anything not imported yet is skipped and
named, so this can be run as clips arrive.

  blend     BS_Idle_Walk_Run_CWM: the nine samples at speed 300 play Walk, the nine at 600 play Run. The nine at 0
            are left alone (they already play the authored idle).
  montages  makes AM_CafeWalker_<Clip>_Authored on DefaultSlot from each fight clip and sets BP_Player's class
            defaults PlayerAnimPunchA / PunchB / PunchFinisher / HitReact to them. Short blends, because a punch
            that takes a quarter of a second to blend in is a punch that lands late.

The jump, fall and land clips are played by states inside ABP_Unarmed_CWM; those are re-pointed through the MCP's
ObjectTools (the anim graph nodes are not reachable from here), not by this script.

Everything is read back after it is written, and nothing is saved unless every read-back matches.
"""
import os
import sys
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'player_authored_wire.txt')
AUTH = '/Game/Game/Imported/CafeWalker/Authored'
BS = '/Game/Game/Imported/CafeWalker/MeshyAnims/BS_Idle_Walk_Run_CWM'
BP = '/Game/Game/Blueprints/BP_Player'
SPEED = {300.0: 'Walk', 600.0: 'Run'}
# clip -> (BP_Player variable, blend in s, blend out s)
# Blend times, after watching the combo in dumped gameplay frames (Nov 15). At 0.03 s in, a chained hit cut from the
# last hit's recovery straight to the next clip's first frame, which is a rigid stand: every attack began with a
# snap to attention. At 0.10 s out he was back in the idle and dead still a third of a second after the hit. A
# longer blend IN carries the previous pose into the strike (the hit still lands by frame 3-4); a longer blend OUT
# lets the settle melt into the idle instead of arriving at it.
MONT = {'PunchA': ('PlayerAnimPunchA', 0.08, 0.22), 'PunchB': ('PlayerAnimPunchB', 0.08, 0.22),
        'Finisher': ('PlayerAnimPunchFinisher', 0.08, 0.25), 'HitReact': ('PlayerAnimHitReact', 0.04, 0.20),
        'FreezeCast': (None, 0.06, 0.20), 'SpliceBlink': (None, 0.04, 0.15)}
eal = unreal.EditorAssetLibrary
log = []


def say(s):
    log.append(str(s))
    unreal.log('[authored-wire] %s' % s)


def clip(name):
    p = '%s/A_CafeWalker_%s_Authored' % (AUTH, name)
    unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous([AUTH], True)
    a = eal.load_asset(p)
    return a if isinstance(a, unreal.AnimSequence) else None


def do_blend(save):
    bs = eal.load_asset(BS)
    samples = bs.get_editor_property('sample_data')
    have = {n: clip(n) for n in SPEED.values()}
    for n, a in have.items():
        if a is None:
            say('blend: %s not imported yet, its samples are left alone' % n)
        elif a.get_editor_property('skeleton') != bs.get_editor_property('skeleton'):
            say('REFUSING: %s is not on the blend space skeleton' % n)
            return
    fresh, want = [], []
    for s in samples:
        v = s.get_editor_property('sample_value')
        tgt = have.get(SPEED.get(round(v.y, 1))) or s.get_editor_property('animation')
        ns = unreal.BlendSample()
        ns.set_editor_property('animation', tgt)
        ns.set_editor_property('sample_value', v)
        ns.set_editor_property('rate_scale', 1.0 if tgt != s.get_editor_property('animation') else s.get_editor_property('rate_scale'))
        fresh.append(ns)
        want.append(tgt.get_name() if tgt else None)
    bs.modify()
    bs.set_editor_property('sample_data', fresh)
    back = bs.get_editor_property('sample_data')
    got = [s.get_editor_property('animation').get_name() if s.get_editor_property('animation') else None for s in back]
    by = {}
    for s, g in zip(back, got):
        by.setdefault(round(s.get_editor_property('sample_value').y, 1), set()).add(g)
    say('blend space now plays, by speed: %s' % {k: sorted(v) for k, v in sorted(by.items())})
    if got != want:
        say('FAILED: the blend space did not read back as written. NOT saved.')
        return
    if save:
        say('saved blend space -> %s' % unreal.EditorLoadingAndSavingUtils.save_packages([bs.get_outermost()], False))


def do_montages(save):
    bp = eal.load_asset(BP)
    cdo = unreal.get_default_object(bp.generated_class())
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    packages, changed = [], False
    for name, (var, b_in, b_out) in MONT.items():
        a = clip(name)
        if a is None:
            say('montages: %s not imported yet, skipped' % name)
            continue
        # A montage keeps the length its clip had when it was made. Re-importing a longer clip over the same asset
        # leaves the montage cutting it short, and a montage's segment cannot be edited from Python. So when the
        # lengths disagree a new montage is made beside the old one (_B, _C ...) and BP_Player is pointed at it;
        # the old one is left alone, because deleting an asset a loaded Blueprint points at nulls the pointer.
        mont = None
        for suffix in ('', '_B', '_C', '_D', '_E'):
            mname = 'AM_CafeWalker_%s_Authored%s' % (name, suffix)
            mont = eal.load_asset('%s/%s' % (AUTH, mname))
            if mont is None:
                f = unreal.AnimMontageFactory()
                f.set_editor_property('source_animation', a)
                f.set_editor_property('target_skeleton', a.get_editor_property('skeleton'))
                mont = tools.create_asset(mname, AUTH, unreal.AnimMontage, f)
                break
            if abs(mont.get_play_length() - a.get_play_length()) <= 0.01:
                break
            say('%s is %.3f s but its clip is now %.3f s: superseded' % (mname, mont.get_play_length(), a.get_play_length()))
            mont = None
        if mont is None:
            say('FAILED: could not make %s' % mname)
            continue
        bi = mont.get_editor_property('blend_in')
        bi.set_editor_property('blend_time', b_in)
        mont.set_editor_property('blend_in', bi)
        bo = mont.get_editor_property('blend_out')
        bo.set_editor_property('blend_time', b_out)
        mont.set_editor_property('blend_out', bo)
        mont.set_editor_property('blend_out_trigger_time', -1.0)
        mont.set_editor_property('enable_auto_blend_out', True)
        say('%s  length %.3f s (clip %.3f s)  blend in %.2f out %.2f' % (
            mname, mont.get_play_length(), a.get_play_length(), mont.get_editor_property('blend_in').get_editor_property('blend_time'),
            mont.get_editor_property('blend_out').get_editor_property('blend_time')))
        if abs(mont.get_play_length() - a.get_play_length()) > 0.01:
            say('    WARNING: the montage is not the length of its clip')
        packages.append(mont.get_outermost())
        if var:
            before = cdo.get_editor_property(var)
            cdo.set_editor_property(var, mont)
            after = cdo.get_editor_property(var)
            say('    BP_Player.%s: %s -> %s' % (var, before.get_name() if before else None, after.get_name() if after else None))
            if after != mont:
                say('    FAILED: the default did not take')
                return
            changed = changed or before != mont
    if changed:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        packages.append(bp.get_outermost())
    if save and packages:
        say('saved %s -> %s' % ([p.get_name().split('/')[-1] for p in packages], unreal.EditorLoadingAndSavingUtils.save_packages(packages, False)))


try:
    args = [a.lower() for a in sys.argv[1:]]
    if 'blend' in args:
        do_blend('save' in args)
    if 'montages' in args:
        do_montages('save' in args)
    if not ('blend' in args or 'montages' in args):
        say('usage: [blend] [montages] [save]')
except Exception:
    import traceback
    say('ERROR ' + traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')
