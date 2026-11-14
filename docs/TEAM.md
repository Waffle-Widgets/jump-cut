# Team

Up to 5 people (jam rule §2). Every member must be 18+, have an Epic account, and be listed on the entry.
Claude reads this file to know who owns what. Update it whenever ownership changes, and commit it.

## Members

| Name | GitHub | Epic account email registered? | PC(s) | Role |
|---|---|---|---|---|
| **Manuel Mendez** (goes by Manny) — **Team Owner** (submits the entry, §1c/§13) | mendezm87 | **confirmed** — held outside this public repo, see note below | GameStation (Unreal), M Station (Blender, TRELLIS) | builder, maker, devlog + submission |
| **Justin Catrambone** | allbarkdev (joined Waffle-Widgets and Jam Team Nov 8) | **confirmed** — held outside this public repo, see note below | Justins-Mac-mini | tester, maker |
| | | | | |
| | | | | |
| | | | | |

**Emails are not written in this repo.** The entry needs every member's full name and the email on their Epic account
(§1c, §2, §13), and the repo is public, so the addresses are kept with the submission notes off GitHub and typed
straight into the itch.io form. This table only records *whether* we have each person's address. Everyone must also
be 18+ with an active Epic account, and a human — the Team Owner — presses submit (§17).

**Both members are confirmed for §1c/§2/§13 as of Thu Nov 12, evening.** Justin confirmed the address on his Epic
account and that he is over 18; the Team Owner relayed that confirmation. The address itself is with the submission
notes off GitHub, not here. Nothing on the entry is waiting on a teammate now.

**GitHub access:** every teammate joins the Waffle-Widgets team **Jam Team**, which has write access (needed to push
and to lock files). The org's base permission is "No permission" (since Nov 8), so members see only the repos their
team is given; the owner's other projects stay private to the owner. When the jam repo is made, give Jam Team write
on it (repo Settings > Collaborators and teams), or teammates won't even see it.
**Teammates get the MegaJam repos only.** Add new people to Jam Team, never to a repo directly, and give Jam Team
only MegaJam repos. The org's other repos aren't part of this work. Members may create repos of their own. Each new person needs a paid seat on the org first.

## Computers: who does what
Claude reads this table at the start of every chat. It runs `hostname` and finds its row (case doesn't matter, and a
Mac's `.local` ending is ignored). If no row matches, it asks which computer it is on and fixes the name here.
**Change a role by asking any chat** ("make GameStation the builder", "add this Mac as a tester"): Claude edits this
table, commits and pushes. A computer can have more than one role (`tester, maker`).

| Computer (`hostname`) | Person | OS | Role | Notes |
|---|---|---|---|---|
| Gamestation | Manuel Mendez | Windows | builder | Unreal edits, packaging, fixes playtest issues |
| M_Station | Manuel Mendez | Windows | maker, **builder** (see the claim rule below) | TRELLIS, Blender, Meshy, sounds, ComfyUI on the 3090, the Gemini browser. UE 5.8 installed and the project has been opened here |
| _(Manny's Mac: hostname to add)_ | Manuel Mendez | macOS | tester | |
| Justins-Mac-mini | Justin Catrambone | macOS | tester, maker, **builder (beat 4, beats 1-3 cleanup, the beat 1-3 imports: #40, #5, #7, #6)** | Mac mini, Apple silicon. Full UE 5.8 (43 GB, `~/Epic Games/UE_5.8`) with the MCP plugin prebuilt for Mac, and a complete clone with all LFS objects, so it can do Unreal work. git-lfs, gh, uv and the Blender MCP set up Nov 9; Blender is 5.1.2 (team uses 5.2) |

**Why this Mac is a builder for beat 4 only** (asked for by the Team Owner, Fri Nov 13, 22:30 UTC: *"Continue beat 4
on this mac"*). It was `tester, maker`, and a maker never saves in Unreal - but it had already saved `.uasset`s twice
(the Splice rebuild, `26d437b` and `2c76ffc`) because it was the only machine that could, and the Team Owner has now
put beat 4's platforming here. The role is **scoped to beat 4** so GameStation stays the builder for everything else:
this Mac saves the beat-4 ruin assets and the beat-4 actors in `Lvl_JumpCut`, and nothing else. GameStation and this
Mac share one GitHub account, so LFS locks cannot tell them apart - say which files were touched after each push.

**Widened on Fri Nov 13, 4:36 PM Pacific** by a direct instruction to this Mac's chat: *"For you, we need to clean
up beats 1-3"* (flicker, enemy animation, thugs that act as one, the levitating Splice boss, Chaos physics). That
work saves `BP_EnemyBase`, `BP_Goon`, `BP_Player`, the cleaver boss's animation assets, new breakable assets and
the beat 1-3 actors in `Lvl_JumpCut`. It is still scoped: GameStation remains the builder for everything else, and
Issue #19 (*may this Mac change Unreal files?*) is still open for the general answer.

**Widened again on Fri Nov 13, 4:54 PM Pacific.** M Station moved the four import tickets to this Mac in a comment
on #40 (*"Manny has moved the four import tickets to you because you have Unreal open: #40, #5, #7, #6"*), and the
Team Owner then told this chat to do the tickets assigned to it. That **replaces** the earlier line here saying the
character-model imports were not this Mac's. The four are: the set pieces (#40), `SK_CafeCoworker` onto
`BP_Coworker` (#5), `SK_CafeWalker` onto `BP_Player` plus the montage retarget (#7), and `SK_StreetGoon` onto
`BP_Goon` with its chains hand-mapped (#6). Everything outside those four, and outside beat 4 and the beats 1-3
cleanup, is still GameStation's.

**M Station is a builder too, as of Fri Nov 14** (Team Owner: *"M Station can be a builder too but we need to make
sure it doesn't try to build or modify any blueprints that are being worked on by another chat or computer."*). The
role is not scoped to an area - the condition is the sentence after the "but", and it is a hard gate, not advice.

**The claim rule: before M Station opens ANY `.uasset` to change it.** Three different chats and three computers are
now in this repo at once, and the usual guard does not work here - GameStation and M Station share one GitHub account,
so an LFS lock held by "mendezm87" could be either of them. So check all four, in this order, and stop at the first
one that says someone else is in there:

1. `git lfs locks` - any lock on the file at all, by anyone, means stop. Do not assume a lock under Manny's name is
   your own; it is more likely GameStation's.
2. `git fetch --all && git log --all --since=6.hours --name-only -- <the file>` - if another machine has touched it
   today, it is theirs until they say otherwise.
3. The open issue for that area. If a ticket naming that Blueprint is assigned to another machine, the Blueprint is
   that machine's, even if nothing is locked yet - Justin's import queue (#52, #56) is the live example.
4. The `[COLLAB]` board the chats share. A sibling chat quoting work in that file is a claim.

**And when it does go in: take the lock first, say so, and release it.** `git lfs lock <file>` before the editor
opens it, the file list in the push message so the other machines can tell which "mendezm87" did it, and
`git lfs unlock` after the push. Never two chats in one Blueprint, which is the rule that already existed for
`builder (area)` and is the one this change could break.

**What this does NOT change.** GameStation is still the single builder of record for packaging and for the Windows
build the jam wants. M Station building is for work nobody else is holding - the title screen widget is the first
of it - not a second queue competing with Justin's imports.

**Roles**
- **builder:** the only computer that changes Unreal files (`.uasset`, `.umap`) and commits them. It packages and publishes
  test builds and works through the playtest issues (`playtest-issues` skill). Exactly **one** at a time, on Windows
  (the jam wants a Windows build). It works on the `playtest` branch and merges into `main` once testers confirm.
- **builder (area):** e.g. `builder (UI)`. A second person may change Unreal files in that one area only (its folder
  in "Who owns what" below), with LFS locks. Use it when one builder can't keep up; never two in the same Blueprint.
- **maker:** makes things outside Unreal (Blender, Meshy, TRELLIS, `tools/make_sfx.py`) and commits FBX, textures,
  sounds and scripts. It never saves in Unreal; the builder imports what it makes.
- **tester:** plays test builds and files GitHub issues (`docs/PLAYTEST.md`). Windows: downloads the build from the
  repo's Releases. Mac: pulls the `playtest` branch and presses Play in Unreal, never saving.
- Everyone may edit docs and scripts (text files merge normally).

## Who owns what this jam
Own a system, a folder, or a set of Blueprints. Others ask before changing it, and only the owner (or whoever holds
the lock) edits its `.uasset` files.

| Area | Owner | Files / folders |
|---|---|---|
| Level layout | | `Content/Game/Maps/` (One File Per Actor: lock the actors you move) |
| Player character | | `Content/Game/Blueprints/BP_<Player>*` |
| Obstacles / enemies | | |
| UI (title, HUD, end screen) | M Station (title screen), Justin's Mac (the #52 texture imports) | `Content/Game/UI/` - `WBP_Title` and its animation are M Station's; the rest is unclaimed |
| Audio | | `Content/Game/Audio/`, `tools/make_sfx.py` |
| Art made outside Unreal | | `Art/Blender/`, imported by the level owner |
| Devlog, video, submission | Manuel Mendez | `docs/devlog/`, the zip |
