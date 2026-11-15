# 2026-11-14 — The details were thinner than a pixel (GameStation)

- **What we asked for:** after #114 the city was much better, but four things still shimmered. The playtester named
  them precisely, and ranked them — which turned out to matter, because one of the four is barely worth fixing.

- **Prompt(s) we gave the agent:**
  > This helped a lot, I still see some flickering on some things like the cracks in the sidewalk, the rims of the
  > circles in the street, the thing that looks like a ladder in the coffee shop behind the register on the wall,
  > and railings on buildings at a distance from an angle. The railings are the least of my concern.
  >
  > whatever fixes it is fine, go.

- **What happened:**

  **It was not z-fighting at all**, which took three separate checks to establish. Intra-mesh different-material
  ties are **0.0 cm²** in every model that could plausibly be involved — `SM_Kerb`, `SM_Manhole`, `SM_CafeShelf`,
  `SM_FireEscape`, `SM_DrainGrate`, `SM_CafeRegister`. The between-actor vertical class was what #114 had just
  fixed. And the third check found a hole in #114's own scan: `final.py:40` reads
  `if abs(n[2]) >= 0.1: continue`, so that scan looked at **vertical faces only** and never checked horizontal
  ones — exactly the surfaces you look *down* at, which is three of the four complaints. That class is real,
  19.60 m² across 100 pairs, but ray-casting straight up from each tie showed only **7.70 m² is open to view, and
  all of it is one skyline pair 110 m away**. Every street-level instance is buried: the 53 kerb pairs sit under a
  14 cm pavement slab, the counter pair under 6 cm of counter.

  **The "ladder behind the register" was the wrong object twice over.** `SM_CafeShelf` is the obvious candidate —
  two posts, five rungs, literally a ladder — and it is not it: its posts measure 9.98 px at 5.1 m, nowhere near
  sub-pixel, and it sits at x = −220, well away from the register at x = −540. The thing actually behind the
  register is `City_CafeDeco_09_CafeChalkboard`, spanning x[−600, −360], and `build_cafe_chalkboard:2006-2011`
  draws the menu as **seven horizontal bars at 21 cm pitch**. Seven rungs on a dark frame. A false lead got killed
  there too: the chalkboard really does sit with 40,800 cm² of exact 0.00 cm tie against the cafe wall, and the
  wall art is likewise at y = 500.0, none of which #114 touched — but every one of those ties is
  **opposite-facing**, so the prop's back is backface-culled and the wall behind it is occluded by the prop's own
  body. Invisible.

  What it actually is: **all four are thinner than one screen pixel.** Measured at each object's real distance from
  the beat-1 walk, 90° FOV, PIE at 1709 px wide:

  | what the playtester called it | geometry | size | dist | px @62.5% | px @100% |
  |---|---|---|---|---|---|
  | cracks in the sidewalk | `build_kerb` flag joints, 1 cm proud | 2.0 cm | 4.9 m | **1.06** | 1.70 |
  | rims of the circles in the street | manhole annulus, foreshortened | 6.0 cm | 7.2 m | **1.62** | 2.59 |
  | the ladder | chalk strokes, proud edge | 0.6 cm | 6.9 m | **0.74** | 1.18 |
  | railings at a distance | balusters, 3 cm at 30 cm pitch | 3.0 cm | 42.9 m | **0.60** | 0.96 |

  The chalk strokes are the worst case because the contrast is maximal — `MS_CafeWall` (0.93, 0.85, 0.72) on
  `MS_CityTrim` (0.11, 0.12, 0.14), a **7.6:1 luma step on a 0.74 px edge**. The baluster pitch crosses the Nyquist
  limit as well: 6.41 px per 30 cm repeat at 40 m, down to 2.70 px at 95 m. That is why the railings were ranked
  least important and are also the hardest to fix — the fix for a repeat that outruns the pixel grid is fewer
  balusters, not thicker ones.

  Two findings closed off the easy routes. **Every city mesh is LOD count 1 with Nanite off**, verified live on ten
  models, so "LOD popping" — still on #67's suspect list at that point — is *impossible*: there are no LODs to pop.
  But turning either on is the wrong medicine, because `jumpcut_city_place.py:309-316` disables Nanite deliberately
  (its fallback mesh "drops thin parts … the signage, the cables, the fire escapes, the noren and the bicycles",
  and RT shadows read that fallback), and auto-LOD by triangle reduction does the same thing. Both work by deleting
  exactly the detail that is aliasing. And **TSR is already at its maximum anti-flicker setting** — the log shows
  `AntiAliasingQuality@3` applying `r.TSR.History.ScreenPercentage:200`, which `TemporalSuperResolution.cpp:53-61`
  documents as the Nyquist-sufficient rate and the highest supported value, plus `ShadingRejection.Flickering:1`
  and `Resurrection:1`. For the first time on this hunt there was no five-second console variable to try.

  So the fix was geometry: make the four features thick enough to survive a pixel. Five models rebuilt, triangle
  counts **168/252/696/132/120 → 108/140/588/184/184**, every bounding box unchanged to the millimetre by design,
  material slot order identical, and net **164 triangles cheaper** overall. Merged as PR #118, `main` at
  `bc6865a`, and verified live in a relaunched editor reporting those same five counts.

- **What we learned:**

  **Part of this was our own previous fix.** #111's `stand_proud()` cured the depth tie by lifting flat detail
  0.4 cm along its normal. That worked — and a 0.4–0.8 cm proud face is itself sub-pixel at these distances, so it
  traded a z-fight for a shimmer. The proper cure is to stop standing flat detail proud at all: punch the parent
  face and butt the detail into the hole, so it is coplanar by construction with no overlapping parent behind it.
  No depth tie and no sub-pixel step. That is what the chalkboard now does; the others were simply thickened.
  A fix measured only against the symptom it targets can introduce the next symptom.

  **A guard written for the last pass refused this one, and inverting it made it stricter.**
  `tools/unreal_city_reimport_by_name.py` was built for #111, where triangle counts must **not** move and bounds
  growth is what proves the import took. This pass inverts both: triangle counts **must** move, and every bounding
  box is unchanged to the millimetre, so bounds prove nothing. The guard would have refused to save all five. It
  now reads an **expected-tris table**, which does both jobs better than bounds ever did — the count must equal
  what Blender built *and* differ from what was in the level. A model with no entry keeps the old strict
  behaviour, and an unreadable table is fatal rather than a silent fallback, because a strict fallback would fail
  every model for the one reason you expect.

  **Punching a hole in a face is the risky edit, so it was proved rather than eyeballed.** Tiling a punched-out
  face can leave a hole straight through the board, or a doubled strip — which would be a *new* coplanar tie, the
  exact class #111 cleared, reintroduced by the fix meant to remove a shimmer. Rasterised at 2 mm: **3.680000 m²
  of face on a 3.680000 m² board, 0 gap cells and 0 overlap cells across 920,000 samples**, with all 11 chalk
  strips flush. And the whole-kit z-fight number came back byte-identical to the committed kit (9294.9 cm²,
  #111's documented same-material residual), so nothing new was introduced anywhere. A screenshot could not have
  shown any of this — a flush-vs-proud change is deliberately invisible.

  **A verifier that reports a real feature as absent is worse than no verifier.** Ours printed the manhole's outer
  side wall as `0.000 m` — a real 2.5 cm feature. The cause: `tube` winds its bottom cap *up-facing*, so the
  up-facing z set contained the buried underside and missed the centre plate's top entirely. It now measures from
  radius and z directly: outer side wall **2.81 px** (the sunlit, high-contrast feature) and centre plate riser
  **1.35 px** (dark-on-dark, the tolerated residual). Both measurement tools are committed as
  `Art/Blender/subpixel_measure.py` and `subpixel_coverage.py` so the other PCs have them.

  **The FBX exports are not byte-reproducible.** A no-op rebuild changes all 85 FBX binaries, so "which files did
  I actually change" cannot be answered with `git status` — it needs a content hash of the geometry. `city_models.json`
  by contrast came back content-identical apart from line endings, and after the edits differed in exactly five
  `tris` values with no bounds moved, which is what proved nothing in the layout would shift.

  **Two mechanical things bit, both worth avoiding next time.** `gh pr merge --delete-branch` tried to fast-forward
  the local clone while the editor was open and **failed to unlink two of M_Station's character assets** from PR
  #117 that the editor had loaded, leaving the working tree a partial mix of two commits — GitHub's merge was
  fine, only the local checkout broke, and `git reset` to `origin/main` put it right. Then closing the editor
  raised a **Save Content** dialog listing **46 dirty actor packages** — the actors that *reference* the five
  re-imported meshes. No actor had moved; the dirty flag was just the mesh reference reloading. Saving them would
  have added 46 LFS binaries for no semantic change, on files we held no locks for, so **Don't Save** was correct.
  Read that dialog before answering it.
