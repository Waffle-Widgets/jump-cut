# 2026-11-14 — The game opens on a crash (Justin's Mac mini)

- **What we asked for:** a beginning cinematic that starts the game. A peaceful coffee shop, interrupted
  by the car coming through the wall and the driver thrown out of it; the player takes control at that
  moment; a marker that says *go and check on the driver*.

- **Prompt we gave the agent:**

  > "We need a begining cinematic that starts the game. A peaceful coffee shop experience. Interrupted
  > by the car crashing into the cafe, the driver thrown from the car. This should be when the play gains
  > control of the car. There should be a marker telling the player to check on the driver. There's
  > currently some stuff in place for pressing f to gain the first ability and then e to stop some
  > shrapenal. I think it might be simpler and more interest to watch if the car catches on fire after
  > gaining the ability, and then the freeze frame to save the co-worker is for getting the player and
  > worker out of range of the following explosion. After all that is resolved the next indicator should
  > be taking the player out to the street towards the goons"

- **What happened**

  Beat 1 used to begin with the player standing in a cafe that already had a wrecked car in it. Nothing
  explained the wreck; the first thing a judge saw was the aftermath of the scene the pitch is about.
  It now opens on an 11-second cinematic.

  **The shape of it.** `/Game/Game/Cinematics/LS_Beat1_Opening` is a Level Sequence at 30 fps with four
  shots: the quiet cafe (0–4 s), the car coming through the west wall (4–6.2 s), the driver thrown out of
  the cab and landing (6.2–8.8 s), and a settle behind the player before control is handed over
  (8.8–11 s). `BP_OpeningDirector` plays it, holds the player's input down while it runs, and hands
  control back facing the wreck.

  **Everything the camera sees move is a spawnable.** The four cine cameras, the flying car and the
  flying body only exist while the sequence plays, so the sequence owns no level actor and leaves nothing
  behind — `0 sequence spawnables alive` the moment it ends. The *real* wreck and the *real*
  `BP_CrashDriver` are hidden by the director until the moment each one should appear, and revealed
  mid-shot. That split was deliberate: a Sequencer visibility track keys `bHidden` behind a label that
  reads "Visible", and getting that backwards is invisible until someone looks at a frame.

  **The wall had to be put back.** A cafe with a car-shaped hole in it is not peaceful, and the hole is
  modelled into `SM_CafeShell`, so it cannot be hidden. `B1_Cine_WallPatch` is a plain cube in the kit's
  own `M_CafeWall`, standing **4 cm proud** of the wall's inner face — not flush with it, because a
  flush face of a different material is exactly the depth tie that caused #67. The director hides it on
  the frame the car arrives.

  **Three things were wrong and only a screenshot found them.**

  1. The first build left a **`CineDriver` standing bolt upright in mid-air** through the whole peaceful
     shot. Not a Sequencer bug: `b1_opening_cine.py` spawns a throwaway actor, copies it into the
     sequence as a spawnable, then destroys it — and the first run raised on the line *before* the
     destroy. The throwaway stayed in the level as a real, untagged actor that nothing else cleaned up.
     The same failure left a stray `LevelSequenceActor` from `b1_opening_actors.py`. Both are gone, and
     both scripts now destroy their throwaways in a `finally`.
  2. The driver was upright because a **`SkeletalMeshActor`'s SkeletalMeshComponent IS its root**, so
     `set_relative_transform` on it is the actor transform and the transform track overwrote it every
     frame. The lie-down is baked into the keys instead. A rotator is applied Yaw·Pitch·Roll, so actor
     rotation (roll 0, pitch −78, yaw 140) at z = +18 is the *same world pose* as the real body's actor
     yaw 140 plus mesh relative pitch −78 — which is why the hand-off from the thrown body to the real
     one does not jump.
  3. The wall patch rendered as the **grey checker default**, because the cafe's wall material is at
     `/Game/Game/Materials/City/M_CafeWall`, not `/Game/Game/Materials/M_CafeWall`. `load_asset` returns
     `None` for a wrong path and `set_material(0, None)` does not complain.

  **Measuring an 11-second cinematic does not work live.** An MCP round trip to this editor is about
  five seconds, so by the second sample the sequence had finished every time (`t=14.09`, `t=19.07`,
  `t=39.69`, all done). The fix was to stop using PIE for it: open the sequence in the editor, scrub with
  `LevelSequenceEditorBlueprintLibrary.set_current_time`, and read each binding's transform back frame by
  frame (`tools/b1_cine_scrub.py`). That is what proved the tracks were right — the car goes −2400 → −520
  and settles, the body rides in the cab, leaves at 5.10, apexes at z = 250 at 5.40 and lands at
  (−380, 220, 18) rot (0, −78, 140), exactly the real body's pose — while the live captures were still
  showing a stray actor and telling us nothing.

  **What the director does, and what it does not.** On the first tick after the title screen releases
  input it locks input and movement, plays the sequence, counts its own clock, un-hides the wreck at
  4.70 s and the body at 6.45 s, and at 11.0 s unlocks input, sets the control rotation to 172° so the
  camera does not snap, and lights the first objective. The objective marker is one unlit blue sphere
  (`B1_Objective_Beacon`) that the director teleports to whatever the current objective is and bobs —
  one actor for all three objectives rather than three markers to keep in step. Verified live: at the
  end of a run the director reads `done=True time=11.01 objState=1`, the beacon is visible at
  (−380, 220, 238) over the driver, the player reads `inputLocked=False`, and the view target is back on
  `BP_Player`.

  **Not done in this entry, and said plainly:** the fire-then-explosion rework the same prompt asks for
  is not built — beat 1 still uses the shrapnel hazard. Objective states 2 (get her clear) and 3 (out to
  the street) exist in the director and have their positions set, but nothing advances past state 1 yet;
  that lands with the hazard rework, because the two are the same change. **Nobody has played this.**
  Every number above is a script reading live actors or scrubbing the asset, plus frames I looked at
  myself.

  **One blemish worth knowing about:** the crash rubble is modelled into `SM_CafeShell`, so there are
  broken blocks on the floor during the peaceful shot, before anything has broken. Hiding them needs a
  kit change (rubble as its own mesh), which is the city lane's, not this one's.

- **What we learned**
  - A throwaway actor that outlives a failed script is a **real actor in the level**, and nothing else
    removes it. Destroy throwaways in a `finally`, never on the happy path.
  - `ASkeletalMeshActor`'s mesh component is its root, so its relative transform is the actor transform.
  - `/Game/Game/Materials/City/` is where the city kit's materials are. A wrong asset path is silent.
  - To check a Sequencer track, **scrub the asset in the editor**; a cinematic shorter than two MCP round
    trips cannot be sampled live.

- **Media:**
  ![the peaceful cafe, before](../media/2026-11-14-beat1-opening-peaceful-cafe.png)
  ![the driver thrown from the car](../media/2026-11-14-beat1-opening-driver-thrown.png)
