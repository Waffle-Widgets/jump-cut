# The sun was twice too strong

**Sun Nov 15, about 3:05 PM, GameStation (builder). After the noon cut-off; the Team Owner asked.**

## What we asked for

> is there anything we can do to fix the lighting? Everything in the light looks washed out

then, after playing the "strong" option in the editor:

> yes this looks better. Keep it.

## What happened

`Sun_Main` was at 10 against a sky light of 1, and `PP_AnimeLook` overrode nothing about exposure, so exposure
was automatic. Anything in direct sun reached the cel look already near white: pavement, kerbs and shop shutters
were one flat tone.

Tried in the running game from one fixed camera, without saving anything: `r.ExposureOffset` for exposure and
`set_intensity` on the live sun. Two of the first four captures never landed (two console commands a second
apart), so the comparison that went to the owner was three pictures: now, mild (sun 6, exposure -0.5) and strong
(sun 5, exposure -0.9). He played strong in the editor and kept it.

`tools/jc_light_fix.py 5 -0.9 save` writes it as level data: the sun's intensity, and an exposure bias of 0.1 with
the override on (the engine default bias is 1.0, so 0.1 is "0.9 lower"). It resets `r.ExposureOffset` to 0 first.
That console variable was still at -0.9 from the test, and left alone it would have doubled the change in the
editor and not existed at all in the packaged game.

![Now, mild, strong](../media/2026-11-15-lighting-options.png)

## Checked, and not checked

- Checked: both values read back; both actor files saved; the look volume still has its one blendable.
- The owner played it in the editor and said keep it.
- **Not checked by me:** the cafe interior, the opening explosion, the plaza and boss area with the new values, and
  a packaged build. No build has this yet.

## What we learned

- **A console variable set during a test outlives the Play session.** Reset it in the script that makes the change
  permanent, or the editor shows a look the build does not have.
- **Show the options from one fixed camera and let the person who complained pick.** It took three pictures.
