# MCP tips found during the first build (Nov 12)

How-to notes passed from one builder subagent to the next. Fold the ones that hold up into the `unreal-blueprint`
skill after the run.

- **Blueprint with a parent:** `editor_toolset.toolsets.blueprint.BlueprintTools.create` with
  `{"folder_path":"/Game/Game/Blueprints","asset_name":"BP_X","asset_type":{"refPath":"<parent path>.<Parent>_C"}}`.
  `asset_type` is the parent class; a Blueprint's generated `_C` class works there.
- **`execute_tool_script` has no `unreal` module, and no MCP tool creates a level.** For real Unreal Python: write a
  `.py` file under `JumpCut/Saved/`, then type `py <full path>` into the editor's console box
  (`SlateInspectorToolset.Snapshot` with ref `""` to find the textbox next to the "Cmd" combobox, then `Type` with
  `submit: true`). Have the script write its result to a `.txt` in `Saved/` and read that back.
- **New level from Python:** `LevelEditorSubsystem.new_level(path, False)`, check
  `get_editor_world().get_name()` is the new level before placing anything, spawn with `EditorActorSubsystem`, then
  `save_current_level()`.
- **Game mode override:** `world.get_world_settings().set_editor_property('default_game_mode', unreal.load_class(None, '<path>_C'))`.
- **"Use External Actors" has no Python setter.** It is switched on in the World Settings panel through the Slate
  inspector, and that opens a modal "Convert Actors Packaging" Yes/No window which freezes the MCP (the call times
  out after 300 s). Close it from PowerShell: find the window by title (EnumWindows) and PostMessage
  WM_KEYDOWN/WM_KEYUP VK_RETURN (Yes is the default). `Lvl_JumpCut` already has it on: don't touch it again.
- **Captures:** `CaptureViewport` needs a full `captureTransform` and an all-zero `annotations`. Write the base64 to
  `Saved/` with `AssetTools.write_file` and decode it in PowerShell. Never call the Slate `Screenshot` with ref `""`
  at full size: it returns 7 MB into the chat.
- **Saving the level and its actors:** `py unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()`
  writes the map and every external-actor file.
