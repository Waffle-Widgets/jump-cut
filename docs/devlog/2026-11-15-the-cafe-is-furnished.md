# The cafe is furnished

**Sun Nov 15, about 3:25 PM, GameStation (builder). After the noon cut-off; the Team Owner asked.**

## What we asked for

> Can we do something about the assets in the coffee shop that are still gray boxed? Why haven't we made assets
> for everything? We have way too many Meshy credits left over.

## What happened

GameStation listed what in the cafe still wore a kit mesh (nine pieces worth doing, with their sizes) and sent
the list to M Station. M Station had all nine baked and pushed 11 minutes later
(`M_STATION/cafe-furniture`, its own devlog entry says how each was fitted to the box it replaces).

On GameStation: merged the branch, `unreal_street_models.py import` (9 meshes, 9 textures, 9 material instances),
`plan`, lock, `swap` by name.

- `plan` said **25** actors, not 20. The extra five were the street's A-frame signs, which I had reverted to the
  kit sign an hour earlier: to the tool they are just "actors still wearing a kit mesh". A plain `swap` would have
  put the coffee sign back outside four other shops. Swapped by name instead; 20 actors changed.
- The chair is a prop you can knock over, so its import took a new path M Station wrote and had never run: one
  simple box, default collision. The import log reads "simple box x1, CTF_USE_DEFAULT (simulated prop)".
- The counter is the one the latte game sits on. Checked the pour view afterwards: the cup, pitcher, goal and
  match meter are where they were, now on a wooden top.

![Counter from both sides](../media/2026-11-15-cafe-furniture-in-game.png)
![Seating, and the latte view on the new counter](../media/2026-11-15-cafe-seating-and-latte-view.png)

## Checked, and not checked

- Checked by script: 9 imported, 20 actors changed, both saves `ok=True`.
- Checked by eye from the game camera: counter (both sides), shelves, pendants, chairs, a table, the bar counter and
  stools, the hanging sign, and the latte pour view.
- **Not checked:** knocking a chair over, the banquette and chalkboard up close, whether the espresso machine and
  pastry case (placed at z 104) sit 6 cm into the new flat 110 top, and the explosion with the new furniture in the
  room. No packaged build has any of this yet.

## What we learned

- **A sweep tool does not know about the exception you made by hand an hour ago.** Read `plan`'s count against the
  number you expect before running the sweep. 25 against 20 was the whole warning.
- **Sending the other computer a list with sizes and "do not make" items got nine fitted models back in 11 minutes.**
