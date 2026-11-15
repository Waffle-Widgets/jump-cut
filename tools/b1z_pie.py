"""Drive and measure beat 1's OPENING cinematic in PIE: the breakable wall, the fire that lights
in the third cut and freezes with Freeze Frame, and the driver thrown out as a ragdoll.

    py <repo>/tools/b1z_pie.py open      begin the opening and step its own clock to the end
    py <repo>/tools/b1z_pie.py state     one sample of everything that matters, right now
    py <repo>/tools/b1z_pie.py freeze    prove the fire stops while Freeze Frame is active
    py <repo>/tools/b1z_pie.py title off|on   ShowTitleOnStart on the game mode CDO

WHY THE CLOCK IS STEPPED BY HAND. Python runs ON the game thread, so a `time.sleep` here stops
the very world it is waiting for - and an 11 s sequence is over long before a second MCP round
trip (5-8 s) can arrive. So `open` calls BP_OpeningDirector.CineDirectorStep with a fixed delta
itself: the director's Tick cannot run while this script holds the thread, so this loop is the
only thing advancing it, and every trigger is exercised through the real function.

What that CANNOT show is physics: no ticks happen while the loop runs, so Chaos debris does not
fall and the ragdoll does not settle. `open` proves each trigger FIRED and the physics state was
APPLIED (the collection went Dynamic, the mesh is simulating); run `state` a few seconds later,
after real PIE ticks, to see where it all actually came to rest.

Appends to Saved/jcpy/b1z_pie.txt so a run of calls reads as one timeline.
"""
import unreal, os, sys, time

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'state'
ARG = sys.argv[2] if len(sys.argv) > 2 else ''

L = []
def say(s):
    L.append(str(s)); print(str(s))

def v(x):
    try:
        return '(%.1f, %.1f, %.1f)' % (x.x, x.y, x.z)
    except Exception:
        return str(x)

def gp(o, n, d='<none>'):
    try:
        return o.get_editor_property(n)
    except Exception as e:
        return '<%s %s>' % (type(e).__name__, n)

def allof(w, p):
    try:
        return list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_object(None, p)))
    except Exception:
        return []

DIRC = '/Game/Game/Blueprints/BP_OpeningDirector.BP_OpeningDirector_C'
PLYC = '/Game/Game/Blueprints/BP_Player.BP_Player_C'
DRVC = '/Game/Game/Blueprints/BP_CrashDriver.BP_CrashDriver_C'


def wallstate(d):
    """The wall collection: is it still one kinematic slab, or has it come apart?"""
    gc = gp(d, 'CineWallGC')
    if not isinstance(gc, unreal.Actor):
        return 'CineWallGC not wired (%s)' % gc
    o = gc.get_actor_bounds(False)
    comp = gc.get_component_by_class(unreal.GeometryCollectionComponent)
    ot = gp(comp, 'object_type') if comp else '<no comp>'
    hid = gc.is_hidden_ed() if False else gc.get_editor_property('hidden')
    return 'wall %s origin %s extent %s type %s hidden %s' % (
        gc.get_actor_label(), v(o[0]), v(o[1]), ot, hid)


def firestate(d):
    fa = gp(d, 'CineFireActor')
    fx = gp(d, 'CineFireFX')
    bits = []
    if isinstance(fa, unreal.Actor):
        bits.append('fireactor hidden %s' % gp(fa, 'hidden'))
    else:
        bits.append('CineFireActor not wired (%s)' % fa)
    if isinstance(fx, unreal.Object):
        # UNiagaraComponent exposes CustomTimeDilation through accessors, not as a readable
        # UPROPERTY: get_editor_property raises on every spelling of it. Try the methods too.
        got = False
        for cand in ('custom_time_dilation', 'CustomTimeDilation'):
            val = gp(fx, cand)
            if not str(val).startswith('<'):
                bits.append('fx dilation %s' % val); got = True
                break
        if not got:
            for meth in ('get_custom_time_dilation', 'getCustomTimeDilation'):
                try:
                    bits.append('fx dilation %s' % getattr(fx, meth)()); got = True
                    break
                except Exception:
                    pass
        if not got:
            try:
                bits.append('fx dilation(call) %s' % fx.call_method('GetCustomTimeDilation', args=()))
                got = True
            except Exception as e:
                bits.append('fx dilation unreadable (%s)' % type(e).__name__)
        for meth in ('is_active', 'is_paused'):
            try:
                bits.append('fx %s %s' % (meth, getattr(fx, meth)()))
            except Exception:
                pass
    else:
        bits.append('CineFireFX not wired (%s)' % fx)
    fl = gp(d, 'CineFireLight')
    if isinstance(fl, unreal.Actor):
        bits.append('firelight hidden %s' % gp(fl, 'hidden'))
    return ' | '.join(str(b) for b in bits)


def driverstate(w, d):
    drv = gp(d, 'CineDriverBP')
    if not isinstance(drv, unreal.Actor):
        drvs = allof(w, DRVC)
        drv = drvs[0] if drvs else None
    if drv is None:
        return 'no crash driver'
    mesh = drv.get_component_by_class(unreal.SkeletalMeshComponent)
    sim = None
    try:
        sim = mesh.is_simulating_physics()
    except Exception as e:
        sim = '<%s>' % type(e).__name__
    return 'driver at %s hidden %s ragdollive %s simulating %s meshworld %s' % (
        v(drv.get_actor_location()), gp(drv, 'hidden'), gp(drv, 'RagdollLive'), sim,
        v(mesh.get_world_location()) if mesh else '-')


def sample(w, d, tag):
    say('--- %s   t=%.3f' % (tag, gp(d, 'CineTime')))
    say('    running %s done %s  walldone %s firedone %s firelit %s' % (
        gp(d, 'CineRunning'), gp(d, 'CineDone'), gp(d, 'CineWallDone'),
        gp(d, 'CineFireDone'), gp(d, 'CineFireLit')))
    say('    ragdoll on %s done %s t=%s' % (gp(d, 'RagdollOn'), gp(d, 'RagdollDone'), gp(d, 'RagdollT')))
    say('    %s' % wallstate(d))
    say('    %s' % firestate(d))
    say('    %s' % driverstate(w, d))
    car = gp(d, 'CineRealCar')
    if isinstance(car, unreal.Actor):
        say('    realcar hidden %s' % gp(car, 'hidden'))
    say('    objective %s' % gp(d, 'ObjectiveState'))


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
        say('NO PIE WORLD - press Play first')
        raise SystemExit
    say('')
    say('=== %s   %s   world %s' % (MODE, time.strftime('%H:%M:%S'), w.get_name()))

    dirs = allof(w, DIRC)
    say('directors in world: %d' % len(dirs))
    if not dirs:
        say('no BP_OpeningDirector in the PIE world')
        raise SystemExit
    d = dirs[0]

    if MODE == 'state':
        sample(w, d, 'state')

    elif MODE == 'freeze':
        plys = allof(w, PLYC)
        if not plys:
            say('no player')
            raise SystemExit
        p = plys[0]
        # FreezeFrameActive is NOT instance-editable, so drive the REAL power instead of
        # writing the flag: grant it, start it, step the fire, end it, step again.
        say('before:     %s' % firestate(d))
        say('            firelit %s  HasFreezeFrame %s  FreezeFrameActive %s' % (
            gp(d, 'CineFireLit'), gp(p, 'HasFreezeFrame'), gp(p, 'FreezeFrameActive')))
        if gp(p, 'HasFreezeFrame') is not True:
            p.call_method('PlayerGrantFreezeFrame', args=())
            say('granted:    HasFreezeFrame %s' % gp(p, 'HasFreezeFrame'))
        p.call_method('FreezeFrameStart', args=())
        say('            FreezeFrameActive %s' % gp(p, 'FreezeFrameActive'))
        d.call_method('CineFireTimeStep', args=())
        say('freeze ON : %s' % firestate(d))
        p.call_method('PlayerFreezeFrameEnd', args=())
        say('            FreezeFrameActive %s' % gp(p, 'FreezeFrameActive'))
        d.call_method('CineFireTimeStep', args=())
        say('freeze OFF: %s' % firestate(d))

    elif MODE == 'open':
        DT = 0.1
        STEPS = 125
        say('wall at %s   fire at %s   impact %s   body %s   length %s' % (
            gp(d, 'CineWallTime'), gp(d, 'CineFireTime'), gp(d, 'CineImpactTime'),
            gp(d, 'CineBodyTime'), gp(d, 'CineLength')))
        d.call_method('CineSceneBeforeCrash', args=())
        say('after CineSceneBeforeCrash:')
        sample(w, d, 'pre-roll')
        d.call_method('CineBeginOpening', args=())
        say('after CineBeginOpening: running %s' % gp(d, 'CineRunning'))
        marks = {}
        for i in range(STEPS):
            d.call_method('CineDirectorStep', args=(DT,))
            t = gp(d, 'CineTime')
            for key, flag in (('wall', 'CineWallDone'), ('fire', 'CineFireDone'),
                              ('firelit', 'CineFireLit'), ('ragdoll', 'RagdollOn'),
                              ('ragdolldone', 'RagdollDone')):
                if key not in marks and gp(d, flag) is True:
                    marks[key] = t
                    say('    %-12s fired at t=%.3f   %s' % (key, t, wallstate(d) if key == 'wall' else ''))
            if 'car' not in marks:
                car = gp(d, 'CineRealCar')
                if isinstance(car, unreal.Actor) and gp(car, 'hidden') is False:
                    marks['car'] = t
                    say('    %-12s shown at t=%.3f' % ('realcar', t))
            if 'cinetime' in marks:
                break
            if gp(d, 'CineRunning') is False and t > 1.0:
                marks['cinetime'] = t
                say('    %-12s stopped at t=%.3f' % ('running', t))
        say('')
        say('TRIGGER TIMES: %s' % marks)
        sample(w, d, 'end of opening')

    else:
        say('unknown mode %r' % MODE)

except SystemExit:
    pass
except Exception as e:
    import traceback
    say('ERROR %r' % e)
    say(traceback.format_exc())

with open(os.path.join(OUT, 'b1z_pie.txt'), 'a') as fh:
    fh.write('\n'.join(L) + '\n')
print('b1z_pie %s done' % MODE)
