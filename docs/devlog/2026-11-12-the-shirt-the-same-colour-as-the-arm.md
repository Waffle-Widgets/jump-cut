# The shirt the same colour as the arm

**Thu Nov 12, evening — M Station**

Manny reversed a call he made earlier the same day: the ComfyUI models, the ones drawn on the local 3090 before
we had a browser, turned out to be the best of everything we generated. So those are the cast we build on —
`SK_CafeWalker`, `SK_CrashDriver`, `SK_CleaverBoss`, `SM_Cleaver`. The two Gemini-sourced bosses stay in the repo
as alternates rather than being deleted. The cel-shaded anime look is unchanged; it was never the models that
were in question, only which picture each one came from.

He also asked for the thing nobody had checked: **are the colours actually in the right places?** No
skin-coloured hair, no skin-coloured clothes, and nothing the other way round.

## Why no existing tool could answer that

Image to 3D bakes **one texture for the whole body**, and nothing downstream knows that a given pixel is "hair" or
"sleeve" or "boot". So a model can come back with a flesh-toned fringe or a shirt the same colour as the arm
inside it, and every number in the pipeline still reads green — triangle count fine, bake fit fine, rig fine.

`meshy_character.py` does render a contact sheet, but it is **lit** and 300 px square. A lit render mixes the light
rig into every pixel, so you end up judging the lighting instead of the texture. It is the wrong instrument.

So: `tools/color_audit.py` and `Art/Blender/color_audit_render.py`.

1. Render the baked base colour **unlit** — Emission shader, Cycles at 1 sample, `Standard` view transform (not
   Filmic or AgX, which would shift every colour before you saw it). A rendered pixel then *is* the texture colour.
2. Take the skin tone from the middle of the face.
3. Paint every pixel within dE76 14 of it — **green** on the head and around the hands where skin belongs,
   **red everywhere else**. Red is the defect, and you can see where it is rather than read a number.
4. Sample named zones for hair, face, chest, waist, thigh, shin, hands and feet.

Locating the zones is the part worth stealing. Meshy's Smart Rig names every bone `Bone_017`, so there is nothing
to match on. But in an A-pose the geometry gives it away for free: **the hands are the most lateral bone tips, the
feet the lowest, the scalp the highest.** No name matching, works on a 31-bone rig and an 83-bone rig alike.

## The answer, and it is mostly good news

**Nothing has skin-coloured hair. Nothing has skin where skin should not be.** Every hair sample sits far from its
own character's skin — `CafeWalker` dE 87.7, `CleaverBoss` dE 27.8 — and the crash driver scores a literal 0.00%
on both views, because the only skin on him is his face. The cleaver is a pale steel blade and a warm wood handle
with no flesh tone anywhere.

We also checked the thing the palette rule actually depends on. All three mob bosses' shirts measure hue
**329°–333°** — magenta, inside the 290°–335° band — so Splice's colour is safe. That one nearly went down as a
false alarm: the first pass sampled `CleaverBoss`'s collar *in shadow* and read 345°, crimson. **Measure a garment
from its saturated pixels, not from whatever fold the sampler landed in.**

## The one that failed, and the trap inside the fix

`CafeWalker`'s cream shirt `#F7F2E0` is **dE 14.4** from his face skin `#FDD9BF`. Six per cent of his front lights
up red.

Up close it does not matter — the boundary that actually touches is rolled sleeve against bare forearm, and that
is dE 26.5. At game-camera size it matters a lot. Rendered at 64 px tall, his head, shirt and hands merge into one
pale mass; you cannot tell which way he is facing. The apron and trousers still read, exactly as the design
promised, but we lose the head.

Then the obvious fix turned out to be backwards. **Darkening the shirt makes it worse.** Dropping it 22% raises
separation from the face to 19.9 but drops separation from the *forearm* to 15.3 — because the shirt moves *down
through* the skin's own lightness on the way. Every step that helps one boundary hurts the other.

So we searched every pale colour instead — value above 0.76, saturation under 0.18 — for one that clears both skin
samples. The ones that do are **blue, violet and lilac**, and our own palette rule reserves pale cyan for Freeze
Frame and magenta for Splice. The main character is explicitly allowed neither, so that the power colours read as
borrowed.

The cast's colour rules box the fix in. The only move that separates him without stealing a power colour is to
**deepen his skin about 10%** (`#E4BFA4`, dE 21.0) and leave the shirt alone. That is a design call and it is
Manny's, not ours, so it is written up in `CHARACTERS.md` with the numbers and left undecided.

## What we took away

- **A lit contact sheet is the wrong instrument for a colour question.** Render unlit with a Standard view
  transform or you are grading the light rig.
- **Check the back.** Every reference sheet we drew shows the front only, so the back of every model was invented
  by the generator. It happens to be clean on all six — but we only know that because we looked.
- **Measure a garment from its saturated pixels.** A shaded fold reads as a different hue and will hand you a
  false alarm.
- **An "obvious" colour fix can move the wrong way.** Two boundaries, one slider; check both before you repaint.

![Colour audit: every model, front and back, with skin-coloured pixels painted](../media/COLOUR-AUDIT.jpg)
