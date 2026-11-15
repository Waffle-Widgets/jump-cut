# 2026-11-15 — The pan ends on the player's own camera, and getting the power is a moment (Justin's Mac mini)

- **What we asked for:** a review of the intro and tutorial up to the goon fight ("this scene needs to hook
  the player"), plus five notes from Justin.

- **Prompt(s) we gave the agent:** "Review the intro cinematic and tutorial play all the way to when the player
  needs to go fight the goons. This scene needs to hook the player to the game. Identify areas of improvement
  then implement them. Notes from me: 1. the quest markers should glow to be seen better. 2. The Text boxes
  should have a pulse effect to draw the eye to them. 3. The story beat when acquiring our ability could be
  better. 4. At the end after saving the co-worker the camera pans to the goons, but once the player has control
  of the model isn't lined up with that camera move and the camera snaps to a position pointing the other way.
  We need the player camera and model to meet the end of that cinematic camera panning. 5. Implement any
  improvement from your analysis of the scene."

- **What happened:**

  **It is Sunday, which is bug-fix day.** Note 4 is a bug. Notes 1 to 3 are polish that was asked for by
  name, so each was kept to the smallest version that does the job: no new system, no new dependency, one new
  material. `BP_Player` was LFS-locked by another computer, so nothing here edits it — the two things that
  want the player's camera reach it from the director with `GetComponentByClass(CameraComponent)`.

  **Note 4, the snap.** Last round fixed the hand-off after the *opening*; this is the one after the
  *explosion*. The pan finished on a fixed pose (`ExplCamD`: 180, 60, 210, yaw -5, a 75 degree lens) and then
  blended 0.6 s to wherever the player's camera happened to be. After walking west to the coworker it was
  pointing west, so the view swung through 180 degrees as control came back. Now, 0.9 s into the cinematic,
  while the camera is on the wreck and he is out of frame, `CineExplFacePlayer` turns the model **and** the
  controller toward the street; and the last leg of the pan lerps to the follow camera's **live** world pose
  with the lens opening 75 → 90. A script played the beat with the player deliberately facing west (yaw 128)
  and sampled every frame: between the last cinematic frame and the first frame of play the camera moves
  **0.01 cm, 0.00 degrees, 0.00 degrees of FOV**; model yaw 4.09, controller yaw 4.09.

  **Note 3, getting Freeze Frame.** It used to be: walk within 120 cm of the body, a star burst, a line of
  text. Now the world actually stops. For 2.2 real seconds: global time dilation 0.06, a white-cyan shutter
  flash (0.9 → 0 over 0.45 s), the letterbox closes, the player's own lens pushes in 90 → 64 and back, the
  unused `SFX_PowerFreezeFrame` finally plays, and the caption is two words: FREEZE FRAME. The power-pop stars
  hang in the air because time is stopped, which is the power explaining itself.

  **Note 2, the caption box** pops in at 1.28x and settles in 0.3 s, then breathes 3.5% with a faint teal
  tint. **Note 1, the marker** is an unlit pulsing `M_ObjectiveGlow` instead of lit `M_PropBlue`, and its
  scale breathes ±14%.

  **Found on the way (note 5):**
  - **The caption box collapsed into a column four words wide** after the first caption
    (`AutoWrapText` + an auto-sized slot: the wrap width is last frame's box width, so a short caption makes
    every later one narrow). It also made the box tall enough to cover the HUD's own PRESS E. `AutoWrapText`
    is off; `WrapTextAt 1180` does the wrapping.
  - "That was meant for you. There are more of them out on the street - go and put them down." →
    "That was meant for you. They are waiting outside."
  - A "Press E to freeze time." caption was written and then **removed**: the HUD already says PRESS E.
  - The pan's legs ease in and out instead of moving at constant speed.

  **The editor hung three times, and it was not us.** Twice at PIE start and once mid-pan, with the game
  thread waiting on the render thread waiting on `MTLCompilerService`. `~/Library/Logs/DiagnosticReports` has
  17 crashes of Apple's Metal shader compiler since Saturday 10 PM, all `llvm::report_bad_alloc_error`, and
  the viewport says "Ray Tracing PSO is not ready yet". Launching the editor with **`-noraytracing`** ended it:
  a full run with no stall. That is very likely the 12:38 AM crash too. It is a launch flag on this Mac only;
  the project's ray tracing setting is untouched.

  **Not done:** the rescue still does not *require* pressing E (`RescueRequiresFreeze` is false, a 9 s fuse for
  a 3 m walk), so the tutorial shows the power and names the key but does not make you use it. That is a
  design decision, not a fix. Nobody has played this with a keyboard; feel is not ours to call.

- **What we learned:**
  - End a cinematic on the **live** pose of the camera you are handing to, not on a measured constant. The
    constant is right until the player stands somewhere else.
  - Turn the model while the camera is looking at something else.
  - Under time dilation, anything that should run at wall-clock speed has to divide `DeltaSeconds` by the
    dilation — including the letterbox, which would otherwise take 50 s to close.
  - `AutoWrapText` in an auto-sized canvas slot is a ratchet: it only ever gets narrower.
  - An unresponsive editor on a Mac: `sample <pid>` and look for `MTLCompilerConnectionQueue`. A dead editor's
    `CrashReportClient` keeps port 8000, so the next editor starts with no MCP until it is killed.

- **Media:**
  ![The frame the power lands: flash, bars closing, lens pushing in](../media/2026-11-15-beat1-freeze-frame-flash.png)
  ![Time held: the stars hang, FREEZE FRAME](../media/2026-11-15-beat1-freeze-frame-hold.png)
  ![The glowing marker over the coworker, and a caption on one line under the HUD's PRESS E](../media/2026-11-15-beat1-marker-and-caption.png)
  ![The last frame of the pan](../media/2026-11-15-beat1-pan-last-frame.png)
  ![The first frame of play: the same picture](../media/2026-11-15-beat1-first-frame-of-play.png)
