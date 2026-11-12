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

If a file is in `e9bfc06`, we are declaring it as pre-jam material. If it arrived after, it is jam work.

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
| `tools/make_sfx.py` | Generates sound effects and music loops from pure Python — no samples, nothing to credit. |
| `tools/gen_images.py` | Generates reference images locally. |
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
| `tools/setup_mcp.ps1`, `tools/setup_mcp.sh` | Thu Nov 12 8:40 AM Pacific | Written *during* the jam. They register each computer's MCP servers; the shared `.mcp.json` was changed the same day to drop the Windows-only Blender path |

**Where that work was authored.** The anime look, the coffee shop and the hero were built in our practice
project on GameStation, because the Unreal editor and the MCP were already running against it, and then carried
into this repo with Unreal's Migrate. In *this* repo that shows up as a single commit, `c19e0ad`, which is a
thin record of several hours of work. The step-by-step trail is committed in the practice repo
(`megajam-2026-practice`, commit `c86ddd6`, Thu Nov 12) with the file timestamps intact. We would rather point
at it than have §7h's "Epic may ask for your Git history" meet one squashed commit.

**From that commit onward, jam content is authored in this repo.** That is also what our own
`.claude/skills/jam-rules-check` already told us to do, and we didn't, for the first night.

## How to check any of this

- This repo's history: `git log --name-status` — `e9bfc06` is the pre-jam set, everything after it is jam work.
- The practice repo it came from, with its own full history: `github.com/Waffle-Widgets/megajam-2026-practice`
  (108 commits by the time the jam opened; worked on Nov 1–11).
- File timestamps for the jam work: practice-repo commit `c86ddd6`.
- Every asset we didn't make ourselves, with source and licence: `CREDITS.md`.
- The devlog, which narrates all of it: `docs/devlog/`.

## Before we submit, re-check

- [ ] Add anything else prepared before Nov 12 that we bring in later (a script, a prompt, a config).
- [ ] Move any new helper script written *during* the jam into the "made during the jam" section, not the pre-jam one.
- [ ] Paste the short version above into the itch.io submission's pre-jam declaration.
- [ ] Fill the "Tools you used" field: Claude Code (Anthropic), Gemini (Google), TRELLIS.2 (Microsoft, MIT, local),
      Tripo (tripo3d.ai), Blender 5.2, Unreal Engine 5.8 and Epic's Unreal MCP.
- [ ] Check `CREDITS.md` is still complete.
