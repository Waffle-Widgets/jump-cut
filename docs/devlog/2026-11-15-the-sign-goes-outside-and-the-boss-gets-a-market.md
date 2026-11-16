# The sign goes outside, and the boss gets a market square

**Sun Nov 15, about 4:10 PM, GameStation (builder). After the noon cut-off; the Team Owner asked while playing.**

## What we asked for

> this cafe sign looks out of place. It would probably look better outside attached to the wall instead of flat
> against it. Is there something we can do about the area with the cleaver boss? It looks very gray box.

> that type of cafe sign is usually perpendicular to the wall on the outside of a building

## What happened

**The sign.** M Station's hanging sign was fitted to the kit sign's origin, which is on the INSIDE face of the
cafe's front wall with the kit board running along it. A bracket sign belongs outside, sticking out. Moved
`City_CafeSign` to the street face of the wall (x 645 to 769), turned so it projects straight out, and stood it
just past the end of the awning so the two do not cross. One actor.

**The boss plaza** is 30 x 30 m of paving inside four plain walls, with about a dozen props. Issue #50 has said
since Friday: "dress the edges without changing the arena". Nothing new was modelled. `tools/jc_boss_dress.py dress`
stands 39 more things round the edge, every one a model already in the game: display stalls, benches, vending
machines, planters, pot rows, a bicycle, a scooter, two chalkboards, gas bottles, a hedge, four wall air-conditioners
and eight of the kit's lantern strings along the walls.

- Everything is within 1.3 m of a wall. The script prints the nearest one to the middle of the arena: 13.6 m.
- The two gates (the middle 6 m of the east and west walls) and the six lamps are left clear.
- The lantern strings have collision off; everything else is solid, like the props that were already there.
- Running `dress` again removes the old set first. `undress` removes them.

![The sign outside the cafe, and the plaza](../media/2026-11-15-cafe-sign-outside-and-boss-plaza.png)

## Checked, and not checked

- Checked by eye from the game camera: the sign over the pavement beside the awning; the plaza's north wall with
  stalls, benches and vending machines behind the boss.
- **Not checked:** the boss fight itself with the props in (his blink flanks to the SIDE of the player, and a prop
  at the wall could be where he lands), the east, west and south walls up close, and a packaged build.
- The plaza floor is still the kit's grey checker paving. That is a material, not a prop, and there was no time.

## What we learned

- **"Fitted to the kit piece's box" keeps a wrong placement wrong.** The kit sign was in an odd place; the new one
  inherited it exactly.
- **Dressing a space is placing, not modelling.** Thirty-nine actors from models already paid for took one script.
