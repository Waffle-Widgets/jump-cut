# 2026-11-12 — The crash driver, made locally, with bones Unreal can read (GameStation)

- **What we asked for:** a second CrashDriver model, built on our own RTX 5090 with the local TRELLIS.2 generator
  instead of the paid Meshy service — specifically so the skeleton comes out with Unreal mannequin bone names.

- **Prompt we gave the agent:**

  > build a NEW, locally-generated 3D model of the CrashDriver character (the first boss of the game: the man who
  > crashes a car through the coffee-shop wall and hands over the Freeze Frame power) using the local TRELLIS.2
  > generator, and clean it into a game-ready rigged FBX with a walk cycle.
  >
  > [...] a CrashDriver model already exists, made on the paid Meshy cloud service. Its problem is that Meshy's
  > 'Smart Rig' names every bone `Bone_000`, `Bone_001`, ... so Unreal's automatic IK-rig characterisation fails
  > outright and every animation chain has to be mapped by hand (that cost hours yesterday).

- **What happened:**

  The whole run took about six minutes and cost nothing. `Art/Refs/CrashDriver_apose.png` is RGB with no alpha, so
  it went through `tools/cutout.py` (isnet-general-use) first; the cutout kept the figure whole and — importantly —
  kept the gaps between his arms and his body open, which is what stops image-to-3D fusing an arm to a torso.

  `run_image_to_3d.py ... 1024_cascade` with `DEC=30000 TEX=2048` **generated in 41.8 seconds** (1,569,278 verts
  / 3,159,950 faces before the export remesh); the whole TRELLIS step including loading the 4B model and baking
  the GLB was 2 min 22 s. `trellis_character.py` cleaned and rigged it in **6.5 seconds**. For comparison, the
  Meshy route for the same character was a browser session, 35 credits, and a rig we then had to map by hand.

  **The bone names are the whole point, and they came out right:**

  ```
  root  pelvis  spine_01  spine_02  spine_03  neck_01  head
  clavicle_l/r  upperarm_l/r  lowerarm_l/r  hand_l/r
  thigh_l/r  calf_l/r  foot_l/r  ball_l/r                     — 23 bones
  ```

  That is Epic's naming, which means `apply_auto_generated_retarget_definition` should characterise it and an
  `IKRetargetBatchOperation` can copy the mannequin's attacks, hit reacts and deaths across. The existing
  `SK_CrashDriver` from Meshy is `Bone_000`…`Bone_082` and cannot.

  **We did not trust the green log.** Twice this week a rig has reported fine and been wrong — the human with a
  tail, then the boss whose legs were driven as arms (`MESHYCHAR-BAD-RIG` exists because of that one). So the
  bones were read back out of the saved `.blend` by position:

  - `thigh_l` head z = 91.8 cm → `calf_l` tail z = 9.0 → `ball_l` z = 2.7, on the floor. Same on the right.
    Two chains that start at the hip and end on the ground. Those are legs.
  - `hand_l` tail x = **+45.2 cm**, `hand_r` tail x = **−46.8 cm**, against a mesh half-width of 47.1 cm. The
    hands are the most lateral points on the model, which is what hands are on a standing person. Those are arms.
  - Three spine bones, no tail bone, **0 unweighted vertices**, mesh exactly **180.00 cm** with its lowest vertex
    at z = 0.000.

  `tools/color_audit.py` then re-imported the **exported FBX** and independently counted the same 23 bones, so the
  rig survives the export and is not just correct inside Blender.

  **The one real defect: shoulder deformation at large swing angles.** Rotating `upperarm_l` 50° forward flattens
  the sleeve into a broad plate instead of swinging a cylinder. Reading the weights explains it — `clavicle_r` is
  the top owner of **2,234 of the 14,140 vertices (16% of the whole model)**, while `upperarm_r` owns 348. The
  frost mass sits on his right shoulder, between the clavicle bone and the body, and the automatic weighting
  swallowed a chunk of torso and upper arm into the clavicle along with it. At walk amplitude this does not show
  — the side and front walk sheets are clean, no leg crossing, no knee pop — but a thrown punch will show it.

  **The colour audit flagged, and the flag is leather, not a colour mistake.** 2.84% of the front and 0.91% of the
  back sit within dE76 < 14 of the face tone (`#8E6D58`). The painted sheet shows exactly where: specular
  highlights on the brown leather jacket and the toes of the brown boots. The face and both gloves are green
  (skin where skin belongs). The zones read helmet `#D4E4E1` pale silver, skin `#8E6D58`, jeans `#303B3E`
  blue-grey, frost on the back `#8AA2A1` cyan. Nothing has skin-coloured hair or hair-coloured skin; brown leather
  and a tanned face are simply close together in Lab and the audit has no idea one is a jacket.

  Nothing was written under `Content/`. `CHAR_OUT` was set to `Art/Blender/export/Characters/CrashDriverTrellis`
  before the Blender run, because the script's default output path is inside `Content/Game/Imported/` and the
  Unreal editor was open on this machine with another agent working in it — an auto-import there pops a modal
  that freezes the MCP.

  **Is it worse than the Meshy one? No — it is different, and the honest answer needed a render, not an
  opinion.** Both FBX files were loaded fresh, normalised to 1.8 m and lit identically (second picture below).
  They are the same size: 30,000 tris (Meshy) against 29,459 (TRELLIS).

  - **Meshy is cleaner.** Smoother panels, crisper lapel and zip edges, and noticeably **better hands** — its
    fingers are modelled apart, ours are chunky and half-mittened. Its ice shard is a crisp white crystal; ours
    is a fluffy ruff that reads more like fur than frost. Its wider A-pose is also the easier thing to rig.
  - **TRELLIS is more faithful.** More leather grain, wear and creasing, real folds in the jeans, better boots,
    and a weathered, stubbled face — the reference is a grizzled older man, and Meshy smoothed him into someone
    younger and more generic. Ours looks like the drawing.

  For the cel-shaded look the team picked, Meshy's smoother read may well suit better, and `CLAUDE.md` already
  says Tripo beats TRELLIS for stylised people. But "visibly worse" is not what happened here, and only one of
  the two arrives with a skeleton Unreal can characterise by itself.

- **What we learned:**

  - **A local model can be the better model, not just the cheaper one.** Side by side with the reference, this is
    a faithful likeness: helmet, goggles, scarf, lapels, zip, belt, gloves, boots, and a real face under the brim.
    `CLAUDE.md` says Tripo beats TRELLIS for stylised people, and that may still hold for the cel-shaded cast —
    but for this leather-and-grime character TRELLIS.2 did not come out visibly worse than the Meshy model, and it
    came with a skeleton Unreal can read.
  - **The narrow A-pose cost us the shoulders.** Meshy's model holds its arms further from the body; ours came
    from a reference where they nearly touch, and that is the same crowding that the weighting then got wrong.
    Next reference sheet for a TRELLIS character: ask for a wider A-pose.
  - **41.8 seconds on the 5090.** The skill warns TRELLIS peaks near 17 GB VRAM; measured peak was **14,144 MiB of
    32,607 total card**, against a 9,439 MiB baseline from the open Unreal editor and browsers — so TRELLIS itself
    took about 4.7 GB at `DEC=30000 TEX=2048`. It shares the card with a running editor comfortably.
  - **Automatic weights lose to a bulky shoulder.** The check that caught it was not a status line; it was asking
    which bone owns how many vertices. A bone that top-owns 16% of the mesh is a bone that has eaten something.
  - **The colour audit cannot tell leather from skin,** and it should not be read as a pass/fail on its own. It
    tells you where to look; the painted sheet is the answer.

- **Still untested:** none of this has been inside Unreal. The claim that `apply_auto_generated_retarget_definition`
  will characterise these bones is reasoned from the names, not demonstrated — nobody has run the retarget on this
  skeleton yet. That is the next thing to do, and it is the thing that justifies the whole exercise. The shoulder
  weighting should be looked at before this model takes a punch animation.

- **Media:** ![Reference sheet, the TRELLIS.2 model in four views, the walk cycle, and the colour audit](../media/2026-11-12-crashdriver-trellis.jpg)

  ![The Meshy crash driver and the TRELLIS.2 one, same size and same light: Meshy smoother with better hands, TRELLIS more weathered and closer to the drawing](../media/2026-11-12-crashdriver-meshy-vs-trellis.png)
