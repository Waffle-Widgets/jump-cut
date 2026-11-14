# The player gets a death we authored ourselves

**Sat 14 Nov 2026 · Justin's Mac mini · Blender 5.3.0 · animation authored by Fable 5.2 (`claude-fable-5-2`)**

Every character animation in this game had been Epic's mannequin, retargeted onto Meshy Smart Rigs. This is
the first clip that is ours: `Art/Blender/death_clip.py` builds the player's death on his own 69-bone rig and
writes `Art/Blender/export/Characters/CafeWalker/SK_CafeWalker_Death.fbx`. It is issue #103's proof clip, and
it fills issue #14.

## Why this clip, and why it is not a replacement

`AM_CafeWalker_Death` already existed — retargeted from `MM_Death_Front_01` during #7. But `BP_Player`'s own
name table carries `PlayerAnimPunchA`, `PunchB`, `PunchFinisher`, `HitReact` and `IsLost` and **no death
variable at all**, so nothing plays either clip today. The hole is in the Blueprint, not in the animation.
Whichever clip gets wired in is the first death anyone sees, so authoring one displaces nothing that works.

## What it is

Sixty frames at 30 fps, two seconds. A last hook to the jaw, a reel and a step back, the legs go, he sits
down hard, his back and head slam, and he settles on his back with one knee fallen open and the head rolled
away. Frames 52–60 are identical, because the montage is imported with auto blend-out off and the last frame
is what the body holds.

![The fall, three-quarter](media/2026-11-14-cafewalker-death-sheet.png)

## The point of the exercise was looking at it

Issue #103's argument is that the retarget path could only ever verify by reading assets back — `19 of 19
chains mapped`, `saved ok True` — while shipping four defects that all looked finished. Three defects in this
clip only surfaced because it was rendered and traced rather than trusted: limbs left hanging 15 cm in the
air in the first version, a one-frame 3.5 cm whole-body pop at the slam, and a right-elbow flip in the same
frames. None of them would have shown up in a number the export produced.

The hands are the clearest case. The Smart Rig's bind pose is a wide A-pose with open, splayed palms — that
is where the paddle hands of #72 come from. Here every finger bone is curled on every frame.

![Hands at frames 1, 24 and 60](media/2026-11-14-cafewalker-death-hands.png)

## Checked, independently of the script that made it

The script's own report was re-run through a separate read-back that shares no code with it:

| | in (`SK_CafeWalker.fbx`) | out (`SK_CafeWalker_Death.fbx`) |
|---|---|---|
| bones | 69 | 69, same names, max rest drift **0.00008 cm** |
| verts / polys | 26,852 / 30,000 | 26,852 / 30,000 |
| actions | `Idle`, `Walk` | exactly one: `Armature|Armature|Death`, frames 1–60 |

- **Lowest vertex on any of the 60 frames: +0.031 cm.** Nothing goes below the floor anywhere in the clip.
- Final frame lowest vertex **+0.043 cm**; body, head, both forearms and both shins each rest at 0.04–0.06 cm,
  so he is lying on the floor rather than balanced on one point.
- Frames 52→60 differ by **0.0 cm**: the held pose is genuinely still.
- Largest single-frame vertex move: **25.2 cm** at frame 3 (the head snap) and **25.0 cm** at frame 33 (the
  back slam). Those are the two impacts; nothing else comes close, so there is no pop hiding in the middle.
- Re-running the committed script reproduced the same clip to the same numbers — the recipe is the asset.

![The held pose, four views](media/2026-11-14-cafewalker-death-final.png)

## Two traps this clip carries into Unreal

**Root motion must be OFF.** A Meshy Smart Rig's root (`Bone_000`) sits at pelvis height and carries skin
weight, so the whole fall is keyed on it. Extract that as root motion and `RootMotionRootLock = AnimFirstFrame`
pins the pelvis at standing height — the body falls out from under itself and the character hangs in the air.
That is the float defect of #69 by another route. `tools/unreal_import_authored_clip.py` sets
`enable_root_motion = False` explicitly for this reason.

**FBX does not go through the legacy importer on this project.** `DefaultEngine.ini` routes
`InterchangeFbxTranslator` → `DefaultFBXOBJAssetsPipeline`, so the usual recipe —
`AssetImportTask(options=FbxImportUI(skeleton=...))` — configures an importer Unreal is not using here. The
failure mode is the dangerous one: the clip imports, saves and reads back perfectly **on a second skeleton
that no character wears**, and never plays. The import script configures an Interchange pipeline instead
(`bImportOnlyAnimations`, `Skeleton`, `bImportSkeletalMeshes=false`, `bImportAnimations`) and refuses to
finish unless the imported clip's skeleton is the same *object* as the one already in the game.

## Honest verdict, and what is not done

The sit-down at frames 20–28 is the weakest beat — both knees fold fairly symmetrically and it reads a little
deliberate. The held pose is believable but slightly posed: left arm straight out, torso flat, hands still
fairly tight. The thumbs poke slightly out of the frame-1 fists, and the finger mesh is angular in close-up,
which is the mesh and the skin weights, not the clip.

**None of this has been in Unreal.** The clip is not imported, `BP_Player` still has no death variable, and
nobody has seen the player die in the game. Both of those need Justin's clone brought up to `origin/main`
first — it is 42 commits behind with the editor open on it, and `7ef73e1` (the root-lock fix on 44 clips) is
among what it is missing.
