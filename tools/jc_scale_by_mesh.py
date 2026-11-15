"""Scale every placed actor wearing one mesh, keeping its feet where they are (Sun Nov 15, GameStation).

    py tools/jc_scale_by_mesh.py <mesh name> <scale> [save]

The Tripo gas bottles came back as two bottles in a wide rack: sized to the kit's 114 cm height they are 155 cm
wide against the kit's 94, and overlap the vending machine next to them. Scaling the placed actors is quicker than
a re-bake and a forced re-import, and it is undone by running this again with 1.0.
"""
import os, sys
import unreal
name, sc = sys.argv[1], float(sys.argv[2])
out = []; pk = []
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in sub.get_all_level_actors():
    if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name() == name:
        a.set_actor_transform(unreal.Transform(location=a.get_actor_location(), rotation=a.get_actor_rotation(), scale=unreal.Vector(sc, sc, sc)), False, True)
        o, e = a.get_actor_bounds(False)
        out.append('%s scale %.2f size now %.0f %.0f %.0f at %.0f %.0f  file JumpCut/Content/%s.uasset' % (a.get_actor_label(), sc, e.x * 2, e.y * 2, e.z * 2, a.get_actor_location().x, a.get_actor_location().y, a.get_outermost().get_name()[len('/Game/'):]))
        pk.append(a.get_outermost())
if len(sys.argv) > 3 and sys.argv[3] == 'save':
    out.append('SAVED ok=%s' % unreal.EditorLoadingAndSavingUtils.save_packages(pk, False))
open(os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'scale_by_mesh.txt'), 'w').write('\n'.join(out) + '\n')
