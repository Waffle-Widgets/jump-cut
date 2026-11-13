# 2026-11-12 — The boss ladder is settled, and the mob boss stops giving away the wrong power (GameStation)

- **What we asked for:** the Team Owner settled the order of the bosses and which power each one hands over, and
  asked us to generate more models at the same time, splitting the work across machines as we saw fit.

- **Prompt(s) we gave the agent:** the actual words were

  > First boss is the car crash that gives Freeze Frame. The second boss is the Mob Boss with the cleaver and the
  > Splice power. The third boss if we have time would be the Stunt Double power. If we can generate models at the
  > same time that would be good too, feel free to split up the work between machines as you see fit.

- **What happened:**

  The build had a character who looked like one boss and behaved like another. Since the evening before, the plaza
  boss wore `SK_CleaverBoss` and carried a cleaver — he *was* the Splice mob boss — but his `BossHandOverPower`
  still called `PlayerGrantFreezeFrame`, because nobody had said which power he gives. That question had been
  sitting in `ROADMAP.md` under *Still to decide* for two days. This prompt answered it.

  Before changing anything we checked the thing that could have broken: if the mob boss stops granting Freeze
  Frame, can a player reach the plaza without it? The design note said two markers inside the cafe grant it, but a
  design note is not the level. We queried the six `BP_SceneMarker` actors in `Lvl_JumpCut` directly and read
  `MarkerGrantsFreezeFrame` off each one. Two are true: one at **(-300, 330)**, the driver, and one at
  **(560, 0)**, the cafe door. The other four — including both plaza markers at x = 8120 and x = 10220 — are
  false. Both granting markers are inside the cafe, so the boss's grant really was the redundant one, and
  removing it costs the player nothing.

  The change itself was small and went in one place. `BP_Player` gained a `HasSplice` bool and a
  `PlayerGrantSplice` function — one node, `SetHasSplice true`, copied from the shape of `PlayerGrantFreezeFrame`.
  Then `BP_BossFreeze.BossHandOverPower` was re-pointed to call it. `EventEnemyDefeatedHook` calls
  `BossHandOverPower` on **both** branches of its `IsValid` check (gate valid and gate not valid), so that single
  function was the only thing that needed editing — a good argument for the previous author having pulled the
  hand-over out into its own function instead of leaving it inline.

  Two things nearly went wrong and are worth writing down.

  **The `.uasset` files are `lockable` in `.gitattributes`, and `BP_BossFreeze.uasset` was read-only on disk.**
  Saving it from the editor would have silently done nothing — no error, no dialogue, just a file that never
  changed. `git lfs lock` on both Blueprints made them writable first. `BP_Player.uasset` happened to already be
  writable, which is exactly the kind of inconsistency that makes this failure hard to notice: half your saves
  work.

  **The DSL read-back looked wrong and wasn't.** After the edit, `read_graph_dsl` printed the new call as
  `(|PlayerGrantSplice ...)` — a blank class prefix, where the line above it still said
  `(Class|BPPlayer|PlayerFreezeBreak ...)`. That looks like a dangling call to a function that didn't resolve. It
  isn't: inspecting the node showed its `self` pin typed as **BP Player Object Reference** and wired to the
  `PlayerRef` variable, and its exec pin wired from the `PlayerFreezeBreak` node. The blank prefix is just how the
  printer renders a call into a class that was compiled moments earlier in the same session.

  On the second half of the ask — generating models at the same time — the honest finding is that the machines
  are not interchangeable. GameStation has **TRELLIS.2 and Pixal3D installed with their weights cached**, and an
  RTX 5090, so it can make 3D models locally and for free. What it does **not** have is ComfyUI or the
  signed-in browser profile, so it cannot make the *reference pictures* that image-to-3D needs. Those live on
  M Station. And from this chat, M Station can be sent files but cannot be told to run anything. So the work was
  split three ways **on GameStation**: this lane in the Unreal editor, one lane running TRELLIS on the 5090 from
  a reference sheet already committed to the repo, and one lane writing the design and the image prompt for the
  Stunt Double boss, who has no artwork at all.

- **What we learned:**

  - **Check the level, not the design note.** The note said two cafe markers grant Freeze Frame. It was right —
    but it was a two-day-old claim about a file that three agents had edited since, and the whole safety of this
    change rested on it. Reading `MarkerGrantsFreezeFrame` off the six live actors took one call.
  - **A lockable LFS asset that is already writable will hide the bug.** Check every file you intend to save, not
    one of them.
  - **A blank class prefix in the Blueprint DSL is not evidence of a broken call.** Judge a node by its pin types
    and connections, not by how the text printer renders it.
  - **Granting a power is not implementing one.** `HasSplice` is set and nothing reads it. The ladder is true in
    the docs and in the hand-over, and the ability itself is still Friday's work. Saying so is the point of this
    entry.
