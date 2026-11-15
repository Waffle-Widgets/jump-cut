"""Turn every placed actor wearing one mesh to face the other way, WITHOUT moving the box it occupies.

    py tools/jc_flip_by_mesh.py paths <mesh> [<mesh> ...]    files to lock -> Saved/jcpy/flip_lock.txt
    py tools/jc_flip_by_mesh.py apply <mesh> [<mesh> ...]    turn 180 about Z, slide back into the old bounds, save

WHY (Sun Nov 15, GameStation). The Tripo meter box and duct were baked with PROP_YAW=180 because I read the kit
box (Unreal y -22.5 .. 0) as "sticks out toward -Y, so that is the front". It is the other way round: the kit's
origin is on the FRONT plane and the body goes back into the wall, so the front is Unreal +Y, Blender -Y, exactly
as meshy_prop_bake.py says. Both props were showing their blank backs. A re-bake needs a forced re-import over
assets that are already committed; turning the 10 actors is level data only. The box is not centred on its origin,
so a plain 180 would push it 22 cm out of the wall: the actor is slid until its bounds are where they were.
"""
import os, sys
import unreal
mode, names = sys.argv[1], set(sys.argv[2:])
out = []; pk = []
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in sub.get_all_level_actors():
    if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name() in names:
        if mode == 'paths':
            out.append('JumpCut/Content/%s.uasset' % a.get_outermost().get_name()[len('/Game/'):]); continue
        o0, e0 = a.get_actor_bounds(False)
        r = a.get_actor_rotation(); l = a.get_actor_location(); s = a.get_actor_scale3d()
        r2 = unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=(r.yaw + 180.0) % 360.0)
        a.set_actor_transform(unreal.Transform(location=l, rotation=r2, scale=s), False, True)
        o1, e1 = a.get_actor_bounds(False)
        l2 = unreal.Vector(l.x + o0.x - o1.x, l.y + o0.y - o1.y, l.z)
        a.set_actor_transform(unreal.Transform(location=l2, rotation=r2, scale=s), False, True)
        o2, e2 = a.get_actor_bounds(False)
        out.append('%s yaw %.0f -> %.0f moved %.1f %.1f; bounds centre off by %.2f cm' % (a.get_actor_label(), r.yaw, r2.yaw, l2.x - l.x, l2.y - l.y, ((o2.x - o0.x) ** 2 + (o2.y - o0.y) ** 2) ** 0.5))
        pk.append(a.get_outermost())
if mode == 'apply':
    out.append('SAVED ok=%s' % unreal.EditorLoadingAndSavingUtils.save_packages(pk, False))
open(os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'flip_lock.txt' if mode == 'paths' else 'flip.txt'), 'w').write('\n'.join(out) + '\n')
