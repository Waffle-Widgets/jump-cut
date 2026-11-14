# Pre-jam declaration

**What we made before the 2026 Epic AI MegaJam opened, and what we made during it.**

First written Thu Nov 12, 2026, 7:48 AM Pacific. Keep it current — the last section of this file is the one
that has to be re-checked before we submit.

## Why this file exists

- **Official Rules §7h** lets us bring AI tools, agent configuration, MCP settings, prompt libraries and scripts
  that we prepared before the jam. **Gameplay, levels and art must be made during the jam** (Nov 11, 9:00 PM
  Pacific → Nov 15, 5:59 PM Pacific). Epic may ask to see these files or our Git history to check.
- **The itch.io jam page** goes one step further than the PDF: it asks us to *declare* anything made before
  Nov 12, and its FAQ names prompts, scripts and assets specifically.

So bringing our practice-week toolbox is allowed; saying what it is, is required. This file is that statement.
Paste the short version below into the submission form, and link this file for the detail.

## Short version (paste this into the form)

> Prepared before the jam and brought into the repo: our AI agent configuration and prompt library
> (`CLAUDE.md`, `GEMINI.md`, `.mcp.json`, and 13 Claude Code skills under `.claude/skills/`), 42 helper
> scripts under `tools/` (Unreal MCP helpers, a Windows packaging/zip script, a pure-Python sound-effect
> generator, and local image-to-3D runners for TRELLIS.2 and Pixal3D), 28 Blender Python scripts under
> `Art/Blender/` for cleaning up and rigging AI-generated models, our project config `.ini` files and
> repo/workflow setup, and our team process docs. These came from our practice repository,
> github.com/Waffle-Widgets/megajam-2026-practice, worked on Nov 1–11.
>
> No gameplay, no levels, no art, no sounds and no Blueprints were brought in. Everything in the game
> itself was made after the jam opened. The one third-party starting point is Unreal Engine 5.8's own
> Third Person Blueprint template, used under the Unreal Engine EULA and listed in `CREDITS.md`.

## The provable split

This repo was created on **Thu Nov 12, 2026 at 6:42 AM Pacific**, and the split is visible in its Git history
rather than only asserted here:

| Commit | What it is |
| --- | --- |
| `e9bfc06` — *"Jump Cut: jam repo from the bootstrap"* | **Everything prepared before the jam.** 346 files, written out by `tools/bootstrap/new_jam_repo.ps1`. Nothing in it is gameplay, art or a level, except Epic's own template content. |
| `c19e0ad` and later | **Everything made during the jam.** |

If a file is in `e9bfc06`, we are declaring it as pre-jam material. If it arrived after, it is jam work — with one
declared exception, `docs/TEAM_SYNC_BACKUP.md`, which is pre-jam content that reached this repo late. It is named
and dated in section 4 rather than left for someone to notice.

## 1. Prepared before the jam — AI agent configuration and prompts (§7h)

| Path | Files | What it is |
| --- | --- | --- |
| `CLAUDE.md` | 1 (37 KB) | Standing instructions for Claude Code: how this team works, and a long list of Unreal/MCP traps we hit during practice week and wrote down so we don't repeat them. |
| `GEMINI.md` | 1 | Standing instructions for Gemini (concept art, textures, second opinions). |
| `.mcp.json` | 1 | MCP server settings: Epic's Unreal MCP on `127.0.0.1:8000`, and a local Blender MCP. |
| `.claude/settings.local.json` | 1 | Lets the project's MCP servers start without a prompt. |
| `.claude/skills/` | 13 | Our prompt library, as Claude Code skills. Listed below. |

The 13 skills, all written during practice week (Nov 1–11):

| Skill | What it tells the agent to do |
| --- | --- |
| `asset-import` | Import meshes, textures, animations and sounds through the MCP without freezing the editor or losing materials. |
| `chaos-physics` | Breakable objects with Chaos: Geometry Collections via a Dataflow graph, and breaking them from code with strain + impulse. |
| `devlog-entry` | Write the Glass Box devlog entry for a tested change, with a screenshot, and commit it with the change. |
| `jam-rules-check` | Check a request, asset or idea against these jam rules before we start it. |
| `make-sound` | Make sound effects and music from code with `tools/make_sfx.py`, so there is nothing to credit. |
| `niagara-fluids` | Realistic fire, smoke and explosions with Niagara Fluids, and baking a simulation into a flipbook. |
| `niagara-fx` | Attack and impact effects with Niagara particles, judged from the game camera. |
| `package-build` | Package the Windows build and zip it for itch.io with `tools/package_build.ps1`. |
| `pc-handoff` | Hand a computer over safely: save, commit, push, release Git LFS locks, close or open Unreal. |
| `playtest-capture` | Screenshot the game as the player sees it and measure frame rate, so a remote teammate can follow along. |
| `playtest-issues` | The playtest loop through GitHub issues: file, build, publish, confirm, merge. |
| `trellis-model` | Make a game-ready 3D model from a picture with the local TRELLIS.2 generator, then clean it up in Blender. |
| `unreal-blueprint` | The safe procedure for creating or editing Blueprints through the MCP (`write_graph_dsl`, `execute_tool_script`). |

**One honest note on `CLAUDE.md`:** the file is pre-jam, but three lines were *added* after the jam opened
(practice-repo commit `8baf59c`, Thu Nov 12 6:40 AM Pacific) recording lessons from the jam's own first hours.
Editing our agent instructions during the jam is allowed; we mention it so the file's history isn't a surprise.

## 2. Prepared before the jam — scripts (§7h)

**`tools/` — 42 files.** None of them is game code; they are things we run *at* Unreal, Blender or an image
generator from outside.

| Path | What it is |
| --- | --- |
| `tools/package_build.ps1` | One command to package the Windows build and zip it under the jam's 1 GB limit. |
| `tools/publish_build.ps1` | Publishes a test build as a GitHub Release; refuses to run anywhere but the builder PC. |
| `tools/make_sfx.py` | Generates sound effects and music loops from pure Python — no samples, nothing to credit. The script is pre-jam; the `make_jumpcut()` function added to it during the jam, and every sound it has made for this game, are jam work (see the jam-work section). |
| `tools/gen_images.py` | Generates reference images locally. The script is pre-jam; every picture it has drawn for this game was drawn during the jam, from jam-written prompts. |
| `tools/bootstrap/` (10 files) | `new_jam_repo.ps1` and its templates — the script that created *this* repo. |
| `tools/trellis/` (6 files) | Our patched Windows port of Microsoft's TRELLIS.2 image-to-3D model (MIT), plus its build patches. |
| `tools/pixal3d/` (4 files) | A second local image-to-3D runner and its patches. |
| `tools/glb_for_unreal.py`, `tools/unreal_import_glb.py` | Prepare and import generated `.glb` models into Unreal. |
| `tools/unreal_make_beam_particle_mat.py`, `unreal_make_flame_particle_mat.py`, `unreal_make_fire_flipbook_mat.py`, `unreal_make_melt_mat.py`, `unreal_make_fx3d.py` | Build effect materials through the MCP. |
| `tools/fx3d_graphs.py`, `beam_destruction_graphs.py`, `meltwall_graphs.py` | Niagara and Blueprint graph definitions for those effects. |
| `tools/unreal_chaos_test.py`, `unreal_fx_spawn_test.py`, `unreal_fx_component_setup.py`, `unreal_capture_megabeam.py`, `unreal_find_new_assets.py` | Test and inspection helpers for the editor. |
| `tools/bakeoff_sheet.py`, `cutout.py`, `deflect.py` | Image and comparison utilities used while judging art. |

**`Art/Blender/` — 28 Python scripts** that drive Blender from the command line to clean up, weld, decimate,
unwrap, bake and rig AI-generated meshes, and to build kit-bash kits (`trellis_*.py`, `*_kit.py`,
`meshy_character.py`, `walk_cycle.py`, `bakeoff_render.py` and others). They operate on models we generate;
none of them contains art.

A note on where some of these came from: 12 of the effect helper scripts were written during practice week in
our own sister project `deep-archive-hd2d` (commits dated Nov 9–11, all before the 9:00 PM Nov 11 open) and
copied into the practice repo at 6:40 AM Pacific on Nov 12 so that the skills which name them would work. They
are our own earlier work, moved — not new work disguised as old.

## 3. Prepared before the jam — project settings and repo setup

| Path | Files | What it is |
| --- | --- | --- |
| `JumpCut/Config/*.ini` | 6 | Project settings: MCP and Python enabled, import dialogs off so the agent can import while we're remote, editor and input defaults. |
| `JumpCut/JumpCut.uproject` | 1 | Plugin set: Model Context Protocol, Python, Modeling Tools, Geometry Collection (Chaos Destruction, off by default in 5.8), Terminal, Gameplay State Tree. |
| `.gitignore`, `.gitattributes` | 2 | Unreal ignores, and Git LFS plus file locking for `.uasset`/`.umap` and source art. |
| `.github/ISSUE_TEMPLATE/` | 2 | The playtest issue form the testers file bugs with. |

## 4. Prepared before the jam — team process docs

`docs/HOW_WE_WORK.md`, `docs/TEAM.md`, `docs/PLAN.md`, `docs/PLAYTEST.md`, `docs/RULES.md`,
`docs/SETUP_TEAMMATE.md` — how the team works, which computer does what, the playtest loop, our reading of
these rules, and teammate setup. Process, not game.

**`docs/TEAM_SYNC_BACKUP.md` is pre-jam too, and it is the exception to the split above.** Its own first line says
*"Saved 2026-11-09"* — written during practice week, before the 9:00 PM Nov 11 open — but it was only copied into
this repo on Nov 12, so it arrives in a commit that is otherwise jam work. It is a backup plan for splitting the
team's work across two Claude plans and syncing through GitHub: process, not game, and allowed under §7h. The copy
here is byte-for-byte identical to `megajam-2026-practice/docs/TEAM_SYNC_BACKUP.md`, which is public, so the Nov 9
date can be checked in that repo's history rather than taken on our word.

Two files in `docs/` arrived as *templates* in `e9bfc06` and were filled in during the jam, so their
**contents are jam work**: `docs/PITCH.md` (written after the Nov 11, 11:00 AM theme reveal) and
`docs/DEVLOG.md` (since Nov 12 the entries are one file each in `docs/devlog/`). `docs/media/` shipped as a single `.gitkeep`.

## 5. Not ours and not pre-jam: Epic's template

`JumpCut/Content/` arrived with 238 files of Unreal Engine 5.8 **Third Person Blueprint template** content
(the mannequin, prototyping meshes, input actions, the template level). That is Epic's, used under the Unreal
Engine EULA, allowed as a starting point by §7d and §7e, and listed in `CREDITS.md`. It is not scored as ours,
and the game has to go well beyond it.

## Made during the jam (the other side of the declaration)

Everything below was made after the jam opened at 9:00 PM Pacific on Wed Nov 11. We list it because a
declaration that only names the pre-jam side is half an answer.

| What | When | Where the record is |
| --- | --- | --- |
| The pitch and the game's name, "Jump Cut" | Wed Nov 11 evening → Thu Nov 12 morning | `docs/PITCH.md`, devlog entry *"The theme drops, and the game gets a name"* |
| The cel-shaded anime look (`M_AnimeLook`, `M_AnimeChar`, `M_AnimeSurface`, `M_AnimeShaft` and instances) | Wed Nov 11 11:57 PM → Thu Nov 12 7:16 AM Pacific | `tools/unreal_make_anime_look.py`, commit `c19e0ad` |
| The coffee-shop opening scene (`Lvl_Cafe`), built from primitives by script | Thu Nov 12, by 7:16 AM Pacific | `tools/unreal_make_anime_cafe.py`, commit `c19e0ad` |
| The hero: Gemini drawing → Tripo model → Blender rig → Unreal (`SK_CafeWalker_Walk`, `BP_CafeWalker`, `T_CafeWalker_BaseColor`) | Thu Nov 12 1:10 AM → 7:34 AM Pacific | `Art/Blender/anime_repaint.py`, `tools/unreal_retarget_mannequin.py`, `CREDITS.md` |
| Mannequin animations retargeted onto the hero | Thu Nov 12 morning | `CREDITS.md` — Epic's, under the EULA, sourced and **not scored** |
| `Art/Blender/anime_repaint.py`, `tools/unreal_make_anime_look.py`, `tools/unreal_make_anime_cafe.py`, `tools/unreal_retarget_mannequin.py` | Thu Nov 12 1:26 AM → 7:34 AM Pacific | Written *during* the jam, so **not** declared as pre-jam scripts, even though they sit in `tools/` and `Art/Blender/` beside ones that are |
| The team's agent rules and shared plan: `docs/ROADMAP.md`, `docs/INITIAL_PROMPT.md`, the `docs/devlog/` split, and the reporting / "done means" sections **added to the pre-jam `CLAUDE.md`** | Thu Nov 12 morning | Branch `justin/agent-rules`. `CLAUDE.md` and `GEMINI.md` are declared pre-jam above; what they said on Nov 11 is `e9bfc06`, and every change since is jam work, visible in `git log -p CLAUDE.md` |
| `tools/setup_mcp.ps1`, `tools/setup_mcp.sh` | Thu Nov 12 8:40 AM Pacific | Written *during* the jam. They register each computer's MCP servers; the shared `.mcp.json` was changed the same day to drop the Windows-only Blender path |
| The first three characters — designs, reference prompts and reference sheets: `docs/CHARACTERS.md`, `docs/prompts.md`, `Art/Refs/*_apose.png` | Thu Nov 12 afternoon Pacific, M Station | Drawn by `tools/gen_images.py`, which **is** a declared pre-jam script, from prompts written **during** the jam. `docs/prompts.md` is jam work and is **not** the pre-jam prompt library declared in section 1 (that is `.claude/skills/`). The difference matters: the pictures these prompts make are art we generated ourselves, and art is scored |
| The three rigged characters and the cleaver prop: `Art/Blender/export/Characters/{CafeWalker,CrashDriver,CleaverBoss}/`, `Art/Meshy/Cleaver/` | Thu Nov 12 3:54 → 4:20 PM Pacific, M Station | Made on meshy.ai in our own browser from our own reference sheets (Meshy named them *The Weary Apron*, *Frostbound Rider*, *The Obsidian Enforcer*, *Steel Butcher Cleaver*), then processed by `Art/Blender/meshy_character.py` and `meshy_prop_bake.py`. Meshy is a paid AI tool and is credited in `CREDITS.md`; the models are scored as our own work |
| The text-only Gemini prompt library and the cast redrawn from it: `docs/prompts-gemini.md`, `Art/Refs/gen/gemini2/` | Thu Nov 12 5:30 → 5:48 PM Pacific, M Station | Written during the jam and drawn in a new Gemini chat with **nothing uploaded** — no earlier picture of ours was given to the model, so every line of each design comes from text we wrote. Gemini is an AI tool and is credited in `CREDITS.md`; the pictures are scored as our own work. Separate from the pre-jam prompt library in section 1, which is `.claude/skills/` |
| Two more CleaverBoss models from the unused Gemini reference art: `Art/Blender/export/Characters/{CleaverBossGemRef,CleaverBossGemText}/`, `Art/Refs/CleaverBoss_apose_gemref.jpg`, `Art/Refs/CleaverBoss_apose_gemtext.png` | Thu Nov 12 7:17 → 7:35 PM Pacific, M Station | Made on meshy.ai in our own browser from two Gemini reference pictures we drew earlier the same evening (Meshy named them *The Iron Broker* and *The Stern Negotiator*), then processed by `Art/Blender/meshy_character.py`. 70 credits. Meshy and Gemini are AI tools and are credited in `CREDITS.md`; the models are scored as our own work |
| The leg/tail fix **made during the jam to the pre-jam `Art/Blender/meshy_character.py`** | Thu Nov 12 4:13 PM Pacific | That script is declared pre-jam in section 1; what it said on Nov 11 is `e9bfc06`, and every change since is jam work, visible in `git log -p Art/Blender/meshy_character.py`. Same rule we applied to `CLAUDE.md` |
| The first build's scripts: the Blueprint graphs as text (`tools/b1_graphs.py`, `b2_graphs.py`, `b3_graphs.py`, `b4_graphs.py`, `c1_graphs.py`, `d1_graphs.py`, `d2_graphs.py`, `e1_graphs.py`), the level layout and its checks (`tools/c1_layout.py`, `c1_materials.py`, `c1_traces.py`, `c1_pie.py`), and the one-off editor steps (`tools/d1_editor.py`, `e1_editor.py`, `a3_editor.py`, `a3_pie.py`) | Thu Nov 12, 10:45 AM → evening Pacific, GameStation | Written *during* the jam by the first build's builder and checker subagents, so **not** declared as pre-jam scripts, even though they sit in `tools/`. The four editor-step scripts were first kept in the ignored `JumpCut/Saved/` and copied into `tools/` after the final audit |
| The first build's books: `docs/FIRST_BUILD_LEDGER.md`, `docs/FIRST_BUILD_DESIGN.md`, `docs/FIRST_BUILD_MCP_TIPS.md`, `docs/FIRST_BUILD_AUDIT.md` | Thu Nov 12, 10:45 AM → evening Pacific, GameStation | Jam work: the ledger, the design note the builders shared, the MCP lessons they wrote down, and the final audit. The method they follow is `docs/INITIAL_PROMPT.md`, listed above |
| `tools/color_audit.py`, `Art/Blender/color_audit_render.py` and `docs/media/COLOUR-AUDIT.jpg` | Thu Nov 12 evening Pacific, M Station | Written *during* the jam. They render each finished model's baked base colour unlit and check that skin, hair and clothing colours land where they are meant to. No pre-jam script does this; the sheet they produce is a record of our own models, not generated art |
| The crash driver, the mob boss and the cleaver imported into Unreal: `JumpCut/Content/Game/Imported/{CrashDriver,CleaverBoss,Cleaver}/`, `MI_CrashDriver`, `MI_CleaverBoss`, `MI_Cleaver`, `docs/media/MODELS-IN-UNREAL.png` | Thu Nov 12 evening Pacific, GameStation | Jam work: the Unreal assets derived from our own jam-made FBX models (row above), imported through Interchange and pointed at new instances of our own `M_AnimeChar`. Nothing sourced from outside |
| The mob boss wired into the plaza fight: `BP_BossFreeze` (mesh, material, `cleaver_r` socket, `BossDriveAnim`), `JumpCut/Content/Game/Imported/CleaverBoss/Anims/*_CB`, `docs/media/MOB-BOSS-PLAZA.png` | Thu Nov 12 10:00 → 10:30 PM Pacific, GameStation | Jam work. The animations are Unreal's own mannequin motion capture (shipped with the Third Person template, sourced in `CREDITS.md`) retargeted onto our own skeleton by the jam-written `tools/unreal_retarget_mannequin.py`; the retarget definition, the socket and the Blueprint wiring are ours |
| A second crash driver, generated locally instead of bought: `Art/Blender/export/Characters/CrashDriverTrellis/` (`SK_CrashDriverTrellis.fbx`, `T_CrashDriverTrellis_BaseColor.png`) and `Art/Blender/export/Characters/SK_CrashDriverTrellis_Walk.fbx` | Thu Nov 12, 11:03 → 11:09 PM Pacific, GameStation | Jam work, and **no third-party service touched it**. Made on our own RTX 5090 from our own jam-made reference sheet `Art/Refs/CrashDriver_apose.png` by Microsoft's TRELLIS.2 (MIT, running locally from `tools/trellis/`), then cleaned, rigged and animated by `tools/cutout.py`, `Art/Blender/trellis_character.py` and `Art/Blender/walk_cycle.py`. Those four are **declared pre-jam scripts** in sections 1–2 and were **not modified** for this; the model they produced is jam-made art and is scored as ours. 0 credits, nothing uploaded anywhere. TRELLIS.2 is already credited in `CREDITS.md` |
| The third boss designed before he is drawn: the `StuntDouble` entry in `docs/CHARACTERS.md`, the `GEM2-BOSS3` prompt in `docs/prompts-gemini.md` and the `BOSS3-APOSE` code in `docs/prompts.md` | Thu Nov 12, 11:15 PM → Thu Nov 12, 11:58 PM Pacific, GameStation | Jam work, and **nothing was generated** — this row is design text and image prompts only, written during the jam from the Team Owner’s Nov 12 boss-ladder decision. No picture, no model and no asset exists for this character, so there is no generated art to score yet; the design itself is a **proposal** that no person has agreed to. Both prompt files already have rows above and are jam work, not part of the pre-jam prompt library in section 1 (that is `.claude/skills/`). The one measurement in it read a colour off our own committed `T_CrashDriver_BaseColor.png` with Python’s standard library — no new tool was installed and no pre-jam script was modified |
| The fight's animation: `tools/unreal_fight_anims.py`, `JumpCut/Content/Game/Anims/Human/AM_Human_*`, `JumpCut/Content/Game/Imported/CleaverBoss/Anims/{ABP_CleaverBoss,AM_CleaverBoss_*,MM_Attack_01_CB,MM_Attack_03_CB,MM_HitReact_Front_Med_01_CB,MM_Death_Front_01_CB}`, the montage wiring in `BP_Player`, `BP_EnemyBase`, `BP_Goon` and `BP_BossFreeze`, and `docs/media/FIGHT-ANIMATION.png` | Thu Nov 12, 11:00 PM → 11:45 PM Pacific, GameStation | Jam work. The motion itself is **Epic's own mannequin motion capture**, shipped with the Third Person template and already sourced in `CREDITS.md` — it is **not scored as ours**. What is ours and is scored: the montage assets that wrap it, the retargets onto our own CleaverBoss skeleton (through the jam-written `tools/unreal_retarget_mannequin.py`), the `ABP_CleaverBoss` anim blueprint, and every line of Blueprint that decides when a clip plays. `tools/unreal_fight_anims.py` was written **during** the jam, so it is **not** a declared pre-jam script even though it sits in `tools/` |
| Beat 1's rescue: `JumpCut/Content/Game/Blueprints/{BP_Coworker,BP_Shrapnel}.uasset`, the `PlayerInteract` function and the **F** / `Gamepad_FaceButton_Top` poll added to `BP_Player.PlayerTickInput`, the `Coworker_Cafe` actor in `Lvl_JumpCut`, and the `CafeCoworker` design with its `GEM2-COWORKER` and `COWORKER-APOSE` prompts | Fri Nov 13, 12:59 → 1:15 AM Pacific, GameStation | Jam work, written from scratch during the jam against the Team Owner's Nov 13 "build in play order" decision. Every Blueprint graph, variable and placed value is ours; the only art in it is two engine primitives (`/Engine/BasicShapes/Cube`, `Sphere`) used as grey-box stand-ins under the Unreal EULA, already sourced in `CREDITS.md`, and our own jam-made materials `M_CheckGreen`, `M_PropRed` and `M_WarnFreeze`. **Nothing was generated**: the coworker's design text and her two image prompts are written, and no picture and no model exist for her yet. Both prompt files already have rows above and are jam work, not part of the pre-jam prompt library in section 1 |
| Boss 3 built as a fight before he is drawn: `JumpCut/Content/Game/Blueprints/{BP_StuntDouble,BP_StuntStandIn}.uasset`, the `EnemyStandIns` redirect in `BP_EnemyBase.EnemyTakeHit` | Fri Nov 13, 12:05 → 12:50 AM Pacific, GameStation | Jam work, written from scratch during the jam. Both Blueprints are children of our own jam-built `BP_EnemyBase` on **Epic's mannequin** (`SKM_Manny_Simple`, shipped with the Third Person template and already sourced in `CREDITS.md`) as a deliberate placeholder body, reusing the `AM_Human_*` montages from the row above. **Nothing was generated for this character** — the `GEM2-BOSS3` and `BOSS3-APOSE` prompts are still unrun, so there is no picture and no model to score. What is ours and is scored: every Blueprint graph, variable and tuned value, including the damage-redirect and the Freeze Frame counter |
| Beat 1 rebuilt to the Team Owner's written scene: `JumpCut/Content/Game/Blueprints/BP_CrashDriver.uasset`, `CoworkerExplosionStep` and the death-instead-of-retry change in `BP_Coworker`, the `BP_CrashDriver` branch of `BP_Player.PlayerInteract`, the `C1_Cafe_CrashDriver` actor and the two switched-off `MarkerGrantsFreezeFrame` flags in `Lvl_JumpCut` | Fri Nov 13, 2:10 → 2:40 AM Pacific, GameStation | Jam work, written from scratch during the jam against the Team Owner's Nov 13 beat-1 scene. The only art in it is our **own** jam-made `SK_CrashDriver` and `MI_CrashDriver` (declared two rows up) and one engine primitive (`/Engine/BasicShapes/Sphere`) used as the touch prompt under the Unreal EULA, already sourced in `CREDITS.md`, wearing our own `M_PropBlue`. **Nothing was generated.** The grey-box `C1_Cafe_Driver` placeholder it replaces is deleted |
| Beat 1's quick time event turned into a bullet-time window, and the game's first sound: `PlayerBulletTimeStart`/`PlayerBulletTimeEnd`/`PlayerTickBulletTime`/`PlayerTickFreezeCountdown` and the countdown fields on `BP_Player`, `BulletTimeOnExplosion` on `BP_Coworker`, `CountdownText` and `QtePrompt` on `WBP_HUD`, and `JumpCut/Content/Game/Audio/{SFX_CountdownBeep,SFX_CountdownAction,SFX_BulletTime}` with their `.wav` sources in `Art/Audio/` | Fri Nov 13, 2:50 → 3:25 AM Pacific, GameStation | Jam work, written from scratch during the jam against the Team Owner's Nov 13 quick-time-event decision. Every Blueprint graph, variable, tuned value and HUD widget is ours. **The three sounds are ours too and are scored as ours**: they are synthesized from sine/square/noise by `make_jumpcut()` in `tools/make_sfx.py` using only Python's standard library — no samples, no library, no service, nothing to credit. `tools/make_sfx.py` itself **is** a declared pre-jam script in sections 1–2; the `make_jumpcut()` function added to it is jam work, visible in `git log -p tools/make_sfx.py`, the same rule we applied to `CLAUDE.md` and `Art/Blender/meshy_character.py` |
| ComfyUI + Qwen-Image installed on GameStation so both computers can draw: `tools/install_comfyui.sh` | Fri Nov 13, 2:52 → 3:05 AM Pacific, GameStation | The **script** is jam work — written during the jam, so it is **not** a declared pre-jam script even though it sits in `tools/`. What it installs is third-party software (ComfyUI, and Alibaba's Qwen-Image weights) onto one of our own computers; it is a **tool**, which §7h allows, and it is the same tool and the same model files M Station has been using since the cast was drawn — the point of installing it was that the two machines draw in the same hand. No art was brought in with it: the model weights are a tool, every picture drawn from them during the jam is ours and is scored, and ComfyUI and Qwen-Image belong in `CREDITS.md` beside Gemini and TRELLIS.2 |
| The coworker drawn at last: `Art/Refs/CafeCoworker_apose.png` | Fri Nov 13, 9:00 → 9:02 AM Pacific, GameStation | Jam work, and **no third-party service touched it**. Drawn on our own RTX 5090 by ComfyUI + Qwen-Image (declared as a tool in the row above) from our own jam-written `COWORKER-APOSE` prompt in `docs/prompts.md`, through the jam-written `tools/gen_images.py`. **0 Meshy credits, nothing uploaded anywhere.** Three takes were drawn into the gitignored `Art/Refs/gen/`; take 1 is the pick and the only one committed. This **supersedes** the "nothing was generated" note on the beat-1 rescue row above, which was true when it was written. She is still a grey box in Unreal — no model exists yet |
| The coworker given a body: `Art/Blender/export/Characters/CafeCoworker/` (`SK_CafeCoworker.fbx`, `T_CafeCoworker_BaseColor.png`) | Fri Nov 13, 9:49 -> 10:05 AM Pacific, M Station | Jam work. Made on **meshy.ai in our own browser** (Meshy named it *Welcoming Apron Pose*) from our own jam-made reference sheet `Art/Refs/CafeCoworker_apose.png`, then remeshed to 30K Quad, Smart Rigged and downloaded as the animate-phase GLB, and processed into an Unreal-ready FBX with Walk and Idle by `Art/Blender/meshy_character.py`. **35 credits**; the remesh and the rig were free. That script **is** a declared pre-jam script in sections 1-2 and was **not** modified for this. Meshy is an AI tool and is already credited in `CREDITS.md`; the model is scored as our own work. This **supersedes** the "no model exists yet" note on the row above. She is still not imported into Unreal - that is the builder's job, and M Station is the maker |
| The goons designed and drawn: the `StreetGoon` section of `docs/CHARACTERS.md`, the `GOON-APOSE` prompt in `docs/prompts.md`, `GEM2-GOON` in `docs/prompts-gemini.md`, and `Art/Refs/StreetGoon_apose.png` | Fri Nov 13, 10:05 -> 10:30 AM Pacific, M Station | Jam work, and **no third-party service touched the picture**. The design text and both prompts were written from scratch during the jam; the reference sheet was drawn on our own RTX 3090 by ComfyUI + Qwen-Image (already declared as a tool above) through the jam-written `tools/gen_images.py`. **0 credits, nothing uploaded anywhere.** Three takes went into the gitignored `Art/Refs/gen/`; take 2 is the pick and the only one committed - it is the only take with cuffs at the wrists rather than rolled sleeves. Until this point no document in the repo said what a goon looks like, though `BP_Goon` had been playable since the first build wearing Epic's mannequin |
| The goons given a body, twice: `Art/Blender/export/Characters/StreetGoon/` (`SK_StreetGoon.fbx`, `T_StreetGoon_BaseColor.png`) and `Art/Blender/export/Characters/StreetGoonTrellis/` | Fri Nov 13, 10:30 AM -> 12:00 PM Pacific, M Station | Jam work, from our own jam-made reference sheet `Art/Refs/StreetGoon_apose.png`. **The canonical model was made on meshy.ai in our own browser** (Meshy named it *Crimson Enforcer*), remeshed to 30K Quad, Smart Rigged and downloaded as the animate-phase GLB - **35 credits**, the remesh and rig free. **The fallback was made locally on our own RTX 3090 with TRELLIS.2** (Microsoft, MIT licence, already declared as a tool) for **0 credits, nothing uploaded**, while the meshy.ai session was logged out. Both were processed into Unreal-ready FBX with Walk and Idle by `Art/Blender/meshy_character.py` and `Art/Blender/trellis_character.py` respectively; both scripts **are** declared pre-jam scripts in sections 1-2 and neither was modified for this. Meshy and TRELLIS are AI tools and are already credited in `CREDITS.md`; the models are scored as our own work. Neither is imported into Unreal - that is the builder's job, and M Station is the maker |
| The city, the coffee shop and the street clutter: `Art/Blender/jumpcut_city_kit.py`, `Art/Blender/export/City/` (44 `SM_*.fbx`, `city_layout.json`, `city_models.json`), `tools/jumpcut_city_layout.py`, `tools/jumpcut_city_place.py`, `docs/CITY.md`, `docs/media/2026-11-13-city-*.jpg`, `docs/media/2026-11-13-cafe-interior.jpg` | Fri Nov 13, 11:20 AM -> 1:50 PM Pacific, M Station | Jam work, written from scratch during the jam, and **no third-party service touched any of it**. Every one of the 44 models is **procedural geometry built by our own jam-written Blender script** on our own machine - no image-to-3D, no generated art, no reference picture, **0 Meshy credits and nothing uploaded anywhere**. The check pictures are Blender renders of those same meshes, not generated images. Blender is a tool and is already credited in `CREDITS.md`. `Art/Blender/jumpcut_city_kit.py` is **new jam work** and is *not* a declared pre-jam script even though it sits beside ones that are: it reuses techniques (real-scale UVs, flat facade tiling) read from the pre-jam `city_kit.py` and `real_kit.py` in the same folder, but shares no code with them and neither of those was modified. **Section 15d:** every sign in the kit is a blank lit panel or an invented abstract glyph block - no real shop name, no logo, nothing readable, nothing traced off a photograph of a real street |
| The player re-made to fix a measured colour defect: `Art/Refs/CafeWalker_apose.png` (redrawn), `Art/Blender/export/Characters/CafeWalker/` (`SK_CafeWalker.fbx`, `T_CafeWalker_BaseColor.png`, both **replaced**), the rewritten `MC-APOSE` prompt in `docs/prompts.md`, and `docs/media/2026-11-13-walker-colour-fixed.jpg` | Fri Nov 13, 12:00 -> 1:35 PM Pacific, M Station | Jam work. The reference sheet was redrawn on our own RTX 3090 by ComfyUI + Qwen-Image (already declared as a tool) through the jam-written `tools/gen_images.py` - **0 credits, nothing uploaded**; three takes went to the gitignored `Art/Refs/gen/`, take 2 is the pick and the only one committed. The model was then made on **meshy.ai in our own browser** (Meshy named it *The Reluctant Barista*) from that sheet, remeshed to Fixed 30K Quad, Smart Rigged, and processed by the pre-jam `Art/Blender/meshy_character.py`, which was **not** modified. **35 credits**; the remesh and the rig were free. This **supersedes** the Nov 12 `CafeWalker` model (*The Weary Apron*) in the row above, which is kept in git history rather than beside it. The reason is measured and recorded in `CHARACTERS.md`: the old cream shirt sat dE76 8.8 from his own face tone against a threshold of 14; the new khaki shirt measures 40.3. Meshy, ComfyUI and Qwen-Image are AI tools and are already credited in `CREDITS.md`; the sheet and the model are scored as our own work |

| Beat 4's Splice power and its HUD box: the nine `Splice*` fields, the `SpliceStart` function and the **Left Shift** / `Gamepad_FaceButton_Right` poll added to `BP_Player.PlayerTickInput`, `SpliceBox`/`SpliceIcon`/`SpliceKey`/`SpliceBar` and the `HudRefresh` patch on `WBP_HUD`, and the recipe `tools/splice_graphs.py` | Built and measured Fri Nov 13, 17:28 → 17:40 UTC, GameStation; lost unsaved when that editor quit; rebuilt and committed Fri Nov 13, 18:20 UTC and re-measured 19:05 UTC, Justin's Mac mini | Jam work, written from scratch during the jam against the Team Owner's Nov 13 beat-4 and beat-5 decisions. Every Blueprint graph, variable, tuned value and HUD widget is ours. **Nothing was generated and no asset was brought in** — the power is pure Blueprint logic acting on bodies that are already declared in the rows above. `tools/splice_graphs.py` is **jam work and is not a declared pre-jam script**, even though it sits in `tools/`: it was written during the jam, as the recipe that put the power back after the editor quit with it still in memory |
| The set pieces for beats 1 to 3: eleven more models in `Art/Blender/jumpcut_city_kit.py` (`SM_CrashCar`, `SM_Shrapnel`, `SM_YardWall_1250`, `SM_YardWall_3040`, `SM_Hoarding_990`, `SM_PlazaGate`, `SM_CheckpointPost`, `SM_CheckpointTaken`, `SM_PlazaPaving`, `SM_Crosswalk`, `SM_RoadLines` in `Art/Blender/export/City/`), the `REPLACES` check and 21 new placements in `tools/jumpcut_city_layout.py`, the `add` mode and `set_ground()` in `tools/jumpcut_city_place.py`, `docs/media/2026-11-13-set-*.jpg` | Fri Nov 13, 4:30 PM -> 4:45 PM Pacific, M Station | Jam work, written during the jam. **Procedural geometry from our own jam-written Blender script** - no image-to-3D, no generated art, no reference picture, **0 Meshy credits, nothing uploaded**. The pictures are Blender renders of those meshes. **Section 15d:** the car carries no badge, plate text or real model's lines; posters, signs and the slate are blank panels or invented blocks, no words. |

**Where that work was authored.** The anime look, the coffee shop and the hero were built in our practice
project on GameStation, because the Unreal editor and the MCP were already running against it, and then carried
into this repo with Unreal's Migrate. In *this* repo that shows up as a single commit, `c19e0ad`, which is a
thin record of several hours of work. The step-by-step trail is committed in the practice repo
(`megajam-2026-practice`, commit `c86ddd6`, Thu Nov 12) with the file timestamps intact. We would rather point
at it than have §7h's "Epic may ask for your Git history" meet one squashed commit.

**From that commit onward, jam content is authored in this repo.** That is also what our own
`.claude/skills/jam-rules-check` already told us to do, and we didn't, for the first night.

## How to check any of this

- This repo's history: `git log --name-status` — `e9bfc06` is the pre-jam set, everything after it is jam work
  (the one declared exception, `docs/TEAM_SYNC_BACKUP.md`, is in section 4).
- The practice repo it came from, with its own full history: `github.com/Waffle-Widgets/megajam-2026-practice`
  (108 commits by the time the jam opened; worked on Nov 1–11).
- File timestamps for the jam work: practice-repo commit `c86ddd6`.
- Every asset we didn't make ourselves, with source and licence: `CREDITS.md`.
- The devlog, which narrates all of it: `docs/devlog/`.

## Before we submit, re-check

- [ ] Add anything else prepared before Nov 12 that we bring in later (a script, a prompt, a config).
- [ ] Move any new helper script written *during* the jam into the "made during the jam" section, not the pre-jam one.
- [ ] Paste the short version above into the itch.io submission's pre-jam declaration.
- [ ] Fill the "Tools you used" field: Claude Code (Anthropic), Gemini (Google), ComfyUI + Qwen-Image (local),
      Meshy (meshy.ai), TRELLIS.2 (Microsoft, MIT, local), Tripo (tripo3d.ai), Blender 5.2, Unreal Engine 5.8
      and Epic's Unreal MCP.
- [ ] Check `CREDITS.md` is still complete.
