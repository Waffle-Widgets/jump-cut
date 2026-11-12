# 2026-11-12 — Borrowing another project's agent rules: a roadmap, honest reports, one file per devlog entry (Justin's Mac)

- **What we asked for:** Justin runs another project (a character builder app) with a lot of rules for how its AI
  agents finish work and stay organised. He asked Claude to compare those with this repo's agent files, bring over
  what fits, and list where the two disagree.
- **Prompt(s) we gave the agent:** "I want to review the agent.md and other files for guiding agents. and compare
  it to what we have set. ... I'd like you to alter our set up to work in this new project as well along with what
  is set up there. Let me know of any conflicting prompts so we can work though that" / "Rules should be for whole
  team not just me. We will be pushing these changes as a PR." / "The devlog the diary in this project. Have it do
  the multi file rules though" / "Maybe keep the jump cut rule for 2 then. Did you adapt our roadmap? Seems like it
  fixes the PITCH.md issue no?" / "Lets fix those contradictions first. Then I'd like to put together an
  INITIAL_PROMPT.md."
- **What happened:**
  - Claude read `CLAUDE.md`, `GEMINI.md`, the docs and the skills, and found seven places where the two setups
    disagree. Justin settled each one. Jump Cut's own way won for merging and for "one small change, then stop".
  - **New in `CLAUDE.md`:** a section on reporting (what was asked, done and left out, with numbers; what the agent
    checked and what a person still has to play; label guesses as guesses), a seven-point "done" list, and a rule to
    fix a bug's siblings in the same pass.
  - **New `docs/ROADMAP.md`:** open work, proposals waiting for the team's yes, what is still to decide, the cut
    list and dated decisions. The build order, cut list and Claude's scope proposal moved there from `PITCH.md` word
    for word. Before, an agreed change had nowhere to be written down, so a Claude on another PC couldn't tell the
    team's list from a proposal.
  - **The devlog is now one file per entry** in `docs/devlog/`, so two people writing at once never collide. The
    four existing entries were moved word for word.
  - **Contradictions fixed in our own files:** `.gitignore` ignored the folder where makers are told to commit art;
    `PLAN.md` had no deadline and the old role names; `HOW_WE_WORK.md` linked a file that was only in the practice
    repo; `RULES.md` had the old prize order.
  - **New `docs/INITIAL_PROMPT.md`:** a first prompt for the builder that builds the grey-box game in one sweep,
    with a lead that hands every piece to a builder subagent and a separate checker, and a ledger so nothing is
    dropped.
  - **What went wrong:**
    - Claude first put the rules in a personal file on Justin's Mac, to avoid editing a teammate's files. Justin
      wanted them for the whole team.
    - It switched "one small change, then stop" to the other project's "act, then report", then switched it back
      twenty minutes later when Justin reconsidered.
    - It reported three skills as pointing at missing files. Two of them said, in the same sentence, that the
      files were in another repo. It had read a search result instead of the sentence, and corrected itself.
    - While this was being written, two new commits landed on `main` that touched four of the same files. The new
      devlog entries had to be moved into their own files and the other three merged by hand.
    - Asked to write Justin's email into `TEAM.md`, Claude didn't: the file says addresses stay out of this
      public repo.
- **What we learned:** Rules written for one project don't transfer as they are; about half fit. Give decisions a
  place of their own, or every agent re-argues them. Check what a teammate pushed before editing shared docs.
- **Media:** (none)
