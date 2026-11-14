# 2026-11-14 — The player puts on the new body (M Station)

- **What we asked for:** the body we remade — the one whose apron is a front panel instead of a skirt — was in
  the project but not on the character. One property stood between "in the repo" and "in the game", and it was
  left for a person to say yes to, because the main character the day before submission is not something to
  change on an agent's own judgement.

- **Prompt(s) we gave the agent:**
  > do it

- **What happened:**

  The change itself is a single line: `BP_Player.CharacterMesh0.skeletal_mesh_asset` goes from
  `/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker` to
  `/Game/Game/Imported/CafeWalkerV2/SK_CafeWalkerV2`. Everything interesting is either the checking around it
  or something we found while looking at the result.

  **Why it can be one line.** V2 was reskinned onto the *existing* 69-bone `SK_CafeWalker_Skeleton` (#96), and
  the two meshes resolve to that skeleton as the **same object**, not merely the same path. So the component's
  `anim_class` — `ABP_Unarmed_CWM` — and all five `AM_CafeWalker_*` montages carry straight over. The saved
  asset's name table proves it from outside Unreal: `ABP_Unarmed_CWM`, `AM_CafeWalker_PunchA`, `PunchB`,
  `Finisher`, `HitReact` and `Death_Authored` are all still there, `SK_CafeWalker` is gone, and
  `SK_CafeWalkerV2` is in its place.

  **Two things that would have been easy to miss.** Both bodies measure **175.0 cm with feet at z = 0**
  (175.01 and 175.00), so the component's `z = -90` offset seats him exactly as before — a different height
  there would have sunk him into the floor or floated him, with nothing erroring. And the level holds a
  *placed* player, `Player_Main`: this project has been burned before by a placed actor keeping its own copy of
  a setting in its external-actor package, so we read that package's name table directly. It imports no
  skeletal mesh at all, so it has no override and the change reaches it. Confirmed afterwards by asking the
  loaded level what the actor is actually wearing.

  `tools/unreal_player_body_v2.py` does it, and refuses rather than guesses: it will not swap if V2 is not on
  that skeleton, and it will not save if `anim_class`, `override_materials` or the relative transform moved, or
  if the material slot does not resolve to an `MI` parented to `M_AnimeChar`. Then `measure` was run again in a
  **fresh process**, because a value read back in the process that set it proves nothing about what reached
  disk.

  **Then we looked at him, which is where the useful part came from.** In the editor, under the cel shader, the
  apron reads as a front panel with trousers visible down both sides, and from behind he is a plain shirt and
  two separate trouser legs. The skirt is gone *in the game*, not just in a Blender render.

  **But his face and shirt render blown to near-white, and we nearly filed that as a regression.** The
  committed texture has eyes, eyebrows and a khaki shirt — we opened it and looked. So we spawned the *same V2
  mesh* as a plain `SkeletalMeshActor` a metre away and photographed both in one frame, same light, same
  shader. The spawned one keeps its face and its khaki shirt. The player does not. Same mesh, same material,
  same frame.

  The difference is `render_custom_depth`: `True` on `BP_Player.CharacterMesh0`, `False` on a fresh component.
  The live look material `MI_AnimeLook_JumpCut` holds `CharLevel 0.95`, and that character band only touches
  custom-depth pixels — so the player's light skin and khaki shirt clip to white while an identical character
  beside him does not. V1 had the same component setting, so **the swap did not cause it**. It is #72, and it
  now has a control instead of an argument.

- **What we learned:**
  - A mesh swap is only one property **if the new mesh resolves to the same skeleton object** — check identity,
    not the path string, and check the height too, because the component's Z offset is tuned to the old one.
  - A placed actor can hold its own copy of a component setting in its external-actor package. Read that
    package before assuming a class-default change reaches the thing standing in the level.
  - **Spawn a control.** The quickest way to tell "the art is wrong" from "the shader is doing this" is to put
    the identical mesh in the same frame without the character setup. One screenshot ended a three-day argument
    about where the washout comes from.
  - Verify a saved asset from a **fresh process**, and from outside Unreal if you can — the name table of the
    `.uasset` is readable with nothing but Python and a regex.

- **Media:** ![the player in his new body, and the control that explains the washout](../media/2026-11-14-player-wears-cafewalker-v2.jpg)
