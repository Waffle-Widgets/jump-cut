# The street gets its small things

**Sun Nov 15, about 4:00 PM, GameStation (builder). After the noon cut-off; the Team Owner asked.**

## What we asked for

> We've already tested the package, let's get as many assets in as possible to make the game look cleaner. In the
> meantime I will work on a prompt for the video.

## What happened

Listed every kit model still placed in the level, with how many of each, and took the ones there are most of that
are not structure, not physics props and not M Station's: air-conditioner units (19 placed), utility poles (13),
hedges (11), shop display stalls (6), the plain A-frame signs (5) and the rooftop tanks (4).

**Tripo runs several at once.** Typing a new prompt and pressing Generate while the last one is still running
queues it, so five were generating together, about three minutes for the lot. The prompts as typed (each ends
"Stylized anime background prop, clean simple shapes, flat painted colors, slightly worn, no text, no logos."):

- *A wall-mounted outdoor air conditioner condenser unit: a white-grey rectangular metal box with a large round
  fan grille on the front, standing on two small wall brackets, with a short insulated pipe at the side.*
- *A neatly trimmed rectangular green boxwood hedge, low and long, about 1.8 metres long and 0.9 metres tall, dense
  small leaves, flat top, growing out of a thin strip of dark soil.*
- *A Japanese concrete utility pole, nine metres tall and slender, with two wooden crossarms near the top carrying
  ceramic insulators, a grey cylindrical transformer mounted below them, and a few small cable brackets down the
  pole. Just the pole standing upright, no wires.*
- *A small Japanese greengrocer street display stall: a slanted wooden stand with three tiers of wooden crates
  full of colorful fruit and vegetables, open at the front, plain wooden back.*
- *A rooftop water tank for a Japanese city building: a large cylindrical steel tank with a shallow conical lid,
  standing on a square steel frame with four legs and cross braces, a ladder up one side and a pipe going down.*
- A-frame, second try: *One single folding A-frame sandwich board sign standing open on the pavement: two wooden
  framed chalkboard panels hinged together at the top so that from the side it forms an upside-down letter V. One
  object only.*

**Two were thrown away.** The first A-frame prompt said "two hinged wooden frames" and came back as two separate
boards standing side by side. And a "red and white nobori banner" came back as a plain red-and-white bicolour,
which reads as a national flag; not worth the question.

**The pole was not fitted to the kit box.** The kit pole is 3 m wide at the crossarm and the Tripo one about 1.2 m;
stretching it to fit would have made a 9 m pole oval. It is sized by height with its origin under its foot, so the
kit's cables now end about a metre short of the new crossarms. They are nine metres up.

**M Station's six small cafe pieces** (table settings, wall art, clock, rug, awning, door curtain) landed on
`M_STATION/cafe-small` at 3:51 and went in with the stall: 15 actors.

## My mistake, found while doing this

The meter boxes and ducts from the last batch were baked facing the WALL. I had read the kit box (Unreal y from
-22.5 to 0) as "it sticks out toward -Y, so that is the front". The kit's origin is on its FRONT plane and the body
goes back into the wall, so the front is Unreal +Y, which is Blender -Y, exactly as the bake script's first comment
says. The last devlog entry says the opposite and is wrong. `tools/jc_flip_by_mesh.py` turns the ten placed actors
180 degrees and slides each one until its bounds are where they were (0.00 cm off on all ten). That is level data
only, so nothing committed had to be re-imported.

![Cafe with the small pieces, and the street](../media/2026-11-15-street-and-cafe-fifth-batch.png)

## Checked, and not checked

- Checked by script in the running game: three capsule-width sweeps through the cafe door are clear (the new
  curtain is walk-through); the rug's collision is off.
- Checked by eye from the game camera: the wall art, awning valance and curtain from inside the cafe; the new poles
  on the street.
- **Not checked by eye:** the air-conditioner units, the hedges, the stalls, the tanks, the clock and table settings
  up close, and the meter boxes and ducts after the turn. Their sizes match the kit pieces by script.
- No packaged build has any of this.

## What we learned

- **Count the placed copies before choosing what to remake.** Nineteen air-conditioner boxes change the street more
  than one fire stair does.
- **Say "one object" to a text-to-3D model, and never describe a thing as "two" of anything.**
- **When a note in the tool says which way is front, a number that seems to disagree is the thing to doubt.**
