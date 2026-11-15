# A match meter for the latte, and rubble that waits for the crash

*Sun 15 Nov 2026, about 12:55 PM Pacific — GameStation · UE 5.8 · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** two things from playing it.

- **Prompt we gave the agent:**

  > Let's give the user a meter on how close they are to the goal art while they are doing it. Also make sure
  > the debris from the car crash isn't there until after the car crash.

- **What happened:**

  ## The debris: three wrong answers, then the kit

  With the latte shift in front of the opening, the cafe is on screen for minutes before the car arrives, and
  there were bricks on the floor under an unbroken wall.

  1. **"It is the breakable wall panel shedding pieces."** Plausible: it is a live Geometry Collection from
     frame one. The mini game now holds every `B1_Cine` collection Kinematic until clock-out (the director's own
     break switches it back). Measured: panel intact, type Kinematic. **The bricks were still there.**
  2. **"Then it is some small prop."** A search for every small visible thing on that floor found nothing.
  3. **"Then a particle effect."** No Niagara component anywhere near.
  4. Hiding the wall panel showed the hole behind it, with the bricks still lying there. They belonged to
     nothing, because they were not objects: `jumpcut_city_kit.py:605`, *"rubble spilling inward from the
     impact"*. Fourteen bricks **modelled into the cafe room itself**, from Thursday, when the game began after
     the crash.

  The fix is in the kit. The room no longer draws them; it makes the same fourteen random draws (so nothing
  after them in the mesh moves) and hands them to a new model, `SM_CafeImpactRubble`. The room was re-imported
  with `unreal_city_reimport_by_name.py` and an expected-triangle table: 840 to 672, exactly 14 boxes, materials,
  collision and Nanite identical. The rubble is placed at the room's transform, hidden, tagged
  `JC_ImpactRubble`, and `BP_LatteGame.LatteRubbleStep` shows it when the director's `CineWallDone` or
  `CineDone` goes true. Justin's Blueprint is not changed.

  ![Before the crash and after it](../media/2026-11-15-rubble-before-and-after-the-crash.png)

  The wall-panel hold stays: it was a real fault too, just not the one on screen.

  ## The meter

  `M_LatteMatch` draws the cup and the goal into a 16 x 16 target, each pixel blurring a patch of both (16 taps),
  red = foam they share, green = foam in either. Five times a second the Blueprint reads the 256 pixels back and
  adds them up; red over green is the match. One picture holds all three goals (red heart, green rosetta, blue
  tulip) and a parameter picks the channel. A bar under GOAL shows it.

  The same test pours as before now report the game's own number: heart **0.86**, tulip **0.69**, rosetta
  **0.52**. The bar is scaled per pattern so that full means "as good as following the guide exactly".

  ![The meter under the goal](../media/2026-11-15-latte-match-meter.png)

  The first reading was 0.50, 0.46, 0.45 for all three and looked like a broken meter. It was a broken test: the
  script poured a heart while the game had picked a random pattern, so each cup was scored against someone
  else's goal. `LattePick` (which the 1/2/3 keys now use too) lets the test choose.

- **Known flaws:**
  - Not played by a person. The meter has been seen in screenshots, not watched moving.
  - The rosetta's ceiling is low (0.52 unscaled) because the meter compares foam, and a rosetta is half lines.
  - The rubble no longer collides (it used to, as part of the room). Nobody should notice bricks 15 cm tall.
  - `jumpcut_city_place.py` and the mesh audit do not know about the new model yet.

- **What we learned:**
  - When a thing on screen belongs to no actor, it is part of a mesh. Hide the suspect and look: that one
    screenshot ended three rounds of guessing.
  - Art made for "after the event" becomes a spoiler the moment you add a "before".
