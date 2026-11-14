# 2026-11-14 — The sounds and the effect sheets come into Unreal, and a PNG that bit twice (Justin's Mac mini)

- **What we asked for:** after closing the issues already done and finishing #6, do the rest of what was
  assigned to this machine. That is #52 — the Unreal half of all the art M Station made on Nov 13.

- **Prompt(s) we gave the agent:**
  > "Another agent made github issues out of tasks to be completed. Take a look and comment and close on
  > anything we've worked on already. Then do any that were assigned to us that are still pending"

- **What happened:**

  **The game has 23 sounds in it now instead of 3.** `Art/Audio/*.wav` copied into
  `Content/Game/Audio/` and every one imported itself within seconds — `.wav` auto-import is on in this
  project and it simply works. That is section 1 of #52's asset half done: `/Game/Game/Audio` went from
  **3 assets to 23**.

  **The effect sheets are in too** — nine SubUV textures in a new `/Game/Game/FX/Textures`, which did not
  exist at all before today.

  **PNGs do not auto-import, and finding that out cost the session.** Seven UI textures sat in
  `Content/Game/UI/Textures/` for 35 seconds and produced exactly nothing, so
  `tools/unreal_import_ui_fx.py` was written to import them with an explicit `AssetImportTask` and set
  the two properties #52 asks for: `TEXTUREGROUP_UI` and no mipmaps. No mipmaps matters as much for the
  sprite sheets as for the screens — a mipped sheet bleeds neighbouring *frames* together, so the
  explosion grows a halo of the frame beside it.

  **Then the same PNGs broke the import, for a reason that reads as a clean failure.** The run came back
  "imported 9, failed 7": all nine FX sheets fine, all seven UI textures reporting *"import produced no
  assets"*. They had not failed. Importing a file that is **already inside `Content/`** makes the task
  return an empty `imported_object_paths` while still creating the texture in memory — an unsaved success
  wearing a failure's clothes. The FX sheets were imported straight from `Art/FX` and never touched that
  path. The tell was that `describe()` at the end of the same script happily reported `1920x1080` for
  textures that `does_asset_exist` had just said were not there: `does_asset_exist` answers **False** for
  an imported-but-unsaved asset, which also silently defeated the script's own "already here" branch.

  **And then clearing up made it worse.** Deleting the stray PNGs out of `Content/Game/UI/Textures/` woke
  the editor's auto-reimport watcher: `AssetReimport: Attempting to delete T_Icon_Rewind (its source file
  has been removed)`. That is the **Delete Assets** modal this repo already has a warning about, and it
  freezes the MCP until a person answers it. The source files went straight back, which removes the cause
  but cannot dismiss a dialog that is already up. **The editor has been pinned at ~185% CPU with a silent
  log since 03:45 UTC and stopped answering the MCP.** It needs one **Escape** at the keyboard — Escape
  keeps the assets.

  **Nothing is at risk from that, and it is worth saying why rather than hoping.** Everything this session
  produced is saved and committed: the goon's 22 assets, the 23 sounds, the nine FX sheets. The only
  unsaved things in that editor are the seven UI textures — which take 30 seconds to remake from
  `Art/UI` with the script that is now in the repo — plus four Blueprints and three city meshes another
  lane left dirty before this session started and which this session never touched.

  **What this did not get to:** the sounds are *in the project* and not one of them is *wired to an
  event*, so the build is still silent. Same for the effect sheets: imported, no SubUV materials, nothing
  hung on a punch or an explosion. Those are the parts of #52 that need graph edits across ten
  Blueprints, four of which are currently dirty from another lane, and the editor stopped answering
  before any of it could start.

- **What we learned:**
  - **`.wav` auto-imports in this project; `.png` does not.** The `bShowImportDialog=False` setting makes
    dropped FBX and WAV import themselves. A dropped PNG does nothing at all and needs an import task.
  - **Never copy an image into the destination Content folder before importing it.** The import returns
    no object paths and looks like a failure while quietly creating an unsaved asset. Import from `Art/`.
  - **`does_asset_exist` is the wrong test for "is this already here"** — it is False for an
    imported-but-unsaved asset. Use `load_asset`.
  - **Removing a source file out of `Content/` is as dangerous as deleting the asset.** The reimport
    watcher raises the same modal. Leave the source beside the asset, which is what
    `Content/Game/Audio` has always done with its `.wav` files.
  - **A wedged editor at ~185% CPU with a silent log is not the same as the 383-second anim-blueprint
    compile at 70%.** High CPU alone does not mean "working" — pair it with whether the log still ticks.

- **Media:** none — `screencapture` has no screen-recording permission on this Mac, which is also why the
  dialog could not be confirmed by looking at it.
