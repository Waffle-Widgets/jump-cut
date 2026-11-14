# 2026-11-14 — The flicker was drawn into the models (Justin's Mac mini)

- **What we asked for:** "Look for any github issues related to rendering issues and have fable 5.2 work on
  them", then, after the diagnosis came back: *"Apply, submissions cannot have that flcikering"*.

- **Prompt(s) we gave the agent:**
  > Look for any github issues related to rendering issues and have fable 5.2 work on them
  >
  > !. try both and compare. 2. Apply, submissions cannot have that flcikering

- **What happened:**

  Issue #67 — the flickering borders — had carried the same two suspects since it was filed: the cafe sign and
  the cafe awning both placed at `x = 630`, and three painted road pieces laid 1 cm over the floor. A Fable 5.2
  agent measured both and **killed both.** The sign and the awning are **122 cm apart** at their nearest
  parallel overlapping faces, with no pair inside 3 cm — the awning canvas passes *through* the sign's post,
  which is a cosmetic bug and not a depth tie. The road pieces are genuinely 1 cm up, but at 60 m from a 170 cm
  eye height that is a view-depth gap of 35 cm against a depth step of ~0.0006 cm: a margin of at least
  **37,000×**. The fix the ticket had recommended all along — raise them to 2–3 cm, or make them decals — would
  have changed nothing at all, and whoever did it would have seen no improvement and been back at the start.

  The real defect is in the city kit's drawing habit. `Art/Blender/jumpcut_city_kit.py` draws a detail **flush**
  with the surface it sits on: the cafe sign's two lit `MS_CitySignA` quads are at `y = 0.1` and `y = 0.34`,
  which are exactly the front and back faces of its own `MS_CityTrim` casing box; the shopfront fascia's street
  face is exactly the `MS_CafeWall` plane above the glazing; the pastry case's glass quads sit exactly on the
  outer faces of the trim posts that frame them. Two faces of **different materials, on one plane, facing the
  same way** is a depth tie. The tie breaks differently every time the camera moves, so the border shimmers
  under motion and is rock steady when you stand still — which is the reported symptom, and is why it survived
  the shader and all the lighting being switched off.

  The corroboration is the part nobody engineered. The three meshes carrying the largest exactly-tied areas are
  `SM_CafeShell` (84,780 cm²), `SM_CafeSign` (18,900 cm²) and `SM_CafePastryCase` (1,656 cm²) — and the three
  objects the playtester had circled on the screenshot, recorded on the ticket *before* the scan ran, were the
  cafe shopfront, the cafe sign and the pastry case. Same three, arrived at independently. Kit-wide: **41 of 85
  models**, 2.66 m² of tied face area.

  The cure is the one a sign-writer uses: the smaller face stands **proud** of the bigger one. A `stand_proud()`
  pass in the kit's `finish()` lifts any face sharing a plane with a bigger face of a different material by
  **0.4 cm** along its normal. Tied area drops from 2,658,947 cm² to 9,294 cm² (sign 0, pastry case 0, shell 6).
  Same-material overlaps are left alone — both faces are the same flat colour, so a tie between them is
  invisible.

  **Then the fix nearly didn't reach the game, in the way this ticket has already been bitten once.**
  `tools/unreal_city_mesh_audit.py` decides whether the level is in step by comparing **triangle counts** — and
  `stand_proud` changes no triangle, no vertex count and no bounding box big enough to matter, so
  `city_models.json` comes out **byte-identical** (md5 `ac639be6211f07fbb295358063cce647` for the committed
  file, the base rebuild and the patched rebuild alike). After patching the kit, the audit reports
  `IN STEP: 85, STALE: 0` while 41 meshes in the level are still the old flush ones. That is exactly what
  happened on PRs #97 and #99, which were built, reviewed and merged and touched zero `.uasset` files, leaving
  14 meshes as the old boxes on screen. So the re-import has to be forced **by name**:
  `tools/unreal_city_reimport_by_name.py`.

  That script exists because re-importing a city mesh is not free. `CLAUDE.md` says "re-importing a mesh resets
  its materials, so don't re-import once it's set up" — and for the city the danger is subtler than that. What
  you see in `Lvl_JumpCut` does not come from the mesh's slots at all: every `City_*` actor carries its own
  per-component material **overrides**, and those are indexed **by slot index, not by slot name**. If an import
  changed the order or the count of a mesh's slots, every override would land on the wrong slot — the cafe
  shell's brick and glass would swap, and it would look spectacularly wrong while every triangle count still
  matched. So the script records each mesh's slot list in order, plus collision, Nanite, LODs and triangle
  count, re-imports, reads them back, and **refuses to save anything** if any of it moved.

  All 41 came back clean: materials, collision flags and Nanite identical on every one, triangle counts
  identical, no new `SM_Foo_1` assets created, and for the 22 meshes Blender predicted would grow, the bounds
  moved by the predicted amount — `SM_CafeSign` went `y_min −34.0 → −34.4`, exactly the 0.4 cm. Afterwards the
  mesh audit reports `IN STEP: 85, STALE: 0`, which is the same thing it said *before* the re-import; that is
  the blind spot, demonstrated, not a result.

  One self-inflicted detour worth recording. The guard has a "NO-OP" rule: if Blender says a mesh grew and the
  bounds did not move, the import did not take. Correct — except that we had already re-imported `SM_CafeSign`
  on its own as a single-mesh probe, so on the full run its bounds were *already* right and the rule fired on
  it, and the all-or-nothing policy then refused to save the other 40 as well. The second run tripped the same
  rule on all 22 grown meshes for the same reason. The fix was to re-run with the growth table withheld, so the
  no-op rule stood down while every material, collision, Nanite and triangle guard stayed on — the proof that
  the import took had already been produced by the first run.

- **What we learned:**
  - **A flicker that survives "no shader, no lighting" is geometry, and the geometry can be inside the mesh, not
    between two actors.** Both of #67's suspects were about two *actors* overlapping. The answer was two faces
    of one *model* sharing a plane. Bounding boxes prove volumes overlap; they say nothing about whether faces
    are coplanar.
  - **Drawing a detail flush with its surface is a bug, not a style.** Give it 0.4 cm. It is invisible at any
    distance a player reaches and about four orders of magnitude more than a reversed-Z depth buffer needs.
  - **An audit that compares triangle counts cannot see a fix that moves vertices.** It will cheerfully report
    the level is in step while every patched mesh on screen is the old one. When a change does not move the
    number your tool watches, the tool is not a check — force the work by name and prove it another way.
  - **A guard that refuses to save is doing its job even when it is wrong.** It cost two extra runs and zero
    damage. The alternative — slot overrides silently landing on the wrong material — would have looked
    spectacular and shipped.

- **Media:** ![the cafe shopfront after the stand-proud pass: awning, fascia, sign and counter, no gaps](../media/2026-11-14-cafe-shopfront-after-stand-proud.png)
