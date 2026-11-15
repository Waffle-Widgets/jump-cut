"""Read or change the numbers on the look material that is really in the level.

    py tools/unreal_look_char.py get
    py tools/unreal_look_char.py set CharLevel=0.6 CharEnv=0.3 [save]

The look in Lvl_JumpCut is MI_AnimeLook_JumpCut, NOT MI_AnimeLook (CLAUDE.md). Its Char* numbers only touch pixels that
write custom depth, and the player is the only thing that does - so they are the player's lighting. Result goes to
Saved/jcpy/look_char.txt. `save` needs the asset writable (git lfs lock + chmod u+w first).
"""
import sys, os
import unreal

MI = '/Game/Game/Materials/MI_AnimeLook_JumpCut'
out = []
try:
    mi = unreal.load_asset(MI)
    MEL = unreal.MaterialEditingLibrary
    args = sys.argv[1:]
    mode = args[0] if args else 'get'
    if mode == 'set':
        for a in args[1:]:
            if '=' not in a: continue
            k, v = a.split('=')
            old = MEL.get_material_instance_scalar_parameter_value(mi, k)
            MEL.set_material_instance_scalar_parameter_value(mi, k, float(v))
            out.append('SET %s %.3f -> %.3f (reads back %.3f)' % (k, old, float(v), MEL.get_material_instance_scalar_parameter_value(mi, k)))
        MEL.update_material_instance(mi)
        if 'save' in args:
            ok = unreal.EditorLoadingAndSavingUtils.save_packages([mi.get_outermost()], False)
            out.append('saved %s' % ok)
    out.append('parent %s' % mi.get_editor_property('parent').get_name())
    for n in sorted(str(x) for x in MEL.get_scalar_parameter_names(mi)):
        out.append('%s %.3f' % (n, MEL.get_material_instance_scalar_parameter_value(mi, n)))
    for n in sorted(str(x) for x in MEL.get_vector_parameter_names(mi)):
        c = MEL.get_material_instance_vector_parameter_value(mi, n)
        out.append('%s (%.3f %.3f %.3f)' % (n, c.r, c.g, c.b))
except Exception as e:
    out.append('ERROR %r' % e)
d = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(d, exist_ok=True)
open(os.path.join(d, 'look_char.txt'), 'w').write('\n'.join(out))
