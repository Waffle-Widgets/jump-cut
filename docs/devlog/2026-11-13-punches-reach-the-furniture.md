# 2026-11-13 — Punches reach the furniture (Justin's Mac mini)

- **What we asked for:** item 5 of the beats 1-3 clean-up list:

  > We needs to implement chaos physics for the environment

- **Prompt(s) we gave the agent:** the line above, then "continue".

- **What happened:**

  **Scope, decided before building.** "The environment" could mean every object in a 224-piece city. We took the
  props a fight actually touches along beats 1 to 3 and split them in two:

  | | What | How many | Where |
  |---|---|---|---|
  | **Break** (Geometry Collections) | crate stacks, road barriers, cafe tables | 12 | cafe, the street fight, the plaza |
  | **Knock** (ordinary physics bodies) | cafe chairs, traffic cones, one pile of trash bags | 12 | cafe, the street fight, the plaza |

  Buildings, lamps, vending machines and everything else stay solid. Nothing was deleted: each original prop is
  hidden with its collision off (the city placer still owns it) and a breakable stands in the same spot.

  **How a punch reaches them.** `BP_Player` gained one function, `PlayerSmashProps`, called once from
  `PlayerPunch`. Anything breakable inside the punch arc gets strain at its middle (which cuts the bonds between
  its pieces) and a push; anything knockable gets a shove away from the player and slightly up. The finisher
  breaks a wider radius and pushes harder. The recipe is `tools/chaos_props_graphs.py`, the assets and placement
  are `tools/unreal_chaos_props.py`, and the play test is `tools/chaos_props_test.py`.

  **It took four play tests, and each one failed differently.**

  1. **The crate left the plaza.** One light punch and the pieces were 35 metres away and still going. The same
     call made from a script on a road barrier scattered it a metre and a half. So we measured instead of guessing:

     | Breakable | Push asked for | Speed the pieces left at |
     |---|---|---|
     | crate stack | 350 cm/s | **2,516 cm/s** |
     | crate stack | 30 cm/s | 191 cm/s |
     | road barrier | 350 cm/s | 199 cm/s |
     | cafe table | 350 cm/s | 250 cm/s |

     The crate stack answers the same push about seven times harder than the other two. We did not find out why
     (our guess, unchecked: it is several separate boxes, so it shatters into more, lighter pieces). Crates carry
     a `JC_BreakSoft` tag and get 0.15 of the push.
  2. **Nothing knockable moved.** Two separate reasons. `set_simulate_physics(True)` on a placed actor reads back
     fine and does not persist; the body instance itself has to be written. And the city kit's meshes use their
     render mesh as collision (a fix from earlier today), which Unreal refuses to simulate at all - it says so in
     the log and carries on. The three knockable meshes went back to a simple box.
  3. **A bag of trash went into orbit.** Punched toward the plaza wall, it finished 16 metres up and still
     climbing: it had been driven into the wall and was thrown back out. Halving the shove, switching on
     continuous collision and capping the speed a body may be ejected at (120 cm/s) fixed it. Two other trash
     piles turned out to be resting on a kerb and floated 15 and 64 cm up as soon as they simulated; those two
     stay static.
  4. **Clean.** Below.

  **Measured in Play mode** (the fourth run; the player teleported to a plaza crate, far from any goon):

  | Check | Result |
  |---|---|
  | The 12 knockable props, 2.5 s after play starts | all 12 at rest, none more than 1 cm from where it was placed |
  | Crate stack before any punch | 104 x 54 x 90 cm |
  | After one light punch | 242 x 166 x 106 cm and settling |
  | After the full combo, 1.7 s later | 308 x 170 x 114 cm, not moving |
  | Trash bags, one light punch | left at 324 cm/s, came to rest 107 cm away on the floor |
  | Player health either side | 100 and 100 |

  **Rewriting a graph left a second copy behind, again.** After the first rewrite the function had 126 nodes
  instead of 66. This time the stale copy was *not* on the execution path - it hung off the shared input pin - so
  it would not have run twice, but it was 60 dead nodes in a saved Blueprint. A short script now walks the
  execution chain from the entry node and deletes whatever it cannot reach.

- **What we learned:**
  - **Measure the push per asset.** The same number means a seven-fold different speed on two breakables.
  - **A prop that has to simulate needs simple collision.** "Use the render mesh" is right for walls and wrong
    for anything that moves, and Unreal only mentions it in the log.
  - **`set_simulate_physics` in the editor is a preview, not a setting.** Write the body instance.
  - **Cap ejection speed on anything a player can punch into a wall.**
  - **Check what a prop is resting on before letting it go.** Two of fourteen were sitting on something else.
  - **Not checked:** nobody has watched any of it. The numbers say things break and land; whether it *looks*
    good is a person's call. Not tested at all: props during Freeze Frame (they will keep moving while time is
    stopped, which may read as wrong), goons walking through debris, the cafe tables in the beat-1 scene, frame
    rate with several broken at once, and a packaged build. The level was not reloaded from disk afterwards;
    all 36 actor files and the folder object show as written in git.

- **Media:** none; the result is the tables.
