# Project notes for Claude Code

## Read these first
- `docs/HOW_WE_WORK.md` — the team's workflow for newcomers (roles per computer, playtest loop); keep it current
- `docs/PLAN.md` — the team plan, schedule, and rules of thumb
- `docs/PITCH.md` — the game we're making (filled in after the theme reveal)
- `docs/ROADMAP.md` — what is open, what is waiting for the team's yes, the cut list and what was decided. Read it
  before any feature or scope discussion
- `docs/RULES.md` — the official jam rules we must follow
- `CREDITS.md` — every asset we didn't make ourselves

## Who we are
- A team of up to 5 (the jam's limit) entering the 2026 Epic AI MegaJam (Nov 12-15). Each teammate works on their own
  PC, with their own GitHub account and their own Claude account. Team list and who owns what: `docs/TEAM.md`.
- **This repo is the jam entry: Jump Cut.** Everything for the game is made here, between Nov 11, 9 PM and Nov 15.
  Our practice repo (`megajam-2026-practice`) is where the tools and lessons came from; when we discover a better way
  to work, update this CLAUDE.md.
- We are beginners: we play a lot of games but have little coding or Unreal experience.
- We act as game designers and testers. You do the implementation.

## Goals, and keeping us on track (the team asked for this on Nov 11)
**Goal:** submit a finished, fun Windows build before **Sun Nov 15, 5:59 PM Pacific**, with everything the form asks
for: a 30-60 s gameplay video at 1080p, the devlog link, credits, our pre-jam work declared and "Tools you used" filled in.
**Prize focus (one modifier per entry):** Glass Box first (the devlog), Render Royalty second (best visuals), Best Team
third, Best Overall as a stretch. Don't spend jam time chasing other prizes (NVIDIA RTX Award, mobile, web builds).

| When (Pacific) | Checkpoint |
|---|---|
| Wed Nov 11, 11 AM | Theme reveal. Pick a one-sentence pitch within about an hour; write `docs/PITCH.md`; the cut list lives in `docs/ROADMAP.md` |
| Wed Nov 11, 9 PM | Jam starts. Nothing for the game is made before this |
| Thu Nov 12 | Core loop playable start to finish, grey boxes, no art |
| Fri Nov 13 | Level, win/lose, start/restart; first packaged build tested. **Feature freeze at the end of the day** |
| Sat Nov 14 | Art, audio, juice and playtests only; record footage |
| Sun Nov 15 | Bug fixes only. Final build by noon, video and itch.io page by 3 PM, submit before 5:59 PM |

Your job, in every chat from Nov 11 to Nov 15:
- **Open with one line:** time left to the deadline and where we stand against today's checkpoint.
- **Check every request** against the pitch, today's checkpoint and the prize focus. If it doesn't serve them, say so
  plainly, suggest a smaller version or the cut list, and only go ahead if we still say go. Saying no is helping.
- **Behind a checkpoint?** Say so and name what to cut. After Friday's freeze, refuse new features (bugs, polish, art,
  audio only). After Sunday noon, only submission work.
- Keep the devlog current without being asked: it's our best prize chance.

## Engine and project
- Unreal Engine 5.8, connected to you through Epic's Unreal MCP plugin.
- C++ project, but build gameplay in **Blueprints** unless C++ is truly required. Ask before writing C++.
- Target platform: Windows.

## Which computer am I on? (check at the start of every chat)
Run `hostname` and find this computer's row in the **Computers** table in `docs/TEAM.md`, and do only what its role allows:
- **builder:** the only role that saves or commits Unreal files (`.uasset`, `.umap`) and publishes test builds. Work on
  `main` and merge finished work straight into it: there is no `playtest` branch any more (Justin, Nov 14).
  The `playtest-issues` skill still runs the issue loop. `builder (Area)` = only that area.
- **maker:** Blender, Meshy, TRELLIS, sounds, scripts. Never save in Unreal, even if it's open: hand the files to the builder.
- **tester:** help play, file and check issues (`docs/PLAYTEST.md`). If Unreal is open to play, never save in it.
- Any role may edit docs and scripts.
If asked to do something the role doesn't allow, say which computer is the builder and offer to file an issue or hand it
over instead. If the user wants to change roles, edit the table, commit and push (`pc-handoff` skill when the builder
moves). If no row matches `hostname`, ask which computer this is and fix its name in the table.

## How to work with us
- Make **one small change at a time**, then stop and tell us exactly what to test in Play mode.
- Explain every change in plain language: what you made, where it lives in the Content Browser, and why.
- Before a big or risky change, tell us the plan and wait for "go".
- If something fails, tell us the actual error and your best guess at the cause. Don't silently retry many times.
- Once we confirm a feature works in Play mode, save all assets in the editor, then commit and push to GitHub yourself
  with a short plain-language message. Tell us what you committed. Don't commit work we haven't tested.
- We often prompt you remotely from another machine, so send screenshots of the editor or results when they help us follow along.
- Keep the project tidy: put our content under `Content/Game/` in folders by type (Blueprints, Maps, Materials, Audio, UI).
- Use clear names: `BP_` for Blueprints, `M_` for materials, `MI_` for material instances, `WBP_` for widgets, `SFX_` for sounds.

## Reporting and what "done" means (from Justin's Cerberus project, Nov 12)
**Reporting**
- Every "done" says what was asked, what was done and what was left out, with a number where one exists (issues
  fixed, files changed, triangle count, zip size).
- If you make a task smaller than what was asked, say so when you decide it, not in the wrap-up. A smaller task is
  never reported as the original one done.
- Say what you checked yourself (it compiled, the graph read back right, it spawned, a capture from the game camera)
  and what still needs a person in Play mode. Feel is never yours to call verified.
- On a maker or tester computer, a change you couldn't see running in the game is untested. Say that plainly and
  name who has to check it.
- Label anything you inferred rather than checked as inferred.

**A change is done when** all of these are true, and the report says which are not:
1. A person confirmed it in Play mode or in a test build (maker work: the builder imported it and it was looked at
   from the game camera).
2. Saved, then committed and pushed under the teammate's own Git name, after `git pull --rebase`.
3. Its devlog entry is in the same commit (`devlog-entry` skill).
4. `CREDITS.md` lists anything we didn't make.
5. LFS locks we no longer need are released.
6. `docs/ROADMAP.md` still tells the truth (its top says how it is organized): a shipped item moved from Open into
   its devlog entry, a settled question moved to Decisions with the date and who decided, and a proposal stays under
   "Waiting for a yes" until a person on the team agrees. An idea that isn't for now is a GitHub issue labelled
   `idea`, not a quiet edit to a doc.
7. A hand-off to another computer names the files and what to do with them.

**Fixing things**
- When you fix a problem, look for the siblings that share its Blueprint, function or script and fix them in the
  same pass. Say which ones you checked.
- A fix that needs another computer or a second player to check goes on a `<name>/<topic>` branch with the untested
  part named at the top of the hand-off. It doesn't reach `main` on an inference.

## Skills (`.claude/skills/`)
Step-by-step checklists Claude loads when a task matches (or type `/<name>`). Use them; update the skill when we
learn something, and copy it into the jam repo (the bootstrap does). Allowed before the jam: they're prompts (§7h).
`unreal-blueprint`, `asset-import`, `trellis-model`, `make-sound`, `playtest-capture`, `package-build`,
`playtest-issues`, `devlog-entry`, `pc-handoff`, `jam-rules-check`, `niagara-fx`, `niagara-fluids` (realistic fire: Niagara Fluids, tuning through Slate, baking a sim into a flipbook), `chaos-physics` (things that break: Geometry Collections cut by a Dataflow graph, broken from code).

## Lessons from practice (Unreal + MCP)

### Slowing down something that is NOT self (learned 2026-11-15, beat 1's fire)
- **`Variables|Actor|SetCustomTimeDilation` has NO `self` pin.** It writes the dilation of the
  actor the graph is running on and nothing else's; `write_graph_dsl` refuses `:self` with
  *"Input pins: ['CustomTimeDilation']"*. To stop another actor's effect, hold its COMPONENT and
  use **`Niagara|SetCustomTimeDilation`**, whose pins are **`self`** and **`Dilation`** - note it
  is `Dilation`, not `CustomTimeDilation`, which is the spelling that fails. Freeze Frame stops
  enemies through `BP_EnemyBase.EnemySetTimeStopped`, a custom function, which is why there was no
  working example of the cross-actor form to copy.
- **`write_graph_dsl`'s error message is the cheapest pin documentation there is.** It names every
  valid input pin and rolls the whole graph back, so a wrong guess costs one call and teaches you
  the right name. `get_node_type_pins` does NOT substitute: it returns each pin's *value*
  (`"1.000000"`, `"Chaos_NONE"`), not its name.
- **A `Package` has no `is_dirty()` in UE 5.8 Python.** It is the obvious name and it raises.
- **You cannot WAIT for a cinematic from Python - drive its clock.** Python runs on the game
  thread, so `time.sleep` stops the world it is waiting for, and an 11 s sequence is over before a
  second MCP round trip (5-8 s) lands. `tools/b1z_pie.py open` calls `CineDirectorStep` with a
  fixed delta itself; the director's own Tick cannot run while the script holds the thread, so the
  loop is the only thing advancing it and every trigger runs through the real function. It cannot
  show PHYSICS (no ticks = no falling debris, no settling ragdoll), so it proves each trigger fired
  and each physics state was applied; sample again later for where things came to rest.
- **`BP_Player.FreezeFrameActive` is not instance-editable.** Drive the real power instead of
  writing the flag: `PlayerGrantFreezeFrame` -> `FreezeFrameStart` -> ... -> `PlayerFreezeFrameEnd`
  through `call_method`. It goes through the gates, so it is better evidence anyway.
- **`b1_opening_cine.py` reads the PLACED `BP_CrashDriver`'s location** to key the last two frames
  of the thrown body, so the driver must be MOVED BEFORE the sequence is rebuilt. Rebuilding first
  keyed the arc to the old left-hand spot - a mid-air tumble to y -118 and then a snap to y +220 -
  and nothing errored. Order: `b1z_wallpanel.py place` -> `b1_opening_wire.py` -> `b1_opening_cine.py`.

### Blueprint graphs through `write_graph_dsl` (learned 2026-11-15, beat 1's explosion)
- **A variable's CATEGORY is part of its DSL type id.** Move a variable out of `Default` and
  `Variables|Default|GetFoo` stops existing - `write_graph_dsl` fails with
  *"Variables|Default|GetExplCarGC does not exist"* for a variable `list_variables` plainly
  returns. Thirty variables were written fine, then `set_variable_category` to "Beat1 Explosion"
  broke every later write to the same graphs. Keep new variables in `Default`, or write
  `Variables|<Category>|Get<Name>` in the DSL.
- **A multi-exec node terminates the exec flow it sits in, so it must be the LAST statement in
  its scope.** `Utilities|IsValid`, any `CastTo*`, any latent node. Two guards in one function
  are refused with *"Unreachable code after branch/return"*; split the function or nest the
  second guard inside the first's continuation. Plain `if`/`elif` do NOT terminate - a chain of
  them followed by more statements is fine, which is what makes the rule easy to misread.
- **`write_graph_dsl` leaves the OLD graph behind as orphaned nodes.** Confirmed by dumping
  `find_nodes` + `get_node_infos` on `CineDirectorStep`: the function entry is repointed at the
  new chain and the previous chain survives, fully wired, with nothing pointing into it. It is
  dead code in a *function*; in an EVENT graph a second copy of an event would run. Count nodes
  after any rewrite you care about.
- **The read-back form is not the write form.** `read_graph_dsl` prints
  `Math|Vector|vector-vector`, which `get_node_type_pins` refuses to create. Write `(- a b)` and
  let the DSL pick the node.

### Chaos geometry collections (learned 2026-11-15, the exploding car)
- **A GeometryCollectionActor spawns `Chaos_Object_Dynamic`, and anything car-sized falls out of
  the world.** The cafe-table GCs use Dynamic and are fine, which makes the setting look safe.
  Measured: `B1_Cafe_CrashCar_GC`'s bounds reached **z -19405 within four seconds of BeginPlay**.
  Use **Kinematic** for something that must stand still until it is hit.
- **A kinematic collection CANNOT be broken, and fails silently.** `ApplyExternalStrain` plus
  `AddRadialImpulse` ran with no error and the bounds came back identical to the intact mesh.
  Switch it first: `Class|GeometryCollectionComponent|SetObjectType` to `Chaos_Object_Dynamic`,
  then `ChaosPhysics|RemoveAllAnchors`, then `ChaosPhysics|CrumbleActiveClusters`, then the
  strain and the impulse.
- **Chaos debris does not collide with this city kit's floors.** The kit is collision-trace
  *complex-as-simple* and GC particles only collide with simple/convex collision, so broken
  pieces fall straight through to **z -44289**. Put a hidden box collider under anything that
  breaks (`B1_Cafe_DebrisFloor`).
- Run **`py <repo>/tools/b1x_orphans.py`** after any script that destroys and re-spawns a placed
  actor. A re-spawned actor gets a NEW package hash, the old `__ExternalActors__` file stays on
  disk, and World Partition loads everything in that folder - which would have put a **second
  BP_OpeningDirector** in the level and run beat 1 twice. It found exactly two.

### Other traps from the same session
- **The editor console box is `tb1`. `tb2` is the Outliner search.** Refs are assigned per
  session and the old note naming `tb2` is stale. A `py <path>` typed into `tb2` silently becomes
  an Outliner filter - the Outliner then reads *"No matching actors (473 total)"* and no `Cmd:`
  line appears in the log. Confirm by the `Cmd:` line, never by the return value.
- **`SlateInspector.Type` with `submit: true` works where `FillForm` + `PressKey("Enter")` does
  not.** `PressKey` goes to the *focused* widget, and `FillForm` does not focus. `Type` focuses
  first.
- **`MakeRotFromZ` leaves the roll about the view axis free.** A billboard card built with it
  came out at **roll -83 degrees** - the sprite drawn on its side. For a `/Engine/BasicShapes/Plane`
  facing a camera, use `MakeRotator(roll 0, pitch = camPitch + 90, yaw = camYaw)`.
- **A flipbook frame index must be floored inside the MATERIAL.** A fractional `Frame` lands
  between two cells of the sheet and draws half of each.
- **A change made only on a placed actor is reverted by the next run of the script that places
  it.** The objective beacon was changed from a sphere to a cone in a live session on Nov 14 and
  never written into `tools/b1_opening_wire.py`; running that script on Nov 15 put the sphere
  straight back, and it took a PIE capture to notice.
- **`EditorActorSubsystem` cannot spawn into the PIE world.** `spawn_actor_from_class` returns
  `None` there, so a SceneCapture2D is not an option for photographing a running game. Point the
  real player camera (`tools/b1x_pie.py look`) and use `CaptureEditorImage`, which DOES composite
  UMG during PIE - the letterbox bars and the caption box photograph fine.
- **Lock before you edit.** Git LFS marks committed `.uasset`/`.umap` files read-only. Run `git lfs lock <file>` before changing
  an asset that's already committed, or the editor's save silently does nothing. After pushing, `git lfs unlock <file>`.
  Check `git status` after saving to confirm the file really changed.
- `Content/Game/` on disk is `/Game/Game/...` inside Unreal (and in MCP tool paths).
- A child Blueprint's input event does **not** replace the parent's. To stop the template character walking, override the
  parent's `Move` event with an empty one in the child.
- Claude can't send keyboard input into Play mode, so it can check that things compile and spawn, but **we** test movement and feel.
- The Blueprint graph tool (`write_graph_dsl`) can't attach code to Enhanced Input events or create Timelines. Put logic in a
  function, then wire the input event to it by hand; use Event Tick instead of a Timeline.
- **Never edit while Play mode is running.** Stop PIE first. Creating or editing Blueprints during PIE froze the editor
  for good and lost all unsaved work. Also **save after every batch** of changes, not at the end.
- Reset the input mode to "game only" when a level starts; "UI only" from an end screen survives a level reload.
- After deleting a Blueprint function, compile before re-adding one with the same name, or it becomes `Name_0`.
- Changing a Blueprint's components doesn't always update copies **already placed in the level**. After a component
  change, check one placed copy; if it's stale, re-place the actors (keep their transforms and settings).
- Blueprint "pure" nodes re-run every time they're read. Don't `bind` a value, then set the variable it came from and read
  the bind again (the goal count got +1 twice). Read the variable after setting it instead.
- Batch many MCP calls into one `execute_tool_script` (sandboxed Python) to save round trips. Don't `time.sleep` inside
  it; that freezes the game thread. Wait outside instead.
- With "prompt before auto-importing" off (Editor Preferences > Loading & Saving), `.wav` files dropped into or changed in
  `Content/` import by themselves within seconds, even while the editor is open. Save the new asset afterwards.
  `tools/make_sfx.py` generates our sounds and music from code: no downloads, no credits needed.
- Night scenes need fixed exposure (post-process Metering Mode = Manual), or auto-exposure brightens night back to day.
- **Lock new assets right after their first commit.** Committing makes them read-only, and the next save fails silently.
- `set_actor_transform` resets any part you leave out (location, rotation or scale). Always pass the full transform.
- When two engine classes share a node name (e.g. Set Volume Multiplier on Audio vs Synth components), the DSL may pick
  the wrong one. Write it, then use `retarget_node_class` and reconnect its pins.
- Give every Blueprint function a name that is unique across the engine **and** our project (not Clear, SetTime, or a
  second `SpeedUp`). Otherwise the graph tool quietly calls the wrong one and it still compiles. Always `read_graph_dsl`
  after writing to check what was really built.
- `write_graph_dsl` replaces the whole graph (good: a function can be rebuilt from text; read it out first as a backup).
  The reader prints literals as `(bind _x 1.0)` and the writer rejects exactly that: fold literals back into the
  expressions. Actor calls like `SetActorLocation` need `:NewLocation value`; a positional arg lands in the `self` pin. Same for `SetActorRotation` (`:NewRotation`). The reader prints a `b`-bool variable as `(|GetbIsHopping)`, but the writer needs `Variables|Default|GetIsHopping` / `SetIsHopping`.
- In Play mode, `SceneTools.find_actors` with `actor_type` = the Blueprint's generated class (`BP_Car.BP_Car_C`) lists the
  live actors, so captures can be aimed at a specific car.
- Never write `(return (SomeFunction ...))` with one of our own Blueprint functions inside. It compiles, but the call never
  runs and the return gives the default (0 / false). `bind` the call first, then `(return value)`. This made every endless
  row count as grass (checkpoints on roads) and switched off obstacle blocking.
- **Importing images and models:** save the file into `Content/Game/Imported/<Name>/`, then import it with the MCP's
  `StaticMeshTools.import_file` / `TextureTools.import_file`, which never open a window. Files dropped in also import by
  themselves: `Config/DefaultEngine.ini` sets Interchange's `bShowImportDialog=False` (read at editor start); without it an
  `.fbx` opens an "Import Content" window that freezes the MCP until a human clicks, so we can't answer it remotely.
  Re-importing a mesh resets its materials, so don't re-import once it's set up.
  **Never delete the source file afterwards:** Unreal opens a modal "Delete Assets" dialog that freezes the MCP until
  someone answers it (Escape = keep the assets). Raw sources under `Imported/` are gitignored instead.
- **GLB files** (TRELLIS.2, Pixal3D, Meshy): auto-import ignores `.glb`, and `StaticMeshTools.import_file` only takes
  FBX/OBJ. Run `tools/glb_for_unreal.py` (PNG textures, real size), then type
  `py <repo>/tools/unreal_import_glb.py <dest folder> <file.glb>` into the editor's console box with the Slate inspector
  (`Observe` the window and `Click` the box first, or `Type` returns false). It imports through Interchange, which keeps
  the glTF PBR material, and switches Nanite off through `StaticMeshEditorSubsystem.set_nanite_settings`: setting the
  property alone left Nanite's fallback mesh, a fifth of the triangles.
- **Meshes that rely on vertex colours** (flowers, leaf shading from our Blender kits): `StaticMeshTools.import_file` uses
  the old FBX importer with vertex colours set to Ignore, and that can't be changed. Copy the `.fbx` into
  `Content/Game/Imported/<Name>/` instead and let Interchange import it by itself (it keeps vertex colours). Afterwards:
  re-point the slots at our materials, delete the empty placeholder `M_*` materials it makes, and **switch Nanite off**
  (`set_nanite_enabled false`). Interchange turns Nanite on, and its simplified mesh drops thin parts like petals.
  Check with `get_triangle_count` that the full count is back.
- A `.png` that Unreal refuses with "produced no assets" may really be WebP (TRELLIS GLBs pack WebP). Check the first
  bytes (`RIFF....WEBP`) and re-save it as a real PNG.
- Fab in Claude's browser pane: the user signs in there once (the launcher login doesn't carry over). Free items still
  need "Add to My Library" and a one-time EULA; Megascans surfaces are free, but many Megascans 3D models are not.
  Downloads land in `~/Downloads` as `<guid>.tmp` zips; identify them by their contents.
- **Packaging a Windows build:** run `tools/package_build.ps1 [-Game Name] [-Run] [-CopyTo <folder>]`. It cooks the start
  map (`GameDefaultMap`) plus every map under `Content/Game/`, zips `Builds/<Team>_<Game>.zip` for itch.io, checks the
  1 GB limit, keeps the `.pdb` debug symbols out of the zip (`Builds/Symbols/`), and `-Run` checks the game launches.
  Works with the editor open (don't save while it cooks). What it handles for us:
  - Our editor plugins (MCP, toolsets) make Unreal build a game program of the project's own, even with no C++.
    `Binaries/` isn't in Git, so the first package on each PC compiles it (about 20 s); later runs reuse it.
  - `-nocompileeditor`: without it, `-build` also rebuilds the editor, which fails with the editor open and needs the
    .NET Framework SDK (not installed on GameStation). `-unrealexe=UnrealEditor-Cmd.exe` avoids the missing
    `<Project>Editor.target` error during the cook.
- Turn off "Use Less CPU when in Background" (Editor Preferences) so Play mode runs at full speed while Claude tests it.
  In a project's files it belongs in `Config/DefaultEditorSettings.ini`, not `DefaultEditorPerProjectUserSettings.ini`
  (the bootstrap script does this, and its `-Verify` reads it back from the running editor).
- To pass a per-actor number to a material (e.g. how often the log bark repeats), use a Scalar Parameter with
  "Use Custom Primitive Data" and set it with `SetDefaultCustomPrimitiveDataFloat`. The runtime `SetCustomPrimitiveDataFloat`
  doesn't stick when the editor runs a construction script. Every mesh using that material needs a value, or it reads 0.
- One Blueprint can be set up in more than one place. `BP_Log` is built by its construction script (placed logs) **and** by
  `LogSetup` (Endless spawns). Search for every caller before changing how an actor looks, and test both maps.
- `mcp__unreal__call_tool` needs `toolset_name` **and** `tool_name` (e.g. `EditorToolset.EditorAppToolset` / `StartPIE`).
- `ObjectTools.get_properties` takes exact property names only. `list_properties` returns a JSON schema, not a list:
  never turn its text into names by string-splitting. A 2,000-character "name" hit Unreal's 1,023-character FName
  limit and crashed the editor (assertion in UnrealNames.cpp). Save before any exploratory call during PIE.
- `ObjectTools.set_properties` writes only **instance-editable** Blueprint variables. A variable that isn't exposed
  is refused by name (the loud failure). The quiet failure is worse: an exposed one can accept the write with **no
  error at all** and still read back unchanged (`BP_Player.InputLocked` did exactly that). Read every value back
  after setting it; never assume a set took.
- **To call one of our own Blueprint functions from a script there is no "call function" tool.** Add a temporary
  instance-editable `Debug<Thing>` bool and one `if` in the actor's tick that clears the flag and calls the
  function. Afterwards remove both and `read_graph_dsl` to check — count the call sites of the function you hooked,
  because `write_graph_dsl` appending twice looks identical to appending once until you count.
- **A simulated key press cannot drive anything we poll.** `SlateInspector.PressKey` presses *and releases* inside
  one call, while our input is read with `IsInputKeyDown` once per tick, so the press never spans a tick. That
  includes the title screen's R. The way into play from a script is `ShowTitleOnStart = false` on the
  `BP_JumpCutGameMode` CDO: `JumpCutFlowTick` then calls the real `JumpCutStartPlay` itself (`FlowState` 1,
  `InputLocked` and `MoveLocked` both false). Put it back to true afterwards.
- **A live enemy ruins a measurement, silently.** A test goon placed 250 cm away chased the player across the
  street and killed him; `PlayerCanAct` is false when `IsLost`, so every ability measured after that read "did
  nothing" for a reason that had nothing to do with the ability. Read `Health` and `IsLost` either side of every
  measurement, and for a static obstacle prefer a body that does not chase (`BP_StuntStandIn` with
  `StandInFights` false stands still).
- **Prefer a structural check to a physics race.** Whether the Splice blink passes through people is settled for
  good by reading each character's capsule *and* mesh `BodyInstance`: all of ours set `Visibility -> ECR_Ignore`,
  and `DefaultEngine.ini` declares no custom trace channels, so `TraceTypeQuery1` is Visibility. That is a fact
  about the assets; a single blink past a walking goon is an anecdote about one frame.
- **A bounding box is not a walking surface.** `SM_RuinSlab_A` is a broken slab: its box reaches 119 cm only
  because of chunks standing up near the edges, while the surface the player stands on down the centre line is
  45. Placing it at `z = -box_height` put the whole beat-4 walkway 74 cm below the street, which turned the head
  room under its 215 ceiling from 39 cm into 113 - enough that a jump clears the gaps the section exists to stop
  it clearing. Nothing about it is visible; the slabs render exactly where you put them. For anything broken or
  jagged, **line-trace down and use where the feet land**, not the box.
- **Imported meshes get ONE auto convex hull from Interchange, and it need not match the art.** For static level
  geometry set `body_setup.collision_trace_flag = CTF_USE_COMPLEX_AS_SIMPLE` so collision is the render mesh.
- **Hidden is not non-colliding, and component collision does not serialize.** `set_actor_hidden_in_game(True)`
  survived a reload; `static_mesh_component.set_collision_enabled(NO_COLLISION)` did NOT, leaving an invisible
  wall across the route (`C1_Run_End` blocked all of beat 4). Use the actor property `set_actor_enable_collision(False)`,
  then re-set the full transform to dirty the package, then save it. Trace from **before** the obstacle to check.
- **Hiding a placed actor does not DIRTY its package.** `set_actor_hidden_in_game(True)` reads back as set and
  survives a reload *only if the package was actually written*. In a one-file-per-actor map it is not: after
  hiding 8 grey boxes, 224 newly spawned actor packages were dirty and **not one of the 8 was**, so the hide
  lived in memory and the grey walls would have come back standing inside the city. Re-set the full transform to
  dirty it, then `EditorLoadingAndSavingUtils.save_packages([a.get_outermost()], False)` - and `git lfs lock`
  them first, because a committed actor package is read-only and the save fails **silently**.
- **Two scripts can both be right about one asset and silently undo each other.** `jumpcut_city_place.py`
  sets every city model to `CTF_USE_COMPLEX_AS_SIMPLE`; `unreal_chaos_props.py` gives three of those same
  models a simple box and `CTF_USE_DEFAULT`, because a body with complex-as-simple collision **cannot
  simulate** and only the log says so. Running the placer after the chaos pass put `SM_CafeChair`,
  `SM_TrafficCone` and `SM_TrashBags` back, which would have stopped every knockable prop the next time
  those meshes were saved. Nothing looks wrong at any point. When a tool writes a property across a whole
  kit, give it an exceptions list (`SIMULATED` in the placer) the moment one member of that kit is used for
  something else, and read the other tool's list rather than trusting the names.
- **`CTF_USE_COMPLEX_AS_SIMPLE` is right for level geometry and wrong for cloth.** Setting it across the city kit
  turned the cafe's noren - a hanging door curtain - into a solid 150 x 100 cm wall across the cafe's only exit.
  It renders perfectly and nothing looks wrong; only a chest-height trace along the route finds it. Keep a
  per-model walk-through list (noren, cables, drapes) and switch collision off on the **actor**.
- **A generated file drifts from its generator, silently.** `city_layout.json` was committed with 216 actors while
  the committed generator produced **224**: the script had gained the New York avenue - the road the car crashes
  in from - after the JSON was last written, so that road existed in code and nowhere else. Before building on any
  generated artefact, re-run its generator and diff the result against what is committed.
- **A keep-clear / no-go table only knows about level geometry that existed when it was written.** The city
  layout's checker passed a 62 m tower standing in the middle of beat 4, because beat 4 was placed hours after
  the checker was authored. When new geometry lands, add its box in the same session - and prove the new entry
  catches something by putting the offender back and watching it fail.
- **An orphaned actor package is not orphaned.** If the editor dies with placed actors dirty, it restores their
  packages to `__ExternalActors__` on the next start. They are not in the loaded level, so they look like junk -
  but World Partition loads every package in that folder, so the next map load gives you **two of everything**
  (we got 46 beat-4 actors from 23). Compare the level's own `actor.get_outermost().get_name()` list against the
  files on disk and move the extras out of `Content` before committing.
- **Lumen is OFF on purpose (`r.DynamicGlobalIlluminationMethod=0`, `r.ReflectionMethod=0`).** `M_AnimeLook`
  bands every surface into lit/shadow at one hard threshold, and Lumen's bounced light sits on that threshold and
  wobbles, so whole walls flipped tone frame to frame ("flickering assets"). Do not turn Lumen back on to make an
  interior look warmer: add a small direct light instead (`Cafe_WarmFill_A/B`, 8 cd, no shadows).
- **Ray tracing, if you ever enable it, needs the skin cache in the SAME commit.** `r.SkinCache.CompileShaders`
  defaults to **0** (`GPUSkinCache.cpp:94`) and `RenderUtils.cpp:1045` is a **Fatal** - *"Ray tracing requires skin
  cache to be enabled"* - so `r.RayTracing=True` on its own crashes the editor on startup, before any window opens.
  Both are `ECVF_ReadOnly`, so they are editor-restart-only. `r.RayTracing.Shadows` is NOT read-only
  (`LightRendering.cpp:84`), so once RT is compiled in, the A/B is a console toggle: `r.RayTracing.Shadows 0` / `1`.
  No `.umap` edit is needed to opt a light in: `r.RayTracing.Shadows.Lights.Directional` defaults to 1 and a light's
  `CastRaytracedShadow` defaults to `UseProjectSetting` (`LightRendering.cpp:253-272`).
  RT **shadows** suit this look - they are hard-edged and stable, which is what the band wants. RT/Lumen **GI** does
  not, for the reason in the Lumen note above. See branch `M_STATION/rt-shadows-test`.
- **`[VSM] Non-Nanite Marking Job Queue overflow` is logged ONCE per session, not once per occurrence**
  (`LoggedOverflowFlags`, `VirtualShadowMapCacheManager.cpp:765`). So grepping the log tells you *whether* it
  happened, never *how often*. The on-screen red version is the useful one: it is shown for ~10 s after the last
  overflow (`VirtualShadowMapCacheManager.cpp:949`), so if it is on screen in a screenshot, one happened in the
  10 s before that frame.
- **A movable directional light's `DynamicShadowDistanceMovableLight` is INERT while VSM is on.** We nearly
  "fixed" the flicker by cutting it from 40,000 to 8,000, and it would have changed nothing:
  `GetDirectionalLightDistanceFadeParameters` returns early with *"Virtual shadow maps do not use cascade distance
  fading"* (`DirectionalLightComponent.cpp:510-516`), and `r.Shadow.DistanceScale` only scales `GetCSMMaxDistance`
  (`DirectionalLightComponent.cpp:701-713`), which the VSM path never reads. Under VSM the clipmap's reach is
  `GetLevelRadius(L) = 2^(L+1)` cm from `r.Shadow.Virtual.Clipmap.LastLevel` (default **22** = ~84 km over our ~150 m
  level). That cvar is the lever; the light property is not. The light setting still matters on the SM5 fallback
  below, so set both - just know which one is doing the work on which machine.
- **The VSM marking-queue overflow is a PERFORMANCE fallback, not dropped shadow pages.** Read the shader before
  blaming it for a visual bug: on overflow `VirtualShadowMapBuildPerPageDrawCommands.usf:346` takes the
  `bIsSmallJob || bMarkingJobQueueOverflow` branch and marks every page inline in a single-threaded loop. The pages
  still get marked - it just does it the slow way, which is why the engine's own message says *"Performance may be
  affected."* So it is a real thing to fix, but it is not by itself an explanation for flicker.
- **Mac M1 (and any D3D11/SM5 PC) gets neither RT nor VSM, so it runs the legacy CSM path.** `METAL_SM5` sets
  `bSupportsNanite=false` and `bSupportsRayTracing=false` (`Mac/DataDrivenPlatformInfo.ini:54,60`), and
  `UseVirtualShadowMaps` requires `DoesPlatformSupportNanite` (`RenderUtils.cpp:1498-1526`) - so no Nanite means no
  VSM. `METAL_SM6` has both (`:95,104`) but needs macOS 15+ and an Apple8 GPU, i.e. **M2 or later**
  (`MetalRHI.cpp:255-266`); an Intel Mac cannot run the Metal RHI at all (`MetalRHI.cpp:407`). Practical upshot:
  changes made only in cvars reach every machine, changes made only on the sun actor reach only the CSM machines,
  and anything that depends on ray tracing reaches neither an M1 nor a pre-2020 PC GPU.
- **A stochastic shadow term is poison to a posterising toon shader, and RT shadows are stochastic.**
  `MI_AnimeLook` quantises light to `Poster` = 6 steps and splits it on a `smoothstep` band only 12% wide, so a
  shadow term that wobbles by a fraction of a percent is amplified into a whole tone step. Hardware ray-traced
  shadows sample the sun's disc with `SamplesPerPixel` = **1** per light, which is noise by construction; TSR is
  the only thing denoising it. Measured on `Lvl_JumpCut` from a fixed camera: the pavement swung **15-17/255**
  between consecutive frames, and whole bands of it flipped tone. The cure is NOT more samples and NOT a
  different anti-aliasing method - it is to stop making a penumbra at all. `LightSourceAngle` **0.5357 -> 0.05**
  on `Sun_Main` took whole-frame instability from **2.1% -> 0.7%** of pixels and the pavement swing to **3/255**,
  while `SamplesPerPixel` 1 -> 2 changed nothing measurable (4.3% vs 3.9%). It costs no GPU time, it is level
  data rather than a cvar, and because VSM reads `LightSourceAngle` too it is one of the few fixes here that
  reaches a Mac and a pre-2020 PC as well as a 5090.
  **Nov 14 corrections to this entry.** (a) Every percentage above was produced with the invalid two-capture
  harness described in the flicker note below, so treat them as VOID. The `LightSourceAngle` change is still worth
  keeping - it was also confirmed by eye, clean hard shadows where there had been visible stipple - but the
  "2.1% -> 0.7%" figure is not evidence of anything. (b) It did **not** fix the reported border flicker: that
  survives with the look material removed entirely (see the elimination entry below). (c) The material named here
  is the WRONG ONE - see the next bullet.
- **The look material actually in `Lvl_JumpCut` is `MI_AnimeLook_JumpCut`, NOT `MI_AnimeLook`.** They are two
  different assets with different numbers, and `docs/FIRST_BUILD_DESIGN.md:883` has said so all along. Live values
  read off the volume's single blendable: `Boil` **0.30** (not 0.45), `ShadowT` **0.30** (not 0.80), `Smooth`
  **2.0** (not 5.0), `CharSmooth` **3.0** (not 2.5), `InkOpacity` **0.95** (not 0.92). A day of parameter A/Bs was
  run against `MI_AnimeLook` and therefore turned a dial connected to nothing. Any claim in this file, a devlog or
  a ticket that quotes a look parameter without saying `_JumpCut` was measured on the wrong asset - including the
  12%-wide band figure above and the character-blur radius on ticket #72. Check the PostProcessVolume's
  `weightedBlendables` for the real one before touching a parameter.
- **The cel look's `Char*` parameters only touch pixels that write custom depth, and the player is the only
  thing that does.** `BP_Player.CharacterMesh0` has `render_custom_depth = True`; a fresh `SkeletalMeshComponent`
  defaults to `False`. With `MI_AnimeLook_JumpCut`'s `CharLevel` at **0.95**, his light skin and khaki shirt clip
  to near-white, while the **identical mesh spawned as a plain `SkeletalMeshActor` one metre away, in the same
  frame and the same light, keeps its eyes and its khaki shirt** (`docs/media/2026-11-14-player-wears-cafewalker-v2.jpg`).
  So: before blaming a character's art or its texture for washing out, **spawn the same mesh as a control**. That
  one screenshot is what separates "the bake is wrong" from "#72 is doing this", and it costs a minute.
- **Do not "fix" toon flicker by turning off temporal anti-aliasing - it makes it much worse.** The tempting
  reasoning is that TSR blends a posterised image and smears the bands; that part is true. But the post-process
  material runs at `BL_SceneColorBeforeDOF`, which is **before** the temporal upscaler
  (`PostProcessing.cpp:962` vs the upscaler ~line 1110), so TSR is also the denoiser for the ray-traced shadows.
  Measured: FXAA and SMAA both removed the pavement band flip (17/255 -> 1-2/255) but raised edge instability
  from 6.9% to **11-13%** and left the shadow penumbrae as raw stipple. Fix the noise at the source instead.
  **Nov 14: those percentages came from the invalid two-capture harness below and are void**, and the reasoning
  was separately tested in a real playtest - `r.AntiAliasingMethod 2` (FXAA) did **not** remove the reported border
  flicker. The advice "do not reach for an AA change first" survives; the measurements do not.
- **`Boil` is a deliberate feature, not the flicker.** `Boil` (`MI_AnimeLook_JumpCut`: **0.30** px at `BoilFps` 8;
  the `MI_AnimeLook` copy says 0.45) wobbles the ink-line sample UVs on purpose - "drawn on threes". Do not spend
  art time on it when hunting a flicker. **Nov 14: the "~13% of the edge instability (7.9% -> 6.9%)" figure this
  entry used to carry is void twice over** - it came from the invalid two-capture harness, and it was measured on
  `MI_AnimeLook`, which is not in the level. The conclusion stands; the number does not.
- **To find a flicker, DUMP REAL GAMEPLAY FRAMES - do NOT diff two viewport captures.** `r.DumpingMovie N` in the
  PIE console writes N lossless PNGs to `Saved/Screenshots/WindowsEditor/` and counts itself down
  (`ConsoleManager.cpp:3792`, `UnrealClient.cpp:285-288`), so there is nothing to remember to switch off. 300 frames
  is about 1.1 GB. It is `ECVF_Cheat` (fine in PIE, not in a shipping build) and it suppresses on-screen debug text
  while it runs (`UnrealEngine.cpp:13630`), so the red VSM banner will not appear in the frames.
  **Nov 14: the two-capture method this entry used to describe is INVALID and cost a day of work.** Passing
  `captureTransform` to `CaptureViewport` renders a *fresh scene view with no TSR history*, so every frame you get
  back is frame one of the temporal upscaler. It manufactures its own noise: it reported 36-51% edge instability on
  a scene whose true figure is 1.7%, and five A/B arms (`Boil` 0, ink lines off, the whole look bypassed) all came
  back at 32-51% regardless - the signature of a broken instrument, not a scene property. **Any flicker number in
  this file, in a devlog or on a ticket that was produced that way is void.**
  Even done correctly (`captureTransform: null`, see below), the editor viewport cannot reproduce a motion artifact:
  TSR fully reconverges in the latency between the camera move and the capture, so the editor measured 1.7-2.2% on
  a scene where a PIE dump of the same walk measured 28-85% frame to frame. If it only happens while the player
  moves, you need the dump. Auto-exposure settling after a camera turn changes half the picture too - that is a
  drift, not a flicker.
  Decoding the dump: this machine has **no numpy and no Pillow**, and pure-Python PNG decoding runs ~20 s/frame (100
  minutes for 300). Build a decoder against GDI+ with the `csc.exe` that ships under `C:/Windows/Microsoft.NET/`
  instead - 0.07 s/frame, and nothing gets installed on the artist's machine.
- **The border flicker on ticket #67 is NOT the cel shader, the lighting, or the upscaler - all of that is
  eliminated, by test, on real hardware.** Nov 14 playtest on GAMESTATION (RTX 5090), reported each time as "still
  there": `r.ScreenPercentage 100` (so it is not the 62.5% default upscale - and note a manual value DOES beat the
  PIE override, `LegacyScreenPercentageDriver.cpp:216`); `r.AntiAliasingMethod 2` (not TSR ghosting);
  `r.PostProcessing.DisableMaterials 1` (not the look material at all - the volume holds exactly ONE blendable, so
  that command removes the cel shader and nothing else, `PostProcessMaterial.cpp:1008-1014`); and finally
  `viewmode unlit`, which strips lighting, shadows, GI and reflections - **and it still flickered.** That kills ink
  lines, the light band, `Boil`, screen percentage, temporal AA, RT shadows, VSM and Lumen in one go. What is left
  is geometry. **Nov 14: found, and it was NOT either of the two suspects this entry used to name.**
  `City_CafeSign` and `City_CafeAwning` are **122 cm apart** at their nearest parallel overlapping faces (the
  awning canvas passes THROUGH the sign's post - cosmetic, not a depth tie), and the road pieces 1 cm over the
  floor have a depth margin of at least **37,000x** anywhere a player stands. Raising them to 2-3 cm or making
  them decals - the fix this ticket recommended for a day - would have changed nothing.
  **The tie is INSIDE the meshes:** `Art/Blender/jumpcut_city_kit.py` drew a detail flush with the surface it
  sits on (the sign's lit `MS_CitySignA` quads exactly on its own `MS_CityTrim` casing faces; the shopfront
  fascia's street face exactly on the `MS_CafeWall` plane; the pastry case's glass exactly on the trim posts).
  Two faces of **different materials on one plane facing the same way** tie in the depth test, and the tie
  breaks differently every frame the camera moves - a shimmering border under motion, steady when still.
  41 of 85 kit models carried it, 2.66 m2 of tied face area, the three worst being exactly the three objects
  the playtester circled. Cure: `stand_proud()` in the kit's `finish()` lifts the smaller face **0.4 cm** along
  its normal (tied area 2,658,947 -> 9,294 cm2); same-material overlaps are left alone.
  **A bounding box proves volumes overlap, not that faces are coplanar** - that is why this hid for a day.
  Full evidence and the per-frame dump analysis are on
  https://github.com/Waffle-Widgets/jump-cut/issues/67 - read it before re-running anything above.
- **`unreal_city_mesh_audit.py` CANNOT see a vertex-only kit change, and will tell you the level is in step
  while every patched mesh on screen is the old one.** It compares **triangle counts**; `stand_proud` changes
  no triangle, no vertex count and no bounds the audit reads, and `city_models.json` comes out **byte-identical**
  (md5 `ac639be6211f07fbb295358063cce647` committed, base rebuild and patched rebuild alike). Force the
  re-import **by name** with `py <repo>/tools/unreal_city_reimport_by_name.py apply @<file of names>`, which
  records each mesh's material slot list **in order**, collision, Nanite, LODs and triangle count, re-imports,
  reads them back and refuses to save if any of it moved. Slot ORDER is the invariant that matters: every
  `City_*` actor carries per-component material **overrides indexed by slot INDEX, not by name**, so a
  re-import that reordered slots would swap the cafe shell's brick and glass while every triangle count
  still matched. Its "NO-OP: bounds unchanged but Blender says this mesh grew" rule fires on a mesh you
  already re-imported in a previous run - withhold `/tmp/jc67_expect.json` for that pass rather than
  weakening any of the other guards.
- **That same tool's guard INVERTS for a pass that rethinks geometry rather than nudging it, and it will
  refuse to save all of your work if you do not tell it so.** The sub-pixel pass (grooves instead of ribs,
  an inlay instead of a proud slab, three wide gully bars instead of seven thin ones) **changes triangle
  counts on purpose** while leaving every bounding box identical to the millimetre so nothing moves. So the
  `TRIS a -> b` rule fires on exactly the thing you intended, and bounds can no longer prove the import
  took. Write an **expected-tris table** to `/tmp/jc67_tris.json` (or point `$JC67_TRIS` at one) mapping
  model name to the count Blender built: the tool then requires the count to equal that number *and* to
  differ from what was in the level, which is stricter proof than bounds ever were. A model with no entry
  keeps the strict behaviour. An unreadable table is fatal rather than a silent fallback, because strict
  fallback would fail every model for the one reason you expect and read as "the import broke".
- **A 2 px floor, and ground detail is foreshortened to about a third.** PIE renders 1709 px wide at 90 deg;
  a feature narrower than ~2 screen pixels at the distance the player sees it will boil no matter what the
  renderer does, and a repeating one narrower than the sampling limit will crawl as a moire. Measure a new
  detail in PIXELS AT ITS VIEWING DISTANCE before adding it - `Art/Blender/subpixel_measure.py` does this
  against the built geometry, and `Art/Blender/subpixel_coverage.py` checks an inlay tiles exactly. Four playtest complaints and one nobody had named all measured 0.60-1.62 px.
- **`stand_proud()` trades a z-fight for a shimmer, so prefer an INLAY where the detail is flat.** Lifting
  coplanar detail 0.4 cm along its normal (PR #111) genuinely cured the depth tie, but 0.4-0.8 cm is itself
  sub-pixel at normal viewing distances. Where the detail is flat colour on a flat parent, punch the
  parent's face out and tile it around the detail so both share one plane: no relief to alias, no overlap
  to z-fight, nothing for the outline pass to find. `build_cafe_chalkboard` is the worked example. **Verify
  a tiling by rasterising the plane** and requiring coverage of exactly one everywhere - a missing strip is
  a hole straight through the prop, and a doubled one is a brand new coplanar tie.
- **TSR is already at maximum anti-flicker in this project, so there is no cvar left to try.** The log shows
  `AntiAliasingQuality@3` applying `r.TSR.History.ScreenPercentage:200` - documented in
  `TemporalSuperResolution.cpp:53-61` as the Nyquist-sufficient rate and the highest supported value - plus
  `ShadingRejection.Flickering:1` and `Resurrection:1`. And **every city mesh is LOD count 1 with Nanite
  off**, so "LOD popping" is impossible; turning either on would delete the thin parts that are aliasing,
  which is why `jumpcut_city_place.py:309-316` disables Nanite deliberately.
- **A character that floats only while it moves: check Root Motion Root Lock before the retarget.** Meshy's Smart
  Rig keeps its root bone at pelvis height in the *reference pose*; retargeted clips animate it on the floor. A
  clip with root motion on locks its root to `RefPose` by default, so the mob boss rose 87.26 x 1.2921 = 113 cm
  whenever he walked or swung and stood correctly when idle. Set `root_motion_root_lock = AnimFirstFrame` on every
  root-motion clip of such a rig (`tools/unreal_boss_root_lock.py`); never `Zero`, which wipes the root's up-axis
  turn. And **evaluate a clip the way the game does**: `AnimPoseEvaluationOptions.extract_root_motion = True`.
  Without it every clip read 0 and looked innocent.
  **Nov 14: the same defect was still on the player and the goons a day later, and two things hid it.** (1) That
  tool's docstring said "the player's CafeWalker clips read 0" - true of the `_CW` clips (our Blender rig, root on
  the floor), false of the `_CWM` clips the anim blueprint actually plays, which read 90.6. One sentence covering
  two clip sets. (2) Its folder list was hand-written and omitted `StreetGoon/Loco`, so no run could ever find the
  goon's 16 locomotion clips. It now scans `/Game/Game/Imported` recursively - **never hand-list folders in a
  sweep tool**, because it reports complete success over whatever subset it was handed. And a bold note in a doc
  saying "the goon needs this too" is not a fix: do it in the same pass or file a ticket.
- **`force_root_lock` + `root_motion_root_lock = REF_POSE` is the whole bug, and FOUR separate
  checks say the clip is fine (Nov 15).** A clip with that pair has its root pinned to the
  SKELETON'S reference pose, which on every Meshy Smart Rig here is pelvis height - so the mesh is
  drawn ~90 cm up for as long as it plays. `7ef73e1` moved the locomotion clips to
  `ANIM_FIRST_FRAME` and missed `MM_Jump/Fall_Loop/Land` for the player (`_CWM`) and the goons
  (`_SGN`), which is why the float only showed while airborne. What makes it hide: the clips' own
  root tracks read **0.0** at every sample; they all DO carry a `bone_000` track (so it is not a
  missing-track fallback); none is marked additive; and the Jump state really is wired to
  `MM_Jump_CWM`. All four are true and all four are irrelevant - the lock is applied after the clip
  is sampled. Read the two properties, not the clip. `tools/b1y_rootlock.py` reports and fixes.
  **Do not sweep this across the project**: 85 clips match the pattern and 60 are Epic's own
  mannequin clips, where REF_POSE is CORRECT because the mannequin's reference pose has its root on
  the floor. Only Meshy rigs are affected; confirm which clips are live by reading each anim
  blueprint's asset references.
- **This project's own unlock path puts the player into MOVE_Falling, so the bug above fires at the
  start of every game.** `PlayerRefreshMoveLock` releases a lock with
  `SetMovementMode(MOVE_Falling)`, and the title screen's lock is released on the first tick - so
  beat 1 opened with the character 90 cm in the air for 0.9 s. If you are hunting something that
  only happens "at the start", check what the first tick's state transition does before looking at
  the cinematic.
- **An INTACT Geometry Collection is not the same surface as the static mesh it was cut from
  (Nov 15, "the car is flickering badly").** Measured on the wreck: `B1_Cafe_CrashCar_GC` and
  `City_CafeCrashCar` stand at the same transform with the same geometry, and the collection's
  bounds come back **0.05-0.1 cm LARGER** in y and z. That is fracture pieces inflated slightly
  outward, so along every cut line across the whole body two pieces overlap by about a
  millimetre - a depth tie with real area, spread over the entire object, which is the #67
  mechanism at prop scale. The static mesh has no cut lines at all and is drawn exactly like
  every other city prop. **So draw the static mesh until the thing actually breaks**, and show
  the collection on the frame you break it: beat 1 does this in `CineExplFire`, which hides
  `CineRealCar` (the static) and shows `ExplCarGC` before applying the strain. The two bounds
  agree to 0.1 cm, so the swap is invisible.
- **A collection's ROOT PROXY is a red herring unless a custom renderer is set.** `GC_CrashCar`
  carries `RootProxyData.ProxyMeshes = (SM_CrashCar)` with **empty** override materials, which
  reads exactly like "the intact car draws the grey `MS_*` import placeholders". It does not:
  `GeometryCollectionComponent.cpp:6540` only consults the root proxy inside
  `RefreshCustomRenderer`, and every `GC_*` component in this level has
  `custom_renderer_type = None`. Check that property before spending time on the proxy.
- **In this map a BOUNDING-BOX test for "is this floor clear" returns nothing useful.**
  `City_CafeShell`'s box covers the whole room, `B1_Cine_ExplCam`'s covers 20 m, `Player_Main`
  and `Coworker_Cafe` cover most of the street and every `Marker_*` is a 5 m sphere - so a
  clearance search over bounds found **zero** clear spots anywhere in the cafe. Use real traces:
  a downward line trace for the floor height, a capsule at the point for "can someone stand
  here", twelve horizontal spokes for clearance and a capsule sweep for "can someone walk here".
  `tools/b1w_spot.py` is the worked example, and it is what found that beat 1's driver was being
  thrown onto the **counter top** (floor height 150 cm at the old landing spot, not 0).
- **Moving a range-gated actor closer to the player can delete a whole beat, silently.**
  `BP_CrashDriver.DriverCanTouch` is a plain XY distance against `TouchRange`, and the player
  starts at the origin. Landing the body at `(-200, -60)` put it 209 cm away against a range of
  220, so Freeze Frame was granted on the first frame after the cinematic - measured in PIE, the
  objective jumped straight to 3 with the player still standing at `(0, 0, 94)`. Nothing errors
  and the capture looks fine. After moving any actor a beat triggers off, read the objective
  state back with the player where he really starts.
- **A Sequencer SPAWNABLE WITH NO SPAWN KEYS IS SPAWNED FOR THE WHOLE SEQUENCE (Nov 15).**
  `add_spawnable_from_instance` creates a `MovieSceneSpawnTrack` whose section has **zero keys**,
  and that means on from the first frame to the last. Beat 1's flying car therefore sat inside
  the real wreck from 6.2 s to 11.0 s (a whole-body depth tie, the #67 mechanism at car scale)
  and the thrown body stood beside the real ragdoll for four and a half seconds ("seeing two
  driver models"). **Check the spawn track before anything else when a cinematic shows two of
  something**, and read the key COUNT - the track exists, which is what makes it look wired.
  `b1_opening_cine.key_spawn` writes True@0 and False@<hand-off frame>; reveal the real actor one
  frame BEFORE the despawn, never after, so you get one frame of identical overlap rather than one
  frame of nothing.
- **A camera hand-off is POSITION, ROTATION *and* FIELD OF VIEW, and the FOV is the one nobody
  checks (Nov 15).** Beat 1's last cut ended 194 cm from where the player camera sits *and* on a
  26 mm lens, which on this project's 23.76 mm sensor is **49.1 deg** against
  `BP_Player.FollowCamera`'s **90**. Convert before comparing: `hfov = 2*atan(sensor_w/2/focal)`,
  and the focal that matches 90 deg here is **11.88 mm**. A CineCameraActor also constrains its
  view to 16:9 by default and a `CameraComponent` does not, so turn `constrain_aspect_ratio` off
  on the cut that has to match - at a cut, where it cannot be seen.
- **MEASURE the player camera's pose, do not compute it from the spring arm.** The arm does a
  collision probe and can shorten itself, and the pawn's resting z is not floor + half height
  (94.15, not 92). `tools/b1v_cam.py prep|set|read` does it in PIE: set the control rotation in
  one MCP call and read `FollowCamera` + the camera manager in the NEXT one, so real ticks happen
  in between.
- **A Level Sequence with a camera cut track reverts the view the frame it stops, so there is
  nothing to blend FROM.** Park a plain CameraActor at the cut's final pose with the matching FOV
  (`B1_Cine_HandCam`), then: stop the player, `SetViewTargetWithBlend(handcam, 0.0)` - which
  changes nothing on screen - then `SetViewTargetWithBlend(pawn, 0.4, EaseInOut)`. And make the
  sequence LONGER than the director's own clock (11.2 vs `CineLength` 11.0) so the director always
  gets to the hand-off first; a sequence finishing on its own schedule is itself a one-frame pop.
- **To turn a character "with animation" when there is no turn-in-place clip, drive the MOVEMENT
  COMPONENT, not `SetActorRotation` (Nov 15).** The anim blueprint is a blend space on
  `GetVelocity`'s XY length, so a set-rotation turn is the idle pose sliding round on the spot.
  Feed `Pawn|Input|AddMovementInput` toward the target yaw and let `orient_rotation_to_movement`
  turn him at his own 500 deg/s. All 38 of the player's `_CWM` clips are idle/walk/jog/attack/hit
  react/death/jump - there is no turn clip to montage.
  **And you do NOT clear `MoveLocked` to do it.** `BP_Player.PlayerRefreshMoveLock` derives
  `MoveLocked` from `InputLocked` every tick, so clearing it is undone next frame - but it only
  acts on the TRANSITION (`if (and locked (not MoveLocked))`), so with `MoveLocked` already true
  it never re-calls `DisableMovement`. Setting the movement mode to `MOVE_Walking` from outside is
  stable, and `InputLocked` stays true so the player's own keys still do nothing. Measured: 31 cm
  of drift over a 172 deg turn at scale 0.30, which the view-target blend absorbs.
- **The hidden grey-box crash-car placeholders `C1_Cafe_Car` and `C1_Cafe_CarCab` used to wall off
  the cafe (Nov 15).** Hidden in game, still colliding, and sticking out past the real wreck, they
  made every spot deeper than x = -460 on the car's +Y side unreachable. Collision is off on both
  now (`tools/b1v_greybox.py`). When a capsule sweep is stopped by something you cannot see, check
  the grey-box layer before the art.
- **You cannot step the director's clock by hand to test anything the MOVEMENT COMPONENT does.**
  `tools/b1z_pie.py open` works precisely because no ticks happen, so `AddMovementInput` would be
  recorded and never applied. Use `StartPIE`'s `warmupSeconds` to let the opening run in real time
  and sample afterwards (`tools/b1v_pie.py sample`).
- **`ALevelSequenceActor` has no `get_sequence_player()` in Python** - the obvious name raises
  `AttributeError`. It is `get_editor_property('sequence_player')`, and that player's
  `get_current_time().time` is an `FFrameTime`, which `round()` refuses.
- **A settled ragdoll's MASS is about 55 cm from its actor origin**, because the body collapses
  out of the head-down pose the throw ends in. The beacon, the touch test and the arc all use the
  actor origin; the thing the player SEES is the bones. Measure bone extents
  (`tools/b1w_land.py`), not the actor location, when deciding whether a body is clear of
  furniture.
- **The kit source FBXs inside `Content/Game/Imported/City/` are STALE and gitignored.** All 48
  of them differ from `Art/Blender/export/City/`, because the #67 re-import (`0f9b13c`) was
  driven by name from the export folder and nothing rewrote the copies under `Content/`. They are
  older than the assets, so the auto-reimport watcher leaves them alone today - but anything that
  touches their mtimes would re-import the pre-`stand_proud` flush geometry over the flicker fix,
  on this machine only. Do not copy a kit FBX into `Content/` to "fix" an import.
- **A Geometry Collection draws the materials its SOURCE FBX came in with, and nobody tells it
  otherwise (Nov 15).** Every `GC_*` in `/Game/Game/Destruction` was drawing `MS_City*` from
  `Imported/City/` - `MaterialInstanceConstant`s of `FBXLegacyPhongSurfaceMaterial` with
  DiffuseColor 0.8, i.e. Unreal's flat grey import placeholder. The real look materials are
  `M_City*` under `Materials/City/`, and every placed `City_*` STATIC actor overrides to them per
  slot (measured: **0** static actors draw an `MS_` directly), so only the things that shatter were
  grey. Fix it on the collection ASSET's `materials` array, slot for slot, which fixes every actor
  using it at once - 13 actors here. `tools/b1y_fix3.py`.

- **"The capsule lifts" and "the mesh lifts" look identical in a screenshot and need opposite fixes.** Log
  `pawn.get_actor_location().z` beside the bone world heights. On the float bug `actor_z` never moved (94.15 for
  four seconds) while every bone rose 90.58 cm, which ruled out root-motion translation in one reading and sent
  the fix to `RootMotionRootLock` instead. A root lock moves the skeleton; it never moves the capsule.
- **The reference pose is a visible failure mode on a Meshy rig, not a harmless fallback.** An anim graph that
  outputs the ref pose for a few frames is invisible on the mannequin (root at 0) and a 90 cm float in an A-pose
  on a Smart Rig. If a character hangs in the air *after* an action rather than during it, suspect a state with no
  reachable pose and measure the bone **spread**: the ref pose has a characteristic one (162.0 for CafeWalker).
- **`unreal.HitResult` is opaque in 5.8:** no `.distance`, every property "protected and cannot be read", and
  `SystemLibrary.break_hit_result` does not exist. Use `to_tuple()` / `to_dict()`, or get the distance from the
  MCP's `SceneTools.trace_world`, which just returns a number.
- **Start a downward trace BELOW anything overhead.** Tracing down from z=300 through a ceiling that occupies
  215-350 begins inside the collider and reported a floor where there was a gap - it hid all three gaps at once.
- **A viewport capture can be of a different world than Python is editing.** The editor sat on a scratch
  `/Temp/Untitled_1` while `get_editor_world()` answered `Lvl_JumpCut`, so three screenshots showed an empty
  landscape while the work was fine. Check `SceneTools.get_current_level` **and** `GetVisibleActors` (it prints
  the world in each actor's path) before believing a picture, and `SceneTools.load_level` to fix it.
- **`SlateInspector.Type` APPENDS to a textbox, it does not replace.** A leftover `stat fps` turned the next
  command into `stat fpspy /path/to/script.py`, which failed silently. Clear the box with BackSpace presses
  first. It also returns **false** for text containing double quotes - pass an unquoted path.
- **Clear the console box with ONE BackSpace, not Cmd+A.** `SlateInspector.Type` appends, and the box
  keeps a leftover `/` between commands, so the next command runs as `py /py /path/...` and fails with
  "Could not load Python file". `Click` then `Cmd+A` then `Type` does **not** replace the selection -
  it still appends. A single `PressKey("BackSpace")` before each `Type` is what works. The failure is
  quiet from the caller's side: `Type` returns **true** either way, and the script simply never runs,
  so check the thing the script was supposed to write (a file's mtime), never the return value.
- **A mesh fixed in the kit is NOT a mesh fixed in the game, and nothing anywhere says so.** Two de-blocking
  passes were built, committed, reviewed and merged on Sat Nov 14 and touched **zero `.uasset` files**, so
  14 meshes - all six chamfered cafe pieces and all eight building shells - were still the old boxes on
  screen. Run **`py <repo>/tools/unreal_city_mesh_audit.py`** after any kit change: it compares each
  model's triangle count in `city_models.json` against the Unreal asset and names what is stale.
  `reimport` mode fixes them. A kit commit that changes geometry MUST also carry the re-imported `.uasset`.
- **The `Check Out Assets` modal also fires from the AUTO-IMPORT WATCHER, not just an explicit import** -
  so it can appear minutes after you copied an FBX into `Content/`, with no command of yours running, and
  it freezes the game thread and the MCP with it. It fires even on a file you have already made writable.
  **The screen cannot be photographed on this machine** (a `CopyFromScreen` of the dialog comes back pure
  black - the session is not rendering to a visible desktop), so find it by enumerating the editor's
  window titles. `chat-tools/dismiss_modal.ps1` does that and posts ESC, which is Cancel. **Cancel is
  always correct: this repo uses git LFS, not Unreal source control.**
- **Qualify the "a timed-out MCP call still ran" note.** That holds for a call the editor *received*. A
  `FillForm`/`PressKey` that times out because a modal is blocking the game thread never reaches it at all,
  and the console box keeps whatever was in it. The editor's own `Cmd:` log line is the only reliable
  evidence that a script ran - check it before believing either outcome.
- **A component's `override_materials` BEATS the mesh asset's own material slot, and nothing warns you.**
  `BP_Goon.CharacterMesh0` carried `override_materials = [M_Goon]` - a flat skin-tone placeholder from the
  grey-box build - so the goons rendered as naked orange silhouettes while their correct 2048 texture was
  bound, sampled by 100%-occupancy UVs, and discarded. The mesh, the texture, the UVs and the import material
  all measured perfect. **Check the override before blaming the asset.** And put a character's material on the
  SkeletalMesh ASSET slot, not on an actor: goons are spawned at runtime by `BP_GoonSpawner`, so there is no
  placed actor to override. `tools/unreal_char_materials.py measure` prints every character's slot and what
  parents it.
- **Every field of a `HitResult` is PROTECTED in UE 5.8 Python.** `hit.get_editor_property('location')` raises
  *"Property 'Location' ... is protected and cannot be read"*, `'hit_actor'` raises *"Failed to find
  property"*, and there is **no** `GameplayStatics.break_hit_result` in the Python API. The only route that
  works is **`hit.to_dict()`**, which returns all 18 fields including `location`, `hit_actor`,
  `hit_component` and `initial_overlap`. `to_tuple()` works too (location is [4], hit_actor [9]).
- **A capsule sweep that starts inside geometry returns `initial_overlap` and a stop at the START point**,
  which reads exactly like "blocked immediately" if you only look at the hit location. Read `initial_overlap`
  from `to_dict()` and start the sweep at `floor_z + half_height + 2`, not at a round number.
- **Never call `save_dirty_packages` - save your own packages by path.** It saves EVERY dirty package in
  the project. With another lane's four read-only Blueprints dirty, that save failed, left `.tmp` files
  in `Saved/`, and the editor stopped answering the MCP for ten minutes. Collect the assets you touched
  (`list_assets(folder)` -> `load_asset` -> `get_outermost`) and pass those to `save_packages`.
- **You cannot save a level actor through the MCP in this map, and three things lie about it.**
  `Lvl_JumpCut` is One File Per Actor, so each actor owns a package under `Content/__ExternalActors__/`.
  `SceneTools.save_actor` and `AssetTools.save_assets` both resolve that package and then save it as a
  *registry asset*, which it is not: every actor fails with `Asset does not exist:
  /Game/__ExternalActors__/...` (useful side effect - the error names the package path). The toolbar's
  **Save Current Level** returns **true** and writes nothing. And `SceneTools.can_edit` returns **true**
  for an actor whose package is read-only under LFS, where the save would fail silently anyway. Use
  `py <repo>/tools/jc_save_actors.py <label> ...` through the console box - real `unreal`,
  `save_packages([a.get_outermost()], False)` on only the actors you name - then confirm with
  `git status`. If you need to know which five packages are dirty, the autosave names them in the log.
- **The editor can open onto a `Check Out Assets` modal that freezes the MCP.** The log stops
  mid-startup and the MCP accepts connections but never answers. It is a Slate window with no Win32
  children, so there is no button to click: find it by title from PowerShell and `PostMessage` **WM_CLOSE**
  (0x0010) to cancel. Cancel is correct - we coordinate with `git lfs lock` on named files, not with
  Unreal source control, so a blanket check-out at startup is never what we want.
- **30 assets re-import themselves on every editor open, and two of them used to undo real work.**
  23 sounds and 7 UI textures keep their source file committed beside them inside `Content/`, and
  `bMonitorContentDirectories=True`, so a `git checkout` touching those mtimes makes the watcher
  re-import all 30 (this is most of the "35 Unsaved" you see on a fresh open). That is harmless only
  while the source MATCHES: `Content/Game/UI/Textures/T_UI_Title.png` and `T_UI_ToBeContinued.png` were
  the old rejected pictures, so every launch silently reverted those assets to them. If you update a
  picture in `Art/UI/`, update the copy in `Content/` in the same commit, or the watcher will undo you.
- **`jumpcut_city_place.py add` matches by ACTOR LABEL, so renumbering the layout makes duplicates.**
  Inserting `SM_CafeRegister` at cafe index 1 shifted every row after it, so only 7 of 15 cafe labels
  still matched: `add` would have skipped the counter (leaving it unmoved - the whole point of the
  change) and spawned **8** duplicate shelves, tables and chairs. Before running `add`, compare the
  layout to the level **by position**, not by label; the geometry is usually right and only the labels
  have drifted. Fix the labels first, then `add` is safe.
- **`IKRetargetBatchOperation.duplicate_and_retarget` returns package names you cannot save by.** On a
  re-run into a folder that already holds `_SG` assets it makes `_SG1` copies and renames them, and the
  names it hands back are the pre-rename ones - so saving by them saves nothing, and the real assets are
  discarded later. A folder of 42 retargeted clips came back as **3** on disk twice before this was
  understood. Retarget, then save the FOLDER by path, in the same script run.
  **And that is not enough on its own: the same run must not call it twice into one folder.** The street
  goon's run retargeted the clips, then retargeted the anim blueprint into the same folder, logged
  `saved 43 packages ok True`, and left **21** assets on disk - every `MF_*`, the blend space and the
  anim blueprint itself were gone. Do one batch per folder, into a folder that holds nothing with your
  suffix yet, and afterwards read the folder back off the asset registry and count. Never report the
  batch call's own return value as the result (`tools/unreal_goon_abp.py`).
- **Unreal is left-handed, so a character's right is `up x forward`.** `tools/unreal_retarget_meshy.py`
  shortcut that to the sign of a bone's X against the hip's and had it **inverted**: a rig facing +Y has
  its right side at **-X**. Both Meshy characters face +Y, so every arm and leg chain was labelled with
  the wrong side and the mannequin's right-arm clip played on the character's left - and because
  `ALIGN=arms` calls `auto_align_bones(CHAIN_TO_CHAIN)`, each arm's retarget pose was rotated onto the
  **other arm's**, which is what turns a mirror into limbs folded across the body ("the arms look
  mangled"). **A left/right swap passes every internal check there is:** chain names stay unique, all 19
  map, the batch runs, and the assets read back as exactly what the script meant to build. Verify a
  geometric rule against a rig whose answer you already know - `check_side_rule()` runs it on the
  mannequin's own `_l`/`_r` bone names before every retarget and refuses if it disagrees.
  **And a symmetric clip hides it:** the goons' walk was signed off as correct the day before and was,
  because a walk with the legs swapped is a walk phase-shifted. Judge a retarget on an asymmetric clip.
- **A Meshy target rig has no finger chains unless you build them**, so all ten of the mannequin's are
  dropped and the hands hold their reference pose in every clip - a splayed claw on a body built from an
  A-pose sheet. `finger_chains()` names the five branches off each hand (thumb = the branch that leaves
  the palm sideways soonest) the way Epic's auto definition names the mannequin's.
- **A mismatched anim class is SILENT, and it looks exactly like a finished job.** `BP_Goon` wore
  `SK_StreetGoon` (76-bone Meshy Smart Rig) with Epic's `ABP_Unarmed` assigned - an anim blueprint whose
  target skeleton is the *mannequin's*. No warning, no error, no log line: the mesh reads as correctly
  assigned, every montage variable reads as correctly assigned, and the character stands in his reference
  pose and never moves. **Reading the Blueprint back cannot catch this.** The only check that does is
  reading the LIVE anim instance's class off a spawned actor in PIE
  (`comp.get_anim_instance().get_class().get_name()` - `tools/goon_body_test.py`).
- **The asset registry does not know about a folder a PREVIOUS editor session created.** It is on disk and
  the Content Browser shows it, but its paths are not in the registry's index, so `does_asset_exist` and a
  registry `ARFilter` both answer "empty" for assets that are plainly there - which silently defeated an
  idempotence guard and re-ran a batch retarget. Call
  `AssetRegistry.scan_paths_synchronous([folder], True)` before trusting either.
- **`SlateInspector.FillForm` with `fieldType: textbox` REPLACES the box; `Type` appends.** This is the fix
  for the leftover-`/` console trap below, which the one-`BackSpace` cure does not reliably solve. Use
  `FillForm` to set the command, then `PressKey("Enter")`, then confirm the `Cmd:` line in the log says
  what you meant - two commands came out as `py /py /Users/...` and failed silently before this.
- **An unresponsive editor is not necessarily frozen.** Compiling a freshly retargeted anim blueprint
  stopped the game thread for **383 seconds** with nothing in the log, which looks identical to the
  modal-dialog freeze, and recovered on its own. Wait before assuming a dialog and force-closing anything -
  but tell the two apart by the log, not by `%CPU` (see the note below).
- **`.wav` auto-imports in this project; `.png` does NOT.** `Config/DefaultEngine.ini` sets Interchange's
  `bShowImportDialog=False`, so a `.wav` or `.fbx` dropped into `Content/` imports itself within seconds
  (23 sounds landed that way). A dropped `.png` does **nothing at all** - it needs an explicit
  `AssetImportTask` with `automated = True` (`tools/unreal_import_ui_fx.py`).
- **Never copy an image into the DESTINATION `Content/` folder before importing it.** Importing a file that
  is already inside `Content/` makes the task return an EMPTY `imported_object_paths` while still creating
  the texture in memory - an unsaved success that reads as a clean failure. Nine FX sheets imported fine from
  `Art/FX`; seven UI textures "failed" purely because they had been copied into `Content/Game/UI/Textures/`
  first. Always import from `Art/`.
- **`does_asset_exist` answers False for an imported-but-unsaved asset.** It is the wrong test for "is this
  already here" and it silently defeats an idempotence guard. Use `load_asset` (and see the asset-registry
  scan note above for the other half of this problem).
- **Taking a source file back OUT of `Content/` wakes the auto-reimport watcher.** It logs
  `AssetReimport: Attempting to delete <name> (its source file has been removed)` and then churns at high
  CPU working through the change, which stops the MCP answering for minutes. Put the file back, or better,
  leave the source beside its asset - which is exactly what `Content/Game/Audio` has always done with its
  `.wav` files. (It did NOT raise a dialog and nothing was deleted; see the next note, which is how that
  was established after guessing wrong.)
- **Use `sample <pid>` to tell a BUSY editor from a BLOCKED one. `%CPU` cannot.** A stack in
  `FAutoReimportManager::Tick` or a compile is a game thread that is still ticking and will recover; a
  stack in `RunModal` is a dialog waiting for a person. Both can show a silent log and high CPU - a
  383-second anim-blueprint compile sat at ~70%, the reimport churn at ~185%, and neither was a modal.
  On a Mac `screencapture` needs screen-recording permission and `osascript` needs assistive access, so
  neither can be used to look at the screen; `sample` needs nothing.
- **An MCP call that times out on the client still RAN in the editor.** A `FillForm` that "failed" had
  already put its text in the console box, so the next one appended and the command came out as the path
  twice (`py <path><path>`) and silently did nothing. Recipe: `FillForm` with `""` to clear, `FillForm` the
  command, `PressKey("Enter")`, then read the `Cmd:` line in the log to confirm what actually ran.
- **`AssetTools.write_file` only accepts `.csv/.html/.json/.md/.py/.txt` and only under the project roots**, so
  write a capture's base64 to a `.txt` under `Saved/` and decode it outside the editor.
- The frog's `CameraBoom` has Inherit Yaw off (that keeps the camera north while the frog turns). A spring arm
  with Inherit Yaw off ignores its world rotation's yaw and uses its *relative* yaw, so turn it with
  `SetRelativeRotation`, not `SetWorldRotation`. Debug camera problems with `CaptureEditorImage` during PIE: the
  variables can all look right while the picture shows the camera never moved.
- Measure frame time with the console commands `startfpschart` / `stopfpschart` (type them into the console box with the
  Slate inspector, read the result from the log). The `stat unit` overlay never shows in `CaptureEditorImage`. If it reads
  3 fps, the editor is throttling in the background: `bThrottleCPUWhenNotForeground` must be false.
- `TextureTools.import_file` / `StaticMeshTools.import_file` never overwrite: delete the old asset first, or use a new name.
  Deleting leaves every referencer pointing at nothing: run `AssetTools.get_referencers` first and re-point each one
  afterwards. `M_CarMasked` uses the coupe textures as its parameter defaults, so after a texture re-import its
  three `TextureSampleParameter2D` nodes need the new textures set (`ObjectTools.set_properties` `Texture`), then
  `MaterialTools.recompile` and save, or every car on it turns default grey ("Found NULL, requires Texture2D").
- Import 4096 textures one per call. Three in one script crashed the editor with a plain out-of-memory: each build
  needs about 1 GB, and a Blender that has run a long session can hold 100 GB of committed memory (undo history)
  that counts against the same limit. Save and restart Blender before heavy Unreal work; its MCP add-on autostarts.
- To get the real game lighting in a capture, `StartPIE` in Simulate mode, click the editor's Pause button via the Slate
  inspector, then `CaptureViewport` with a camera transform; `CaptureEditorImage` shows the game camera as the player sees it.
- Save captures without pulling the picture through the chat: inside `execute_tool_script`, write the capture's base64
  `data` to a `.txt` under `Saved/` with `AssetTools.write_file`, then decode it in PowerShell. `CaptureViewport` needs
  both `captureTransform` and `annotations` to be PRESENT - but pass them as **`null`**, not as values:
  `captureTransform: null` plus `annotations: null` uses the viewport's own camera *with its accumulated TSR history*,
  which is the only form that measures anything real. Omitting either key errors out, which is how this entry came to
  say it "needs a camera transform" - and that wording is what produced the invalid flicker measurements described in
  the flicker note above. Supply a transform only to frame a shot you intend to look at, never to one you intend to
  measure. `CaptureEditorImage` comes back 1280 px wide.
- Check the game's scale before comparing art with it. The practice city is built at **0.405**: the pedestrians' Man and
  Dog meshes are scaled 0.405 and the car meshes are modelled small (the RAV4 is 186 cm long).

- **Never click the editor's "N Unsaved" button** through the Slate inspector: it opens a modal Save Content window
  that freezes the MCP. Save with `AssetTools.save_assets`. (Escape it: find the window from PowerShell and send Enter.)
- `AssetTools.delete` on a **folder** also deletes the source files on disk inside it (a texture's `.png`).
- `ObjectTools.set_properties` on a placed actor doesn't mark the level as changed, so saving writes nothing. Re-set the
  actor's full transform afterwards, then save and check `git status`.
- To test untested `.uasset` work on another PC, push it to a branch (`<name>/<topic>`), play it there, then merge.
- **A maker or tester computer can look at the level without saving anything:** `tools/asset_walkthrough.py`
  lists every placed actor's mesh and materials, what each Blueprint and widget references (asset registry), and
  takes pictures along the route. Launch it with `-ExecCmds="py <script>"`, not `-ExecutePythonScript`: that
  flag quits the editor the moment the script returns, before a single frame is drawn, so no screenshot is
  ever taken. The script counts editor ticks itself and calls `quit_editor()`. Restore `DefaultEngine.ini`
  afterwards (opening the editor writes a generated token into it).
- **Importing a rigged FBX into Blender applies the pose it was exported in** (ours: frame 0 of Walk) to the
  pose bones, even with `use_anim=False`. Reset every pose bone before measuring or posing, or the work is
  built on a walking stride (`Art/Blender/pose_clip.py`). `ignore_leaf_bones=True` also drops real end bones
  (the head, the fingertips) on rigs exported without leaf bones.

- More Unreal patterns live in the skills: keyboard/gamepad input without wiring, effects without Niagara and
  light levels (`unreal-blueprint`), Meshy rigging and prop baking (`asset-import`), full-size game-camera shots with
  `HighResShot` (`playtest-capture`), local reference pictures with `tools/gen_images.py` (`trellis-model`).
- **Real particle effects (Niagara), learned on the Deep Archive Mega Beam (Nov 10):** see the `niagara-fx` skill. In short:
  solid shapes with outlines read at the game camera, painted texture doesn't; mock up 2-3 options in Blender before
  building; use an unlit Masked material (Niagara's default adds light, so red over white turns white); make ribbons
  `Tube`, not flat; drive the effect with a few `User.` numbers from the Blueprint; and judge it with freeze-frame
  captures from the game camera **and** a side angle. Toolset traps: new ribbons have no material, DirectionalBurst
  systems run once for 1 s, number ribbon points with `ExecIndex()`. Effects are art: build them during the jam.

- **Putting a Blender-authored clip into Unreal (Nov 14, #103/#14).** `tools/unreal_import_authored_clip.py` does it
  end to end and refuses to finish unless the imported clip's skeleton is the same OBJECT as the one in the game.
  Three API traps cost real time and all three look like your own mistake:
  - UE 5.8's `AnimSequence` has **no** `get_number_of_sampled_keys` and **no** `get_sampling_frame_rate` in Python.
    Both are the obvious names; both raise `AttributeError`. Frame count comes from
    `unreal.AnimationLibrary.get_num_frames(anim)`. Wrap any such REPORTING call in try/except: the first run died
    while logging a success and left the clip on `RefPose`, the float defect from `7ef73e1`.
  - `FAnimSegment.StartPos` is **read-only to Python**, so hand-building a montage track
    (`seg.set_editor_property('start_pos', 0.0)`) raises and no montage is made. Give
    `AnimMontageFactory` a `source_animation` and it builds the slot track itself - the recipe
    `tools/unreal_fight_anims.py:make_montage` has always used.
- **The graph DSL does not round-trip bool parameters, and the failure is silent (Nov 14).** `read_graph_dsl` prints
  an own-function call as `(CallFunction|PlayerStopAllEnemies true)` - positionally. Write that back and the literal
  binds to nothing: the pin reverts to its default and `PlayerLose` quietly stopped stopping the enemies. The pin is
  named, so write `(CallFunction|PlayerStopAllEnemies :Stopped true)`. **Reading a graph and writing it straight back
  can change behaviour.** Same family as the `HudShowIf :Target` trap. After every `write_graph_dsl`, read the PINS
  (`find_nodes` + `get_node_infos`), not the printed DSL - the printed form is what lied in the first place.
- **Never call `EditorLoadingAndSavingUtils.reload_packages` from the MCP (Nov 14).** With anything dirty it goes
  `PackageTools::ReloadPackages -> PromptUserForDirtyPackages -> FMessageDialog::Open -> EditorAddModalWindow` and the
  game thread sits in a modal nobody can see, with every MCP call timing out. There is no way back without a human
  click: `osascript` keystrokes need Accessibility permission this machine has not granted, so the editor had to be
  killed. Same family as driving editor shutdown or asset deletion through the MCP. To discard unwanted in-memory
  actor changes, close the editor and choose Don't Save instead.
- **`CaptureViewport` during PIE renders the level viewport, editor sprites and all** - it is not a player's-eye view,
  and `CaptureAssetImage` on a clip (the asset's own preview, real mesh + real clip) is the cheaper and more honest
  way to LOOK at an animation. See the Nov 14 devlog for a render that could not be explained from either.

- **Sequencer, learned building beat 1's opening (Sat Nov 14, `tools/b1_opening_cine.py`).** The whole
  Python API is present in 5.8 and works: `add_spawnable_from_instance`, `MovieScene3DTransformTrack`
  (9 channels, `Location.X/Y/Z`, `Rotation.X/Y/Z` = roll/pitch/yaw, then Scale),
  `MovieSceneCameraCutTrack` with `set_camera_binding_id(seq.get_binding_id(binding))`. Four traps:
  - **A throwaway actor that outlives a failed script is a REAL actor in the level.** The spawnable
    recipe is spawn a temp -> `add_spawnable_from_instance` -> destroy the temp. A raise in between
    leaves the temp standing in the map, untagged, and nothing else removes it: one run left a
    `CineDriver` upright in mid-air through the whole peaceful shot, and a `LevelSequenceActor` with no
    tag. Destroy throwaways in a `finally`, and keep a finder (`tools/b1_cine_strays.py`).
  - **`ASkeletalMeshActor`'s SkeletalMeshComponent IS its root component**, so `set_relative_transform`
    on it is the actor transform and a transform track overwrites it every frame. Bake any pose offset
    into the keys. A rotator is applied Yaw*Pitch*Roll, so actor rot (roll 0, pitch -78, yaw 140) equals
    actor yaw 140 plus a mesh relative pitch -78 - which is how a thrown body hands over to a placed one
    with no jump.
  - **You cannot measure a short cinematic from PIE.** An MCP round trip to this editor is ~5 s, so an
    11 s sequence is over before the second sample (measured: t=14.09, 19.07, 39.69, all finished).
    Open the asset and scrub it instead - `LevelSequenceEditorBlueprintLibrary.open_level_sequence` +
    `set_current_time(frame)`, then read each binding back (`tools/b1_cine_scrub.py`). `GetBoundObjects`
    wants `seq.get_binding_id(binding)`, not the binding proxy.
  - **`ALevelSequenceActor` has no `auto_play` property of its own** - it is
    `playback_settings.auto_play`, and that struct has no `restore_state`. Prefer the director Blueprint
    hiding and showing real actors on its own clock over a Sequencer visibility track: the track keys
    `bHidden` behind a label that reads "Visible", and backwards is invisible until you look at a frame.
- **The city kit's materials are under `/Game/Game/Materials/City/`, not `/Game/Game/Materials/`.**
  `M_CafeWall`, `M_CityBrick`, `M_CityTrim` and the rest live there. `load_asset` on the wrong path
  returns `None`, `set_material(0, None)` does not complain, and the mesh renders as the grey checker
  default. Read a neighbouring actor's slot list rather than guessing a path.
- **The graph DSL treats a multi-exec-output node as TERMINAL.** `(Utilities|IsValid x (:"Is Valid" ...)
  (:"Is Not Valid"))` cannot be followed by another statement - the writer refuses with
  "Unreachable code after branch/return". Plain `(if ...)` is fine to sequence. Wrap the guarded work in
  a tiny own function (`CineHideActor(Target, Hide)`) and call that instead of repeating the IsValid.
  Setting a variable on ANOTHER actor needs the value named after the variable:
  `(Class|BPPlayer|SetInputLocked :self ref :InputLocked true)` - positional is refused.
- **A placed actor keeps the class layout it was spawned with.** An instance spawned before a variable
  was made instance-editable refuses the write with *"cannot be edited on instances"*. That is a stale
  instance, not a wrong property name: recompile, then destroy and re-place the actor.

- **A positional argument to `CallFunction|<OurFunction>` lands in the SELF pin, not in the
  parameter (Nov 14).** `(CallFunction|CineRescueStep DeltaSeconds)` fails outright with
  *"Could not connect pin DeltaSeconds to self"*, and `write_graph_dsl` **rolls the whole graph
  back** when it does - so a half-written function is not the failure mode, a silently unchanged
  one is. The trap is that `read_graph_dsl` PRINTS every call in exactly that positional form
  (`(CallFunction|CoworkerExplosionStep DeltaSeconds)`), so reading a graph and writing it back
  is not safe. Name every pin: `(CallFunction|CineRescueStep :DeltaSeconds DeltaSeconds)`.
  Same family as the bool-parameter trap below.
- **A swept `SetActorLocation` that begins already TOUCHING something returns to the START
  point - it does not slide (Nov 14).** Beat 1's rescue moved the player **zero centimetres in
  4.4 seconds** while the fuse burnt down and the blast killed the coworker, because he was
  standing against a cafe table and every frame's sweep was refused. Nothing logs it and the
  function returns normally. For a scripted camera-held move down a path the player has already
  walked, pass `bSweep false`.
- **`CaptureEditorImage` does NOT composite UMG - it cannot photograph a widget (Nov 14).**
  Three captures of a running PIE session came back with no letterbox bars and no caption box
  while the live widget reported `renderScale = (1,1)`, `visibility = HitTestInvisible` and
  `IsInViewport = True`. Same family as the `stat unit` overlay note below. To prove a widget is
  really on screen use the Slate side instead: `SlateInspector.WaitFor` on a string the widget
  displays returns true only if that text is in the live Slate tree, and
  `widget.get_desired_size()` is non-zero only once it has laid out and measured its content.
- **A UMG `Border`'s default brush DRAWS NOTHING, and `BrushColor` tints the nothing (Nov 14).**
  A fresh `UBorder` has `Background.DrawAs = Image`, `ImageType = NoImage`,
  `ResourceObject = None`. Setting `brushColor` to opaque black gives an invisible panel that
  reads as perfectly healthy in every property dump. Set
  `background.resourceObject = /Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture`
  and tint that. `ObjectTools.set_properties` takes its payload in a **`values`** parameter as a
  JSON **string**, not a `properties` object.
- **Beat 1's cinematic car settles at frame 186 (6.20 s) at `(-520, 0, 0)` rot 0, which is the
  real wreck's placed transform (Nov 14).** Reveal the real wreck anywhere earlier and both are
  on screen at once - `CineImpactTime` was 4.70 s, so they overlapped for 1.5 s ("I can see two
  cars"). The `CineCar` spawn track now keys `False` at 186 so the two never coexist; the thrown
  body does the same at 194. Two identical coincident meshes would also be a perfect depth tie
  (#67).
- **`DriverTryTouch` and `CoworkerCanRescueNow` were ALWAYS range-gated** - the F key only chose
  *when* to ask. So "walk up to it and the story moves on" is the director calling them every
  tick while the objective is live, not new interaction code. `BP_OpeningDirector.AutoBeats`
  (instance-editable) puts the key presses back.
- **`Object.call_method` reaches our own Blueprint functions on a live PIE actor** - this is the
  way to drive a mechanic a script cannot press a key for, and it beats writing state. Most
  Blueprint variables are NOT instance-editable, and `set_editor_property` on one is refused
  outright (*"cannot be edited on instances"*): `HasFreezeFrame`, `ExplosionTimeLeft` and
  `FuseLeft` all do it. `actor.call_method('DriverTryTouch')` / `('FreezeFrameStart')` /
  `('CoworkerTryRescue')` run the real gated functions instead (`tools/b1_fire_test.py`).
- **Check whether the TEST is slower than the thing it tests.** An MCP round trip to this editor is
  5-8 s. Beat 1's fuse is 9 s, so running the steps as separate calls burnt the fuse before the
  rescue every time, three runs running, and it read as "the beat is unwinnable". Doing the whole
  run-up inside ONE script call - one frame - showed it wins cleanly. Same family as the 11 s
  cinematic that is over before the second sample.
- **An emissive value that looks right in the material editor can clip to WHITE through this
  project's posterising look.** `M_FireHot` at emissive 3.0 came out of the tonemapper white; 1.7
  reads orange. `MI_AnimeLook_JumpCut` quantises, so judge any emissive from a captured frame, not
  from the number.
- **Re-placing an actor makes a NEW `__ExternalActors__` package and orphans the committed one.**
  Re-placing is the cure for a stale instance, but World Partition loads every package in that
  folder, so the old one must be `git rm`-ed in the same commit or the next load has two. After any
  re-place, run `py <repo>/tools/b1_beat1_audit.py`: it counts the actors that must be unique and
  prints each one's package, so a duplicate is visible before it ships.

## AI-generated 3D models (Hunyuan3D 2.1 and TRELLIS.2, both local)
- **TRELLIS.2** (Microsoft, MIT licence, `D:\AI\TRELLIS2` on the main PC, `C:\AI\TRELLIS2` on GameStation) is the one to use: one photo with the background cut out ->
  `venv\Scripts\python.exe run_image_to_3d.py <cutout.png> out\<name> 1024_cascade` (about 5 minutes on the 3090) -> a GLB
  with real panel lines, handles, lights and wheel spokes. Hunyuan3D 2.1 (`D:\AI\Hunyuan3D2`) is lumpier and its licence is
  non-commercial. TRELLIS.2 is Linux-only upstream; the Windows port (patched CUDA extensions, `build_ext.py`, a
  `segment_reduce` replacement in `trellis2/modules/sparse/basic.py`) is done, don't `git pull` it away. Its DINOv3 image
  encoder is gated: the owner's Hugging Face login (`hf auth login`) must be on the PC.
- Generate from the photo that shows most of the car. A second photo does not merge into the first model; a front-photo run
  gave a different, misshapen car.
- **Cleanup lives in `Art/Blender/ai_car_clean.py`** and carries over to any AI model: `import_trellis` (orient, cut the
  reflection plates the generator puts on roofs, smooth, decimate with the high-poly normals transferred), `bake_maps` +
  `paint_pixels` (paint windows, lights and trim by baked 3D position, so outlines stay crisp on any triangles),
  `texture_lamps` (take lamps from the generator's own red texture pixels), `fill_gaps`, `smooth_body`, `fix_trunk`.
  Only the outlines and the wheel numbers are car-specific.
- When smoothing a textured mesh, move points only along their normals. Sliding them sideways drags the painted
  outlines into zigzags. Don't freeze "sharp" vertices either: the AI's jagged seams count as sharp and stay as ridges.
- Never `recalc_face_normals` on a whole AI mesh (it isn't closed, big areas flip inside out); orient new patches only.
- Decimating a smooth remeshed skin folds it into creases: smooth first, decimate, then transfer the smooth normals.
- Measure the real object (length, width, height, wheelbase) before judging an AI model. The BRZ was 15% too wide and
  only looked "squat" until the numbers said why.
- Never keep a generator's own UV atlas (thousands of micro-islands): mipmaps bleed them into smears, and without
  mipmaps the model sparkles at distance. Re-UV with `smart_project` (big islands), bake with margin 8, keep mipmaps on.
- **Fix the photo, not the mesh.** Reflections in the paint become raised plates on the model; flatten them first
  (`tools/deflect.py`), or use a studio shot. Five rounds of roof-patching code taught us this.
- **The generator only knows what the photo shows.** Whole car in frame, 3/4 angle, a little height. A clipped roof
  gave strips hanging under the car; a close rear shot gave an invented front. One photo gives one good end: join two
  (`Art/Blender/trellis_join.py`: rear-photo model is the body, its nose shrink-wrapped onto the front-photo model).
- **Bake the generator's own texture** (Cycles selected-to-active, full-res source -> clean smart-project UVs) instead of
  painting outlines by position; only wheels, glass, lamps and plastics are rules. Park nothing aside before a bake
  (an object at (3, 1.5, 0) bakes black), and never pick a datablock with `[-1]` on `bpy.data.images` (alphabetical).
- **Weld before decimating.** The glTF import splits vertices along every UV island; decimating that tears holes
  that show as dark flecks. `remove_doubles(dist=1e-5)` first. And never tell bmesh faces apart by index after a
  delete: freed slots are reused. Tag them in an int layer.
- Close Chrome and anything else not in use before a TRELLIS run (it peaks near 17 GB VRAM); the GLB bake runs in its
  own process (`export_glb.py`) after the model is unloaded. A forced Unreal close leaves a "Restore Packages" dialog
  that blocks the MCP; close it with a window message from PowerShell.
- After every TRELLIS build, render each wheel from a low side angle in Blender: the game camera hides the lower half of
  a wheel, and the strip filter in `trellis_build.py` cut every coupe's hub and spokes there for a day before anyone saw it.
- A nearest-point shrink-wrap can't carry recesses (grille, lamp pockets): where a generator model has them, use its own
  faces (`nose_transplant` in `trellis_join.py`). Join torn AI edges with an overlap (flange + dipped band), never by
  bridging or welding the edges: pairing fails and leaves holes.
- `git lfs unlock` makes the file read-only, and then `AssetTools.delete` fails and blames a referencer. `attrib -r` first.
- **Characters and animals** (`Art/Blender/trellis_character.py`, headless: `blender -b --factory-startup --python
  trellis_character.py -- <glb> <Name> human|dog <height_m>`): imports, sizes, finds which way it faces, adds a skeleton
  with the UE mannequin's bone names (humans) or a simple dog skeleton, weights it, and exports `SK_<Name>.fbx` and the colour
  texture to `Content/Game/Imported/<Name>/`, with rest and test-pose renders in `Art/Blender/cache/`.
  - Reference pictures come from Gemini in the user's Chrome (Claude in Chrome; the in-app browser isn't signed in).
    **(Stale as of Sat Nov 14 - the in-app browser IS signed in. See the Gemini note below.)**
    Ask for the full body on a plain white background; for people, an A-pose with clear gaps between the arms and body.
    Never pick a download by a filename pattern: `~/Downloads` holds older Gemini images. Take the newest file.
  - Let TRELLIS simplify: `DEC=30000 TEX=2048` before `run_image_to_3d.py`. Its export rebuilds the surface from the voxel
    volume, which is far cleaner than decimating the GLB in Blender (fur flaps stop the decimator and remeshes shatter).
  - Fur gives pale patches at `1024_cascade`; furry animals come out clean at `512`. Try that before changing seeds.
  - Blender's automatic bone weights fail on anything small (a 0.5 m dog got zero weights). The script weights at 10x scale.

- **Animations for our characters** (`Art/Blender/walk_cycle.py <Name> human|dog`): keys a looping walk/trot on the
  rig in a centimetre scene and exports mesh + rig + action. Import it the way the character came in: copy the FBX
  into its own new folder under `Content/Game/Imported/` and let Interchange auto-import it (mesh, skeleton and
  anim together), then point the slot at the character's `MI_`. `SkeletalMeshTools.import_file` onto the existing
  skeleton does NOT work: the old FBX importer read the bones differently from Interchange (first 1/100 size, then
  twisted) and the walk crushed the man. Test an animation on a placed `SkeletalMeshActor` next to a plain copy.
- **Learned on GameStation in the jam's first hours (Nov 12):**
  - **Tripo** (a jam partner; image-to-3D on its website, then its Retopology) gives a much cleaner anime-style
    character than TRELLIS. Try it first for stylised people; add it to `CREDITS.md` and "Tools you used".
  - **Free animations for our own rigs:** `IKRigController.apply_auto_generated_retarget_definition` recognises the
    skeleton `trellis_character.py` makes (UE mannequin bone names), so an `IKRetargetBatchOperation` copies the
    template mannequin's idle, walk and jog onto it. No hand-keyed walk needed for humans.
  - **One post-process, two looks:** switch on Render CustomDepth for characters, and a single post-process material
    can cel-shade them and treat the background differently (it reads the custom depth as a mask).
- **Fight animation is montages, and the project had none** (GameStation, Nov 12). Combat code that only does damage
  looks broken to a player even when every number is right. `tools/unreal_fight_anims.py` makes the montage assets;
  `ACharacter::PlayAnimMontage` is null-safe, so one `AnimMontage` variable per class and one call site serves
  player, goons and boss.
  - **Epic's `ABP_Unarmed` already carries a `Slot 'DefaultSlot'` node**, so montages play on anything using it with
    no change to the anim blueprint. `BlueprintTools.list_graphs` lists only sub-graphs and hides it; use
    `find_nodes` on `<ABP>:AnimGraph`.
  - **`AnimationSingleNode` mode cannot play a montage**, and a blend space in it has nothing driving its axis, so the
    character stands at the idle corner forever. A character that needs to attack needs an anim blueprint. A minimal
    one is three nodes — blend space -> `Slot 'DefaultSlot'` -> Output Pose — with the blend space X wired to a float
    the event graph sets from `TryGetPawnOwner` -> `GetVelocity` -> `VectorLengthXY`. `AnimBlueprintFactory` takes
    `target_skeleton` through `set_editor_property` even though it is not in `dir()`.
  - **A new variable's default does not reach an existing child Blueprint**, even after recompiling the child: set the
    child's class defaults too. A **placed actor** is worse — it keeps its own serialized value, and when the level
    uses one-file-per-actor, `AssetTools.save_assets` on the `.umap` will not save it. Save the actor's own package
    with `EditorLoadingAndSavingUtils.save_packages([actor.get_outermost()], False)`.
  - Give a death montage `bEnableAutoBlendOut = false` so the body stays down, and make sure the actor lingers at
    least as long as the clip (ours removed the body at 0.6 s into a 1.1 s death).
  - **`unreal.Rotator` is `(roll, pitch, yaw)` positionally.** `Rotator(0, 180, 0)` stands a character on his head.
- **A group that acts as one may be the attacker's fault.** Three goons flinched and died together because
  `PlayerPunch` damaged every enemy in the arc on every punch, not because of their AI. Light hits now take the one
  nearest target; only the finisher sweeps. For per-enemy variety, roll the numbers at spawn behind a flag that is
  off on the base class (`EnemyVary`), so bosses and stand-ins that share `BP_EnemyBase` are untouched - and read
  the flag back on every sibling. `tools/goon_individual_test.py` measures it: run it as the first script of a
  fresh PIE session and stop PIE afterwards (a session left running blocks every Blueprint edit).
- **Props that break or get knocked about (`chaos-physics` skill, `tools/unreal_chaos_props.py`).** Breakables are
  `GeometryCollectionActor`s tagged `JC_Break`; knockables are ordinary `StaticMeshActor`s tagged `JC_Knock`;
  `BP_Player.PlayerSmashProps` reaches both from `PlayerPunch`. Four traps, all silent: the same radial push
  throws one Geometry Collection's pieces 7x faster than another's (measure each; crates carry `JC_BreakSoft`);
  a mesh with complex-as-simple collision **cannot simulate** (only the log says so); `set_simulate_physics(True)`
  on a placed actor does not persist (write `body_instance.simulate_physics`); and a body punched into a wall is
  thrown back out at any speed unless `max_depenetration_velocity` is capped.
- **`write_graph_dsl` over an existing function can leave the old nodes behind.** They may hang off a shared input
  pin, off the execution path, so `read_graph_dsl` shows one clean copy. Count with `find_nodes` (title `""`) and
  delete what the entry node's exec chain cannot reach.
- **The graph DSL reader does not round-trip into the writer.** It prints `Math|Vector|vector-vector` (writer wants `-`),
  `(bind _x 1.0)` (fold the literal in) and `(Character|LaunchCharacter v true true)` (the first positional lands in the
  `self` pin — name the pins: `:LaunchVelocity`, `:bXYOverride`, `:bZOverride`). Read the graph out as a backup first,
  rewrite, then read it back and compare.
- **Player-facing text is American English** (color, defense). Docs can stay as they are.
- **Grid games: put decoration (posts, lamps, props) on tile corners, never tile centres.** The frog lands on centres and
  hops along the lines between them; a corner is 50 cm from every path. Street lamps on tile centres had the frog jumping through them.
- **Judge art from the real game camera** (Simulate, pause, `CaptureViewport` from the game's height), not from
  close-ups. The TRELLIS coupe looked great close up and like a dark blob from the game camera.
- **Meshy (paid, cloud): retries go through the browser, never the API.** Every API call (and the Meshy MCP) costs
  credits; the free retries (4 per model on Pro, 40 on Ultra) are a feature of Meshy's website, for models made there.
  So make every Meshy model on meshy.ai in the user's Chrome from the start (Claude in Chrome: its `file_upload` sends our
  reference picture; the in-app browser can't upload files), and press its Retry until one is good. Use the API only for
  steps that never need a retry, and save its results at once (Meshy keeps them 3 days).
  The user signs in to Meshy themselves. Downloading needs the user's OK in chat unless the request already says to
  download (e.g. "make these five and download them"); take the newest file in `~/Downloads`, never one picked by name.
  Plan credits are monthly and reset each month (no carry-over); bought credit packs never expire.
  **Claude Code drives this in a real browser now** (M Station, 2026-11-12): `@playwright/mcp` at user scope,
  on our own Chrome, with its own profile at `C:/Users/thecl/Documents/megajam-browser/profile` that the user signs
  into by hand once (Google refuses a sign-in inside an automated browser, and we deliberately do not copy the
  user's normal profile). That is the **website**, so it is on the free-retry side of the rule above: the ban is on
  the paid API, not on a browser. `browser_file_upload` is what sends the reference picture.
- **Meshy Image to 3D, the settings that worked:** High Detail (Meshy 7.1), Texture on, Ultra 2K, texture 2K,
  License Private, and Pose -> A-Pose **on** for people, **off** for props. 35 credits and about 2 minutes each.
- **Rigging is two presses, and the first one is only a remesh.** Image to 3D returns 600-950k triangles and
  rigging refuses anything over 300k (*"The polycount is over 300K. Please remesh before rigging"*). The first
  **Rig** press opens a *Target Polycount / Topology* dialog - that is the remesh, it costs 0 credits, and it makes
  a new model-phase asset. Press **Rig** again on **that** asset to get the real *Rig Model* dialog (Humanoid /
  Quadruped Dog / Smart Rig). Use **30K + Quad** so the mesh matches `meshy_character.py`'s 30,000-triangle target.
  The two "Rigging failed" assets from 2026-11-09 are this trap, not bad art.
- **Always remesh to 30K Quad before rigging - do not trust Meshy's 300K gate to make you.** It only offers the
  remesh when it feels like it: on 2026-11-12 a 300,892-face model skipped the dialog entirely and went straight
  to *Rig Model*, while a 477,752-face one was stopped. Smart Rig on that un-remeshed mesh returned a **degenerate
  60-bone skeleton with a one-bone spine**, and `meshy_character.py` then classified the **legs as the arms**
  (`"legs": []`) - so the walk swung the legs as arms and never moved the arms, which still *looks* like walking
  in a contact sheet. Remeshing the same model to 28,025 Quad and rigging that gave a clean 31-bone rig with two
  legs and two arms. If the first Rig press does not offer the remesh, use the mesh-ops button in the viewer bottom
  bar -> **Remesh** -> 30K + Quad; that standalone remesh is **also 0 credits**. The script now prints
  `MESHYCHAR-BAD-RIG` when a "smart" rig has no leg chains, so this cannot ship silently again.
- **Meshy's current Humanoid rig has NO FINGERS, and no export setting gets them back** (Sat Nov 14). A fresh
  `CafeWalker` remeshed to 30K Quad and Humanoid-rigged came out **28 bones**, `LeftHand -> LeftHand_End`, where
  our shipped `SK_CafeWalker` is **69 bones with a 21-bone five-finger subtree on each hand**. Two dead ends,
  both measured rather than assumed: the download dialog's **"Skeleton template" dropdown is inert in this path**
  - the same asset exported as `Mixamo` and as `UE5 Mannequin` gave **byte-identical files** (5,460,508 bytes,
  `cmp` clean, `Hips`/`Spine`/`LeftArm` names both times) - and **`Smart Rig` is now marked (Beta) with a deer,
  an octopus and a spider as its examples**, i.e. it is the creature rigger, not the better humanoid one. So a
  new Meshy body **cannot** drop onto our existing animation set. If a character has to be remade, transfer the
  new mesh's weights onto the **existing** armature in Blender and keep the old skeleton; that is the only route
  that preserves the clips, the montages and the anim blueprint. See issue #96.
- **Meshy's remesh DISCARDS the texture, so a rigged Meshy body has NO colour map to download** (Sat Nov 14).
  Rigging runs on the remeshed asset, and that asset is genuinely untextured - it renders plain grey in Meshy's
  own viewer and its FBX export embeds only `texture_0_normal.png`, a tangent-space normal map. Do not go hunting
  for a download setting; there is no colour on that asset. The colour IS on the pre-remesh high-poly asset, and
  its **glb** export carries it (glTF image `texture_0` -> `baseColorTexture`) where the **fbx** export of the same
  asset does not - but the remesh regenerated the UVs, so that map and the rigged mesh are in **different UV
  spaces**. Dropping it on the rigged mesh renders as camouflage noise: a plausible atlas, a ruined character, and
  nothing errors. **Bake it instead**: `blender -b --factory-startup --python Art/Blender/bake_meshy_basecolor.py
  -- <textured.glb> <rigged.fbx> <out.png>` does the high-poly -> low-poly EMIT bake, 0 credits. The two exports
  are not in the same units or origin (1.902 m centred vs 1.75 m feet-on-floor), so it aligns them first and
  prints the residual - read that number, a bad align gives bald patches, not an error.
- **The armature OBJECT's name becomes the root bone of the Unreal skeleton, so it must match or the import is
  refused** (Sat Nov 14). `SK_CafeWalkerV2_oldrig.fbx` had all 69 bone names and parents identical to the shipped
  rig and Interchange still failed with *"cannot merge bone tree with the existing skeleton"*, because the reskin
  script had left its armature object called `OLD_Armature` where the shipped one is `Armature`. A bone-name diff
  shows nothing - the mismatch is one level above the bones. Rename the armature object AND its data to match
  before exporting. Worse, the failure is not fatal: the SkeletalMesh is still created and still reports the
  skeleton you asked for, so every scripted check passes and only the error line in the log says otherwise.
  **Read the `Warning/Error Summary` at the end of an import log, not just the script's own output.**
- **Do NOT bake a Meshy character's colour map. Decimate the high-poly instead** (Sun Nov 15, supersedes the
  bake advice above for CHARACTERS). Meshy's remesh regenerates UVs and discards the texture, so #112 baked
  high-poly -> low-poly. The bake is lossy and it shows on screen: a dark blotch across the apron, a sawtooth
  hem, a mottled collar. The high-poly keeps its **own** UVs and its **own** clean texture and a Blender
  DECIMATE COLLAPSE to the same triangle count keeps both, so the damage never happens and it costs 0 credits.
  `Art/Blender/rebuild_walker_v2.py` is the worked example. A clean atlas is also a quarter the file size of a
  baked one - 494 KB vs 3.3 MB at 2048x2048 - which is a cheap way to tell them apart.
- **Never fit the RIG to the mesh when the mesh must bind to a skeleton that already has clips.** Unreal's
  `UAnimSequence` tracks are ABSOLUTE LOCAL transforms: playback puts each bone where the clip says whatever the
  mesh was bound in, and the mesh is skinned `(clip pose) * (bind)^-1`. So a bind pose that is not the rest pose
  the clips were keyed against is extra twist on EVERY frame. Fitting the 69-bone rig into `CafeWalkerV2`
  measured better than the conform on every number (bone-to-mesh 1.71 cm vs 2.39) and still shredded the head
  and one arm the moment `Idle` played - while rendering perfectly standing still, which is the trap. Deform the
  MESH into the rig's rest pose, never the other way round, and check it with
  `blender -b --python Art/Blender/rest_delta.py -- <rig_with_the_clips>.fbx <candidate>.fbx`: **it must print
  0.0 deg**, mean and max, or the body is broken in motion.
- **A re-import can hand the material slot back as `WorldGridMaterial`.** Interchange matches slots by the FBX's
  own material name, and a rebuilt FBX need not use the same one. It does not error; the character just renders
  as grey checkerboard. `tools/unreal_reimport_char_v2.py` now restores `MI_*` and says so. When you restore it,
  build FRESH `unreal.SkeletalMaterial` structs - `get_editor_property('materials')` hands back COPIES, so
  mutating them in place is discarded silently and the read-back still says `WorldGridMaterial`.
- **`-script=` on `UnrealEditor-Cmd.exe` mangles backslash paths, and the shell still reports success.** A
  Windows path through this flag turns `	hecl` and `	ools` into TAB characters; the log says
  *"Could not load Python file"*, the commandlet returns -1, and the process still exits **0**. Use forward
  slashes, and never trust the exit code - read the log or the script's own output file.
- **`pose_bone.matrix` resolves against the parent's CURRENT evaluated matrix.** Setting it for a whole chain
  without a `view_layer.update()` **between bones** compounds the error down each chain: the arms and hair tear
  into long streaks that look exactly like a broken bind and are nothing of the kind. Bit a clip-playback check
  on both the old and the new body at once, which is the only reason it was caught.
- **A blueprint that is not a Character keeps its mesh in an SCS component, and `get_components_by_class`
  on the CDO returns an EMPTY list for those.** `BP_Coworker`'s body is `CoworkerBody`, an SCS
  `SkeletalMeshComponent`; the CDO reports zero components, which reads as "this blueprint has no mesh".
  Reach the templates through `unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)` →
  `k2_gather_subobject_data_for_blueprint`, write to EVERY handle it returns for that name (it lists each
  node twice), then `BlueprintEditorLibrary.compile_blueprint` before saving. `BP_Player` is a Character,
  so `CharacterMesh0` IS on its CDO - the two are not interchangeable.
- **A just-deleted asset keeps answering `load_asset()` with the trashed object.** Deleting
  `SK_CafeCoworkerV2` and importing a replacement, then reading it back, returned the CORPSE: old bounds,
  `skeleton None`, and a perfectly good import reported as a failure. Call
  `unreal.SystemLibrary.collect_garbage()` after the delete and re-scan the registry before verifying.
  Same cause: gating a rename on `not does_asset_exist(TARGET)` skips it silently, because the deleted
  name still answers true until the registry catches up.
- **A placed actor can render as a crumpled lump straight after its mesh is re-imported, and be fine on
  the next launch.** The coworker went from a correct asset thumbnail to a teal blob in the level viewport
  the moment the import landed, and came back upright after a restart - stale skinning on the editor-world
  actor, the same thing #109 chased. Restart before filing it as a defect.
- **Look at the colours before calling a character done: `python tools/color_audit.py`.** Image to 3D bakes one
  texture for the whole body and nothing in the pipeline knows a pixel is "hair" or "sleeve", so a model can come
  back with skin-coloured hair, or a shirt the same colour as the arm inside it, and every number still reads
  green. The audit renders the baked base colour **unlit** (a lit contact sheet makes you judge the light rig
  instead of the texture), takes the skin tone from the middle of the face, and paints every pixel within dE76 14
  of it: green on the head and hands where skin belongs, **red everywhere else**. Run it on the **back** too - the
  reference picture only ever shows the front, so the back is the half the model invented.
- **Only the animate-phase asset carries the skeleton.** Downloading the remeshed model gives a bare mesh in
  **both** glb and fbx - no armature, no vertex groups - and `meshy_character.py` then dies with `IndexError` on
  `[o for o in sc.objects if o.type == 'ARMATURE'][0]`. The rigged one is the running-man filter in the asset
  panel and downloads as `..._character.glb`. That is the file the script wants.

## Blender (for building our own 3D models)
- Blender **5.2 LTS** with Blender's official MCP (Blender Lab), from
  `https://projects.blender.org/lab/blender_mcp.git`. **Not** the `blender-mcp` package on PyPI: that name belongs to
  a different, third-party project (ahujasid), so never install it with a bare `uvx blender-mcp`.
- `blender` is **not** in the shared `.mcp.json`, because it needs a real folder path and that path differs on every
  computer. Each machine registers it at **user scope** instead. See "Where each MCP server is configured" below.
- Setup on a new computer:
  1. In Blender 5.2, enable online access, then drag the add-on link from blender.org/lab/mcp-server in twice
     (repository, then add-on), enable it, and click Start (it listens on port 9876).
  2. Install `uv` (`irm https://astral.sh/uv/install.ps1 | iex`, or `curl -LsSf https://astral.sh/uv/install.sh | sh`).
  3. Run `tools\setup_mcp.ps1 -Clone` (Windows) or `./tools/setup_mcp.sh --clone` (Mac). It clones blender_mcp, runs
     `uv sync`, registers both servers at user scope, and writes `.claude/settings.local.json`.
  4. Start a new Claude Code session so the servers are picked up, and check with `claude mcp list`.
- Blender warns that the MCP runs AI-written code with no guards: keep only scratch/project files open while connected.
- **Open Unreal and Blender yourselves** (Start menu, or Claude launches them with `explorer.exe <path>`), never as a
  child of a chat. An app a chat starts closes when that chat is deleted, and its MCP tools vanish from every chat.
  If tools disappear mid-chat, check both apps are running and listening (ports 8000 and 9876), relaunch, then start a new chat.
- The Claude desktop app keeps a private copy of `AppData\Roaming`: anything a chat installs there (e.g. a Python from
  `uv python install`) is invisible to the user's own terminal. Install tools outside `AppData` (e.g. `C:\AI\...`).
- `.claude/settings.local.json` (per PC, gitignored) holds `"enableAllProjectMcpServers": true` so the servers in
  `.mcp.json` load without an approval prompt. `tools/setup_mcp.*` writes it; create it on each new PC.
- Models made in Blender count as our own (scored) art in the jam. Export FBX into `Content/Game/Imported/<Name>/`.
- With our FBX settings (forward -Z, up Y, scale 1), Blender's +Y becomes Unreal's **-Y** (X and Z stay). Check a mesh's
  bounds after import before rotating it in a Blueprint.
- When building meshes from script, add the material slots **before** writing faces, and never `materials.clear()` later.
  Either one silently resets every face to material 0. `Art/Blender/log_kit_materials.py` is a worked example of
  procedural materials baked to textures, including bark that tiles seamlessly.

### Where each MCP server is configured
- **Shared `.mcp.json` is for what is true on every computer.** Only `unreal` qualifies: `http://127.0.0.1:8000/mcp`
  means "this machine's editor" on Windows and Mac alike. Never put a machine path in it (see the team rules below).
- **User scope is for what differs per computer.** `claude mcp add <name> -s user ...` writes `~/.claude.json` on that
  machine only, so each person points `blender` at wherever their own clone lives. `tools/setup_mcp.*` does this.
- User scope also loads in **whatever folder a session starts in**, not just the repo, which matters when a chat lands
  somewhere else (the ClaudeThought peer starts in `Documents` unless its working root is set).
- `/mcp` in a session **lists and re-authenticates** servers that session already loaded; it cannot attach one that
  was not in the config at startup. MCP servers are read when the session starts.
- Gotchas, all found the hard way:
  - **Quote the `--`** when calling `claude mcp add` from PowerShell: `claude mcp add blender -s user '--' uv ...`.
    PowerShell 5.1 swallows a bare `--` as its own end-of-parameters marker, and `claude` then fails with
    `unknown option '--directory'`.
  - `claude mcp remove` **writes to stderr** when the server isn't there. Under `$ErrorActionPreference = 'Stop'`
    PowerShell treats a native command's stderr as fatal, so an idempotent remove-then-add aborts the script.
  - `blender: Connected` in `claude mcp list` only means the bridge process started. Blender itself must be running
    with the add-on listening on **9876** before any Blender tool actually answers.

## Starting a new repo (Nov 11)
- `tools/bootstrap/new_jam_repo.ps1 -Repo <new folder> -Name <Game> [-Verify]` makes the jam repo: the Third Person BP
  template, our plugins and settings, scripts, agent files and docs, git with LFS. No practice gameplay or art.
  `-Verify` opens it in Unreal and checks the MCP, load errors and settings; close any other Unreal first (port 8000).
  It never commits. Its starter files are in `tools/bootstrap/templates/`.
- PowerShell variable names ignore case: `$uproject` and `$UProject` are the same variable.
- So do function names: a function called `Git` that runs `git` calls itself forever. Never name a function after a command.

## Working as a team (up to 5 people, each on their own PC)
Every teammate clones the repo and runs their own Claude Code. You only see and act on the PC this session runs on, and
your chat can't message chats on another person's Claude account: hand-offs go through Git (commits, `docs/TEAM.md`)
or through the humans. New teammate setup: `docs/SETUP_TEAMMATE.md`.
- **Unreal files can't be merged.** `.uasset`/`.umap` are binary: if two people change the same one, one person's work is
  lost. Git LFS locks are what stops that, and they work because everyone has their own GitHub account:
  - Before changing an asset: `git pull --rebase`, then `git lfs lock <file>`. If it's locked by someone else
    (`git lfs locks`), don't edit it: tell the user who has it, and suggest making a new asset or waiting.
  - New assets: commit, then lock right away if you'll keep editing them.
  - After pushing, unlock what you're done with (`git lfs unlock <file>`; by ID for many: `git lfs locks --json`,
    strip `\r` on Windows). Never `--force` unlock someone else's file unless that person agreed.
  - `git config lfs.locksverify true` (set by the setup guide) makes Git refuse a push over someone else's lock.
- **One level, many people:** the level uses "One File Per Actor" (World Settings > Use External Actors), so each placed
  actor is its own small file under `__ExternalActors__`. Two people can then place and move different things in the same
  map. Lock the actor files you change, not the whole `.umap`. Blueprints are still one file each: split big ones
  (e.g. separate `BP_` per system) so people don't queue for the same file.
- **Ownership:** `docs/TEAM.md` says who owns which Blueprints, folders and systems this jam. Stay in your owner's
  area; ask before editing another person's. Each person keeps work in their own folder for new assets
  (`Content/Game/<Type>/`, with clear names) to avoid name clashes.
- **Commit small, commit often, pull first:** `git pull --rebase` before every commit and before starting work. Text
  files (scripts, docs, `.ini`) merge normally; if a rebase stops on a conflict, show the user both sides.
- **Teammates on a Mac** (Justin): the project is Blueprint-only, so it opens without Xcode. Packaging, TRELLIS.2 and
  the bootstrap stay on Windows PCs. Their Blender MCP is registered at user scope by `tools/setup_mcp.sh`, exactly
  like everyone else's; no machine path goes in the shared `.mcp.json`. Use forward slashes and no `C:\` paths in
  anything shared.
- **Git identity:** every commit must be under the teammate's own name (`git config user.name` / `user.email`, their
  GitHub address). Epic may read our Git history, and it shows who built what.
- Push only tested work to `main` (see "How to work with us"). Bigger experiments go on a branch named
  `<name>/<topic>`; merge them once the team has played them.
- **Art made outside Unreal** (Blender, TRELLIS) is committed as FBX + textures under `Art/Blender/export/` and imported
  by whoever owns that area in Unreal (see `docs/TEAM.md`). Tell them the asset names in your hand-off.

## Switching computers (one person, two PCs)
Only one machine should have a given person's working copy of the project open at a time.
- **Which PC does what** is the Computers table in `docs/TEAM.md`, not a fixed rule here. The Team Owner's PCs share
  one GitHub account, so locks can't tell them apart: message the other PC's chat with the asset names after each push.
- **"I'm leaving this computer":** check every asset under `/Game/Game` is saved (`is_dirty`), make sure tested work is
  committed and pushed (ask about anything untested), release our LFS locks (`git lfs locks`), then close Unreal. If it
  stalls on a save prompt for a template asset we never meant to change, force-close it, but only after confirming our
  own assets are clean and pushed.
- **"Let's work on this computer":** `git pull` (LFS brings the assets), open `JumpCut/JumpCut.uproject`
  in UE 5.8, wait until the Unreal MCP at `http://127.0.0.1:8000/mcp` answers, then tell us it's ready.

## Scope guardrails
- The game should be one level, one core mechanic, 3-5 minutes of play.
- Push back if we ask for multiplayer, story/dialogue systems, inventories, complex enemy AI, or open worlds during the jam. Suggest a simpler version instead.
- Prioritize game feel (responsive controls, feedback, sound, juice) over feature count.

## Devlog (Glass Box)
- We're aiming for the Glass Box prize (best devlog showing how we built the game), so keep `docs/devlog/` going without being asked.
- **One file per entry** (`docs/devlog/YYYY-MM-DD-what-happened.md`, rules in `docs/devlog/README.md`). Never append to
  another entry: two people writing at once must never collide on one file.
- After each change we test and you commit, add an entry using the template in `docs/devlog/README.md`: what we asked for,
  the actual prompt, what happened (including failures, retries and dead ends), and what we learned. Commit it with the change.
- Log setup problems and things that broke too, not just successes. Those are the most useful parts.
- When the editor is open, save a screenshot to `docs/media/` and link it from the entry.

## Drawing a character (the character lock)
**Never describe one of our characters in a prompt in your own words.** `docs/character-locks.json` holds one
canonical description each, taken from the reference sheet the rigged model was built from. Write a token and
`tools/gen_images.py` substitutes it:

    {CafeWalker}          full - when he is close and most of him is in frame
    {CafeWalker:short}    shortened - when he is small or far away

Run `python tools/char_lock_check.py` before committing a prompt change; it fails if a prompt starts describing
a locked character by hand. The A-pose prompts that *drew* the sheets are exempt (`sheet_prompts` in the lock).

**Why**: on Fri Nov 13 the title card, the ending card and the itch.io cover each drew the main character's
apron differently, because each prompt described him from memory and six words left the apron's construction
free. The Team Owner's reason for the rule: *"else the game be labeled AI slop."*

**Two things this does not do.** It makes the words identical; it does not make the model obey them - three
takes running still drew a cross-back apron with the no-crossed-straps sentence in the prompt. And it cannot
see the picture. So: pose the character so the detail that drifts is actually **in frame** (a detail on a
surface the camera cannot see gets invented), use `--lock-ref` to hand the model the sheet itself, and look at
the take.

**A lock is changed only when the MODEL is wrong**, which means redrawing the sheet and remaking the rig. Never
edit a lock to match a picture that came out differently.

## Assets and credits
- When we import an asset we didn't make (Fab, AI-generated, sound libraries), remind us to add it to `CREDITS.md` with its source and license.

## Jam rules to enforce
Full summary in `docs/RULES.md`. Warn us if a request would break one of these:
- Only tools, agent configs, MCP settings, prompts and scripts may be prepared before the jam. Gameplay, levels and art must be
  made between Nov 12 and 15, and Epic may check our Git history. **Declare** everything we prepared before the jam
  (scripts, skills, prompts, `CLAUDE.md`) when we submit, and fill in the form's "Tools you used" field.
- Sourced assets (Fab, sound libraries) are allowed but not scored. Assets we make or generate with AI are scored, so prefer those.
- Everything in English, suitable for ages 13+, and no trademarks or logos except the Unreal Engine logo.
- The game must use the theme and go well beyond the Third Person template.

## The current game
**Jump Cut** (theme: "Directors Cut"). See `docs/PITCH.md` for the pitch, the story and the powers, and `docs/ROADMAP.md` for the build order, the cut list and the decisions.

- **Gemini is reachable from the agent's own browser - the note saying it is not is stale.** `CLAUDE.md` said
  reference pictures must come from "Gemini in the user's Chrome (Claude in Chrome; the in-app browser isn't
  signed in)". On Sat Nov 14 the Playwright browser opened `gemini.google.com/app` already **signed in** to the
  owner's account (Pro), with the project's own Gemini history in the sidebar. So an agent can drive Gemini end to
  end. The steps that work, in order, all from the prompt bar: `Upload & tools` (+) -> **Create image** ->
  **Aspect ratio** -> the ratio -> paste -> Enter. Confirm all three before sending (`Deselect Images` chip
  present, ratio button reads what you picked, textbox length equals the prompt's) - a missed toggle wastes the
  take and looks identical until the answer comes back as prose.
  - **Paste, never type, a locked prompt.** `Set-Clipboard` from a file then `Control+v`, and read the textbox
    back and compare its length. The whole point of the lock is identical words; retyping 3,000 characters by
    hand quietly defeats it.
  - **Getting the picture out:** the displayed `<img>` is a `blob:` URL and `fetch()` on it fails once revoked.
    Draw it to a canvas and `toDataURL` instead - it is same-origin so the canvas is not tainted. That yields the
    **1024-wide display copy**, which is enough to judge a take but NOT what to ship; the full-size file still
    needs the page's own "Download full size image".
  - **Once the page settles the `blob:` is gone and the `<img>` becomes an `lh3.googleusercontent.com/gg-dl/`
    URL.** A canvas draw on that one throws `SecurityError: Tainted canvases may not be exported`, and `curl` on
    the URL outside the browser gets **403** - it needs the session. The way back: **click the image** to open
    the lightbox, which mounts a fresh `blob:` copy, and canvas-grab that. An element screenshot is NOT a
    substitute - it comes back at the displayed size with the container's rounded corners baked in.
  - **COUNT what the picture must contain; do not eyeball it.** A model draws the right thing the wrong number
    of times and the take still looks completely correct - two of three takes drew three power rings instead of
    four and nothing about them said so. `tools/count_power_rings.py` is the pattern: give it a box, let it
    count, let it exit non-zero. It needs a box because the same cyan is also the collar and the rim light.
  - **"Download full size image" lands in `megajam-browser/out/`, NOT `~/Downloads`.** The Meshy note below says
    to take the newest file in `~/Downloads`; that is true of the user's own Chrome and **false of the Playwright
    browser**, which writes to its own output directory. Taking the newest `~/Downloads` file after a Playwright
    download gets you a stale picture from another project - exactly the trap the "never pick by filename
    pattern" rule warns about, arriving from the other direction. Check the tool's own `Downloaded file ... to`
    line for the real path (Sat Nov 14).
  - **Do not judge a take from an element screenshot - the composer sits on top of it.** A full-body A-pose came
    back looking cropped at the shins twice running, and it was not: the prompt bar overlays the bottom of the
    `<img>`, and an element screenshot captures whatever occludes it. The downloaded full-size file had complete
    headroom and footroom both times. Either download first, or make the window taller before looking (Sat Nov 14).
  - **Start a NEW chat for each take.** A follow-up message makes Gemini *edit* the previous picture and inherit
    whatever it got wrong, which is exactly what `docs/prompts-gemini.md` warns about.
  - It composes to fill the frame and will not reliably leave an empty band for title text; see `UI-TITLE2` in
    `docs/prompts.md` for the measured numbers.
