# Three pictures, three different aprons

**Fri Nov 13, evening — M Station**

The Team Owner looked at the screen art we made this afternoon and found the thing we had not: our main
character's apron is different in every single picture of him.

- On the **title card** his back is bare shirt.
- On the **"to be continued"** card he has crossed X straps across his back, like a Japanese cross-back apron.
- On the **itch.io cover** the bib has no neck strap at all. It just floats on his chest.

The reference sheet his rigged 3D model was built from has none of those: one strap over the head, bare shirt
back, a square pocket on the bib, the waist ties knotted at the **front**, and a grey bar towel at his left hip.

So three pictures of one man, three aprons, and none of them the real one. His exact words were the reason this
matters: *"else the game be labeled AI slop."* He is right. A player cannot name what is wrong, but they can see
that the character is not the same person twice, and that is the tell.

## Why it happened, which is the boring and important part

Every prompt described him **from memory**. `UI-TITLE` said "a khaki brown long-sleeve shirt and a dark green
apron". `UI-TBC` said the same six words. `UI-COVER` said something slightly longer. None of them said how the
apron is fastened, because whoever wrote each prompt was thinking about the *scene*, not about him.

An image model fills in anything you do not pin down, and it fills it in differently every time. Six words of
description leave the apron's entire construction free. We did not have a consistency problem so much as we had
three separate descriptions and no single place that said which one was true.

## The fix: a character lock

`docs/character-locks.json` now holds **one** canonical description per character, taken from the reference
sheet the model was actually built from. Prompts are not allowed to describe a locked character any more. They
write a token:

    {CafeWalker}          the full lock - when he is close and most of him is in frame
    {CafeWalker:short}    the same lock, shortened - when he is small or far away

`tools/gen_images.py` substitutes the lock before it sends anything to the graphics card, so every picture gets
**byte-identical words**. It also folds each character's `never` list into the negative prompt automatically, so
nobody has to remember that his shirt must not be cream or that her apron is not his green.

Both forms keep the detail that actually drifted — *"one single strap looped behind his neck, leaving his shirt
back completely bare with no crossed straps"* — because that is the sentence the short form existed to drop and
exactly the sentence we could not afford to lose.

`tools/char_lock_check.py` fails the moment a prompt starts describing a locked character by hand again. The
A-pose prompts that **drew** the canonical sheets are exempt, listed as `sheet_prompts` in the lock, because they
are its source. Changing one of those means redrawing the sheet *and* remaking the rigged model, and the lock
says so in its own file so that nobody does it by accident.

## What the lock does not do, which we found out immediately

It makes the words identical. It does not make the model obey them.

The very next take still drew the coworker in a cross-back apron, with the no-crossed-straps sentence sitting
right there in the prompt. A 400-word prompt has a lot of instructions in it and the model drops some. So the
honest claim is narrow: **the lock removes drift caused by us, not drift caused by the model.** That is still
most of it — three different descriptions could never have agreed — but it is not all of it, and the picture
still has to be looked at.

The stronger lever is `--lock-ref`, which hands the model the character's actual reference sheet alongside the
prompt. That is the next thing to lean on when words alone are not holding.

## While we were in there: the other five things he found on the title card

He reviewed the title card properly and every point was real:

| What he said | What was wrong | Now |
|---|---|---|
| "coming out of a cave made of glass" | the hole was an undefined mass of glowing cyan shards, no wall, no street | a hole torn in red brick, with the Japanese street visible through it |
| "the car has no driver" | empty seats | the driver lies on the floor against the open door, where his body actually is in the level |
| "the car has no damage" | pristine bonnet, both headlights intact | crumpled bonnet, cracked windscreen, one smashed headlight, dented wing |
| "way too many coffee cups ... no customers" | six cups and a saucer, nobody in the room | three cups, and two customers at a table |
| "the register should be nearby" | there was no register in the picture **or in the game** | see below |

The cyan was the interesting one. It was not a colour mistake so much as a lighting mistake: the prompt asked
for "pale cyan light glowing on every frozen shard", and the model obliged on every shard at once, which turns a
room into a cave. It now asks for a thin rim light on the frozen pieces **only**, with warm daylight everywhere
else.

## The register did not exist

"The register should be nearby so that the car barely misses the coworker" sounded like a note about the
picture. It was also a note about the game, and checking it found two things.

The kit had a counter, an espresso machine and a pastry case and **no register at all** — so every picture that
drew one was inventing it. `SM_CafeRegister` now exists: 312 triangles, blank keys and a lit panel for a screen,
no brand and no readable text (rules 15d).

And the car did not come anywhere near her. The counter sat at `(200, -380)` and the coworker at `(300, -250)`,
while the car stops at `x = -334`. That is over six metres of empty floor between the wreck and the person it
was supposed to nearly hit.

The counter, register, espresso machine and pastry case have moved to the west end beside the wall the car comes
through. One detail took a second pass: the counter puts its recessed customer panels on Blender `-Y`, which the
FBX export turns into Unreal `+Y`, so at yaw 0 the **customers** would have been standing on the car's side and
the staff would have been safely against the south wall. Turned round to yaw 180, the staff side faces the
wreck. Measured from the written layout rather than estimated: a person at the register stands **70 cm** from the
car. The till had to be rebuilt too, so its drawer, keys and screen all face the same way the counter's staff
side does — otherwise the cash drawer opens at the customer.

![The cafe plan after the move, top down and to scale](../media/2026-11-13-cafe-plan-after-the-move.png)

The layout still passes its own check: 246 actors, nothing solid in the road, the cafe, the arena, the gates or
the exit run, and all three protected lanes still clear — the player's walk at `y = 0`, the shrapnel's flight,
and the driver's body at `(-380, 220)`.

## What is not done

**The Unreal half of the register move.** The coworker is a placed actor in `Lvl_JumpCut` at `(300, -250)` and
the shrapnel flies to her there. Moving the counter in the layout file does not move her, and a half-done move
is worse than none — she would be standing at a counter that is no longer there. That is on a ticket for the
builder, with the coordinates, and it changes how far the player has to run during the rescue, so the quick time
event's 3.5-second window needs a look afterwards.

**Nobody has seen the new counter in Unreal**, or in a Blender render. The 70 cm is arithmetic over the layout
file, which is the same arithmetic the placer will use, but it is not a picture.

**The car in the take carried a manufacturer badge on its grille** — a straight 15d violation that the first
pass did not catch because we were looking at the damage. The prompt now asks for a blank grille and the badge
words are in the negative list, but this is the second rules slip in two days from looking at the wrong part of
the picture.
