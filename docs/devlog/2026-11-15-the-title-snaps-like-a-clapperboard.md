# 2026-11-15 — The title snaps like a clapperboard (issue #64) (Justin's Mac mini)

- **What we asked for:** "Full animation please": the 4-second title animation designed on #64, built on top of
  the still title from the previous entry.
- **Prompt(s) we gave the agent:** Justin, relayed: *"Full animation please"*.
- **What happened:** built inside `WBP_Title` only (the game mode is locked by another machine and did not need
  to change).
  - Four new images stacked on the existing canvas: `TitleBarista` and `TitleDirector` (full canvas at 0,0, as
    #64 says), `TitleClapOpen` and `TitleClapShut` (same slot and size, so the hinge never moves; 80% of screen
    height, centred). All start transparent, so nothing flashes on the first frame.
  - One small function, `TitleAnimStep(Dt)`, called from the widget's own Tick. It adds real time (UMG's tick is
    not slowed by time dilation) to `TitleT`, capped at 0.05 s a frame so PIE's first long frame cannot skip the
    start. Every layer's opacity is a clamped ramp of `TitleT`:

    | t | What |
    |---|---|
    | 0.0-0.8 | barista half fades in |
    | 0.8-1.6 | director half fades in, completing him |
    | 1.6-2.4 | open clapperboard fades in over them |
    | 2.4 | snap: open -> shut on one frame, `SFX_Clapper` plays, "JUMP CUT" pops in (scale 1.3 -> 1.0) |
    | 2.4-3.2 | figures wipe out; the shut clapper fades 2.7-3.2 |
    | 3.2-3.6 | R / (A) prompt fades in |

  - **Measured per frame in PIE** (`tools/c2_pie.py title`): each layer followed the table; the swap and the
    sound were on the same frame (`TitleT` 2.415); end state held.
  - **R during the animation** (`tools/c2_pie.py titleskip`, calling the game mode's own `JumpCutStartPlay` 1 s
    in): the title collapsed at once, its clock stopped at 1.006, so the snap sound cannot fire later in play.
    A whole-level restart made a new title widget that started again from 0.02 s. Time dilation stayed 1.0.
- **Left out:** `SFX_TitleSting` still plays when the title first appears, not on the reveal. Moving it needs
  `BP_JumpCutGameMode`, which is LFS-locked by another machine. The #64 suggestion to delete the old
  `T_UI_Title` is not done (it needs the Team Owner's yes).
- **Not yet checked by a person:** how it looks and feels in motion, and whether the snap sounds right. Justin
  needs to watch the title from a fresh Play, full screen. The editor's play window on this Mac is very wide,
  so the pictures below are cropped top and bottom.
- **What we learned:** a collapsed UMG widget does not tick, which is exactly what makes "R skips it" safe here.
- **Media:**
  ![1.3 s, both halves](../media/2026-11-15-title-anim-1.jpg)
  ![2.1 s, clapper open](../media/2026-11-15-title-anim-2.jpg)
  ![2.5 s, the snap](../media/2026-11-15-title-anim-3.jpg)
  ![4.0 s, end state](../media/2026-11-15-title-anim-4.jpg)
