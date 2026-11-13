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

### GEM2-BOSS3 — the stunt double, `StuntDouble` (PROPOSED character)

Aspect ratio **3:4**. **The character himself is a proposal** — boss 3 is conditional in `ROADMAP.md` and nobody
has agreed to this design, so read [`CHARACTERS.md`](CHARACTERS.md#the-third-boss--stuntdouble-proposed) before
spending a take on him. The prompt is finished and self-contained either way.

Two things in it are different from the three above, both on purpose. **The arms are wider** — about fifty-five
degrees rather than forty-five — because he has shoulder pads, and `trellis_character.py`'s automatic weighting
gave `clavicle_r` 16% of the verts on `SK_CrashDriverTrellis`'s shoulder accessory and flattened the sleeve when
the shoulder swung. **And the pads are pinned down hard**, because a pad drawn floating above the sleeve with a gap
under it comes back from image-to-3D as a loose shell. He is **empty-handed and has no prop at all**, so unlike the
mob boss he needs no second prompt.

> A single anime character illustration of one slim athletic man in his mid-thirties, drawn in a clean cel-shaded
> anime style: flat areas of solid colour, hard-edged shadows, only two or three large simple shadow shapes per
> garment, a clean dark outline around every form, and a face drawn with a few confident clean lines. Bright
> overall, light and airy, nothing dark or heavy or gritty.
>
> He stands facing the viewer in a wide relaxed A-pose, his whole body from the top of his head to the soles of his
> boots inside the frame. Both arms are angled down and away from his sides at about fifty-five degrees, wider than
> a normal A-pose, with a large empty gap of white background clearly visible between each arm and his torso and
> his shoulders completely clear of his chest. Both hands are open with the palms toward the viewer and the fingers
> spread wide apart and clearly separated from one another. His legs are well apart, with a wide clear gap of white
> background between his thighs, between his knees and between his ankles. He stands straight and symmetrical.
>
> He is slim and athletic with a narrow waist and an upright, easy posture, about average height. Very short dark
> buzz-cut hair, close to the scalp. A cheerful, friendly, relaxed face with laugh lines at the corners of the
> eyes, clean-shaven, with one short thin pale scar on his chin. He looks completely untroubled and faintly
> amused.
>
> He wears a bright safety-orange one-piece coverall, zipped all the way up to a flat stand-up collar that covers
> his neck. Sewn onto the coverall are protective pads in dark navy blue: one rounded pad over each shoulder, one
> over each elbow, one over each hip, one over each knee and one down each shin. Every pad is a flat smooth panel
> lying flush against the coverall, drawn as a flat navy shape with a clean dark outline, level with the surface of
> the cloth, with no gap underneath it, no shadow underneath it and no thick bulging foam. Around each upper arm
> are two flat pale grey bands, and one more flat pale grey band runs straight across his chest. Across his chest
> and over both shoulders he wears flat dark navy harness webbing: plain flat straps lying flush against the
> coverall, with one plain flat rectangular metal plate at the centre of his chest. He wears a flat dark navy belt,
> dark navy boots, and his hands are bare.
>
> Nothing on him sticks out past the edge of his body. The pads lie flat, the straps lie flat, and nothing hangs,
> dangles or trails from the harness: no rope, no cable, no wire, no hook, no carabiner, no ring, no loose strap
> end, no protruding buckle, no cape, no scarf, no helmet and no hat. His outline is the clean simple silhouette of
> a standing man.
>
> His hands are completely empty. He is holding no weapon, no chair, no pole, no rope, no tool and no object of any
> kind. There is nothing in the picture except the man.
>
> His colours are only safety orange, dark navy blue, pale grey and his own skin tone. There is no cyan, no pale
> blue, no magenta, no purple and no pink anywhere in the picture. There are no letters, numbers, logos, badges,
> patches or printed markings of any kind on the coverall.
>
> One single figure, one single front view, alone in the picture. This is not a reference sheet and not a character
> model sheet: no text, no letters, no words, no labels, no arrows, no measurements, no colour swatches, no grid,
> no panels, no second view of him, no turnaround, no border or frame.
>
> No photographic texture of any kind: no fabric weave, no quilted stitching, no stitching detail, no scuff marks,
> no scratches, no wear, no dirt, no soot, no burn marks, no scorch marks, no cross-hatching, no stippling, no
> visible brush strokes, no gradient or airbrushed shading, no film grain, no painterly rendering, no comic-book
> inking texture, no 3D render look. No blood, no wounds and no bandages anywhere.
>
> The background is flat pure white and completely empty. Even flat lighting from the front. No shadow on the
> ground beneath him.

**Judge a take on four things, in this order.** Is there white background visible between each arm and the torso
and between the thighs; do the pads lie flat with no gap or bulge under them; is the coverall one flat orange with
two or three shadow shapes rather than a scuffed sooty garment; are his hands empty with the fingers separated.
Everything else is a costume detail a redraw can fix — those four decide whether the mesh survives. And per the
lesson in `CHARACTERS.md`, **do not ask Gemini to tweak a take**: an edit request re-rolls the rest of the design.
Change the words here and draw fresh.

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

### GEM2-COWORKER — the cafe coworker, `CafeCoworker` (beat 1)

Aspect ratio **3:4**. The person the player saves in the demo's opening beat. Her design is in
[`CHARACTERS.md`](CHARACTERS.md#the-coworker--cafecoworker-beat-1-built-in-unreal-as-a-box-not-yet-drawn); she is
built and playable in Unreal as a green box already, so this prompt is a model swap, not a blocker.

Two things in it are deliberate. **She carries nothing at all** - the obvious cafe props (a tray, a cup, a
cloth) are exactly the thin shapes held away from the body that image-to-3D fuses into the torso or drops as a
floating shard, the lesson the `CrashDriver` ice crystals cost us. **And cream, beige and tan are banned on her**,
because this cast's one measured colour failure is `CafeWalker`'s cream shirt sitting dE76 14.4 from his own face.

> A single anime character illustration of one short compact woman in her mid-twenties, drawn in a clean
> cel-shaded anime style: flat areas of solid colour, hard-edged shadows, only two or three large simple shadow
> shapes per garment, a clean dark outline around every form, and a face drawn with a few confident clean lines.
> Bright overall, light and airy, nothing dark or heavy or gritty.
>
> She stands facing the viewer in a wide relaxed A-pose, her whole body from the top of her head to the soles of
> her shoes inside the frame. Both arms are angled down and away from her sides at about forty-five degrees, with
> a large empty gap of white background clearly visible between each arm and her torso and her shoulders
> completely clear of her chest. Both hands are open with the palms toward the viewer and the fingers spread wide
> apart and clearly separated from one another. Her legs are well apart, with a wide clear gap of white background
> between her thighs, between her knees and between her ankles. She stands straight and symmetrical.
>
> She has warm mid-brown skin and very dark brown, almost black, hair tied back in a short low tail that lies
> flat against the back of her head with no loose strands standing out. Her face is open, friendly and calm.
>
> She wears a plain pure white short-sleeve shirt, a deep teal canvas apron with a flat square bib and flat ties
> lying flush against her hips, charcoal grey trousers and flat brown shoes. No cream, no beige and no tan
> anywhere on her clothes or her hair.
>
> Her hands are completely empty and she carries nothing: no tray, no cup, no plate, no cloth, no notepad, no bag
> and no strap. Nothing hangs or dangles from her apron and nothing protrudes past her silhouette - no scarf, no
> hat, no jewellery, no badge.
>
> One single figure, one single front view, alone in the picture. This is not a reference sheet and not a
> character model sheet: no text, no letters, no words, no labels, no arrows, no measurements, no colour swatches,
> no grid, no panels, no second view of her, no turnaround, no border or frame.
>
> No photographic texture of any kind: no fabric weave, no stitching detail, no cross-hatching, no stippling, no
> visible brush strokes, no gradient or airbrushed shading, no film grain, no painterly rendering, no comic-book
> inking texture, no 3D render look. No stains, no dirt and no blood anywhere.
>
> The background is flat pure white and completely empty. Even flat lighting from the front. No shadow on the
> ground beneath her.

### GEM2-GOON — the mob's foot soldier, `StreetGoon` (beats 2 to 5)

Aspect ratio **3:4**. The enemy the player actually fights, in four of the demo's six beats. His design is in
[`CHARACTERS.md`](CHARACTERS.md#the-goons--streetgoon-beats-2-to-5); `BP_Goon` has been playable since the first
build wearing Epic's mannequin, so this prompt is a model swap and not a blocker.

Three things in it are deliberate. **He wears no jacket** - an open suit jacket is what a mob foot soldier should
wear, and its lapels stand off the chest as a loose shell, the exact shape image-to-3D returns as a floating
sheet; a buttoned waistcoat gives the same chest panel lying flush. **His sleeves reach his wrists**, because the
coworker's rolled sleeves put her bare forearms outside the colour audit's head-and-hands whitelist and she reads
FLAG for it as a false positive. **And nothing on him is white or pale**: Freeze Frame's colour is "pale cyan,
almost white", every white garment measures under dE76 10 from it, and three goons stand on screen in the beats
that teach Freeze Frame.

> A single anime character illustration of one tall, broad-shouldered, heavily built young man, drawn in a clean
> cel-shaded anime style: flat areas of solid colour, hard-edged shadows, only two or three large simple shadow
> shapes per garment, a clean dark outline around every form, and a face drawn with a few confident clean lines.
>
> He stands facing the viewer in a wide relaxed A-pose, his whole body from the top of his head to the soles of
> his boots inside the frame. Both arms are angled down and away from his sides at about fifty degrees, with a
> large empty gap of white background clearly visible between each arm and his torso and his shoulders completely
> clear of his chest. Both hands are open with the palms toward the viewer and the fingers spread wide apart and
> clearly separated from one another. His legs are well apart, with a wide clear gap of white background between
> his thighs, between his knees and between his ankles. He stands straight and symmetrical.
>
> He has warm tan skin and black hair buzzed down almost to the scalp, so his head is a small clean round shape
> with no loose strands standing out. His expression is hard, flat and blank.
>
> He wears a dark graphite grey waistcoat buttoned flat and lying flush against his chest, over a medium grey
> long-sleeve shirt with the cuffs at his wrists. A dark red necktie is tucked flat under the waistcoat. A plain
> dark red cloth band is wrapped around his left upper arm, lying flush against the sleeve. He wears dark
> graphite grey trousers and flat black boots. Nothing on his clothes is white, cream, beige, pale blue or pale
> grey, and there is no magenta and no orange anywhere on him.
>
> His hands are completely empty and he carries nothing: no weapon, no knife, no bat, no club, no gun, no bag and
> no strap. He wears no jacket, no coat, no hat, no cap, no mask, no sunglasses and no jewellery. Nothing hangs or
> dangles from him and nothing protrudes past his silhouette.
>
> He carries no insignia of any kind: no letters, no numbers, no logos, no crests, no badges, no emblems and no
> tattoos anywhere on his clothes or his skin.
>
> One single figure, one single front view, alone in the picture. This is not a reference sheet and not a
> character model sheet: no text, no letters, no words, no labels, no arrows, no measurements, no colour swatches,
> no grid, no panels, no second view of him, no turnaround, no border or frame.
>
> No photographic texture of any kind: no fabric weave, no stitching detail, no cross-hatching, no stippling, no
> visible brush strokes, no gradient or airbrushed shading, no film grain, no painterly rendering, no comic-book
> inking texture, no 3D render look. No stains, no dirt and no blood anywhere.
>
> The background is flat pure white and completely empty. Even flat lighting from the front. No shadow on the
> ground beneath him.
