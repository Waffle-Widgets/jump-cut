# 2026-11-12 — Player fists and Rewind, built by subagents (GameStation, the builder PC)

- **What we asked for:** nothing new. This is the run the Team Owner started with "go ahead and kickoff the
  INITIAL_PROMPT.md" continuing by itself, one packet at a time. Two packets this time: **B1** (the player with health and
  a three-hit fist combo, plus the base class every enemy will use) and **B4** (Rewind, our core power). Time: late
  morning to about noon Pacific, Thu Nov 12.
- **Prompt(s) we gave the agent:** no person typed a prompt for these. The "prompts" are the briefs the lead agent wrote
  for its subagents. Each **builder** brief had the packet's goal, the files to read first, what not to touch, the
  "done means" checks word for word, and the editor rules (what freezes the MCP, never edit during Play mode). Each
  **checker** brief had the same checks but **not** the builder's report, so it had to find out for itself.
- **What happened:**
  - **B1, the player and the enemy base.** An Opus builder took about 13 minutes, a Fable checker about 11.
    - `BP_Player` is a child of the template character with 100 health and a three-hit combo: 10, 10, then 20 damage
      plus a knockback. Keys are read by polling every frame, because the graph tool can't wire input events.
    - `BP_EnemyBase` walks up to the player, shows a **red warning ball over its head**, then punches for 8.
    - The builder created all 61 player variables and 14 empty functions up front, so later builders only fill in
      function bodies and nobody has to rewrite the player's main loop.
    - The checker's numbers: a 30 hit left 70 health. Three punches took an enemy 100 -> 90 -> 80 -> 60, and the third
      threw it 590 cm. A beaten enemy lingers 0.6 s so you see the knockback, then is removed. Punches only land on what
      is in front and within reach: facing away, or from 200 cm, they missed.
    - **What went sideways:**
      - The game mode spawned a second character next to the placed player until its default pawn was set to None.
      - The checker found that merely reading and compiling Blueprints marks them, even the template character, as
        unsaved in the editor. So every later brief now says "never save all, save only your own files".
      - The checker couldn't spawn test enemies into the running game from Python, so it placed them in the editor
        level instead.
  - **B4, Rewind.** An Opus builder took about 12 minutes, a Fable checker about 10.
    - The player records where they are and their health every 0.1 s, but only when they moved or their health
      changed, for the last 10 seconds. Pressing Rewind slides them back along that path in 0.25 to 1 second and gives
      back the health they had then. There is a 6 s cooldown, and no damage during the slide or for 0.5 s after.
    - It is a slide, not one jump: the checker found every frame of the slide sitting on the recorded path.
    - The checker's numbers: after a 1000 cm move and two hits (100 -> 70 -> 50), Rewind landed 0 cm from the spot of 10
      seconds earlier, with health back to 100. With real walking at 600 cm/s it landed 25 cm off, because samples
      are up to 60 cm apart at that speed. It also works from the "downed" state (0 health with Rewind ready gives a
      1.5 s window to press it) and after falling off the world.
    - **What went sideways:**
      - The graph tool once added a second full copy of a function's graph instead of replacing it (121, then 181
        nodes, the extra ones unreachable). The builder deleted the nodes and wrote the function once (61 nodes).
      - The builder and the checker both slowed game time to fit 10-second waits between tool calls.
      - The checker's mid-slide capture shows nothing on screen that says "rewinding". The effect is correct but
        **invisible**, and Rewind is the one mechanic that has to feel great. That goes on the list for the art and
        juice day.
      - There is a 1.7 cm drop for a few frames on landing.
  - **Nothing here has been played by a person.** Every number above came from agents calling the game's own functions
    and reading values back. Still needed from a person: left mouse or gamepad X to punch (one punch per press); Q or
    left shoulder to Rewind after walking around; and how the slide and the camera feel. The HUD, goons, the level and
    the boss are not built yet.
- **What we learned:**
  - Writing every name down in one design note before building let three separate agents with no shared memory build
    on each other's work without a single naming clash.
  - A check that can't press keys can still prove a lot by calling the game's own functions and reading numbers.
    It can't prove feel, and the invisible Rewind shows the gap.
  - "Read-only" isn't read-only in the editor: opening and compiling Blueprints marks them unsaved, so save lists
    must name files one by one.
- **Media:**
  - ![Game view from the checker's run: an enemy on the left with the red warning ball over its head, facing the player](../media/first-build-b1-enemy-warning.png)
  - ![The checker's mid-slide capture of Rewind. This one is the whole editor window, not just the game view; the player is mid-slide and nothing on screen says "rewinding"](../media/first-build-b4-rewind-midslide.png)
