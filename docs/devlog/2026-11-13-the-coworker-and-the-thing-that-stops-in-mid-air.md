# 2026-11-13 — The coworker, and the thing that stops in mid-air (GameStation)

- **What we asked for:** the Team Owner changed how we pick work. Not "what is most interesting", but
  **the order a player meets it**. Beat 5 had just been built; beats 1 to 4 had not been checked against that
  rule. In his words:

  > We should work on things in order of how we are playing through the game, so if we still have work to be
  > done on earlier beats we should do that.

  He also settled two things about beat 5 in the same message, written down in `ROADMAP.md` and not built here
  (see "What we did not build", below).

- **What the order turned up.** Beat 1 is the first thing a player does and the only beat whose *lesson* is
  written down: the roadmap says an explosion sends shrapnel at a coworker, and "the action button teaches the
  player to use Freeze Frame to save the coworker." None of it existed. There was no coworker — not in
  `CHARACTERS.md`, not in the level, not as a Blueprint — no shrapnel, and no action button of any kind; the
  player had punch, rewind and freeze and nothing else. The cafe handed you Freeze Frame and then asked you to do
  nothing with it until the street fight.

- **What we built.** Two Blueprints and one placed actor.

  - **`BP_Shrapnel`** — the thing in the air. A red bar that flies at a fixed world point at 260 cm/s and
    destroys itself when it arrives or after 14 s. It asks the player one question every tick:
    `BP_Player.FreezeFrameActive`. While that is true it does not move, does not turn, and **does not age** — its
    life timer is frozen too, so a player who stops time does not lose the beat by taking too long.
  - **`BP_Coworker`** — the person, and the whole scene. She owns the beat rather than scattering it: a trigger
    sphere (650 cm) arms it, but only once the player actually has Freeze Frame, so picking the power up is what
    starts the danger. She spawns the shrapnel at the crashed car, watches its distance to her own chest each
    tick, and lights a cyan sphere over her head exactly when a rescue would succeed.
  - **`Coworker_Cafe`** in `Lvl_JumpCut` at (300, -250), between the counter and the cafe door, so she is on the
    way out and not a detour.

- **The lesson is enforced, not hoped for.** `RescueRequiresFreeze` is **true**: the prompt does not light and
  the action button does nothing unless time is stopped. We argued about this. With 3.1 s of flight the player
  *could* sprint to her without freezing, learn nothing, and still win — and beat 1 exists to teach the power.
  The flag is instance-editable, so a playtest that finds it patronising can switch it off without a code change.

- **Failure is a loop, not a death.** If the shrapnel reaches her she falls over (mesh tipped 80°,
  `RescueTriesUsed` goes up), and 2.5 s later she stands up, returns to her spot and a fresh piece of shrapnel
  leaves the car. A tutorial that can strand you on its first lesson is worse than one you can fail twice.

- **The action button.** There wasn't one. `BP_Player` now polls **F** and **Gamepad_FaceButton_Top** in
  `PlayerTickInput` beside the existing punch/rewind/freeze polls, with the same edge detection, and calls a new
  `PlayerInteract` — which checks `PlayerCanAct` and offers the rescue to every `BP_Coworker` in the level. The
  coworker decides whether it lands; the player does not need to know what interacting means.

- **What we checked in Play-In-Editor, and how.** Not by reading the Blueprint back.
  - Standing in the cafe with no power, the scene stays asleep: `RescueStarted` false.
  - Teleported to the driver's marker; the marker granted Freeze Frame. Still asleep — she is 834 cm away, past
    the 650 cm trigger.
  - Walked into the trigger. Shrapnel spawned **at (-470, 0, 185)**, the car, and was already moving on the next
    read.
  - Left alone, it hit her **twice**: `CoworkerDown` true, `RescueTriesUsed` 2, retry timer counting down. The
    loop works.
  - With `FreezeFrameActive` true, the shrapnel sat at **exactly (-470, 0, 185)** across two reads seconds apart,
    `ShrapnelStopped` true and `ShrapnelLifeLeft` still 14.0 — it had not aged a frame.
  - The rescue moved her from **(300, -250, 0)** to **(300, 70, 0)** — her spot plus the 320 cm safe offset — with
    `RescueDone` true and `RescueTriesUsed` still 0.
  - Released the freeze: the shrapnel finished its flight to the place she used to be and destroyed itself.
    She was never hit.

- **One honest note about that test.** The player's own key presses cannot be driven from here, so for the test
  we made `FreezeFrameActive` instance-editable and briefly had the coworker call her own rescue when it was
  legal, instead of waiting for F. Both changes were reverted and both Blueprints recompiled with warnings
  treated as errors afterwards, and the reverted graph was read back to prove it. What that means: the mechanic
  is verified, **the F key itself is not** — nobody has pressed it.

- **What we did not build**, and why it is not in this entry's commit: the Team Owner also decided that Splice
  should let the player get **past** the beat-5 attack stand-in to reach the boss, and that the attack stand-in
  should disappear on a timer once it has nothing in range to fight. Both are beat-5 work, and the Splice one
  needs Splice, which is still unbuilt and still gates nothing. Under his own new rule they wait: beat 4 is the
  earlier beat, and beat 4 is where Splice actually has to exist.

- **What we learned.** *Play order is a better work queue than interest order.* Beat 5 got a boss power and a
  stand-in system last night while beat 1 — the first thirty seconds, and the only tutorial in the demo — had no
  coworker, no shrapnel and no action button. Nobody hid that; nobody had looked in that order.

- **Still missing:** she is a green box. She has a written design and a prompt (`GEM2-COWORKER`) and no model.
  And a floating cyan sphere is not a "press F" label — the HUD has no prompt text.
