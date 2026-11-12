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

From B3 (`BP_Goon`, `BP_GoonSpawner`; graphs as text in `tools/b3_graphs.py`, test steps in `JumpCut/Saved/b3_test.py`):
- **A child Blueprint made with `BlueprintTools.create` gets real BeginPlay / Tick events that call `Parent:`**, plus an
  empty ActorBeginOverlap. For a child with "no graph at all" delete all five nodes (`find_nodes` title `""`,
  `delete_node`); the parent's BeginPlay and Tick still run (checked in Play mode).
- **Making a new Scene component the root:** `add_component` (owner = the Blueprint), then
  `set_parent_component` with `component` = `<BP>_C:DefaultSceneRoot_GEN_VARIABLE` and `parent` = the new
  component. That promotes it and removes DefaultSceneRoot. Passing only the new component fails ("cannot be parented
  to the world"). Further components: `add_component` with `owner` = the root's `_GEN_VARIABLE` path.
- **Int and float in one maths chain:** `(* (- GoonCount 1) 0.5)` was built as int-int and a float*float whose
  output pin is Integer (0.5 lost). Convert first: `(Math|Conversions|ToFloat(Integer) x)`. Check pin types with
  `get_node_infos`. `(for i (range n) ...)` makes a ForLoop 0 .. n-1.
- `(Game|SpawnActorfromClass "<path>_C" (Math|Transform|MakeTransform :Location at :Rotation rot) "AlwaysSpawn" "MultiplyWithRoot")`
  gives a typed `BP_Goon` output that `Utilities|Array|Add` takes straight into a `BP_Goon` array.
- **Python can't spawn into the PIE world** (`GameplayStatics` has no `begin_deferred_actor_spawn_from_class`). Place
  temporary actors in the editor level before `StartPIE` (labels `TEMP_<packet>_*`), destroy them after `StopPIE`;
  the level then reports no dirty map packages.
- The goons hurt the player fast (8 every ~1.85 s each): with three goons a test player is lost in ~7 s. Order tests so
  health doesn't matter, or restart PIE. `set_global_time_dilation 0.25` gives ~1 game second per Type call.

From C1 (`BP_PlazaGate`, `BP_Checkpoint`, `BP_SceneMarker`, the level; graphs `tools/c1_graphs.py`, level `tools/c1_layout.py`):
- **Console box textbox ref:** `Snapshot` ref `m2` (the menu next to "Cmd") lists `textbox [ref=tb2]`; `Type` needs that ref. `py <path> args` passes `sys.argv`.
- **`set_variable_instance_editable`** takes `variable_name`, `instance_editable`. `ActorTools.add_component` takes `owner`, `component_type`, `name`; `ObjectTools.get_properties` takes `properties` (a list). `AssetTools.save_assets` takes `asset_paths`.
- **Component node ids:** `(Variables|Default|GetTriggerSphere)`, `Transformation|GetWorldLocation :self c`, `Components|Sphere|GetScaledSphereRadius :self c`,
  `Class|SceneComponent|GetRelativeLocation :self c`, `Transformation|SetRelativeLocation :self c :NewLocation v`, `Math|Interpolation|FInterptoConstant :Current :Target :DeltaTime :InterpSpeed`,
  `Rendering|SetVisibility :self c :bNewVisibility true`. A new Actor Blueprint's EventGraph has a stray empty `ActorBeginOverlap` event: `find_nodes` title `ActorBeginOverlap`, `delete_node`.
- **Python in the editor:** `eas.spawn_actor_from_class(unreal.StaticMeshActor, ...)`, `a.static_mesh_component.set_static_mesh/set_material/set_mobility`; tag actors (`set_editor_property('tags', [unreal.Name('C1_Layout')])`) to delete only your own on a re-run; Blueprint variables via `a.set_editor_property('GoonCount', 3)` work on placed copies (instance-editable ones). `GameplayStatics.get_time_seconds(world)`; `SystemLibrary.line_trace_single(world, a, b, TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], DrawDebugTrace.NONE, True)` works in the editor world and in PIE.
- **`CaptureViewport` during PIE draws the editor scene, not the game** (a gate that Tick had raised still showed closed). Use `CaptureEditorImage` with the player teleported in front of the thing. Calls right after a `py` Type arrive before the py runs: capture in the next call.
- `Floor_Base` is a 200 m square (x/y +-10000): anything beyond needs its own floor slab. `PlayerReachWin` does nothing if the player `IsLost` (a test player the goons killed needs a PIE restart).

From D1 (`BP_BossFreeze`, boss-freeze functions on `BP_Player`, C1b fixes; graphs `tools/d1_graphs.py`, Play-mode steps `JumpCut/Saved/d1_pie.py`):
- **The `IsValid` macro ends the exec flow like a cast:** anything written after `(Utilities|IsValid ...)` in the same
  body is rejected ("Unreachable code after branch/return"). Two IsValid checks in one event: put the second part in its
  own small function and call it from both the `Is Valid` and `Is Not Valid` branches.
- **Hook events with parameters:** after `add_event(bp, 'EnemyThink')` the reader prints `(event EventEnemyThink (DeltaSeconds))`;
  write it exactly like that. A child made with `BlueprintTools.create` still gets the BeginPlay/Tick/Overlap nodes: delete them.
- **Another Blueprint's variable:** `(Class|BPPlayer|GetIsFrozenbyBoss :self ref)` (find exact ids with `find_node_types`,
  filter = the variable name). Component scale: `Transformation|SetRelativeScale3D :self c :NewScale3D v`.
- `SetVisibility` with `:bNewVisibility false` reads back without the pin (false is the default): check with `get_node_infos`.
- **Component template visibility:** `ObjectTools.set_properties` on `<BP>_C:<Comp>_GEN_VARIABLE` takes `{"bVisible": false}`
  (keeps a big warning mesh out of the editor view). Inherited native components (`:CollisionCylinder`, `:CharacterMesh0`)
  take `CapsuleHalfHeight` / `RelativeScale3D` / `OverrideMaterials` on the child's CDO.
- **A placed actor's material/radius that doesn't reach disk:** `comp.modify()`, change it, then
  `actor.modify()` + `set_actor_transform(<its own full transform>)` and `save_current_level()`; `git status` then shows the
  actor file. (Floor_Base and the checkpoint's `TriggerSphere` radius were fixed this way.)
- **Scripted fights:** a `register_slate_post_tick_callback` "bot" (walk with `add_movement_input`, `set_actor_rotation` +
  `PlayerPunch` when in reach, `RewindStart` when frozen) plays the whole loop at full speed and logs every state change;
  far more reliable than one Type call per step (each call is 1-20 s of real time). `d1_pie.py bot rewind|norewind`.
- **Waiting from Bash:** plain `sleep N` longer than a few seconds is blocked; use `until grep -q <marker> <log>; do sleep 3; done`.
- A capture "freeze" for `CaptureEditorImage`: set global dilation 0.0001, call the function that shows the warning
  (`BossStartFreezeWindup`), capture in the next call, then restore dilation.

From C1c / D2 (gate close-behind fix, wake-on-hit, the player's Freeze Frame; graphs `tools/d2_graphs.py`, Play-mode
scenarios `JumpCut/Saved/d2_pie.py`):
- **The duplicate-graph trap hit again** on `EnemyTakeHit` (an `if` followed by more statements inside an `if`): 44 -> 91
  nodes after one write. Count before and after every write; if it grew, `delete_node` all but `K2Node_FunctionEntry_0`
  (keep `K2Node_FunctionResult_0` too in a function with outputs) and write again (it came back at 48).
- **Scenario generators beat one Type call per step:** `d2_pie.py` runs each test as a Python generator driven by a
  slate post-tick callback; it yields `('t', secs)` or `('until', fn, timeout)` and logs with game times. A whole
  10 s Freeze Frame test runs in one call. Wait from Bash with `for i in $(seq 1 40); do grep -q "=== x done" log && break; sleep 3; done`.
- **Order of a test reset:** teleport the player out of the plaza *before* `PlazaGateResetToStart` / boss reset, or the
  re-armed gate sees the player inside and shuts again on the next tick. An awake boss left in the plaza between runs
  kills an idle player within ~15 s, and then every enemy is stopped (lose state): restart PIE between groups.
- Freeze Frame's 20 s cooldown means one freeze per PIE session in a test; restart PIE (about 5 s) rather than wait.
- `SystemLibrary.line_trace_single` returns `None` (not a hit result) when nothing is hit.
- A scene component's location from Python: `c.get_editor_property('relative_location')` (no `get_relative_location`).
- `sys.argv` read inside a tick-driven generator is whatever the *latest* `py` run set: capture arguments when the
  scenario starts, not later.
