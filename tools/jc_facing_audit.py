"""Finds placed props that face a wall instead of the open side, and lamps whose arm points into a building.

    py tools/jc_facing_audit.py           report only -> Saved/jcpy/facing_audit.txt
    py tools/jc_facing_audit.py paths     the files of the actors it would turn -> Saved/jcpy/facing_lock.txt
    add `lamps` to `paths` or `fix` to act on the lamps only (the box props it flags need a look first:
    a dumpster with another prop in front of it is flagged and is not wrong)
    py tools/jc_facing_audit.py fix       turn the flagged ones 180 in place (bounds kept where they were) and save

WHY (Sun Nov 15, GameStation). Sixty-odd generated models went into the level in one afternoon, each sized to an
old kit piece's box, and "which way is the front" turned out to differ per piece (the register and the meter boxes
both came in backwards). Looking at each is not possible in the time. A prop with a front has open ground in front
of it and usually a wall behind: so for each one, trace 2.5 m forward and 2.5 m back at chest height and compare.
FRONT is where the model's face is in Unreal's axes: +Y for everything baked the normal way, -Y for the two I baked
turned round. A lamp is judged by its arm: the side its bounding box overhangs.
"""
import os, sys, math
import unreal
MODE = sys.argv[1] if len(sys.argv) > 1 else 'report'
FRONT = {'SM_VendingMachineM': 1, 'SM_BenchM': 1, 'SM_ShopDisplayM': 1, 'SM_ACUnitM': 1, 'SM_MeterBoxM': -1, 'SM_DuctRunM': -1,
         'SM_CafeShelfM': 1, 'SM_CafeBanquetteM': 1, 'SM_CafeChalkboardM': 1, 'SM_CafeWallArtM': 1, 'SM_CafeClockM': 1,
         'SM_PlanterM': 1, 'SM_PotRowM': 1, 'SM_DumpsterM': 1, 'SM_CafePastryCaseM': 1, 'SM_CafeEspressoM': 1}
W = unreal.UnrealEditorSubsystem().get_editor_world()
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = []; flagged = []
def reach(a, p, d, dist=250.0):
    """How far a ray from p along d gets before it hits something that is not this actor."""
    hit = unreal.SystemLibrary.line_trace_single(W, p, unreal.Vector(p.x + d[0] * dist, p.y + d[1] * dist, p.z), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [a], unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        return dist, None
    h = hit.to_dict()
    if not h.get('blocking_hit'):
        return dist, None
    return h.get('distance', dist), (h.get('hit_actor').get_actor_label() if h.get('hit_actor') else '?')
for a in sub.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor) or not a.static_mesh_component.static_mesh or a.get_editor_property('hidden'):
        continue
    n = a.static_mesh_component.static_mesh.get_name()
    l = a.get_actor_location(); yaw = math.radians(a.get_actor_rotation().yaw)
    o, e = a.get_actor_bounds(False)
    if n == 'SM_StreetLampM':
        ax, ay = o.x - l.x, o.y - l.y
        L = math.hypot(ax, ay) or 1.0
        d = (ax / L, ay / L)
        p = unreal.Vector(l.x, l.y, l.z + 300.0)
        f, fa = reach(a, p, d, 300.0); b, ba = reach(a, p, (-d[0], -d[1]), 300.0)
        bad = f < b - 60.0                      # the arm is on the side with LESS room: it points at the wall, not the road
        out.append('%s LAMP %-26s arm toward (%.1f, %.1f): open %.0f cm that way (%s), %.0f cm the other way (%s)' % ('FLAG' if bad else ' ok ', a.get_actor_label(), d[0], d[1], f, fa, b, ba))
        if bad: flagged.append(a)
    elif n in FRONT:
        s = FRONT[n]
        d = (-math.sin(yaw) * s, math.cos(yaw) * s)
        p = unreal.Vector(o.x, o.y, max(o.z, l.z + 40.0))
        bb = a.static_mesh_component.static_mesh.get_bounding_box()
        hd = (bb.max.y - bb.min.y) * 0.5 * a.get_actor_scale3d().y + 3.0
        r = 0.0
        # Start each ray just OUTSIDE the prop's own front and back faces. Many of these are set into a wall (the kit
        # duct is 42 cm deep and 35 of it is inside the building), and a ray from the middle starts inside the wall.
        f, fa = reach(a, unreal.Vector(p.x + d[0] * hd, p.y + d[1] * hd, p.z), d, 200.0)
        b, ba = reach(a, unreal.Vector(p.x - d[0] * hd, p.y - d[1] * hd, p.z), (-d[0], -d[1]), 200.0)
        bad = f < b - 60.0 and f < 60.0
        out.append('%s %-20s %-30s front open %.0f cm (%s), back open %.0f cm (%s)' % ('FLAG' if bad else ' ok ', n[3:], a.get_actor_label(), f, fa, b, ba))
        if bad: flagged.append(a)
if len(sys.argv) > 2 and sys.argv[2] == 'lamps':          # `paths lamps` / `fix lamps`: act on the lamps only
    flagged = [a for a in flagged if a.static_mesh_component.static_mesh.get_name() == 'SM_StreetLampM']
out.sort()
out.append('%d flagged of %d checked' % (len(flagged), len(out)))
if MODE == 'paths':
    open(os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'facing_lock.txt'), 'w').write('\n'.join('JumpCut/Content/%s.uasset' % a.get_outermost().get_name()[len('/Game/'):] for a in flagged) + '\n')
if MODE == 'fix':
    pk = []
    for a in flagged:
        o0, e0 = a.get_actor_bounds(False)
        r = a.get_actor_rotation(); l = a.get_actor_location(); s = a.get_actor_scale3d()
        r2 = unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=(r.yaw + 180.0) % 360.0)
        a.set_actor_transform(unreal.Transform(location=l, rotation=r2, scale=s), False, True)
        o1, e1 = a.get_actor_bounds(False)
        if a.static_mesh_component.static_mesh.get_name() != 'SM_StreetLampM':     # a lamp turns about its column; a box prop keeps its box
            a.set_actor_transform(unreal.Transform(location=unreal.Vector(l.x + o0.x - o1.x, l.y + o0.y - o1.y, l.z), rotation=r2, scale=s), False, True)
        pk.append(a.get_outermost())
    out.append('turned %d; SAVED ok=%s' % (len(pk), unreal.EditorLoadingAndSavingUtils.save_packages(pk, False) if pk else 'nothing to save'))
open(os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'facing_audit.txt'), 'w').write('\n'.join(out) + '\n')
