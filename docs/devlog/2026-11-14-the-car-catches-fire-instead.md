# 2026-11-14 — The car catches fire, and Freeze Frame is for getting out (Justin's Mac mini)

- **What we asked for:** from the same prompt as the opening cinematic —

  > "I think it might be simpler and more interest to watch if the car catches on fire after
  > gaining the ability, and then the freeze frame to save the co-worker is for getting the player
  > and worker out of range of the following explosion. After all that is resolved the next
  > indicator should be taking the player out to the street towards the goons"

- **What happened**

  Beat 1's hazard was a single piece of shrapnel flying at the coworker, which you stopped by
  freezing time and pressing **F** to teleport her 320 cm sideways. It worked, but the thing the
  player was being asked to understand — *stop time, then act* — was over in one keypress and
  happened to one person standing still.

  It is now a fire and a blast radius, and **this is also the answer to issue #18**, which has
  been asking since Thursday what sets the explosion off: the car catches, and the fire is the fuse.

  **The new beat, in order.** Touch the driver (**F**) → you get Freeze Frame → two seconds later
  the car catches fire, a warning ring the size of the blast appears on the floor, and a **9-second
  fuse** starts → the fuse only burns while time is running, so pressing **E** stops it → **F** on
  the coworker while time is stopped takes her hand, and from then on she walks after you → get
  **both of you** outside the ring before the fuse ends. The car explodes. Anyone still inside the
  ring is caught: she dies, and the player loses 30 health.

  **Why the ring is a thing on the floor and not a number.** 700 cm from the wreck at (−520, 0)
  means safety starts at x = 180 — the east half of the room, with the door at x = 615. The player
  can see exactly where that line is and walk over it, which is the whole point: the beat teaches
  *use the power to buy time*, and the ring is what makes "out of range" legible.

  **It is built as a switch, not a replacement.** `UseFireHazard` is instance-editable and defaults
  to true; turn it off and the old shrapnel path runs exactly as before, teleport and all. A
  playtest that hates the new one costs a checkbox, not a revert.

  **How it was checked, since nobody can press a key for us.** `Object.call_method` reaches a
  BlueprintCallable UFunction, so the test calls the real functions the key polls would have
  called — `DriverTryTouch`, `FreezeFrameStart`, `CoworkerTryRescue`, `CoworkerBlastNow` — rather
  than writing state. That matters more than it sounds: most of these variables are **not**
  instance-editable and a write is refused outright (`HasFreezeFrame` does exactly that), so the
  poke-the-state approach fails loudly on some and silently misleads on others.

  Both endings are measured.

  *Caught in the blast:* fire lights (`fireLit=True`, fuse 9.00 → 3.83 → −0.01), the fuse runs out,
  `blown=True dead=True`, and the player — standing 284 cm from the wreck — goes **100 → 70**
  health. Fire, light and ring all hide. The objective advances to 3 and the beacon jumps to
  (820, 0), out of the door.

  *Dragged clear:* `DriverTryTouch → True`, `CoworkerLightFire → fuse 9.00 armed=True`,
  `FreezeFrameStart → ffActive=True`, `CoworkerTryRescue → True holding=True`. The player walks to
  the safe spot and **she follows**: (−540, −161) → (315, −54), stopping 115 cm behind him, which
  puts her **837 cm** from the blast against a 700 cm radius. The fuse reads 9.00 the whole time,
  because time is stopped. Then the blast: `blown=True`, **`dead=False`**, `rescueDone=True`, player
  health **100**.

  **The failure path kept winning by accident, and that was the harness, not the game.** An MCP
  round trip to this editor is 5–8 seconds and the fuse is 9, so running the steps as separate
  calls burnt the fuse before the rescue every single time — three runs in a row ended with her
  dead and it looked like the beat was unwinnable. The fix was to do the whole run-up inside one
  script call, in one frame. If a measurement keeps producing the same bad answer, check how long
  the measurement takes.

  **Two things the Blueprint graph tool taught us.** A multi-exec-output node (`IsValid`) is
  **terminal** in the DSL — nothing may follow it, which is why both Blueprints now have a tiny
  `CoworkerHideThing(Target, Hide)` / `CineHideActor(Target, Hide)` helper instead of repeating the
  guard. And setting a variable on *another* actor needs the value pin named after the variable:
  `(Class|BPPlayer|SetInputLocked :self ref :InputLocked true)`; positional is refused.

  **The flame is honest about what it is.** It is an unlit cone in a material of our own
  (`M_FireHot`) that `CoworkerFireStep` rescales every tick so it licks, plus an orange point light
  with shadows off — the same rule as the cafe's warm fills, because Lumen is off on purpose here.
  The first version came out of the tonemapper **white**: emissive 3.0 clips through this project's
  posterising look. 1.7 reads orange. Judge an emissive by a frame, never by the number. A real
  Niagara or flipbook fire is the upgrade, and it is not in this entry.

  **The objective marker now walks the player through the whole beat**, which is the last part of
  the request: 1 "check on the driver" (over the body) → 2 "get her clear" (at the safe spot, the
  moment the driver is touched) → 3 "out to the street" (at (820, 0), the moment the car blows) →
  off once the player is past x = 1200. Verified advancing 1 → 2 → 3 in a live run.

  **Nobody has played any of it.** The key bindings themselves are still unpressed — this proves
  the logic and the gates, not **F**, **E**, or how any of it feels.

- **What we learned**
  - `Object.call_method` on a live PIE actor calls our own Blueprint functions. It is far better
    than writing state, because most Blueprint variables are not instance-editable and the write
    is refused.
  - If a test keeps failing the same way, check whether the *test* is slower than the thing it is
    testing. Ours was.
  - An emissive value that looks right in the material editor can clip to white through a
    posterising post-process. Look at a frame.
  - The graph DSL treats `IsValid` as terminal; wrap the guarded work in a small own-function.

- **Media:** ![the coworker follows the player out of the blast, time stopped](../media/2026-11-14-beat1-fire-rescue-frozen.png)
