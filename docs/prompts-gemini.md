# Reference-picture prompts — Gemini, text only

These are the prompts used in **Gemini in the browser** (`gemini.google.com`, `Create image` on, model
**4 Hydrogen**). They are **self-contained text**: no reference picture is uploaded with them, so every line of
the design has to be in the words. That is deliberate — see "Why text only" below.

They are kept **separate from [`prompts.md`](prompts.md)** because that file is parsed by `tools/gen_images.py`
(local ComfyUI + Qwen-Image) and a code added there becomes a thing the script will draw. These are not for the
script.

Takes land in `Art/Refs/gen/gemini2/CODE-N.jpg`, which git ignores. Copy a pick to `Art/Refs/<name>_apose.png`
and commit that, so the picture a 3D model was made from sits in the repo next to the model.

**Settings that matter**, because getting one wrong wastes the take:

| | Value | What goes wrong otherwise |
|---|---|---|
| `Create image` toggle | **on** | Gemini answers in prose about the character instead of drawing it |
| Model | **4 Hydrogen** | `4 Argon` is the reasoning model, not the image one |
| Aspect ratio | **3:4** figures, **4:3** the cleaver | 1:1 is the default and crops a standing figure's feet |
| Download | **"Download full size image"** | The in-page image is a 765x1024 display copy; the button gives the real ~1792x2400 |

**Why text only.** The earlier Gemini pass uploaded the ComfyUI pick with each prompt to carry the costume across.
That works, but it hands the model the drifted rendering as well as the design, and an image model copies what it
is shown more faithfully than what it is told. Drawing from words alone makes the prompt the single source of the
design — which means the design has to be written down properly, which is the real value.

**Design source.** Every detail below is taken from [`CHARACTERS.md`](CHARACTERS.md). If the two disagree,
`CHARACTERS.md` is right and this file is stale.

**Rules note.** No trademarks or logos, nothing above 13+ (`docs/RULES.md`). The mob boss's lapel pin is an
invented plain diamond, never a real family crest, and no blade in this project ever carries blood.

---

## The four blocks every prompt repeats, and why

Each prompt below is built from the same four blocks. They are repeated in full in every prompt rather than
referenced, because each generation is judged on its own and a prompt that leans on an earlier message inherits
whatever that message got wrong.

1. **STYLE** — cel-shaded anime, stated as *drawing instructions* (flat fills, few large shadow shapes, clean
   outline) rather than as a style name. A style name alone is what let worn leather and a tailored suit drag the
   earlier takes into a gritty western-comic look.
2. **NOT A SHEET** — one figure, one view, no text. The words "reference sheet" in a prompt produce a multi-view
   page with labels and colour swatches, and labels get baked into the 3D mesh as surface detail.
3. **POSE** — A-pose with wide gaps between arms and torso and fingers spread. Meshy fuses whatever touches.
4. **NO TEXTURE** — the named failure modes, individually: scuffs, weave, cross-hatching, gradients, grain.
   Naming the failure is what worked; repeating the style words was not.

---

### GEM2-MC — the main character, `CafeWalker`

Aspect ratio **3:4**.

> A single anime character illustration of one young adult man, drawn in a clean cel-shaded anime style: flat
> areas of solid colour, hard-edged shadows, only two or three large simple shadow shapes per garment, a clean
> dark outline around every form, and a face drawn with a few confident clean lines. Bright overall, light and
> airy, nothing dark or heavy.
>
> He stands facing the viewer in a relaxed A-pose, his whole body from the top of his head to the soles of his
> shoes inside the frame. Both arms are angled down and away from his sides at about forty-five degrees, with a
> wide empty gap of white background visible between each arm and his torso. Both hands are open with the palms
> toward the viewer and the fingers spread wide apart and clearly separated from one another. His legs are apart
> with a clear gap between them. He stands straight and symmetrical.
>
> He is slim and narrow with an upright posture, about average height. Short messy black hair. A calm, tired,
> ordinary face, clean-shaven. He wears a warm cream long-sleeve shirt with the sleeves pushed up to the elbows,
> a dark forest green canvas apron tied at the waist that makes a flat clean rectangle across his hips, charcoal
> grey work trousers, and plain grey canvas sneakers. A small folded cloth hangs from the knot of the apron tie
> at his hip. He carries nothing and holds nothing. No jacket, no weapon, no badge, no insignia.
>
> His colours are only cream, dark green, charcoal and grey. There is no cyan, no blue, no magenta, no purple and
> no pink anywhere in the picture.
>
> One single figure, one single front view, alone in the picture. This is not a reference sheet and not a
> character model sheet: no text, no letters, no words, no labels, no arrows, no measurements, no colour swatches,
> no grid, no panels, no second view of him, no turnaround, no border or frame.
>
> No photographic texture of any kind: no fabric weave, no stitching detail, no scuff marks, no scratches, no
> wear, no dirt, no cross-hatching, no stippling, no visible brush strokes, no gradient or airbrushed shading, no
> film grain, no painterly rendering, no 3D render look.
>
> The background is flat pure white and completely empty. Even flat lighting from the front. No shadow on the
> ground beneath him.

### GEM2-BOSS1 — the crash driver, `CrashDriver`

Aspect ratio **3:4**. The hard one: see the note under the prompt before judging a take.

> A single anime character illustration of one lean man in his forties, drawn in a clean cel-shaded anime style:
> flat areas of solid colour, hard-edged shadows, only two or three large simple shadow shapes per garment, a
> clean dark outline around every form, and a face drawn with a few confident clean lines. Bright overall, light
> and airy, nothing dark or heavy or gritty.
>
> He stands facing the viewer in a relaxed A-pose, his whole body from the top of his head to the soles of his
> boots inside the frame. Both arms are angled down and away from his sides at about forty-five degrees, with a
> wide empty gap of white background visible between each arm and his torso. Both hands are open with the fingers
> spread wide apart and clearly separated. His legs are apart with a clear gap between them.
>
> He is lean but his jacket thickens his chest and shoulders, so he reads as bulky above the waist and thin below.
> A cracked open-face motorcycle helmet is pushed back off his face and sits on the back of his head, giving his
> head a lopsided asymmetric shape. A pair of goggles with pale frosted lenses rests on the brim of the helmet. He
> wears a brown leather racing jacket, a torn dark grey scarf, brown leather driving gloves, dark charcoal
> trousers and heavy dark boots. He carries nothing and holds nothing.
>
> Across his left shoulder only, a patch of frost: sharp angular pale cyan ice crystals with crisp straight
> geometric edges, like flat shards of broken glass, drawn as flat pale cyan shapes with a clean dark outline and
> lying close against the shoulder of the jacket. The ice is hard and angular. It is not soft, not fluffy, not
> feathery, not furry, not woolly, not sheepskin, not a fur collar and not a fur trim. It appears nowhere else on
> him — his right shoulder is plain leather.
>
> The leather is drawn as flat clean areas of solid mid-brown with one simple hard-edged shadow shape. The leather
> is new and smooth. No scuffs, no scratches, no creases, no wrinkles, no wear marks, no patina, no stains, no
> studs, no zippers rendered in detail, no texture of any kind on the leather.
>
> One single figure, one single front view, alone in the picture. This is not a reference sheet and not a
> character model sheet: no text, no letters, no words, no labels, no arrows, no measurements, no colour swatches,
> no grid, no panels, no second view of him, no turnaround, no border or frame.
>
> No photographic texture of any kind: no fabric weave, no stitching detail, no cross-hatching, no stippling, no
> visible brush strokes, no gradient or airbrushed shading, no film grain, no painterly rendering, no comic-book
> inking texture, no 3D render look.
>
> The background is flat pure white and completely empty. Even flat lighting from the front. No shadow on the
> ground beneath him.

**Why this one is written so defensively.** A leather jacket drags every image model tried so far toward texture,
and his frost has come back as **white fur trim** once in ComfyUI and once in Gemini — two tools, same failure.
The fix both times was describing the *shape* of the ice rather than the material, and naming fur explicitly as
the thing it must not be. Judge a take on those two things first: is the leather flat, and does the frost read as
glass rather than wool.

### GEM2-BOSS2 — the mob boss, `CleaverBoss`

Aspect ratio **3:4**. **Empty-handed on purpose** — the cleaver is a separate model on a hand socket
(`CHARACTERS.md`), because a blade drawn across his leg fuses into the trousers in image-to-3D.

> A single anime character illustration of one broad heavyset older man, drawn in a clean cel-shaded anime style:
> flat areas of solid colour, hard-edged shadows, only two or three large simple shadow shapes per garment, a
> clean dark outline around every form, and a face drawn with a few confident clean lines. Bright overall, light
> and airy, nothing dark or heavy or gritty.
>
> He stands facing the viewer in a relaxed A-pose, his whole body from the top of his head to the soles of his
> shoes inside the frame. Both arms are angled down and well away from his sides, with a wide empty gap of white
> background visible between each arm and his torso. Both hands are completely empty and open with the fingers
> spread wide apart and clearly separated. His legs are apart with a clear gap between them.
>
> He is the broadest figure imaginable for his height: square heavy shoulders, a deep chest, a thick neck, built
> roughly a third wider through the chest than an average man. Slicked-back grey hair. A hard, heavy, scarred
> face with one clean pale scar line across one cheek. He wears a sharply tailored charcoal grey double-breasted
> suit jacket worn open, over a deep magenta dress shirt with no tie, matching charcoal trousers and polished
> black shoes. On his left lapel is a small plain geometric diamond-shaped metal pin — a simple abstract diamond
> outline, invented, with no emblem, no letters, no symbol and no crest on it. On the backs of both hands are
> stylised flat wave tattoos, drawn as simple curved dark blue line shapes.
>
> His hands are empty. He is holding no cleaver, no knife, no weapon, no cane, no cigarette and no object of any
> kind. There is nothing in the picture except the man.
>
> One single figure, one single front view, alone in the picture. This is not a reference sheet and not a
> character model sheet: no text, no letters, no words, no labels, no arrows, no measurements, no colour swatches,
> no grid, no panels, no second view of him, no turnaround, no border or frame.
>
> No photographic texture of any kind: no fabric weave, no pinstripes, no suit cloth texture, no stitching
> detail, no cross-hatching, no stippling, no visible brush strokes, no gradient or airbrushed shading, no film
> grain, no painterly rendering, no comic-book inking texture, no 3D render look. No blood anywhere.
>
> The background is flat pure white and completely empty. Even flat lighting from the front. No shadow on the
> ground beneath him.

### GEM2-CLEAVER — the cleaver prop

Aspect ratio **4:3**, because a cleaver seen side-on is a landscape shape and a 3:4 frame wastes half the pixels.

> A single object illustration of one heavy steel meat cleaver, alone in the picture, drawn in a clean cel-shaded
> anime style: flat areas of solid colour, hard-edged shadows, two or three large simple shadow shapes, and a
> clean dark outline around every form.
>
> The cleaver lies flat and is seen straight from the side in perfect profile, horizontal, filling most of the
> width of the frame, blade to the left and handle to the right. The blade is a large clean rectangle of flat
> light blue-grey steel with a straight cutting edge along the bottom and a single round hole near its top left
> corner. The handle is dark warm brown wood with three small round rivets in a row where it meets the blade.
>
> The whole object is inside the frame with empty white space around it. Nothing else is in the picture: no hand,
> no person, no table, no block, no food, no second knife, no blood.
>
> This is not a reference sheet: no text, no letters, no words, no labels, no arrows, no measurements, no colour
> swatches, no grid, no panels, no second view of the cleaver, no border or frame.
>
> No photographic texture of any kind: no metal grain, no brushed-steel streaks, no scratches, no nicks, no rust,
> no wood grain detail, no cross-hatching, no stippling, no gradient or airbrushed shading, no reflections of a
> room, no 3D render look.
>
> The background is flat pure white and completely empty. Even flat lighting. No shadow on the ground beneath it.
