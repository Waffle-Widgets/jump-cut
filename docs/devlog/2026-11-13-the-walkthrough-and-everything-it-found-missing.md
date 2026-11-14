# 2026-11-13 — The walkthrough, and everything it found missing (M Station)

- **What we asked for:** look at the game itself on M Station to see what art is still missing, write tickets
  for it, and start making it, while Justin imports the models that already exist on his Mac mini.

- **Prompt(s) we gave the agent:** the actual words, quoted:

  > If you need to do a walkthrough in the game to see what asset they're missing, do so on mStation. After
  > the walkthrough, create tickets for any assets that still need to be created and start working on those.
  > Justin is working on importing the assets on his Mac Mini.

- **What happened.**

  **The walkthrough is a script, not a person with a controller.** M Station is a maker: it must never save an
  Unreal file. So `tools/asset_walkthrough.py` opens `Lvl_JumpCut`, writes down every placed actor with its
  mesh and materials, asks the asset registry what every Blueprint and widget references, flies the editor
  camera to eighteen places along the route (cafe, street, boss lot, the run past it) and takes a picture at
  each, then quits. It saves nothing. The one file Unreal touches by being opened (`DefaultEngine.ini`, a
  generated security token) was restored afterwards.

  **First run: a list and no pictures.** `-ExecutePythonScript` closes the editor the moment the script
  returns, and a screenshot needs frames to pass. The census was already on disk by then, so nothing was
  lost. The second run used `-ExecCmds="py ..."`, which leaves the editor running; the script counts editor
  ticks, takes its eighteen pictures and quits itself. About a minute each.

  **What it found on `main` at `27fdc7c`: 291 actors, 26 of them visible placeholders.**

  - The crashed car is still two red boxes, the coworker a green box, the player Epic's mannequin, the gates
    yellow slabs, the boss lot six grey walls on a grey floor. **All of those already have models** and are
    waiting on the builder (#40, #5, #6, #7). Nothing to make. (Justin merged #40, the set pieces, while
    this entry was being written, so the car, the walls, the gates and the checkpoint are no longer boxes.)
  - **No Blueprint or widget in the game references an effect or a texture, and only `BP_Player` references a
    sound** (the three countdown ones). That confirmed tickets #42, #43 and #44 from the game's own asset
    registry instead of from reading files.
  - **One thing no ticket had: eleven spheres.** The "press F" prompt over the driver, the rescue prompt over
    the coworker, the warning over every enemy's head and five scene markers are all the engine's sphere in a
    flat colour. They are the things the game uses to *tell the player what to do*. That is ticket #49.
  - The boss lot is a 30 m square with nothing in the middle and very little at the edges. Filed as #50, not
    started: it is a layout change, and Justin is running the placer on that layout right now.

  **Then we made the four sets that were on the board, plus the new one.**

  **Sounds (#43): twenty, from the same synth as the first three.** `make_jumpcut_fight()` in
  `tools/make_sfx.py`: the three-hit combo (the third lower and longer), hits taken and given, a goon going
  down, the cleaver, the boss going down with the cleaver ringing on the ground a beat later, the car through
  the wall with glass, the explosion, both powers being taken, Freeze Frame switching on, the Splice blink,
  the checkpoint, the gate, and stings for the title, win and lose screens. Sine, square, triangle and noise
  only. The three existing sounds were regenerated in the same run and are byte-identical, checked by hash,
  so nothing Justin already imported changed under him. **Nobody has heard any of them**: this session has no
  ears. Peak and loudness were measured so none clips or is silent, and that is all that was checked.

  **Effect sheets (#42, #49): drawn from code, not generated.** `tools/make_fx.py` uses numpy and Pillow. Our
  own practice lesson is that solid shapes with a dark outline read at the game camera and painted texture
  does not, and an image model paints texture. So the explosion is four flat tones with a ragged edge from
  seeded noise, eaten from the inside until only smoke is left: 36 frames. The rest: a hit flash, focus
  lines, the Freeze Frame screen overlay, the Splice trail, a ground ring that is a film countdown leader, a
  scene marker, an interaction prompt, the attack warning, and three HUD icons.

  **Two bugs, both invisible in the numbers.** Every explosion frame whose cloud reached the top of its cell
  had a dark line underneath it: the outline was grown with `np.roll`, which wraps around, so the outline of
  the top edge came out at the bottom. And three sheets started with an empty frame, because frame 0 was
  time 0 and nothing has happened yet at time 0; on a sixteen-frame hit flash that is a sixteenth of the
  effect spent showing nothing. Both were found by looking at the sheet on a grey card.

  **Poses (#45): the importer hands you a pose you did not ask for.** `Art/Blender/pose_clip.py` reads the
  committed FBX, poses the same skeleton and writes a one-clip FBX beside it. The coworker's "down" pose came
  out hovering 20 cm above the floor. We blamed her ponytail first (it does stick out behind her head) and
  taught the script to ignore hair when finding the floor. It made no difference. Printing the *rest*
  position of the lowest vertices showed a foot 36 cm behind her: an FBX stores the bind pose **and** the
  pose the rig was in when it was exported, which was frame 0 of Walk, and Blender applies that second one
  on import even with animation off. Every pose was being built on top of a walking stride. Clearing the
  pose bones after import fixed all three, including the driver's, which had looked fine and was wrong by
  the same amount. The ponytail rule stayed, because it is still right.

  The poses are written as world-space rotations (lean back 14 degrees, this thigh forward 78), not in each
  bone's own axes. Meshy's rig gives every bone an arbitrary local axis, so a pose written in local axes for
  the driver would be a different pose on the coworker.

  **Screen art (#44): five pictures on the 3090, no lettering in any of them.** `UI-TITLE`, `UI-WIN`,
  `UI-LOSE`, `UI-TBC` and `UI-COVER` in `docs/prompts.md`, drawn with ComfyUI and Qwen-Image like the cast.
  Each prompt asks for a calm area and says where, so the game's name and every word are set in Unreal on
  top. Generated letters are unreliable and a generated logo is a rules risk (15d). One win-screen take came
  back split into two panels and was dropped.

- **What we learned:**
  - **Ask the game what it references, not the files.** The asset registry answered "which Blueprints play a
    sound" for all twenty in one call, and it cannot be out of date the way a ticket can.
  - **`-ExecutePythonScript` quits when the script returns.** Anything that needs frames (a screenshot, a
    camera move) wants `-ExecCmds="py <script>"` and a tick callback that quits the editor itself.
  - **A maker computer can look.** Opening the level, reading it and taking pictures saves nothing. The rule
    is about saving, and the script never does.
  - **After importing a rigged FBX into Blender, clear the pose bones before you measure or pose anything.**
  - **`np.roll` wraps.** Pad instead, for anything that grows a shape near the edge of a sprite cell.
  - **A flipbook's first frame should already show something.**
  - **A check that passes for the wrong reason:** the driver's pose looked right while built on the wrong
    base. One character that is visibly wrong is a reason to re-check the ones that look fine.

- **Not done, said plainly:** nothing here has been in Unreal. Every sheet, sound, picture and clip is a file
  under `Art/`; the builder's side is ticket #52. No one has heard the sounds or seen an effect at the game
  camera. The boss lot's dressing (#50) and music are not started.

- **Media:**
  ![Six of the eighteen walkthrough pictures: the cafe with its red-box car and green-box coworker, the plaza gate, the cleaver boss in the empty lot, the exit run](../media/2026-11-13-walkthrough-route.jpg)
  ![The effect sheets on a grey card: the 36-frame explosion, the hit flash, the attack warning, the prompt, the ground ring, the marker, the Splice trail and the three HUD icons](../media/2026-11-13-effect-sheets.jpg)
  ![The three poses, each from the front, the side and three-quarter: the driver slumped, the coworker down, the coworker flinching](../media/2026-11-13-poses.jpg)
  ![The five screen pictures: title, win, lose, to be continued and the itch.io cover](../media/2026-11-13-screen-art.jpg)
