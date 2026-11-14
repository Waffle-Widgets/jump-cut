# 2026-11-13 — The boss floated on his own reference pose (Justin's Mac mini)

- **What we asked for:** item 4 of the beats 1-3 clean-up list, after playing with the city in:

  > Splice Boss is levitating.

- **Prompt(s) we gave the agent:** the line above. This is the second time it was reported; the first time it was
  measured and written up (`CHARACTERS.md`, "he floats about a metre whenever he animates") but not fixed.

- **What happened:**

  **The written diagnosis was wrong, and it was wrong in a way that would have cost a day.** The earlier write-up
  blamed the retarget: the mannequin's pelvis height written into `Bone_001` on top of a floor-level root, "applied
  twice", and the repair it prescribed was to redo the retarget and re-bake all twenty clips. So the first thing
  we did was read the clips, bone by bone, before redoing anything. They were fine. In every one of the 21 clips
  the root `Bone_000` sits at z = 0 and the lowest bone stays within 7 cm of the floor. There was nothing to
  re-bake.

  **So where do 113 cm come from?** From one number nobody had looked at: the skeleton's *reference pose*. Meshy's
  rig keeps its root bone at **pelvis height** (z = 87.26), with the hips 5 cm from it. The retargeted clips move
  that same bone down to the floor, because that is where Epic's mannequin keeps its root. Both are legal. But
  every clip with **root motion** switched on (the 16 walk and jog clips and the two attacks) resets its root
  while it plays, and the setting that says *where to* - "Root Motion Root Lock" - defaults to **Ref Pose**. So
  while he walked, the root went back up to 87.26 and took the whole skeleton with it. 87.26 times his mesh scale
  of 1.2921 is **112.7 cm**. The old table says "107 - 113 cm".

  That also explains the word in the original report - he "*sometimes*" floats. Idle, hit react and death have
  root motion off. He only left the ground when he moved or swung.

  **Measured before touching anything.** Evaluating each clip with root motion extracted, the way the game does:
  all 18 root-motion clips rode **78.8 to 87.3** units high; the other three read 0. Our first probe had read 0
  for everything, because it evaluated the clips *without* extracting root motion - the asset looked innocent
  until it was asked the question the game asks.

  **The fix is one property on 18 clips:** `root_motion_root_lock = AnimFirstFrame`. The first frame has the root
  on the floor with its rotation intact. Not `Zero`, which was the tempting one: `Bone_000` carries the rig's
  90-degree up-axis turn, and Zero would have wiped it and laid him on his side.

  **Then the live boss, not the asset.** `tools/boss_feet_test.py` presses start, wakes him, stands the player in
  front of him and reads the world height of all 83 bones ten times a second:

  | State | lowest bone above the capsule bottom, before | after |
  |---|---|---|
  | asleep, as placed | 0 | **0.0** |
  | awake, standing | 0 | **-3.6 to 0.0** |
  | walking at 380 cm/s | 107 to 113 | **-5.9 to 0.0** |
  | cleaving | 94 to 113 | **-10.8 to 0.0** |
  | hit react | (not measured) | **-14.1 to 0.0** |

  96 samples, movement mode `MOVE_WALKING` on every one.

  **The sibling was checked.** The player's `CafeWalker` clips came through the same retarget. All 20 read 0: his
  skeleton is our own Blender rig with the mannequin's bone names, and its reference pose already has the root on
  the floor, so Ref Pose and the first frame agree. Nothing changed there.

- **What we learned:**
  - **A diagnosis that fits the number is not yet the cause.** "117.6 cm is the lift we measure" was true and
    persuasive, and the mechanism attached to it was invented. Read the data the theory is about before paying
    for the repair it asks for. This one would have re-baked twenty clips and floated exactly as before.
  - **Evaluate an animation the way the game will.** With root motion on, the pose you see in a tool and the pose
    the game plays can differ by the whole reference-pose root offset.
  - **For any rig whose reference-pose root is not at the origin, set Root Motion Root Lock to AnimFirstFrame** on
    every root-motion clip. Meshy's Smart Rig is such a rig, so the street goon will need the same when his model
    goes onto `BP_Goon`.
  - **Not checked:** nobody has watched him walk. The numbers say his feet are on the ground; whether the walk
    *looks* right is a person's call. His swinging foot dips up to 14 cm below the capsule bottom mid-cleave -
    into the floor - which the old float was hiding.

- **Media:** none; the result is the table.
