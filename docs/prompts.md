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

**THE CHARACTER LOCK - read this before you write a prompt with a person in it.**
`docs/character-locks.json` holds one canonical description per character. Prompts do **not** describe a
locked character in their own words; they write a token and `gen_images.py` substitutes the lock:

    {CafeWalker}          the full description - use it when he is close and most of him is in frame
    {CafeWalker:short}    the same lock, shortened - use it when he is small or far away

Locked today: `CafeWalker`, `CafeCoworker`, `CrashDriver`. The tool also folds each character's **never**
list into the negative prompt automatically, so you do not have to remember that his shirt must not be cream.

Why: on Fri Nov 13 the title card, the "to be continued" card and the itch.io cover each drew the main
character's apron differently - a crossed X-back, a plain bare back, and a bib with no neck strap at all. Three
pictures of one man, three aprons. That is what gets a game called AI slop, and it happened because each prompt
described him from memory. Now there is one description and every picture gets the same words.

`python tools/char_lock_check.py` fails if a prompt starts describing a locked character by hand again. The
A-pose prompts that **drew** the canonical sheets are exempt (they are listed as `sheet_prompts` in the lock) -
they are its source. Changing one of those means redrawing the sheet **and** remaking the rigged model.

**It is a text check, not a picture check.** It guarantees the words are identical; it cannot make the model
obey them. Looking at the take is still the job - and `--lock-ref` hands the model the actual reference sheet,
which is the stronger lever when words alone are not holding.

---

**Rules note.** No trademarks or logos, nothing above 13+ (`docs/RULES.md`). For the mob boss that means an
invented crest or none at all, never a real family crest, and a clean blade — no blood.

---

### MC-APOSE
The player. **Rewritten Fri Nov 13**, for two reasons.

**The shirt colour was a real defect.** Cream measured **dE76 8.8** from his own face tone `#FDD9BF` (dominant
texels as close as **6.0**) against a threshold of 14, so his torso and arms merged at distance - the fault
`COWORKER-APOSE` below already names as "the one failure this cast already has". It is now **medium
khaki-brown**, measured at **dE 34.8** from his skin and at least **33** from every other cast and power
colour (apron green 38.6, trousers 33.9, goon graphite 47.5, Freeze Frame cyan 50.9, Splice magenta 80.2,
StuntDouble orange 57.0). The colour word is deliberately a strong, concrete one, and the whole cream family
is pushed into the negative prompt as well: ask for "oatmeal" or "tan" and the model has an easy path back
to cream, because a barista in a cream shirt is a very strong prior.

**The pose language was the old short kind.** It predates what `GOON-APOSE` and `COWORKER-APOSE` learned, and
image-to-3D depends almost entirely on it: wide arm gaps, separated fingers, gaps between thighs, knees and
ankles. It now matches theirs. Sleeves stay **pushed up** - unlike the goon, his bare forearms sat inside the
audit's hand allowance and measured clean, so there is no reason to redesign them away.

> anime character illustration, single front view of one man alone, cel shaded with hard-edged shadows and clean
> dark line art, flat areas of solid colour, two or three large simple shadow shapes per garment, full body from
> the top of his head to the soles of his shoes, a slim upright young adult man standing straight and symmetrical
> in a wide A-pose, both arms angled down and away from his sides at about fifty degrees with a large empty gap
> of white background between each arm and his torso, both hands empty and open with the palms toward the viewer
> and the fingers spread wide apart and clearly separated, legs well apart with a wide gap of white background
> between the thighs and between the knees and between the ankles, facing the viewer, pale skin, short messy
> black hair, a calm tired expression, a medium khaki brown long-sleeve shirt in a solid earthy brown clearly
> several shades darker than his face and his hands, the sleeves pushed up to below the elbow, a dark green
> canvas apron with a flat bib lying flush against his chest and flat ties at the waist, charcoal grey work
> trousers, scuffed grey canvas shoes, a small folded cloth tucked flat at the apron tie lying against the apron,
> bare hands, holding nothing, carrying nothing, no tray, no cup, no bag, no strap, no jewellery, no hat,
> nothing hanging or dangling, nothing protruding past his silhouette, no cream and no ivory and no off-white and
> no beige and no pale yellow and no white anywhere on the shirt, the shirt must not be close in colour to his
> skin, no letters or numbers or logos or badges, no text, no labels, no colour swatches, no second view, no
> panels, no border, no fabric weave, no stitching detail, no stains, no dirt, no blood, no gradient shading,
> flat plain white background, even front lighting, no ground shadow

Draw it **portrait**. `gen_images.py` defaults to `1664x928`, which puts a standing figure in a small
part of a wide frame and throws away most of the resolution Meshy gets to work from. The rest of the cast
was drawn at `1024x1536` and this must match:

    py -3 -I tools/gen_images.py MC-APOSE --takes 3 --size 1024x1536 --neg "cream shirt, ivory shirt, off-white shirt, white shirt, beige shirt, pale shirt"

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

### COWORKER-APOSE
The cafe coworker the player saves in beat 1: see
[`CHARACTERS.md`](CHARACTERS.md#the-coworker--cafecoworker-beat-1-built-in-unreal-as-a-box-not-yet-drawn). The
self-contained Gemini version is `GEM2-COWORKER` in [`prompts-gemini.md`](prompts-gemini.md). She carries
**nothing** - no tray, no cup, no cloth, no bag - because a thin prop held away from the body is the exact shape
image-to-3D fuses into a blob or drops as a floating shard, which is what the `CrashDriver` ice crystals taught
us. Her palette is chosen so no garment and no hair sits near her skin colour, the one failure this cast already
has (`CafeWalker`'s cream shirt, dE76 14.4 from his face).

> anime character illustration, single front view of one woman alone, cel shaded with hard-edged shadows and clean
> dark line art, flat areas of solid colour, two or three large simple shadow shapes per garment, bright and light,
> full body from the top of her head to the soles of her shoes, a short compact woman in her mid-twenties standing
> straight and symmetrical in a wide A-pose, both arms angled down and away from her sides at about forty-five
> degrees with a large empty gap of white background between each arm and her torso, both hands empty and open with
> the palms toward the viewer and the fingers spread wide apart and clearly separated, legs well apart with a wide
> gap of white background between the thighs and between the knees and between the ankles, facing the viewer, warm
> mid-brown skin, very dark brown hair tied back in a short low tail lying flat against the back of her head, an
> open friendly calm face, a plain pure white short-sleeve shirt, a deep teal canvas apron with a flat square bib
> and flat ties lying flush against her hips, charcoal grey trousers, flat brown shoes, bare hands, holding
> nothing, carrying nothing, no tray, no cup, no cloth, no bag, no strap, no jewellery, no badge, nothing hanging
> or dangling, nothing protruding past her silhouette, no cream and no beige and no tan anywhere on her clothes or
> her hair, no letters or numbers or logos on the apron, no text, no labels, no colour swatches, no second view, no
> panels, no border, no fabric weave, no stitching detail, no stains, no dirt, no blood, no gradient shading, flat
> plain white background, even front lighting, no ground shadow

### GOON-APOSE
The mob's foot soldiers, the enemy the player actually fights in beats 2, 3, 4 and 5: see
[`CHARACTERS.md`](CHARACTERS.md#the-goons--streetgoon-beats-2-to-5). The self-contained Gemini version is
`GEM2-GOON` in [`prompts-gemini.md`](prompts-gemini.md). He carries **nothing** and wears **no jacket** - an open
jacket's lapels are a loose shell held away from the chest, which is the shape image-to-3D returns as a floating
sheet, the same failure the `StuntDouble` write-up warns about for pads. The chest read comes from a flat
buttoned waistcoat instead, which lies flush. Sleeves stay **long**: the coworker's rolled sleeves put her bare
forearms outside the colour audit's head-and-hands whitelist and she reads FLAG for it, which is a false positive
nobody needs twice. **Nothing on him is white or pale**, because Freeze Frame's colour is "pale cyan, almost
white" and every white garment measures under dE76 10 from it - with three goons on screen at once in the beat
that teaches Freeze Frame, that is the one collision worth designing out.

> anime character illustration, single front view of one man alone, cel shaded with hard-edged shadows and clean
> dark line art, flat areas of solid colour, two or three large simple shadow shapes per garment, full body from
> the top of his head to the soles of his boots, a tall broad-shouldered heavily built young man standing straight
> and symmetrical in a wide A-pose, both arms angled down and away from his sides at about fifty degrees with a
> large empty gap of white background between each arm and his torso, both hands empty and open with the palms
> toward the viewer and the fingers spread wide apart and clearly separated, legs well apart with a wide gap of
> white background between the thighs and between the knees and between the ankles, facing the viewer, warm tan
> skin, black hair buzzed down almost to the scalp, a hard flat blank expression, a dark graphite grey waistcoat
> buttoned flat and lying flush against his chest, a medium grey long-sleeve shirt with the cuffs at the wrists,
> a dark red necktie tucked flat under the waistcoat, a plain dark red cloth band around his left upper arm lying
> flush against the sleeve, dark graphite grey trousers, flat black boots, bare hands, holding nothing, carrying
> nothing, no jacket, no coat, no weapon, no knife, no bat, no hat, no cap, no mask, no sunglasses, no jewellery,
> no bag, no strap, nothing hanging or dangling, nothing protruding past his silhouette, no white and no cream and
> no beige and no pale blue and no pale grey anywhere on his clothes, no magenta, no orange, no letters or numbers
> or logos or crests or badges or tattoos, no text, no labels, no colour swatches, no second view, no panels, no
> border, no fabric weave, no stitching detail, no stains, no dirt, no blood, no gradient shading, flat plain
> white background, even front lighting, no ground shadow

### CLEAVER-PROP
> a single heavy steel meat cleaver lying flat and seen straight from the side, filling the frame, clean polished
> blade with a dark wooden handle and three rivets, one round hole near the top corner of the blade, cel shaded
> with hard-edged shadows and a clean dark outline, flat plain white background, even lighting, no ground shadow,
> nothing else in the picture

---

## Screen art (issue #44, Fri Nov 13 evening, M Station)

The walkthrough of `main` at `27fdc7c` found that `WBP_Title`, `WBP_Win`, `WBP_Lose` and `WBP_HUD` reference no
texture at all. These five are the pictures behind those screens and the itch.io cover. **None of them contains
lettering**: generated letters are unreliable and `docs/RULES.md` 15d bans trademarks, so the game's name and every
word are set in Unreal on top of the picture. Each prompt leaves a calm area for that text and says where.

Draw them wide (the default `1664x928`), the cover at `1328x1056` and cropped to 630 x 500 afterwards:

    python tools/gen_images.py UI-TITLE UI-WIN UI-LOSE UI-TBC --takes 2
    python tools/gen_images.py UI-COVER --takes 2 --size 1328x1056

### UI-TITLE
The title card: the moment the demo is about. The upper third is kept as plain dark wall for the title text.
Rewritten Fri Nov 13 evening after the Team Owner's review: the first take had an undamaged car with no driver
coming out of a glowing cave of glass with no street behind it, no counter or coworker near it, six floating cups
and no customers. The second take fixed all of that but drew a 1950s American car on a small-town American
street, so the car and the street are now pinned down as modern and Japanese. The driver lies on the floor by
the open door, not at the wheel, because that is where his body is in the level (-380, 220).

> anime key visual illustration, cel shaded with hard-edged shadows and clean dark line art, flat areas of solid
> colour, wide cinematic shot inside a small warm wooden city coffee shop in the daytime, a modern plain dark red
> hatchback car with smooth painted bodywork, black plastic bumpers and a plain black horizontal mesh grille
> whose centre is smooth and empty, which has smashed head first through the brick
> wall on the left and stopped half inside the room, the car is badly wrecked with a crumpled buckled bonnet, a
> cracked shattered windscreen, one smashed headlight and a dented front wing, the driver's door hangs open and
> {CrashDriver:short} lies slumped lifeless on the floor against the open door with his head down, behind the car
> a ragged hole torn through the red brick wall opening onto a narrow Japanese city street outside with modern
> tiled shop fronts and hanging overhead cables clearly visible through the hole, on the right a wooden cafe
> counter with a cash register standing close beside the car's front corner, {CafeCoworker:short} standing frozen
> still at the register an arm's length from the car, seen from the side so the single apron strap over her shoulder is visible, {CafeWalker:short} standing with his back to us in the
> lower left foreground with his whole head and shoulders and upper back in frame, two seated customers frozen
> still at a table in the middle distance, time is completely frozen so many
> small broken brick fragments and exactly three paper coffee cups and a scatter of coffee drops hang perfectly
> motionless in mid-air, a thin pale cyan rim light on the frozen pieces only, warm daylight and brown wood and
> cream painted walls everywhere else, the whole top third of the picture is empty plain dark brown wall with
> nothing in it at all, dramatic low camera angle, no text, no letters, no logos, no signs
### UI-WIN
The win screen: the yard after the cleaver boss, with Splice's violet. The left half is kept calm for text.

> anime key visual illustration, cel shaded with hard-edged shadows and clean dark line art, flat areas of solid
> colour, wide cinematic shot of an empty walled city yard at dusk between tall buildings, a heavy steel meat
> cleaver standing upright with its blade stuck in the pavement on the right side of the picture, a thin trail
> of glowing violet light curling up from the cleaver into the sky, long shadows, tall apartment towers and
> water tanks against an orange and violet evening sky, the left half of the picture is calm open sky and
> plain wall with nothing on it, low camera angle, no people, no text, no letters, no logos, no signs

### UI-LOSE
The lose screen. Nobody is hurt in it (13+): the take was simply no good.

> anime illustration, cel shaded with hard-edged shadows and clean dark line art, flat areas of solid colour, a
> dark empty film studio, a single spotlight shining straight down on {CafeWalker:apron} lying crumpled on
> the bare floor, a long strip of photographic film snapped in two lying beside it, deep navy darkness all around
> the circle of light, the upper half of the picture is plain darkness with nothing in it, quiet and still, no
> people, no blood, no text, no letters, no logos

### UI-TBC
The demo's last frame, the "to be continued" card. It carries no words, so it can be drawn before issue #17
decides what the card says. The sky is the calm area. Rewritten Fri Nov 13 evening: the tower was too close
and read as a lighthouse at the end of the lane, and the apron was drawn with crossed X straps on the back.

> anime key visual illustration, cel shaded with hard-edged shadows and clean dark line art, flat areas of solid
> colour, {CafeWalker:short} seen from behind and very small and far away at the bottom of the frame, standing
> in the middle of a long narrow city street lined with shop fronts and hanging cables, looking up at one
> enormous pale white skyscraper standing far away in the far distance many blocks beyond the end of the street,
> the tower small and hazy with distance behind the rooftops, on the very top of the distant tower a tiny empty
> folding chair under a single bright studio lamp, evening sky going from orange to deep violet filling the
> upper half of the picture, long shadows on the road, no other people, no text, no letters, no logos, no signs
### UI-COVER
The itch.io cover (630 x 500). Tighter than the title card; the top quarter is kept plain for the name.
Rewritten Fri Nov 13 evening: the apron bib was drawn with no neck strap and no chest pocket.

> anime key visual illustration, cel shaded with hard-edged shadows and clean dark line art, flat areas of solid
> colour, {CafeWalker} seen from the waist up in three quarter view, one open hand raised toward the viewer, a
> calm tired expression, around him a few shards of glass and drops of coffee and one paper coffee cup hang
> frozen in mid-air with a thin pale cyan rim light, behind him a broken red brick wall with daylight coming
> through the hole and the dented bonnet and one smashed headlight of a dark red car, the top quarter of the
> picture is plain dark wall with nothing on it, strong diagonal composition, no text, no letters, no logos
