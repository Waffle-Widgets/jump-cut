"""What FOV does a 26 mm CineCamera actually have in this project, and what focal length matches
the player camera's 90 deg? Spawns a throwaway CineCameraActor, reads its filmback, destroys it.

    py <repo>/tools/b1v_film.py
"""
import unreal, os, json, math, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
L = []; res = {}
def say(s):
    L.append(str(s)); print(str(s))

tmp = None
try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if ues.get_game_world() is not None:
        raise RuntimeError('PIE is running - stop it first')
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    tmp = eas.spawn_actor_from_class(unreal.CineCameraActor,
                                     unreal.Vector(0.0, 0.0, 200000.0), unreal.Rotator())
    cc = tmp.get_cine_camera_component()
    f = cc.get_editor_property('filmback')
    sw, sh = f.sensor_width, f.sensor_height
    res = {'preset': str(f.sensor_aspect_ratio) if hasattr(f, 'sensor_aspect_ratio') else '',
           'sensor_w': round(sw, 4), 'sensor_h': round(sh, 4),
           'default_focal': round(cc.get_editor_property('current_focal_length'), 3)}
    for mm in (22.0, 24.0, 26.0, 28.0):
        res['hfov_%g' % mm] = round(math.degrees(2.0 * math.atan((sw / 2.0) / mm)), 3)
    res['focal_for_hfov90'] = round((sw / 2.0) / math.tan(math.radians(45.0)), 4)
    res['fov_from_component'] = round(cc.get_editor_property('field_of_view'), 3)
    say(json.dumps(res, indent=1))
except Exception as e:
    say('ERROR %r' % e); say(traceback.format_exc())
finally:
    try:
        if tmp is not None:
            unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(tmp)
            say('throwaway destroyed')
    except Exception:
        pass

with open(os.path.join(OUT, 'b1v_film.json'), 'w') as fh:
    json.dump(res, fh, indent=1, default=str)
with open(os.path.join(OUT, 'b1v_film.txt'), 'w') as fh:
    fh.write('\n'.join(L))
print('b1v_film done')
