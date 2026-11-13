# 2026-11-12 — The cast drawn from words alone (M Station)

- **What we asked for:** draw the three characters and the cleaver again in Gemini, in a brand-new chat, with no
  ComfyUI picture given to the model — only prompts the agent writes.

- **Prompt we gave the agent:**

  > regenerate those with Gemini without using the images from ComfyUI. Use a new chat in Gemini with only the
  > prompts you create.

- **What happened:**

  **The point of the ask, as we understand it.** The previous pass uploaded the old ComfyUI pick with each
  prompt, to carry the costume across. That works, but it hands the model the *drifted rendering* as well as the
  design, and an image model copies what it is **shown** more faithfully than what it is **told**. Removing the
  upload forces every line of each design into text. The pictures are the visible output; the prompt file is the
  durable one.

  **So the first thing written was not a picture, it was `docs/prompts-gemini.md`** — four self-contained prompts
  assembled from `CHARACTERS.md`, each built from the same four blocks: the style stated as *drawing
  instructions* rather than as a style name, an explicit "this is not a reference sheet", the A-pose
  requirements, and a list of the texture failures we have actually hit. It is deliberately a separate file from
  `docs/prompts.md`, because that one is parsed by `tools/gen_images.py` and a code added there becomes something
  the local ComfyUI script will draw.

  **Six renders, four keepers, in a new chat (`3a8078099d39ce5e`).** Create image on, model 4 Hydrogen, 3:4 for
  the figures and 4:3 for the cleaver, nothing attached. The main character went first and became the style
  anchor; the others were told to match *the picture you just made*. The mob boss and the cleaver were right on
  take 1 — the boss is the best style match of the three, and his hands are empty as the socketed-weapon decision
  requires.

- **What went wrong, and what we learned:**

  **The frost spikes would have broken the Meshy model, and we only caught it by looking.** The crash driver's
  take 1 is a genuine success on the thing that had failed twice before: the leather is flat and clean, and the
  frost reads as hard angular ice rather than as the white fur trim both earlier tools produced. But those
  crystals **stick out past his shoulder into empty space**, and image-to-3D turns a thin protruding spike into
  either a fused blob or a shard floating off the mesh. Take 2 asked for the ice as flat angular plates lying
  *on the surface* of the jacket with nothing crossing the silhouette, and that is the pick. The general rule —
  **nothing protrudes from the outline** — now belongs in every A-pose prompt we write.

  **Asking for one change re-rolls everything else.** The main character's take 1 has the design exactly right
  but his legs close together, which is the same fusion risk at the inner thigh. Asking for "the same man, wider
  stance" produced a wider stance *and* silently changed his hair from black to brown, his expression from tired
  to smiling, his shirt to a collared one, his grey sneakers to brown leather shoes, and deleted the folded cloth
  at his apron tie. Both takes are kept and neither is picked; the lesson is that for anything other than a pose
  change you edit the prompt and draw fresh rather than asking for a tweak.

  **Two browser traps cost time and are worth recording.** Gemini's *Download full size image* button did not
  fire a download in this session at all — not on the first click and not on a retry — so every picture here was
  taken off the page as the 765×1024 display copy via canvas rather than the ~1792×2400 original. Good enough to
  judge a design, and we should get the full-size files before any of these goes into Meshy. And after a page
  reload, filling the composer and pressing Enter leaves the prompt sitting there **unsent**; the send button has
  to be clicked. That silently cost two generations' worth of waiting on an image that was never queued.

  **Honest read of the result.** Across the cast the text-only pass is flatter, lighter and more consistent than
  the uploaded-reference pass, which is what we wanted. It is not a dramatic difference, and anyone judging it
  should look at `Art/Refs/gen/gemini2/TEXT-ONLY-COMPARISON.jpg` rather than take this paragraph's word for it.
  One thing did get slightly worse: the figures in this pass stand with their legs closer together than the
  earlier ones, which matters only because of Meshy.

- **Where it stands:** six pictures in `Art/Refs/gen/gemini2/`, which git ignores, so they exist **only on M
  Station** until a pick is committed. Nothing has been through Meshy — the three rigged characters on `main` are
  still the ones built from the ComfyUI pictures. No Meshy credits were spent this session.

- **Still open:** which `CafeWalker` take to use, and whether to spend the 140 credits rebuilding the cast from
  this pass.
