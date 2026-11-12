# 2026-11-12 — Three characters, and a power that lost its boss (M Station)

- **What we asked for:** pull `main`, then start on the main character, the boss who crashes through the cafe wall,
  and the second boss. Two design changes came with the ask: the first boss now gives **Freeze Frame** instead of
  Rewind, and the second boss is a **Japanese mob boss with a cleaver** who gives Splice.

- **Prompt we gave the agent:**

  > Pull the latest main. Let's start working on the main character, the boss that crashes through the wall, and
  > the second boss. The first boss gives the Freeze Frame ability now. The second boss has the splice ability, we
  > were thinking he looks like a Japanese mob boss with a cleaver. You can use Gemini and Meshy to work on this.

- **What happened:**

  **The pull was clean**, which is worth saying because it nearly wasn't a given: this clone was sitting on
  `e9bfc06`, the bootstrap commit, **14 commits behind**. Everything the team built this morning — the agent
  rules, `ROADMAP.md`, `PREJAM.md`, the whole `docs/devlog/` folder — was missing from the working copy. It
  fast-forwarded to `7bbe168` with nothing to merge and nothing lost. Anyone who had started editing docs on this
  machine before pulling would have been writing against the bootstrap versions.

  **A one-line design change had a three-file blast radius.** "The first boss gives Freeze Frame now" sounds like
  a table edit. It isn't. `PITCH.md` named **Rewind** as the core mechanic *and* as the first boss's gift, and the
  whole ladder is "beat each boss with the power you took from the one before". Moving Freeze Frame to the front
  leaves the rest of the ladder intact — Splice is still countered by Freeze Frame — but it leaves **Rewind with
  no boss and no home**. Either the worker already has it at the cafe, or it is cut and Freeze Frame is the core
  mechanic. Nobody has said which, so that went into `ROADMAP.md` under *Still to decide* rather than being
  guessed at. The two things that *were* decided went into Decisions, under the name of the person who decided
  them. Three files changed from one sentence: `PITCH.md`, `ROADMAP.md`, and this.

  **"Use Gemini and Meshy" ran into our own rules, and the rules won.** Both tools turn out to be
  *person-operated* here, not agent-operated, and `CLAUDE.md` says so in two separate places:

  - Reference pictures "come from Gemini in the user's Chrome (Claude in Chrome; the in-app browser isn't signed
    in)". This session is a command-line agent with no browser.
  - Meshy is blunter: **"retries go through the browser, never the API"**, because every API call costs credits
    while the website's retries are free — 4 per model on Pro, 40 on Ultra. An agent that "helpfully" called the
    Meshy API would have spent real money to get a worse workflow.

  So instead of working around the rules, we took the local path the same file points at: `tools/gen_images.py`,
  which runs **ComfyUI + Qwen-Image on M Station's own graphics card**. Nothing goes online, it costs nothing,
  and the prompts live in the repo as text. Meshy is still the right tool for the 3D step — it just has to be a
  person pressing Retry, so the hand-off in `CHARACTERS.md` ends exactly where an agent has to stop.

  **A pre-jam script with a stale docstring.** `gen_images.py` came from an older project and reads its prompts
  from `docs/prompts.md` — while its own docstring still tells you to look in `docs/attack-pieces.md` or
  `docs/concept-prompts.md`, neither of which exists here. Neither does `docs/prompts.md`; the file had simply
  never been created in this repo. Rather than guess, we read the code: `find_prompt()` wants a `### CODE`
  heading with `> ` quoted lines under it. We wrote `docs/prompts.md` to that shape and then **imported the
  module and called `find_prompt()` directly on all three codes** before spending nine renders on a format
  guess. All three parsed. That check cost about ten seconds and would have cost twenty minutes of GPU time.

  **The declaration needed a line, for a reason that isn't obvious.** `PREJAM.md` declares our **prompt library**
  as pre-jam material — meaning `.claude/skills/`. We have now added a *second* file with "prompts" in the name,
  `docs/prompts.md`, which is jam work and which produces **scored** art. Left alone, a judge could reasonably
  read our own declaration as covering it. So `PREJAM.md` now names it on the jam-work side explicitly, and the
  pre-jam row for `gen_images.py` now says the script is pre-jam while every picture it has drawn for this game
  is not.

  **Checked rather than assumed, on the maker machine:** Blender **5.2.3 LTS** runs headless here with numpy
  2.3.4, glTF import and FBX export all present, so `meshy_character.py` has somewhere to run the moment a rigged
  GLB exists. ComfyUI had all three Qwen models and the 3090 was free. `Art/Refs/gen/` is git-ignored while
  `Art/Refs/*.png` is tracked and routed to LFS, so the picture a model was made from gets committed next to it.

  **Twelve renders, and two of them were because looking at the pictures changed the plan.** The first nine (three
  takes each) came back usable, and `CafeWalker` take 3 is genuinely good: every finger separated, wide gaps
  between arms and torso, which is exactly what image-to-3D needs. But the mob boss failed in a way that is
  invisible until you look: **in all three takes the cleaver blade crosses his trouser leg.** Image-to-3D fuses
  whatever overlaps, so Meshy would have returned a man with a blade growing out of his thigh, and someone would
  have spent an evening in Blender cutting it off. So we re-rolled him empty-handed and drew the cleaver on its
  own. That is the better answer anyway: a weapon on a hand socket can be swung, dropped, and lit at the edge when
  Splice charges — a weapon baked into the body can do none of that. The design doc now says the blade is a
  separate model, and the hand-off has four Meshy uploads instead of three.

  **The cast does not share a style, and we are not fixing it yet.** `CafeWalker` came out as clean cel-shaded
  anime exactly as the prompt asked. Both bosses came out heavier and grittier, closer to a western comic —
  painted leather, painted suit fabric. Same style sentence in all three prompts; the subject matter dragged the
  model somewhere else. The fix is already in the tool (`gen_images.py --ref` switches to the Qwen *edit* model
  and draws in the style of a reference picture, so the bosses can be anchored to the main character we picked)
  and it is about four minutes per boss. We wrote the command down and did **not** run it, because the team has
  not actually settled the art style — `ROADMAP.md` still has it under "Still to decide", and re-rolling into a
  look nobody has agreed to is work that might be thrown away twice.

  **One small trap closed on the way past:** `__pycache__/` was not in `.gitignore`, and importing a tools script
  creates one. Anyone running the Python tools would eventually have committed bytecode. Added, and verified with
  `git check-ignore`.

- **What we learned:**
  - **A power is not a table row.** Reassigning one ability rewrote the pitch's core-mechanic line and opened a
    question nobody had noticed was open. Change *which boss drops what* and check what the change orphans.
  - **Read the code, not the docstring**, for a script carried in from another project. The docstring named two
    files that don't exist; the code named a third. A ten-second import check beat a twenty-minute render.
  - **Some tools are the person's, not the agent's.** Paid-cloud retry economics put Meshy in a human's browser,
    and the useful thing an agent can do is prepare everything up to that door and write down exactly what to do
    at it — not find a way through it.
  - **Look at the picture, not the file list.** Nine renders "succeeded" and one of the three characters was
    quietly unusable. The blade overlapping a leg is not an error any script would report.
  - **A prop a character holds should be its own model.** It survives image-to-3D, and it is the only version the
    game can animate.
  - **A second file with "prompts" in the name can quietly undermine a declaration** that already uses the word
    for something else. Scored art makes that worth a sentence.

- **Media:** ![The main character reference sheet, first take](../media/2026-11-12-cafewalker-apose.png)
