# The last boss gets a body before a face

*Thu Nov 12, 2026, 11:54 PM Pacific — GameStation*

The six-beat demo got approved tonight, and that quietly promoted the stunt double from "number 2 on the cut
list" to the fight the demo ends on. He had a written design, a Gemini prompt and a ComfyUI prompt. He did not
have a single thing you could walk up to and punch.

So he has one now, and it is deliberately not him. `BP_StuntDouble` is a child of `BP_EnemyBase` wearing Epic's
mannequin, scaled 1.15 so nobody mistakes the final boss for a goon. He punches with `AM_Human_Punch_02`,
flinches with `AM_Human_HitReact`, dies with `AM_Human_Death` — the same three montages the goons use. 300
health, 0.40 s windup, 1.0 s cooldown: quicker and lighter than the mob boss, who has less health but a 0.70 s
wind-up. A stuntman should feel like he has done this before.

This is what Justin's list actually asked for. "Enemy types completely set up, **ready for model swapping after
the playtest**" means the fight is the deliverable and the body is a slot. Saturday is model-swap day. If the
orange coverall never gets drawn, beat 5 still works, and that is the whole point of building it this way round.

## What this pass checked rather than assumed

Combat was committed last night and verified by reading back which animation was playing, which is a check that
passes even when nothing is visible on screen. The thing that makes it invisible is a missing Slot node, and the
project has been bitten by the animation-mode version of that before. So it got looked at properly:

- `BP_Player` and `BP_Goon` are both in `AnimationBlueprint` mode on `ABP_Unarmed` — not `AnimationSingleNode`,
  which would have swallowed every montage silently.
- `ABP_Unarmed`'s graph runs `Main States` → Slot **`DefaultSlot`** → ControlRig → Output Pose. The slot is there
  and it is wired.
- `ABP_CleaverBoss` is the same story: blend space → `DefaultSlot` → Output Pose.
- Every montage is authored on `DefaultSlot`, and every anim variable on every enemy CDO is actually assigned.

So the boxing works. Controls, too: left mouse or the gamepad's left face button to punch, Q and E for the
powers, polled on tick with edge detection and a 0.25 s interval.

Two things turned up that were not on anyone's list. `BP_BossFreeze` is **not** boss 1 — it is the cleaver boss
who hands over Splice, carrying a name from back when it handed over Freeze Frame. Worth knowing before someone
goes looking for the mob boss and finds nothing. And the player has punch, hit-react and a downed state but no
death montage, where both enemy types have one.

## The part that is stuck

Three documents describe three different final fights. The roadmap says he copies himself. The pitch says he
makes a double of *you*, plus decoys. The design proposal says two or three doubles wearing your face, with
damage transferred to the nearest one so he cannot be hurt until they are gone.

One of those is an extra enemy spawn. Another is a damage-redirection system plus a runtime copy of the player's
mesh. On the Friday of a feature freeze that is not a detail, so the shell is where this stops until somebody
picks one.
