# Pitch: Jump Cut

**Theme:** Directors Cut (the organisers said it is vague on purpose and can be read abstractly).

**One-sentence pitch:** A coffee shop worker inherits a dying stranger's power to stop time, hunts down three more
"editing" powers from the bosses who guard them, and learns too late that someone has been directing every scene.

**Core mechanic (the one thing that has to feel great):** an editing trick you press in a fight, and every later power
is another one. **Freeze Frame is the first power and the core** (Nov 12): the dying driver hands it over in the
cafe. Rewind moves to a later boss; which one is still open, see "Still to decide" in [`ROADMAP.md`](ROADMAP.md).

**How you win / how you lose:** Beat each boss with the power you took from the one before, then survive the
Director's scenes. You lose when your health runs out.

**How it uses the theme:** Every power is an editing cut (freeze frame, splice, stunt double, the director's cut), the villain is
the Director, and the ending is his cut of the story: the player was following his script all along.

## Story (the team's outline, Nov 11)
- The main character is an ordinary person working at a coffee shop when a car crashes through the wall.
- The driver is dying and passes on a mysterious power: **Freeze Frame** (Nov 12; it used to be Rewind).
- That power leads to three more. Together they complete one entity's power.
- Twist: that entity is the villain (working name: **the Director**). He controlled the power all along and tricked
  the main character into restoring him. More twists can be added if there's time.
- Idea still open: several opposing factions, each guarding one power, so you never know who is after you.

## The powers (the team's list; "we might iterate through some of them")
Each boss is beaten with the power taken from the boss before. Boss 1 is already dead when you find them.

| # | Power | What the player does with it | How its boss uses it | Counter |
|---|---|---|---|---|
| 1 | Freeze Frame | Everything pauses for 10 s | No fight: the dying driver who crashes through the cafe wall | - |
| 2 | Splice | Teleport; platforming in the second half of the map, and getting past the stunt double that fights for boss 3 | Blinks around and attacks through portals. A Japanese mob boss with a cleaver | Freeze Frame |
| 3 | Stunt Double | A copy fights beside you and takes one hit | Spawns stunt doubles **of himself** that dive in front of his hits, and can tag one in to fight for him - the tagged-in one leaves on a timer once nothing is in its range | Freeze Frame (Splice to get past the tagged-in one) |
| 4 | Director's Cut | "Your will becomes reality"; the full version only at the ending | Calls 10-second "scenes" with one rule each ("No abilities", "The floor is gone", "You can't move left") | Stunt Double |

**Rewind** moves to a later boss (Nov 12, see Decisions in [`ROADMAP.md`](ROADMAP.md)) and has no row yet: which
boss gives it, and where it sits in the ladder, is still open there.

**Boss 3 breaks the "countered by the power before it" rule, deliberately** (Manny, the Team Owner, Fri Nov 13,
12:30 AM Pacific). The Stunt Double boss is countered by **Freeze Frame**, which is power 1, not by Splice. His
doubles jump in front of your punches, so the only way to land one on *him* is to stop time first. Bosses 2 and 4
still follow the old rule. The cost is that beat 5 no longer needs Splice to be finished - which, with Splice
still unbuilt, is a reason it is this way round.

**Splice is back in that fight, but not as the counter** (Manny, the Team Owner, Fri Nov 13, 1:15 AM Pacific).
Splice gets the boss's **bodyguard**, not his soak: the player blinks past the stunt double the boss tags in to
fight, and reaches the boss directly. Freeze Frame is still what makes a hit on the boss land, because a teleport
does nothing about a double diving in front of a punch. So the ladder's rung is half restored - the power from
the boss before is useful in the fight, it is just not the thing that wins it. **Neither half of this is built
yet**: Splice does not exist, and the tagged-in double has no despawn timer.

**The demo stops after power 2, and that is a scope call, not a design change** (Justin, Fri Nov 13, 4:30 PM
Pacific). This file describes the **whole game**; the jam entry is a demo of its first half. As of the
four-beat rescope in [`ROADMAP.md`](ROADMAP.md) the demo ends with a "to be continued" after the **Splice
boss**, so powers 3 and 4 - Stunt Double and Director's Cut - and the Director himself are full-game design
that the jam build does not reach. Power 3's *fight* is built and plays (the diving stand-ins, the Freeze
Frame counter); it is a nice-to-have on the cut list, not a beat. **The two paragraphs above still describe
the game's ladder correctly** - they are what the Stunt Double fight does when it is in - but neither is on
the demo's critical path any more, and the Splice-past-the-bodyguard half of the second one is now the
clearest reason the demo might want the platforming section back: Splice is handed over in the demo's last
fight and the demo currently gives the player nowhere to press it.

**Who the characters are** — the worker, the crash driver and the mob boss: [`CHARACTERS.md`](CHARACTERS.md).

**Renamed, Nov 12:** power 4 was called "Final Cut" until the Team Owner called the rename. "Final Cut" is an
Apple trademark and the jam allows none (§15d), so the power is **Director's Cut** everywhere now - which is also
the theme. The old name is kept only in `docs/devlog/`, as the record of the decision.

## The plan
The build order, the cut list, proposals waiting for the team's yes, what is still to decide and what has been
decided are in [`ROADMAP.md`](ROADMAP.md) (moved there word for word on Nov 12). This file is the game itself.
