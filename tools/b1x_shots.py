"""Render N camera poses to PNG in one editor call, so framing can be tuned without one MCP
capture per pose. Poses come from Saved/jcpy/b1x_poses.json: [{"name","loc":[x,y,z],
"rot":[pitch,yaw],"fov":75}, ...]. Writes Saved/jcpy/shots/<name>.png.

Uses a SceneCapture2D with FinalColorLDR so the capture goes through the level's post process
(the anime look) rather than showing raw lit colour. Editor-only actors are gone from the
capture because a scene capture respects bHiddenInGame, which an editor viewport capture does
NOT - that is the trap that made the first framing pass unreadable.
"""
import unreal, os, json, traceback

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
SHOTS = os.path.join(OUT, 'shots')
if not os.path.isdir(SHOTS):
    os.makedirs(SHOTS)
res = {}
try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = ues.get_game_world() or ues.get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    poses = json.load(open(os.path.join(OUT, 'b1x_poses.json')))
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1280, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = eas.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 0), unreal.Rotator())
    c = cap.capture_component2d
    c.set_editor_property('texture_target', rt)
    c.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    c.set_editor_property('capture_every_frame', False)
    c.set_editor_property('capture_on_movement', False)
    done = []
    for p in poses:
        loc = unreal.Vector(*p['loc'])
        rot = unreal.Rotator(0.0, p['rot'][0], p['rot'][1])     # (roll, pitch, yaw)
        cap.set_actor_location_and_rotation(loc, rot, False, True)
        c.set_editor_property('fov_angle', float(p.get('fov', 75.0)))
        c.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, rt, SHOTS, p['name'] + '.png')
        done.append(p['name'])
    eas.destroy_actor(cap)
    res = {'ok': True, 'shots': done, 'dir': SHOTS}
except Exception as e:
    res = {'ok': False, 'error': '%r\n%s' % (e, traceback.format_exc())}
with open(os.path.join(OUT, 'b1x_shots.json'), 'w') as fh:
    json.dump(res, fh, indent=1)
print('B1X SHOTS ok=%s' % res.get('ok'))
