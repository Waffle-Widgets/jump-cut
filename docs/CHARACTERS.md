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
| the goons — **no colour at all** | graphite, medium grey, black, one oxblood band | `StreetGoon`, the crew the player fights for most of the demo. Achromatic on purpose, so every colour on screen belongs to a power. Nothing white or pale: see the goons below for why |

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

## The coworker — `CafeCoworker` (beat 1; modelled and rigged Nov 13, not yet imported into Unreal)

The person the player saves in the demo's first beat. She exists because the beat's *lesson* needs a subject:
the roadmap's beat 1 ends with an explosion sending shrapnel at a coworker, and the action button teaching the
player to use Freeze Frame to save her. Until Fri Nov 13 she was not written down anywhere, which is how a beat
can be "designed" and have no character in it.

She is deliberately the plainest person in the cast after `CafeWalker` — she is on screen for about fifteen
seconds and her job is to be unmistakably *a colleague*, in the same cafe, in the same uniform family.

- **Silhouette:** short and compact, the same flat apron rectangle across the hips as `CafeWalker` so the two
  read as the same workplace from distance. Hair tied back in a short tail — the one piece that moves.
- **Design:** dark brown hair tied back; open friendly face, mid-twenties. White short-sleeve shirt, teal canvas
  apron, charcoal trousers, flat brown shoes. No bag, no tray, no prop — see the rules note below.
- **Height:** 162 cm. **Triangle budget:** 30,000.
- **Palette, with the numbers** — picked against the one colour failure this project has already had
  (`CafeWalker`'s cream shirt sits dE76 **14.4** from his own face, see the colour audit below):

  | Part | Hex | Why |
  |---|---|---|
  | Skin | `#C98C64` | warm mid-brown; different family from every garment |
  | Hair | `#3A2A22` | near-black brown, dE76 ~37 from the skin — not a skin-coloured hair |
  | Shirt | `#FFFFFF` | pure white, the largest possible separation from skin |
  | Apron | `#14626B` | deep teal; reads as the same uniform as `CafeWalker`'s dark green without copying it |
  | Trousers | `#2E3338` | charcoal, matching the cast |
  | Shoes | `#5A4231` | flat brown |

  **Run the colour check before anyone models her**, the same one that caught `CafeWalker`: no garment within
  dE76 20 of the skin, and no hair within dE76 20 of either.
- **Rules constraint, deliberate:** no prop and nothing that leaves her silhouette. Image-to-3D fuses a thin
  protruding shape into a blob or drops it as a floating shard — the lesson from the `CrashDriver` ice crystals
  — so she is empty-handed and her apron ties are flat against her.
- **Prompt:** `GEM2-COWORKER` in [`prompts-gemini.md`](prompts-gemini.md), and `COWORKER-APOSE` in
  [`prompts.md`](prompts.md). **Both have now been run.** Her reference sheet is
  `Art/Refs/CafeCoworker_apose.png` and her model is `Art/Blender/export/Characters/CafeCoworker/` — see
  "The coworker's model" under Hand-off.

### Built in Unreal: `BP_Coworker` + `BP_Shrapnel` (Fri Nov 13, 2026, 1:15 AM Pacific, GameStation)

The fight-shaped half of her exists and is verified; the body does not. She is a green box
(`/Engine/BasicShapes/Cube`, `M_CheckGreen`, 0.5 x 0.5 x 1.8, chest at +90 cm) so that beat 1 is playable now
and model-swappable on Saturday, exactly as `BP_StuntDouble` was.

- **`BP_Coworker`** owns the whole beat. `TriggerSphere` 650 cm arms it, but `CoworkerStartStep` only fires once
  `BP_Player.HasFreezeFrame` is true — so **picking up the power is what starts the danger**, and the player can
  never meet the shrapnel without the means to stop it. It spawns the shrapnel, watches its distance to her own
  chest, and shows `RescuePrompt` (a cyan `M_WarnFreeze` sphere at +260 cm) exactly when a rescue would succeed.
- **`BP_Shrapnel`** flies to a fixed world point at `ShrapnelSpeed` 260 cm/s and destroys itself on arrival or
  after 14 s. Every tick it reads `BP_Player.FreezeFrameActive`; while that is true it does not move, does not
  turn, and **does not age** — a player who stops time is not punished for thinking.
- **The rescue is gated on the power, not on speed.** `RescueRequiresFreeze` is true, so the prompt stays dark
  and **F** does nothing unless time is stopped. It is instance-editable: a playtest that finds it heavy-handed
  can switch it off without touching a graph.
- **Failing it loops.** Shrapnel reaching her tips the mesh 80°, counts `RescueTriesUsed`, and 2.5 s later she
  stands up, returns to her spot and a fresh piece leaves the car. Beat 1 cannot strand anybody.
- **The action button is new.** `BP_Player` had no interact key at all. `PlayerTickInput` now polls **F** and
  **Gamepad_FaceButton_Top** with the same edge detection as punch/rewind/freeze, and `PlayerInteract` offers the
  rescue to every `BP_Coworker` in the level after a `PlayerCanAct` check.
- **Placed as** `Coworker_Cafe` in `Lvl_JumpCut` at (300, -250, 0), yaw 180, with `ShrapnelSpawnLocation`
  (-470, 0, 185) — the crashed car's cab — and `CoworkerSafeOffset` (0, 320, 0).
- **Verified in Play-In-Editor** by reading live actor state, not by eye: shrapnel spawns at the car and travels;
  with the freeze on it sits at exactly (-470, 0, 185) with its life timer untouched; the rescue moves her
  (300, -250) → (300, 70) and the shrapnel then finishes its flight into empty space. **Nobody has pressed F**
  — the key binding itself is unplayed.
- **Changed Fri Nov 13, 2:35 AM Pacific** to match the Team Owner's written scene. Failing is no longer a 2.5 s
  retry loop: `CoworkerDead` latches, the prompt stays dark, and the level carries on without her. The explosion
  is now a timed step she owns (`ExplosionDelay` 1.2 s after the power lands), and `AutoFreezeOnExplosion` stops
  time *for* the player when it goes off, so the quick time event starts on its own.
- **A trap worth writing down:** her placed actor `Coworker_Cafe` was carrying `AutoFreezeOnExplosion = false` and
  `ExplosionDelay = 0` — zero-initialised instance overrides left behind because the actor was placed *before*
  those variables existed. The class defaults were right and the beat still did nothing. If a new variable on a
  Blueprint seems to be ignored, check the placed instance before you check the graph.

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

### Built in Unreal: `BP_CrashDriver` (Fri Nov 13, 2:35 AM Pacific, GameStation)

The Team Owner's scene says the player *touches* the driver to get the power. That is now literally what happens,
and it is the first time one of our own generated characters is the thing a mechanic runs through.

- **`BP_CrashDriver`** is an `Actor` with a `SkeletalMeshComponent` on our own `SK_CrashDriver` wearing
  `MI_CrashDriver`, pitched −78° and lifted so he lies beside the car rather than standing in it. He has no
  AnimBlueprint and no death clip — he is a body on the floor, which is exactly the cheap version this file
  already recommends for him.
- **`DriverCanTouch`** is the whole gate: not already touched, the player does **not** already have Freeze Frame,
  and the player is inside `TouchRange` (220 cm, instance-editable). `DriverTickStep` lights a blue sphere
  (`M_PropBlue`) exactly when a touch would land, so the prompt never lies.
- **`DriverTryTouch`** calls `BP_Player.PlayerGrantFreezeFrame` and latches `DriverTouched`. It is reached from
  `BP_Player.PlayerInteract`, which now walks every `BP_CrashDriver` **and** every `BP_Coworker` behind the same
  `PlayerCanAct` check — so **F** is one button that means "the thing in front of me".
- **Placed as** `C1_Cafe_CrashDriver` in `Lvl_JumpCut` at (-380, 220, 0), yaw 140. The grey box `C1_Cafe_Driver`
  that used to stand there is deleted. `Marker_FreezeFrameGiven` and `Marker_FreezeFrameDoor` both had
  `MarkerGrantsFreezeFrame` turned **off**: the body is the only source of the power now.
- **Verified in Play-In-Editor through the real `PlayerInteract` path:** out of range the prompt stays dark and
  nothing is granted; in range it lights; one call grants `HasFreezeFrame` and latches `DriverTouched`; the
  explosion, the auto-freeze and the rescue all follow from it. The **F** key itself is still unpressed by a
  person.

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

## The goons — `StreetGoon` (beats 2 to 5)

The crew the player actually fights. Written on M Station on Fri Nov 13, 2026, because `BP_Goon` has existed
since the first build and **nobody had ever written down what a goon looks like** — they are Epic's mannequin in
four of the demo's six beats (street thugs in 2, the plaza in 3, the destroyed buildings in 4, and beside the
Stunt Double in 5), which is more screen time than any boss gets.

- **Silhouette:** the only **inverted triangle** in the cast. Heavy square shoulders, narrow waist, straight thin
  legs, and a small round buzzed head sitting clear of the shoulder line. The others are narrow-and-upright
  (`CafeWalker`), short-and-compact (`CafeCoworker`), lopsided-headed (`CrashDriver`), a broad rectangle with one
  bright edge (`CleaverBoss`) and segmented (`StuntDouble`) — a wedge was free.
- **The head is load-bearing.** `BP_GoonSpawner` puts three of them on screen 150 cm apart
  (`FIRST_BUILD_DESIGN.md`), and a dark head above dark shoulders turns a group into one blob at the game camera.
  His hair is buzzed almost to the scalp so the head reads as a skin-tone dot, which is what separates three
  figures into three.
- **Design:** a tall, heavily built young man with a hard flat expression. Dark graphite waistcoat buttoned flat
  over a medium grey long-sleeve shirt, a dark red necktie tucked flat underneath, a plain dark red cloth band
  around the left upper arm as the crew mark, graphite trousers, flat black boots. Bare hands, empty.
- **No jacket, deliberately.** An open suit jacket is what a mob foot soldier should wear, and its lapels are a
  loose shell standing off the chest — the exact shape image-to-3D returns as a floating sheet, the failure the
  `StuntDouble` write-up already warns about for floating pads. The buttoned waistcoat gives the same chest panel
  lying flush against the body.
- **Long sleeves, deliberately.** The coworker's rolled sleeves put her bare forearms outside the colour audit's
  head-and-hands whitelist, so she reads FLAG at 4.46% / 5.27% as a false positive. Cuffs at the wrist mean this
  one measures clean instead of needing the same explanation twice.
- **No weapon.** `BP_Goon` is defaults-only on `BP_EnemyBase` with no graph of its own, and it punches. A prop
  would need a socket, a second asset and a reason.
- **Height:** 180 cm — taller than the 175 cm hero so a group of three is intimidating, while `CleaverBoss` still
  outranks him on width (1.3x through the chest) rather than on height.
- **Triangle budget: 18,000, not 30,000.** Three on screen at once is 54,000 — nearly two heroes' worth for the
  cast's least important body. Meshy's remesh step stays at the documented fixed 30K quad; the budget is applied
  at FBX export by `meshy_character.py`'s `tris` argument.
- **One model, used three times.** Every goon is the same skeletal mesh, so variety — if anyone ever wants it —
  is a material swap, not a second character.

### Palette, with the numbers

| Part | Hex | dE76 from his skin |
|---|---|---|
| face and hands | `#C08E5E` | — |
| hair, buzzed | `#15131A` | **68.5** |
| waistcoat and trousers | `#23262E` | **62.5** |
| shirt | `#8A8F99` | **41.1** |
| necktie and arm band | `#6B2430` | **48.2** |
| boots and belt | `#141519` | **67.6** |

His **worst** skin separation is 41.1 against `color_audit.py`'s threshold of 14 — nearly three times the
clearance, and well clear of `CafeWalker`'s known failure at 14.4.

**He owns no colour, and that is the point.** Every colour on screen is supposed to mean a power, so the crew the
player fights for most of the demo is deliberately achromatic: graphite, grey and black. The one chroma on him is
the oxblood band, which measures dE76 **54.9** from Splice's magenta, **80.0** from Freeze Frame's cyan and
**62.3** from the proposed safety orange, so it dilutes nothing.

**Nothing on him is white or pale, and this is the finding worth keeping.** This file records the Freeze Frame
colour in words only — "pale cyan, almost white, like frost" — with no hex anywhere, so it was measured against a
representative pale cyan, `#DCF2F5`. Against that, **pure white is dE76 9.7 away and every off-white tested is
8.5 to 9.8** — all of them *under* the audit's threshold of 14. With three goons on screen in the beats that
teach Freeze Frame, a white shirt on the crew is the one colour collision in this cast that would actually cost
the player something, so the shirt is a medium grey at dE 35.4 from that cyan.

That number also applies to the coworker's pure white shirt, and **it is not a reason to re-make her**: she is one
small figure against a full-screen effect, her deep teal apron carries her read, and her 35 credits are spent.
It is written down here so the next white garment in this cast is a choice rather than an accident.

### How to draw him, with nothing else to work out

`GOON-APOSE` in [`prompts.md`](prompts.md) for the ComfyUI/Qwen path on either card, and `GEM2-GOON` in
[`prompts-gemini.md`](prompts-gemini.md) as the self-contained version.

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
| `CafeCoworker` | `Art/Refs/CafeCoworker_apose.png` (`COWORKER-APOSE` take 1) | The only take whose apron stops at mid-thigh, so the gap between the legs stays open - takes 2 and 3 hang it past the knee and close that gap, which is what image-to-3D fuses. Take 3 also came back framed in black bars, breaking the "no border, no panels" rule. Drawn on GameStation's 5090 with ComfyUI + Qwen-Image, 0 Meshy credits. |
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

### The coworker's model — 2026-11-13, by Claude in a real browser on M Station

She was the first item on the roadmap's M Station queue and the only character in the opening beat with no face.
Same settings as the four above: High Detail (Meshy 7.1), Texture on, Ultra 2K, texture 2K, License Private,
Pose -> A-Pose on. **35 credits; the remesh and the rig were free.**

| Reference | Meshy named it | Result |
|---|---|---|
| `Art/Refs/CafeCoworker_apose.png` | `Meshy_AI_Welcoming_Apron_Pose` | Smart Rig, **68 bones** -> `SK_CafeCoworker.fbx` |

    blender -b --factory-startup --python Art/Blender/meshy_character.py -- <rigged.glb> CafeCoworker smart 162 30000

**162.0 cm exactly**, 30,000 triangles (from 57,447), Walk + Idle, bake fit **0.072 cm**. The rig is clean on
every test the script makes: two leg chains, two arm chains, a four-bone spine, a three-bone head and **no tail**
— so `MESHYCHAR-BAD-RIG` did not fire. `color_audit.py` independently re-imported the exported **FBX** and counted
the same 68 bones, so the export round-trips, and the FBX carries `T_CafeCoworker_BaseColor` inside it.

**The remesh was done twice, and the first one was on the wrong asset.** One Image-to-3D run with Pose on leaves
**two** generated assets in the panel — an untextured one (191,949 verts) and the textured one (210,280 verts) —
and the workspace auto-selected the *untextured* one. Remeshing that gives a bare 28,857-face mesh that would have
rigged and downloaded with no colour at all. Check the viewer's vertex count, not the thumbnail, before pressing
Remesh. Both remeshes cost 0 credits, so the mistake was free; the one that matters is **28,762 faces, Quad**.

**Her colour audit reads FLAG and it is a false positive.** 4.46% front / 5.27% back of the body sits within
dE76 14 of her face tone `#DC8754` while being neither head nor hand — and the painted sheet
([`media/2026-11-13-coworker-colour-audit.jpg`](media/2026-11-13-coworker-colour-audit.jpg)) shows all of it is
her **bare forearms**. She wears a short-sleeve shirt, and the audit only whitelists the head plus a disc at each
hand, so the arm between elbow and wrist is counted as a defect. No garment is skin-coloured and no skin is
garment-coloured, which is the rule that actually matters. This is the same shape of false positive as
`CrashDriverTrellis`'s brown-leather highlights.

**Meshy has no rename.** The current meshy.ai workspace shows assets by date only and offers no rename control in
the grid, the Assets sidebar or a context menu, so an asset cannot be labelled on their side. The mapping tables in
this file are the label: find a model by its reference picture, not by Meshy's invented name.

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

### The goons' model — 2026-11-13, made locally on M Station with TRELLIS (no credits)

`StreetGoon` is the first character in this cast built **without Meshy**. The Team Owner's Nov 13 decision is
"Meshy where we can, TRELLIS as the backup", and Meshy was unreachable: the dedicated Chrome profile's meshy.ai
session had **lapsed to logged-out** (the workspace served "Log In / Sign Up Free" with no credits line), and a
password is not something an agent may ask for or type. TRELLIS.2 is installed on this machine at
`D:\AI\TRELLIS2` with its weights already cached, so the model was generated locally instead.

| Reference | Pipeline | Result |
|---|---|---|
| `Art/Refs/StreetGoon_apose.png` | TRELLIS.2-4B `1024_cascade`, `DEC=30000 TEX=2048` | 23 mannequin-named bones -> `SK_StreetGoon.fbx` |

    D:/AI/TRELLIS2/venv/Scripts/python.exe run_image_to_3d.py in/StreetGoon_rgba.png out/StreetGoon 1024_cascade
    blender -b --factory-startup --python Art/Blender/trellis_character.py -- out/StreetGoon.glb StreetGoon human 1.8 18000

**There is a second reason beyond the lapsed login, and for this character it is the stronger one.**
`trellis_character.py` names its bones the way Epic's mannequin does; Meshy's Smart Rig names them
`Bone_000...`, which is why the cleaver boss needed nine chains mapped by hand. The goon's three animations —
`AM_Human_Punch_02`, `AM_Human_HitReact`, `AM_Human_Death` — are **authored on the mannequin skeleton**, so a
mannequin-named rig is the one that should retarget them without hand-mapping. **That is reasoning from bone
names and is not yet demonstrated in Unreal**, exactly as the `CrashDriverTrellis` write-up says of the same
claim.

**What the run measured.** 1,024 px cascade: dual contouring gave 2,903,648 verts / 5,811,524 faces, simplified
to 237,711 / 477,743, then decimated at export to **17,999 triangles** against the 18,000 budget. The rig took
18.3 s and reports **23 bones, 0 unweighted vertices**, direct weights, UV extent 0.997 x 0.997, and a height of
exactly **1.800 m** with a half-chest of 0.404 m. Three specks totalling 229 vertices were removed. Peak VRAM on
the 3090 was about **8.6 GB of 24**, so it never came close to the card's limit.

**The defect, and it is on his back.** The reference sheet is a single front view, so TRELLIS invented the back —
and it put a **dusty mauve patch on his left shoulder blade** that is in no part of the design. It looked at
first like a collision with Splice's reserved magenta, so it was measured rather than argued: across 2,002,160
non-background texels, **zero** sit within dE76 25 of `#C0279B`, and the closest texel in the whole texture is
`#9B4B76` at dE **35.0**. It is not a power-colour collision. It is still invented colour on an achromatic
character, and it is the thing to fix or paint out if he is kept. The same single-view limitation gave the back of
his head a soft shape rather than the buzzed scalp the front view has, and widened the oxblood arm band well past
the flush band the prompt asked for.

**The colour audit passes him, and the bigger finding is the one the audit cannot see.** `color_audit.py`
returns **no flags** for him — 0.11% front / 0.01% back within dE76 14 of the sampled face tone, the cleanest
numbers of any character in the cast, and the long sleeves are why: there are no bare forearms to count, which is
the false positive `CafeCoworker` and `CrashDriverTrellis` both carry. Read that pass with one caveat, though —
the audit sampled his skin reference as `#56523E`, value 0.34, because TRELLIS bakes the reference sheet's cel
shading into the base colour, so it compared garments against a shadow tone rather than lit skin.

Measuring the baked texture directly says what that costs, and it lands on **exactly the one read this design
depends on**. On the sheet, skin `#C08E5E` sits **47.6 L points** above the graphite `#23262E`, which is what
makes the head a bright dot above dark shoulders so three goons 150 cm apart read as three figures. In the baked
texture the dominant skin cluster is `#6E4632` and the dominant body cluster `#1E1E1E` — **22.6 L points
apart**. The bake keeps the hues but throws away **53% of the head-to-body lightness contrast**. This is the same
characteristic already recorded for `SK_CrashDriverTrellis`, whose leather measured value 0.28-0.35 and "is why
the model reads dark". It is the strongest argument for spending the 35 credits on him once Meshy is reachable.

**Nothing about this makes him canonical.** He is committed as the free option, in the same way
`SK_CrashDriverTrellis` sits beside the Meshy `SK_CrashDriver`. One Meshy login restores the 35-credit path, and
the choice between them belongs to a person.

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
| animation | `ABP_CleaverBoss` (AnimationBlueprint mode, verified on both the class default and the placed actor, Nov 13). Its AnimGraph is `BS_Idle_Walk_Run_CB` -> Slot `DefaultSlot` -> Output Pose, with the blend space driven by a `BossAnimSpeed` float. The earlier single-node + `BossDriveAnim` note was superseded by `5920c65` |
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

### OPEN DEFECT - he floats about a metre whenever he animates (found Nov 13, not fixed)

The Team Owner reported after a playtest that the mob boss "sometimes floats in the air". He does, and the
"sometimes" is the clue: **standing still he is correct, and the moment any clip plays he rises ~107-113 cm.**

Measured in PIE by reading the world Z of all 83 bones each frame (`JumpCut/Saved/jcpy/boss_feet.py`), floor at
`z = 2.0`:

| State | lowest bone in the skeleton | height above the floor |
|---|---|---|
| idle, standing | `z = 2.00` | **0 cm** - correct, feet planted |
| walking (380 cm/s) | `z = 108.8 - 114.8` | **107 - 113 cm** |
| cleaving | `z = 95.7 - 114.8` | **94 - 113 cm** |
| back to idle | `z = 2.00` | 0 cm |

**It is not the Blueprint and it is not physics.** The class default and the placed actor agree exactly (capsule
half-height 115, mesh `z = -115`, scale 1.2921, `AnimationBlueprint` + `ABP_CleaverBoss`) - there is no stale
instance override this time. The capsule stays on the ground: `MOVE_WALKING` on all 1,910 sampled frames, actor
`Z = 117.00` throughout. **Only the mesh leaves the floor**, so it is baked into the retargeted clips.

**The cause is the retarget root.** `IK_SK_CleaverBoss`'s retarget root is `Bone_001` and `IK_Mannequin_Src`'s is
`pelvis`. In this rig `bone_000` is the real root and sits on the floor (`z = 2.00` in the idle pose), while
`Bone_001` sits **117.6 cm above it** - and 117.6 cm is the lift we measure. The retarget writes the mannequin's
pelvis height into `Bone_001`'s *local* transform, whose parent is already the floor-level `bone_000`, so the
offset is applied twice and the whole skeleton rides a pelvis-height too high. The idle escapes it because
`MM_Idle_CB` has no root translation at all (measured delta `(0,0,0)`); every clip that *does* have one is lifted.

**The repair** is to re-do the retarget with the roots at matching heights - target root `bone_000` against the
mannequin's `root` - and re-bake the locomotion clips (`MF_*_CB`) and the four `MM_*_CB` montage sources. Do not
try to cancel it with a mesh `z` offset: that would sink him into the floor whenever he is idle.

**Two related things found at the same time, both left alone deliberately:**

- `MM_Attack_01_CB` / `MM_Attack_03_CB` carry `bEnableRootMotion = true` with `bForceRootLock = false` (the walk
  and jog clips have the lock *on*), and `ABP_CleaverBoss` runs `RootMotionFromMontagesOnly`, so on paper a punch
  should drag the capsule `+145.8 cm` and a cleave `+209.1 cm` (measured on the assets; Z is zero in both, so this
  is never what lifts him). **In PIE the capsule does not jump by anything like that**, so the motion is evidently
  not reaching the movement component - consistent with it living on `Bone_001` rather than the skeleton root.
  Setting `bForceRootLock = true` on both was tried and **reverted**: it changed nothing measurable, and an
  unproven edit to an LFS binary is not worth committing. Re-test this after the retarget is redone.
- During a Freeze Frame the boss holds whatever pose he is in, including mid-air (`CustomTimeDilation = 0` freezes
  his animation as designed). Measured: he hung with his lowest bone 72.9 cm up for the whole 4.6 s freeze. That
  is correct time-stop behaviour, but it compounds the float and will read as the same bug to a playtester.

**How to re-check it in one command:** `py "<repo>/JumpCut/Saved/jcpy/boss_feet.py"` in the editor console during
PIE. It wakes the boss, puts the player in front of him, and writes a per-frame table of the lowest bone's Z. A
fixed boss reads `LIFT` near 0 while walking. Judge it by that number, not by a montage name: a montage reports
itself as playing whether or not the pose is anywhere near the floor.
