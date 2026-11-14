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

### UI-TITLE4
The title card, **third concept, and the one being built**. The Team Owner corrected the back-to-back pair on
Sat Nov 14: *"I was thinking two halves of the main character, half barista and half director, and together they
make one person on the screen but there is a clear split down the center. The barista half looks like he does
normally, the director version looks powerful."*

**`UI-TITLE3` drew two whole people standing beside each other.** That is a different picture and it does not do
what the animation needs. Here there is **one** body, one head, one face, standing square to the camera dead in
the middle of the frame, and the costume changes at the picture's exact vertical centre: his right-hand side (the
viewer's left) is the apron, his left-hand side (the viewer's right) is the coat. Cut down that line, the first
fade shows **half a man**, and the second completes him - which is the storyboard's own first two beats, said
properly for the first time.

**Why the composition has to be dead-on frontal and dead-on centred.** The cut is at `w // 2` and nothing moves it.
If the figure sits 40 px left of centre, the split does not run down his nose, it runs down his cheek - the barista
half gets a sliver of coat and the join stops reading as one person. `split_title_pair.py --one-body` measures this
and refuses the take; see its notes. A three-quarter turn fails the same way, because a turned head has no straight
vertical midline to cut along.

**The forearm rings swap arms here, and that is staging rather than a redesign.** Only his left arm is inside the
director half, so `{CafeWalker:director_half}` puts the three rings there. The count is the invariant - three, one
per power - and `docs/character-locks.json` now says so in as many words.

**The clear split is a costume and lighting change, not a drawn line.** A line drawn down the middle would be
bisected by the cut and half of it would fade in with the barista, reading as a stray mark - the same trap
`UI-TITLE3` take 1 fell into. The warm/cool lighting break and the apron-to-coat change carry it instead.

    python tools/gen_images.py UI-TITLE4 --print    # the words, to paste into Gemini
    python tools/gen_images.py UI-TITLE4 --takes 3  # or draw locally

**Three takes drawn in Gemini, Sat Nov 14 06:11-06:16 UTC** (`Art/Refs/gen/gemini4/GEM4-UI-TITLE4-{1,2,3}.png`,
gitignored; the picked take is committed as `Art/UI/T_UI_TitlePair.png`). What they settled:

| | Take 1 **(picked)** | Take 2 | Take 3 |
|---|---|---|---|
| One body, not two people | yes | yes | yes |
| Off the cut (limit 20 px) | **2 px** | 2 px | 3 px |
| Halves equally wide (limit 22%) | **2%** | 2% | 4% |
| Apron: one neck strap, square bib pocket | yes | yes | yes |
| Three cyan forearm rings | yes | yes | yes |
| A line drawn down his face | **no** | **yes** - top edge to collar | **yes** - top edge to chin |
| Skin tone matches across the cut | yes | yes | **no** - the coat half's face is greyer |

**The composition landed on the first take and on all three.** Every one came back as one centred frontal body
with the costume changing at the midline, inside 3 px of the cut and inside 4% on width. That is the opposite of
how `UI-TITLE2` went, where the first take ignored "back to back" entirely - and the reason is that this
composition does not ask the model to hold two things true at once.

**Take 1 was picked because the other two have a line drawn down his face.** Gemini's habit of drawing a divider
between two panels survives into this composition, except here it lands *on him* - a hard black line from the top
edge, through the hair, down the nose. Above his head it is removable (`--erase-seam 8 --erase-rows 0:17`); over
his face it is not, because filling those columns with the background cuts a cream slot through him. Take 1 drew
no line at all, so **the committed picture needed no retouch of any kind** - unlike the title card it replaces,
which had a badge painted out of its grille.

Drawn in **Gemini** (`Create image`, Hydrogen, 16:9), which beat the local ComfyUI/Qwen path on this kind of
picture. **Reject a take for**, in order: two separate people instead of one body; the midline not on the picture's
centre; a three-quarter or turned head; a cross-back apron; the two halves not joining at the shoulder; any scenery
or lettering at all.

> anime key visual illustration, cel shaded with hard-edged shadows and clean dark line art, flat areas of solid colour, only two or three large simple shadow shapes per garment, bright and light and airy, a symmetrical centred poster composition of ONE SINGLE PERSON and one person only - one body, one head, one face, one neck, two eyes, a pair of shoulders joined to each other - standing square to the camera and facing straight forward towards the viewer with his head perfectly level and not turned, shown from the waist upward with the bottom edge of the picture cutting across him at the waist, placed exactly in the middle of the frame so that the picture's own vertical centre line runs precisely down the middle of his face between his two eyes, down the bridge of his nose, through the middle of his mouth and chin, down the centre of his throat and down the centre of his chest and stomach, and this one person wears a different costume on each side of that centre line with a clean hard perfectly straight vertical boundary at the exact centre of the picture where one costume stops and the other starts, on the viewer's left of that centre line he is {CafeWalker:bust}, on the viewer's right of that centre line he is {CafeWalker:director_half}, the two sides are the two halves of the same single continuous unbroken body and they join at the centre with both shoulders at exactly the same height and the two halves of his one face meeting exactly and lining up perfectly, the viewer's left half of the picture is lit with warm flat even daylight, the viewer's right half is a little cooler and deeper with one narrow clean line of pale cyan rim light running down his outer edge on that side only, the background is one single flat plain field of warm pale cream colour that is completely empty from edge to edge, generous wide empty margins of that same flat cream at the left and right edges well clear of both of his shoulders, no second person, no twin, no duplicate, no mirror reflection, no scenery, no furniture, no walls, no windows, no clapperboard, no text, no letters, no numbers, no logos, no signs, no drawn dividing line

### UI-TITLE3
The title card, **third concept, and the one being built**. The Team Owner asked for a title *animation* on Fri Nov 14:
*"half of the barista fade into frame then the other half fades in as the director, then have a clapperboard fade in
over them, snap, then transition through them to the background."* He chose the expensive version of it - the two
halves drawn as separate images so the seam is real - and then solved its own worst problem himself: *"see if you can
do the characters in one shot [so they look as] they would look after fading in so you can just do an easy split. They
only really need to show the torso up."*

**That is why this is one prompt and not two.** Two independently drawn halves would not line up: the shoulder line,
the head height and the lighting would all disagree at the seam, and no amount of prompt wording fixes that. Drawn
together in one picture and cut down the exact centre afterwards, the seam is guaranteed, because both halves came off
the same drawing. `tools/split_title_pair.py` does the cut and checks it.

**So the composition is doing a job, not just looking nice.** Every clause about the centre line is there because the
cut has to land on it: the two figures' backs meet along one straight vertical line at the exact horizontal centre, and
nothing of either figure - hair, shoulder, arm, hand - crosses it. If something crosses, the halves tear when they fade
in one at a time. Both figures are the same height with their heads at the same level, so neither half looks wrong
alone, which is exactly how the first second of the animation shows it.

**The headroom problem is gone, and worth understanding rather than inheriting.** `UI-TITLE2` below fought the model
for an empty top third to put the game's name in and never got past 16.3%. An animation does not need it: the lettering
lands on the clapper snap, over the background, after the figures have wiped away. So this prompt asks for no empty band
at all and spends the whole frame on the two of them - which is also what "torso up" buys.

**The clapperboard is not in this picture.** It fades in over both figures as its own element, so a board in his hand
would have put two in the shot. It is drawn by code, not generated - `tools/make_clapperboard.py` - because it is a
geometric object with a flat blank slate, and a blank slate is the one thing the model keeps writing on. That is also
why the director costume's clapperboard moved out to `{CafeWalker:director_board}`; this prompt uses the plain
`{CafeWalker:director}`.

**The director costume is new.** The Team Owner: *"You can give the main character a whole new outfit if it works, just
get the point across that he becomes a director of reality when all powers have been collected."* The charcoal bomber
jacket became a long open charcoal black coat with one line of pale cyan power-light down each open edge and **three
cyan rings on his right forearm, one per power collected**. The three rings are the whole point of the picture: they are
how the shot says "all of them" without a word of text, which `docs/RULES.md` 15d would ban anyway.

    python tools/gen_images.py UI-TITLE3 --print    # the words, to paste into Gemini
    python tools/gen_images.py UI-TITLE3 --takes 3  # or draw locally

Drawn in **Gemini** (`Create image`, Hydrogen, 16:9), which beat the local ComfyUI/Qwen path on exactly this kind of
picture - see `UI-TITLE2`'s notes. Judge every take on three things before anything else: **the two faces must be the
same man**, the apron's single neck loop must be visible on the left figure, and **nothing may cross the centre line**.

**Three takes drawn in Gemini, Fri Nov 14 05:49-05:58 UTC** (`Art/Refs/gen/gemini3/GEM3-UI-TITLE3-{1,2,3}.png`,
gitignored; the picked take is committed as `Art/UI/T_UI_TitlePair.png`). What they settled:

| | Take 1 | Take 2 **(picked)** | Take 3 |
|---|---|---|---|
| Same man, both halves | yes | yes | yes |
| Apron: one neck loop, square bib pocket | yes | yes | ambiguous - reads as two shoulder straps |
| Three cyan forearm rings | yes | yes | yes |
| Clear of the centre cut | yes, but a drawn divider line sits on it | **yes, a clean 7 px gap** | **no - the coat crosses the centre** |
| Heads level | 0 px | 0 px | 0 px |

**The lock held on the first take, in both costumes, three times running.** Single neck loop, square bib pocket,
same face, same hair - and exactly three rings every time. For contrast, the local ComfyUI/Qwen path needed seven
takes to draw that apron correctly twice. The positively-worded strap clause (see the say-what-is-there rule in
`docs/character-locks.json`) is doing the work in both paths.

**Take 2 was picked over take 1 only because of the centre.** Gemini likes to draw a thin vertical divider between
two figures that are presented as a pair - take 1 has one, three pixels wide, running the full height. Left in, half
of that line fades in with each half and reads as a stray mark down the middle of the screen. `split_title_pair.py
--erase-seam 7` removes it cleanly, and take 1 passes every check with it, so it is a usable fallback. Take 2 simply
did not draw one.

**Take 3 is the composition to avoid and is kept as the counter-example.** The director's coat crosses the centre
and overlaps the barista. It looks fine as a picture and is useless here: cut it in half and the coat loses a panel
to the other image, so the first fade shows a man with a slice taken out of him. The splitter fails it rather than
writing it, which is the check earning its place.

> anime key visual illustration, cel shaded with hard-edged shadows and clean dark line art, flat areas of solid colour, only two or three large simple shadow shapes per garment, bright and light and airy, a symmetrical centred poster composition of one single young man drawn twice as two figures of exactly the same height whose backs are pressed flat together along one perfectly straight vertical line at the exact horizontal centre of the picture, the left figure's body turned to face the left edge and the right figure's body turned to face the right edge, each of them turning his head to look straight out at the viewer, both figures are the same one person with an identical face and identical hair and their two heads are at exactly the same height, both figures are shown from the middle of the chest upward only and the bottom edge of the picture cuts across them at mid-chest, the whole of the left figure is inside the left half of the picture and the whole of the right figure is inside the right half of the picture and the vertical line down the exact centre of the picture is the clean straight join between their two backs, on the left {CafeWalker:bust}, on the right {CafeWalker:director_bust}, the background is one single flat plain field of warm pale cream colour that is completely empty from edge to edge, a thin pale cyan rim light down the outer edge of the right figure only, generous empty margins of that same flat cream at the left and right edges, no scenery, no furniture, no walls, no windows, no clapperboard, no text, no letters, no logos, no signs

### UI-TITLE2
The title card, **second concept**. The Team Owner rejected the crash scene outright on Sat Nov 14 - *"I don't
think we want to have that as the title anyway"* - and asked instead for the main character as a film director,
back to back with himself in the barista uniform. **Something simple**, in his words, so there is no cafe, no car,
no street and no scenery in this one at all: one flat background, two figures, two props. `UI-TITLE` is kept below
for the record and because its crash-scene notes are the file's best worked example of a prompt argument.

This is the first prompt to use a **costume form**, `{CafeWalker:director}`. Both halves of the picture take their
words from the same lock entry, so the face, hair, shirt, trousers and shoes are identical between them and only
the apron and the jacket differ. That is the point: the same man twice in one frame is the hardest consistency
test there is, and the lock is the only reason it is winnable. If his two faces disagree, the picture is rejected -
there is no retouch for that.

Both figures stand square to the viewer so the apron's single neck loop is **in frame**. See the camera-angle rule
in `docs/character-locks.json`: drawn from behind, the model invents a cross-back apron every time, and this
composition would be the obvious place to make that mistake.

    python tools/gen_images.py UI-TITLE2 --takes 3
    python tools/gen_images.py UI-TITLE2 --print    # the same words, to paste into Gemini

**Three takes drawn in Gemini, Sat Nov 14 05:11-05:16 UTC** (`Art/Refs/gen/gemini2/GEM2-UI-TITLE2-{1,2,3}.png`,
gitignored). What they settled:

| | Take 1 | Take 2 | Take 3 |
|---|---|---|---|
| Back to back | **no** - side by side | yes | yes |
| Apron: one neck loop, square pocket, front bow, towel | yes | yes | yes |
| Clapperboard slate blank | yes | yes | yes |
| Background flat and empty | yes | yes | yes |
| First row of ink, measured | 14.3% down | **5.9%** | **16.3%** |

**Take 1 came back side by side, and the prompt was at fault.** It asked for figures "back to back" *and* "seen
almost straight on from the front", which cannot both be true. The model resolved the contradiction by dropping
the back-to-back - the one thing actually asked for. Rewritten so it is physically coherent (bodies turned to the
outer edges, heads turned to the viewer) and takes 2 and 3 both obeyed it.

**The top third will not stay empty, and this is the one thing to know before using this prompt.** The title card
needs a clear band for the game's name. "The two figures are small in the frame and stand entirely within the
lower two thirds" was ignored twice, and take 2 came back *worse* than take 1 - the model composes to fill the
frame. Rewriting it as a positive description of a thing that exists ("across the whole top of the picture runs a
wide deep empty horizontal band of flat cream colour") is the repo's own say-what-is-there lever and it did move
the number, 5.9% -> 16.3%. **It did not reach 33%.** Best measured headroom over three takes is 16.3%, so either
the title text sits in the empty cream at the left and right of the figures, or it goes lower in the frame, or
the picture is drawn taller and cropped. That is a composition decision, not a prompt one.

**The lock held across both costumes.** Every take drew the same one neck strap, the same square bib pocket, the
same front bow and the same grey towel - on the first take, which the local ComfyUI/Qwen path never managed in
seven. Faces between the two figures are close but not identical; judge that one by eye on any take you pick.


> anime key visual illustration, cel shaded with hard-edged shadows and clean dark line art, flat areas of solid colour, only two or three large simple shadow shapes per garment, bright and light and airy, a simple symmetrical centred poster composition of one single young man drawn twice as two figures of exactly the same height standing with their backs pressed flat together at the exact centre of the picture, the left figure's body turned to face the left edge and the right figure's body turned to face the right edge, each of them turning his head to look straight out at the viewer, both figures are the same one person with an identical face and identical hair, both shown full length from the top of the head down to their shoes, on the left {CafeWalker}, holding a plain white paper coffee cup upright in one hand, on the right {CafeWalker:director}, across the whole top of the picture runs a wide deep empty horizontal band of flat cream colour that fills the entire upper third of the image and is completely bare, and the two figures stand below that band in the lower part of the picture with the tops of their heads well underneath it, the background is one single flat plain field of warm pale cream colour that is completely empty, the whole top third of the picture is that same flat cream colour with nothing in it at all, a thin pale cyan rim light down the outer edge of the right figure only, generous empty margins at the left and right edges, no scenery, no furniture, no walls, no windows, no text, no letters, no logos, no signs

### UI-TITLE
The title card: the moment the demo is about. The upper third is kept as plain dark wall for the title text.
Rewritten Fri Nov 13 evening after the Team Owner's review: the first take had an undamaged car with no driver
coming out of a glowing cave of glass with no street behind it, no counter or coworker near it, six floating cups
and no customers. The second take fixed all of that but drew a 1950s American car on a small-town American
street, so the car and the street are now pinned down as modern and Japanese. The driver lies on the floor by
the open door, not at the wheel, because that is where his body is in the level (-380, 220).

THE GRILLE IS A LOST ARGUMENT, and the honest record is worth more than the prompt. "No badge, no emblem" in the
prompt and "car badge, car emblem" in the negative were ignored outright. Describing the grille positively instead
("a plain black horizontal mesh grille whose centre is smooth and empty") got 1 clean take in 3, then 0 in 3 - it
cut the rate and never ended it. Six takes, one badge-free. So the wording stays (it helps) but the picked take is
patched afterwards with `tools/promote_ui.py --patch-out`, which is deterministic. Do not spend more takes on this.

The apron, by contrast, WAS fixed by the same lever: see docs/character-locks.json, "say what is there, not what
is absent". Takes 2 and 3 drew the coworker's back exactly as the lock describes it, which no take had before.

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

Both are fixed in the picked take. The tower now stands far beyond the end of the street, small and hazy behind the
rooftops. The back is plain khaki shirt with one green strap at the nape - canonical. It is still mostly luck: of
four ending-card takes after the lock was reworded, ONE drew the canonical back, one drew a single diagonal strap
and two drew a full cross-back. Counting the title card too, 2 of 7 post-rewording takes were exactly canonical,
against 0 of 4 before it. The rewording moved the odds; it did not settle the matter. Draw several takes and look
at the back of every one before picking. One residual in the pick: his waist ties are
bowed at the BACK, where the lock has them knotted at the front. Small, and the bib is not visible from behind
anyway, but it is a difference and it is written down rather than ignored.

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
