# The apron gets its own bones, the arms stop thinning, and the attacks learn to flow

*Sun 15 Nov 2026, about 3:15 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`), one Fable 5.2 helper on the attacks*

- **What we asked for:** after the shoulder fix, an honest answer about what a skin rework would and would not cure,
  and then the cure.

- **Prompt we gave the agent:**

  > Go ahead and merge what we have for now. If you cured it would that fix all the issues? Do we need to create
  > the clothes separate from the character? The apron looks stuck to the character instead of being its own thing.
  > The arms look really thin when he starts running. The attack animations stretch out the model in weird ways.
  > The attack animations look cheap, I'm not sure how we can make them look smoother or more fluid. If you can fix
  > all of these issues then do so properly and then be ready to apply fixes to other characters.

- **The answers, before the work:**
  - *Would curing the skin fix everything?* No. Three different faults were being described as one. Thin arms and
    stretching are DEFORMATION. An apron that copies the legs is RIGGING. Attacks that look cheap are ANIMATION.
  - *Do the clothes need to be separate from the character?* Not as separate models. The apron needs bones of its
    own. That turned out to be possible because of what the model already was.

- **What happened:**

  **Thin arms: one joint was doing a two-joint job.** This rig has no twist bones. Skin wrung through a single joint
  by an angle keeps only the cosine of half that angle of its thickness. The dash rolled the whole forearm 95
  degrees at the elbow alone: 68 % left. `hand()` now splits every twist across two joints - the forearm roll half
  at the elbow and half at the wrist (91 % left), and the upper arm's spin half at the shoulder and half at the
  elbow, with the forearm turned back so nothing below the elbow moves. It also reports the spin per arm
  (`upper_arm_twist_deg`), which found a 139 degree left arm in the finisher nobody had been able to name.

  **The apron: the model was better than its weights.** A ray fired at him from the front crosses the apron twice
  and THEN the thigh. The skirt is a real two-sided sheet with a leg behind it. It looked painted on because 84 %
  of its skin weight sat on the two thigh bones. No re-weighting onto existing bones can fix that: cloth is pushed
  out by a thigh that swings forward and is not pulled back by one that swings behind, and a fixed weight cannot
  tell those apart. So `Art/Blender/apron_bones.py` gives it two bones, `Apron_L` and `Apron_R`, hinged at the
  waist tie, and `cw_clip.py` swings each one only as far as that leg needs to pass behind it, then lets it fall
  back about half the way per frame.

  Which vertices are "the skirt" comes from the TEXTURE, because nothing in the mesh says so: apron green or towel
  white, below the tie, holes closed by a neighbour vote.

  ![What was selected: skirt and towel in red](../media/2026-11-15-apron-selection.png)

  **It took five passes, and the stretched-edge count called each one:**

  | pass | what it did | stretched edges in a plain walk |
  |---|---|---|
  | before any of this | skirt on the thighs | 23 |
  | 1 | two stiff halves, 9 cm weight ramp at the waist | 562 |
  | 2 | cut the skirt free of the trousers where the generator had stitched them (261 shared vertices) | - |
  | 3 | moved the cloth's leftover leg weight to the hips, everywhere | worse: the waistband is still one surface with the trousers |
  | 4 | one sheet that twists across its width instead of two halves; ramp cut to 5 cm | 202 |
  | 5 | no ramp at all: the free skirt is wholly the apron bones', cut right at the hinge | **2** |

  The ramp was the mistake each time. The body at the waist is weighted to the thighs, so any blend from "apron"
  into "body" there is a blend into a leg.

  ![The dash on the new body, four sides](../media/2026-11-15-apron-dash-four-sides.png)

  **Unreal took two new bones without complaint,** which was the step most likely to fail. The body went in through
  the same re-import tool as before; the skeleton went from 69 bones to 71, the mesh stayed on the same skeleton
  object and the material slot survived. Every older clip has no track for the new bones and leaves the skirt
  hanging straight, which is still better than following the legs.

  **Across the clips,** stretched edges fell everywhere, because most of what had been stretching WAS the skirt:
  dash 163 -> 91, jump 19 -> 6, Freeze Frame cast 63 -> 28, Splice blink 67 -> 19.

  ![In the game: idle, the first strides, the dash from the front and from behind](../media/2026-11-15-apron-in-game.png)

  **The attacks.** "Cheap" had four causes, none of them the poses. Every key eased to a dead stop, so the motion was
  pose-to-pose. Every body part moved on the same frames. Nothing carried past the hit. And each clip snapped back
  to a rigid stand. The rework kept the key poses and the impact frames and changed how he gets between them:

  - a spline THROUGH the keys, flat only where a value turns round or rests, so planted feet still hold exactly;
  - a clock per body part: the pelvis leads by about half a frame, the striking limb is on time, the loose arm
    drags a full frame, and the head is solved from a world gaze so his eyes stay on the target while the rest of
    him runs on different clocks;
  - follow-through: the hips keep turning a few degrees after the fist has started home;
  - a settle that passes slightly through the stand and eases back, which cost three frames of tail on the two
    punches (12 -> 15) and two on the finisher (20 -> 22). The game cuts to the next attack anyway.

  Also fixed on the way: the finisher's toes dipping under the floor, its 139 degree left arm (now 79), the lunge's
  chin-down head and limp wrist, and the kick's foot, which now rolls over with the hip.

  ![The lunge, every frame, four sides](../media/2026-11-15-lunge-every-frame.png)
  ![In the game: lunge recovery, the kick with the skirt swinging, the uppercut airborne](../media/2026-11-15-fluid-attacks-in-game.png)

  A montage keeps the length its clip had when it was made, so the longer clips needed new montages
  (`AM_CafeWalker_*_Authored_B`); `tools/unreal_player_authored_wire.py` now notices the mismatch and makes one
  rather than letting the old montage cut the clip short.

- **Known flaws:**
  - With the skirt cut free, a dark band shows at his waist where it parts from the waistband. It reads as a belt.
  - The idle does not drive the apron bones, so the skirt sits a few degrees differently between the idle and the
    first frame of a clip.
  - The skirt is two rigid boards sharing a twist. It cannot fold over a raised thigh; at a full knee drive it tips
    out to 70 degrees and the leg can show through it for a frame.
  - The helper who re-timed the attacks judged them from contact sheets, and so did I. Whether they FEEL fluid is
    for a person with a keyboard. Its own notes: the lunge holds almost one silhouette for frames 3-5, and the hit
    react's arms hang a little symmetric.
  - Nobody has played it with a keyboard.

- **For the other characters:** `apron_bones.py` takes any body and its texture; the colour test is the only part
  written for green. The coworker wears an apron too and her skirt is stitched to her legs the same way. The twist
  sharing lives in `cw_clip.py`, which so far only knows the player's rig.

- **What we learned:**
  - "The model looks wrong" is at least three different questions. Ask which one before picking a tool.
  - Probe the model before deciding it cannot do something: one ray settled whether the apron was a sheet.
  - When a count gets worse after a fix that should help, the fix is exposing the real seam. Follow it.
