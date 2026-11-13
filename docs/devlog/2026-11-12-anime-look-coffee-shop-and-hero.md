# 2026-11-12 — A hand-drawn anime look, a coffee shop and a hero (GameStation)

- **What we asked for:** A look that feels like watching a hand-drawn anime while you control the character, tried out
  on the game's opening scene (the coffee shop), so the team can decide whether to use it.
- **Prompt(s) we gave the agent:** "Can you make a level where we can walk around in 3D as a person in a coffee shop.
  Our main focus is that no matter from what angle it looks like we are watching a hand drawn anime." /
  "This needs to look better or it'll be scrapped" / "Are there any partner companies that can help us make assets?" /
  "looks better but movement is really rough for the player model right now and the arms look weird when he moves" /
  "his jacket is stuck to his arms and the legs look like the bow inwards" /
  "can we move what we did here for this starting scene into the new repo so Justin can see the demo"
- **What happened:**
  - Where it was made: in our practice project on GameStation, in the first hours of the jam (after the 9 PM start on
    Nov 11), then moved here with Unreal's Migrate. Every script that builds it is in this repo.
  - First version: one post-process material that cel-shaded everything. It read as a flat cartoon, and the owner said
    so. The fix was to do what anime does: paint the background, cel-shade only the characters. Characters draw into
    Unreal's custom depth, and the same material uses that as a mask: two flat tones and a rim light for them, real
    light with a brush filter and thin lines for the room. Low golden sun and drawn sunbeams did the rest.
  - Unreal's fog gave no visible light shafts indoors, so the beams are see-through slabs drawn after the look.
  - The whole coffee shop is built by a script from cubes, cylinders and flattened balls (the plant leaves).
  - The hero: Gemini drew him, our local TRELLIS model was lumpy from the side, so we tried the jam partners. Tripo and
    Meshy both made him from the drawing in two minutes; Tripo's face and hair were clearly better.
  - Movement took four rounds. Our script-keyed walk looked rough, so Claude copied Unreal's motion-captured mannequin
    animations onto him with the IK Retargeter (Unreal recognised the skeleton our Blender script builds). Then the
    jacket stuck to his arms: he was modelled arms-down, so sleeves and body were one surface. Tripo's image tool redrew
    him in an A-pose and we made the model again.
  - Claude's own bug cost three failed attempts: on an arms-out model its Blender script measured the "chest" through
    both arms and put the shoulder joint halfway down the upper arm. It only found this by measuring joint positions
    in the animation instead of guessing from pictures.
  - Claude cannot press keys, so it checked the walk by pushing the character along from a script in Simulate mode and
    freezing time for pictures. The owner did the real play tests and caught every one of the problems above.
- **What we learned:** Paint the backgrounds and cel-shade only the characters. Model characters in an A-pose. When an
  animation looks wrong, print the numbers (joint positions) before trying another fix.
- **Media:** ![before and after of the room](../media/anime-cafe-film-look.jpg)
  ![the scene running in this project](../media/anime-cafe-jumpcut.jpg)

_Written on the branch `mendezm87/anime-look` as a demo for the team to judge; the team chose this look later the same day (see `docs/ROADMAP.md`, Decisions). Moved here from the old single-file devlog when the branch was merged._
