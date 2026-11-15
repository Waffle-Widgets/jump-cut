# 2026-11-15 — The boss intro ends behind you, facing him (Justin's Mac mini)

- **What we asked for:** "the camera after the boss monologue pans above the player looking down. It should pan to
  behind the player, facing the boss."

- **Prompt(s) we gave the agent:** the message above, relayed with the music ask that follows it.

- **What happened:**

  **Cause.** The intro turned the player toward the boss once, on its first frame, and then trusted the control
  rotation to stay put for 8.7 seconds. It does not: `BP_Player`'s `InputLocked` stops moving and attacking, but the
  template's look input is a separate event and keeps working. So whatever the mouse did during the speech, the
  last second of the shot travelled to - and a player who nudged the mouse down got a camera above his own head
  looking at the floor. The earlier test never saw it because a script has no mouse. (The cause is **inferred**
  from reading both graphs; the fix was proven against simulated mouse input, not a real mouse.)

  **Fix, in `BP_OpeningDirector`:**
  - `CineBossFacePlayer` now runs **every frame** of the intro (spliced into `CineBossStep`, one node), so the
    mouse cannot drag the camera away. It aims at the **boss actor** (falls back to the objective marker), and
    sets the camera pitch to **-10** so the player's own camera sits behind him looking at the boss.
  - **Sibling, same fault:** the explosion pan after the rescue turned the player once at 0.9 s and had the same
    hole. A new `CineExplFaceHold` re-applies that facing every frame after 0.9 s (spliced into `CineExplStep`).
  - Checked and left alone: the Freeze Frame / Splice power moments never change the view target (the player keeps
    his own camera), and the outro fades to black and reloads, so there is no hand-off to fix in either.

  **Measured in PIE** (`tools/c3_pie.py boss`: the real latte clock-out and opening, then the player dropped into
  the plaza facing north, and look input pushed down-and-right on every frame of the speech):
  - control rotation during the speech: stays at pitch -10, yaw toward the boss, **despite** the injected look input
  - last cinematic frame to first player-camera frame: **0.3 cm, 0.00 degrees, 0.01 degrees of FOV**
  - largest per-frame camera step across the 1 s return pan: 60.7 cm and 0.9 degrees (the pan itself, smooth)
  - final camera: **394 cm behind** the player and 78 cm above his centre, pitch **-10.0**, yaw **0.0** = the
    bearing to the boss when the shot ended
  - one thing seen afterwards that is not the hand-off: 0.66 s after control returned the FOV jumped to 104 and
    eased back to 90 - the boss had already blinked to the player and attacked (**inferred** to be the hit's own
    camera kick)

- **Not checked by a person:** nobody has played it. Justin: walk into the plaza, move the mouse around while the
  boss talks, and watch the last second - it should glide to just behind you with the boss straight ahead.

- **What we learned:**
  - "Input locked" in this project means movement and attacks. The camera is still the player's. Any cinematic
    that hands back to the player's camera must hold the control rotation every frame, not once.

- **Media:**
  ![The frame after the hand-off: behind the player, the boss ahead](../media/2026-11-15-boss-handoff-behind-player.png)
