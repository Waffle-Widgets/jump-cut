# 2026-11-13 — The goons get a body, and the credits buy a number (M Station)

- **What we asked for:** the morning's goon model had been made with TRELLIS for nothing, because the meshy.ai
  session in our browser had lapsed to logged-out and an agent may not ask for or type a password. We reported
  that as a deviation from the standing "Meshy where we can" decision and asked whether to spend 35 credits on a
  Meshy version and compare, or keep the free one.

- **Prompt(s) we gave the agent:** the actual words, quoted:

  > spend them

  and, after the session dropped mid-run and was resumed:

  > continue. Remember to use ComfyUI and Meshy for consistency.

- **Why it mattered enough to ask.** The goons are the enemy the player fights in beats 2, 3, 4 and 5 — more
  screen time than any boss — and until that morning no document in this repo said what one looks like. The
  design's whole silhouette rule is that the head reads as a bright dot above dark shoulders, so that three goons
  standing 150 cm apart read as three figures rather than one mass. Whether a generator keeps that contrast is
  not a matter of taste, so it could be measured instead of argued.

- **What happened.** The Team Owner logged the dedicated Chrome profile back into meshy.ai (8,322 credits), and
  the whole flow ran from the chat through Playwright: upload the jam-made reference sheet, generate, remesh,
  rig, download. Meshy named him *Crimson Enforcer*. One generation, **35 credits**; the remesh and the rig were
  free. `Art/Blender/meshy_character.py` turned the animate-phase GLB into `SK_StreetGoon.fbx` at **180.0 cm
  exactly, 18,000 triangles, 76 bones, Walk + Idle**, bake fit 0.145 cm.

- **What we verified, and how.** Not by reading the generator's log. The exported FBX was re-imported into a
  clean Blender and measured: 76 bones, 18,000 triangles, 15,417 vertices, **0 unweighted vertices**, both
  actions present. The weighting is better spread than our TRELLIS characters — the heaviest top-owner is
  `Bone_014` at **10.1%** of the mesh, against `SK_CrashDriverTrellis`'s `clavicle_r` at 16%, the bone that
  flattens that model's sleeve into a plate on a big shoulder swing. The walk cycle was checked **by looking**:
  legs alternate, knees bend, feet plant and lift, arms counter-swing.

- **The number the credits bought.** On the reference sheet, skin sits **47.6 L points** above the graphite. We
  sampled the same zones on both bakes:

  | | sampled skin | sampled chest | head-to-body lightness | share of the sheet's contrast kept |
  |---|---|---|---|---|
  | **Meshy `StreetGoon`** | `#C78E79` (L 64.1) | `#2A363A` (L 21.7) | **42.3 L** | **89%** |
  | TRELLIS `StreetGoonTrellis` | `#56523E` (L 34.7) | `#202020` (L 12.3) | 22.5 L | 47% |

  TRELLIS bakes the reference sheet's own cel shading into the base colour, so what the audit sampled as its
  "skin" is really a shadow tone. Meshy's reads as lit skin. That is the whole justification for the 35 credits,
  and it is worth saying that **the colour audit cannot see it**: both models pass `color_audit.py` with no flags
  at all.

  ![Meshy vs TRELLIS, the same goon](../media/2026-11-13-streetgoon-meshy-vs-trellis.jpg)

- **The other defect the paid model does not have.** Our reference sheet is a single front view, so a generator
  has to invent the back. TRELLIS invented a dusty mauve patch across the left shoulder blade that is in no part
  of the design, and softened the buzzed scalp into a shapeless crown. Meshy's back is the waistcoat, belt and
  pockets the design asks for. We measured the mauve rather than arguing about it, both times: the nearest texel
  to Splice's reserved magenta is dE76 **45.4** away on the Meshy bake and **33.4** on the TRELLIS one, and
  neither has a single texel within 25. It was never a power-colour collision — it was invented colour on a
  deliberately achromatic character.

- **What it cost us to choose Meshy, which we are not hiding.** Meshy's Smart Rig names bones `Bone_000...`.
  TRELLIS names them the way Epic's mannequin does. The goon's three animations — `AM_Human_Punch_02`,
  `AM_Human_HitReact`, `AM_Human_Death` — are authored **on the mannequin skeleton**, so the free model is the
  one that should have retargeted them without hand-mapping, and the paid one will need chains mapped by hand the
  way `SK_CleaverBoss` needed nine. We picked the model that looks right over the model that wires up easily,
  because the contrast loss is visible to a judge and the hand-mapping is an hour of someone's time. Both claims
  about retargeting are still **reasoning from bone names**: neither goon has been imported into Unreal at all.

- **Two traps worth the next person's time, both silent.** Meshy's **Pose switch read off** when the upload panel
  opened, even though the character generated an hour earlier had it on — it does not persist, and A-Pose off on
  a character you intend to rig is only visible once the rig is already wrong. And the **Remesh dialog defaulted
  to 10K / Triangle** this time, where it had offered 30K / Quad for the coworker. The documented values have to
  be set and read back every time, never assumed. Picking the textured asset out of the two that one run leaves
  behind was done by querying the page for mean saturation (0.19 textured against 0.03 untextured) — the
  thumbnails do not distinguish them, and the coworker nearly shipped from the untextured one.

- **One thing flagged and left alone.** The whole garment carries a blue-slate cast: chest, waist, thigh and shin
  all sample at hue **195 to 210 degrees**, within a few degrees of the **192** this project reserves for Freeze
  Frame. By the measure that decides whether a player confuses two colours it is clear — those zones are value
  0.22 to 0.29 against frost's near-white, 65 to 80 dE apart, and only 0.003% of the texture comes within dE 14
  of frost at all. Same shape as `CafeCoworker`'s apron at hue 189.9. Recorded, not changed.

- **What is still not true.** **He is not in Unreal.** `CLAUDE.md` makes M Station the maker and GameStation the
  only machine that touches `.uasset` files, so `SK_StreetGoon.fbx` and its texture are committed and waiting for
  the builder, and `BP_Goon` still wears Epic's mannequin — alongside `SK_CafeCoworker.fbx`, which has been
  waiting since this morning. Nobody has seen either model move outside a Blender preview.

- **Housekeeping we owed the record.** The goon's design, his reference sheet and the TRELLIS model were all made
  earlier today and **had no rows in `PREJAM.md`** — an omission in the jam declaration, not in the work. Both
  rows are added now, and the submission form's "Tools you used" checklist was missing ComfyUI and Meshy, which
  we have both been using all week.
