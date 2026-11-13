import unreal
OUT = r"C:\Users\thecl\code\jump-cut\JumpCut\Saved\jcpy\splice_test.txt"

ws = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
player = None
goon = None
gm = unreal.GameplayStatics.get_game_mode(ws)
for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.Actor):
    cn = a.get_class().get_name()
    if cn.startswith('BP_Player'):
        player = a
    if cn.startswith('BP_Goon') and goon is None:
        goon = a

rows = []
st = {'t': 0.0, 'phase': 0, 'done': False}
mem = {}

def rec(s):
    rows.append(s)
    unreal.log("[SPLICE] " + s)

def loc():
    v = player.get_actor_location()
    return (v.x, v.y, v.z)

def dist(a, b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5

def face(yaw):
    # unreal.Rotator(roll, pitch, yaw) -- yaw is the THIRD argument
    r = unreal.Rotator(0.0, 0.0, yaw)
    player.set_actor_rotation(r, False)
    pc = unreal.GameplayStatics.get_player_controller(ws, 0)
    if pc:
        pc.set_control_rotation(r)

def put(x, y, z, yaw):
    player.set_actor_location(unreal.Vector(x, y, z), False, True)
    face(yaw)

def splice(tag):
    """Call SpliceStart and report the state that governs it."""
    f = player.get_actor_forward_vector()
    rec("%s: at %s facing (%.2f,%.2f)  CanAct=%s  cd=%.2f" % (
        tag, tuple(round(v, 1) for v in loc()), f.x, f.y,
        player.call_method('PlayerCanAct'),
        player.get_editor_property('SpliceCooldownLeft')))
    player.call_method('SpliceStart')

def tick(dt):
    if st['done']:
        return
    st['t'] += dt
    t = st['t']
    p = st['phase']
    try:
        if p == 0 and t >= 0.3:
            st['phase'] = 1
            # press start: this is what the title screen does
            gm.call_method('JumpCutStartPlay')
            rec("JumpCutStartPlay called; InputLocked=%s MoveLocked=%s HasSplice=%s" % (
                player.get_editor_property('InputLocked'),
                player.get_editor_property('MoveLocked'),
                player.get_editor_property('HasSplice')))

        elif p == 1 and t >= 0.8:
            st['phase'] = 2
            put(7000.0, 1200.0, 130.0, 0.0)

        elif p == 2 and t >= 1.3:
            st['phase'] = 3
            mem['A0'] = loc()
            splice("TEST A (no power yet)")

        elif p == 3 and t >= 1.7:
            st['phase'] = 4
            rec("TEST A result: moved %.1f cm   EXPECT 0 (HasSplice was %s)" % (
                dist(mem['A0'], loc()), player.get_editor_property('HasSplice')))
            player.call_method('PlayerGrantSplice')
            rec("PlayerGrantSplice -> HasSplice=%s" % player.get_editor_property('HasSplice'))

        elif p == 4 and t >= 2.1:
            st['phase'] = 5
            put(7000.0, 1200.0, 130.0, 0.0)

        elif p == 5 and t >= 2.6:
            st['phase'] = 6
            mem['B0'] = loc()
            splice("TEST B (open plaza, facing +X)")

        elif p == 6 and t >= 3.0:
            st['phase'] = 7
            mem['B1'] = loc()
            rec("TEST B result: moved %.1f cm to %s   EXPECT ~600" % (
                dist(mem['B0'], mem['B1']), tuple(round(v, 1) for v in mem['B1'])))
            splice("TEST C (immediate second blink)")

        elif p == 7 and t >= 3.4:
            st['phase'] = 8
            rec("TEST C result: moved %.1f cm since B   EXPECT 0 (on cooldown)" % dist(mem['B1'], loc()))

        elif p == 8 and t >= 5.2:
            st['phase'] = 9
            rec("cooldown has now run down to %.2f" % player.get_editor_property('SpliceCooldownLeft'))
            put(3000.0, 0.0, 130.0, 90.0)

        elif p == 9 and t >= 5.8:
            st['phase'] = 10
            mem['W0'] = loc()
            splice("TEST D (street wall face at y=500, i.e. 500 cm away, facing +Y)")

        elif p == 10 and t >= 6.2:
            st['phase'] = 11
            w1 = loc()
            rec("TEST D result: moved %.1f cm, ended y=%.1f   EXPECT ~455 (stopped short of the wall), NOT 600" % (
                dist(mem['W0'], w1), w1[1]))

        elif p == 11 and t >= 7.4:
            st['phase'] = 12
            if goon is None:
                rec("TEST E SKIPPED: no BP_Goon in the level")
                st['phase'] = 14
            else:
                g = goon.get_actor_location()
                mem['G'] = (g.x, g.y, g.z)
                try:
                    mem['gh'] = goon.call_method('EnemyGetHealthNow')
                except Exception:
                    mem['gh'] = 'n/a'
                put(g.x - 250.0, g.y, g.z + 40.0, 0.0)
                rec("TEST E: goon '%s' at (%.1f,%.1f,%.1f) health=%s; player put 250 cm behind him on the +X line" % (
                    goon.get_actor_label(), g.x, g.y, g.z, mem['gh']))

        elif p == 12 and t >= 8.0:
            st['phase'] = 13
            mem['E0'] = loc()
            splice("TEST E (a goon standing 250 cm directly in front)")

        elif p == 13 and t >= 8.4:
            st['phase'] = 14
            d = dist(mem['E0'], loc())
            rec("TEST E result: moved %.1f cm   EXPECT ~600 (passed THROUGH him); ~205 would mean he blocked it" % d)
            g2 = goon.get_actor_location()
            rec("TEST E: goon moved %.1f cm (expect ~0 - a blink must not shove him)" % (
                ((g2.x - mem['G'][0])**2 + (g2.y - mem['G'][1])**2) ** 0.5))

        elif p == 14 and t >= 8.9:
            st['done'] = True
            open(OUT, 'w', encoding='utf-8').write("\n".join(rows))
            unreal.log("[SPLICE] ==== written ====")
    except Exception as e:
        rec("EXCEPTION in phase %d: %r" % (p, e))
        open(OUT, 'w', encoding='utf-8').write("\n".join(rows))
        st['done'] = True

unreal.register_slate_post_tick_callback(tick)
unreal.log("[SPLICE] harness registered; player=%s goon=%s gm=%s" % (player, goon, gm))
