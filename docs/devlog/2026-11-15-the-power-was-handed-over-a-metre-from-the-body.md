# The power was handed over a metre away from the body

**Sun Nov 15, about 3:15 PM, GameStation (builder). A bug fix; the Team Owner asked for the check.**

## What we asked for

> I would like to make sure the power is transferred to the main character when he comes into contact with the
> dead driver.

## What happened

Ran the real thing in Play mode: clock out, let the 11 s cutscene play, then stand the player by the driver and
read `HasFreezeFrame` with nobody calling `DriverTryTouch` (the director asks every tick).

- First try, at (-300, 180): no power after ten seconds. That was my mistake. The position came from an old test
  script; the driver has been moved since.
- Probed the live driver. Its ACTOR is at (-300, -60) with `TouchRange` 120. Its BODY, the ragdoll the player can
  see, lies from x -268 to x -117, centred about (-184, -37). The body comes to rest **118 cm from its own actor
  origin**, and the test was a plain distance to that origin.
- So: standing against the near end of the body, 150 cm from the origin, gave no power. Walking on past the body
  to 107 cm gave it. The hand-off worked, but only if you overshot the thing you were told to touch.

`BP_CrashDriver.DriverCanTouch` now measures from the body itself (`Bone_000` on `DriverMesh`, its hip) with a
reach of 130 cm. Checked both ways in a fresh Play session:

| Player | Distance to the hip | Power |
|---|---|---|
| Where the cutscene leaves him, (-26, 4) | about 160 cm | not granted (correct) |
| Against the near end of the body, (-85, -40) | about 95 cm | granted within one tick |

The first row matters as much as the second. On Nov 15 morning a wider range gave him the power on the first
frame after the cutscene, without moving. 130 leaves about 30 cm of margin; 150 left 9.

## Checked, and not checked

- Checked by script in the running game: both rows above, and the graph read back as written.
- **Not checked:** a person walking up to the body with the keyboard, and where the body lands on a different run
  (a ragdoll does not settle in exactly the same place twice; the measure now follows it, which is the point).
- `TouchRange` on the Blueprint is no longer read by this function.

## What we learned

- **Gate on what the player can see.** The CLAUDE.md note already said a settled ragdoll's mass is about 55 cm from
  its actor origin. Here it was 118.
- **Probe the live actor before trusting a test position from an older script.**
