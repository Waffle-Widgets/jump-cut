# The goons were naked because a Blueprint overrode them

*Sat Nov 14 2026, 6:20 AM Pacific. M_Station, Unreal editor live (PID 12844).*

The Team Owner's screenshot showed three goons rendering as **flat orange silhouettes with no clothing at
all**, standing beside a correctly textured player. I had a hypothesis for it on Friday night and the
hypothesis was wrong. This is what it actually was, and how the wrong answer was eliminated.

## My Friday guess, and why it was wrong

I said the UVs were probably collapsed onto a single flesh-tone region of the texture, and that all three
Meshy characters sitting on `/InterchangeAssets/Materials/FBXLegacyPhongSurfaceMaterial` was the likely
cause. Both halves of that were wrong, and both were cheap to check.

**The UVs are perfect.** Blender, on the committed FBX, 32x32 occupancy grid:

| mesh | verts | u range | v range | grid occupancy | loops outside [0,1] |
|---|---|---|---|---|---|
| `SK_StreetGoon` | 15,417 | 0.004 - 0.996 | 0.004 - 0.995 | **100.0%** | 0 |
| `SK_CafeWalker` | 26,852 | 0.004 - 0.996 | 0.004 - 0.990 | **100.0%** | 0 |
| `SK_CafeCoworker` | 24,212 | 0.004 - 0.996 | 0.004 - 0.996 | **100.0%** | 0 |

Every one of the 1,024 grid cells is used, nothing wraps. There is no collapse.

**And the import material is innocent.** All three `FBXLegacyPhongSurfaceMaterial` instances have their
texture correctly bound - `DiffuseColorMap` pointed at the right 2048x2048 base colour with
`DiffuseColorMapWeight = 1.0`. Put the three meshes side by side in the live level and photograph them and
they render **correctly textured**: the goon in grey waistcoat, white shirt, crimson tie and oxblood arm
band, exactly as `CHARACTERS.md` specifies.

So the mesh is right, the texture is right, the UVs are right, the material is right - and he still comes
out orange in the game.

## What it was

`BP_Goon`'s `CharacterMesh0` carries **`override_materials = [M_Goon]`**.

`M_Goon` is a two-expression flat colour material from the grey-box build, in the same family as
`M_PropRed`, `M_PropBlue` and `M_GreyWall` - and its colour is skin tone. **An override beats the mesh
asset's own slot**, so the goon's correct texture was bound, sampled by correct UVs, and then thrown away
before it reached a pixel. `BP_Player` has **no** override, which is exactly why the player standing next
to them looks right. That one asymmetry is the whole bug.

![Before and after](media/2026-11-14-goon-material-before-after.jpg)

The before half of that picture is reproduced deliberately - three real `BP_Goon` actors with `M_Goon`
forced back on the *instance* only - so it is the defect itself, not a drawing of it.

## The fix, and where it had to go

On the **SkeletalMesh asset's material slot**, plus the Blueprint override. Not on an actor's
`override_materials`: the goons are **spawned at runtime** by `BP_GoonSpawner`, so there is no placed actor
to override. `C1_Cafe_CrashDriver` and `Boss_Freeze` get away with actor-level overrides only because they
are hand-placed, and that is a trap waiting for whoever adds a spawned boss.

`tools/unreal_char_materials.py` does it, and reports before acting (`measure` is the default mode):

- Three new instances of **`M_AnimeChar`** with `Tex` pointed at each character's own committed base colour:
  `MI_StreetGoon`, `MI_CafeCoworker`, `MI_CafeWalker_Meshy`.
- Assigned to the asset slot of `SK_StreetGoon`, `SK_CafeCoworker` and the Meshy `SK_CafeWalker`.
- `BP_Goon.CharacterMesh0.override_materials`: `[M_Goon]` -> `[MI_StreetGoon]`.

**Five of the six character meshes are now on `M_AnimeChar`**, which is the material the cel pass is written
against. The sixth, `SK_CafeWalker_Walk`, is the old Blender-rig walk mesh that nothing in the game points
at; it is left on its import material on purpose, so the diff stays about characters that are actually used.

## One thing that looks like a bug and is not

In the editor every goon wears a glowing orange ball over his head. That is `WarnSign` - an engine sphere at
z = 130 on `M_WarnPunch`, the attack telegraph. It reads as permanently visible in the editor because
`EnemySetup` is what hides it (`FIRST_BUILD_DESIGN.md:137`) and that only runs at BeginPlay. It is correct.

## Nobody has played it

Everything above is the editor rendering its own level from a camera I positioned, plus Blender measuring
committed FBX files. The three preview actors were deleted; the level is back to **466 actors**, zero dirty
map packages, and the `.umap` was never touched.
