# The model is corrected once, not posed around

*Sun 15 Nov 2026, about 6:12 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the idle still looked wrong after the lean came out.

- **Prompt we gave the agent:**

  > This looks the same as last time

- **What happened:**

  It did look the same, because what was left was never the pose. The last entry listed the model's own faults and
  stopped to ask. This one fixes the two that show most, in the model's rest pose, so no clip has to work around
  them again.

  `Art/Blender/model_tuneup.py`:
  - **Arms.** Everything the upper-arm and forearm bones carry is scaled 1.15 about the shoulder joint, by vertex
    weight, so the shoulder's cloth stays put and the change fades in down the sleeve. The hand rides the wrist and
    grows 1.06. Shoulder to wrist: **48.7 cm to 56.0** (a person his height: 58). The arm is 15 % thicker too,
    which is the other half of "shriveled".
  - **Head.** Measured ear to ear in 12 slices, the head's centre line sat **6.1 cm to his right** of the point
    between his shoulder joints, as sculpted. It is slid 4.0 cm back (the cap), fading out down the neck. The
    idle's remaining neck correction takes up the rest.

  51 bones moved with their vertices. Names, parents, faces, UVs and weights are untouched.

  ![The corrected body in its sculpted pose](../media/2026-11-15-model-tuned-bind.png)

  Measured in the idle afterwards:

  | | before | now | a person |
  |---|---|---|---|
  | shoulder to wrist | 48 cm | 54.8 | 58 |
  | fingertips reach | 72 cm (hip) | 60 (mid-thigh) | 65 |
  | head, sideways from the feet | 4.5 cm to his right | 0.6 | 0 |
  | chest, sideways from the feet | 0.2 | 0.1 | 0 |

  **Every clip rebuilt.** A changed rest pose means every clip is wrong until it is rebuilt, so all 13 were, four at
  a time, and re-imported. In the same pass the stand that every clip starts and ends in (`cw_clip.STANCE`) was
  pointed at the new idle: arms 10 cm out and open-handed, collarbones as sculpted, feet 20 cm apart. That ends the
  foot slide after attacks the last three entries listed as a known flaw.

  The body importer refused the first import: its size guard still held the old arm span (the new A-pose is 8.8 cm
  wider). The guard did its job; its numbers were updated with a comment saying why.

  ![The idle on the corrected body](../media/2026-11-15-idle-tuned.png)
  ![In the game](../media/2026-11-15-idle-tuned-in-game.png)
  ![A punch, the kick, a run stride and the uppercut on the corrected body, in Blender](../media/2026-11-15-actions-tuned.png)

- **Known flaws:**
  - **Attacks and the run were NOT seen in the game.** The scripted punch and walk did not fire during the capture,
    so only the idle was photographed in Play. The action poses were checked in Blender only.
  - `A_CafeWalker_Death_Authored` was not rebuilt (it has no script in this pipeline). It still carries the old
    arm lengths, so his arms shorten when he dies.
  - Any old retargeted clip that still plays anywhere will do the same.
  - The legs are still uneven: one knee 3 degrees, the other 14.
  - The sprint stretches 224 edges (206 before), the uppercut 157 (135 before).

- **What we learned:**
  - When the same complaint survives a fix, the fix was aimed at the wrong layer. Pose, then mesh, then proportions:
    it took three layers to reach the one that was wrong.
  - Change proportions in the rest pose and rebuild, or not at all. Scaling a bone inside one clip would have made
    his arms grow and shrink between clips.
  - A guard that refuses is a guard that works. Update its numbers with the reason; do not switch it off.
