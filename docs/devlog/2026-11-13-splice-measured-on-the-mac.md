# 2026-11-13 — Splice measured on the Mac, and the test that kept killing the tester (Justin's Mac mini)

- **What we asked for:** make sure Splice is working properly, finish the housekeeping, and go back over anything
  that was skipped or missed on the last run, before starting beat 4.

- **Prompt(s) we gave the agent:**
  > "Make sure splice is working properly. And complete any housekeeping and revisit anything that was skipped or
  > missed from the last run before beat 4"

- **What happened:**

  The last run rebuilt Splice on this Mac and pushed it, but signed off with an honest hole: *"nobody has pressed
  Left Shift"*. The blink distances in the docs were GameStation's numbers, carried over on the argument that the
  graph was pin-for-pin identical. The note went further and said the power **could not** be re-measured here,
  because the Splice variables are not instance-editable and the editor's script sandbox has no `unreal` module.

  That turned out to be wrong, and it was wrong in a useful way. There is no MCP tool that calls one of our own
  Blueprint functions — but you don't need one. A temporary instance-editable `DebugSplice` bool plus a single
  `if` at the end of `PlayerTickInput`, which clears the flag and calls `SpliceStart`, drives the real function on
  the live Play-In-Editor pawn. The same trick had already been used for beat 1's **F** key; nobody had connected
  it to this problem.

  Two things fought back before any number was trustworthy.

  **The title screen.** Nothing moved, and the pawn read `InputLocked: true`. Setting that property directly
  *appeared* to work — no error — and then read back `true` anyway. (`ObjectTools.set_properties` only writes
  instance-editable variables; a non-exposed one is refused by name, but an exposed one can silently not take.
  That is now in `CLAUDE.md`.) `SlateInspector.PressKey` can't dismiss the title either: it presses and releases
  inside one call, and the title's R is an `IsInputKeyDown` poll on the game-mode tick, so the press never spans a
  tick. The door was `ShowTitleOnStart = false` on `BP_JumpCutGameMode` — with it false, `JumpCutFlowTick` calls
  the game's own `JumpCutStartPlay`, which is how every run below reached `FlowState` 1 with input genuinely
  unlocked. That is the real start path, not a bypass of it.

  **The test goon kept killing the tester.** Three bodies were placed 250 cm in front of the player to measure the
  blink passing through them. The goon woke up, chased the player the length of the street, and beat him to
  `Health: 0`. `PlayerCanAct` is false when `IsLost` — so the next blink measured **0 cm**, which looks exactly
  like a broken power and was nothing of the kind. One earlier reading (240 cm instead of 600) came from the same
  fight and was thrown away rather than written down. The fix was to delete the two bodies that chase and keep
  `BP_StuntStandIn`, which with `StandInFights` false genuinely stands still.

  With that cleared, six measurements, each driving the real `SpliceStart`:

  | Test | Measured | Expected |
  |---|---|---|
  | No power (`HasSplice` false), input unlocked | **0.0 cm**, cooldown untouched | 0 |
  | Open ground from x=1000 | **600.0 cm** (→ 1600.0) | 600 |
  | Wall 500 cm ahead (line trace = 500) | **455.0 cm**, x drift **0.0** | 455 = 500 − 45 |
  | **Through the attack stand-in** at 250 cm | **600.0 cm**; stand-in **not shoved** (0.0) | 600 |
  | Cooldown written by a blink | **19.44 s of 30** left after | > 0 |
  | Fire again during that cooldown | **0.0 cm**, **8.54 s** left | 0 |

  To prove the cooldown is actually *written* rather than inferred from the graph, `SpliceCooldown` was raised
  1.2 → 30 s for one run, because at 1.2 s it had always decayed to zero before the next round trip could read it.
  It is back at 1.2.

  The better result is the one that isn't a measurement at all. Whether the blink passes through people was
  settled by reading each character's capsule **and** skeletal mesh: `BP_Goon`, `BP_StuntStandIn`, `BP_BossFreeze`
  and `BP_Player` all set `Visibility -> ECR_Ignore` on both, and `DefaultEngine.ini` declares no custom trace
  channels, so `TraceTypeQuery1` is Visibility. There is no surface on a character that answers the channel the
  blink traces. **This is the first time the stand-in itself was checked** — which matters, because the stand-in is
  the body the Team Owner's beat-5 call is actually about, and GameStation had only tested a goon and the boss.

  Everything temporary was reverted and read back: hook gone, `DebugSplice` deleted, exactly **one**
  `CallFunction|SpliceStart` call site left (so nothing was duplicate-appended), the two instance-editable flags
  put back, `SpliceCooldown` 1.2, `ShowTitleOnStart` true, all three test bodies removed. The level ended **not
  dirty**, so no actor package was written or orphaned. Saving re-serialized `BP_Player.uasset` and
  `BP_JumpCutGameMode.uasset` to different bytes with identical content, so both were restored to their committed
  bytes and the LFS locks released.

  **Housekeeping, and two things it turned up that are not about Splice at all.**

  The working tree is clean again: the three audio `.uasset`s and the two Blueprints that were sitting modified
  were all byte-churn from editor re-saves with no content change, and were restored. `JumpCut/Config/DefaultEngine.ini`
  is deliberately **left** modified — it is an auto-generated `AndroidFileServerRuntimeSettings` block Unreal wrote
  on open, it contains a random `SecurityToken`, and it is nobody's work; it should not be committed.

  Going back over what was skipped: the `PREJAM.md` gap was **not** the boss-3 build row (a later run had already
  added that). It was **Splice itself** — the power had no declaration row at all, and `PREJAM.md` is the file that
  has to be re-checked before we submit. It has one now. `INITIAL_PROMPT.md` got the status banner it was owed: its
  powers table still said the Stunt Double "makes a double of you plus decoys" with "Counter: Splice", both
  overtaken by the Nov 13 decision.

  Then the two that need a person. First: **this Mac is `tester, maker` in `docs/TEAM.md`, and a maker "never saves
  in Unreal"** — only GameStation, the builder, changes `.uasset` files. Last night's Splice commits (`26d437b`,
  `2c76ffc`) broke that rule, and this session saved in Unreal too (though nothing of it reached the repo). Second:
  both of those commits are authored **`Claude <noreply@anthropic.com>`**, not under Justin's name, even though
  this clone's `user.name`/`user.email` are set correctly — and `CLAUDE.md` requires every commit to be under the
  teammate's own name because Epic may read the history. Neither was fixed here: the first is a role decision, and
  the second means rewriting commits already pushed to a branch two other machines have.

- **What we learned:**
  - *"It can't be measured from here"* deserves one more try than it usually gets. The thing that made it
    measurable — a temporary debug bool and one line in tick — was already in this project, used for a different key.
  - A failed measurement and a broken feature look identical. Four readings of "0 cm" were caused, in order, by
    the title screen, a silently-ignored property write, and twice by the tester being dead. Reading `Health` and
    `IsLost` either side of a measurement would have saved most of it.
  - Prefer a fact about the assets to a fact about one frame. The collision table settles the pass-through question
    permanently, for all three bodies, and it took one read-only call.
  - Housekeeping finds things the feature work never would. The missing `PREJAM` row, the wrong commit author and
    the role breach were all sitting in plain sight.

- **Media:** none this run — every result above is a number read from the live pawn, not a screenshot.
