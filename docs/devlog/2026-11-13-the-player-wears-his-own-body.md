# 2026-11-13 — The player wears his own body (Justin's Mac mini)

- **What we asked for:** do the tickets assigned to this machine. This is #7, the third of four.

- **Prompt(s) we gave the agent:** the actual words, quoted:

  > Another agent made github issues out of tasks to be completed. Take a look and comment and close on
  > anything we've worked on already. Then do any that were assigned to us that are still pending

- **What happened.**

  **The ticket reads like a mesh swap and it is not one.** There were already a `SK_CafeWalker` in Unreal,
  twenty retargeted mannequin clips and a blend space — and none of it was usable, because that import is
  the `trellis_character.py` build with **23 bones named the way Epic's mannequin names them**, while the
  committed FBX is Meshy's Smart Rig with **69 bones called `Bone_000`**. Two different skeletons wearing
  the same character's name. The only thing that carries over between them is nothing.

  So the new body needed the retarget the cleaver boss needed: the chains mapped by hand, because
  `apply_auto_generated_retarget_definition()` recognises mannequin bone names and finds nothing on a
  Smart Rig.

  **`tools/unreal_retarget_meshy.py` does that mapping by itself**, using the same reasoning
  `Art/Blender/meshy_character.py` uses in Blender: the parentless bone is the root, its child is the hip,
  the branch whose **end** reaches highest is the spine, the ones that end low are legs, the chest is where
  the spine splits, and the arms and head hang off the chest. It found all nine chains and `auto_map_chains`
  paired every one. It took one bug to get there, and it is worth writing down: my first version asked how
  high each branch *reaches* rather than how high it *ends*, and a thigh is high — so it found zero legs.

  **Then the template's whole anim blueprint retargeted too.** Rather than hand-build a three-node one,
  `ABP_Unarmed` went through the same batch operation, which brought the locomotion state machine and its
  `DefaultSlot` across with every animation reference remapped. Montages play with no graph work at all.

  **The float trap fired again and it is a big number.** Meshy keeps the root bone at pelvis height in the
  reference pose, so 19 of 25 root-motion clips lifted him **86 to 90.6 cm** off the floor. That is the
  cleaver boss's bug (#46) on a new character, and the same one-property fix brings it to −4.6 to 0.

  **And his FBX carried no texture**, exactly like the coworker's an hour earlier — same hole, same fix.

- **What we checked.** In PIE: mesh `SK_CafeWalker`, 69 bones **posed**, head 162.5 cm above the feet, feet
  within 4 cm of the capsule bottom, anim instance `ABP_Unarmed_CWM_C`, all four montage variables resolving
  to the new `AM_CafeWalker_*` assets. The asset thumbnails show the khaki shirt and green apron on every
  retargeted clip, so the retarget produced real poses rather than a heap.

- **What we did not check.** Nobody has played it. Whether the mannequin's punches read correctly on a
  slimmer body is a judgement, not a measurement. The old cream model is still in the repo, unused.

- **What we learned.** Two assets can share a character's name, a folder and a colour scheme and still have
  nothing in common where it matters. Before trusting an "already imported" character, read its bone names.
