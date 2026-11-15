# He sprints after the first power, and a blend space that lied about what it plays

*Sun 15 Nov 2026, about 5:40 AM Pacific — GameStation · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the sprint clip had been authored against the owner's photographs of real sprinters and
  imported, but nothing played it. Making him faster is a gameplay change after feature freeze, so the agent asked
  first.

- **Prompts we gave the agent:**

  > After he get's the first power he should be able to sprint like an actual sprint.

  and, to the question "Raise his speed after the first power so the sprint plays?":

  > Yes, make him faster

- **What happened:**

  **The smallest change that does it.** Nothing in `BP_Player` touched his speed, and the first power is granted in
  a one-line function. `PlayerGrantFreezeFrame` gained one node: set `MaxWalkSpeed` on his movement component to
  850 (it is 600 until then). The DSL node id was a guess among five; the first one,
  `Class|CharacterMovementComponent|SetMaxWalkSpeed`, took. Read back as four nodes with nothing orphaned, compiled.

  The blend space's speed axis was stretched from 600 to 900 and given a sprint row at 900 (its grid is in 300s),
  played 900/850 faster because the clip is authored for 850. At 850 he plays five parts sprint to one part run.

  **Then the test said his speed was right and his body was wrong.** In Play: 600 before the grant, 850 after.
  But the picture showed him WALKING upright at 850. So the lean was measured in the running game - how far his
  head is in front of his hips - and compared with each clip's own:

  | speed | lean in the game | what the blend should give |
  |---|---|---|
  | 439 | 43 cm | about 15 (walk 5, run 17) |
  | 600 | 33 cm | 17 (the run) |
  | 850 | 10 cm | about 41 (sprint 46, run 17) |

  He leaned like the sprint while accelerating and like the walk at full sprint. The blend space's contents read
  back perfectly: 36 samples, the right clip at every speed.

  **The cause is in the engine source.** A blend space plays from a triangulation that stores sample INDICES.
  `UBlendSpace::ResampleData` rebuilds it, and the only callers an edit can reach are in the blend-space EDITOR
  widget: `SBlendSpaceEditor`'s construction and its property-changed hook (`SAnimationBlendSpace.cpp:105-108`).
  `set_editor_property` on `sample_data` or `blend_parameters` does not rebuild it. The script had put the nine new
  sprint samples at the FRONT of the array, so the stale triangulation's "walk" indices now pointed at the sprint,
  its "run" indices at the walk, and its "idle" indices at the run.

  The cure is one line of intent: open the asset's editor (which rebuilds), save, close it.
  `tools/unreal_player_authored_wire.py` does that now and says why.

  | speed | lean in the game, after |
  |---|---|
  | 302 | 4 cm |
  | 600 | 15 cm |
  | 850 | 39 cm |

  ![In the game: the run at 600, then the sprint at 850 after the power is granted](../media/2026-11-15-run-then-sprint-in-game.png)

  Swapping the CLIP on an existing sample - which is all this script had done all night - never needed a rebuild,
  because the indices did not move. That is why this hid until a sample was added.

- **Not verified:**
  - The grant was triggered by calling `PlayerGrantFreezeFrame` from a script. Nobody has earned the power by
    playing the opening and felt the change.
  - 850 against 600 is a 42 % faster hero for everything after beat 1. Jumps, enemy chase speeds and the camera
    were tuned at 600. That needs a person to play the whole level.
  - A level restart was not tested: the speed should go back to 600 with a fresh player, by construction.

- **What we learned:**
  - "The data reads back right" and "the game plays it right" are different claims. Measure in the running game.
  - One number measured in Play (how far the head is ahead of the hips) settled in a minute what a screenshot
    only hinted at.
  - When a tool has done one kind of edit safely a hundred times, the hundred-and-first kind is not covered.
