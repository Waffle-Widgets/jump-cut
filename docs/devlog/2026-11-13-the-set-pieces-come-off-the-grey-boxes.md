# 2026-11-13 — The set pieces come off the grey boxes (Justin's Mac mini)

- **What we asked for:** work the GitHub board — comment and close what we have already done, then do the
  tickets assigned to this machine.

- **Prompt(s) we gave the agent:** the actual words, quoted:

  > Another agent made github issues out of tasks to be completed. Take a look and comment and close on
  > anything we've worked on already. Then do any that were assigned to us that are still pending

- **What happened.**

  Four tickets were assigned to this Mac — **#40, #5, #7, #6** — in that order, by a comment M Station left
  on #40 at 00:54 UTC. This entry covers **#40**, the set pieces.

  **The eleven models were waiting and the script to place them had never been run anywhere.**
  `tools/jumpcut_city_place.py add` is a mode the city placer gained after the city was already in the level;
  its own header says to expect to fix a line. It ran clean first time: 21 new actors placed beside the 224
  already there, 18 grey boxes hidden, asphalt on both floor actors.

  **Then the four Blueprint meshes, which the script deliberately does not do.** `BP_PlazaGate.GateMesh`,
  `BP_Checkpoint.PostMesh` and `.TakenSign`, `BP_Shrapnel.ShrapnelMesh` were all the engine's basic cube,
  scaled. Each is now its own model at scale (1,1,1), with the city materials on its slots — except the
  checkpoint's "taken" face, which keeps `M_CheckGreen`, because the green **is** the signal that you took it.

  **The one that would have cost us a feature.** `prepare_meshes()` sets every city model to
  `CTF_USE_COMPLEX_AS_SIMPLE` — correct for buildings, and the reason the whole kit collides with the shape
  you can see. But three of those models are the knockable props from PR #48, and chaos physics had
  deliberately given them the opposite: a simple box and `CTF_USE_DEFAULT`, because **Unreal will not
  simulate a body whose collision is complex-as-simple**, and it only ever says so in the log. Running the
  placer put `SM_CafeChair`, `SM_TrafficCone` and `SM_TrashBags` back to complex-as-simple in memory. Nothing
  looked wrong; the next save of those three would have made every chair, cone and bin in beats 1 to 3 stop
  moving when punched. They are restored, and the placer now keeps a `SIMULATED` list so the two scripts stop
  overwriting each other.

  **Two old traps fired exactly as written down.** Hiding an actor does not dirty its package, so the
  placer's own save wrote nothing for 12 of the 18 boxes until each one's full transform was re-set; and a
  committed actor package is read-only under LFS, so those saves would have reported success and written
  nothing if the files had not been locked first. The script already knew about the first trap — it calls
  `save_packages` itself — which is what made it look like it had worked.

- **What we checked.** All 21 new actors present, right mesh, **0.0 cm** from the layout, no duplicate
  labels. Both gates still stop a chest-height trace. The player still reaches the dead driver with **134 cm**
  to spare inside a 220 cm interact range, and the cafe door still opens onto the street. A viewport capture
  of the cafe shows the car through the wall.

- **What we did not check.** Nobody has played it. The level was **not** reloaded from disk, because four
  Blueprints and three actor packages left dirty by the previous lane would raise Unreal's Save Content modal,
  which freezes the MCP; `git status` showing the 12 changed packages is the evidence that the hide survives
  instead.

- **What we learned.** Two scripts can both be right about the same asset and still undo each other. When a
  tool sets a property across a whole kit, it needs an exceptions list the moment any single member of that
  kit is used for something else — and the exceptions list belongs in the tool, not in a devlog entry.

![The crashed car in the cafe, with the dead driver beside it](media/2026-11-13-setpieces-cafe.png)
