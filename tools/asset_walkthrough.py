"""Asset walkthrough: what in Lvl_JumpCut is still a placeholder, and what does the route look like?

Read-only. It never saves, never dirties on purpose, and quits the editor itself when it is done.
Run it with the editor CLOSED, from a shell (not from the editor's console):

    UnrealEditor.exe <repo>/JumpCut/JumpCut.uproject -ExecutePythonScript=<repo>/tools/asset_walkthrough.py
        -unattended -nosplash -nopause

Writes into JumpCut/Saved/walkthrough/ (gitignored):
    census.json      every placed actor: label, class, place, hidden, each mesh and its materials
    blueprints.json  for every Blueprint and widget under /Game/Game: what it references, by kind
    placeholders.txt the short list a person reads - engine shapes, grey materials, mannequins, silent Blueprints
    shot_NN_*.png    eye-height pictures along the route (cafe -> street -> boss lot -> exit run)

A maker or tester computer may run this: it opens the level and looks, nothing more.
"""
import json
import os

import unreal

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'walkthrough')
os.makedirs(OUT, exist_ok=True)
LEVEL = '/Game/Game/Maps/Lvl_JumpCut'

PLACEHOLDER_MESH = ('/Engine/BasicShapes/', '/Engine/EngineMeshes/', '/Game/LevelPrototyping/')
PLACEHOLDER_MAT = ('M_GreyWall', 'M_GreyFloor', 'M_PropRed', 'M_PropBlue', 'M_CheckGreen', 'M_GateColor',
                   'M_WarnFreeze', 'M_WarnPunch', 'M_Goon', 'M_Boss', 'BasicShapeMaterial', 'WorldGridMaterial',
                   'DefaultMaterial')
MANNEQUIN = ('/Game/Characters/Mannequins/', 'SKM_Manny', 'SKM_Quinn')

# (name, x, y, z, yaw, pitch) - eye height along the route in tools/c1_layout.py, plus a few high looks.
SHOTS = [
    ('cafe_from_door_looking_west', 520, 0, 170, 180, -5),
    ('cafe_crash_site', -100, -150, 170, 160, -8),
    ('cafe_counter', -150, 150, 170, -45, -8),
    ('cafe_looking_out_the_door', 0, 0, 170, 0, 0),
    ('street_start_looking_east', 800, 0, 170, 0, 0),
    ('street_start_looking_back', 1600, 0, 170, 180, 0),
    ('street_mid', 2800, -150, 170, 10, 0),
    ('street_mid_high', 3600, 0, 900, 0, -35),
    ('street_end_checkpoint', 5600, 0, 170, 0, 0),
    ('plaza_gate_entry', 6200, 0, 170, 0, 0),
    ('boss_lot_from_entry', 6750, 0, 170, 0, -3),
    ('boss_lot_centre_looking_north', 8120, -600, 170, 90, 0),
    ('boss_lot_centre_looking_south', 8120, 600, 170, -90, 0),
    ('boss_lot_high', 7000, -1300, 1100, 35, -32),
    ('boss_lot_exit_gate', 9100, 0, 170, 0, 0),
    ('exit_run', 9700, 0, 170, 0, 0),
    ('exit_run_end', 10300, 0, 170, 0, 0),
    ('whole_route_high', -1500, -2600, 2600, 25, -30),
]


def cls_name(obj):
    return obj.get_class().get_name() if obj else None


def path_of(obj):
    return obj.get_path_name() if obj else None


def census():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    rows = []
    for a in sub.get_all_level_actors():
        loc = a.get_actor_location()
        row = {'label': a.get_actor_label(), 'class': cls_name(a),
               'loc': [round(loc.x), round(loc.y), round(loc.z)],
               'hidden': bool(a.is_hidden_ed()) or bool(a.get_editor_property('hidden')),
               'meshes': []}
        for c in a.get_components_by_class(unreal.MeshComponent):
            mesh = None
            if isinstance(c, unreal.StaticMeshComponent):
                mesh = c.static_mesh
            elif isinstance(c, unreal.SkeletalMeshComponent):
                mesh = c.get_skeletal_mesh_asset()
            entry = {'comp': c.get_name(), 'kind': cls_name(c), 'mesh': path_of(mesh),
                     'visible': bool(c.is_visible()),
                     'mats': [path_of(m) for m in c.get_materials()]}
            if isinstance(c, unreal.SkeletalMeshComponent):
                ac = c.get_editor_property('anim_class')
                entry['anim_class'] = path_of(ac)
            row['meshes'].append(entry)
        rows.append(row)
    with open(os.path.join(OUT, 'census.json'), 'w') as f:
        json.dump(rows, f, indent=1)
    return rows


def blueprint_refs():
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    opts = unreal.AssetRegistryDependencyOptions(True, True, True, False, False)
    out = {}
    for ad in reg.get_assets_by_path('/Game/Game', recursive=True):
        kind = str(ad.asset_class_path.asset_name)
        if kind not in ('Blueprint', 'WidgetBlueprint', 'AnimBlueprint'):
            continue
        deps = reg.get_dependencies(ad.package_name, opts) or []
        by = {}
        for d in deps:
            d = str(d)
            if d.startswith('/Script/'):
                continue
            das = reg.get_assets_by_package_name(d)
            k = str(das[0].asset_class_path.asset_name) if das else '?'
            by.setdefault(k, []).append(d)
        out[str(ad.package_name)] = {'kind': kind, 'refs': by}
    with open(os.path.join(OUT, 'blueprints.json'), 'w') as f:
        json.dump(out, f, indent=1)
    return out


def placeholders(rows, bps):
    lines = []
    lines.append('== PLACED ACTORS still on placeholder geometry or materials (visible ones first) ==')
    flagged = []
    for r in rows:
        why = []
        for m in r['meshes']:
            mesh = m['mesh'] or ''
            if any(p in mesh for p in PLACEHOLDER_MESH):
                why.append('%s mesh=%s' % (m['comp'], mesh.split('.')[-1]))
            if any(p in mesh for p in MANNEQUIN):
                why.append('%s MANNEQUIN %s' % (m['comp'], mesh.split('.')[-1]))
            for mat in m['mats']:
                if mat and any(p in mat for p in PLACEHOLDER_MAT):
                    why.append('%s mat=%s' % (m['comp'], mat.split('.')[-1]))
        if why:
            flagged.append((r['hidden'], r['loc'][0], r, sorted(set(why))))
    flagged.sort(key=lambda t: (t[0], t[1]))
    for hidden, _, r, why in flagged:
        lines.append('%s %-34s %-26s x=%-6d %s' % ('hidden ' if hidden else 'VISIBLE', r['label'], r['class'],
                                                    r['loc'][0], '; '.join(why)))
    lines.append('')
    lines.append('== BLUEPRINTS / WIDGETS: what each one references ==')
    for name in sorted(bps):
        refs = bps[name]['refs']
        sounds = refs.get('SoundWave', []) + refs.get('SoundCue', [])
        fx = refs.get('NiagaraSystem', []) + refs.get('ParticleSystem', [])
        tex = refs.get('Texture2D', [])
        meshes = refs.get('StaticMesh', []) + refs.get('SkeletalMesh', [])
        anims = refs.get('AnimMontage', []) + refs.get('AnimSequence', [])
        lines.append('%-46s sounds=%d fx=%d textures=%d meshes=%d anims=%d' % (
            name.split('/')[-1], len(sounds), len(fx), len(tex), len(meshes), len(anims)))
        for m in meshes:
            tag = '  <-- placeholder' if any(p in m for p in PLACEHOLDER_MESH + MANNEQUIN) else ''
            lines.append('      mesh  %s%s' % (m, tag))
        for s in sounds:
            lines.append('      sound %s' % s)
    with open(os.path.join(OUT, 'placeholders.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


class Walker(object):
    """Takes the shots a few editor ticks apart, so each camera move has rendered before its picture."""
    SETTLE = 45

    def __init__(self):
        self.i = -1
        self.wait = 240  # let the level and its shaders settle first
        self.phase = 'move'
        self.handle = unreal.register_slate_post_tick_callback(self.tick)

    def tick(self, _dt):
        try:
            self.wait -= 1
            if self.wait > 0:
                return
            if self.phase == 'move':
                self.i += 1
                if self.i >= len(SHOTS):
                    self.finish()
                    return
                name, x, y, z, yaw, pitch = SHOTS[self.i]
                unreal.EditorLevelLibrary.set_level_viewport_camera_info(
                    unreal.Vector(x, y, z), unreal.Rotator(0.0, pitch, yaw))
                self.phase, self.wait = 'shoot', self.SETTLE
            else:
                name = SHOTS[self.i][0]
                path = os.path.join(OUT, 'shot_%02d_%s.png' % (self.i, name))
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, path)
                self.phase, self.wait = 'move', self.SETTLE
        except Exception as e:  # never leave the editor hanging on a bad shot
            unreal.log_error('WALKTHROUGH shot failed: %s' % e)
            self.finish()

    def finish(self):
        unreal.unregister_slate_post_tick_callback(self.handle)
        with open(os.path.join(OUT, 'DONE.txt'), 'w') as f:
            f.write('shots attempted: %d\n' % max(0, self.i))
        unreal.SystemLibrary.quit_editor()


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if not world or LEVEL not in world.get_path_name():
        unreal.EditorLoadingAndSavingUtils.load_map(LEVEL)
    try:
        rows = census()
        bps = blueprint_refs()
        placeholders(rows, bps)
        unreal.log('WALKTHROUGH census: %d actors, %d blueprints' % (len(rows), len(bps)))
    except Exception as e:
        import traceback
        with open(os.path.join(OUT, 'ERROR.txt'), 'w') as f:
            f.write(traceback.format_exc())
        unreal.log_error('WALKTHROUGH census failed: %s' % e)
    global _walker
    _walker = Walker()


main()
