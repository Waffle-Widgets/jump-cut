# The arms were thin, not short

*Sun 15 Nov 2026, about 6:16 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** a correction to the last correction.

- **Prompt we gave the agent:**

  > The length of his arms were fine they were just too skinny

- **What happened:**

  The owner said "shriveled". I measured his arms against a person, found them 10 cm short, and lengthened them
  15 %. That was the wrong reading: the table compared him with a real adult and he is an anime character, drawn
  with the proportions the owner chose. The word was about thickness.

  `model_tuneup.py` now leaves the length alone (`ARM` 1.0) and thickens: every vertex the upper-arm and forearm
  bones carry moves straight out from its bone's own line, by its weight, times 1.25 (`THICK`). 1.18 was rendered
  first and was hardly visible. Shoulder to wrist is back to 48.7 cm. The head centring from the last entry stays.

  Because the last entry changed the rest pose, putting the length back meant rebuilding all 13 clips and
  re-importing them and the body a second time. The body importer's size guard went back to its original numbers.

  ![The idle: original arm length, thicker arms](../media/2026-11-15-idle-thick-arms.png)
  ![In the game](../media/2026-11-15-idle-thick-arms-in-game.png)

- **Known flaws:**
  - Only the idle was seen in Play. Attacks and the run on this body were checked by their numbers and two Blender
    frames, not in the game.
  - The death clip still was not rebuilt.
  - The legs are still uneven (knees 3 and 14 degrees).

- **What we learned:**
  - A number from a real person is evidence about a real person. For a drawn character it is one opinion, and the
    owner's eye is the other. Ask which one a word like "shriveled" means before changing a skeleton.
  - A rest-pose change costs a full rebuild each way. This one was paid twice in half an hour.
