# 2026-11-12 — The entry gets a name on it, and the practice repo goes public (8:05 – 8:30 AM)

- **What we asked for:** The Team Owner's details for the submission, and permission to make the practice repo
  public if the declaration needed it.
- **Prompt(s) we gave the agent:** "Team Owner: Manny Mendez theclassyhobo@gmail.com. You will need to ask Justin
  for his info. If we need to make the practice repo public then do so."
- **What happened:**
  - **The roster is real now.** `docs/TEAM.md` and `CREDITS.md` had placeholders — "(your name) — Driver" — where
    §1c/§2/§13 want every member's full name and one named Team Owner. Manny Mendez is now recorded as Team Owner
    and the owner of the devlog, video and submission; the computer table says who each PC belongs to instead of
    saying "Team Owner".
  - **Emails deliberately stay out of the repo.** The rules want each member's Epic-account email *on the entry
    form*; they never asked for it in the source. This repo is public, so the addresses live with the submission
    notes off GitHub, and the table records only whether we have each person's. One line of judgement that costs
    nothing and would have been hard to undo.
  - **The practice repo is public too.** `PREJAM.md` rests its whole provenance argument on
    `megajam-2026-practice` — the authoring trail for the anime look, and the proof that the pre-jam toolbox is
    what we say it is. A private link proves nothing to a judge, so it had to open. Scanned it first the same way
    we scanned this one: no tokens, no keys, no personal photos in history — the dog pictures are all in-engine
    screenshots of a model. One thing did turn up and we are leaving it: `DefaultEngine.ini` carries an
    `AndroidFileServer` `SecurityToken` that Unreal generated on Nov 1 and committed in `eb2bb69`. It authenticates
    a USB file server to a dev Android device, we never ship Android, and it is already in history, so rewriting
    109 commits to hide it would cost more than it protects.
  - **Still missing one person.** Justin's full legal name and Epic-account email are not ours to invent; the form
    went out to him this morning. Both files say plainly that the row is incomplete rather than quietly looking
    finished.
- **What we learned:** "Make it public" is two jobs, not one — the switch takes a second, and reading your own
  history as a stranger would takes the rest. The second job is the one that matters, and it is much cheaper before
  the switch than after.
- **Media:** (none)
