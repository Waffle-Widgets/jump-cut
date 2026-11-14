# 2026-11-13 — The city goes into the level, and the door curtain that sealed the cafe (Justin's Mac mini)

- **What we asked for:** "If we're done with beat 4 lets continue. What's next?" — and, standing from an
  earlier message in the same chat, "We should work on things in order of how we are playing through the game"
  and "make sure we are merging as we go".

- **Prompt(s) we gave the agent:** *"If we're done with beat 4 lets continue. What's next?"*

- **What happened:**

  Beat 4 was confirmed merged (`main` and `playtest` both `99c9fdb`, 0 ahead / 0 behind). Reading the roadmap in
  play order, the one Friday checkpoint item with **zero** progress was *"Buildings and basic assets laid out to
  follow the story beats"* — the 44-model city kit M Station built on Nov 13. It had never been opened in Unreal
  on any machine, and `tools/jumpcut_city_place.py` had never been run. GameStation, the builder, was asleep.

  **Four things were wrong before a single asset was imported, and all four were found by arithmetic.**

  1. **The committed `city_layout.json` was stale.** Regenerating it from the committed generator produced **224**
     actors, not the 216 in the file. The eight extra were every `City_Avenue*` piece — the New York avenue at
     x = -1900 that the generator's own docstring calls *"the one piece of layout the story actually requires"*,
     because it is the road the car comes down before it hits the cafe. The script had been edited after the JSON
     was last written, so the avenue existed in code and nowhere else. Nobody would have noticed it missing; there
     would simply have been no road outside the hole in the wall.
  2. **A 62 m tower stood in the middle of beat 4.** `City_Landmark` (`SM_CurtainTower`) sits at (12600, 0) to
     close the view down the lane. Its footprint is x 11891..13309, y -1309..+30 — which is gap 2, platform
     `B4_P2` and gap 3 of the platforming section. Beat 4 was placed at 23:20 UTC **after** this layout was
     authored, so the layout's own collision checker had never heard of it. It is moved to x = 16200: same view
     axis, still 62 m tall, now behind the beat-5 landing pad. The checker was taught about beat 4 first
     (`'beat 4 run', 11200..14750, |y| <= 300`) and then **proved** by putting the tower back at 12600 and
     watching it fail: *"City_Landmark (SM_CurtainTower) at (12600, 0) is inside 'beat 4 run'"*.
  3. **Five of the 44 FBX were already imported** as beat 4's ruin pieces, with Nanite off and
     `CTF_USE_COMPLEX_AS_SIMPLE` collision set by hand yesterday. Re-importing resets materials, so only the
     **37** models the layout actually uses were copied in. The five ruins were never touched.
  4. The layout references 37 distinct models and every one of them had an FBX. Nothing was missing.

  **Then the script ran, for the first time ever.** Its author predicted *"expect to fix a line, not a layout"*,
  and that is exactly what happened: it created 12 materials, placed all 224 actors, and died on
  `a.set_editor_property('hidden_in_game', hidden)` — a property `AActor` does not expose to Python. One line.
  The setter is `set_actor_hidden_in_game()`.

  **Two things the script never did at all, which mattered more than the crash.** Interchange turns Nanite **on**
  and builds **one auto convex hull** per mesh. Nanite buys nothing on a 20,615-triangle city and its simplified
  fallback drops thin parts — which here is the signage, the cables, the fire escapes, the noren and the bicycles,
  i.e. most of what makes the lane read as Tokyo. And a convex hull does not match an L-shaped shophouse or a cafe
  interior. `prepare_meshes()` now switches Nanite off and sets `CTF_USE_COMPLEX_AS_SIMPLE` on all 37, reading
  before it writes so a second run reports `Nanite off on 0, collision ... on 0, of 37`.

  **And that fix created the best bug of the day.** With real collision, `City_CafeNoren` — the cloth door curtain
  at (648, 0), 150 cm wide and 100 cm tall — became a **solid wall across the only exit from the cafe**. A
  chest-height trace down the route found it at x 640..660. It renders perfectly. Nothing about it looks wrong.
  It would have ended every playtest at beat 1 with "I can't get out of the coffee shop". Collision is now off for
  `SM_Noren` and `SM_CableSpan` — on the **actor**, via `set_actor_enable_collision(False)`, because that
  serializes where the component-level flag did not for beat 4's end wall.

  **The last defect was the hide not reaching disk.** `set_greybox` hid the 8 grey boxes the city supersedes, and
  the editor reported success — but after the save, 224 new actor packages were dirty and **not one** of the 8
  grey-box packages was. Hiding an actor does not mark its package dirty, and this map is one-file-per-actor, so
  the hide lived only in memory and the grey walls would have come back on the next load, standing inside the
  city. Re-setting the full transform dirties it; `EditorLoadingAndSavingUtils.save_packages` writes it. All 8
  were also read-only under LFS and had to be locked first, or the save would have failed silently a second time.

  **Verified after reloading the level from disk**, not from the script's own report: 289 actors total, **224**
  `JC_City`, **23** `JC_Beat4` untouched, **0** duplicate labels, all 8 grey boxes still
  `hidden_in_game=True`, ground present at x = 0, 300, 3000, 8120, 11700, 12850 and 14250 (so the tower move did
  not cost beat 4 its floor), and the route clear at chest height along y = -200, 0 and +200 except for the two
  plaza gates, the crashed car, the cafe's own east wall beside the door, and `City_Barrier_2` — a deliberate
  200 cm road barrier in a 10 m lane.

- **What we learned:**
  - **A generated file and its generator drift apart silently.** The only way to know `city_layout.json` was eight
    actors out of date was to re-run the generator and diff. Check a committed artefact against the code that
    makes it before building on it.
  - **A keep-clear list is only as good as its newest entry.** The layout checker passed a tower standing in beat 4
    because beat 4 was built after the checker was written. When new level geometry lands, add it to the no-go
    table in the same session — and prove the new entry catches something.
  - **Correct collision is not the same as wanted collision.** Making the kit collide with its render mesh was the
    right call and it immediately sealed the cafe door with a cloth curtain. Decide per-model which pieces the
    player walks *through*.
  - **"Hidden" does not dirty a package.** In a one-file-per-actor map, a flag you set on a placed actor can be
    reported as set, read back as set, and still not exist after a reload.

- **Media:** ![The street the player walks, looking east from the cafe door](../media/2026-11-13-city-lane.png)
