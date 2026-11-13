# 2026-11-13 — The Stunt Double learns to take the hit (GameStation)

- **What we asked for:** three documents described three different beat-5 fights, so the boss had a body but no
  power. The Team Owner settled it at 12:30 AM Pacific, and this lane built exactly what he described.

- **Prompt we were given**, in his words:

  > For the beat 5 fight the boss should be able to create stunt doubles of himself to soak damage, as stunt
  > doubles do, so they would probably jump in front of the way of an attack. The boss should also have an option
  > where he can spawn a stunt double that fights for him but we play into the theme and use tricks they use in
  > film where stunt doubles are involved. If the boss spawns stunt doubles that absorb damage then the player
  > needs to Freeze Frame to even be able to land an attack.

  He also corrected our wording: **boss 1 is the crash driver** because he is the boss of his organisation, not
  because he is the first fight. **The first boss the player actually fights is the cleaver boss.**

- **What we built.** `BP_StuntStandIn`, a new `BP_EnemyBase` child: the double. Same mannequin and montages as the
  boss, mesh scaled 1.15 to match him, 45 health, and a `StandInFights` flag. Flag off, it stands and watches you.
  Flag on, it fights like a goon.

- **Where the redirect lives, and why there.** In `BP_EnemyBase.EnemyTakeHit`, in front of the damage, not in the
  boss. Every enemy now has an `EnemyStandIns` array — empty for goons and for the cleaver boss, so their damage
  path is unchanged. When it is not empty and the enemy is not time-stopped, `EnemyPickStandIn` finds a living
  stand-in, teleports it onto the line between the boss and the attacker, turns it to face the blow, and forwards
  the whole hit to it. The boss takes nothing.

- **Freeze Frame cost nothing to add, which is the nice part.** Freeze Frame already calls
  `BP_Player.PlayerStopAllEnemies`, which sets `EnemyTimeStopped` on every enemy. The redirect is skipped when the
  enemy is time-stopped. So with time stopped, the doubles are pinned mid-dive and the punch reaches the man it
  was aimed at — with no new flag and no coupling between the boss and the player.

- **The two tricks he does with them.** `BossCallStandIns` calls in a crew of three in a 42° fan facing the player,
  but only when the last crew is gone (14 s cooldown, first wave 2.5 s after he wakes). `BossCallFighter` tags one
  in from behind him every 16 s, at most one alive at a time — the double walks on from off-camera and takes the
  dangerous shot.

- **How we checked it, and what that is worth.** Play-In-Editor on GameStation, reading live actor state through
  the editor console. A test `BP_StuntDouble` was placed, woken, and removed again afterwards; the level was not
  saved. Results:
  - three stand-ins spawn in the fan, `StandInFights` false, 45 health each;
  - a 10-damage hit on the boss with the crew up: boss **300 → 300**, one stand-in **45 → 35**, and that stand-in
    moved onto the attack line;
  - the same hit with Freeze Frame on (`EnemyTimeStopped` true): boss **300 → 290**, every stand-in untouched;
  - the tag-in double spawned awake with `StandInFights` true, and `FighterRef` pointed at it;
  - regression: a plain `BP_Goon` still took 10 damage from the same call, so the shared base class is intact.

  **Nobody has played this.** Every number above came from calling the real functions and reading the result, which
  is not the same as a person seeing a double jump in front of a punch.

- **What it changes elsewhere.** Beat 5 is now the one rung where the ladder is broken on purpose: the Stunt Double
  boss is countered by **Freeze Frame**, power 1, not by Splice. That is the useful direction — Splice is still
  unbuilt, and this fight no longer waits on it. `PITCH.md`, `ROADMAP.md` and `CHARACTERS.md` were all updated in
  the same pass, and the "doubles wear the player's face" idea is dropped.

- **Still open:** his artwork. The prompts `GEM2-BOSS3` and `BOSS3-APOSE` are written and nothing has been
  generated, so he is still Epic's mannequin at 1.15 scale.
