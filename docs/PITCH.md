# Pitch: Jump Cut

**Theme:** Directors Cut (the organisers said it is vague on purpose and can be read abstractly).

**One-sentence pitch:** A coffee shop worker inherits a dying stranger's power to rewind time, hunts down four more
"editing" powers from the bosses who guard them, and learns too late that someone has been directing every scene.

**Core mechanic (the one thing that has to feel great):** Rewind. Take a hit, press the button, and slide back along
your last 10 seconds to where you were before it landed. Every later power is another film-editing trick you can
use in a fight.

**How you win / how you lose:** Beat each boss with the power you took from the one before, then survive the
Director's scenes. You lose when your health runs out and Rewind is on cooldown.

**How it uses the theme:** Every power is an editing cut (rewind, freeze frame, splice, stunt double), the villain is
the Director, and the ending is his cut of the story: the player was following his script all along.

## Story (the team's outline, Nov 11)
- The main character is an ordinary person working at a coffee shop when a car crashes through the wall.
- The driver is dying and passes on a mysterious power: **Rewind**.
- That power leads to four more. Together they complete one entity's power.
- Twist: that entity is the villain (working name: **the Director**). He controlled the power all along and tricked
  the main character into restoring him. More twists can be added if there's time.
- Idea still open: several opposing factions, each guarding one power, so you never know who is after you.

## The powers (the team's list; "we might iterate through some of them")
Each boss is beaten with the power taken from the boss before. Boss 1 is already dead when you find them.

| # | Power | What the player does with it | How its boss uses it | Counter |
|---|---|---|---|---|
| 1 | Rewind | Hits taken in the last 10 seconds miss on replay | No fight: the driver's body flickers back to life in the opening | - |
| 2 | Freeze Frame | Everything pauses for 10 s | Freezes the arena and gets free hits | Rewind |
| 3 | Splice | Teleport; used for platforming in the second half of the map | Blinks around and attacks through portals | Freeze Frame |
| 4 | Stunt Double | A copy fights beside you and takes one hit | Makes a double of you plus decoys | Splice |
| 5 | Final Cut | "Your will becomes reality"; the full version only at the ending | Calls 10-second "scenes" with one rule each ("No abilities", "The floor is gone", "You can't move left") | Stunt Double |

**Name to change:** "Final Cut" is an Apple trademark, and the jam allows no trademarks. Suggested: **Director's Cut**,
which is also the theme.

## How we keep it buildable (Claude's proposal, Nov 12: the team still has to say yes)
- **Small Rewind:** record the player's position and health for 10 seconds. Rewind slides the player back along that
  trail in about a second and restores the health. No replay of the whole world.
- **One boss Blueprint** with a "which power" setting, not five different bosses.
- **Freeze Frame** shortened to about 3 seconds so fights stay quick.
- **Splice platforming** is one or two gaps, not half a map.
- **Stunt Double** as a still decoy that takes one hit. It's the first thing to cut.
- **Factions** as one grunt enemy recoloured per area, or cut until the bosses work.

## Build order
| Day | Goal |
|---|---|
| Thu Nov 12 | Player + Rewind + the Freeze Frame boss, in grey boxes, playable start to finish |
| Fri Nov 13 | Splice boss, the Director with two rule scenes, win/lose and restart screens, first packaged build. **Feature freeze** |
| Sat Nov 14 | Art, sound, juice, playtests, footage. Stunt Double only if Friday went well |
| Sun Nov 15 | Bug fixes and submission only |

## Cut list (in the order we drop things)
1. Factions with different behaviour, and factions fighting each other
2. Stunt Double (power and boss)
3. Splice platforming section (keep the teleport for the fight)
4. Dialogue: one line of text per power instead
5. A full rewind of the world (already cut: only the player rewinds)
6. More than one level

## Still to decide
- **Art style.** GameStation is testing an anime look (cel-shaded characters over painted backgrounds) and a cafe
  level in the practice project. If the team keeps it, it moves here as jam work.
- The Director's real name and the final names of the powers.
- Camera: third person behind the player (the template's) unless we choose otherwise.
