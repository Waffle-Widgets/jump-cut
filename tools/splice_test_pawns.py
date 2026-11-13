import unreal
OUT = r"C:\Users\thecl\code\jump-cut\JumpCut\Saved\jcpy\splice_test_e.txt"
ws = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
gm = unreal.GameplayStatics.get_game_mode(ws)
player = None
goons = []
boss = None
for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.Actor):
    cn = a.get_class().get_name()
    if cn.startswith('BP_Player'):
        player = a
    if cn == 'BP_Goon_C':
        goons.append(a)
    if 'BossFreeze' in cn:
        boss = a

rows = []
st = {'t': 0.0, 'phase': 0, 'done': False}
mem = {}

def rec(s):
    rows.append(s); unreal.log("[SPLICE-E] " + s)

def loc():
    v = player.get_actor_location(); return (v.x, v.y, v.z)

def d2(a, b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5

def put(x, y, z, yaw):
    player.set_actor_location(unreal.Vector(x, y, z), False, True)
    r = unreal.Rotator(0.0, 0.0, yaw)
    player.set_actor_rotation(r, False)
    pc = unreal.GameplayStatics.get_player_controller(ws, 0)
    if pc: pc.set_control_rotation(r)

def target_info(a):
    cap = a.get_component_by_class(unreal.CapsuleComponent)
    r = cap.get_scaled_capsule_radius() if cap else -1
    h = cap.get_scaled_capsule_half_height() if cap else -1
    return "%s at %s capsule r=%.1f hh=%.1f" % (a.get_actor_label(), a.get_actor_location(), r, h)

def run_against(a, tag):
    g = a.get_actor_location()
    mem['T'] = (g.x, g.y, g.z)
    rec("%s -> %s" % (tag, target_info(a)))
    put(g.x - 250.0, g.y, g.z + 40.0, 0.0)

def measure(a, tag):
    moved = d2(mem['E0'], loc())
    g2 = a.get_actor_location()
    rec("%s RESULT: player moved %.1f cm  (600 = passed THROUGH, ~205 = he blocked it)" % (tag, moved))
    rec("%s        : target moved %.1f cm (expect 0)" % (tag, d2((g2.x, g2.y, 0), (mem['T'][0], mem['T'][1], 0))))

def tick(dt):
    if st['done']: return
    st['t'] += dt; t = st['t']; p = st['phase']
    try:
        if p == 0 and t >= 0.3:
            st['phase'] = 1
            gm.call_method('JumpCutStartPlay')
            player.call_method('PlayerGrantSplice')
            rec("start pressed; HasSplice=%s; real BP_Goon_C found=%d; boss=%s" % (
                player.get_editor_property('HasSplice'), len(goons),
                boss.get_actor_label() if boss else None))
        elif p == 1 and t >= 0.8:
            st['phase'] = 2
            if not goons:
                rec("no real goon found"); st['phase'] = 10
            else:
                run_against(goons[0], "GOON")
        elif p == 2 and t >= 1.4:
            st['phase'] = 3
            mem['E0'] = loc()
            rec("GOON: blinking from %s facing (%.2f,%.2f) cd=%.2f" % (
                tuple(round(v,1) for v in mem['E0']),
                player.get_actor_forward_vector().x, player.get_actor_forward_vector().y,
                player.get_editor_property('SpliceCooldownLeft')))
            player.call_method('SpliceStart')
        elif p == 3 and t >= 1.8:
            st['phase'] = 4
            measure(goons[0], "GOON")
        elif p == 4 and t >= 3.4:
            st['phase'] = 5
            if boss is None:
                rec("no boss found"); st['phase'] = 10
            else:
                run_against(boss, "BOSS")
        elif p == 5 and t >= 4.0:
            st['phase'] = 6
            mem['E0'] = loc()
            rec("BOSS: blinking from %s cd=%.2f" % (
                tuple(round(v,1) for v in mem['E0']),
                player.get_editor_property('SpliceCooldownLeft')))
            player.call_method('SpliceStart')
        elif p == 6 and t >= 4.4:
            st['phase'] = 10
            measure(boss, "BOSS")
        elif p == 10 and t >= 4.9:
            st['done'] = True
            open(OUT, 'w', encoding='utf-8').write("\n".join(rows))
            unreal.log("[SPLICE-E] ==== written ====")
    except Exception as e:
        rec("EXCEPTION phase %d: %r" % (p, e))
        open(OUT, 'w', encoding='utf-8').write("\n".join(rows))
        st['done'] = True

unreal.register_slate_post_tick_callback(tick)
unreal.log("[SPLICE-E] registered")
