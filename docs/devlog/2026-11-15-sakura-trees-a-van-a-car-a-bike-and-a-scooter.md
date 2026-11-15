# 2026-11-15 — sakura trees, a van, a car, a bike and a scooter, five hours before the deadline (M Station)

- **What we asked for:** nicer trees, cars and bikes on the street. The ones in the level were the city kit's
  own block models: a tree that is a green blob (960 triangles), a 798-triangle van, a 400-triangle bicycle
  and a 264-triangle scooter.
- **Prompt(s) we gave the agent:**
  > "can you pull down the latest, I am working on the latte art branch on GameStation. We need to add assets
  > for the trees, cars, and bikes. If they aren't already generated create them. You can use Gemini, ComfyUI
  > and Blender if you need. The trees can be sakura trees. Make the assets look nice not like generic fill-ins."

  The agent answered with the clock first: 12:47 PM Sunday, 5 h 12 m left, past our own "submission work only
  after noon" line, with the final build, the footage and the itch page still open. It offered four sizes of
  the job and recommended the smallest (trees only). The Team Owner picked the bigger one and named the tools:
  > "Trees, cars and bikes. Use the paid models we have access to to generate these the quickest. Gemini and
  > Meshy will probably be our best bets."
- **What happened:**
  - **Gemini, 5 pictures, about 4 minutes.** One new chat per picture, all five sent at once in separate
    tabs, first take kept for every one. The five prompts share one style block (flat anime colours, whole
    object in frame, white background, no logos) and are kept word for word in
    [`Art/Refs/Street/PROMPTS.md`](../../Art/Refs/Street/PROMPTS.md). Every vehicle prompt says "a generic
    invented design that is not any real make or model, with a blank grille and blank number plates", because
    the jam allows no trademarks.
  - **Meshy Image to 3D, 5 models, about 5 minutes, 175 credits.** On the website, not the API. All five
    queued one after another without waiting. They came back at 453,000 to 1,311,000 triangles each.
  - **Blender, two passes.** `meshy_prop_bake.py` (from our practice week) resizes, cuts the triangles and
    re-bakes the colour onto clean UVs. The first pass worked and showed four things to fix:
    1. **The texture was nine-tenths empty.** A decimated Meshy car unwraps into several hundred islands,
       and the script left a 3% margin round each one, so the hatchback's whole body sat on about a tenth of
       the picture. Re-packing the same islands tight took the filled share from a mean of 0.045 to 0.212
       (about 4.7x the texels) with no other change.
    2. **The tree was a fan.** Image to 3D only sees one side: 6.2 m wide, 1.9 m deep. Stretched before
       sizing (0.764 across, 1.36 deep) it is 4.4 x 2.4 x 4.2 m, which also keeps it out of the shopfronts.
    3. **The blossom baked with black spots.** The bake looked 22 cm outward from the low mesh, which on a
       lumpy canopy starts inside the next clump. 5 cm fixed it.
    4. **Everything faced backwards** for this kit (nose at -X; the kit builds nose at +X), and the
       hatchback was as tall as the player. Turned 180 degrees and sized to 3.1 m long, 1.47 m tall.
  - **Result:** sakura tree 21,999 triangles, van 10,000, hatchback 10,000, bicycle 12,000 (its spokes
    survived as real geometry, which we did not expect), scooter 9,000. One 2048 texture each.
  - **Not done in this entry:** nothing here is in the game yet. `tools/unreal_street_models.py` imports
    the five and swaps them onto the 26 placed actors; it is written and has not been run.
- **What we learned:**
  - Asking for the whole set at once is what made this fit: five Gemini tabs and five Meshy jobs in parallel
    took less time than one model done carefully would have.
  - A new model with one material cannot be imported over a kit model with three. The placed actors
    override materials by slot number, so the first kit material would be painted over the whole new tree.
    New asset names, and a script that changes the mesh and clears the overrides, is the safe route.
  - Look at the baked texture itself, not just the render. The render of the first pass looked fine at 512
    pixels; the texture showed the waste at a glance.
- **Media:**
  ![The five Gemini reference pictures](../media/2026-11-15-street-models-gemini-refs.jpg)
  ![The five baked models from two angles, each beside a 1.75 m figure](../media/2026-11-15-street-models-meshy-bake.jpg)
