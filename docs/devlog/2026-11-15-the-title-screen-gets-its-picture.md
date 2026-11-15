# 2026-11-15 — The title screen gets its picture (Justin's Mac mini)

- **What we asked for:** the title art that was drawn for #64 and never imported, shown on the title screen.
  First as a still, so there is always a shippable title, then the full animation on top (next entry).
- **Prompt(s) we gave the agent:** relayed from Justin's list, item C, then *"Full animation please"*.
- **What happened:**
  - Imported `T_UI_TitlePair`, `T_UI_TitleBarista` and `T_UI_TitleDirector` from `Art/UI` with
    `py tools/unreal_import_ui_fx.py title` (a new `title` mode on the existing importer, so the PNGs never
    had to sit in `Content/`). All three 1024x572, UI group, no mips, alpha kept.
  - `WBP_Title`: the near-black background is now the picture's own cream (`#F8F0DC`, the modal colour measured
    on #64), with a real white-square brush so it actually draws. New `TitleArt` image, the pair, centred at
    1934x1080 so it fills a 16:9 screen. "JUMP CUT" moved into the empty cream on his left with a dark
    outline; the R / (A) prompt moved to the empty right, cream on ink.
  - Checked in PIE with a `Screenshot showui` from the running game (`tools/c2_pie.py title`).
- **Not yet checked by a person:** this is the layout as the editor shows it. The editor's play window on this
  Mac is very wide, so the picture is cropped top and bottom there. In a 16:9 game window it fills the screen.
  Justin needs to look at it full screen.
- **What we learned:** an Image brush set by property keeps `imageType = NoImage` and can draw nothing. Set
  `FullColor` along with the texture.
- **Media:** ![the still title in PIE](../media/2026-11-15-title-still-pair.jpg)
