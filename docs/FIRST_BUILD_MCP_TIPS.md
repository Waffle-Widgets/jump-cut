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
  writes the map and every external-actor file. (`SceneTools.save_actor` fails on a never-saved actor:
  "Asset does not exist: /Game/__ExternalActors__/...".)

From B1 (`BP_Player`, `BP_EnemyBase`; all graphs as text in `tools/b1_graphs.py`):
- **Variables / functions in one script:** `BlueprintTools.add_variable` (`type_name` `float`/`bool`/`int`/`Vector`,
  `container_type: "ARRAY"`), `add_object_variable` (`object_class` = `<bp path>.<BP>_C`), `add_function_graph`, then
  `add_function_param` (`input_param: false` = output). Compile, then set defaults with `ObjectTools.set_properties`
  (`instance` = `/Game/.../BP_X.Default__BP_X_C`, `values` = JSON string); they survive later compiles.
- **Inherited components' defaults:** `.../BP_X.Default__BP_X_C:CharacterMesh0` and `:CharMoveComp`. An added
  component: `ActorTools.add_component` (`owner` = the Blueprint), then `.../BP_X.BP_X_C:<Name>_GEN_VARIABLE`.
  No collision: `{"BodyInstance":{"CollisionProfileName":"NoCollision","CollisionEnabled":"NoCollision"}}`.
- **DSL ids that worked:** own function `(CallFunction|Name :Param v)`; another Blueprint's
  `(Class|BPEnemyBase|EnemyTakeHit :self actor ...)` / `(Class|BPPlayer|PlayerTakeHit :self ref :Damage d)`;
  `(Actor|GetAllActorsOfClass "/Game/.../BP_EnemyBase.BP_EnemyBase_C")` + `(for foe foes ...)` gives typed elements;
  keys `(Game|Player|IsInputKeyDown :self (Game|GetPlayerController :PlayerIndex 0) :Key "LeftMouseButton")`;
  `(Variables|Character|GetCharacterMovement)`, `(Class|CharacterMovementComponent|SetMaxWalkSpeed :self cm :MaxWalkSpeed v)`,
  `(Pawn|Components|CharacterMovement|SetMovementMode :self cm :NewMovementMode "MOVE_Falling")`,
  `(Variables|Actor|SetCustomTimeDilation :CustomTimeDilation v)`, `(Character|LaunchCharacter :LaunchVelocity v :bXYOverride true :bZOverride true)`,
  the IsValid macro `(Utilities|IsValid x (:"Is Valid" ...) (:"Is Not Valid" ...))`. `(if ...)` followed by more
  statements wires both Branch outputs on (the reader prints it as `elif`/`else _`; check with `get_node_infos`).
- A new Blueprint's EventGraph keeps empty BeginPlay / ActorBeginOverlap nodes after `write_graph_dsl`. Delete them
  (`find_nodes` with `entry_points_only`, `delete_node`) where a BeginPlay must not exist (`BP_Player`).
- **Calling functions on live PIE actors:** a `.py` run through the console box with
  `world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()`,
  `unreal.GameplayStatics.get_all_actors_of_class(world, unreal.load_class(None, '<path>_C'))`, then
  `actor.call_method('PlayerTakeHit', (30.0,))`; a function with one output returns it (`call_method('PlayerGetHealthNow')`
  -> 70.0). `actor.get_editor_property('Health')` reads Blueprint variables. Each step a separate `py` run; wait between.

From B4 (Rewind on `BP_Player`; graphs as text in `tools/b4_graphs.py`, test steps in `JumpCut/Saved/b4_test.py`):
- **Array node ids:** `(Utilities|Array|Add :TargetArray (Variables|Default|GetTrailPos) :NewItem v)`, `Utilities|Array|Clear`,
  `Utilities|Array|RemoveIndex :TargetArray a :IndexToRemove 0`, `Utilities|Array|Length`, `Utilities|Array|LastIndex`,
  read with `(Utilities|Array|Get(acopy) array index)` (positional; its index pin is called "Dimension 1").
  Maths: `Math|Vector|Lerp(Vector)`, `Math|Vector|Distance(Vector)`, `Math|Float|Floor` (returns int),
  `Math|Integer|Min(Integer)` (plain `Math|Integer|Min` and `Math|Vector|Lerp` don't exist). Int x float mixes compiled fine.
- **`write_graph_dsl` did NOT replace one graph:** `PlayerTickTrail` (an `if` with an `else` that holds more statements)
  got a second full copy appended on each write (61 -> 121 -> 181 nodes; the old copies were unreachable, so it still
  compiled and read back right). Other graphs replaced fine. After writing, count nodes with `find_nodes`
  (`title: ""` lists all) and if it grew: `delete_node` every node except `K2Node_FunctionEntry_0`, then write again.
- `find_nodes` needs `title` (pass `""`). A failed tool call inside `execute_tool_script` aborts the whole script even
  inside `try`, so write graphs one per call or expect a partial batch.
- **Timing in Play mode:** Type calls sent in parallel land about 0.02 game s apart; one call per turn is ~1-15 s of real
  time. Slow the world (`GameplayStatics.set_global_time_dilation(world, 0.2)`) to make a 10 s window and a 6 s
  cooldown fit between calls, and 0.02 to sample positions during a 0.25-1 s slide.
- The trail keeps "the newest sample at least 10 s old", so a test that waits too long rewinds to a later spot than
  expected. Log the game time (`get_time_seconds`) of every teleport and compare with the rewind time minus 10.
