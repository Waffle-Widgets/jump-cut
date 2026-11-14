# 2026-11-14 — The texture was never there to download (M Station)

- **What we asked for:** "did you push all the new models and textures?" — and then, when the answer came back
  that `CafeWalkerV2` and `CafeCoworkerV2` were the only two character folders in the repo with no
  `T_*_BaseColor.png`, and that neither body was in Unreal at all: *"yes"* — go and get the two base-colour
  textures from Meshy, then import both bodies into the game.

- **Prompt(s) we gave the agent:**
  > did you push all the new models and textures?
  >
  > yes

- **What happened:**

  The plan was a download. It turned out there was nothing to download, and finding that out is most of this
  entry.

  **Meshy's remesh step discards the texture.** Rigging only runs on the *remeshed* asset, so the body you can
  actually animate is untextured — it renders plain grey in Meshy's own viewer, and its FBX export embeds a
  single 2048×2048 `texture_0_normal.png`, a tangent-space normal map, and no colour map at all. We had read
  that missing `T_*_BaseColor.png` as a download someone forgot to take. It was not. There is no colour on that
  asset to take.

  **The colour does exist — on the 365,038-face asset from before the remesh — and its `glb` export carries it
  where its `fbx` export does not.** That is worth writing down on its own: same asset, same dialog, and the
  glTF image `texture_0` is wired to `baseColorTexture` in the GLB while the FBX ships only the normal. So both
  maps came down as GLB, 0 credits, and the base colour extracted cleanly: a real atlas, green apron, khaki
  shirt, dark trousers, skin, white shoes.

  **And it was useless on the rigged mesh, which is the trap.** The remesh regenerates UVs. The high-poly map
  and the rigged body are in different UV spaces, so dropping one onto the other renders as **camouflage
  noise** — the left-hand panel of `docs/media/2026-11-14-cafewalker-v2-texture-bake.jpg`. Nothing errors. A
  2048 map loads, a mesh samples it, every scripted check passes, and the character is ruined. It is only
  obvious because somebody rendered it and looked.

  So the map is **baked**, not downloaded: `Art/Blender/bake_meshy_basecolor.py` makes the high-poly emit its
  base colour and bakes `EMIT` selected-to-active onto the rigged mesh's own UVs, in Cycles at 1 sample. EMIT
  rather than DIFFUSE on purpose — a diffuse bake would fold in a light rig nobody chose. The one thing that
  can silently go wrong is alignment, because Meshy's two exports are not in the same units or origin (1.902 m
  centred on the origin vs 1.75 m with the feet at zero), so the script scales and seats the source first and
  **prints the per-axis residual**. On the player it is under 2 mm. A bad align does not error either; it just
  leaves bald patches.

  **Then the import refused, for a reason no bone diff could show.** `SK_CafeWalkerV2_oldrig.fbx` is the new
  mesh reskinned onto the shipped 69-bone armature (#96), and the whole point is that it binds to the existing
  `SK_CafeWalker_Skeleton` so every clip, montage and anim blueprint still applies. All 69 bone names and all
  69 parent links matched exactly — we diffed them — and Interchange still logged **"cannot merge bone tree
  with the existing skeleton."** The cause was one level above the bones: **Unreal makes the armature OBJECT's
  name the root bone of the skeleton**, and the reskin script had left its armature called `OLD_Armature`
  where the shipped one is `Armature`. Renamed the object and its data, re-exported, and the same import logs
  `Success - 0 error(s)`.

  The nastiest part of that is how it fails. It is **not fatal**. The SkeletalMesh is still created, and it
  still reports the skeleton you asked for — so `mesh.skeleton == skel` passes by object identity, the vertex
  count is right, the material is right, and the only thing anywhere that says the bind is wrong is one line
  in the engine log. Our first run printed a clean bill of health over a broken import. Read the
  `Warning/Error Summary` at the end, not just the script's own output.

  **What landed.** `/Game/Game/Imported/CafeWalkerV2/SK_CafeWalkerV2` on the **existing**
  `SK_CafeWalker_Skeleton`, 69 bones; `/Game/Game/Imported/CafeCoworkerV2/SK_CafeCoworkerV2` on a new 28-bone
  skeleton of her own; both on `MI_*V2` instances of `M_AnimeChar` with the baked map in `Tex`, assigned on the
  **mesh asset's** slot rather than an actor override — the distinction that made the goons render flat in PR
  #105. The import is `tools/unreal_import_char_v2.py`, headless, and it refuses rather than quietly building
  a second skeleton.

  One smaller thing fixed on the way: `get_editor_property('materials')` hands back **copies** of the slot
  structs, so mutating them in place is silently discarded and the mesh keeps its Interchange import material.
  Fresh `SkeletalMaterial` entries have to be built and the whole array set back.

- **What it cost:** 0 Meshy credits. Two GLB downloads of models already paid for, two Blender bakes on this
  machine, and four headless Unreal runs.

- **What is still wrong, and what nobody has checked:**
  - **`BP_Player` still wears the Nov 13 body.** Importing is not swapping. The swap is one property on
    `BP_Player.CharacterMesh0` and it is deliberately left for a person — the main character the day before
    submission is not something to change untested.
  - **The coworker is art only.** She is on her own skeleton with no clips, because her reskin failed (#101):
    her two A-poses are 13.5 cm apart per hand, and posing the hand bone moves 1,384 vertices on the shipped
    mesh against 30 on the reskinned one. `BP_Coworker` must not be pointed at her.
  - **Her apron straps still cross in an X on the back**, which the character lock forbids. The bake makes it
    plainly visible for the first time; it does not fix it. Still #101.
  - **Nobody has played any of this, and nobody has seen either body under the cel shader.** Every picture here
    is a Blender render of the committed FBX with the committed texture on its own UVs.
