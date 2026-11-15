"""The cafe's west wall, measured from the MESH rather than inferred from the Blender script.

Traces can't find the hole: C1_Cafe_WallW, a grey-box collider from the Thursday build, still stands
at x = -600 across the whole wall. So this reads SM_CafeShell's own triangles and reports, for the
brick on the west wall plane, which y and z are solid and which are open - the exact opening an
intact wall panel has to fill.

    py <repo>/tools/b1z_wallgeo.py
Writes Saved/jcpy/b1z_wallgeo.json. Read only.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
res = {}
try:
    sm = unreal.load_asset('/Game/Game/Imported/City/SM_CafeShell')
    PML = unreal.ProceduralMeshLibrary
    slots = [str(s.material_slot_name) for s in sm.get_editor_property('static_materials')]
    res['slots'] = slots
    secs = {}
    for si in range(len(slots)):
        try:
            v, t, n, uv, tg = PML.get_section_from_static_mesh(sm, 0, si)
        except Exception as e:
            secs[slots[si]] = 'ERR %r' % e
            continue
        xs = [p.x for p in v]
        secs[slots[si]] = {'verts': len(v), 'tris': len(t) // 3,
                           'x': [round(min(xs), 2), round(max(xs), 2)]}
        # the west wall plane: everything at x <= -600
        west = [p for p in v if p.x <= -600.0]
        if west:
            ys = sorted(set(round(p.y, 1) for p in west))
            zs = sorted(set(round(p.z, 1) for p in west))
            secs[slots[si]]['west_verts'] = len(west)
            secs[slots[si]]['west_y'] = ys[:80]
            secs[slots[si]]['west_z'] = zs[:80]
            # a solidity map of the wall plane: for each 10 cm y column, the lowest z of any
            # triangle whose three verts are all on the wall plane
            cols = {}
            for i in range(0, len(t), 3):
                a, b, c = v[t[i]], v[t[i + 1]], v[t[i + 2]]
                if max(a.x, b.x, c.x) > -610.0:
                    continue
                y0 = min(a.y, b.y, c.y); y1 = max(a.y, b.y, c.y)
                z0 = min(a.z, b.z, c.z); z1 = max(a.z, b.z, c.z)
                k0 = int(round(y0 / 10.0)); k1 = int(round(y1 / 10.0))
                for k in range(k0, k1 + 1):
                    cur = cols.get(k)
                    cols[k] = (min(cur[0], z0), max(cur[1], z1)) if cur else (z0, z1)
            secs[slots[si]]['cols'] = {str(k * 10): [round(a, 1), round(b, 1)] for k, b_ in [(k, 0) for k in sorted(cols)] for a, b in [cols[k]]}
    res['sections'] = secs

    # every grey-box cafe actor that is still in the level
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    greys = {}
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith('C1_Cafe_') or lab.startswith('B1_Cine_') or lab.startswith('B1_Cafe_'):
            smc = a.get_component_by_class(unreal.StaticMeshComponent)
            m = smc.static_mesh if smc else None
            greys[lab] = {'class': a.get_class().get_name(),
                          'mesh': m.get_name() if m else None,
                          'hidden': bool(a.get_editor_property('hidden')),
                          'loc': [round(a.get_actor_location().x, 1), round(a.get_actor_location().y, 1),
                                  round(a.get_actor_location().z, 1)],
                          'scale': [round(a.get_actor_scale3d().x, 3), round(a.get_actor_scale3d().y, 3),
                                    round(a.get_actor_scale3d().z, 3)],
                          'collides': bool(a.get_actor_enable_collision())}
    res['cafe_actors'] = greys
except Exception as e:
    res['error'] = repr(e)
    res['tb'] = traceback.format_exc()
with open(os.path.join(OUT, 'b1z_wallgeo.json'), 'w') as fh:
    json.dump(res, fh, indent=1, default=str)
print('b1z_wallgeo done')
