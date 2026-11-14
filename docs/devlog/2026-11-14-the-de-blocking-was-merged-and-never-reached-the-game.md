# The de-blocking was merged twice and never reached the game

*Sat Nov 14 2026, 6:40 AM Pacific. M_Station, Unreal editor live (PID 12844).*

The Team Owner asked, twice now, why beats 1 to 3 still look blocky. This morning two passes answered it
in the kit — six cafe pieces chamfered (PR #97), every building shell chamfered through two shared helpers
(PR #99) — and both were merged to `main` and `playtest`. **None of it was in the game.**

## How that happens, and why nothing says so

`Art/Blender/jumpcut_city_kit.py` builds a mesh. `Art/Blender/export/City/SM_X.fbx` is what it exports.
`JumpCut/Content/Game/Imported/City/SM_X.uasset` is the thing Unreal actually renders, and it only changes
when **something re-imports the FBX**. Both de-blocking commits touched the kit, the FBX and the model
index, and **zero `.uasset` files** — `git show --stat` on each one confirms it. So the work was real,
committed, reviewed and merged, and the thing on screen never moved. Nobody was wrong about anything; there
was simply no check that the two halves agreed.

There is now: **`tools/unreal_city_mesh_audit.py`**. `city_models.json` already records every model's
triangle count as Blender built it; the tool asks Unreal for the same number and prints the difference.

```
model                       blender   unreal
SM_CafeShelf                   1364      372   STALE  (-992)
SM_CafeChair                    532      128   STALE  (-404)
SM_CafeBanquette                576      192   STALE  (-384)
SM_CafeBarCounter               288       96   STALE  (-192)
SM_CafeCounter                  240       96   STALE  (-144)
SM_CafePastryCase               196      100   STALE  (-96)
SM_CurtainTower                5306     3266   STALE  (-2040)
SM_SetbackTower                3922     2410   STALE  (-1512)
SM_PlazaTower                  3782     2638   STALE  (-1144)
SM_BlockFiller                 1442      938   STALE  (-504)
SM_ShopHouse_B                 1196      692   STALE  (-504)
SM_ShopHouse_A                 1718     1342   STALE  (-376)
SM_ShopHouse_C                  824      576   STALE  (-248)
SM_CornerBlock                 1356     1116   STALE  (-240)

IN STEP: 71   STALE: 14   MISSING: 0
```

**Fourteen**, and look at which ones. The six cafe pieces are everything the player stands among for the
whole of beat 1. The eight shells are the largest silhouettes on the street. The exact things he was
pointing at.

All 14 are re-imported, saved, and the audit now reads **IN STEP: 85, STALE: 0, MISSING: 0**.

## The street tree, which was blocky for a reason and did not have to be

![Street tree, before and after](media/2026-11-14-street-tree-before-after.jpg)

The canopy was axis-aligned boxes in three spaced tiers, and the comment above it explains why: crossed
leaf cards are one quad each, so Unreal culls their backs and the canopy vanished from the north; marking
the material two-sided fixes the culling and makes Unreal light a back face with the **front** face's
normal, so half the canopy came out pure black before the cel pass even ran. Blocks have outward normals
on every side, so they were the safe answer. They were also three green bricks on a stick.

The middle ground is a **lobe** — new primitive, `B.lobe()`. An n-gon profile, rotated by a per-lobe `yaw`
so no two share an edge direction, lofted in three bands: pinched, full at the waist, pinched again. It
keeps the one property blocks have and cards do not — **every face points outward** — and its silhouette
under the outline pass is a curve instead of three straight lines. 32 triangles at n=6.

Two things mattered beyond the primitive:

- **The tiers have to overlap.** Spaced apart they read as three stacked discs, which is the blocky problem
  in a different shape. Each lobe is now taller than the gap to the tier above and its centre is jittered
  in z, so the union is one rounded mass with bumps.
- **The canopy had to not get bigger.** The first version grew the footprint 15 cm on +y, and re-running
  `jumpcut_city_layout.py` showed the nudging placer shuffling two unrelated props to make room — a level
  change, for a tree. Tuned until the footprint came out **strictly smaller** than the committed one
  (x −125.1…123.0 → −100.2…108.5, y −110.7…112.2 → −104.1…111.8), which cannot create a collision that
  was not already there, so `city_layout.json` is unchanged and nothing in the level moves.

`SM_StreetTree` 316 → 960 tris, `SM_Hedge` 216 → 728 (its broken top edge is lobes now too). Kit total
50,079 → 51,235 across 85 models.

## Three traps this cost, all now in CLAUDE.md

- **A re-import of a committed `.uasset` raises a modal `Check Out Assets` that freezes the game thread and
  the MCP with it**, even when the file has been made writable. It is already documented; what is new is
  that it fires from the **auto-import watcher**, not just from an explicit import, so it can appear
  minutes after you copied a file in and with no command of yours running.
- **The screen cannot be photographed on this machine.** A `CopyFromScreen` capture of the dialog came back
  pure black — the session is not rendering to a visible desktop. Enumerate the window titles for
  `UnrealEditor` instead; `chat-tools/dismiss_modal.ps1` finds it by title and posts ESC to it, which is
  Cancel. **Cancel is always correct here: this repo uses git LFS, not Unreal source control.**
- **An MCP call that times out on the client may never have reached the editor at all.** The documented
  note says a timed-out call still ran. That is true of a call the editor *received*; a `FillForm` that
  times out during the modal freeze does not, and the editor's log is the only way to tell - check for the
  `Cmd:` line before believing the script executed.

## Nobody has played it

Everything above is the editor rendering its own level from cameras I positioned, plus Blender and the
triangle-count audit. The `.umap` was not touched and no actor moved.
