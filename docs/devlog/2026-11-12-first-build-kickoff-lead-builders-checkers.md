# 2026-11-12 — First build kickoff: a lead, builders and checkers (GameStation, the builder PC)

- **What we asked for:** Thursday's checkpoint, built by agents working in a team: start the prepared
  `INITIAL_PROMPT.md` on the latest `main`, then, after the agent stopped to ask a question, keep the scope jam-sized.
  Time: about 10:30 AM Pacific, Thu Nov 12.
- **Prompt(s) we gave the agent:**
  1. "Make sure we are on the latest main, then go ahead and kickoff the INITIAL_PROMPT.md"
  2. After the agent stopped and asked: "For the scope we should follow the rules of the MegaJam and if we have time for
     more we can look at expanding our scope. We have not decided if we want to move forward with the anime-look but we
     should keep those assets in a branch in case we want to go that route."
- **What happened:**
  - **The agent did not start, on purpose.** The first lines of `INITIAL_PROMPT.md` say it is a draft and must not run
    until the team agrees its scope (one large city, about 30 minutes of play). `docs/ROADMAP.md` still listed that
    under "Waiting for a yes", and our own `CLAUDE.md` guardrail says one small level and 3-5 minutes. So the agent
    asked instead of obeying "go ahead". The owner kept the scope jam-sized. The decision went into ROADMAP's
    Decisions, and the large city moved to Fallbacks, turned down but kept in case a playtest changes our minds.
  - **What the run is now.** The prompt's method, but only for Thursday's slice: a player with fists, goons, Rewind,
    the Freeze Frame boss and one small level (cafe, street, plaza). A lead agent plans and keeps a ledger
    (`docs/FIRST_BUILD_LEDGER.md`, eleven packets). Each packet gets one builder subagent and a separate checker
    subagent that never sees the builder's report, so it can't just agree with it. Only a checker's pass counts as
    "verified". Models: Opus builds the Blueprint systems, Sonnet does simpler packets and devlog entries, Fable leads,
    designs and checks.
  - **Switching branches with Unreal open.** The editor was on the anime-look branch with its cafe map loaded. The agent
    checked nothing was unsaved, loaded the template map, then created `Gamestation/first-build` from `main`. Git could
    not remove 11 anime-look files that Unreal still held open ("unable to unlink ... Invalid argument"), so they stayed
    on disk as leftovers. The agent hid them from git on this PC only (`.git/info/exclude`) so a builder can't commit them
    by accident. The anime-look work itself is safe on its own branch on GitHub.
  - **A design note first.** A design subagent wrote `docs/FIRST_BUILD_DESIGN.md`, the contract between builders who
    share no memory: exact names, the player as the hub, no timers or overlap events (countdowns run in Tick, triggers
    are distance checks), Rewind as three arrays sampled every 0.1 s, Freeze Frame as per-enemy time dilation rather
    than global. It also pointed out which of the ledger's checks cannot be proven without a person pressing keys.
  - **Packet A1: an empty lit level and the game mode.** An Opus builder made `Lvl_JumpCut` and `BP_JumpCutGameMode` in
    about 10 minutes, and a Fable checker passed all four checks (in Play mode the template character stands on the
    floor). What went wrong along the way: no MCP tool creates a level, and the tool-script sandbox has no `unreal`
    module. So the builder wrote a Python file and typed `py <path>` into the editor's console box. Then switching on
    "Use External Actors" opened a modal "Convert Actors Packaging" window that froze the MCP for 300 seconds, until the
    builder found the window from PowerShell and sent it Enter. The checker, which had not read the builder's report,
    noticed three things the builder never mentioned: its read-only checks plus a Play-mode run left the game mode
    Blueprint marked unsaved, the floor has no material yet, and the project's start map still points at the template
    level (a later packet sets it).
  - **Nothing here has been played by a person.** Every packet is "untested" until someone plays it.
- **What we learned:**
  - A prompt that says "don't run me yet" should be obeyed even when a person says go, until the person settles the
    open question. Asking cost a couple of minutes and kept us from building a 30-minute city in a 3-5 minute jam.
  - A checker that hasn't seen the builder's report finds things the builder didn't mention.
  - Modal windows are the MCP's weak spot: one Yes/No box froze everything for five minutes. The workaround is now in
    `docs/FIRST_BUILD_MCP_TIPS.md` for the next builder.
- **Media:** ![Play mode in the empty level: the template character on a plain floor under a lit sky](../media/first-build-a1-empty-level.png)
