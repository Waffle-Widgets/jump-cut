# Thirteen more Meshy props are in the level

**Sun Nov 15, about 2:40 PM, GameStation (builder). After the noon cut-off; the Team Owner said go.**

## What we asked for

M Station made a second batch of 13 props (PR 135) for the kit models that still looked blocky. GameStation
recommended waiting until the video was done. The Team Owner's answer:

> all of it

## What happened

- Pulled `main` with PR 135, reopened Unreal, ran `tools/unreal_street_models.py import`: 13 meshes, 13 textures and
  13 material instances, 39 packages saved. The new skip-if-already-imported path left the first five alone, as
  M Station intended. It had only ever passed a syntax check before this run.
- `plan` listed 57 placed actors, exactly M Station's count. Locked all 57 actor files.
- `swap` with the seven street names changed 48 actors; a second `swap` with no names changed the 9 cafe ones. The
  name filter worked first time.
- Looked at them in the running game: vending machines, street lamps, a bench and a planter on the street all face
  the road. In the cafe the pastry case shows its glass to the customers and the espresso machine shows its working
  side to the barista.
- The latte pour view is top-down on the cup, so none of the new counter props are in it. Checked with a capture.

![Street: bench, planter](../media/2026-11-15-street-props-batch2-in-game.png)
![Cafe counter from both sides](../media/2026-11-15-cafe-props-batch2-in-game.png)

## Checked, and not checked

- Checked by script: 13 imported, 57 actors changed, both saves `ok=True`.
- Checked by eye, from the game camera: four street props and the three counter props.
- **Not checked:** which way the new register faces (too small in the capture to tell, and it is where the player
  clocks out), the dumpsters, pot rows and A-frame signs, the plaza, and whether the deeper bench and planter
  (about 30 cm further into the pavement) get in the player's way. A scooter now stands partly in front of one bench.
- **Not checked:** a packaged build played by a person.

## What we learned

- **A filter on a tool that changes 57 actors is worth writing even when there is no time to test it.** Swapping the
  street seven first meant a bad cafe model could have been left out without undoing anything.
- **Ask the other computer for its expected count.** M Station said "57, but trust `plan`"; `plan` said 57. One number
  agreeing from two machines is the cheapest check there is.
