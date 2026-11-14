# The title stops being a picture and becomes four seconds

**Fri Nov 14, M Station.** The title card has now been rejected twice, and both times for the right reason. The
crash-scene version was a scene from the game that happened to be the first thing you saw. The back-to-back
version was better but still a poster. What the Team Owner asked for this time is not a picture at all:

> half of the barista fade into frame then the other half fades in as the director, then have a clapperboard fade
> in over them, snap, then transition through them to the background.

That is a title *screen*, and it is the first four seconds of the game.

![The four beats: the barista, the director, the board, the snap](../media/2026-11-14-title-animation-storyboard.jpg)

## The expensive version, done the cheap way

There were two ways to build it and they are not close in cost. The cheap one reuses an existing picture and cuts
it down the middle. The expensive one draws each half on its own so the seam is real - and brings back every
consistency risk the character lock exists to stop, once per half, plus a new one: two independently drawn halves
do not line up. Different shoulder height, different head height, different light. No prompt fixes that, because
each half is drawn without knowing the other exists.

The Team Owner asked for the expensive version and then removed its worst problem in the same sentence: *"see if
you can do the characters in one shot [as] they would look after fading in so you can just do an easy split."*
Draw the finished frame - both of them, together, in one picture - and cut it afterwards. The seam is exact
because both halves came off the same drawing. It is the expensive version's result for the cheap version's risk.

So the new prompt, `UI-TITLE3`, is written around the cut. Every clause about the centre is load-bearing: the two
figures' backs meet along one straight vertical line at the exact horizontal centre, both heads at the same
height, and nothing of either figure crosses. `tools/split_title_pair.py` does the cut and checks all of it.

## What came back

Three takes in Gemini. The lock held on the first one, in both costumes, and held on all three: single neck loop,
bare shirt back, square bib pocket, same face, same hair. The local ComfyUI/Qwen path needed seven takes to manage
that apron twice. Take 2 is the pick. Take 3 is kept as the counter-example - it drew the director's coat across
the centre, which looks perfectly good and is unusable, because cutting it in half takes a slice out of a man.

![The two halves, keyed, over a dark field](../media/2026-11-14-title-halves-keyed.jpg)

## Two things that were not obvious until the pictures existed

**The background has to go, and that is not a polish step.** A half faded in *with* its flat cream background is a
cream rectangle growing out of nothing, with a hard vertical edge down the centre of the screen for the whole
first second. So the splitter floods the flat field away from the borders and writes real alpha. Each half is the
full 1024x572 canvas with only its own side present, so the widget stacks them at 0,0 and fades them with no
positioning arithmetic at all.

**And the flood fill ate his arms.** Pale skin is within tolerance of a pale cream background; the figures are
cropped by the bottom edge; so seeding the fill from the bottom row let it walk up the inside of both bare
forearms and punch holes clean through them. The fix is to seed the top and the two sides and never the bottom -
the bottom edge is where the figures leave the frame, so it is figure by definition, never background. It is
written into the tool beside the code, because the next picture cropped at the chest will hit it again.

## The clapperboard is drawn, not generated

`tools/make_clapperboard.py` draws it in code, with transparency, open and shut on a shared hinge. Three reasons,
and the first is the one that matters: **the slate must be blank**, and a blank white panel is the single thing an
image model cannot be talked out of filling in. This is the same failure as the car grille that kept growing a
manufacturer badge through six takes - and it does not occur at all if nobody asks a model to draw it. The other
two: it sits on top of the characters so it needs real alpha, and the snap needs two frames that register exactly,
which two generated drawings would not.

## The director of reality

The costume is new, and the Team Owner's brief for it was a point to make rather than a garment: *"just get the
point across that he becomes a director of reality when all powers have been collected."* The charcoal bomber
jacket became a long open charcoal black coat with a tall standing collar, one line of pale cyan power-light down
each open edge, and **three thin cyan rings on his forearm - one for each power**. The rings are how the picture
says "all of them" without a word of text, which `docs/RULES.md` 15d would ban anyway.

Changing a lock is normally forbidden: the lock is what the rigged model was built from, so editing it says the
model is wrong. That rule is intact here, because **there is no rigged model of the director costume yet**. The
moment one is made, this entry becomes its truth and the rule applies to it too. That reasoning is written into
`docs/character-locks.json` rather than left to be re-derived.

One thing fell out of building it: the clapperboard came out of the costume. A prop is not a garment, and the
animation fades a board in over both figures as its own element - a board already in his hand would have given the
shot two of them. It lives in `{CafeWalker:director_board}` for pictures that want him holding one.

## M Station is a builder now

Asked for in the same message, with a condition attached: *"we need to make sure it doesn't try to build or modify
any blueprints that are being worked on by another chat or computer."* That condition is the hard part, because
the usual guard does not work here - GameStation and M Station share one GitHub account, so an LFS lock held by
`mendezm87` could be either machine. `docs/TEAM.md` now carries a four-step claim rule to check before this
machine opens any `.uasset`: locks, recent commits from any machine, the ticket assignee for that area, and the
shared chat board. Stop at the first one that says somebody else is in there.

**Nothing of this is in the game.** The pictures are files. The widget that plays them is the next job, and it is
the first piece of Unreal work this machine is allowed to do.
