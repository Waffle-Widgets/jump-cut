# 2026-11-12 - The mob boss takes the plaza (GameStation)

- **What we asked for:** one word - "Mob boss" - answering the question the agent had asked at the end of the
  previous turn: is the plaza boss the Splice mob boss the pitch describes, or the crash driver that was built?

- **Prompt(s) we gave the agent:** "Mob boss".

- **What happened:**
  - The open question in `ROADMAP.md` offered three answers: keep the built boss, turn him into the mob boss, or
    drop him. "Mob boss" was read as the middle one, and that choice is worth stating plainly: **every number the
    playtest settled survives** - 240 health, 15 damage, 380 move speed, the 115 cm capsule, the warning sign, the
    gate he opens. Only his skin changed.
  - The first thing that turned up was that **no character of ours had ever actually been put into a Blueprint**.
    `SK_CafeWalker` has been retargeted and imported since the afternoon, but `BP_CafeWalker` was still wearing
    `SKM_Quinn_Simple`. This was the first time one of our models was wired to anything.
  - The scale was computed rather than copied. The mannequin boss ran at scale 1.3 in a 115 cm half-height
    capsule; our boss is 178.0 cm, so 230/178 = **1.2921** fills the same capsule exactly. The silhouette the
    playtest saw is unchanged - he is just a different man inside it.
  - **Unreal cannot characterise a Meshy skeleton.** Meshy's Smart Rig names every bone `Bone_000`...`Bone_082`,
    and `apply_auto_generated_retarget_definition()` came back **False** with no root and no chains at all. The
    repo's own `tools/unreal_retarget_mannequin.py` has a manual fallback, but it names mannequin bones
    (`upperarm_l`, `thigh_r`), which this skeleton does not have.
  - So the chains were read off the rig in Blender and named by hand. Two measurements did the work: the character's
    **right is `-X`** in that file (the toes point `-Y`, and right = forward x up), and the two bones with **five
    children each** are the wrists. That gave `Bone_019` as the right hand and a nine-chain map that fuzzy-matched
    the mannequin's chains one for one. Unreal's mocap idle, walk and jog now exist on his own skeleton as `*_CB`.
  - **The editor lies about whether a character is there.** With the mesh swapped and the blend space set, the
    boss rendered as a dark lump on the ground - the skeleton collapses in the editor because a single-node
    animation instance is not initialised until play begins. Three screenshots were taken before the obvious test
    was run: **start Simulate**. In Simulate he stood up in the mocap idle, correct and complete. Anyone judging a
    character swap from the editor viewport alone will think they broke it.
  - The facing was wrong twice and fixed by looking, not by reasoning: 0 showed him in profile, 90 showed his
    back, **270** faced him down the street - the same yaw the mannequin used, which is the real lesson.
  - The cleaver's socket transform was **solved**, not dragged. The prop's `+X` end is the 4.5 cm wooden grip and
    its `-X` end is the full-height blade, so the grip point is mesh-local `(15, 0, 7.6)`; asking for the blade to
    point forward and down gives socket `(-16.437, -1.978, 2.945)` rotated `(-31.84, -10.18, 39.68)` on
    `Bone_019`. It landed in his fist first try.

- **What it cost:** no credits, no new art. One new Blueprint function (`BossDriveAnim`, four nodes), one
  construction-script attach, 18 retargeted animations and a blend space.

- **What is still open, and said plainly:** he **looks** like the Splice mob boss and still **hands over Freeze
  Frame**. `BossHandOverPower` calls `PlayerGrantFreezeFrame`, the Blueprint is still named `BP_BossFreeze`, and
  `BossUsesFreeze` is still false. That is now the open question in `ROADMAP.md` in place of the one just closed.
  Nobody has played this build either - it has been seen in Simulate, from the editor camera, standing still.

![The mob boss in the plaza, cleaver in his right hand](../media/MOB-BOSS-PLAZA.png)
