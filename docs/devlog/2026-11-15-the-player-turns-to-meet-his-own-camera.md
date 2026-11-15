# 2026-11-15 — The player turns to meet his own camera (Justin's Mac mini)

- **What we asked for:**
  1. "It's fine where he lands but the coworker needs to be on the other side of the car then
     because he's blocking the path right now. That's probably better anyway."
  2. "Seeing two driver models. Once should spawn after the ragdoll motion stops."
  3. "The camera pans around at the end but then snaps to the player camera. The players model
     needs to rotate, with animation, to meet the same destination for the player camera so we
     avoid the snap."

- **Prompt(s) we gave the agent:** the three lines above, verbatim.

- **What happened:**

  **1. The body really was in the way, and a trace proved it rather than a look.** A player-sized
  capsule swept from where the player starts to where `Coworker_Cafe` stood, at (-540, -161), is
  stopped by `C1_Cafe_CrashDriver` at (-241.2, -71.9). She was on the same side of the wreck as
  the body, down the corridor between the car's flank and the bar, so the only way to her ran
  through him. She is now at **(-440, 200)**, the car's other side, picked off a trace grid rather
  than by eye: floor at z = 2.0, a 35 x 90 capsule stands there clear, and the sweep from the
  player's start is clean. She is 215 cm from the blast origin, so she is still well inside the
  700 cm radius and still needs saving.

  **Moving her would have broken the beat on its own, and that took finding.** `BP_Coworker`'s
  `InteractRange` is 280 cm, and at her old spot she stood **260 cm** from the driver's body — so
  the rescue fired the instant the player reached the driver, and it never mattered that objective
  2's beacon pointed at `ObjSafeLoc`, 950 cm in the opposite direction. At her new spot she is
  **295 cm** from the body, outside that range, so the player has to walk to her and the beacon has
  to say so. Objective 2 now points at `ObjCoworkerLoc`, measured live in PIE at **0.0 cm** from
  where she stands. It is a stored vector, not a `GetActorLocation` on `CoworkerRef`: that function
  runs every tick and an "Accessed None" would abort it.

  **And a hidden grey box was walling off her half of the room.** `C1_Cafe_Car` and
  `C1_Cafe_CarCab` are Thursday's grey-box placeholders — hidden in game, but still colliding, and
  sticking out past the real wreck. A sweep from past the body to her new spot was blocked by
  `C1_Cafe_Car`, and every spot deeper than x = -460 on that side was unreachable. Collision is off
  on both now (on the **actor**, then the transform re-set to dirty the package), and the sweep
  reads CLEAR.

  **2. The two driver models were a lost pair of keyframes, not a timing bug.**
  `add_spawnable_from_instance` gives each binding a spawn track whose section has **no keys** —
  which means spawned for the whole sequence. Measured: both spawn sections, 0 keys. So the thrown
  body stood in its head-down landing pose beside the real ragdoll from 6.45 s to 11.0 s, and the
  flying **car** sat inside the real wreck for the same four and a half seconds — a perfect
  whole-body depth tie, and very likely a second cause of the car flicker reported last round.
  `CLAUDE.md` has described these keys since Nov 14; they were lost when the editor side was
  rebuilt after the power cut, because `b1_opening_cine.py` has never written them. It does now:
  car False at frame 187, body False at frame 195, with `CineBodyTime` moved to 6.467 so the real
  driver appears in the pose the flying one ends in and the flying one goes the next frame.

  **3. The snap was three mismatches, and only one of them was the camera move.** Measured in PIE
  with the controller at `CineEndYaw`: the player's own camera sits at
  **(396.107, -55.669, 102.642)**, rotation (0, 0, 172), **FOV 90**, with the 400 cm spring arm not
  shortened by its collision probe. The last cut used to end at (250, 10, 216) pitch -7 — a 194 cm
  jump — **and** it was shot on a 26 mm lens, which on this project's 23.76 mm sensor is **49.1
  degrees** against the follow camera's 90. That is a 2x FOV pop, at least as visible as the move,
  and nobody had noticed it. Cut D now ends on that exact pose and is shot at **11.88 mm**, which is
  exactly 90 degrees on this filmback. Third: a Level Sequence with a camera cut track reverts the
  view the frame it stops, so there is nothing left to blend out of. `B1_Cine_HandCam` is a plain
  CameraActor parked at the same pose; the director stops the sequence, makes that the view target
  with blend 0 (so nothing changes on screen) and then blends from it to the pawn over 0.40 s.

  **The turn uses the movement component, because a SetActorRotation turn is not animation.** The
  anim blueprint is a blend space driven by velocity, so rotating the actor on the spot is the idle
  pose sliding round — and there is no turn-in-place clip to montage: all 38 `_CWM` clips are idle,
  walk, jog, attacks, hit reacts, deaths and jump/fall/land. So from 8.80 s the director feeds
  `AddMovementInput` toward `CineEndYaw` and lets `orient_rotation_to_movement` do the turn at the
  character's own 500 deg/s. **The catch is `PlayerRefreshMoveLock`**, which derives `MoveLocked`
  from `InputLocked` every tick — but only acts on the *transition*, so with `MoveLocked` already
  true it never re-disables movement. Setting the movement mode to `MOVE_Walking` from outside is
  therefore stable, and `InputLocked` stays true so nothing the player presses lands.

  **Measured in a real-time PIE run** (the clock could not be stepped by hand this time — the turn
  needs the movement component to tick): pawn yaw **172.0**, control yaw **172.0**, drift from the
  origin **31.0 cm**, speed 0. The camera ends at (365.44, -51.36, 102.64) rot (0, 0, 172) FOV 90 —
  same height to 2 mm, same rotation, same FOV as the cut's last key, with the blend covering only
  the 31 cm of drift. Exactly **one** body drawn and **one** car drawn, and the sequence player
  reads `playing: false`, stopped by the director rather than by its own schedule.

  The sequence runs to **11.2 s** while `CineLength` stays 11.0, so the director always reaches the
  hand-off first; the last cut holds its final pose over that extra 0.2 s.

- **What we learned:**
  - A spawnable with no spawn keys is spawned for the whole sequence. "Two of something" in a
    cinematic is worth checking at the spawn track before anything else.
  - A camera hand-off is three things, not one: position, rotation **and field of view**. A cine
    camera's focal length and a `CameraComponent`'s FOV are not comparable by eye — convert.
  - Measure the hand-off pose in PIE. Computing it from the spring arm's numbers would have been
    right this time only because the collision probe happened not to fire.
  - Moving a range-gated actor can delete a beat in the other direction too: last round moving the
    body *closer* granted Freeze Frame on frame one; this round moving the coworker *further*
    would have left the rescue unreachable.
  - `ALevelSequenceActor` has no `get_sequence_player()` in Python — it is the `sequence_player`
    editor property.

- **Media:**
  ![Inside the last cut: bars in, the player mid-turn, one body, the coworker on the far side](../media/2026-11-15-beat1-last-cut-turning.png)
  ![The frame after control is handed over — same framing, bars out](../media/2026-11-15-beat1-handoff-no-snap.png)
