# Latte mini game: hand-off between GameStation (builder) and M Station (maker)

*Written Sun Nov 15, 1:05 PM Pacific, on GameStation. Branch: `Gamestation/latte-art`. Delete this file once the
branch is merged.*

## The one rule
**M Station commits source files only (`Art/`, `docs/`, scripts). GameStation imports them into Unreal and commits
every `.uasset`.** Both PCs use the same GitHub account, so Git LFS locks cannot tell us apart: this rule is what
keeps two computers off the same binary file.

## Getting the branch on M Station
```bash
git fetch origin
```
```bash
git checkout Gamestation/latte-art
```
```bash
git pull --rebase --autostash
```
Push straight to the same branch. Pull with `--rebase --autostash` first every time; GameStation pushes often.

## Where things go
| What | Folder | Notes |
|---|---|---|
| Models (FBX) | `Art/Blender/export/Latte/` | one FBX per model, one material slot each |
| Pictures (PNG) | `Art/UI/Latte/` | |
| Blender scripts | `Art/Blender/` | a NEW file, e.g. `latte_customer.py` |

**Do not edit these, GameStation is changing them:** `Art/Blender/latte_kit.py`, `Art/Blender/jumpcut_city_kit.py`,
everything named `tools/latte_*.py`, and anything under `JumpCut/Content/`.

## What the models have to match, if you are replacing one
The game moves these by code, so the origin and the facing matter more than the shape. Build in metres, export with
forward `-Z`, up `Y`, scale 1 (Blender `+Y` comes out as Unreal `-Y`).

| File | Origin | Size / facing |
|---|---|---|
| `SM_LatteCup.fbx` | centre of the **coffee surface** (z 0) | inner wall radius 5.8 cm at z 0, rim at +0.9 cm, base at -8.3 cm |
| `SM_LatteSaucer.fbx` | same point as the cup | top of the saucer at about -8.4 cm |
| `SM_LattePitcher.fbx` | the **spout tip** | exported already tilted 42 degrees to pour, spout toward Blender `+Y` |
| `SM_LatteStream.fbx` | bottom centre | 1 cm tall, 1 cm across, at least 12 rings up its height (the material sways it) |

A new model that nothing replaces (a customer, a napkin, a tip jar) has no such limits: say where it should stand.

## What is still missing, in order of how much it would help
1. **A customer.** Right now the cup just disappears and a caption says a customer took it. A rigged character on the
   existing `SK_CafeWalker` skeleton would let them walk up and take it.
2. A nicer cup, saucer and pitcher than the profile-built ones in `latte_kit.py`.
3. A picture for the order ticket.

## Telling GameStation
After each push, send GameStation's chat: the file names, what each one is, and where it should go in the cafe.
GameStation imports, places, tests in Play, and commits the `.uasset` files.

## Merging to `main`
The pull request from this branch is opened by GameStation. It merges only after a person has played the shift from
the title to the cutscene. GameStation then packages the build.
