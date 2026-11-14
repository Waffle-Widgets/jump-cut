# 2026-11-13 — The coworker gets a body (Justin's Mac mini)

- **What we asked for:** do the tickets assigned to this machine. This is #5, the second of four.

- **Prompt(s) we gave the agent:** the actual words, quoted:

  > Another agent made github issues out of tasks to be completed. Take a look and comment and close on
  > anything we've worked on already. Then do any that were assigned to us that are still pending

- **What happened.**

  `SK_CafeCoworker` went in the way the other characters did — the FBX copied into its own folder under
  `Content/Game/Imported/` and left to Interchange — and `BP_Coworker` now wears it. The green box she has
  been since Friday morning is still in the Blueprint, with its mesh cleared: `CoworkerTakeHit` lays her
  down by rotating *that* component, so deleting it would have broken the beat.

  **Two things went wrong, and the second one nearly had me rebuild something that was fine.**

  **Her FBX did not carry her texture.** `M_CafeCoworker` came in with no `DiffuseColorMap`, so she was a
  plain grey woman — and nothing reports that. The PNG sits beside the FBX in `Art/`; it is imported and
  wired now the way `M_CrashDriver` already was. `M_CafeWalker` has exactly the same hole, which is a free
  warning for #7.

  **Then the editor showed her collapsed in a heap on the cafe floor, about 18 cm across.** Her component
  read back perfectly — world location (300, −250, 0), world scale (1, 1, 1), visible, 68 bones. A plain
  `SkeletalMeshActor` with the same asset placed two metres away stood up correctly at 168 cm, so it was
  not the model. I rebuilt the component hierarchy twice chasing a scale bug that was not there.

  What settled it was measuring **bones**, not bounds: in the editor every one of her 68 bones read
  **z = 0.0** — no pose at all, which is not a scale problem, it is an uninitialised component. In PIE the
  same actor measured **z 2.2 to 151.7**. A skeletal component added to a Blueprint *after* an actor was
  placed has no pose in the editor viewport until the level is reloaded; the game is unaffected.

- **What we checked.** Live PIE bones 2.2 → 151.7 cm, component at (300, −250, 0), scale (1, 1, 1),
  visible; an A/B plain actor at 168 cm; her asset thumbnail shows white shirt, teal apron, grey trousers,
  dark hair — the colours `color_audit.py` signed off.

- **What we did not check.** Nobody has played it. She has no down pose for a failed rescue (#45), and she
  stands in a single-node idle rather than an anim blueprint.

- **What we learned.** A bounding box, a transform read-back and a viewport are all capable of agreeing with
  each other and being wrong together. Bone positions are the thing that tells you whether a skeletal mesh
  is actually posed — and when the editor and PIE disagree about a component, PIE is the one that matters.
