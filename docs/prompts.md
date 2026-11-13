# Reference-picture prompts

Prompts for `tools/gen_images.py`, which draws them on M Station's graphics card (ComfyUI + Qwen-Image, nothing
goes online). Run one by its code:

    python tools/gen_images.py MC-APOSE --takes 3 --size 1024x1536

Takes land in `Art/Refs/gen/CODE-N.png`, which git ignores. Copy the one we pick to `Art/Refs/<name>_apose.png`
and commit that, so the picture a 3D model was made from is in the repo next to the model.

**What the A-pose prompts are for.** They are the input picture for Meshy (image-to-3D), so they follow
`CLAUDE.md`: full body, plain white background, A-pose with clear gaps between the arms and the body. A pose with
the arms against the torso gives a 3D model with the arms fused to the chest.

**The look.** Cel-shaded anime. When the first four codes below were written it was only the leading candidate
(the cel-shader demo on `mendezm87/anime-look` and the `CafeWalker` model); the team **chose** it on the evening of
Nov 12 (`ROADMAP.md`, Decisions), so it is now the style and not a candidate.

**Rules note.** No trademarks or logos, nothing above 13+ (`docs/RULES.md`). For the mob boss that means an
invented crest or none at all, never a real family crest, and a clean blade — no blood.

---

### MC-APOSE
> anime character reference sheet, cel shaded with hard-edged shadows and clean dark line art, full body, a young
> adult man standing straight in an A-pose, arms angled down and away from his sides with clear empty space between
> each arm and his torso, palms open, legs apart, facing the viewer, short messy black hair, calm tired face, a
> cream long-sleeve shirt with the sleeves pushed up, a dark green canvas apron tied at the waist, charcoal work
> trousers, scuffed grey sneakers, a folded cloth hanging from the apron tie, flat plain white background, even
> front lighting, no ground shadow

### BOSS1-APOSE
> anime character reference sheet, cel shaded with hard-edged shadows and clean dark line art, full body, a lean
> man in his forties standing straight in an A-pose, arms angled down and away from his sides with clear empty
> space between each arm and his torso, legs apart, facing the viewer, a cracked open-face motorcycle helmet pushed
> back on his head, frosted goggles resting on the brim, a battered brown leather racing jacket with pale frost
> creeping across one shoulder, a torn dark scarf, worn leather driving gloves, dark trousers, heavy boots, flat
> plain white background, even front lighting, no ground shadow

### BOSS2-APOSE
> anime character reference sheet, cel shaded with hard-edged shadows and clean dark line art, full body, a broad
> heavyset older man standing straight in an A-pose, arms angled down and away from his sides with clear empty
> space between each arm and his torso, legs apart, facing the viewer, slicked back grey hair, a hard scarred
> face, a sharply tailored charcoal double-breasted suit worn open over a deep magenta shirt with no tie, a plain
> geometric diamond pin on the lapel, stylised wave tattoos on the backs of his hands, holding a heavy clean
> steel cleaver point down in his right hand, flat plain white background, even front lighting, no ground shadow

### BOSS2-NOBLADE
> anime character reference sheet, cel shaded with hard-edged shadows and clean dark line art, full body, a broad
> heavyset older man standing straight in an A-pose, both arms angled down and well away from his sides with a wide
> empty gap between each arm and his torso, both hands empty and open with the fingers spread, legs apart, facing
> the viewer, slicked back grey hair, a hard scarred face, a sharply tailored charcoal double-breasted suit worn
> open over a deep magenta shirt, a plain geometric diamond pin on the lapel, stylised wave tattoos on the backs
> of his hands, flat plain white background, even front lighting, no ground shadow

### BOSS3-APOSE
The stunt double, boss 3 — a **proposed** character: see
[`CHARACTERS.md`](CHARACTERS.md#the-third-boss--stuntdouble-proposed) before spending takes on him. The
self-contained Gemini version is `GEM2-BOSS3` in [`prompts-gemini.md`](prompts-gemini.md); this is the same design
written for this script. Two deliberate differences from the four codes above. **It does not say "reference
sheet"** — that phrase produces a multi-view page with labels and colour swatches, and image-to-3D bakes the labels
into the mesh as surface detail (`CHARACTERS.md`, text-only Gemini pass, lesson 2). The older codes predate that
finding and are left as they are because the cast was drawn from them. **And the arms are wider than 45°**,
because he has shoulder pads and `trellis_character.py`'s weighting mis-assigns a shoulder accessory to the
clavicle.

> anime character illustration, single front view of one man alone, cel shaded with hard-edged shadows and clean
> dark line art, flat areas of solid colour, two or three large simple shadow shapes per garment, bright and light,
> full body from the top of his head to the soles of his boots, a slim athletic man in his mid-thirties with a
> narrow waist standing straight in a wide A-pose, both arms angled down and away from his sides at about
> fifty-five degrees with a large empty gap of white background between each arm and his torso, both hands empty
> and open with the fingers spread wide apart and separated, legs well apart with a wide gap of white background
> between the thighs and between the ankles, facing the viewer, very short dark buzz-cut hair, a cheerful relaxed
> clean-shaven face with laugh lines and one thin pale scar on the chin, a bright safety orange one-piece coverall
> zipped up to a flat stand-up collar, dark navy blue protective pads lying flat and flush on the shoulders,
> elbows, hips, knees and shins with no gap and no bulging foam under them, two flat pale grey bands around each
> upper arm and one flat pale grey band across the chest, flat dark navy harness webbing across the chest and over
> both shoulders lying flush with one plain flat rectangular plate at the centre of the chest, a flat dark navy
> belt, dark navy boots, bare hands, nothing hanging or dangling from the harness, nothing protruding past his
> silhouette, no cape, no scarf, no helmet, no hat, holding nothing, no cyan and no magenta and no purple anywhere,
> no letters or numbers or logos or patches on the coverall, no text, no labels, no colour swatches, no second
> view, no panels, no border, no fabric weave, no stitching detail, no scuffs, no dirt, no soot, no burn marks, no
> blood, no gradient shading, flat plain white background, even front lighting, no ground shadow

### CLEAVER-PROP
> a single heavy steel meat cleaver lying flat and seen straight from the side, filling the frame, clean polished
> blade with a dark wooden handle and three rivets, one round hole near the top corner of the blade, cel shaded
> with hard-edged shadows and a clean dark outline, flat plain white background, even lighting, no ground shadow,
> nothing else in the picture
