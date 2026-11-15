# The float came back with the new legs

*Sun 15 Nov 2026, about 12:10 AM Pacific — GameStation · found and fixed by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the models looking right and moving like normal people, before any new animation.

- **Prompt we gave the agent:**

  > Yes, continue. We need the models looking right. We also need to start working on animations once the models
  > look right. The models should look and move like normal people.

- **What happened:**

  While checking how the player moves before authoring a new idle, the agent logged bone heights in the running
  game. Standing was fine. **Running at full speed, his feet were 104 to 109 cm above the floor**: root bone at
  94 cm, hip at 173 cm. The player was floating a metre in the air whenever he ran, and so was every punch.

  This is the float bug from Nov 13 and Nov 14, back for the third time. The cause is the same one line: a clip
  with root motion on locks its root to the **reference pose**, and on a Meshy rig the reference-pose root is at
  pelvis height, so the whole body rides up by 90 cm. It was fixed on 44 clips on Saturday at 12:06 AM. Then at
  10:17 PM the player's 20 root-motion clips (16 walks and jogs, 4 attacks) were rebuilt to correct his wide
  stance, and a freshly retargeted clip comes back with the lock on `RefPose` again. Nothing in the retarget
  script sets it, and the stance check that followed measured angles and widths, not height.

  **Measured before touching anything** with the team's own `tools/unreal_boss_root_lock.py`: of 148 clips, 20
  rode 80 to 91 units high, all 20 the player's `_CWM` set. The boss's 18, the goons' 24 and the older set of 16
  were fine.

  **Fixed** with the same tool's `fix` mode: 20 clips set to `AnimFirstFrame`, saved, none riding high after.

  **Checked in the running game:** at 555 cm/s his feet are now at 14 and 19 cm (ankle height) and his hip at
  83 cm.

  **Made to stay fixed:** `tools/unreal_retarget_meshy.py` now sets the lock on every root-motion clip in the
  folder as it saves, so the next retarget cannot bring the float back.

- **What we learned:**
  - A fix applied to an asset by hand is undone by whatever regenerates that asset. Put the fix in the generator
    the same day, or it will come back the next time the generator runs.
  - A check only finds what it measures. The stance check proved the legs were right and could not see that the
    whole body was a metre too high.
  - Log `actor z` beside the bone heights whenever a character moves in a test. It took one line to find this.

- **Not done:** nobody has played it with a keyboard since the fix. The attacks were fixed by the same change
  but were not re-measured in the running game, only by the tool.
