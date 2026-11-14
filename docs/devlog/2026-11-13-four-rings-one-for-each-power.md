# Four rings, one for each power

_Fri Nov 13, 2026, 10:30 PM Pacific - M Station_

The split-down-the-middle title card was right. The arithmetic on it was not. The Team Owner,
looking at the committed picture:

> take 1 is fine but we should have 4 rings since it takes all 4 powers to unlock the director look.

He is right and the mistake was ours. The director of reality is what **all four** powers buy -
Freeze Frame, Rewind, Splice and Director's Cut - and the rings are the only thing in the picture
that says so, because `docs/RULES.md` 15d forbids writing it in words. Three rings was a quiet lie
about the game's own structure, sitting in the first thing a judge would see.

**A ring is on his arm, so this could not be an edit.** The picture had to be drawn again. The lock
changed first - `FOUR cyan forearm rings, one for each of the four powers` - and every director form
with it, because the lock is where prompts get their words and a prompt is not allowed to describe
him by hand.

## The count is the thing a model gets wrong silently

Two of the three new takes came back with **three** rings. Both look completely correct otherwise:
same man, right apron, right coat, centred on the cut, no scenery, no lettering. Nothing about them
says "this one is wrong". That is exactly the failure this project keeps meeting - the goon who wore
his own mesh and all nineteen montages and still did not animate, the eight-actor-stale layout, the
platforms 74 cm low. **A thing that looks finished and is wrong is worse than a thing that looks
broken.**

So the count is now measured, not eyeballed. `tools/count_power_rings.py` takes a box around his arm
and counts the cyan bands inside it:

    python tools/count_power_rings.py Art/UI/T_UI_TitlePair.png --region 600,330,720,470 --expect 4

It needs a box rather than working on the whole picture, and the reason is worth keeping: the coat's
open edges, the standing collar and the rim light are the **same cyan** at about the same spacing, so
no colour test on earth can tell a ring from a collar. A box around his arm can. The check earned its
place within a minute of existing - it reported **3** on the picture that was already committed, and
**3** on two of the three new takes.

## All three takes drew a line down his face, so this time it was repaired

Gemini draws a thin divider line between two panels. In this composition there are no panels, so the
line lands **on him** - top edge, through the hair, down the nose, to the chest. The earlier round
rejected two takes for it. This round all three had it, and the only take with four rings was one of
them.

`--erase-seam` cannot help: it fills the columns with the background, which cuts a cream slot straight
through his face. The new `--repair-seam N` stretches each half's **own** nearest clean column inward
instead:

    py -3 tools/split_title_pair.py Art/Refs/gen/gemini5/GEM5-UI-TITLE4-1.png \
        --one-body --repair-seam 6 --repair-dump Art/UI/T_UI_TitlePair.png --out Art/UI

Measured before picking the width: the line sits on x=511-512, with its halo on 509-510 and 513-514,
over a face whose flat skin reads about 195. Six columns covers both, taking x=508 for the left and
x=515 for the right. Nothing crosses the cut - left columns come from the left half, right columns from
the right half - so the two costumes cannot bleed into each other, which matters because the halves are
split on that same line a moment later. It removes a drawn line and invents nothing, and it is declared
in `PREJAM.md` as the retouch it is.

## One prompt change that did not work

Take 3 was drawn with the divider forbidden **positively** - "his nose drawn once as one whole shape",
"the only vertical line anywhere in the picture is the edge of his own clothing" - instead of "no drawn
dividing line". That is this project's own say-what-is-there lever, the one that got the badge off the
car grille and finally got the apron straps right. It did not work here: take 3 drew the line anyway.
The rewording is kept because it is the better way to say it, but the honest record is that **the fix
for this failure is the repair tool, not the prompt.**

## Dates

The three devlog entries from earlier this evening are named `2026-11-14-*` and say "Sat Nov 14". That
is the UTC date; in Pacific, where this team works, all of it is **Friday Nov 13**. The date labels in
`character-locks.json`, `prompts.md` and `PREJAM.md` have been corrected to Pacific. The filenames are
left alone so nothing that links to them breaks.

## Where this leaves the title

`T_UI_TitlePair.png` and both halves are redrawn, four rings, no line. The storyboard is
`docs/media/2026-11-13-title-four-rings-storyboard.jpg`, drawn by a script this time
(`tools/make_title_storyboard.py`) so it cannot go stale behind the art again.

**None of it is in the game.** No `.uasset` exists for these three textures, so there is nothing to
re-import and nothing of Justin's is disturbed - but the widget that plays the animation, issue #64, is
still unbuilt. The background colour it stacks the halves on has moved again: **`#F8F0DC`**, half the
picture's pixels, measured rather than sampled from a corner.
