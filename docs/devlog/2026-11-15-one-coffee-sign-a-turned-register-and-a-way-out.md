# One coffee sign, a turned register, and a way out of the game

**Sun Nov 15, about 2:50 PM, GameStation (builder). Found by the Team Owner playing the 2:38 PM build.**

## What we asked for

> these coffee signs shouldn't be here, we should have one that replaces the graybox in front of the shop. Also
> there is no menu to open to exit the game. The register in the coffee shop is also flipped around.

## What happened

**The signs.** The second prop batch put M Station's coffee A-frame on all five of the street's generic A-frame
signs, so the cafe's own sign stood outside four other shops. The "graybox" in front of the cafe was not a grey
box: it is the kit's `SM_CafeMenuBoard`, which draws as a brown smear through the cel look. `tools/jc_shop_fix.py`
puts the coffee sign on that one actor, and `unreal_street_models.py revert AFrameSignM` put the kit sign back on
the five.

Order mattered and I got it wrong first: `revert` matches by mesh, so run after the fix it took the shop's new
sign off again (6 actors changed, not 5). Ran the fix a second time. The register turn in that script was
"add 180", which a second run would have undone, so it is now "set to 180".

**The register.** I reported its facing as "not checked" in the last entry, and it was wrong. The Meshy register's
front is the opposite way round from the kit's. Yaw 0 to 180; the keys now face the barista (captured).

**The menu.** There was no way to leave the packaged game except Alt+F4. New `WBP_QuitMenu` (a copy of the lose
screen with new words) and two functions on `BP_JumpCutGameMode`: `JumpCutQuitStep` runs first in every tick,
Esc, P or the gamepad Menu button opens and closes it, and Q quits while it is open. Keys are polled the way
restart is, so there is nothing to wire by hand.

`add_variable` cannot make an object variable ("Supported: bool, int, float..."). The widget reference was added
from Python instead: `BlueprintEditorLibrary.add_member_variable(bp, name, get_object_reference_type(UserWidget))`.

![Sign outside the shop, and the register from the barista's side](../media/2026-11-15-shop-sign-and-register.png)

## Checked, and not checked

- Checked by script in the running game: the menu widget is created and in the viewport; the graphs read back as
  written; the sign actor wears `SM_AFrameSignM` with its own material; register yaw 180.
- Checked by eye: the register's keys face the barista.
- **Not checked: pressing Esc, P or Q.** A script cannot hold a key across a tick here. A person has to open the
  menu and quit with it, in the packaged build (in the editor, Esc ends Play mode, so use P there).
- **The menu does not pause the game.** Pausing stops the tick that reads the keys, and there was no time to do it
  properly. Enemies keep moving while it is open.
- Pressing Q with the menu open also reaches whatever Q does in play, on the frame before the game closes.

## What we learned

- **A tool that matches "everything wearing mesh X" will also match the one you just made an exception of.** Run
  the sweep first and the exception second, and make the exception safe to run twice.
- **"Not checked" in a report is a to-do, not a caveat.** The register was the first thing the owner found.
