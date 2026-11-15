# 2026-11-15 — The game has music: a title theme and a gameplay loop, made from code (Justin's Mac mini)

- **What we asked for:** music. A moody title theme and a driving gameplay loop, both looping cleanly and mixed
  well under the sound effects. Title music on the title, gameplay music once play starts, quiet or off during
  the opening crash and on the win/lose screens, and never two copies after a restart.
- **Prompt(s) we gave the agent:** relayed from Justin's list, item D. Then, from Justin: *"They were royalty
  free. Might be able to find the license info in the project"* (his Cerberus tracks).
- **What happened:**
  - **Cerberus route: not taken.** This machine's permission rules blocked reading Justin's Cerberus project, so
    no licence text was found. Its music folder's file names suggest community game-music packs, but that is an
    inference, not a licence. As briefed, both tracks were generated from code instead, so they are our own
    scored work and `CREDITS.md` is untouched.
  - `tools/make_sfx.py <folder> music` (new `make_music`): **`MUS_Title`**, 72 BPM, 26.7 s, A minor
    (Am-F-Dm-E): slow pads, a soft plucked figure, a distant low pulse. **`MUS_Gameplay`**, 144 BPM, 66.7 s,
    A minor (Am-F-C-G): kick, snare, hats, an eighth-note bass, a sixteenth arpeggio and a lead, built in five
    8-bar sections (drums+bass, +arp, +lead, breakdown, everything), so a 3-5 minute run does not hear one 8-bar
    loop over and over. Both are rendered into a ring buffer whose note tails wrap round, so the loop point has
    no seam. Both are normalised to peak 0.22 (-13.2 dBFS) against the effects' 0.85, about 12 dB under them.
    RMS: title -26.7 dBFS, gameplay -30.0 dBFS. Both SoundWaves set to looping.
  - **Who plays it:** the game mode would be the natural owner, but it is LFS-locked by another machine. So
    `BP_OpeningDirector`, which is in the level and ticks all game, owns one audio component. New small
    functions: `CineMusicStep` (reads the game mode's `FlowState` and `ShowTitleOnStart`, read only),
    `CineMusicApply` (picks track and level), `CineMusicPlay` / `CineMusicStart` / `CineMusicEnsure` /
    `CineMusicLevelSet`. One call spliced into the director's Tick (89 -> 90 nodes). Levels: title 1.0; opening
    cinematic silent; explosion, boss intro, power moment and outro 0.3; play 1.0; win/lose silent. 0.8 s fades.
  - **Two traps hit:** `AdjustVolume`, `Play` and `SetSound` exist on both Audio and Synth components and the
    graph language picked the wrong ones. Fixed by creating those nodes with an explicit AudioComponent class.
    And **`AdjustVolume` to exactly 0 STOPS the component**: the first test showed the music dying at the
    opening and never coming back. "Silent" is now 0.001 (-60 dB), so the loop keeps running underneath.
  - **Measured in PIE** (`tools/c2_pie.py music`, `bossff`): title track on the title; R switches to the
    gameplay track held silent through the crash; it comes up to 1.0 on the frame the opening ends; ducks to 0.3
    the moment the boss dies and through the outro; silent the frame the win screen shows; a whole-level
    restart brings the title track back. **Never more than one music voice playing** across the restart.
- **Not yet checked by a person:** nobody has heard any of this. Justin needs to listen to the title theme, the
  gameplay loop over at least one loop point (26.7 s / 66.7 s), the mix against punches and the crash, and the
  ducks. Volume and taste are his call.
- **What we learned:** for an audio component, "fade to zero" means "stop".
