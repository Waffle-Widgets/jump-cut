# 2026-11-12 — Freeze Frame goes first, Rewind is parked, and the first full run from title to win (GameStation, the builder PC)

- **What we asked for:** after a usage-limit pause, carry on; then a change of plan from the Team Owner: the jam is one
  level of 3 to 5 minutes, so show the most fun power first. **Freeze Frame is the first power**, Rewind waits for a
  later boss, and the cel-shaded anime look is ready for when the 3D assets arrive. Late afternoon Pacific, Thu Nov 12,
  up to about 6 PM. This continues the builder run in
  [the goons, level and boss entry](2026-11-12-goons-level-and-freeze-frame-boss.md); the same decision seen from the
  other computer is in [the M Station entry](2026-11-12-three-characters-and-a-power-that-lost-its-boss.md).
- **Prompt(s) we gave the agent** (the Team Owner, exactly):

  > I hit my usage limit while you were working, but it has reset now. Please continue from where you left off.

  and then:

  > We are moving Rewind to a later boss due to the constraints of the MegaJam being 1 level 3-5 minutes. We want to
  > showcase the most fun abilities first. I think innovative mechanics would get us huge points. We should keep the
  > work that has been done for Rewind for a later boss and Freeze Frame is the first power the player gets. M_Station
  > is currently working on 3D assets and we will be moving forward with the cell shaded anime look so make sure we
  > have that ready for when we need it, I believe that work is in a branch.

- **What happened:**
  - **Two computers, one decision, and neither could see the other.** While GameStation's agents were building Rewind
    and a boss whose freeze attack only Rewind could break (Rewind was verified at about 11:25 AM), the same person on
    M Station decided at 3:28 PM that the first power is Freeze Frame, and wrote "do not build Rewind" into the roadmap.
    Nobody was wrong. The build branch had not been pushed, so neither side could see what the other was doing.
    The lead agent found the clash when it merged `main` after the pause (the pause was a usage limit, not a plan).
    It put the question to the Team Owner instead of guessing, and in the meantime built only what did not depend on
    the answer: a fix to the gate (C1d) and the HUD (B2), which shows an icon only for powers the player actually has.
  - **What the answer cost: very little.** Rewind's six functions were left untouched and switched off with one default
    (`HasRewind` false). The boss's freeze attack was only fair when Rewind could break it, so one new setting turns it
    off. Freeze Frame, already built as "the power you win from the boss", is now handed over by the driver in the cafe
    at a cyan ball. The first builder had written the player's main loop once, with empty slots for later powers, and
    every number is a named variable, so a change of design was a handful of settings and not a rewrite. (Packet G1.)
  - **The gate, as a story of builder against checker** (C1c, C1d, G1). Each fix was found by the next checker trying to
    break the one before:
    1. The boss could be beaten asleep by hugging the wall, never touching the gate's trigger. Fixed in C1c.
    2. Then the gate's slab, which takes 0.3 s to drop, could land on a player who turned back (9 runs), and with a
       frame-perfect turn (8 runs) the player ended up outside the shut gate with the boss awake. C1d fixed it by
       moving a player who turns back to a safe spot 120 cm inside until the slab is down. The checker tried **283
       scripted gate runs**: none ended outside or inside the slab.
    3. Then the "keep inside" guard could stick on, leaving an invisible line across the plaza, because a number that
       should be 0 was 0.00009. Found by the next checker, fixed in G1 (cleared in 8 of 8 reset-and-retrigger runs).
  - **What a player sees now.**
    - **HUD (B2):** a red health bar top left; a lettered, coloured icon for each power the player owns, dimmed with a
      refilling bar while it recharges; a cyan border while Freeze Frame is on. The only words on screen are the letters
      on the keys.
    - **Screens (E1):** the title reads "JUMP CUT", losing shows "CUT!", winning shows "THAT'S A WRAP", each with "R / (A)"
      to start or restart. Losing restarts at the last checkpoint with full health; five lose-and-restart cycles
      left nothing stacked up.
    - **Start of play (G1):** no powers. The player walks to the driver, a cyan ball vanishes and the E icon appears.
      There is a second ball in the doorway, so no way out of the cafe skips the power. Health 0 is "lost" at once; the
      1.5 s downed window only existed for Rewind. In 60 s of fighting the boss, not one frame was frozen.
  - **The first full run (E2).** A checker played from the title to the win screen by script, with scripted walking and
    real punches, no teleporting: **25.4 s** without Freeze Frame (health 70 at the end) and **27.0 s** with it (health
    100). Both gates behaved, and it could not break the order of play: no exit from the cafe without the power, no way
    to the plaza without the checkpoint, the screens lock input, win and lose can't both happen. Today's checkpoint,
    the core loop playable start to finish in grey boxes, is met **by script**.
  - **The honest verdict: it works, and it is far too short and easy.** The checker's numbers at default settings:
    the run takes 25 to 27 s (the pitch wants 3 to 5 minutes); one three-hit combo beat all three goons in 1.0 s
    with no damage taken; the boss falls to 6.3 s of plain punching and costs the player 30 health; Freeze Frame lasts
    10 s, longer than either fight, so it makes both trivial, and its 20 s cooldown means it is not back for the boss
    on a fast run; goons beaten during a freeze stay standing until it ends and block the lane. There are also 5 s of
    empty walking from the cafe door to the goons, no boss health display, and key prompts that are bare symbols.
    **The lead did not retune anything:** feel and difficulty are for the people who will play it.
  - **The anime look is ready.** The `mendezm87/anime-look` branch was merged into the build branch. Unreal had files
    open, so the merge was done in a separate temporary copy of the repo. The cel shader is in; putting it on the level
    is the next packet (A3, not started).
  - **Nothing here has been played by a person.** All of it was agents calling the game's functions, scripted walking
    and reading values back. A person still has to try, in order: the title and R; the cafe handover (is it clear what
    you got and from whom, and is it right that skipping the driver still gives you the power at the door?); the goons;
    E and what the stopped world feels like; the checkpoint post; turning straight back out of the plaza gate; the boss
    with and without Freeze Frame; losing on purpose to the goons and to the boss; the win screen, and whether holding
    R through the restart skips the title.
- **What we learned:**
  - **Push a build branch early, even when it is untested,** so the other computers can see what exists before anyone
    decides. The clash cost no work this time only because the pause let `main` catch up with us.
  - **A design note with slots and named numbers makes a change of mind cheap.** Rewind off and Freeze Frame first
    was a few settings.
  - **Each fix needs its own checker.** The gate took three rounds, and every round was found by someone trying to
    break the last fix, not by the person who built it.
  - **"All checks pass" from a script says nothing about fun.** The run is 25 seconds long and the player barely gets
    hurt; only people playing can tell us what to change.
- **Media:** all six are captures of the whole editor window while the game runs in it (the game is the large
  left-hand area).
  - ![The title screen: "JUMP CUT" in big yellow letters on a dark background with a white "R / (A)" box beneath it](../media/first-build-e1-title.png)
  - ![The cafe: the white player stands by a small blue box (the driver) next to a big red crashed-car box, with a full red health bar top left. A faint cyan glow shows at the player's shoulder; no power icon yet](../media/first-build-cafe-hand-over.png)
  - ![Freeze Frame on in the street: a cyan border round the screen, a cyan E icon bottom left, and two orange goons walking beside the player](../media/first-build-freeze-frame-goons.png)
  - ![The plaza fight: the violet boss right behind the white player in front of the yellow exit gate, the health bar partly drained and the E icon dimmed while it recharges](../media/first-build-plaza-fight.png)
  - ![The lose screen: the view tinted red with "CUT!" in white and the "R / (A)" box](../media/first-build-e1-lose.png)
  - ![The win screen: the view tinted green with "THAT'S A WRAP" in yellow and the "R / (A)" box](../media/first-build-e1-win.png)
