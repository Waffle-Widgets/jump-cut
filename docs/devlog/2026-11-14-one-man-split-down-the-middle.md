# One man, split down the middle

_Sat Nov 14, 2026 - M Station_

The title card has now been three different pictures in a day, and this is the first one that is
actually the idea the Team Owner had.

Concept two drew the barista and the director **back to back as two whole people**. It passed every
check, the lock held on all three takes, and it was still wrong - because the animation it was made for
fades in one half, then the other. Two whole people means the first fade shows a complete man standing
on the left of an empty screen, and the second drops a second man in beside him. His correction, in his
own words:

> I was thinking two halves of the main character, half barista and half director, and together they
> make one person on the screen but there is a clear split down the center. The barista half looks like
> he does normally, the director version looks powerful.

So: **one** body. One head, one face, standing dead centre, apron on his right-hand side, coat on his
left, and the picture's own vertical centre running down his nose. Cut at `w // 2`, the first fade is
**half a man** and the second completes him. The storyboard is
`docs/media/2026-11-14-title-animation-storyboard.jpg`.

## What this composition stops being hard

`UI-TITLE2` had to hold two things true at once - "back to back" *and* "seen from the front" - and the
model dropped one of them on the first take. One body has no such contradiction, and it showed: **all
three takes came back centred and frontal**, inside 3 px of the cut and inside 4% on width, with the
apron's single neck strap and the three forearm rings correct every time. The lock is doing its job;
the composition stopped fighting it.

## What it makes hard instead

A new failure, and a new check. If the figure stands even 40 px off centre, the cut runs down his cheek:
the barista half keeps a strip of coat and the join stops reading as one person. Nothing can move the cut
to compensate, because the widget stacks the halves at `0,0`. So `split_title_pair.py` grew `--one-body`,
which measures his middle against the cut and refuses the take, and checks the two halves are about equally
wide so a three-quarter turn is caught too. Both were proved by failing them on purpose - a 45 px shift,
and the old two-people pair run through the new mode.

## The divider line moved onto his face

Gemini's habit of drawing a thin line between two panels survived into this composition, which is a
problem it did not have before: here there are no panels, so the line lands **on him**, from the top edge
through the hair and down the nose. Takes 2 and 3 both have it; take 1 has none. Above his head it is
removable - `--erase-seam` grew `--erase-rows` so the erase can be bounded to the rows where there is
nothing behind the line but background - but over his face it is not, because filling those columns with
the background cuts a cream slot through him.

**Take 1 was picked and needed no retouch at all.** That is worth saying out loud after the picture it
replaces, where a manufacturer badge had to be painted off a car grille because six takes would not drop it.

## The rings swapped arms, on purpose

Only his left arm is inside the director half, so `{CafeWalker:director_half}` puts the three cyan rings
there. The lock now says in as many words that the **count** is the invariant - three, one per power - and
which forearm is staging. This is not a lock edited to match a stray picture; it is the same garment seen
from a composition that only shows one sleeve.

## Still not in the game

Nothing here has been imported. `T_UI_TitlePair.png` has never been in Unreal, the halves have never been
in a widget, and the animation in #64 is unbuilt. The background cream the widget must sit on is
`#FBF0DA`, measured off the picked take, and it is **not** the `#FBEFD8` written into #64 against the
previous picture.
