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

From B2 / C1d (`WBP_HUD`, the game mode frame, the gate fix; graphs `tools/b2_graphs.py`, Play-mode steps
`JumpCut/Saved/b2_pie.py`):
- **Creating a widget:** `UMGToolSet.CreateWidgetBlueprint` (`folderPath` `/Game/Game/UI`, `assetName`, `parentClass`
  `{"refPath":"/Script/UMG.UserWidget"}`), then `AddWidget` with `widgetClass` `/Script/UMG.CanvasPanel` and no
  `parentWidget` (it becomes the root), then `AddWidget` per child with `parentWidget` = the panel's `refPath`
  (`<WBP>:WidgetTree.<Name>`). Images, progress bars and canvases come back `bIsVariable` true, a TextBlock false:
  call `ToggleWidgetAsVariable` on every one. `MoveWidget` with `childIndex -1` changes draw order (later = on top);
  `AddWidget` takes a `childIndex` to insert.
- **Property names that worked** (after `list_properties`): canvas slot `layoutData` = `{offsets:{left,top,right,bottom},
  anchors:{minimum:{x,y},maximum:{x,y}},alignment:{x,y}}` (non-stretched axis: right/bottom are width/height;
  full screen = anchors 0,0..1,1 and offsets all 0); Image `colorAndOpacity` `{r,g,b,a}` (no texture needed for a flat
  square), `visibility` `"Collapsed"`/`"HitTestInvisible"`; ProgressBar `percent`, `fillColorAndOpacity`; TextBlock
  `text`, `justification` `"Center"`, `colorAndOpacity` `{specifiedColor:{...},colorUseRule:"UseColor_Specified"}`,
  `font` `{fontObject:{refPath:"/Engine/EngineFonts/Roboto.Roboto"},typefaceFontName:"Bold",size:26}`. One
  `execute_tool_script` built the whole tree. `GetWidgetDescription` (`maxDepth -1`) reads it all back in one call.
- **Widget graph ids:** the EventGraph's tick is `(event UserInterface|EventTick (MyGeometry InDeltaTime) ...)`;
  `(Progress|SetPercent :self bar :InPercent v)` (NOT `Class|ProgressBar|SetPercent`: that is a property setter),
  `(Widget|SetRenderOpacity :self w :InOpacity v)`, `(Widget|SetVisibility :self w :InVisibility "Collapsed")`, a
  widget variable `(Variables|WBP_HUD|GetHealthBar)`, the player's variables `(Class|BPPlayer|GetHealth :self ref)`,
  `Utilities|Time|GetGameTimeinSeconds`. A helper function with an object input: `add_object_function_param`
  (`object_class` `/Script/UMG.Widget`). Game mode: `(UserInterface|CreateWidget "/Game/Game/UI/WBP_HUD.WBP_HUD_C"
  :OwningPlayer (Game|GetPlayerController :PlayerIndex 0))` gives a typed output; `(UserInterface|Viewport|AddtoViewport :self w)`.
- **The reader lies about some class names:** `read_graph_dsl` printed `Class|AbilitySystemTestAttributeSet|GetHealth`
  for what `get_node_infos` shows is BP_Player's `Health` getter (self pin "BP Player Object Reference"). Check with
  `get_node_infos` before "fixing" it. It also prints a float-minus-float feeding a vector multiply as `vector-vector`.
- `get_node_type_pins` on a function graph leaves probe nodes in it; `write_graph_dsl` of an empty body
  `(fn X (DeltaSeconds))` over a graph with nodes left one orphan pure node behind. Count with `find_nodes` and
  `delete_node` leftovers.
- **Captures with the HUD:** `CaptureEditorImage` in PIE DOES include UMG widgets (it is the whole editor window,
  1280 x 517; the game view is the left ~1020 px). Freeze a moment with `set_global_time_dilation 0.0001` from the
  scenario step, capture in the next call. Read widget state objectively from Python: `unreal.ObjectIterator(<WBP_HUD_C>)`
  filtered by `get_world() == game world` (there is no `unreal.WidgetBlueprintLibrary` in this editor's Python), then
  `get_editor_property('HealthBar').get_editor_property('percent')`, `.get_render_opacity()`, `.get_visibility()`.
- **Blueprint variables that aren't instance-editable can't be set on a live actor** (Python `set_editor_property`
  and `ObjectTools.set_properties` both refuse `HasRewind`). To test "player without Rewind", set the CDO
  (`Default__BP_Player_C`) in memory with `ObjectTools.set_properties` before `StartPIE`, and set it back after
  (never save `BP_Player` for it). Health can be refilled with a negative `PlayerTakeHit(h - 100)`.
- An awake boss kills an idle test player between scripted runs; send him home (`EnemyResetToStart`) at the end of each run.

From G1 / E1 (design change, screens and restart; graphs `tools/e1_graphs.py`, editor steps `JumpCut/Saved/e1_editor.py`,
Play-mode scenarios `JumpCut/Saved/e1_pie.py`):
- **A component added to a Blueprint reaches placed copies blank.** `BP_SceneMarker`'s new `GiftMesh` had no mesh, no
  material, scale 1, collision on (!) on every marker placed before it; only a newly spawned one was right. Fix per
  instance in Python: `c.modify()`, set it, `retransform(actor)`, then **fetch the component again**: the
  re-run construction replaces it (the old reference prints `TRASH_StaticMeshComponent_0`) and keeps only some of
  what you set (mesh, material and location stuck; `relative_scale3d` via `set_editor_property`, visibility and
  collision didn't until set with `set_relative_scale3d`, `set_visibility`, `set_collision_enabled` in a second pass).
  Check every placed copy in Play mode (`e1_probe.py`).
- **Duplicate-graph trap again** on `BossThinkFight` (an `if` with an `else`): 17 -> 35 nodes. Count every write.
- **A collapsed widget doesn't tick.** The HUD, kept Collapsed on the title, showed its designer defaults (both power
  icons) on its first visible frame. Make the designer defaults the "off" state.
- `Game|OpenLevel(byName)` needs `(Utilities|String|StringToName (Game|GetCurrentLevelName :bRemovePrefixString true))`.
  `Input|SetInputModeGameOnly :PlayerController pc`; `Pawn|SetControlRotation :self pc :NewRotation r`.
- `ObjectTools.set_properties` on a class default: `/Game/.../BP_X.Default__BP_X_C` (NOT `BP_X.BP_X.Default__...`).
- Widget slot: `get_properties(widget, ['slot'])` returns the `CanvasPanelSlot` ref to set `layoutData` / `bAutoSize` on.
- **A scenario generator across `OpenLevel`:** the new world's game time restarts, so a `('t', n)` wait set in the old
  world never ends. Stop the callback and run a new scenario in the new world.
- `CaptureEditorImage` -> `AssetTools.write_file` (`file_path`, `content`) inside one `execute_tool_script`, decode in
  Bash with `base64`: no picture through the chat.
- Defeated goons stay standing until a Freeze Frame ends (by design), and probably block the player's capsule: the
  scripted walk from the goons to the checkpoint (21 m) took 12 s instead of about 4 (inferred, not measured).

From A3 (the anime look on `Lvl_JumpCut`; editor steps `JumpCut/Saved/a3_editor.py`, Play-mode steps `JumpCut/Saved/a3_pie.py`):
- **Render CustomDepth on characters:** `ObjectTools.set_properties` on `.../BP_X.Default__BP_X_C:CharacterMesh0` with
  `{"bRenderCustomDepth": true}`. Setting it on the parent (`BP_EnemyBase`) did NOT reach the children's CDOs in the
  running editor, even after `BlueprintEditorLibrary.compile_blueprint` on all four: set it on `BP_Goon` and
  `BP_BossFreeze` too. Placed copies (`Player_Main`, `Boss_Freeze`) also kept false until set per instance
  (`mesh.modify()`, `set_render_custom_depth(True)`, re-set the transform, `save_current_level()`). Goons spawned at
  runtime by the spawner come out right once `BP_Goon`'s CDO is set. Check live actors in PIE: `a.mesh.get_editor_property('render_custom_depth')`.
- `r.CustomDepth` is 1 ("enabled on demand", the engine default) with nothing in `DefaultEngine.ini`; that is enough for
  the look (it reads custom depth, not stencil). Stencil values need `r.CustomDepth=3`.
- **Opening another level from Python** (`LevelEditorSubsystem.load_level`) with dirty *content* packages but no dirty
  map opened without a Save window (Nov 12, twice).
- **Tuning a post-process material live in PIE without touching assets:** `unreal.MaterialLibrary.create_dynamic_material_instance(world, mi)`
  (not `KismetMaterialLibrary`), put it in the PIE volume's `weighted_blendables`, `set_scalar_parameter_value`; copy the
  keepers into the MI after `StopPIE`. Toggle a placed volume's `enabled` on the PIE copy for before/after captures.
- `CaptureEditorImage` crops: `JumpCut/Saved/a3_crop.ps1 -In x.txt -Out x.png [-X -Y -W -H -Scale]` decodes the base64
  and crops/zooms with System.Drawing (no PIL on this PC). Give it names, not paths: .NET resolves relative paths
  against the process folder, not PowerShell's.
- `startfpschart` / `stopfpschart` typed into the console box during PIE; the result is in the log under
  `LogChartCreation` (`GetLogEntries` pattern `frames collected|Average (GPU|RenderThread|GameThread)`), file under
  `Saved/Profiling/FPSChartStats/`. The editor is capped at 120 fps here, so compare GPU ms, not fps.
- An awake boss takes an idle player from 100 to 0 in about 10 s; refill (`PlayerTakeHit(h - 100)`) before each 10 s
  measurement.
- `Lvl_Cafe` loads with a `LoadErrors` list: `BS_Idle_Walk_Run_CW` points at `MF_*_CW1` / `MM_*_CW1` packages, but the
  files are named `*_CW` (no `1`). Pre-existing in the merged CafeWalker import; not fixed in A3.
