# Latte: the pitcher follows your hand, a picture of the goal, and you serve when you are ready

*Sun 15 Nov 2026, about 11:30 AM Pacific — GameStation · UE 5.8 · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** the owner played the shift and came back with four things.

- **Prompt we gave the agent:**

  > we need a sample image of how the art is supposed to look to guide us. Once the player is done they need to
  > be able to exit the game and decide when the customer can collect their coffee. It is still difficult to move
  > the pitcher around. The cream that comes out still looks like basic shapes.

- **What happened:**

  **Stop guessing a mouse speed.** Twice the owner said the pitcher was hard to move; the first fix was a bigger
  number (0.012 to 0.08 cm per mouse count) and it was still hard. The number was never the problem: the agent
  cannot hold a mouse, so it had no way to know what a "count" is worth on this PC. The pitcher now sits **under
  the cursor**. The mini game shows the cursor, turns its ray into a point on the plane of the coffee
  (`ConvertMouseLocationToWorldSpace`, cut at the cup's height), and eases the pitcher to it. There is no speed
  left to tune.

  **The goal picture is poured, not drawn.** `tools/latte_pie.py auto heart|rosetta|tulip` pours each pattern
  through the game's own function; after Play stops, the cup's render target still holds the result, and
  `latte_build.py guide <n>` freezes it into a texture. The same surface material shows it beside the cup under
  the word GOAL. So the sample is exactly what the game can produce, in the game's own look.

  ![The goal beside the cup](../media/2026-11-15-latte-goal-picture.png)

  **You decide when it is over.** A good cup no longer ends on a timer: it waits for E. Then the latte sits on
  the counter, and the customer only gets it when you press E at the cup again. Then noon, then the register.

  **The milk.** The stream is a new 14-ring mesh, thicker at the spout with a foot where it lands, and its
  material sways it in world space. The foam carries a second value that the pour stamps in time, so the white
  comes out in fine layers as it is pushed outward, the way real microfoam shows its ripples.

- **Known flaws:**
  - **Not played by a person.** The cursor control, both E presses and the stream have never been seen with a
    real mouse: the test script moves the pitcher itself and cannot hold a button, so the stream never shows in
    its pictures.
  - Still no customer character. The cup disappears and the text says who took it.
  - The judge still counts actions, not the picture.

- **What we learned:**
  - When a tuning number is wrong twice, the design that needs the number is wrong. Pin the thing to the cursor.
  - A sample image made by the system it is a sample for can never promise something the system cannot do.
