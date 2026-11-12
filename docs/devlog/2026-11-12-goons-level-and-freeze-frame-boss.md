# 2026-11-12 — Goons, the level and the Freeze Frame boss, plus what the checkers caught (GameStation, the builder PC)

- **What we asked for:** nothing new. This is the same run the Team Owner started with "go ahead and kickoff the
  INITIAL_PROMPT.md", carrying on by itself in the early afternoon Pacific, Thu Nov 12. One builder subagent per packet,
  then one checker subagent. The lead agent commits only after a checker passes, and writes each finding into the
  ledger. Packets this time: **B3** (goons), **C1** (the level), **D1** (the first boss), plus two small fix packets
  that the checkers' findings created (**C1b**, done; **C1c**, being built with the next packet).
- **Prompt(s) we gave the agent:** no person typed a prompt for these. As before, each builder got a brief with the goal,
  files to read, what not to touch and the "done means" checks word for word. Each checker got the same checks but
  **not** the builder's report, so it had to find out for itself.
- **What happened:**
  - **B3, goons.** Opus builder, Fable checker. A goon is orange, has 40 health, and three punches beat it. A spawner
    places a group and rebuilds the full group on respawn. All five checks passed: a goon 800 cm away closed to 122 cm in
    2.5 s, hit for 8 about every 1.85 s, and three punches took it 40 -> 30 -> 20 -> 0.
    - **Caught:** in a line of three, the middle goon ends up waiting behind the other two (1 punch against 6 each in
      11 s). Three goons take a standing player from 100 to 0 in 9.4 s, which may be too hard.
  - **C1, the level.** Sonnet builder, Fable checker. A script placed everything from a table of numbers: a 12 x 10 m
    cafe with a crashed-car box, a 60 m street, a 30 x 30 m plaza with two gates, a checkpoint, and markers where the cut
    scenes will go. All five checks passed. The checker walked the live player from the cafe to the finish in 17 seconds
    by script and swept the route for snags and gaps, and found none.
    - **Then it found three things the builder had not:** the checkpoint could be walked past (a 5 m trigger in a 10 m
      street); the floor's colour looked right in the editor but was never written to disk, so it would have been lost
      on the next load; and Rewind would slide the player back out through the shut plaza gate, locking them out of the
      boss fight. All three were fixed in **C1b**: the checkpoint now catches the player from the street's edge, the
      floor survived a reload, and Rewind three seconds after the gate shut landed inside the plaza.
    - **Left for a person:** goons walk in straight lines and get stuck on the cafe's front wall, so the cafe is a safe
      spot.
  - **D1, the boss.** Opus builder, Fable checker. He is violet and a head taller than a goon. A **red ball over his
    head** warns of a punch (0.7 s warning, 15 damage). The **whole plaza floor turning cyan** warns of his freeze (1.2 s
    warning, then 3 s frozen). Frozen, the player can't move or punch and takes free hits, up to 48 damage. **Rewind
    breaks the freeze**, gives the health back and dazes him for 1.5 s. Beating him hands over Freeze Frame and opens the
    exit gate. All four checks passed. The checker ran **26 Play sessions** hunting for stuck states and found none.
    - **It then found two holes.** (1) By hugging the wall after the gateway, the player never touches the gate's
      trigger, so the gate stays open, the boss stays asleep, and 18 punches beat him without a fight. The trigger was
      built exactly as the design note said; the note was the problem. (2) Goons outside the shut gate could still hit
      a player standing just inside, because punches are distance checks with no line of sight and walls mean nothing
      to them. Both went into **C1c**, not yet built.
    - **The checker's honest verdict on the fight at default numbers:** it lasts 9 to 10 seconds, so the player sees only
      one freeze; a player who mashes punch and never rewinds wins with 7 health left; nothing on screen tells a frozen
      player to press Rewind; and Rewind pressed in the first 0.45 s of the warning is wasted. These are tuning and
      feedback problems for people to decide, not bugs.
  - **Tool trouble worth a line:**
    - `CaptureViewport` during Play draws the editor's scene, not the game (a raised gate still showed closed), so
      captures use `CaptureEditorImage` instead.
    - A placed actor's floor material and the checkpoint radius did not reach disk until the actor was touched and the
      level saved again. This is how the floor bug got through the builder's own check.
    - The checker played the boss fight with a script "bot" that walks, punches and rewinds, because one tool call per
      key press took 1 to 20 seconds each.
    - Graph tool's `IsValid` node ends the flow like a cast, so code after it was rejected until split into a small function.
  - **Nothing here has been played by a person.** Everything above came from agents calling the game's own functions
    and reading values back. Still needed from a person: walk the route from the cafe to the plaza; fight the goons
    (is three at once too hard, and does the middle one ever swing?); fight the boss at default numbers (is one freeze
    enough, is it clear that Rewind is the answer?); see whether the checkpoint, the gates and the cafe's safe spot feel
    right.
- **What we learned:**
  - A builder's "all checks pass" and a checker's "all checks pass, and here are two ways to break it" are different
    things. That is why the checker never sees the builder's report.
  - Holes in the design note itself only show up when someone tries to cheat the game: the gate trigger was built
    exactly as designed, and still let a wall-hugger skip the fight.
  - Distance checks are simple to build, but walls mean nothing to them.
  - "Looks right in the editor" is not "saved": the floor colour needed a disk check, not a screenshot.
- **Media:**
  - ![Top-down view of the whole level: the small crashed-car room on the left, the square cafe, the long street between two tall blocks, and the boss plaza at the right end. Gates show as yellow patches](../media/first-build-c1-top-down.png)
  - ![The player in game view walking down the grey street toward a yellow gate, between two plain walls](../media/first-build-c1-street-goons.png)
  - ![The plaza: the white player in the middle, an orange goon on the left and the taller violet boss on the right, in front of the yellow exit gate](../media/first-build-d1-boss-goon-player.png)
  - ![The same scene with a red ball floating over the boss's head: the warning for his punch](../media/first-build-d1-punch-warning.png)
  - ![The freeze warning: the whole plaza floor turned cyan, with the player in front and the boss far behind them](../media/first-build-d1-freeze-warning.png)
