# 2026-11-14 — The goon gets an anim blueprint of his own, and the save that lied (Justin's Mac mini)

- **What we asked for:** go through the GitHub issues another agent made from the roadmap, comment and close
  anything already done, then do the ones assigned to us that are still pending.

- **Prompt(s) we gave the agent:**
  > "Another agent made github issues out of tasks to be completed. Take a look and comment and close on
  > anything we've worked on already. Then do any that were assigned to us that are still pending"

- **What happened:**

  The triage found five issues whose work was finished and merged on Nov 13 and never closed — the whole art
  authoring batch from PR #53 (#42 effects, #43 sounds, #44 screen art, #45 poses, #49 prompts). Each is closed
  with what was verified present on disk and an explicit pointer that the **Unreal half is #52**, because in
  every one of those five cases the art exists and nothing is in the game: `/Game/Game/Audio` holds **3 of 23**
  sounds and there is no `/Game/Game/FX` folder at all.

  Then the real work: **#6, the street goon's body.** A previous lane had put `SK_StreetGoon` on `BP_Goon` and
  wired his 19 montages, and its own log said `saved 43 packages ok True`. Only **21** assets existed in that
  folder. Every locomotion clip, the blend space and — the one that mattered — the retargeted anim blueprint had
  been discarded. This is the trap already written into `CLAUDE.md`: the second `duplicate_and_retarget` of a run
  makes `_SGL1` copies, renames them, and hands back the pre-rename names, so the save saves nothing.

  **What that left behind is the interesting part, because it looks correct from every angle a script can see.**
  `BP_Goon` was pointing at Epic's `ABP_Unarmed` — an anim blueprint whose target skeleton is the *mannequin's*,
  on a character with a 76-bone Meshy Smart Rig. A mismatched anim class does not warn and does not error. The
  mesh reads as correctly assigned, the montage variables all read as correctly assigned, and the goon stands in
  his reference pose and never moves. Read back from the editor it is indistinguishable from a finished job.

  `tools/unreal_goon_abp.py` fixes it by retargeting **one** asset — the anim blueprint — into a *fresh* folder
  with a *fresh* suffix, because retargeting into a folder that already holds assets with your suffix is the
  exact condition that triggers the rename collision. Its locomotion state machine drags its own dependencies
  across with it: the blend space, the idle, and all 16 walk/jog clips. 22 assets, and they are on disk this time
  because the script reads the folder back off the asset registry afterwards instead of believing the batch call.
  It carries Epic's `Slot 'DefaultSlot'` node too, so the 19 `AM_Goon_*` montages already on the Blueprint keep
  playing with no graph work.

  Then the Meshy float, the same bug as the cleaver boss's 113 cm: 16 of the new locomotion clips rode
  **92.5 cm** high, because Meshy's rig parks its root bone at pelvis height in the reference pose while the
  retargeted clips animate it on the floor. `tools/unreal_boss_root_lock.py fix` took all 16 to **0.0**. The
  goon's montage sources and the player's whole `_CWM` set were already locked by earlier lanes and were left
  alone.

  Dead ends worth recording. Two console commands silently did not run: one came out as
  `py /py /Users/...` — the leftover-slash trap this repo had already written down, where `SlateInspector.Type`
  **appends** and returns `true` either way. The documented cure (one `BackSpace`) did not work. `FillForm` with
  `fieldType: textbox` **replaces** the box, which does, and that is now the recipe. Separately the editor went
  unresponsive for **383 seconds** compiling the new anim blueprint; it was at 70% CPU the whole time and the log
  printed nothing, so it looked exactly like the modal-dialog freeze and was not one.

  And the idempotence guard in the new script did not fire on its first re-run: a folder that
  `duplicate_and_retarget` created in an **earlier editor session** is on disk but is **not** in the asset
  registry's path index, so `does_asset_exist` answered "no" for 22 assets that were plainly there. It needs
  `scan_paths_synchronous` first. No harm done — the re-run overwrote cleanly, 22 assets and no `_SGN1` leftovers
  — but the guard only works now because of that one line.

  **Checked in Play-In-Editor**, three live goons on the street:

  | | |
  |---|---|
  | mesh | `SK_StreetGoon`, **76 bones posed** |
  | anim instance | **`ABP_Unarmed_SGN_C`** (was `ABP_Unarmed_C`, the mannequin's) |
  | feet, standing | lowest bone **0.5–0.7 cm** above the street |
  | feet, throughout | lowest bone stays **83–98 cm below the actor origin** in every sample — the −88 the capsule expects, so no float |
  | locomotion | all three walked, 46–51 samples each above 10 cm/s |
  | montages | **9 different clips** played: `AM_Goon_Punch`, `AM_Goon_PunchC`, `AM_Goon_Charged` (the feint), four hit reacts, two deaths |

  One thing nobody has decided, found on the way: a heavy hit react throws a goon to **900 cm/s** and about
  **110 cm into the air** (`actor_z` 92 → 204 on the fatal hit). The feet are correct relative to his capsule the
  whole time — he is genuinely airborne, not floating — but whether being launched that far reads as impact or as
  cartoon is a feel judgement nobody has made. Noted on #11 and #12 rather than tuned, because it is feature
  freeze and it is not a defect.

- **What we learned:**
  - **A mismatched anim class is completely silent.** Mesh assigned, montages assigned, no warning, no error, and
    the character stands in his reference pose. The only check that catches it is reading the **live** anim
    instance's class off a spawned actor in PIE. Reading the Blueprint back cannot.
  - **`SlateInspector.FillForm` replaces a textbox where `Type` appends.** That is the fix for the leftover-`/`
    console trap, which until now had no reliable cure.
  - **The asset registry does not know about a folder another session created** until
    `scan_paths_synchronous`. `does_asset_exist` will tell you 22 assets are not there.
  - **An unresponsive editor at high CPU is working, not frozen.** Check `%CPU` before assuming a modal.

- **Media:** none — this one is numbers off a live pawn, not a picture.
