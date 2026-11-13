# 2026-11-13 — Beat 4: the ceiling that takes the jump away, and four invisible bugs (Justin's Mac mini)

- **What we asked for:** "Continue beat 4 on this mac" — and, mid-turn, "Also, make sure we are merging as we go."

- **Prompt(s) we gave the agent:** *"Continue beat 4 on this mac"* / *"Also, make sure we are merging as we go"*.
  Earlier in the same chat the Team Owner set the work order — *"We should work on things in order of how we are
  playing through the game"* — and the beat-5 call beat 4 serves: *"We can let Splice allow the user to get past the
  attack Stunt Double and attack the boss directly."*

- **What happened:**

  Beat 4's destroyed-building platforming is built, placed and saved. 23 actors: three gaps (250 cm open sky, then
  400 and 400 roofed at `z = 215`), a 10 × 15 m landing pad for beat 5, a checkpoint and two goons. The whole thing
  is one script, `tools/beat4_platforming.py`, and it is idempotent — re-running it removed 23 and placed 23.

  **The design, and why `docs/CITY.md` was wrong.** CITY.md asked for "a gap the player must blink is 6.5–8.5 m".
  That cannot work, and the proof is in the assets rather than in anyone's opinion. `BP_Player` serializes none of
  its movement numbers; its parent `BP_ThirdPersonCharacter` serializes only `JumpZVelocity` — exactly one `500.0`
  float, with no 420, 600 or 700 anywhere in the file — beside `AirControl 0.35` and `BrakingDecelerationFalling
  1500`, the UE5 template's trio. `MaxWalkSpeed` and `GravityScale` appear in neither asset, so they are the engine
  defaults 600 and 1, and no capsule override exists, so `ACharacter`'s 34 × 88 stands and the player is 176 cm. A
  flat run-and-jump therefore carries 612 cm, about 680 with a lip at each end — **further than the 600 cm blink**.
  So there is no gap width that defeats the jump and still allows the blink. The jump has to be removed another
  way, and a **ceiling** does it: a collapsed slab 215 cm up leaves 39 cm of head room, a jump spends that head
  room and stops, and the arc collapses to about 288 cm across a 400 cm gap.

  **Then four bugs, and the thing they had in common is that every one of them was invisible.**

  1. **A 20 cm slit in the ceiling.** The two ceiling slabs sat at `y = ±170` and are 320 cm deep, leaving a slot
     running straight along `y = 0`. The player's capsule could never fit through it, so the *section* was fine. The
     *measurement* was not: the script's own ceiling check traces upward at `y = 0` exactly, and would have reported
     **"open sky" over both roofed gaps**. Whoever ran it would have gone hunting for a ceiling that was already
     there. Moved to `±150` so they overlap.
  2. **The old end wall still blocked the route.** `C1_Run_End` — the wall that closed the three-beat demo — was
     hidden, but after a reload its collision was back: the component-level `set_collision_enabled` does not
     serialise. A forward trace from x 10300 stopped dead at 10615. **Beat 4 was unreachable in play**, behind an
     invisible wall, and the only reason we know is that the trace was run from *before* the wall rather than from
     inside the new section. `bActorEnableCollision` is an actor property and does stick.
  3. **Every platform was 74 cm too low.** `SM_RuinSlab_A` is a *broken* slab. Its bounding box reaches 119 cm, so
     placing it at `z = -119` ought to land its top on zero — except the box only reaches 119 because of chunks
     standing up near the edges, and the surface you actually walk on, down the centre line, is 45 above the origin.
     The walkway was therefore at `z = -74`, which turned the head room under the 215 ceiling from 39 cm into
     **113 cm**. At 113 cm a jump carries about 559 cm and **clears both "must-blink" gaps** — the entire section
     defeated. And it looked perfect: the slabs rendered exactly where they were supposed to be.
  4. **The collision did not match the art.** Interchange gives each imported mesh a single auto convex hull, and
     for these broken shapes the hull and the visible surface disagreed. All five are now
     `CTF_USE_COMPLEX_AS_SIMPLE`, which is the right setting for static level geometry.

  **And a fifth, which cost the most time.** The previous session had died with the section dirty. On relaunch
  Unreal quietly restored 23 actor packages to disk. They were not in the loaded level, so they looked like
  harmless orphans — but World Partition loads every actor package in the folder, and reloading the map produced
  **46** beat-4 actors: the whole section doubled, every slab inside another slab. They are moved out of `Content`.

  **Everything above was verified after reloading the level from disk**, not from the script's own report: walkway
  flush at `z = 0` on all three platforms, gaps at 400 cm, ceiling unbroken from `y` −240 to +240, route clear at
  chest height from x 10300 onward.

- **What we learned:**
  - **A bounding box is not a walking surface.** For anything broken, cracked or jagged, trace down and find out
    where the player's feet land. This one would have shipped as "the platforming section where you don't need the
    power".
  - **A measurement that traces one line can be beaten by a 20 cm hole in your own geometry.** The section would
    have worked and the report would have said it didn't.
  - **Hidden is not the same as non-colliding, and component collision does not serialise.** The wall that blocked
    the whole beat was invisible in every sense.
  - **A character's tuning numbers are readable straight from the `.uasset`.** Absence from a name table *is* the
    answer — it means the engine default. That works with the editor shut, and it is not an opinion.
  - **An orphan actor package is not orphaned.** World Partition will pick it up on the next load.

- **Media:** ![The beat 4 run, seen from the side](../media/2026-11-13-beat4_side.png)
