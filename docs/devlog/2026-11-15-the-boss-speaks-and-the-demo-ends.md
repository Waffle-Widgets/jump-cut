# 2026-11-15 — The boss speaks, the demo ends, and the cafe wall falls every time (Justin's Mac mini)

- **What we asked for:** "The boss needs some kind of dramatic introduction and monologue. After again the
  splice power would should do some outro text for the next destination, but then a fade to black finishing
  the demo and going back to the menu. Side note: double check the physics of the wall being crashed through
  by the car. Noticed it's still there sometimes after the cinematic until the car explodes."

- **Prompt(s) we gave the agent:** the message above, verbatim.

- **What happened:**

  **This is new content on bug-fix day, with the final build four hours out.** It went ahead because the
  Team Owner asked for it by name and because all of it fits in the two files this Mac already holds locks
  on (`BP_OpeningDirector`, `WBP_CineOverlay`): no new asset, no level actor, nothing of anyone else's.

  **The wall first, because it is the bug.** Measured before touching anything: three runs of the opening,
  reading the broken panel's bounds at the hand-off. Two scattered (x-extent 228 and 798 cm). One did not:
  **35 cm at the hand-off and 57 cm 1.6 s later**, against 9.5 intact - the panel standing in the hole,
  slowly leaning. That is "still there sometimes". The break is applied on a single frame (set dynamic,
  remove anchors, strain, crumble, impulse) and on some frames the impulse lands before the pieces are
  ready to take it - **inferred** from the fact that the later explosion's impulse always moves them. The
  director now looks again every 0.35 s, up to six times, and re-applies the break while the x-extent is
  under 60 cm. Seven runs since: 263, 659, 1077, 600, 286, 312, 311. **What that does not prove:** bounds
  say the pieces spread, not that no single piece is left upright in the hole, and at 1077 one run threw
  debris ten metres across the cafe.

  **The boss.** Walking into the plaza cuts to a low camera pushing in on him for three lines - "So you are
  the one who stopped the clock." / "That power was never meant for you." / "Let me show you how a scene
  gets cut." - 8.5 seconds in all. He is held with a rolling 0.4 s stun rather than frozen, so he still
  breathes. The player is turned to face him while off camera, and the shot returns on the player's own live
  camera the same way the explosion pan does: **0.18 cm, 0.00 degrees, 0.01 degrees of FOV** at the
  hand-off (the script put him in facing north on purpose). It plays once per level load, so dying to the
  boss does not replay it.

  **A first measurement of that hand-off said 74 cm, and it was the test's fault.** The screenshot taken at
  8.5 s stalls the game for a quarter of a second, so the "last cinematic frame" was really 0.25 s early.
  Moving the screenshot to 7.2 s gave the real number.

  **The ending.** After SPLICE: "Whoever sent them is waiting in the ruins to the east.", a 1.4 s fade to
  black, the ending card revealed under it, eight seconds, black again, and the level reloads to the title
  screen on its own. R still works on the card. The demo therefore **ends at the boss**: the walk through
  the ruins to `Marker_Win` and the two goons there are no longer reached. `Marker_Win` is still in the
  level and still works if anything ever gets there.

  **One hole closed on the way:** running past the street goons into the plaza left the objective stuck on
  "goons", which would have skipped the intro, the Splice moment and the ending. Entering the plaza now
  moves it on.

  **Not done:** no voice or music sting on the intro (no sound in the project is known to fit, and guessing
  one four hours before the build is how you ship a wrong one); the intro cannot be skipped; the boss was
  removed by a 9999-damage hit in every test, so nobody has fought him after hearing the speech. Played by
  the script only.

- **What we learned:**
  - A physics break applied on one frame is a coin toss. Read the result back and apply it again.
  - A screenshot inside a per-frame test is a hitch, and a hitch next to the frame you are measuring makes
    the measurement about the hitch.
  - If a story beat is triggered by an objective state, check what happens to the player who skipped the
    objective.

- **Media:**
  ![The boss, first line](../media/2026-11-15-boss-intro.png)
  ![The outro line after Splice](../media/2026-11-15-outro-line.png)
  ![The ending card, revealed from black](../media/2026-11-15-ending-card.png)
