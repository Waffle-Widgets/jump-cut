# 2026-11-12 — The anime look goes on the level, a walk that was broken on disk, and an audit of the whole run (GameStation, the builder PC)

- **What we asked for:** nothing new. This is the same builder run, carrying on from the Team Owner's afternoon
  message quoted in [the previous entry](2026-11-12-freeze-frame-first-rewind-parked-first-full-run.md): "we will be
  moving forward with the cell shaded anime look so make sure we have that ready for when we need it". That run's
  method (a lead, builders, checkers, a ledger) also ends with an audit by a fresh agent, which is the third part of
  this entry. Thursday evening, Pacific.
- **Prompt(s) we gave the agent:** none since the previous entry. No person has typed anything new into this run.
- **What happened:**
  - **The cel shader went onto the game level (packet A3).** A builder put the anime post-process from the cafe demo
    on `Lvl_JumpCut` (`PP_AnimeLook` with its own settings, `MI_AnimeLook_JumpCut`) and marked the player, the goons
    and the boss so the shader knows they are characters. A separate checker measured it:
    - Characters get flat tones, drawn shadow shapes and dark outlines. Goons that respawn are marked too.
    - The grey boxes barely change: thin lines only. Characters stay bright when they stand in a building's shade.
    - It is the same technique as the cafe demo, **but not yet the same style**: the level has none of the demo's
      exposure, colour grading or lighting.
    - No measurable frame cost in the editor: 4.23 ms with the look on against 4.16 ms off, inside the noise.
    - The HUD and the screens are untouched (their pixel colours are identical with the look on and off), and a
      scripted run still wins, in 26.3 s.
  - **The checker failed the packet's first check, and it was right to.** The check said the cafe demo must still load
    without errors after the merge. It didn't: the demo hero's walk (the blend space `BS_Idle_Walk_Run_CW`) pointed at
    17 animations named `*_CW1` that don't exist; the files are called `*_CW`. The cause, from the editor's log: the
    script that copies the mannequin's animations onto our hero had been run a second time over its own output. That
    made `_CW1` copies, saved the walk while it still pointed at them, and only then renamed the copies to `_CW`.
    The editor that did all this never noticed, because in its own memory the walk followed the renamed animations
    perfectly. Only a second, fresh editor process reading the files from disk saw the broken links. **The machine
    that made the asset is the worst place to test it.** A builder fixed it (packet A3b) by re-saving the walk from
    the editor session that still had the right links in memory, then loaded the cafe in a separate headless editor:
    0 errors. A separate checker then confirmed it: the file on disk named the `_CW1` animations 34 times before and
    0 times after, a headless editor loaded the walk, the hero and the cafe with 0 errors and 0 warnings, and nothing
    else in the hero's folder changed. A one-line fix (re-save everything at the end) was added to the copying script,
    but it **has not been run yet**. And nobody has watched the hero idle, walk and jog in Play mode: that needs a
    person.
  - **The final audit.** A fresh agent that saw none of the run read the ledger against the repository and against
    the owner's own words ([`FIRST_BUILD_AUDIT.md`](../FIRST_BUILD_AUDIT.md), kept unedited). The sharpest things it
    found:
    - **Our previous entry said "The anime look is ready." It was not.** At that point the look wasn't on the level,
      its first check then failed, and it had never been tried on one of M Station's anime characters. **This entry
      is the correction** to [the previous entry](2026-11-12-freeze-frame-first-rewind-parked-first-full-run.md),
      which stays as it was written.
    - **The branch had fallen three commits behind `main` again**, and those commits were the very characters the
      look is for, plus the art-style decision.
    - **The run-through was "verified" by the same agent that ran it.** Only a different checker's pass is supposed
      to count.
    - **Three "done means" lines were quietly reinterpreted:** two "the HUD shows the icon and cooldown" lines were
      passed as "the variables are right, there is no HUD yet", and one lose-screen check could no longer be run as
      written once Rewind was switched off.
    - **Steps that set up the level lived only in scratch scripts that Git ignores** (the checkpoint's wider trigger,
      the boss's links to the gates, the door hand-over, all of the anime look's editor steps). Re-running the level
      layout script would have silently undone them.
    - **The list of tuning numbers was a placeholder.**
    - **Nothing had been pushed**, against the lesson our own previous entry wrote down.
    - One small caption error in the previous entry: the Freeze Frame picture shows **three** orange goons, stopped,
      not "two goons walking".
  - **What was done about it today:** `main` was merged into the branch again (the three rigged characters and the
    art-style decision are on it now); the walk was fixed and checked (A3b); the four scratch scripts were
    copied into `tools/` with a note on what they are, and the layout script got a loud "do not re-run" warning that
    names them; the pitch, the roadmap, the design note (a "what changed" box at the top and a completed tuning table),
    the pre-jam declaration, the credits and the characters file were brought into line with the decisions; and the
    lead corrected the ledger's stale lines, with what was done listed in its "After the audit" section.
  - **What was not done:** **nobody has played any of it yet.** The game is 25 to 27 seconds long at default numbers
    and far too easy. The plaza boss (a big bruiser whose freeze is switched off) has no place in the new design yet:
    that is a team decision. The look has still never been tried on one of M Station's anime characters. And the
    branch is **not pushed** until the Team Owner says so.
- **What we learned:**
  - **Test an asset somewhere other than where it was made.** The editor that broke the walk had the right answer in
    memory and could not see the problem. A second, fresh process found it in six seconds.
  - **A word like "ready" needs a check behind it.** Our own entry claimed it before the check ran. An auditor who
    did none of the work, reading only the books and the files, caught that and six other things the team that did
    the work could not see.
  - **If a step changed the level, its script belongs in Git,** not in a scratch folder that only one computer has.
- **Media:** both are captures from the game camera in Play mode, with the look on and off side by side.
  - ![The street from behind the white player, with the anime look on (left) and off (right): three orange goons around the player (one half hidden behind him), a red ball warning of a punch, the plaza's yellow gates at the far end and the violet boss small in the distance. On the left the characters have dark outlines and flat shadow shapes; the grey walls look almost the same in both halves](../media/first-build-a3-anime-street.png)
  - ![The plaza: the violet boss walking towards the white player in front of the yellow exit gate, a red ball above the boss warning of his punch. Look on (top): outlines and flat shadow shapes on both characters. Look off (bottom): the same scene with soft, ordinary shading](../media/first-build-a3-anime-boss.png)
