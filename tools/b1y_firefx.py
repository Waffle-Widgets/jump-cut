"""Feedback item 2: the car's fire becomes real Niagara particles instead of an orange cone.

NS_CarFire (three sprite emitters - Flames, Smoke, Embers - on M_FlameParticle3D) is added to the
EXISTING B1_Cafe_Fire actor as a NiagaraComponent, rather than as a new actor. That is deliberate:
BP_Coworker already owns that actor (CoworkerLightFire reveals it with SetActorHiddenInGame, and
CoworkerFireStep rewrites its SCALE every tick to make the cone lick), so riding on it means the
fire lights at exactly the right moment with no Blueprint change at all.

Two details make that safe:
  * the Niagara component is set ABSOLUTE location/rotation/scale, so the coworker's per-tick
    (2.9, 2.9, 2.1 +/- wobble) scaling cannot touch the particles;
  * the cone's own static mesh component is set invisible, which SetActorHiddenInGame(false) does
    NOT undo (hidden-in-game and component visibility are separate flags), so the cone never shows
    again while the particles do.

    py <repo>/tools/b1y_firefx.py          report
    py <repo>/tools/b1y_firefx.py apply    build it, save the actor package, read everything back
Writes Saved/jcpy/b1y_firefx.json.
"""
import unreal, os, sys, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
MODE = sys.argv[1] if len(sys.argv) > 1 else 'report'
NS = '/Game/Game/FX/NS_CarFire'
LABEL = 'B1_Cafe_Fire'
FIRE_AT = unreal.Vector(-500.0, 0.0, 95.0)      # the bonnet of the wreck at (-520, 0, 0)
res = {'mode': MODE}

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    assert ues.get_game_world() is None, 'PIE is running - stop it first'
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = None
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == LABEL:
            actor = a
            break
    assert actor is not None, 'no %s in the level' % LABEL
    res['actor'] = {'class': actor.get_class().get_name(),
                    'path': actor.get_path_name(),
                    'loc': [round(v, 1) for v in actor.get_actor_location().to_tuple()],
                    'scale': [round(v, 2) for v in actor.get_actor_scale3d().to_tuple()],
                    'hidden_in_game': bool(actor.get_editor_property('hidden')),
                    'pkg': actor.get_outermost().get_name()}

    def niagara_comps():
        return [c for c in actor.get_components_by_class(unreal.NiagaraComponent)]

    def describe():
        rows = []
        for c in actor.get_components_by_class(unreal.SceneComponent):
            d = {'name': c.get_name(), 'class': c.get_class().get_name(),
                 'visible': c.is_visible()}
            try:
                d['world'] = [round(v, 1) for v in c.get_world_location().to_tuple()]
            except Exception:
                pass
            for f in ('absolute_location', 'absolute_rotation', 'absolute_scale'):
                try:
                    d[f] = bool(c.get_editor_property(f))
                except Exception:
                    pass
            if isinstance(c, unreal.NiagaraComponent):
                asset = c.get_editor_property('asset')
                d['asset'] = asset.get_path_name() if asset else None
                d['auto_activate'] = bool(c.get_editor_property('auto_activate'))
            rows.append(d)
        return rows

    res['components_before'] = describe()

    if MODE == 'apply':
        ns = unreal.load_asset(NS)
        assert ns is not None, 'missing ' + NS
        actor.modify()
        comps = niagara_comps()
        if comps:
            comp = comps[0]
            res['reused_existing_component'] = comp.get_name()
        else:
            comp = actor.add_component_by_class(unreal.NiagaraComponent, False, unreal.Transform(), False)
            assert comp is not None, 'add_component_by_class returned None'
            res['added_component'] = comp.get_name()
        comp.set_editor_property('asset', ns)
        comp.set_editor_property('auto_activate', True)
        # the coworker rewrites this actor's SCALE every tick; absolute transform keeps the
        # particles out of it entirely
        for f in ('absolute_location', 'absolute_rotation', 'absolute_scale'):
            comp.set_editor_property(f, True)
        comp.set_world_location(FIRE_AT, False, False)
        comp.set_world_scale3d(unreal.Vector(1.0, 1.0, 1.0))
        comp.set_visibility(True, False)
        # the cone stops being drawn, for good. SetActorHiddenInGame(false) does not revive it.
        smc = actor.get_component_by_class(unreal.StaticMeshComponent)
        if smc:
            smc.set_visibility(False, False)
            res['cone_visible_now'] = smc.is_visible()
        # it must still start hidden: BP_Coworker is what reveals it
        actor.set_actor_hidden_in_game(True)
        res['hidden_in_game_now'] = bool(actor.get_editor_property('hidden'))
        pkg = actor.get_outermost()
        res['saved'] = bool(unreal.EditorLoadingAndSavingUtils.save_packages([pkg], False))
        res['package'] = pkg.get_name()

    res['components_after'] = describe()
except Exception:
    res['error'] = traceback.format_exc()

with open(os.path.join(OUT, 'b1y_firefx.json'), 'w') as f:
    json.dump(res, f, indent=1, default=str)
print('B1Y_FIREFX_%s saved=%s err=%s' % (MODE.upper(), res.get('saved'), 'error' in res))
