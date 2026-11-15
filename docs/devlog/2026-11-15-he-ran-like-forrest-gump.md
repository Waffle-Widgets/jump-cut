# He ran like Forrest Gump: twelve clips of our own, then the owner played them

*Sun 15 Nov 2026, about 1:15 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`), five Fable 5.2 helpers authoring in parallel*

- **What we asked for:** every limb looking normal from every side, all of the player's animations finished, and
  the same body fixes on the other characters. Then, after playing the result, a second pass.

- **Prompts we gave the agent:**

  > make sure his hands also look normal when moving. make sure all of his limbs look normal when running as well.
  > Make sure they look normal from each side too. Then we need to finish all of the animations for the character.
  > And we need to make sure the other characters get the fixes.

  and, after the first round was in the game:

  > He does not look very cool when he runs, research and fix that, he should not be running like Forest Gump. The
  > speed of the attacks felt fine but it looks pretty lame, this is an anime, take inspiration from popular ones.
  > His shoulders are too low. I've attached an image of how he looked in the 3d modeler for reference.

- **What happened:**

  **First, a way to look.** Every check of a retargeted clip so far had read numbers back or taken one capture
  from the game camera. `tools/unreal_export_clips_fbx.py` writes the clips the game plays out of Unreal with the
  body skinned to them, and `Art/Blender/clip_sheet.py` renders front, his left, back and his right across the
  clip. The retargeted jog, seen that way for the first time: head tucked down, flat paddle hands on bent wrists,
  elbows out, legs crossing the centre line. Not tunable. Replace it.

  **Then a way to author.** `Art/Blender/cw_clip.py` is the shared half of every clip: a script poses one frame
  with `body / spine / neck / foot / hand` in his own left-forward-up terms, and `author()` solves, keys, keeps the
  root on the floor the way the game's other clips do, measures (soles, over-reach, torn skin, planted ankles),
  renders the four-side sheet and exports. With that in place three helpers wrote eleven clips in parallel in about
  seven minutes each: run, walk, punch A, punch B, finisher, hit react, jump, fall, land, a Freeze Frame cast and a
  Splice blink. `tools/unreal_import_player_clips.py` brought them in on the game's own skeleton and
  `tools/unreal_player_authored_wire.py` pointed the blend space, and `BP_Player`'s four montage defaults, at
  them; the anim blueprint's Jump / Fall / Land states were re-pointed through the MCP. The attacks went from
  1.0-1.7 s to 0.37-0.63 s with the hit on frame 3-4.

  **Then the owner played it, and the first round was correct and boring.** The run was a textbook run: upright,
  elbows at ninety degrees, pumping. The attacks were a jab, a cross and an uppercut with both feet planted. We had
  asked the helpers for "normal" and got it. Round two asked for a silhouette instead:

  - **Run:** a dash. Torso thrown 37 degrees forward, head up, pelvis dropped 10-15 cm, arms streaming back,
    heel kicked high. The planted foot still travels at exactly 20 cm a frame, so it does not skate at 600 cm/s.
  - **Punch A:** a lunging straight: front foot stamps out 38 cm, rear leg straight behind, far fist chambered.
  - **Punch B:** became a roundhouse kick at head height, body tipped away from it.
  - **Finisher:** a leaping uppercut, both feet off the floor at the apex.
  - Lengths and impact frames unchanged, because "the speed of the attacks felt fine".

  ![The dash from four sides](../media/2026-11-15-anime-sprint-four-sides.png)
  ![The roundhouse from four sides](../media/2026-11-15-roundhouse-four-sides.png)

  **The shoulders, third time.** 14 degrees of collarbone lift (the previous entry) still read as droopy in the
  game. Rendered close up beside the modelled A-pose at 14, 26 and 38: 28 squares them, 38 is a shrug.

  ![Collarbone lift: A-pose, 14, 26, 38, and two with the arms wider](../media/2026-11-15-shoulder-lift-study.png)

  **And 28 everywhere was wrong within the hour.** The dash came back with shoulders like puffed sleeves from the
  front: the lift is right for an arm that hangs and wrong for one that is level or swept back. `hand()` now
  scales it by how far down the arm points (full when it hangs, none when it is level).

  **The other characters.** A fifth helper audited the goon, the boss, the coworker and the crash driver for the
  fault the player's apron had (skin weighted to the root bone, which the clips keep on the floor). Goon: 994
  vertices, fixed. Boss: 3,368, fixed. Coworker: 429 (one fully on the root, an 82 cm drag), fixed, weights
  smoothed and her shoes, tipped 21 degrees toes-up, flattened. The driver needs nothing for the clips he has.
  `tools/unreal_reimport_body.py` put the three bodies into the assets the game uses, skeleton and material slots
  read back unchanged.

  ![In the game: idle shoulders, and the dash from the side](../media/2026-11-15-anime-sprint-in-game.png)
  ![In the game: the combo caught mid-recovery, mid-kick and airborne](../media/2026-11-15-anime-attacks-in-game.png)

- **What went wrong on the way:**
  - `git pull --rebase --autostash` with Unreal open put everything back except `BP_Player.uasset`, said only
    "Your changes are safe in the stash", and left the old Blueprint on disk. Restored from the stash by hand.
  - The first body re-import "failed" because Play mode was running: `load_asset` returns `None` during Play, and
    the tool reported "not a SkeletalMesh".
  - Smoothing skin weights lowers the torn-edge count on layered clothes (the boss's jacket, the driver's
    leathers) and adds poke-through the count cannot see. Rejected on both after looking at the renders.

- **Not done, and known flaws:**
  - Nobody has played round two with a keyboard yet. Feel is the owner's call.
  - Torn-skin counts on the big poses are over the limit we set (run 147 edges, punch A 195, kick 314, finisher
    267 against the idle's 5): mostly the apron skirt following a raised thigh. No stretch is longer than 7.6 cm.
  - From directly behind, which is the game camera, the dash is less dramatic than from the side.
  - The kick's foot is flat rather than turned over; the finisher dips 0.8 cm through the floor on one frame.
  - The walk is authored for 180 cm/s and will slide a little at 300 (gamepad only; a keyboard is always at 600).
  - The Freeze Frame cast and Splice blink montages exist but nothing in `BP_Player` plays them yet.
  - The coworker's hands are fused to her apron in the mesh itself; no weight change cures that.

- **What we learned:**
  - "Normal" is a brief for a mannequin. Ask for the silhouette you want frozen as a manga panel.
  - Authoring is cheap once a clip is one short script with its own check sheet: the second round of four clips
    cost less than the first.
  - A posing default that is right for one pose is a bug in the next. Make it follow the pose.
