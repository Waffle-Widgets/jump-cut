# Credits

Every asset we did not create ourselves goes here, added the moment it enters the project.

| Asset | Used for | Source / tool | Creator | License | Added by |
| --- | --- | --- | --- | --- | --- |
| Third Person template content (mannequin, level prototyping meshes, input actions) | Starting point of the project | Unreal Engine 5.8 Third Person Blueprint template | Epic Games | Unreal Engine EULA | bootstrap script, 2026-11-12 |
| Mannequin animations copied onto our hero (`Content/Game/Imported/CafeWalker/Anims/*_CW`: idle, walk, jog, jump) | The hero's movement | Unreal Engine 5.8 Third Person template, retargeted with `tools/unreal_retarget_mannequin.py` | Epic Games | Unreal Engine EULA (sourced, not scored) | Claude on GameStation, 2026-11-12 |
| Hero character drawing (`Art/Refs/cafe_walker_ref.jpg`) | Reference for the hero model | AI-generated with Gemini from our own prompt; redrawn in an A-pose with Tripo's image tool | Team (AI-generated) | Ours | Claude on GameStation, 2026-11-12 |
| Street models: sakura tree, kei van, hatchback, city bicycle, delivery scooter (`Art/Refs/Street/*_ref.jpg`, `Art/Meshy/{SakuraTree,KeiVanM,Hatchback,BicycleM,ScooterM}/`) | Replace the block-model tree, van, bicycle and scooter on the street | Reference pictures AI-generated with Gemini from our own prompts (kept in `Art/Refs/Street/PROMPTS.md`), models AI-generated with Meshy Image to 3D on its website (175 credits), resized, reduced and re-baked with `Art/Blender/meshy_prop_bake.py`. Invented designs: no real make, model, badge or plate | Team (AI-generated) | Ours | Claude on M Station, 2026-11-15 |
| Street and cafe props, second batch: vending machine, street lamp, planter, pot row, dumpster, A-frame sign, bench, espresso machine, cash register, pastry case, tall plant, small plant, bar stool (`Art/Refs/Street/*_ref.jpg`, `Art/Meshy/*M/`) | Replace 13 more block models on the street and in the cafe | Reference pictures AI-generated with Gemini from our own prompts (`Art/Refs/Street/prompts_batch2.json`), models AI-generated with Meshy Image to 3D on its website (490 credits for 14; the gas-bottle cage was dropped), re-baked with `Art/Blender/meshy_prop_bake.py`. No brand, text or logo on any of them | Team (AI-generated) | Ours | Claude on M Station, 2026-11-15 |
| Cafe furniture, third batch: chair, table, service counter, back-bar shelf, banquette, window ledge, menu chalkboard, pendant lamp, projecting sign (`Art/Refs/Street/Cafe*_ref.jpg`, `Art/Meshy/Cafe*M/`) | Replace the last nine block models inside the cafe | Reference pictures AI-generated with Gemini from our own prompts (`Art/Refs/Street/prompts_batch3_cafe.json`), models AI-generated with Meshy Image to 3D on its website (315 credits), fitted to the kit pieces' boxes with `Art/Blender/meshy_prop_bake.py`. The only word on any of them is "Menu" on the chalkboard | Team (AI-generated) | Ours | Claude on M Station, 2026-11-15 |
| Alley and street props, fourth batch: gas bottles in a rack, electricity meter cabinet, ventilation duct (`Art/Meshy/{GasBottlesM,MeterBoxM,DuctRunM}/`) | Replace three more block models (tickets #89, #86, #85) | AI-generated with Tripo text-to-3D on its website from our own prompts (165 credits; the prompts are in the devlog entry `2026-11-15-three-props-from-tripo.md`), no reference picture, re-baked with `Art/Blender/meshy_prop_bake.py`. No brand, text or logo on any of them | Team (AI-generated) | Ours | Claude on GameStation, 2026-11-15 |
| Hero character model (`Art/Refs/CafeWalker_tripo_apose.glb`, `SK_CafeWalker_Walk`, `T_CafeWalker_BaseColor`) | The playable character in `Lvl_Cafe` | AI-generated with Tripo (tripo3d.ai, jam partner) from our drawing, slimmed with its Retopology, rigged with `Art/Blender/trellis_character.py` | Team (AI-generated) | Ours | Claude on GameStation, 2026-11-12 |
| Music: "song21 0" (Mysterious Ambience), as `MUS_TitleMystery` | Title screen music | OpenGameArt: https://opengameart.org/content/mysterious-ambience-song21 (taken from Justin's Cerberus app) | cynicmusic | CC0 1.0 (sourced, not scored) | Claude on Justin's Mac mini, 2026-11-15 |
| Music: "jrpg battle full 0" (JRPG Epic Rock Battle Theme 1), as `MUS_Gameplay_Sourced` | Gameplay music | OpenGameArt: https://opengameart.org/content/jrpg-epic-rock-battle-theme-1 (taken from Justin's Cerberus app) | HydroGene | CC0 1.0 (sourced, not scored) | Claude on Justin's Mac mini, 2026-11-15 |
| Music: "Epic Boss Battle [Seamlessly Looping]", as `MUS_GameplayBossBattle` | Boss fight music, from the boss intro on | OpenGameArt: https://opengameart.org/content/boss-battle-music (taken from Justin's Cerberus app) | Juhani Junkala (posted by SubspaceAudio) | CC0 1.0 (sourced, not scored) | Claude on Justin's Mac mini, 2026-11-15 |

The three music licences are as recorded in the Cerberus app's `apps/app/static/sounds/SOURCES.md`; they were not
re-checked on the OpenGameArt pages. Each track was converted to WAV, trimmed to a clean loop and re-levelled
(`tools/mus_loopfix.py`). Our own generated loops (`MUS_Title`, `MUS_Gameplay`) stay in the project; the
`UseGeneratedMusic` switch on `BP_OpeningDirector` plays them instead.

## Team
- **Manuel Mendez** — Team Owner (submits the entry). Driver: Unreal implementation on GameStation, art pipeline on M Station, devlog and video.
- **Justin Catrambone** (GitHub `allbarkdev`) — Director: playtesting and review on his Mac mini, making art outside Unreal.

Full names and the email on each member's Epic account go on the itch.io entry form (§1c, §2, §13), not in this
public repo — `docs/TEAM.md` records only whether we have each person's address.

## AI tools used
Everything here is generated by us from our own prompts, so it is our work and is scored (§15c). Sourced assets
go in the table above instead. This list is also what goes in the itch.io form's "Tools you used" field.

- Claude Code (Anthropic) — implementation in Unreal via MCP, and the character design work on M Station
- Gemini (Google) — art and second opinions
- Qwen-Image, run locally through ComfyUI on **both** machines' graphics cards (M Station's 3090 since Nov 12;
  GameStation's RTX 5090 from Nov 13, installed by `tools/install_comfyui.sh` with the same model files so the
  two draw in the same hand) — the character reference sheets in
  `Art/Refs/` (prompts kept in `docs/prompts.md`, so every picture can be traced to the words that made it).
  Nothing is sent to a service: it runs on our own hardware.
- Meshy (paid, cloud) — image-to-3D and rigging for the characters, and image-to-3D for the five street models
  (Nov 15). Used from the website, not the API.
- Tripo (tripo3d.ai, a jam partner) — image-to-3D for the `CafeWalker` hero made on the jam's first night, its
  A-pose redraw and retopology (the model is in the table above).
- TRELLIS.2 (Microsoft, MIT) — image-to-3D models, run locally
- Blender — rigging, clean-up and animation, run by script, and driven by Claude through Blender's official MCP
  (Blender Lab's `blender_mcp`). We run the current release rather than a pinned one: 5.3.0 on Justin's Mac mini
  from Nov 14, 5.2 on M Station
- Unreal Engine 5.8 (Epic Games) with Epic's Unreal MCP plugin — the engine the game is built in, and how Claude drives
  the editor (Blueprints, levels, materials, Play-mode checks)

## Made before the jam
This file covers assets. Our **tools, scripts, agent instructions and prompt library** were prepared before the
jam opened, which rule §7h allows and the itch.io page asks us to declare. They are listed file by file in
[`docs/PREJAM.md`](docs/PREJAM.md) — read that alongside this file at submission time.
