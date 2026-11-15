# 2026-11-15 — Real music: three CC0 tracks from Justin's Cerberus app, with our loops one switch away (Justin's Mac mini)

- **What we asked for:** Justin's first ask was to "steal" music from his Cerberus app if needed. The earlier entry
  shipped generated loops because the licence could not be read. Then: *"I added the Cerberus repo to the project
  so you can access now."*
- **What happened:**
  - Cerberus keeps a licence record, `apps/app/static/sounds/SOURCES.md`. Every music track in it is **CC0 1.0**
    from OpenGameArt. Three rows were confirmed in the file and used:
    - Title: "song21 0" (Mysterious Ambience), cynicmusic, 42.8 s -> `MUS_TitleMystery`
    - Gameplay: "jrpg battle full 0", HydroGene, 115.1 s -> `MUS_Gameplay_Sourced`
    - Boss fight: "Epic Boss Battle [Seamlessly Looping]", Juhani Junkala (SubspaceAudio), 123.3 s ->
      `MUS_GameplayBossBattle`

    The files were read from the local checkout of Cerberus on this Mac, not cloned. The licences were not
    re-checked on the OpenGameArt pages.
  - **Loop seams, by numbers** (`tools/mus_loopfix.py`): the decoded MP3s did not loop cleanly. The boss track
    jumped from -111 to 19,269 at the loop point, a guaranteed click, and the gameplay track ends loud and starts
    in silence. The tool cuts each track where its tail best matches its opening and blends 50 ms across the join.
    Seam jumps after: boss 1,352 (was 19,380), gameplay 805 (was 4,338), title 0. All are inside each track's own
    normal sample-to-sample range (99th percentile 7,083 / 4,964), so no click. Whether the music lands on the
    beat across the join is for an ear.
  - **Level:** the tracks are mastered loud, so they were re-levelled to sit where our generated loops sat: title
    peak 0.22, gameplay and boss RMS -27 dBFS (peaks 0.16 and 0.13), against the effects' 0.85 peak.
  - **Wiring:** the same single music player on `BP_OpeningDirector`. Track 3 is new: the boss track plays from
    the first frame of the boss intro to the end of the game. It is a cut plus a 0.8 s fade-in, not a two-voice
    crossfade, which keeps the never-two-tracks guarantee. A new instance-editable `UseGeneratedMusic` bool
    (default **false**) switches back to our generated `MUS_Title` / `MUS_Gameplay`, which stay in the project.
  - **Measured in PIE** (`tools/c2_pie.py music`, `bossff`):
    - the title plays `MUS_TitleMystery`
    - R switches to `MUS_Gameplay_Sourced`, held silent through the crash, full when the opening ends
    - a restart brings the title track back, with never more than one music voice playing
    - the boss intro switches to `MUS_GameplayBossBattle` on its first frame, ducked to 0.3 under the intro, full
      in the fight, 0.3 on the kill and the outro, silent the frame the win screen shows
- **Jam rules:** these three are **sourced** assets: allowed, credited in `CREDITS.md`, **not scored**. Our generated
  loops would have counted as our own work; flipping `UseGeneratedMusic` restores them. No track name appears in
  the game.
- **Not yet checked by a person:** nobody has heard any of it. Justin needs to listen to the three tracks, each loop
  point (42.8 s, 115.1 s, 123.3 s), the switch into the boss track at the intro, and the mix against the fight sounds.
- **A slip to own up to:** one batch of graph edits was made while a Play session from the previous test was still
  running, which this project's rules forbid. Nothing froze; PIE was stopped, everything re-compiled and read back,
  and only then saved.
