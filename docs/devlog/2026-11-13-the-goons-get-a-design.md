# 2026-11-13 — The goons get a design, and the card draws them free (M Station)

- **What we asked for:** the Team Owner split the two machines so they stop colliding.

  > Let allbarkdev continue working while this station works on models and assets

- **What that meant in practice.** `allbarkdev` was mid-flight in `BP_Player.uasset` and `WBP_HUD.uasset`
  rebuilding Splice on the Mac. This session touched **neither those files nor the `playtest` branch**. It stayed
  in the art lane and pushed to `main` only, so the integration branch is theirs to move.

- **Why the goons and not the Director.** `ROADMAP.md`'s hand-off queue had the Director at number 2, described
  as "beat 6". That was wrong in a way worth catching rather than following: the six-beat decision of Nov 12
  **supersedes** the Director's rule scenes and ends the demo before him, and beat 6 is a fade to a "continue" —
  a screen, not a character. Meanwhile `BP_Goon` has been playable since the first build and **no document in
  this repo said what a goon looks like**. The player fights goons in beats 2, 3, 4 and 5, which is more screen
  time than any boss gets, and they are Epic's mannequin. The work-order rule in Decisions ("the earliest
  unfinished beat wins") settles it: the goons outrank the Director. The queue was reordered, with the reason
  written in.

- **The design.** `StreetGoon` is the only **inverted triangle** in a cast that already owns narrow-and-upright,
  short-and-compact, lopsided-headed, broad-rectangle and segmented. Three things in him are modelling decisions
  rather than taste:

  - **A buttoned waistcoat, not the open jacket a mob foot soldier should wear.** Lapels stand off the chest as a
    loose shell, which is the shape image-to-3D returns as a floating sheet — the same failure the `StuntDouble`
    write-up warns about for floating pads.
  - **Cuffs at the wrists.** The coworker's rolled sleeves put her bare forearms outside the colour audit's
    head-and-hands whitelist, so she reads FLAG at 4.46% / 5.27% as a false positive. One explanation of that is
    enough.
  - **A buzzed head.** `BP_GoonSpawner` puts three of them on screen 150 cm apart. A dark head above dark
    shoulders turns a group into one blob at the game camera; a skin-tone dot separates three figures into three.

- **The colour finding, which is the part worth keeping.** He is deliberately achromatic — graphite, grey, black,
  one oxblood band — so every colour on screen still belongs to a power. The band measures dE76 **54.9** from
  Splice's magenta, **80.0** from Freeze Frame's cyan and **62.3** from the proposed safety orange.

  The first draft gave him a white shirt, for the obvious black-and-white read. Measuring it first killed it.
  This repo records the Freeze Frame colour **in words only** — "pale cyan, almost white, like frost" — with no
  hex anywhere, so it was measured against a representative pale cyan, `#DCF2F5`. Against that, **pure white is
  dE76 9.7 away and every off-white tested lands at 8.5 to 9.8** — all *under* `color_audit.py`'s threshold of
  14. Three goons stand on screen in the beats that teach Freeze Frame, so a white-shirted crew would be the one
  colour collision in this cast that actually costs the player something. The shirt is a medium grey instead, at
  dE **35.4** from that cyan.

  The same number applies to the coworker's pure white shirt. It is **recorded and not acted on**: she is one
  small figure against a full-screen effect, her deep teal apron carries her read, and her 35 credits are spent.
  Written down so the next white garment in this cast is a choice rather than an accident.

- **The sheet.** Three takes on M Station's 3090 with ComfyUI + Qwen-Image. **No Meshy credits, nothing
  uploaded.** Take 2 is the keeper and the reason is mechanical, not aesthetic: it is the **only one of the three
  with the cuffs at the wrists** — takes 1 and 3 both rolled the sleeves to the elbow, reintroducing exactly the
  bare-forearm case the prompt was written to avoid — and it has the widest gaps at the armpits, thighs, knees
  and ankles. Take 3 also closed the gap between the legs. Committed as `Art/Refs/StreetGoon_apose.png`.

  Measured rather than eyeballed: of 531,001 non-background pixels, the ten dominant colours sit between dE
  **44.5** and **92.1** from the frost cyan. Nothing white, nothing pale, no magenta, no orange.

- **Meshy was unreachable, and that is the one thing a person has to fix.** The dedicated Chrome profile that
  made `CafeCoworker` this morning had **lapsed to logged-out**: meshy.ai's workspace served "Log In / Sign Up
  Free" with no credits line and no session cookie. The profile itself is correct and in use (the MCP server
  points `--user-data-dir` at it and its cookie store was written this session), so this is an expired session
  and not a configuration problem. An agent may not ask for or type a password, so the Meshy path stops there
  until somebody clicks Log In.

- **So the goon was built with TRELLIS instead, and for this character that is arguably the better tool.** The
  Team Owner's standing call is "Meshy where we can, TRELLIS as the backup if we run out of credits" — credits
  were never the problem (8,357 of them), the login was, so this is a deviation and is flagged as one. The
  technical argument is independent of it: `trellis_character.py` names bones the way Epic's mannequin does,
  Meshy's Smart Rig names them `Bone_000...`, and the goon's three animations — `AM_Human_Punch_02`,
  `AM_Human_HitReact`, `AM_Human_Death` — are authored **on the mannequin skeleton**. The cleaver boss needed
  nine chains mapped by hand for exactly this reason. That retarget is reasoned from bone names and **not yet
  demonstrated in Unreal**.

- **The numbers.** TRELLIS.2-4B, `1024_cascade`, `DEC=30000 TEX=2048`, on M Station's 3090 with **0 credits and
  nothing uploaded**: 2,903,648 verts / 5,811,524 faces from dual contouring, simplified to 237,711 / 477,743,
  decimated at export to **17,999 triangles** against the 18,000 budget. `trellis_character.py` rigged it in
  **18.3 s**: **23 bones, 0 unweighted vertices**, direct weights, UV extent 0.997 x 0.997, height exactly
  **1.800 m**, half-chest 0.404 m, three specks of 229 verts removed. Peak VRAM **about 8.6 GB of the 3090's
  24**, so ComfyUI's weights were released through its own `/free` endpoint rather than killing a server the
  Team Owner had running since yesterday.

- **Checked by looking, not by reading the log.** ![StreetGoon walk](../media/2026-11-13-streetgoon-walk.png)

  The pose sheet shows a real walk — legs alternating, knees
  bending, feet planting, fingers separated — and the rest sheet shows the waistcoat, grey shirt, oxblood tie and
  arm band all where the design puts them.

- **Two defects, both from the same cause: the reference is a single front view.**

  - **An invented dusty mauve patch on his left shoulder blade.** It looked like a collision with Splice's
    reserved magenta, so it was measured instead of argued: of 2,002,160 non-background texels, **zero** sit
    within dE76 25 of `#C0279B`, and the closest texel in the entire texture is `#9B4B76` at dE **35.0**. Not a
    power-colour collision — but invented colour on a deliberately achromatic character, so it is paint-out work
    if he is kept. The same single view softened the back of his head out of its buzz cut and widened the arm
    band well past the flush band the prompt asked for.
  - **The bake throws away half the read the design is built on.** `color_audit.py` returns **no flags** — 0.11%
    front / 0.01% back, the cleanest in the cast, because the long sleeves leave no bare forearms to miscount.
    But it sampled his skin reference as `#56523E`, value 0.34, since TRELLIS bakes the sheet's cel shading into
    the base colour. Measuring the texture directly: on the sheet, skin sits **47.6 L points** above the
    graphite; in the bake, the dominant skin cluster `#6E4632` sits **22.6** above the dominant body cluster
    `#1E1E1E`. **53% of the head-to-body lightness contrast is gone** — and that contrast is precisely what makes
    three goons 150 cm apart read as three figures instead of one blob. Same characteristic already recorded for
    `SK_CrashDriverTrellis`.

- **What this does not do.** It does not make him canonical, it is not in Unreal, and nobody has seen him move
  outside a Blender preview. M Station is the maker: `SK_StreetGoon.fbx` and its texture are committed under
  `Art/Blender/export/Characters/StreetGoon/` for the builder to import, and `BP_Goon` still wears Epic's
  mannequin until GameStation does that.

- **Lane discipline.** `allbarkdev` was rebuilding Splice in `BP_Player.uasset` and `WBP_HUD.uasset` on the Mac
  throughout. Neither file was touched, no LFS lock was taken, and nothing was pushed to `playtest` — this
  session pushed to `main` only, so the integration branch stays theirs to move.
