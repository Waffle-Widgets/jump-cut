# 2026-11-15 — The opening waits for the title (Justin's Mac mini)

- **What we asked for:** while wiring the sounds, a scripted run found that the beat 1 opening cinematic was
  already playing **behind the title screen**. With the title up, the director's clock was at 2.35 s. A
  player who sat on the title missed the car crash, and with the new crash sound they would have *heard* it
  behind the title.
- **Prompt(s) we gave the agent:** *"Fix item 1 and merge"* (Justin, 10:12 AM Pacific).

## What happened

**The cause was a race on the very first frame.** The director starts the opening as soon as it sees the player's
input unlocked. The title screen locks input, but it does that from the game mode's tick, and on the first frame
the director got there first. Once the opening starts it locks input itself, so from then on everything looked
consistent. The sequence was not auto-playing on its own: `auto_play` is off, and the director calls Play inside
`CineBeginOpening`, so the clock and the sequence always started together, just too early.

**The fix is one gate.** A new helper, `CineBeginWhenPlaying`, asks the game mode whether play has started
(`FlowState == 1`, which `JumpCutStartPlay` sets when the title is dismissed). Only then does it call the existing
`CineBeginOpening`. If there is no Jump Cut game mode, it starts as before. In `CineDirectorStep` the one call to
`CineBeginOpening` was replaced by a call to the helper: same wires in, same wires out, and the old node deleted.
The node count is 356 before and after, with 41 reachable, and `CineBeginOpening` is no longer called from
anywhere else in that graph. Nothing else changed: the scene is still set up at BeginPlay (car hidden, wall whole,
fire out), so the world behind the title is the calm cafe.

## The test, by script in Play mode

- **Title on, held for 7 s:** director clock **0.0**, sequence **not playing (frame 0)**, crash flag unset,
  view on the player, title showing.
- **Title dismissed through `JumpCutStartPlay`** (what R calls): about 5.6 s later the clock read **5.66 s** and the
  sequence frame **169** (5.63 s at 30 fps). The two started together, from 0, and are in step. The view was on
  `CineCam_B_Crash`.
- **About 12 s after that:** the opening was done, the crash flag was set, the **objective had advanced to 1**, the
  view had been **handed back to the player** and input was unlocked.
- **Title off (`ShowTitleOnStart` false):** at 1.40 s of world time the clock read **1.24 s** and the sequence
  frame **37**, so it starts immediately, as before. Put back to **true** and read back true.
- No errors in the log. The only warning is the Mac's audio device line at each Play start
  (`LogAudioMixerAudioUnit: Error querying Sample Rate`), which was there before.

![The title holding the world still: the clock reads 0 behind it](../media/2026-11-15-title-holds-opening.png)

The capture shows that the title card is opaque, so nothing of the scene shows behind it while the player waits.

## Siblings checked

Nothing else starts its clock behind the title. The coworker's fuse waits for the player to hold Freeze Frame. The
fire, wall and car are driven by the director, which now waits. The boss sleeps until his gate. The goon spawners
place their goons at BeginPlay, but they wake by distance and the player is inside the cafe.

## What is not tested

- A real **R key press** (the script calls `JumpCutStartPlay`, the function R calls).
- **Ending -> R -> whole-level reload -> title** was not run in this round. By the code it reloads the map, so the
  title shows and the opening waits again. **Lose -> restart from checkpoint** does not replay the opening,
  because `CineDone` stays true (that path was run in the sound test).
- A **Windows build**, and how any of it sounds or feels to a person.

## What we learned

- **"Locked input" was being used as "the game has started", and on frame one they are not the same thing.**
  Ask the thing that owns the state (the game mode's `FlowState`) instead of inferring it from a side effect.
