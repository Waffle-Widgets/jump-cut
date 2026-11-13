# 2026-11-12 — The style gets decided, and the cast is redrawn in Gemini (M Station)

- **What we asked for:** the cel-shaded anime look is the one we are going with. Draw the characters in Gemini so
  we can see them before any more Meshy models get made.

- **Prompt we gave the agent:**

  > We are going with the cell shaded anime style look. Generate these in Gemini to see what they would look like
  > before creating anymore meshy models.

- **What happened:**

  **The art style stopped being an open question.** It had been sitting under *Still to decide* in `ROADMAP.md`
  since the roadmap was written — which is why the previous session refused to spend GPU time fixing the boss
  style drift, on the grounds that re-rolling into a look nobody had agreed to means doing the work twice. It is
  now a line in **Decisions**, and the undecided bullet is gone, because the file's own rule says nothing is ever
  in two places.

  **Four pictures, one conversation.** The real reason to use Gemini here rather than another `gen_images.py` run
  is not that it draws better. It is that the problem was **consistency across a cast**, and a conversation can
  carry a style forward while a one-shot prompt cannot. All four were drawn in a single chat: the main character
  first, as the anchor, then each of the others told in as many words to match *the picture you just made*, not
  the picture being uploaded. The uploads were the old ComfyUI picks, there to carry the costume design across —
  each prompt said outright that the upload's rendering was the thing being thrown away.

  **The main character came out right on the first take.** The mob boss did too, and he is the closest match of
  the three — flat, bright, large hard-edged shadow shapes, a clean even outline.

  **The crash driver took two, and that is the reusable lesson.** A leather jacket drags an image model toward
  texture, and take 1 came back dark, busy and covered in scuff strokes — the same failure the ComfyUI pass hit,
  from the same cause, even with the style named explicitly. What fixed it was *not* repeating the style words. It
  was naming the specific failures: delete the scuff strokes, raise the value to match the anchor, two or three
  big flat shadow shapes per garment, a face of a few clean lines rather than rendered wrinkles. The frost on his
  shoulder had also come back as **white fur trim** — twice now, across two different tools — and what finally
  made it read as ice was describing the shape rather than the material: *"sharp angular pale cyan crystals with
  crisp geometric edges, not soft, not fluffy, not feathery."* He is still the darkest and busiest of the three.

  **The browser work, so nobody re-derives it.** `Create image` has to be toggled on or Gemini answers in prose.
  The model was switched off `4 Argon` (code and analysis) to **`4 Hydrogen`**. Aspect ratio defaults to 1:1,
  which wastes half the frame on a standing figure — **3:4** for the people, **4:3** for the cleaver. And the
  image in the page is only a 765x1024 display copy: the **Download full size image** button gives the real
  1792x2400 file, which is what we keep. Scraping the page gets you the thumbnail.

- **What went wrong:**

  - **Three different ways of getting the picture out of the page failed before the obvious one worked.** Fetching
    the blob URL failed, drawing the newest image to a canvas threw `SecurityError: Tainted canvases may not be
    exported` because it is served cross-origin, and `curl`-ing that URL returned **403** without session cookies.
    The answer was the download button that had been on screen the whole time. Two of the pictures had already
    been pulled the scrape way before this was noticed, at less than half the resolution.
  - **A programmatic `.click()` on the download button did nothing.** It needs a real user gesture. The fix was to
    tag the buttons with an attribute from the page and then click them through the driver.
  - **The drift was caught too late to be free.** The three rigged models on `main` were all built from the
    ComfyUI pictures, so the drifted rendering is baked into `SK_CrashDriver` and `SK_CleaverBoss` and their
    textures. Rebuilding the cast from this pass costs 140 Meshy credits and the two-press rig flow over again.
    Had the style been settled before the first Meshy run, it would have cost nothing.

- **What is still open:** nothing from this pass has been through Meshy, so the cast in the repo is still the
  drifted set. The pictures are in `Art/Refs/gen/gemini/`, which git ignores, so they exist only on M Station
  until somebody picks them — `STYLE-COMPARISON.jpg` in that folder puts the two casts side by side, which is the
  thing to look at before deciding. And **Rewind still has no home** (`ROADMAP.md`, *Still to decide*), which is
  what Thursday's "player + the first power" is actually waiting on.
