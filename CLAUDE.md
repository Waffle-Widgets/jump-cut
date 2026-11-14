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
  the `playtest` branch; merge into `main` when testers confirm (`playtest-issues` skill). `builder (Area)` = only that area.
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
- **To find a flicker, capture the same camera twice and diff the pictures** (`CaptureViewport` x2, per-pixel
  difference). It shows *what* changes in one step. Auto-exposure settling after a camera turn changes half the
  picture too - that is a drift, not a flicker; let it settle before comparing.
- **A character that floats only while it moves: check Root Motion Root Lock before the retarget.** Meshy's Smart
  Rig keeps its root bone at pelvis height in the *reference pose*; retargeted clips animate it on the floor. A
  clip with root motion on locks its root to `RefPose` by default, so the mob boss rose 87.26 x 1.2921 = 113 cm
  whenever he walked or swung and stood correctly when idle. Set `root_motion_root_lock = AnimFirstFrame` on every
  root-motion clip of such a rig (`tools/unreal_boss_root_lock.py`); never `Zero`, which wipes the root's up-axis
  turn. And **evaluate a clip the way the game does**: `AnimPoseEvaluationOptions.extract_root_motion = True`.
  Without it every clip read 0 and looked innocent.
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
  `captureTransform` and an all-zero `annotations` even when they're unused; `CaptureEditorImage` comes back 1280 px wide.
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
