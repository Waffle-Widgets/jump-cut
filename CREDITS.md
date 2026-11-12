# Credits

Every asset we did not create ourselves goes here, added the moment it enters the project.

| Asset | Used for | Source / tool | Creator | License | Added by |
| --- | --- | --- | --- | --- | --- |
| Third Person template content (mannequin, level prototyping meshes, input actions) | Starting point of the project | Unreal Engine 5.8 Third Person Blueprint template | Epic Games | Unreal Engine EULA | bootstrap script, 2026-11-12 |
| Mannequin animations copied onto our hero (`Content/Game/Imported/CafeWalker/Anims/*_CW`: idle, walk, jog, jump) | The hero's movement | Unreal Engine 5.8 Third Person template, retargeted with `tools/unreal_retarget_mannequin.py` | Epic Games | Unreal Engine EULA (sourced, not scored) | Claude on GameStation, 2026-11-12 |
| Hero character drawing (`Art/Refs/cafe_walker_ref.jpg`) | Reference for the hero model | AI-generated with Gemini from our own prompt; redrawn in an A-pose with Tripo's image tool | Team (AI-generated) | Ours | Claude on GameStation, 2026-11-12 |
| Hero character model (`Art/Refs/CafeWalker_tripo_apose.glb`, `SK_CafeWalker_Walk`, `T_CafeWalker_BaseColor`) | The playable character in `Lvl_Cafe` | AI-generated with Tripo (tripo3d.ai, jam partner) from our drawing, slimmed with its Retopology, rigged with `Art/Blender/trellis_character.py` | Team (AI-generated) | Ours | Claude on GameStation, 2026-11-12 |

## Team
- (your name) — Driver
- (teammate's name) — Director

## AI tools used
- Claude Code (Anthropic) — implementation in Unreal via MCP
- Gemini (Google) — art and second opinions
- TRELLIS.2 (Microsoft, MIT) — image-to-3D models, run locally
- Tripo (tripo3d.ai, jam partner) — image-to-3D for the hero, A-pose redraw, retopology
- Blender 5.2 — rigging and clean-up, run by script
