# 2026-11-14 — Two walls on the same plane (GameStation)

- **What we asked for:** the playtester had looked at the things that were still flickering after #111 and spotted
  what they had in common — walls sitting on top of each other — and asked us to confirm it before fixing anything.

- **Prompt(s) we gave the agent:**
  > I'm looking at the assets in the game that are flickering and one thing I believe they all have in common is
  > that there are two walls on top of each other and they are clipping through each other. We may need to offset
  > one wall so it is clearly on top or in front of the other and it doesn't create a flicker when walking past it.
  > Can you confirm this?
  >
  > go, and you can file the other separately but fix it as well.

- **What happened:**

  The hypothesis was right, and it was the bigger half of the bug. #111 had fixed faces that tie **inside one
  mesh** — `stand_proud()` works one model at a time and cannot see across actors. PR #41 had compared actors, but
  only their **bounding boxes**. So the class the playtester described — a real face of one actor on the same world
  plane as a real face of another — had never been scanned.

  Scanning it meant rebuilding the city out of real triangles: all 74 kit FBXs loaded in Blender, transformed into
  Unreal world space with `city_layout.json`, **305,183 triangles across 387 actors**. Two checks before trusting a
  number out of it: it reproduces `City_CafeSign`'s world bounds as `(630,−206,290)−(664,−45,390)`, matching what
  the editor had reported in an earlier session, and it independently reproduces #111's finding that the sign and
  the awning are nowhere near a tie — that pair never appears in the output at all.

  The result: **44.84 m² of exactly-tied face area between different actors, across 126 actor pairs**, against the
  2.66 m² #111 had fixed inside meshes. Narrowed to ties that can actually be seen — vertical faces, same facing
  direction, different materials, gap ≤ 0.05 cm, reaching below eye height — **5.69 m² across 16 pairs**, the
  nearest of them 5–10 m from the beat-1 walk.

  The cause is one habit in `Art/Blender/jumpcut_city_layout.py`, and it is the same mistake as #111 one level up.
  Line 45 sets `STREET_Y = 500.0`, *"the facade line, both sides."* Line 564 then mounts every shop sign at
  `sgn * (STREET_Y - 6.0)` — and the sign model is exactly 34 cm deep, so its front face lands precisely on the
  shophouse wall plane at **494**. All 21 sign actors sit there. Lines 471–472 do it to the two street ducts, and
  line 235 puts `SM_CafeClock` on the facade line itself. The kit drew details flush with the surface they sit on;
  the layout mounts props flush with the wall they hang on. Ray-cast from the road at the pastry-case shopfront:
  at x = 1413 the first surface is the sign's own front plate at y = −494.0, and two columns over at x = 1390 the
  first surface is the *building*, also at y = −494.0.

  The cure is the playtester's own suggestion and #111's own number — the smaller thing stands **0.4 cm proud**.
  Vertical wall-on-wall ties went from **10.20 m² to 0.0004 m²**, and the player-visible subset to **none**.

  Three things about it were not obvious. Direction isn't uniform: signs move *toward* the street so they read in
  front of the shopfront, but the two ducts move *into* the wall, because their body already pokes past the
  shopfront pane and standing them proud would re-tie them against that pane a millimetre away. `SM_DuctRun`,
  `SM_ACUnit` and `SM_FireEscape` need **twice** the stand-off, because their mounting face already carries a
  `stand_proud()` lift from #111, so one stand-off just lands the lifted face where the flat one used to be —
  measured on the duct, 7,680 cm² tied at zero stand-offs, **890 cm² at one**, 0 at two. And the nudge had to be
  applied as a post-pass rather than at the call sites: 4 mm applied before `put_clear()` runs was enough to flip a
  slide decision and throw `City_Front_S00_ShopDisplay` 4.8 m down the street.

  The structures that interpenetrate are a different problem and there were more of them than the two we knew
  about. The exit run's shophouses overlapped by 14 cm and 24 cm; `City_RunS_A` stood 27 cm *inside* the plaza
  wall; `City_AvenueFar_N` was buried 189 cm in `City_CornerNW` and `City_AvenueFillA` 209 cm in the same block;
  `City_AvenuePole` stood entirely inside `City_CornerSW`; and `City_SkyTank_0` was at z = 1900 like the other
  three roof tanks, which put it **inside** a 46 m setback tower instead of on top of anything. There is no face
  to lift when two blocks interpenetrate — one of them has to move, which changes the shape of the street — so
  that class went to **issue #115** and the moves were made deliberately rather than by formula.

  So it cannot come back quietly, `validate()` now checks that *every* pair of structures keeps `GAP = 20 cm`, not
  just the two lane rows — the gap in the check that let all of these through in the first place. That new check
  immediately turned up `City_CrossPole` buried in `City_CornerSW`, which the triangle scan had missed.

- **What we learned:**

  **The dead end was ours, and it was the thing the playtester had circled.** The cafe counter props came up high
  in the first pass and we expected them to be the headline. They are not: `City_Cafe_00_CafeCounter` is 110 cm
  tall while the pastry case and the espresso machine sit at z = 104, so they are embedded 6 cm *into* the counter
  and their tied faces point **downward**, buried inside it. That was settled by reading live bounds rather than by
  arguing — the espresso machine's base reads z = 103.6, meaning `stand_proud` pushed that face *down*, so its
  outward normal is −Z. A tie you cannot see is not a bug, and three separate times on this hunt a tie that looked
  enormous on paper turned out to be backface-culled or buried. **Check facing and occlusion before claiming an
  area.**

  **A tool that documents a default can still be wrong about it.** Moving the actors with the editor MCP's
  `set_actor_transform` and passing only a location silently **reset rotation to identity on 47 actors** —
  `City_RunN_B` ended up facing the wrong way down the exit run — even though the schema says an unset rotation
  means "don't change". It was caught by reading the bounds back out of the live level afterwards, and the
  replacement tool now owns yaw as well as position so it cannot recur. Verify a write by reading it back from the
  thing you wrote to, not from the call that claimed success.

  **Neither existing placer mode fit, so there is a third now.** A full `jumpcut_city_place.py` run deletes and
  re-makes all 387 actors — 387 LFS binaries for a 4 mm change — and its `add` mode leaves existing actors alone,
  so it would have changed nothing. `tools/unreal_city_apply_layout.py` moves only the actors whose transform
  actually differs from `city_layout.json` and saves their own packages: 88 of them.

  **The checked-in layout was already stale against its own generator.** Regenerating `city_layout.json` from
  untouched `main` moves `City_Front_S00_ShopDisplay` 4.8 m and `City_Front_Trash` 1.2 m before anyone edits
  anything, and `City_Hedge_S5` sat 30 cm from where the layout put it. Those three are in the 88 and back in
  agreement now, but two of them moved metres, not millimetres. A generated file that is committed can drift from
  its generator, and nothing was checking.

  Merged as PR #114 — 91 files, `main` at `6f25723`. Verified by geometry only: the editor viewport provably
  cannot reproduce this flicker, so the playtest was the test.
