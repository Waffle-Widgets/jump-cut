# Characters

The three we are building first, decided Nov 12 (see `ROADMAP.md`, Decisions): the **main character**, the
**crash driver** who gives Freeze Frame, and the **mob boss** who gives Splice. The story they sit in is in
[`PITCH.md`](PITCH.md).

A fourth entry, the **stunt double** who would give Stunt Double, is below as a **proposal**. He is boss 3, which
`ROADMAP.md` makes conditional ("only if there is time") and keeps at number 2 on the cut list, and no person has
agreed to his design yet — see [The third boss](#the-third-boss--stuntdouble-proposed).

The names below are **working asset names**, not the characters' names in the story. Nobody has named them yet;
that is an open question in `ROADMAP.md`, and an agent does not get to settle it.

## The look, and why

Cel-shaded anime: hard-edged shadows, clean dark outlines, flat colour. That is not a fresh choice — it is the only
style this team has a tested path for, from the cel-shader demo (first made on `mendezm87/anime-look`, now merged
into `Gamestation/first-build`, not yet on `main`) and the `CafeWalker` model made from a drawing. It is decided:
`ROADMAP.md`, Decisions, Nov 12.

**Each power owns a colour, and nobody else may use it.** The player has to learn what a colour means in three
minutes, so a colour that appears twice is worse than a dull character.

| | Colour | Used by |
|---|---|---|
| Freeze Frame | pale cyan, almost white, like frost | the crash driver, and the player's Freeze Frame effect |
| Splice | magenta into violet | the mob boss, his portals, his blade's edge |
| Stunt Double | safety orange `#E8601D` — **proposed**, see the third boss below | the stunt double, and the player's decoy. Hue 20°, so it collides with neither cyan (192°) nor magenta (331°) |
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
- **Already exists:** `Art/Refs/cafe_walker_ref.jpg` and `Art/Refs/CafeWalker_tripo_apose.glb`, first on
  `mendezm87/anime-look` and now merged into `Gamestation/first-build` (not yet on `main`), made with Tripo on the
  jam's first night. That model is the starting point, not a
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

## The third boss — `StuntDouble` (power SETTLED, look still PROPOSED)

> **His power is settled** by the Team Owner on Fri Nov 13, 2026, 12:30 AM Pacific, and built — see
> *What his power does* below and *His power is built* further down. **Everything about how he looks is still a
> proposal**, written by Claude on GameStation on Thu Nov 12, 2026, 11:15 PM Pacific.
> Nobody on the team has agreed to the look. `ROADMAP.md` says an agent may propose but never writes its own suggestion
> into Decisions, so the proposal line for it belongs in that file's **Waiting for a yes** section and nothing here
> is settled — not the look, not the colour, not the name. The reason it is written at all is that boss 3 had no
> design and no artwork of any kind, so if Friday goes well there was nothing to start from. Now there is, and
> reading it costs a minute instead of an evening.

He is the man who has taken every hit in this film so far, and the only one of the four nobody has ever seen. He
gives **Stunt Double** (`PITCH.md`, power 3: *a copy fights beside you and takes one hit*), and he is countered by
**Freeze Frame** — the Team Owner's call on Fri Nov 13, 12:30 AM Pacific. That is power 1, not the power from the
boss before him, so beat 5 is the one rung where the "beat each boss with the power you took from the one before"
ladder is broken on purpose. It is broken in the useful direction: Splice is still unbuilt, and this fight does
not need it.

- **What his power does, mechanically** (settled by the Team Owner, Fri Nov 13, 12:30 AM Pacific). He spawns
  three doubles **of himself**, and while any of them is still standing, every hit aimed at him lands on one of
  them instead — the double throws itself into the path of the blow, which is literally a stunt double's job.
  So he cannot be damaged at all while he has stand-ins. **Freeze Frame is the counter**: with time stopped
  nobody can dive, so the punch reaches the man it was aimed at. He can also **tag in** a double that actually
  fights you, the way a film swaps the star out for the dangerous shot. The doubles do **not** wear the player's
  face — that idea is dropped; they are copies of him.
- **Why that is the Stunt Double power and not a generic clone fight.** A stunt double's whole job is that the
  damage happens to the wrong person on purpose. The boss is not copying himself for company; he is doing to the
  player what has been done to him for twenty years, and the doubles wear *your* face because a double is always
  cast to look like the star.
- **Personality: he is the only boss who is not angry.** Cheerful, professional, completely unbothered — he has
  been set on fire two hundred times and it is a Tuesday. He treats the fight as a shoot: he hits his marks, he
  takes it again from the top, he is pleasant about it. That is more unsettling than another snarl, and it is free
  — it lives in his face and his posture and costs no extra geometry.

### Silhouette and design

- **Silhouette:** the only **segmented** figure in the game. Flat pads sit flush over his shoulders, elbows, hips,
  knees and shins, and between them he has the narrowest waist and chest in the cast, so at 64 px he reads as a
  jointed action figure — bright blocks joined by thin links. He is also the only **bright** body: value 0.91
  against a cast that is cream-and-green, dark brown and charcoal. The other three read pale, dark and dark. He
  reads hot. No helmet and no hat — the crash driver owns the lopsided-head read, so this one gets the smallest
  head shape in the game, a buzz cut, with a flat stand-up collar that takes his neck away.
- **Design:** slim, athletic, mid-thirties, upright and easy. Very short dark buzz-cut hair. A cheerful relaxed
  face with laugh lines, clean-shaven, one short pale scar on the chin. A bright **safety-orange one-piece
  coverall** zipped to a flat stand-up collar. **Dark navy pads sewn flat** over shoulders, elbows, hips, knees and
  shins. Two flat pale-grey hi-vis bands around each upper arm and one across the chest. Flat dark navy
  **wire-work harness webbing** across the chest and over both shoulders, lying flush, with a plain flat
  rectangular plate at the sternum and **nothing hanging off it**. Flat navy belt, navy boots, bare hands.
- **Height: 176 cm, and that is a design beat, not a coincidence.** The main character is 175 cm. The stunt double
  was *cast* to double for the star, so he is built to match him — which is also why the doubles he makes are
  believable. Their skin tones land dE 11.9 apart, and for once that closeness is the point.
- **Triangle budget:** 30,000, the same as the other three.

### Palette, with the numbers

The standing rule from the Team Owner is no skin-coloured hair or clothing and no hair- or clothing-coloured skin,
and `tools/color_audit.py` flags anything within **dE76 14** of the face skin. This palette was checked against
that threshold before it was written down, not after:

| Part | Hex | Hue / sat / val | dE76 from his face skin |
|---|---|---|---|
| face and hands (skin) | `#F0C49A` | 29° / 0.36 / 0.94 | — |
| hair | `#241A15` | 20° / 0.42 / 0.14 | **75.1** |
| coverall | `#E8601D` | 20° / 0.88 / 0.91 | **57.1** |
| pads, harness, belt, boots | `#232A38` | 220° / 0.37 / 0.22 | **75.3** |
| hi-vis bands | `#C9CFD6` | 212° / 0.06 / 0.84 | **33.0** |

**His worst skin separation is 33.0.** `CafeWalker`'s cream shirt against his face is **14.4** and that is the one
real finding in the colour audit below, so this palette has more than twice the clearance on the cast's known
failure. The closest pair anywhere on him is hair against the navy pads at **17.0**, which still clears the
threshold, and the pale bands sit 66.2 from the navy and 85.4 from the orange, so the hi-vis reads as hi-vis rather
than as a wash.

**The orange does not collide with anything already in the game.** It is dE **98.4** from Freeze Frame's pale cyan
and **74.0** from the measured magenta of the mob boss's shirt (`#611339`), with hues 172° and 48° away
respectively. The nearest thing to it on the existing cast is the crash driver's leather, and that was *measured*
rather than guessed: sampling `Art/Blender/export/Characters/CrashDriver/T_CrashDriver_BaseColor.png` directly, its
two biggest non-background clusters are `#584848` and `#483838` — very dark, nearly desaturated browns at value
0.28–0.35 — which are dE **76.1** and **78.4** from this orange. Nothing on the cast is within 57 of it.

**Why orange, beyond the numbers.** Crash mats, fire-gag coveralls and hi-vis are what stunt work actually looks
like, so the colour does a second job: it says *this man expects to be hit* before he opens his mouth. It is also
the one warm saturated hue the two reserved power colours leave free.

### Meshy and TRELLIS safety notes

Every item here is a failure this repo has already paid for once.

- **He is empty-handed, and he does not get a prop at all.** The mob boss needed the two-prompt split
  (`BOSS2-NOBLADE` for the body, `CLEAVER-PROP` for the blade) because a drawn blade crossing his leg fused into
  the trousers. The right answer for *this* boss is simpler: his weapon is the doubles, so there is no prop to
  split out, no hand socket to solve and no second 3D asset to make. That matters for a boss who is number 2 on the
  cut list — he is the cheapest of the four to build. **If the team later wants him holding something**, follow the
  mob boss's pattern exactly (a `NOBLADE`-style body prompt plus a standalone prop prompt, attached to a hand
  socket in Unreal) and pick a **thick single-slab object**. Do not pick the obvious stunt prop, a breakaway chair:
  four thin spindly legs is precisely the geometry image-to-3D either fuses into a block or shatters, and the
  cleaver only survived because it is one flat slab.
- **Nothing protrudes past his outline.** The pads are flat panels sewn flush, the harness is flat webbing lying
  against the coverall, and the buckle is a flat plate. No rope, cable, hook, carabiner, D-ring, loose strap end,
  cape, scarf or hat. This is the crash driver's lesson: his shoulder ice came back as spikes crossing the
  silhouette in the first text-only Gemini take and had to be redrawn as flat plates lying on the jacket.
- **The pads are a new risk, so the prompt names it.** A pad drawn as a separate shape floating above the sleeve
  with a gap under it comes back from image-to-3D as a loose shell or a detached shard. The prompt asks for them as
  flat panels **level with the surface, flush, no gap underneath, no bulging foam**.
- **His A-pose is deliberately wider than the other three: arms about 55° from the body, not 45°.** The reason is
  measured. On `SK_CrashDriverTrellis`, `Art/Blender/trellis_character.py`'s automatic weighting mis-assigned a
  shoulder accessory — `clavicle_r` top-owns 2,234 of 14,140 verts (16%) against `upperarm_r`'s 348 — so a 50°
  shoulder swing flattens the sleeve into a plate. **This character's shoulder pads are exactly that kind of
  accessory**, so the fix that finding asked for — a wider A-pose in the reference sheet — is built into his prompt
  from the start. Legs well apart too, with a visible gap at thigh, knee and ankle: `GEM2-MC` take 1 was rejected
  for an inner-thigh fusion risk.
- **If he goes through Meshy: remesh first, every time.** Two presses — the first **Rig** press only remeshes
  (image-to-3D returns 600–950k triangles and rigging refuses over 300k), then press **Rig** again on the remeshed
  asset for the real dialog, 30K + Quad. Download the **animate-phase** asset, `..._character.glb`. Both traps are
  written up in `CLAUDE.md`'s Meshy section, and `CleaverBossGemText` nearly shipped broken for skipping the first.
- **If he goes through TRELLIS instead he is free.** `SK_CrashDriverTrellis` was generated locally on GameStation's
  RTX 5090 in 41.8 s for 0 credits from a committed reference sheet. That is the cheap path for a cut-list boss,
  with the shoulder-weighting caveat above as the thing to check on the result.

### Two rules constraints, both deliberate

- **No printed markings anywhere on him.** `docs/RULES.md` allows no trademarks or logos, and real stunt coveralls
  carry production names, crew numbers and union patches. His coverall is blank: no letters, no numbers, no badge,
  no logo. That doubles as an image-generation safeguard, because baked-in text becomes surface detail on the mesh.
- **13+.** He is the character most likely to drift gory, because his job is injury. So: no blood, no burns, no
  soot, no scorch marks, no bandages and no visible wounds, on the model or in the concept art. The one scar on his
  chin is a thin clean line. He is cheerful and unhurt, which is the whole joke.

### Built in Unreal: `BP_StuntDouble` (placeholder body, Thu Nov 12, 2026, 11:54 PM Pacific)

The fight shell exists now, so beat 5 is playable before any art lands. `BP_StuntDouble` is a child of
`BP_EnemyBase`, in `Content/Game/Blueprints/`. **Nothing in the design above is approved by this** — the Team
Owner approved the six-beat demo, which is what makes boss 3 a required fight; the colour and the silhouette are
still proposals. His power is no longer a proposal - it was settled and built on Fri Nov 13, 12:30 AM Pacific.

- **Body is Epic's mannequin**, `SKM_Manny_Simple` with `ABP_Unarmed`, inherited from `BP_EnemyBase`. The mesh is
  scaled **1.15** so he does not read as another goon in the playtest. Both go away at the model swap.
- **Animations are the shared human montages** — `AM_Human_Punch_02` to attack, `AM_Human_HitReact`,
  `AM_Human_Death`. All three sit on `DefaultSlot`, which `ABP_Unarmed` wires through to Output Pose, so they play.
- **Tuned between a goon and the mob boss:** 300 health, move 460, damage 14, windup 0.40 s, cooldown 1.0 s,
  attack range 150, reach 190, knockback 320. Faster and lighter than the cleaver boss (240 hp but 0.70 s windup),
  which is the read we want for a stuntman. `EnemyStartsAwake` is false, like every other enemy.
### His power is built: the stand-ins (Fri Nov 13, 2026, 12:45 AM Pacific)

The three docs used to describe three different fights. The Team Owner picked one, and it is the one above. What
that cost, in code:

- **`BP_StuntStandIn`** — a new `BP_EnemyBase` child, the double itself. Same mannequin and same human montages as
  the boss, mesh scaled **1.15** to match him, 45 health, and a `StandInFights` flag. With the flag off it does
  not chase or punch: it stands and faces the player, waiting to be hit. With it on it fights exactly like a goon.
- **The redirect lives in `BP_EnemyBase.EnemyTakeHit`**, not in the boss, because it needed to sit in front of the
  damage for *any* enemy that has stand-ins. Every enemy now carries an `EnemyStandIns` array; it is empty for
  goons and for the cleaver boss, so their damage path is untouched. When it is not empty and the enemy is not
  time-stopped, `EnemyPickStandIn` picks a living stand-in, teleports it onto the line between the boss and the
  attacker, turns it to face the blow, and forwards the whole hit — damage, knockback, stun — to it.
- **Freeze Frame falls out of that for free.** Freeze Frame already sets `EnemyTimeStopped` on every enemy
  (`BP_Player.PlayerStopAllEnemies`). The redirect is skipped whenever the boss is time-stopped, so during Freeze
  Frame the doubles are pinned mid-dive and the hit goes through to him. No new flag, no coupling to the player.
- **The boss drives it from `EnemyThink`**: `BossCallStandIns` calls in a fresh crew of three in a 42° fan toward
  the player whenever the last crew is gone (14 s cooldown, first wave 2.5 s after he wakes), and `BossCallFighter`
  tags in one fighting double from behind him every 16 s, at most one alive at a time.

**Verified in Play-In-Editor on GameStation, by reading live actor state — no person has played it.** Three
stand-ins spawn in the fan; a 10-damage hit on the boss left him at 300/300 and took one stand-in from 45 to 35,
and moved that stand-in onto the attack line; with Freeze Frame on, the same hit took the boss 300 → 290 and left
every stand-in untouched; the tag-in double spawned with `StandInFights` true and awake. A plain goon still took
10 damage from the same call, so the shared base class is not broken.

### What a person has to decide before anyone draws him

1. **Whether boss 3 is in the game at all.** He is number 2 on the cut list, and `ROADMAP.md` makes Saturday's
   "Stunt Double only if Friday went well" the gate. Nothing here changes that.
2. **Safety orange as the Stunt Double colour.** The numbers are above; the choice is not an agent's.
3. ~~**Whether the doubles wear the player's face.**~~ **Settled Fri Nov 13, 12:30 AM Pacific: they do not.** The
   doubles are copies of the boss. Nothing has to be drawn twice, and his model is the only one beat 5 needs.

### How to draw him, with nothing else to work out

The prompt is written and self-contained. Gemini, text only: **`GEM2-BOSS3`** in
[`prompts-gemini.md`](prompts-gemini.md), `Create image` on, model **4 Hydrogen**, aspect ratio **3:4**, and
download with *"Download full size image"*. Local ComfyUI, for whichever machine has it: **`BOSS3-APOSE`** in
[`prompts.md`](prompts.md), `python tools/gen_images.py BOSS3-APOSE --takes 3 --size 1024x1536`. Takes land in the
ignored `Art/Refs/gen/` folders; the pick is copied to `Art/Refs/StuntDouble_apose.png` and committed, so the
picture a model came from sits beside the model.

**Judge a take on four things, in this order:** is there white background visible between each arm and the torso and
between the thighs; do the pads lie flat against the coverall with no gap or bulge under them; is the coverall one
flat orange with two or three shadow shapes rather than a textured, scuffed, sooty garment; and are his hands empty
with the fingers separated. Everything else is a costume detail a redraw can fix — those four decide whether the
mesh survives.

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

### Imported — Thu Nov 12, evening (GameStation)

Done, by Claude driving the Unreal MCP on GameStation with the editor open. The main character was already in
(`SK_CafeWalker_Walk`, with the mannequin retarget); these are the three that were missing.

| FBX | Unreal asset | Height in Unreal | Material |
|---|---|---|---|
| `SK_CrashDriver.fbx` | `/Game/Game/Imported/CrashDriver/SK/SK_CrashDriver` + `_Skeleton`, `_PhysicsAsset`, `SK_CrashDriverArmature_Walk`, `SK_CrashDriverArmature_Idle` | **180.0 cm**, feet on the origin | `MI_CrashDriver` |
| `SK_CleaverBoss.fbx` | `/Game/Game/Imported/CleaverBoss/SK/SK_CleaverBoss` + `_Skeleton`, `_PhysicsAsset`, `SK_CleaverBossArmature_Walk`, `SK_CleaverBossArmature_Idle` | **178.0 cm**, 142 cm arm span (vs the driver's 126) | `MI_CleaverBoss` |
| `SM_Cleaver.fbx` | `/Game/Game/Imported/Cleaver/SM_Cleaver` | 35.0 × 11.3 × **0.85 cm**, 954 triangles, Nanite off | `MI_Cleaver` |

Each `MI_` is a new instance of **`M_AnimeChar`** with its one parameter, `Tex`, pointed at the character's own
base-colour texture — the same shape as `MI_CafeWalker`. The FBX was dropped into its own folder under
`Content/Game/Imported/` and Interchange auto-imported mesh, skeleton, **both** animations and the texture
together; no import window ever opened and `SkeletalMeshTools.import_file` was not used.

**Two things to know before anyone trusts this.**

1. **Nothing has been seen from the game camera, or in the level at all.** The models are assets; they are not
   placed, not on a Blueprint, and not playable. Which boss is the plaza boss is still an open question in
   `ROADMAP.md`, and only a person decides that — so no Blueprint was re-pointed.
2. **The asset thumbnails are cached from import time and show Interchange's own material, not `MI_`.** Captured
   twice, before and after the material was assigned, and the two files were byte-identical. The assignment was
   checked with `get_material` instead, which returns the `MI_`. The sheet below is therefore a picture of the
   geometry and the baked texture, not of the cel-shader.

![The crash driver, the mob boss and the cleaver as Unreal assets](media/MODELS-IN-UNREAL.png)

The cleaver's **0.85 cm** depth is worth a note: it is nearly flat, which is what image-to-3D does with a
side-on reference drawing. The blade is right; the handle is thinner than a real grip. From the game camera, in
a hand, that will not show — seen edge-on it will.


## Colour audit — Thu Nov 12 evening

Run `python tools/color_audit.py`. It renders each finished model's **baked base colour unlit** (front and back),
takes the skin tone from the middle of the face, and paints every pixel within dE76 14 of it — green where skin
belongs, **red anywhere else**. Sheet: [`../docs/media/COLOUR-AUDIT.jpg`](media/COLOUR-AUDIT.jpg).

Unlit matters: the contact sheets in `meshy_character.py` are lit and 300 px, so they show you the light rig, not
the texture. The **back** matters just as much: every reference sheet we drew shows the front only, so the back of
every model is invented by image-to-3D and is where a colour is most likely to go wrong.

### What it measured

| Model | Hair | Skin | Main garment | Legs | Feet | Skin colour outside head/hands |
|---|---|---|---|---|---|---|
| `CafeWalker` | `#0C0D0D` black | `#FDD9BF` | apron `#445345` green, shirt `#F7F2E0` cream | `#353635` charcoal | `#9D978A` grey | **6.13% front / 3.94% back** |
| `CrashDriver` | helmet `#A1AAB0` | `#D6A993` | jacket brown, frost pale cyan on one shoulder | `#383838` | `#423F3C` | 0.00% / 0.00% |
| `CleaverBoss` | `#8D8C8C` grey | `#E3B5A4` | suit `#313135` charcoal, shirt `#611339` magenta | `#303136` | `#232326` | 0.18% / 0.00% |
| `CleaverBossGemRef` | `#C5C7C7` grey | `#FCD9C8` | suit `#5C6167` mid grey, shirt `#AC3B75` magenta | `#5C6167` | `#2D3034` | 0.14% / 0.00% |
| `CleaverBossGemText` | `#CECECA` grey | `#FDDFCB` | suit `#41444A`, shirt `#8E345E` magenta | `#41444A` | `#1E2125` | 0.28% / 0.00% |
| `SM_Cleaver` | — | — | blade `#9CA5AC` steel (86%), handle `#3C201D` wood (14%) | — | — | — |

**No model has skin-coloured hair, and no model has skin where skin should not be.** The thing we were checking
for is absent on all six. Every hair sample is far from its own skin tone (`CafeWalker` dE 87.7, `CleaverBoss`
dE 27.8), and the crash driver scores a literal 0.00% — the only skin on him is his face.

**All three mob bosses' shirts are magenta**, hue 329°–333°, inside the 290°–335° the palette rule wants, so
Splice's colour is safe. Measure a garment from its *saturated* pixels, not from a shaded fold: the first pass
sampled `CleaverBoss`'s collar in shadow and read 345° (crimson), which would have been a false alarm.

### The one real finding: `CafeWalker`'s shirt and his face are the same colour

His cream shirt `#F7F2E0` sits **dE 14.4** from his face skin `#FDD9BF` — close enough that it fills 6% of his
front with "skin" in the map. Two things make this less alarming and one makes it worse:

- Up close it is fine. The boundary that actually touches is **rolled sleeve against bare forearm**, and that is
  dE **26.5** — clearly two colours. The cel-shader's dark outline separates them further.
- At game-camera size it is not fine. Rendered at 64 px tall, his head, shirt and hands merge into one pale mass
  and you cannot tell which way he is facing. The apron and trousers still read, which is what `Silhouette` above
  promises — but we lose the head.

**Darkening the shirt makes it worse, which is the non-obvious part.** Measured: dropping it 22% to `#C0BDB4`
raises separation from the *face* to 19.9 but drops separation from the *forearm* to 15.3, because the shirt moves
down through the skin's own lightness. Options, with numbers:

| Change | shirt→face | shirt→forearm |
|---|---|---|
| keep `#F7F2E0` as-is | 14.4 | 26.5 |
| shirt darkened 22% `#C0BDB4` | 19.9 | **15.3 (worse)** |
| shirt darkened 45% `#8A8781` | 36.5 | 22.0 — but no longer "cream" |
| **skin deepened 10% `#E4BFA4`, shirt untouched** | **21.0** | 26.5 |

A grid search over every pale colour (value > 0.76, saturation < 0.18) found that the only ones clearly separated
from his skin are **blue, violet or lilac** — and the palette rule at the top of this file reserves pale cyan for
Freeze Frame and magenta/violet for Splice, neither of which he may wear. So the cast's own colour rules box this
in: **deepening his skin is the only move that separates him without stealing a power colour.** Nobody has decided
this; it is a design call, not a bug fix.

---

## CleaverBoss is the plaza boss (Thu Nov 12, evening, GameStation)

The Team Owner settled the open question "what is the plaza boss now" with one word: **mob boss**. The built boss
was kept and dressed as him rather than replaced, so nothing the playtest settled was thrown away.

| Part | What it is |
|---|---|
| mesh | `SK_CleaverBoss` on `BP_BossFreeze`'s Character mesh, scale **1.2921**, offset `z = -115`, yaw **270** |
| why that scale | the capsule is 115 cm half-height; the model is 178.0 cm, so 230/178 fills the capsule exactly - the same silhouette size the mannequin boss had at 1.3 |
| material | `MI_CleaverBoss` (our `M_AnimeChar` instance), one slot |
| animation | `BS_Idle_Walk_Run_CB`, played in **single-node** mode and driven each think by `BossDriveAnim` |
| cleaver | `SM_Cleaver` as a component, attached in the Construction Script to socket **`cleaver_r`** on bone `Bone_019` |

**The skeleton has no names.** Meshy's Smart Rig calls every bone `Bone_000`...`Bone_082`, so Unreal's automatic
IK-rig characterisation finds **nothing** - it returns no root and no chains. The retarget was done by naming the
chains by hand, read off the rig in Blender. Right is `-X` in that file and left is `+X`, which is how the sides
were told apart; the toes point `-Y`, which is what fixes the handedness:

| Chain | Bones | | Chain | Bones |
|---|---|---|---|---|
| retarget root | `Bone_001` (pelvis) | | `RightArm` | `Bone_022` -> `Bone_019` |
| `Spine` | `Bone_005` -> `Bone_002` | | `LeftClavicle` | `Bone_028` |
| `Neck` | `Bone_018` | | `LeftArm` | `Bone_027` -> `Bone_024` |
| `Head` | `Bone_017` | | `RightLeg` | `Bone_010` -> `Bone_006` |
| `RightClavicle` | `Bone_023` | | `LeftLeg` | `Bone_015` -> `Bone_011` |

The right hand is `Bone_019` - the wrist with **five** finger chains hanging off it, on the `-X` side. That is
where the socket went. Its transform was solved, not eyeballed: the cleaver's handle sits at mesh-local
`(15, 0, 7.6)` (the `+X` end is the wooden grip, 4.5 cm tall; the `-X` end is the full-height blade), so the
socket is `(-16.437, -1.978, 2.945)` with rotation `(-31.84, -10.18, 39.68)` - the transform that puts that grip
point in the fist with the blade pointing forward and down.

**The same chain map works for any Meshy character we make**, because `Art/Blender/meshy_character.py` numbers
bones the same way every time. `CafeWalker` and `CrashDriver` are not wired into Blueprints yet.
