# The latte becomes a shift: an order, a pour, noon, and clocking out

*Sun 15 Nov 2026, about 11:15 AM Pacific — GameStation · UE 5.8 · by Fable 5.2 (`claude-fable-5-2`) · branch `Gamestation/latte-art`, NOT in the build*

- **What we asked for:** the owner played the first latte mini game and wanted it to be a scene, not a gate.

- **Prompt we gave the agent:**

  > We need to move the cutscene until after this part of the game is done. Let's open up the scene where an order
  > comes in for a latte and the player picks up the cup to start the latte art mini game. Once the player
  > completes the mini game and the customer picks up the latte the clock hits noon and the player's shift can be
  > over. The player has the option to clock out at the register (the register should be flipped around so it can
  > be accessed from behind the counter). The player should have an open path to the register to be able to clock
  > out. Once the player clocks out Justin's cutscene plays. A few things I noticed while playing the minigame,
  > the pouring doesn't look fluidic and it looks very basic, and the sensitivity seemed very low, it was
  > difficult to move the pitcher did not move much.

- **What happened:**

  **The shift is five steps on one number** (`BP_LatteGame.Shift`): an order is in, pouring, served, noon,
  clocked out. Text in front of the camera says what to do; E at the cup starts the pour; E at the register
  clocks out.

  **How the player walks around before the cutscene without touching the director.** `BP_OpeningDirector`
  starts the opening the moment the player's input unlocks. So the input stays locked for the whole shift, which
  also keeps attacks off, and `LatteWalkStep` walks him itself: it reads W A S D and the mouse and feeds
  `AddMovementInput` and the controller. Clocking out is the unlock, and the director's own rule does the rest.
  No change to Justin's Blueprint.

  **The path was closed by something invisible.** A capsule sweep round the end of the counter stopped at
  y -306 on `C1_Cafe_Counter`: Thursday's grey-box counter, hidden in game and still colliding. Collision off;
  all six legs of the route (start, round the end, to the cup, to the register) now sweep clear. The register
  is turned to face the staff side, in the level and in `jumpcut_city_layout.py`.

  **A graph that read one thing and meant another.** `(Pawn|GetControlRotation :self pawn)` compiled, and at
  run time threw *"Accessed None trying to read property LastHitBy"*. The tool had picked the *controller's*
  version of that node and quietly inserted "the controller that last hit this pawn" to make the types fit.
  Asking the player controller directly fixed it. Reading the graph back is what showed it.

  **The pour.** Mouse speed is 6.7 times higher (0.012 to 0.08 cm per count). The surface now has thickness
  (an emboss from the foam's own edge), ripples that run out from the spout while you pour, a tan cut line
  instead of a black one, and a slow drift so edges are not ruler-straight. The first try at that drift was ten
  times too strong and shredded the rosetta into confetti.

  ![The rosetta with the new surface](../media/2026-11-15-latte-rosetta-embossed.png)
  ![Noon](../media/2026-11-15-latte-noon.png)

  **A false alarm worth knowing.** Twice the cup came out black and the pattern wrong straight after rebuilding
  the materials. Nothing was wrong: Play had started while the shaders were still compiling, so Unreal drew its
  grey default material. Wait for the compile before judging a picture.

- **Known flaws:**
  - **Nobody has played this version.** The whole shift was driven by script (`tools/latte_pie.py`): the E
    presses, the walking and the mouse are untested by a person. Keyboard and mouse only, no gamepad.
  - **There is no customer.** The cup disappears and the text says a customer took it. We have no customer
    model; making one is a model and a rig.
  - The pitcher is still a cone and the milk stream a plain cylinder.
  - The judge still does not look at the picture: a rosetta passed as a heart in the test.
  - The player is behind the counter when the car arrives. Whether the opening still reads from there is not checked.

- **What we learned:**
  - A hidden grey box is still a wall. Sweep the route before promising a path.
  - If a rule already exists ("the opening starts when input unlocks"), build on the rule instead of editing
    the thing that owns it.

- **Later the same hour: a real cup and pitcher.** `Art/Blender/latte_kit.py` builds the cup (with a handle), the
  saucer and a milk pitcher with a pulled spout from profiles, and exports the pitcher already tilted with its
  origin at the spout tip, so the Blueprint only moves it. They came into the game **black**: the cup sits on
  the staff side of the counter, in shadow, and the cel look turns a lit material in shadow to ink. A plain
  unlit colour had no form at all. `M_LatteCup` and `M_LatteSteel` are now unlit with their own soft light
  written into the material, so they read from either side of the counter.

  ![A real pitcher pouring a heart](../media/2026-11-15-latte-real-pitcher.png)

  One more trap: the tool that shows the agent a picture cached it by file name, so an hour-old screenshot came
  back in place of a new one with the same name. Copy a capture to a fresh name before looking at it.
