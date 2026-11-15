# 2026-11-15 — The car stops flickering, and the body lands where you can reach it (Justin's Mac mini)

- **What we asked for:** two things from a playtest of beat 1's opening.

- **Prompt we gave the agent:** *"Almost there, The ragdoll went to a place that was hard to get
  to, Can we have it follow a curve to land somewhere intentional and easy to access. Another
  note, the car is flickering badly"*

- **What happened:**

  **The hard-to-reach ragdoll was not bad physics — the spot itself was the counter top.**
  The driver's landing spot was `(-395, -215)`, which sits inside `City_Cafe_00_CafeCounter`'s
  footprint (x -584..-76, y -285..-196). A downward line trace there lands at **z = 150**: the
  bar. A player capsule neither fits at that point nor can sweep to it. The body was being thrown
  onto the service side of the counter every time. The 1.8 s of free ragdoll physics then finished
  the job, because the hand-off velocity was `(210, -260, -40)` — 260 cm/s aimed straight at the
  bar.

  **Bounds could not find a better spot; traces could.** The first search used actor bounding
  boxes and returned *zero* candidates anywhere in the cafe, because `City_CafeShell`'s box covers
  the entire room, `B1_Cine_ExplCam`'s covers 20 m, and the trigger spheres cover 5 m each. Rebuilt
  on real collision traces — floor height, a standing player capsule, twelve clearance spokes and a
  capsule sweep from the middle of the room — it found 138 clear spots. `tools/b1w_spot.py`.

  **The flight is a computed curve now instead of six typed-in waypoints.** The old arc had its
  middle hand-placed to end at the old spot, so moving the landing point left the body teleporting
  240 cm between the last two keys. `b1_opening_cine.py` derives the whole flight from wherever
  `BP_CrashDriver` actually stands: a ballistic parabola from the windscreen to his feet, bowed
  90 cm out to the car's right so he still leaves the cab on the side we asked for, with one full
  tumble. Move `ObjDriverLoc` and the arc follows it.

  **Moving him closer silently deleted the beat, and only a measurement caught it.** The first
  landing spot, `(-200, -60)`, is 209 cm from where the player starts — inside `TouchRange`'s 220.
  So Freeze Frame was granted on the first frame after the cinematic: measured in PIE, the
  objective jumped straight to 3 with the player still standing at `(0, 0, 94)`, never having
  moved. The spot went out to `(-300, -60)` and `TouchRange` came down to 120, which leaves about
  200 cm of real walking.

  **Measured, in a live PIE run with real ticks:** the body comes to rest with its lowest bone at
  z 4.57 on a floor at z 2.00 (nothing through the floor), bones spanning x -282..-173 and
  y -162..-52 — 52 cm clear of the wreck and 34 cm clear of the counter — with the objective still
  at 1, `DriverTouched` false and `HasFreezeFrame` false.

  **The flickering car was the geometry collection, and it had only been on screen since the car
  learned to explode.** In the running game only `B1_Cafe_CrashCar_GC` drew the wreck;
  `City_CafeCrashCar`, the plain static mesh, was hidden. Two things about that collection matter:
  its bounds are **0.05–0.1 cm larger** than the identical static mesh at the identical transform,
  which is fracture pieces inflated slightly outward — so along every cut line across the whole
  body two pieces overlap by about a millimetre — and the static mesh is the one that got #67's
  flush-face fix (`0f9b13c`) and is drawn exactly like every other city prop, none of which anyone
  reports flickering.

  So the wreck is drawn by the static mesh for the whole beat, and the collection is shown only on
  the frame the blast breaks it. Both actors already stood at `(-520, 0, 0)` with bounds agreeing
  to 0.1 cm, so the swap is invisible. Verified by calling the real `CineExplFire` on the live
  director: before, static visible / collection hidden and Kinematic; after, static hidden /
  collection visible and **Dynamic**, at the same bounds.

  **Two dead ends worth naming.** `GC_CrashCar` carries a **root proxy** pointing at
  `SM_CrashCar` with empty override materials, which looks exactly like "the car draws grey
  placeholder materials" — it does not. `GeometryCollectionComponent.cpp:6540` only reads the root
  proxy through the **custom renderer** path, and every collection in this level has
  `custom_renderer_type = None`. And the car's own mesh still carries 11.28 cm² of exactly
  coplanar glass-on-trim in the kit (down from 236 cm² before `stand_proud`), measured by
  `Art/Blender/car_tie_scan.py` — real, but far too small to be what "flickering badly" means.

- **What we learned:**
  - A Geometry Collection standing intact is **not** the same surface as the static mesh it was
    cut from. Draw the static mesh until the thing actually breaks.
  - In this map, a bounding-box test for "clear floor" is worthless — the room shell, the cameras
    and the trigger spheres all have room-sized boxes. Trace.
  - Moving a range-gated actor closer to the player can delete a whole beat with nothing erroring.
    Read the objective state after moving one.
  - A ragdoll's settled **mass** ends about 55 cm from the actor's origin, because the body
    collapses out of a head-down pose. Leave that much room when choosing where it lands.

- **Media:** none worth keeping — the editor's third-person capture puts the player's apron across
  the middle of every frame. Everything above is measured state, and the car in motion still needs
  a person to watch it.
