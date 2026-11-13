# Characters

The three we are building first, decided Nov 12 (see `ROADMAP.md`, Decisions): the **main character**, the
**crash driver** who gives Freeze Frame, and the **mob boss** who gives Splice. The story they sit in is in
[`PITCH.md`](PITCH.md).

The names below are **working asset names**, not the characters' names in the story. Nobody has named them yet;
that is an open question in `ROADMAP.md`, and an agent does not get to settle it.

## The look, and why

Cel-shaded anime: hard-edged shadows, clean dark outlines, flat colour. That is not a fresh choice — it is the only
style this team has a tested path for, from the cel-shader demo on `mendezm87/anime-look` and the `CafeWalker`
model made from a drawing. `ROADMAP.md` still lists the art style under **Still to decide**, so this is the leading
candidate we are building in, not a settled one.

**Each power owns a colour, and nobody else may use it.** The player has to learn what a colour means in three
minutes, so a colour that appears twice is worse than a dull character.

| | Colour | Used by |
|---|---|---|
| Freeze Frame | pale cyan, almost white, like frost | the crash driver, and the player's Freeze Frame effect |
| Splice | magenta into violet | the mob boss, his portals, his blade's edge |
| the main character | warm cream, dark green, charcoal — **no** cyan, **no** magenta | so both power colours read as borrowed, not his |

**Judge every one of these from the game camera, not a close-up.** `CLAUDE.md` records the TRELLIS coupe that
"looked great close up and like a dark blob from the game camera". That is why each design below leads with its
silhouette: shape first, detail second.

## The main character — `CafeWalker`

An ordinary coffee shop worker. The whole twist depends on him looking like nobody special at the start, so he gets
the plainest design of the three: no coat, no weapon, no insignia.

- **Silhouette:** narrow and upright, the apron making a clear rectangle across his hips. The only read from
  distance is that flat apron line — everything else is a thin standing figure.
- **Design:** short messy black hair, tired calm face. Cream long-sleeve shirt, sleeves pushed up. Dark green
  canvas apron. Charcoal trousers, scuffed grey sneakers. A folded cloth at the apron tie — the one piece of
  silhouette that moves when he does.
- **Height:** 175 cm. **Triangle budget:** 30,000.
- **Already exists:** `Art/Refs/cafe_walker_ref.jpg` and `Art/Refs/CafeWalker_tripo_apose.glb` on
  `mendezm87/anime-look`, made with Tripo on the jam's first night. That model is the starting point, not a
  throwaway — the question for the team is whether to keep it or re-run it against the new reference sheet.

## The first boss — `CrashDriver`

The man who drives a car through the cafe wall in the opening and dies giving you Freeze Frame. **He does not
fight** — his body flickers and the power passes. So his whole job is to be read in about four seconds, lying in
broken masonry, and to make the colour cyan mean *stopped time* before the player ever presses the button.

- **Silhouette:** bulky where the main character is thin. The jacket thickens his chest and shoulders, and the
  helmet pushed back off his face gives him a lopsided head shape nobody else in the game has.
- **Design:** lean man in his forties. Cracked open-face motorcycle helmet pushed back, frosted goggles resting on
  the brim. Battered brown leather racing jacket with **pale frost creeping across one shoulder** — the power
  leaking out of him, and the only cyan on him. Torn dark scarf, worn driving gloves, heavy boots.
- **Height:** 180 cm. **Triangle budget:** 30,000.
- **Note for whoever builds the opening:** he is seen lying down and in one light. If time runs short he is a
  static mesh with one flicker effect, not a skeletal mesh with animation. That is the cheap version and it is
  almost as good.

## The second boss — `CleaverBoss`

A Japanese mob boss with a cleaver, who gives Splice. He is the **first real fight in the game** — the first time
the player has to use a power to win rather than to watch a cutscene — so he must read as dangerous instantly and
he must read as *magenta* instantly, because magenta is about to become the portal the player steps through.

- **Silhouette:** the widest shape in the game. Square shoulders in a tailored suit, and the cleaver held point
  down extends his arm into a hard straight line. From the game camera he is a broad dark rectangle with one bright
  edge — that edge is the thing the player learns to watch.
- **Design:** broad, heavyset, older. Slicked-back grey hair, hard scarred face. Sharply tailored charcoal
  double-breasted suit worn open over a **deep magenta shirt**, no tie. Stylised wave tattoos on the backs of his
  hands. A heavy clean steel cleaver with a violet glow along the edge when Splice is charging.
- **Height:** 178 cm, but built roughly 1.3x as wide as the main character through the chest.
- **Triangle budget:** 30,000.
- **The cleaver is a separate model, not part of him.** Every reference take drew the blade crossing his trouser
  leg, and image-to-3D fuses whatever overlaps — we would get a man with a cleaver growing out of his thigh. So he
  is modelled empty-handed from `BOSS2-NOBLADE`, the cleaver is modelled on its own from `CLEAVER-PROP`, and it is
  attached to a hand socket in Unreal. That is the right answer for the game anyway: a weapon on a socket can be
  swung, dropped and glowed at the edge when Splice charges. A weapon baked into the body can do none of that.
- **Two rules constraints, both deliberate:**
  - **No real crest.** `docs/RULES.md` allows no trademarks or logos. Real crime families have real crests, so his
    lapel pin is a plain invented diamond, and there is no insignia anywhere else on him.
  - **13+.** The blade stays clean — no blood, ever, on the model or in the concept art. Tattoos are stylised
    waves, which is an anime convention rather than a depiction of any real group.

## What we picked, and what is wrong with it

Twelve takes were drawn. The picks, committed next to this file:

| Character | Pick | Why that one |
|---|---|---|
| `CafeWalker` | `Art/Refs/CafeWalker_apose.png` (take 3) | The only take with every finger separated on both hands, and the widest gap between arms and torso |
| `CrashDriver` | `Art/Refs/CrashDriver_apose.png` (take 3) | Clearest gloved hands, and the frost reads as frost on **one** shoulder rather than as white fur on both |
| `CleaverBoss` | `Art/Refs/CleaverBoss_apose.png` (`BOSS2-NOBLADE` take 2) | Both arms well clear of the torso and both hands open with the fingers spread — the first three takes all had the blade across his leg |
| the cleaver | `Art/Refs/Cleaver_prop.png` (`CLEAVER-PROP` take 1) | Clean side-on blade filling the frame, nothing else in the picture |

**One thing is still wrong with this set, and one has been fixed.**

1. ~~The bosses are drawn in a different style from the main character.~~ **Fixed on 2026-11-12 — see the Gemini
   pass below.** `CafeWalker` came out as clean cel-shaded anime, exactly as asked. Both bosses came out heavier
   and grittier, closer to a western comic, because the subject matter (worn leather, a tailored suit) pulled the
   model somewhere else even though all three prompts named the same style. The drift was carried into the Meshy
   models before it was caught, so `SK_CrashDriver` and `SK_CleaverBoss` and their textures still have it.

2. **These are reference pictures, not the game's look.** Nothing here has been seen in Unreal, from the game
   camera, under the cel-shader. Per `CLAUDE.md`, that makes all of it **untested** until the builder imports it.

## Gemini pass (2026-11-12)

The team settled the art style on the evening of 2026-11-12: **cel-shaded anime** (`ROADMAP.md`, Decisions). The
cast was redrawn in it through **Gemini in the browser**, which is what `CLAUDE.md` asks for in the first place —
reference pictures come from Gemini, and the local `gen_images.py` path is the substitute for when nobody can drive
a browser.

**Why Gemini and not another `gen_images.py` run.** The drift is a consistency problem, and consistency is the one
thing a conversation gives you that a one-shot prompt does not. All four pictures were drawn in a **single Gemini
chat**, each one told to match the picture before it. The main character was drawn first and is the style anchor;
the rest were measured against him, by eye, and sent back when they missed.

**The settings that mattered:** `Create image` on (otherwise it answers in prose), model **4 Hydrogen**, aspect
ratio **3:4** for the figures and **4:3** for the cleaver. The original ComfyUI pick was uploaded with each prompt
to carry the *design* across, with the prompt saying in as many words that the upload is there for the costume and
not for the rendering.

| Character | File | Takes | Note |
|---|---|---|---|
| `CafeWalker` | `GEM-MC-1.jpg` | 1 | The anchor. Right first time |
| `CrashDriver` | `GEM-BOSS1-2.jpg` | 2 | Take 1 kept as `GEM-BOSS1-1-rejected-drift.png` |
| `CleaverBoss` | `GEM-BOSS2-1.jpg` | 1 | The closest match to the anchor of the three |
| the cleaver | `GEM-CLEAVER-1.jpg` | 1 | Hands still empty on the boss; the blade stays a separate prop |

All four are in `Art/Refs/gen/gemini/`, **which git ignores**, alongside `STYLE-COMPARISON.jpg` — a contact sheet
with the ComfyUI cast above the Gemini cast, which is the picture to look at before deciding anything.

**What the second take on `CrashDriver` was for**, because it is the reusable lesson: a leather jacket drags any
image model toward texture. Take 1 came back dark, busy and covered in scuff strokes, and the frost read as *white
fur trim* rather than ice. What fixed it was naming the failure rather than repeating the style words — delete the
scuffs, raise the value, one flat shadow shape per garment, and *"sharp angular pale cyan crystals with crisp
geometric edges, not soft, not fluffy, not feathery"*. He is still the darkest and busiest of the three.

**Not yet done:** nothing from this pass has been through Meshy. The three rigged models on `main` were all built
from the **ComfyUI** pictures, so the cast in the repo is still the drifted set until they are rebuilt. Rebuilding
all four costs 140 Meshy credits and the two-press rig flow again.

## Text-only Gemini pass (2026-11-12, evening)

The pass above uploaded the ComfyUI pick with each prompt. That carries the costume across, but it also hands the
model the drifted rendering, and an image model copies what it is **shown** more faithfully than what it is
**told**. So the cast was drawn a third time, in a **new Gemini chat with nothing uploaded at all** — only
prompts we wrote, in [`prompts-gemini.md`](prompts-gemini.md).

The real benefit is not the pictures. It is that the design now exists as **text**: if the whole cast has to be
redrawn again, in any tool, the prompt file is the source and nothing depends on a picture that happens to still
be on M Station.

| Character | File | Takes | Verdict |
|---|---|---|---|
| `CafeWalker` | `GEM2-MC-1.png` | take 1 | Design correct. **Legs close together** — a fusion risk for image-to-3D |
| `CafeWalker` | `GEM2-MC-2.png` | take 2 | Wide stance, Meshy-safe. **But the design drifted**: brown hair not black, smiling not tired, collared shirt, brown leather shoes not grey sneakers, folded cloth gone |
| `CrashDriver` | `GEM2-BOSS1-1.png` | take 1 | Style and leather both right. **Ice spikes protrude past his silhouette** |
| `CrashDriver` | `GEM2-BOSS1-2.png` | take 2 | **The pick.** Ice lies flat on the shoulder, inside the silhouette |
| `CleaverBoss` | `GEM2-BOSS2-1.png` | take 1 | **The pick.** Hands empty, invented diamond pin, wave tattoos, no blade |
| the cleaver | `GEM2-CLEAVER-1.png` | take 1 | **The pick.** Side-on, clean, nothing else in frame |

All in `Art/Refs/gen/gemini2/`, **which git ignores**, with two contact sheets: `TEXT-ONLY-COMPARISON.jpg` (the
uploaded-reference pass above the text-only pass) and `MC-STANCE-COMPARISON.jpg` (the main character's two takes).

**Three things this pass established, which are the reusable part:**

1. **The driver's frost is fixed, and it took two tries across three tools to learn how.** Describing the
   *material* gives fur. Describing the *shape* — "sharp angular pale cyan crystals with crisp geometric edges"
   — gives ice. But take 1 then drew those crystals as spikes **sticking out past his shoulder**, and
   image-to-3D turns a thin protruding spike into a fused blob or a shard floating off the mesh. The fix was
   asking for the ice as flat angular plates lying **on the surface** of the jacket, with nothing crossing the
   silhouette. That rule — *nothing protrudes from the outline* — belongs in every A-pose prompt from now on.
2. **Never write "reference sheet" in an image prompt.** It produces a multi-view page with labels and colour
   swatches, and image-to-3D bakes the labels into the mesh as surface detail. Every prompt in
   `prompts-gemini.md` rules it out by name.
3. **An edit request costs design fidelity.** Asking for one change to an existing character ("wider legs")
   re-rolls everything else too — `GEM2-MC-2` silently changed his hair colour, his expression, his shirt and his
   shoes. For a *costume* change, edit the prompt and draw fresh rather than asking for a tweak.

**Still open:** which `CafeWalker` take to use, and whether the cast gets rebuilt in Meshy from this pass. The
three rigged models on `main` are still built from the **ComfyUI** pictures. Rebuilding all four is 140 Meshy
credits and the two-press rig flow again.

## How these get built

1. **Reference sheet** — `docs/prompts.md`, codes `MC-APOSE`, `BOSS1-APOSE`, `BOSS2-APOSE`, drawn by
   `tools/gen_images.py` on M Station's graphics card. Takes land in `Art/Refs/gen/` (git-ignored); the pick is
   copied to `Art/Refs/<name>_apose.png` and committed, so the picture a model came from sits beside the model.
2. **3D model — Meshy, in a browser, by a person.** `CLAUDE.md` is explicit: *"retries go through the browser,
   never the API"*, because every API call costs credits while the website's retries are free. So an agent does not
   make these. Steps are in the hand-off below.
3. **Rig, animation and export** — `Art/Blender/meshy_character.py`, which takes Meshy's rigged GLB and writes
   `SK_<Name>.fbx` plus its base-colour texture into `Art/Blender/export/Characters/<Name>/`, with a Walk and an
   Idle already on it.
4. **Import** — on GameStation only. `CLAUDE.md` line 53: a maker computer never saves in Unreal, it hands the
   files over.

## Hand-off

**Done - 2026-11-12, by Claude in a real browser on M Station.** All four were made on meshy.ai (the website, so
the free retries still apply), the three people were rigged with **Smart Rig**, and everything was downloaded.
Settings: High Detail (Meshy 7.1), Texture on, Ultra 2K, texture 2K, License Private, Pose -> A-Pose on for the
people and off for the prop. 35 credits each; the remesh and the rig were free.

| Reference | Meshy named it | Result |
|---|---|---|
| `Art/Refs/CafeWalker_apose.png` | `Meshy_AI_The_Weary_Apron` | Smart Rig, 69 bones -> `SK_CafeWalker.fbx` |
| `Art/Refs/CrashDriver_apose.png` | `Meshy_AI_Frostbound_Rider` | Smart Rig, 45 bones -> `SK_CrashDriver.fbx` |
| `Art/Refs/CleaverBoss_apose.png` | `Meshy_AI_The_Obsidian_Enforcer` | Smart Rig, 83 bones -> `SK_CleaverBoss.fbx` |
| `Art/Refs/Cleaver_prop.png` | `Meshy_AI_Steel_Butcher_Cleaver` | no rig, it is a prop -> `SM_Cleaver.fbx` |

### Two more CleaverBoss models — 2026-11-12 evening

The CleaverBoss reference art that had never been through Meshy got made into models, so the boss can be picked
from three rather than accepted as one. **No existing asset was replaced** — `SK_CleaverBoss.fbx` on `main` is
untouched; these are additional names.

| Name | Reference it came from | Meshy named it | Result |
|---|---|---|---|
| `CleaverBossGemRef` | `Art/Refs/CleaverBoss_apose_gemref.jpg` (Gemini, drawn with our earlier picture attached) | `Meshy_AI_The_Iron_Broker` | Smart Rig, **69 bones** -> `SK_CleaverBossGemRef.fbx` |
| `CleaverBossGemText` | `Art/Refs/CleaverBoss_apose_gemtext.png` (Gemini, text-only chat, nothing uploaded) | `Meshy_AI_The_Stern_Negotiator` | Smart Rig, **31 bones** -> `SK_CleaverBossGemText.fbx` |

Both are 178 cm, ~30,000 triangles, Walk + Idle, bake fit 0.09 cm. 70 credits; the remeshes and rigs were free.

    blender -b --factory-startup --python Art/Blender/meshy_character.py -- <rigged.glb> CleaverBossGemRef smart 178
    blender -b --factory-startup --python Art/Blender/meshy_character.py -- <rigged.glb> CleaverBossGemText smart 178

**Not made, and why.** Four other CleaverBoss pictures exist and were deliberately left alone:
`BOSS2-APOSE-1/2/3` hold the cleaver **across the trouser leg**, which image-to-3D fuses into the mesh — that is
the defect the `BOSS2-NOBLADE` prompt was written to avoid. `BOSS2-NOBLADE-1` is sound but is in the ComfyUI
rendering the team has since decided against (`ROADMAP.md` → Decisions: cel-shaded anime). Say the word and either
becomes a model for 35 credits.

**The one that nearly shipped broken.** `CleaverBossGemText` was rigged *without* a remesh the first time, because
Meshy let its 300,892 faces past the 300K gate. The rig came back with no identifiable legs and the walk drove the
legs as if they were arms — see `CLAUDE.md`'s Meshy section. Remesh first, every time.

**If you redo one, rigging is two presses.** The first **Rig** press is only a remesh (Image to 3D returns
600-950k triangles and rigging refuses over 300k); press Rig again on the remeshed asset for the real rig dialog,
and use 30K + Quad. Download the **animate-phase** asset, `..._character.glb` - the remeshed one has **no
skeleton** in either glb or fbx. Both traps are written up in `CLAUDE.md`'s Meshy section.

**Then, on M Station (done 2026-11-12):** the three people,

    blender -b --factory-startup --python Art/Blender/meshy_character.py -- <rigged.glb> CafeWalker smart 175
    blender -b --factory-startup --python Art/Blender/meshy_character.py -- <rigged.glb> CrashDriver smart 180
    blender -b --factory-startup --python Art/Blender/meshy_character.py -- <rigged.glb> CleaverBoss smart 178

and the cleaver, which uses the prop script instead (0.35 m across its widest side, 2,000 triangles):

    blender -b --factory-startup --python Art/Blender/meshy_prop_bake.py -- <cleaver.glb> Cleaver 0.35 width 2000

Note the two scripts write to **different places**: `meshy_character.py` to
`Art/Blender/export/Characters/<Name>/`, `meshy_prop_bake.py` to `Art/Meshy/<Name>/`.

**Then, on GameStation (builder only):** copy each `Art/Blender/export/Characters/<Name>/` folder (and
`Art/Meshy/Cleaver/` for the blade) into
`JumpCut/Content/Game/Imported/` with Unreal open and let Interchange auto-import it — mesh, skeleton and both
animations together. Do **not** use `SkeletalMeshTools.import_file` onto an existing skeleton; `CLAUDE.md` records
that going wrong twice. Then point the material slot at the character's `MI_`, place it next to a plain copy, and
look at it **from the game camera** before calling it good.
