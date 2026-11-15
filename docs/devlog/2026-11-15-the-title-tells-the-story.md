# 2026-11-15 — The title tells the story in two lines (Justin's Mac mini)

- **What we asked for:** a short story synopsis on the title screen.
- **Prompt(s) we gave the agent:** Justin: *"I think we need a small text synopsis at the title screen. The story of
  the sorcerer who's power was sealed. And now there's two factions fighting over that power."* The project
  assistant turned it into three lines and a timing slot in the existing 4-second title animation. The third line
  ("One piece just crashed through your cafe wall.") was built and pushed first (`4891763`); Justin then picked the
  two-line version: *"Don't wanna spoil the surprise car crash"*. Only the text changed.
- **What happened:** changed `WBP_Title` only (`Content/Game/UI/`).
  - One new `TextBlock`, `TitleSynopsis`, on the existing canvas, centered at 55.6% of screen height: between the
    "JUMP CUT" title (42%) and the R / (A) prompt (66%). Roboto Regular 22, dark warm grey on the cream, so it
    reads as quieter than both. The two lines are split by an explicit line break, auto-wrap off (the `AutoWrapText` trap
    in CLAUDE.md). It starts at opacity 0.

        A sorcerer's power was cut apart and sealed.
        Now two factions fight over the pieces.

  - It fades in from `TitleT` 2.6 to 3.2: after the 2.4 s clapper snap and title pop, and just before the prompt
    (3.2-3.6), which is unchanged.
  - **Spliced, not rewritten.** The fade lives in a new one-line function, `TitleSynopsisStep`, and one call node to
    it was spliced into `TitleAnimStep` between the function entry and the `TitleT` setter. `TitleAnimStep` went
    from 50 nodes to 51, and its read-back is identical except for the new call.
  - **Measured per frame in PIE** (`tools/c2_pie.py title`, now also sampling `TitleSynopsis`; 218 frames on
    the two-line version, 217 on the three-line one with the same timings to a frame): synopsis opacity 0.0 on
    every frame before `TitleT` 2.6, first non-zero at 2.628, 1.0 by 3.242 (the same
    one-frame lag every layer in this function has). Prompt unchanged: first non-zero at 3.221, 1.0 at 3.618. Title
    pops at 2.414 as before. End state holds at 1.0.
  - **R still skips it** (`tools/c2_pie.py titleskip`): calling the game mode's own `JumpCutStartPlay` 1 s in
    collapsed the title widget, its clock stopped at 1.006, and a whole-level restart made a new title widget that
    started again from 0.021. (Run once, on the three-line build; the text change cannot affect it.)
  - Small tool change: `c2_pie.py title` now waits up to 45 s for PIE, so it can be armed **before** `StartPIE` and
    see the title from its first frame (an MCP round trip on this Mac is longer than the animation).
- **Left out:** nothing that was asked. The look is a first pass: size, color and position were chosen by the
  agent from the existing layout, not by a person.
- **Not yet checked by a person:** how it looks and reads in motion and full screen (the editor viewport on this
  Mac is very wide, so the picture is cropped top and bottom); whether 22 pt is readable on a TV or laptop; and the
  gap above and below it (roughly 30 px each at this viewport size). It is **not in any packaged Windows build** until
  one is repackaged.
- **What we learned:** arming a per-frame recorder before starting Play is the reliable way to measure something
  shorter than one MCP round trip.
- **Media:**
  ![End state at 4.0 s: title, synopsis, prompt](../media/2026-11-15-title-synopsis.jpg)
