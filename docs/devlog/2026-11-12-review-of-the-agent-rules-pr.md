# 2026-11-12 — Claude reviews a teammate's PR, and then fixes it, and we merge it (9:00 – 9:40 AM)

- **What we asked for:** a review of Justin's agent-rules pull request, the review posted to GitHub so Justin could
  read it, then — once he'd read it — the fixes applied, then the whole episode written up and the PR merged.
- **Prompt(s) we gave the agent:** "Review Justin's PR for the agent rules" / "add your review comments so Justin can
  review your review" / "Justin says to fix any issues you found with the PR" / "document what you did and merge".
- **What happened:**
  - **The review checked the claims instead of trusting them.** The PR said three things had been moved "word for
    word". Each was verified rather than taken on faith: the four devlog entries normalised to 78 content lines on
    both sides with zero difference (only `###` → `#`), `PITCH.md` → `ROADMAP.md` kept every body line, and
    `TEAM_SYNC_BACKUP.md` was byte-identical to the practice repo's copy. Two things that looked like bugs weren't:
    un-ignoring `Art/Blender/export/` is safe because `.gitattributes` sends `*.fbx`/`*.png` to LFS, and both
    "contradiction fixed" claims pointed at real contradictions in our own docs.
  - **Six findings, and the two worst were in the same file.** `docs/INITIAL_PROMPT.md` called itself the team's
    "go" for a 30-minute city that `docs/ROADMAP.md`, in the same PR, lists under *Waiting for a yes* with "never
    build from these as if they were agreed" in its header. And it told the lead agent to branch from
    `mendezm87/anime-look`, which is four commits behind `main` — so section 1 would have sent it to read a
    `ROADMAP.md` that doesn't exist on that branch, along with `PREJAM.md`, `docs/devlog/` and the `CLAUDE.md` rules
    the rest of the prompt depends on. Both are now fixed in the file: the "go" is conditional on a Decisions line,
    and the branch starts from `main` with `anime-look` merged in.
  - **A declaration that contradicted the file it was declaring.** `docs/PREJAM.md` rests its whole argument on
    "`e9bfc06` is the pre-jam set, everything after it is jam work". `TEAM_SYNC_BACKUP.md` says "Saved 2026-11-09" in
    its own first line and arrived *after* `e9bfc06`, so it broke that rule. It's legal under §7h — process, not
    game — but the fix is to name it as the one declared exception rather than hope nobody notices. The same pass
    added a jam-work row for these new agent-rules docs, including the fact that the reporting sections were **added
    to a `CLAUDE.md` we declared as pre-jam**: `e9bfc06` is what it said on Nov 11, and `git log -p CLAUDE.md` is
    every change since.
  - **A rule broken by its own first example.** `ROADMAP.md` says settled proposals move to Decisions "so nothing is
    ever in two places", and then kept a turned-down proposal under *Waiting for a yes* as a fallback. An agent
    reading that learns the rule can be ignored. Now there's a **Fallbacks** section with its own entry in the
    header, and the rule names it as the single exception.
  - **`main` moved underneath the PR while we were reviewing it.** By the time we came to fix things, GitHub had
    flipped the PR from MERGEABLE to CONFLICTING — our own cross-machine MCP fix had landed on `main` and appended an
    entry to `docs/DEVLOG.md`, the file this branch empties into a pointer. Resolved by this branch's own rule:
    keep the pointer, move `main`'s entry into its own file. The thing the PR was built to prevent was the first
    thing it hit.
  - **One finding deliberately not fixed as written.** `INITIAL_PROMPT.md` had quietly half-landed the "Final Cut" →
    "Director's Cut" rename while `PITCH.md` still says Final Cut. The Team Owner is holding that rename, so the file
    now explains that the two disagree on purpose and tells the agent not to rename anything itself — rather than
    making the owner's call for him in a doc.
  - **Nits with teeth.** `tools/bootstrap/new_jam_repo.ps1` still stamped a single `docs/DEVLOG.md` into any future
    jam repo, which would have brought this whole problem back the next time we bootstrap. It now writes
    `docs/devlog/` with a README and the first entry, and the block was run against a scratch folder rather than
    read — no BOM, correct filenames, templates resolve.
  - **Everything was done in a throwaway `GIT_LFS_SKIP_SMUDGE=1` worktree**, because Unreal was open on GameStation
    with assets loaded. No branch switch on the working tree.
  - **Merged at 9:39 AM, by us, not by the author.** Justin read the review and said to fix what it found, so the
    fixes went onto his branch rather than into a second PR — six findings and three nits, in `9e535bd` (the `main`
    merge that resolved the devlog conflict) and `7b5629f`. GitHub put the PR back to MERGEABLE/CLEAN and `main` is
    now `1c22fdd`: 29 files, +731/−205, docs and agent files only, no Unreal assets. We did **not** approve the
    review on GitHub — it went up as a Comment (review `5878405222`, 8 inline comments), because approving is a way
    of ending a conversation and the point was to start one. The merge itself waited for the Team Owner's word.
  - **What is now in force for every agent on this repo**, as of this merge: the reporting rules and the seven-point
    "done" list in `CLAUDE.md`; `docs/ROADMAP.md` as the shared memory of what is decided, what is waiting for a yes
    and what is a fallback; one file per devlog entry under `docs/devlog/`, with `docs/DEVLOG.md` left as a pointer
    so old links still land; and `docs/INITIAL_PROMPT.md` as a **draft**, not a go — it now stops and asks the team
    if `ROADMAP.md` still lists its scope under *Waiting for a yes*.
  - **Checked after the merge, logged out:** `docs/devlog/`, `docs/DEVLOG.md`, `docs/ROADMAP.md`, `docs/PREJAM.md`
    and this entry all return 200 without a GitHub login. That matters because the devlog folder is the §10 link we
    hand the judges, and until this merged it pointed at a file that was about to become a signpost.
- **What we learned:** a review is worth more when it verifies the claims it's given, and a pull request is worth
  more when its claims are checkable in the first place — "moved word for word" is a claim you can run `comm` on.
  The other lesson is cheaper to write than to remember: a document that states a rule and then breaks it in its own
  first example has taught the opposite of the rule.
- **Media:** (none)
