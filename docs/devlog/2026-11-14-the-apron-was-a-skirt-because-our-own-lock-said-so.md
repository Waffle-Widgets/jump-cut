# The apron was a skirt because our own lock said so

**Sat Nov 14, 2026, 4:30 → 5:05 AM Pacific — M Station**

The Team Owner's note was three things at once: *why do we still have blocky assets in beats 1-3*, the player
*"has a lot of holes and the apron does not make sense, it shouldn't look like a skirt"*, and the coworker
*"does not fit the style"*. All three turned out to be measurable, and two of them were our fault in a way that
was written down in this repo the whole time.

## Why beats 1-3 are still blocky: the de-blocking pass never went inside the cafe

Yesterday's pass rebuilt ten street props and wrote the chamfer tools. Counting what each `build_*` function
actually calls, **35 of the kit's 85 models are still built from `b.box` alone** — and the pattern is not random:

- **Every single piece of cafe furniture.** `SM_CafeShell`, `SM_CafeCounter`, `SM_CafeRegister`,
  `SM_CafePastryCase`, `SM_CafeShelf`, `SM_CafeChair`, `SM_CafeAwning`, `SM_CafeMenuBoard`, `SM_CafeSign`,
  `SM_CafeFloorBoards`, `SM_CafeRug`, `SM_CafeWallArt`, `SM_CafeChalkboard`, `SM_CafeBarCounter`,
  `SM_CafeBanquette` — fifteen models, zero chamfers between them.
- **The buildings themselves.** `SM_ShopHouse_A/B/C`, `SM_CornerBlock`, `SM_BlockFiller` — the largest
  silhouettes on screen in beats 2 and 3.

**Beat 1 happens entirely inside the cafe, and the cafe got none of the work.** That is the whole answer. The
street stopped being boxes; the room the game opens in never started.

Six of the worst are fixed in this pass, chosen by what the player actually stands among:

| Model | tris before | after | why it mattered |
|---|---|---|---|
| `SM_CafeChair` | 128 | **532** | **six of them**, at eye level, for the whole of beat 1 |
| `SM_CafeShelf` | 372 | **1,364** | two of them, behind the counter, in every cafe shot |
| `SM_CafeBanquette` | 192 | **576** | upholstery is the one thing in a room with no hard edge |
| `SM_CafeBarCounter` | 96 | **288** | a bullnose is the line that says "counter" |
| `SM_CafeCounter` | 96 | **240** | 5 m wide, the biggest object in the room |
| `SM_CafePastryCase` | 100 | **196** | |

**Proof that a sweep like this is safe:** `city_models.json` was diffed before and after, and **all 85
footprints are byte-identical**. Chamfers cut inward, so nothing in `tools/jumpcut_city_layout.py` had to move.

## The apron: our lock, not Meshy

`docs/character-locks.json` said *"the apron reaching below his knees"* and **gave no width rule at all**. So the
Nov 13 sheet drew a flared bell, wider than his hips, with no trouser visible beside it — and from a single
front view Meshy had no way to read that as a front panel. It did the only sensible thing and closed the flare
round the back. Rendering `SK_CafeWalker.fbx` from behind shows a complete knee-length skirt and **no bare shirt
back**, which the lock's own invariants explicitly forbid. We wrote the rule that broke the rule.

The fix is not length, it is **width**, and the lock now says so:

> the apron panel clearly NARROWER than his hips, so a strip of charcoal trouser shows down the OUTSIDE of each
> leg beside it for its whole length and he reads as two trousered legs rather than one shape

Two takes in Gemini. Take 2 is the pick and it is unambiguous: the trouser legs run down both sides of the green
panel from hip to hem.

## The holes are real, and they are on every character

Boundary edges on a closed mesh should be zero.

| Model | boundary edges | distinct holes |
|---|---|---|
| `SK_CafeWalker` (shipped) | **20,451** | **1,743** |
| `SK_CafeCoworker` | 16,600 | 1,052 |
| `SK_CleaverBoss` | 17,585 | 1,019 |
| `SK_StreetGoon` | 11,854 | 605 |
| **`SK_CafeWalkerV2` (new)** | **345** | **31** |

Half of the shipped figure's count survives an aggressive 1 cm weld, so it is not an FBX import artifact — it is
genuinely open. On a render with backface culling on you can see it: a gash through the face, gaps in the hair,
holes in the shoes. The new model is **59× better** on boundary edges.

## The coworker was drawn in the wrong medium

Side by side the problem is obvious: the player is a cel-shaded anime drawing with sharp angular ink of varying
weight and a proper anime face; the coworker is a soft rounded western-cartoon vector illustration with a small
simplified face and a broad corporate grin. She was also drawn 16:9 with the figure small in frame, which gave
Meshy less of her to work from. Redrawn with the player's own style block plus an explicit *not a western
cartoon, not Disney or Pixar, not a soft rounded vector illustration* and a hair rule (*distinct pointed clumps
with sharp tips*). One take; she now belongs in the same show.

## What is NOT done, and the decision it needs

**The new model is in the repo and is not in the game.** Its rig is **28 bones with no fingers**; the shipped rig
is **69 bones with a 21-bone five-finger subtree on each hand**. Swapping it as-is would lose the hands, and
[#72](https://github.com/Waffle-Widgets/jump-cut/issues/72) is already open on the hands.

Two things were tried and did not work, so nobody repeats them:

- **The export's "Skeleton template" dropdown is inert in this path.** The same asset downloaded as `Mixamo` and
  as `UE5 Mannequin` produced **byte-identical files** (5,460,508 bytes, `cmp` clean, `Hips`/`Spine`/`LeftArm`
  names both times). It cannot add fingers the rig does not have.
- **Meshy's `Smart Rig` is not the fix.** It is marked **(Beta)** and its examples are a deer, an octopus and a
  spider — it is the creature rigger. The 69-bone fingered rigs we already have came from an earlier Meshy.

The options and their costs are in [#96](https://github.com/Waffle-Widgets/jump-cut/issues/96). The recommended
one is to transfer the new mesh onto the **existing** skeleton in Blender, which keeps every clip, every montage
and `ABP_Unarmed_CWM` untouched — and that matters today, because #69 and #71 have only just finished
stabilising those.

## Also

Fifteen tickets, one per model used in the back alley ([#81](https://github.com/Waffle-Widgets/jump-cut/issues/81)–[#95](https://github.com/Waffle-Widgets/jump-cut/issues/95)),
each carrying its real triangle count, its instance count and whether it is still raw boxes. Two of them are
whole buildings at under 1,000 triangles with no chamfer anywhere: `SM_ShopHouse_C` (576) and `SM_BlockFiller`
(938) are the alley's two walls and the biggest thing in it.

**Nobody has played any of this.** The cafe numbers are a kit rebuild and a footprint diff; the character numbers
are Blender measuring meshes; the new model has never been in Unreal.

### One for the toolbox

The Playwright browser's downloads land in **`megajam-browser/out/`**, not `~/Downloads`. `CLAUDE.md` says to take
the newest file in `~/Downloads`, which is true of the user's own Chrome and false here — the newest file there was
a stale render from another project, and it is exactly the trap that note warns about in the other direction.
