"""One coffee sign at the shop, and the register turned to face the barista (Sun Nov 15, GameStation).

    py tools/jc_shop_fix.py paths    writes the actor files to lock to Saved/jcpy/shop_fix_lock.txt
    py tools/jc_shop_fix.py apply    City_CafeMenuBoard wears SM_AFrameSignM; City_Cafe_01_CafeRegister turns 180

The kit's SM_CafeMenuBoard in front of the cafe draws as a brown smear through the cel look ("the graybox in
front of the shop"). M Station's coffee A-frame belongs there and nowhere else: run
`unreal_street_models.py revert AFrameSignM` for the five on the street FIRST - that revert matches by mesh, so run
after `apply` it takes the shop's sign back off as well (it did). The Meshy register's front is the
opposite way round from the kit's, so the yaw that faced the kit register at the barista faced this one at the wall.
"""
import os, sys
import unreal
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy')
lines = []
def say(s):
    lines.append(s); unreal.log('[shop-fix] ' + s)
mode = sys.argv[1] if len(sys.argv) > 1 else 'paths'
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
A = {a.get_actor_label(): a for a in sub.get_all_level_actors()}
want = ['City_CafeMenuBoard', 'City_Cafe_01_CafeRegister'] + [l for l in A if l.endswith('_AFrameSign')]
def fname(a):
    return 'JumpCut/Content/' + a.get_outermost().get_name()[len('/Game/'):] + '.uasset'
if mode == 'paths':
    open(os.path.join(OUT, 'shop_fix_lock.txt'), 'w').write('\n'.join(fname(A[l]) for l in want) + '\n')
    say('%d files listed' % len(want))
else:
    def touch(a, yaw=None):
        loc, rot, sc = a.get_actor_location(), a.get_actor_rotation(), a.get_actor_scale3d()
        if yaw is not None:
            rot = unreal.Rotator(roll=rot.roll, pitch=rot.pitch, yaw=yaw)
        a.set_actor_transform(unreal.Transform(location=loc, rotation=rot, scale=sc), False, True)
    b = A['City_CafeMenuBoard']; c = b.static_mesh_component
    sm = unreal.EditorAssetLibrary.load_asset('/Game/Game/Imported/Street/AFrameSignM/SM_AFrameSignM') or unreal.EditorAssetLibrary.load_asset('/Game/Game/Imported/Street/SM_AFrameSignM')
    if sm is None:
        say('REFUSING: SM_AFrameSignM not found')
    else:
        c.set_static_mesh(sm); c.set_editor_property('override_materials', [])
        touch(b)
        say('City_CafeMenuBoard mesh %s materials %s' % (c.static_mesh.get_name(), [m.get_name() if m else None for m in c.get_materials()]))
        r = A['City_Cafe_01_CafeRegister']
        y = r.get_actor_rotation().yaw
        touch(r, 180.0)        # absolute, so a second run does not turn it back
        say('register yaw %.0f -> %.0f' % (y, r.get_actor_rotation().yaw))
        ok = unreal.EditorLoadingAndSavingUtils.save_packages([b.get_outermost(), r.get_outermost()], False)
        say('SAVED ok=%s' % ok)
open(os.path.join(OUT, 'shop_fix.txt'), 'w').write('\n'.join(lines) + '\n')
