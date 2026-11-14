# 2026-11-13 — The flicker was the light, not the meshes (Justin's Mac mini)

- **What we asked for:** after playing beats 1 to 3 with the city in, a clean-up list. The first item:

  > Flickering in the rendering of some assets, we need that fixed.

- **Prompt(s) we gave the agent:** the line above, as item 1 of five (the others: enemies with no life, thugs that
  move and die as one, the levitating Splice boss, Chaos physics).

- **What happened:**

  **The obvious suspect was innocent.** "Some assets flicker" in a level that had 224 city pieces dropped onto a
  grey-box floor that afternoon sounds like z-fighting, so the first check was geometric: every pair of visible
  static meshes whose bounding boxes share a face within 1 cm. It found 343 pairs and none of them matter - they
  are buildings and kerbs *standing on* the floor, bottom face against top face, and a bottom face is never drawn.
  Nothing along the route has two surfaces facing the same way in the same plane.

  **So we stopped guessing and measured the picture.** `CaptureViewport` twice from the same camera, seven spots
  along the route, then a per-pixel difference in Python. A still scene from a still camera should come back the
  same twice. On the street it did not: **25.7 %** of the pixels differed by more than 24 levels and 7.6 % by more
  than 60. And the difference was not noise - it was *whole surfaces*. In one capture the right-hand wall is warm
  cream and the vending machine's glass is white; in the next, same camera, the wall is grey-blue and the glass
  is blue.

  **That is our own anime shader meeting Lumen.** `M_AnimeLook` decides, per pixel, whether a surface is "lit" or
  "shadow" by comparing the light on it with one number (`ShadowT`, 0.8) - two flat tones with a hard edge, which
  is the whole look. A wall in sunlight is far above that number and a wall in deep shade far below. But a wall
  lit only by Lumen's **bounced** light sits right *on* it, and Lumen's bounce is an estimate that is refined over
  many frames and re-estimated whenever the camera shows it something new. A 5 % wobble in a smooth picture is
  invisible. Put a hard threshold on top and a 5 % wobble flips the entire wall between two colours.

  **The fix is two lines:** `r.DynamicGlobalIlluminationMethod=0` and `r.ReflectionMethod=0` in
  `DefaultEngine.ini`. With no bounced light, a surface is either in the sun or lit by the sky, and both are the
  same every frame. Same test afterwards: the strong (>60) differences on the worst view fell from **7.6 % to
  1.2 %**, and the two captures are the same picture to the eye - what is left is the ink lines' deliberate wobble
  ("boil", 8 times a second) and soft ambient-occlusion grain that never crosses the threshold.

  **It cost the cafe its warmth, so the cafe got lamps.** Without bounce the cafe interior went cold blue: the
  warm brown had been sunlight bouncing off the floor. Two small warm point lights (`Cafe_WarmFill_A/B`, 8 cd,
  no shadows) put it back, and because they are direct light they are as stable as the sun. The street reads a
  little cooler and higher-contrast than before - bluer shade, whiter sun.

- **What we learned:**
  - **A hard threshold turns invisible noise into visible flicker.** Any cel shader that bands on *total* light
    will flicker wherever an unstable light term sits near the band edge. Either band on direct light only, or
    take the unstable term away. For a two-tone look, Lumen GI was buying nothing but the flicker - and it is the
    most expensive thing in the frame.
  - **Diff two captures before theorising.** The picture said "whole walls change tone" in one step; no amount of
    reading the level would have.
  - **A capture test has its own artefacts.** Turning the camera away and back changed half the picture with
    Lumen *off* too - that was auto-exposure settling, which is a smooth drift and not a flicker. We nearly
    blamed the fix for it.
  - **Not checked:** nobody has played it since. The change is measured on captures in the editor on a Mac, not
    seen in motion by a person, and not on the Windows build. If something still flickers, name the asset: thin
    railings and far windows under the ink-line wobble are the next suspect, and that is a different dial (`Boil`).

- **Media:** ![the same camera twice with Lumen on, then with it off](../media/flicker_lumen_band_flip.png)
