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

  **And then clearing up looked like a disaster and was not one.** Deleting the stray PNGs out of
  `Content/Game/UI/Textures/` woke the editor's auto-reimport watcher: `AssetReimport: Attempting to
  delete T_Icon_Rewind (its source file has been removed)`. That is the **Delete Assets** modal this repo
  has a warning about, which freezes the MCP until a person answers it. The editor then sat at **~185%
  CPU with a completely silent log** and stopped answering the MCP for several minutes, and the first
  conclusion drawn — written into a commit message and into `ROADMAP.md` before it was checked — was that
  a modal was up and somebody had to press Escape.

  **That was wrong, and the way it was settled is the useful part.** `screencapture` has no
  screen-recording permission on this Mac and `osascript` has no assistive access, so the screen could not
  simply be looked at. `sample <pid>` could: the game thread's stack was
  `FAutoReimportManager::Tick -> FAutoReimportManager::Idle`, which means the thread was **ticking**, not
  parked inside a modal's `RunModal`. No dialog. The source files had already been put back, the watcher
  was just working through them, nothing was deleted, and the MCP answered again a couple of minutes later.
  The seven UI textures then imported, configured and saved on the next run — `TEXTUREGROUP_UI`,
  no mipmaps, all seven on disk.

  **One more trap on the way out.** An MCP call that times out on the client still *ran* in the editor, so
  the `FillForm` that "failed" had already put its text in the console box. The next `FillForm` appended to
  it and the command came out as the path twice — `py <path><path>` — and silently did nothing. The
  reliable recipe is `FillForm` with `""` to clear, then `FillForm` the command, then `PressKey("Enter")`,
  then read the `Cmd:` line in the log to confirm what actually ran.

  **What this did not get to:** the sounds are *in the project* and not one of them is *wired to an event*,
  so the build is still silent. Same for the effect sheets and the screen art: imported and configured, but
  no SubUV materials, nothing hung on a punch or an explosion, and the title/win/lose textures are not in
  their widgets. Those are the parts of #52 that need graph edits across ten Blueprints, four of which are
  currently dirty from another lane.

- **What we learned:**
  - **`.wav` auto-imports in this project; `.png` does not.** The `bShowImportDialog=False` setting makes
    dropped FBX and WAV import themselves. A dropped PNG does nothing at all and needs an import task.
  - **Never copy an image into the destination Content folder before importing it.** The import returns
    no object paths and looks like a failure while quietly creating an unsaved asset. Import from `Art/`.
  - **`does_asset_exist` is the wrong test for "is this already here"** — it is False for an
    imported-but-unsaved asset. Use `load_asset`.
  - **Removing a source file out of `Content/` wakes the reimport watcher.** Put it back, or better, leave
    the source beside the asset — which is what `Content/Game/Audio` has always done with its `.wav` files.
  - **`sample <pid>` tells a busy editor from a blocked one, and `%CPU` does not.** A stack in
    `FAutoReimportManager::Tick` is a thread that is ticking; a stack in `RunModal` is a dialog. Guessing
    from CPU and a silent log produced a confident, committed, wrong answer.
  - **A timed-out MCP call still ran.** Clear the console box before the next command, and verify against
    the `Cmd:` line rather than the tool's return value.

- **Media:** none — `screencapture` has no screen-recording permission on this Mac, which is why the
  question had to be settled from a stack sample instead of a look at the screen.
