# 2026-11-15 — The markers get out of the way, and Splice lands like Freeze Frame (Justin's Mac mini)

- **What we asked for:** "It's feeling good. Can you continue polishing through the rest of the level and
  story beats? I did notice the quest markers moving to the goons and boss don't go away when the player
  approaches."

- **Prompt(s) we gave the agent:** the two sentences above, verbatim.

- **What happened:**

  **It is Sunday morning, about eleven hours before the deadline and five before the final build**, so
  "polish the rest of the level" was cut down on purpose to what one Blueprint can do without touching anyone
  else's files: the reported bug, and the two places the later beats fell silent. Everything is in
  `BP_OpeningDirector`; no level actor, no character, no HUD.

  **The markers.** The goon marker stayed over the spawner until the last goon fell, by design nobody had
  questioned; the boss marker switched itself off at x > 7600, which is 520 cm short of him, so depending on
  where the fight drifted it hung over his head. From objective 3 onward the marker now hides whenever the
  player is within 1200 cm of it. A script teleported the player far and near for each one and read the
  marker back: goons far *shown* / 900 cm *hidden*; boss far *shown* / 820 cm *hidden*; exit far *shown* /
  900 cm *hidden*.

  **Splice gets its moment.** Beating the boss used to set a flag and open a gate. It now gets what Freeze
  Frame got last night: time held for 2.2 s, the flash, the letterbox, the lens push, `SFX_PowerSplice`
  (which, like the Freeze Frame sound, nothing was playing) and one word, SPLICE. As a side effect the boss is
  frozen mid-fall on the killing blow.

  **After the boss there was no marker at all** for the 6,000 cm to the end of the demo. Objective 6 points
  at `Marker_Win`.

  **One caption shortened:** "That is the welcome party dealt with. The one with the cleaver is still waiting
  - keep going east." → "One more. The man with the cleaver."

  **Git bit us on the way in.** A `git fetch` triggered an automatic `pack-refs`, and the branch
  `Justin/beat1-opening-cinematic` stopped existing: HEAD said capital-J `Justin/`, the packed ref said
  lowercase `justin/`, and the loose file that had papered over the difference on this case-insensitive disk
  was gone. `git log` answered "your current branch does not have any commits yet". Nothing was lost — the
  packed ref held the right commit — and `git symbolic-ref HEAD refs/heads/justin/beat1-opening-cinematic`
  put it back.

  **Not done, and said so at the start rather than the end:** no new enemy behaviour, no camera work in the
  fights, nothing in the plaza or the ruins' art, and the ending card is untouched. `main` has moved 31
  commits since this checkout (it already contains last night's beat 1 work); this change is built on the
  older base because a local uncommitted `MI_AnimeLook_JumpCut` blocks the pull, and the only files it
  touches are ones `main` has not changed since. Played by the script only (goons and boss were removed with
  a 9999-damage hit, not fought), not by a person.

- **What we learned:**
  - A marker that points at a fight should disappear when the fight starts. Distance is a simpler rule than
    any per-objective "done" line, and it cannot be 520 cm wrong.
  - On macOS, never have two branches whose names differ only by case (`Justin/…` and `justin/…`). It works
    until git packs its refs.
  - Every power the player gains should land the same way; the second one is nearly free once the first exists.

- **Media:**
  ![Splice: the boss frozen on the killing blow](../media/2026-11-15-splice-moment.png)
  ![The boss marker far off, before the player closes in and it hides](../media/2026-11-15-boss-marker-far.png)
