# 2026-11-15 — six small cafe pieces, and Google decides we are a robot (M Station)

- **What we asked for:** the last of the cafe's block models: what sits on the tables, the wall art, the
  clock, the rug, the awning over the door and the doorway curtain.
- **Prompt(s) we gave the agent:** the agent offered them after the nine furniture pieces went in, and the
  Team Owner answered:
  > "Yes, make them"
- **What happened:**
  - **Gemini stopped at the door.** All six tabs opened onto Google's "unusual traffic" page asking us to
    prove we are not a robot. We have sent it 28 pictures from this browser today, 23 of them in two
    bursts of parallel tabs, so it has a point. An agent does not solve a robot check, so that was the end
    of Gemini for the day. It also cost ten minutes: the script waited its full timeout on every one of the
    six tabs before reporting, the second time today a parallel batch failed slowly.
  - **Meshy's own "Generate Image" button** led to a chat-style agent page instead of a picture box. Not
    something to learn with two hours left.
  - **ComfyUI on the 3090 did it.** `tools/gen_images.py --text` with the same six prompts
    ([`prompts_batch4_cafe_small.json`](../../Art/Refs/Street/prompts_batch4_cafe_small.json)), 1024 x 1024,
    20 steps: 56 seconds a picture, 6 minutes for the six, first take kept for all. Nothing left the machine.
    They are as usable as Gemini's were; the tray of cups is better.
  - **Meshy, 6 models, 210 credits**, uploaded from disk this time.
  - **The size table was in the other program's coordinates.** GameStation, importing the last batch, found
    that the kit's wall props stick out the opposite way from what M Station assumed, which is why the cash
    register arrived backwards. The reason: `city_models.json` records each kit model's box in **Unreal's**
    axes, where front-to-back is mirrored against Blender's, and the bake script works in Blender's. Fitting
    a model "exactly into the kit's box" with that table therefore puts a wall piece on the wrong side of
    its wall. Nothing symmetric shows it, which is why nine pieces went in before anyone noticed. For
    these six the axis is flipped before fitting. Two earlier pieces carry the error: the chalkboard sits
    about 17 cm further into its wall than the kit one, and the door sign about 34 cm along it. Both were
    reported as looking right in game, so they have been left.
  - **The awning was drawn standing on posts.** The kit's hangs off the wall, and two posts either side
    of the cafe door would be two new things to walk into, in a model whose collision is its own triangles.
    `PROP_CUT_BELOW=0.5` deletes the lower half before anything else happens.
  - **Result:** 6 models, 2,500 to 6,086 triangles (the rug would not reduce to 2,000: its fringe is
    hundreds of separate strands).
- **What we learned:**
  - Have a second way to do every step before the deadline day, and know it works. The local picture model
    had been on this machine all week and was the first thing that did not need anybody's permission.
  - A table of numbers has a coordinate system. Ask which one before using it to place something.
  - Every script that loops over tabs or files now needs to fail on the FIRST bad one, not the last.
- **Not done:** none of the six is in the game. GameStation has the names and adds them to the import tool.
- **Media:**
  ![The six small cafe pieces as baked](../media/2026-11-15-cafe-small-pieces-meshy-bake.jpg)
