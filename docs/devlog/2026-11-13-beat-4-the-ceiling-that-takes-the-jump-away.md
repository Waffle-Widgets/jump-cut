# 2026-11-13 — Beat 4: the ceiling that takes the jump away (Justin's Mac mini)

- **What we asked for:** "Continue beat 4 on this mac" — and, mid-turn, "Also, make sure we are merging as we go."

- **Prompt(s) we gave the agent:** *"Continue beat 4 on this mac"* / *"Also, make sure we are merging as we go"*.
  Earlier in the same chat the Team Owner had set the work order: *"We should work on things in order of how we are
  playing through the game"*, and the beat-5 call that beat 4 serves: *"We can let Splice allow the user to get past
  the attack Stunt Double and attack the boss directly."*

- **What happened:**

  The run picked up an interrupted one. On disk, uncommitted, were five imported ruin meshes and three city
  materials written at 14:27–14:29 local, plus a 361-line `tools/beat4_platforming.py`. The Unreal editor was no
  longer running and the `unreal` MCP answered `ECONNREFUSED`, so the first job was not Unreal work at all: get
  those eight `.uasset` files into git. That is the exact shape of the Splice loss the day before — one machine,
  no copy — and it was one `rm -rf` or one tidy-up away from happening twice.

  With the editor unreachable, the useful work was the part that never needed it: checking the section's numbers.

  **`docs/CITY.md` had sized the ruins wrong, and the proof was in the assets.** It asked for "a gap the player
  must blink is 6.5–8.5 m". The player's movement numbers settle that, and they turned out to be readable without
  a running editor: `BP_Player` serializes none of them, and its parent `BP_ThirdPersonCharacter` serializes only
  `JumpZVelocity` — exactly one `500.0` float in the asset, with no 420, 600 or 700 anywhere in it — beside
  `AirControl 0.35` and `BrakingDecelerationFalling 1500`, which is the UE5 template's signature trio.
  `MaxWalkSpeed` and `GravityScale` appear in neither asset's name table, so they are the engine defaults 600 and
  1, and no capsule override exists either, so `ACharacter`'s 34 × 88 stands and the player is 176 cm tall.

  A flat run-and-jump therefore carries `2×500/980 × 600` = 612 cm, about 680 with a capsule at each lip. A 6.5 m
  gap is *jumpable* — and it is also wider than the 600 cm blink, so there is no width at which the jump fails and
  the blink still works. The jump had to be removed some other way. It is removed with a **ceiling**: a collapsed
  slab 215 cm up. The player walks under it with 39 cm of head room; a jump spends that head room and stops, which
  collapses the arc to about 288 cm across a 400 cm gap. Splice is horizontal at chest height and goes under it.

  **Two defects in the script, both found before it ever ran, both of the kind that fakes a failure:**

  1. The two ceiling slabs sat at `y = ±170`, and `SM_RuinSlab_B` is only 320 cm deep — so they left a 20 cm slit
     running straight along `y = 0`. The player's capsule (r = 34) could never fit through it, so the *fight* was
     fine. The *measurement* was not: the script's own ceiling check traces upward at `y = 0` exactly, so it would
     have reported **"open sky" over both roofed gaps**, and whoever ran it would have gone hunting for a missing
     ceiling that was right there. They are at `±150` now and overlap across the centre line.
  2. The ground trace started at `z = 300`, which is *inside* the ceiling slabs (215–350). A line trace that begins
     inside a collider is start-penetrating and its result is not something to build on. It starts at `z = 200` now.

  Then the whole section was verified offline, from the piece table and `Art/Blender/export/City/city_models.json`,
  with no editor in the loop: solid ground as the street to 11200, `B4_P1` 11450–11950, `B4_P2` 12350–13350 and a
  1000 × 1500 cm landing pad at 13750–14750; gaps of 250 (open sky), 400 and 400 (roofed at 215); ceiling coverage
  `y −310..310` with **no holes**; and jump reach 680 / 288 / 288 against a 600 cm blink that crosses all three.

  One thing the arithmetic surfaced that a playtest has to judge: the blink is a fixed 600 cm and does **not** stop
  at a gap, so clearing gap 2 means launching from the eastern 200 cm of a 500 cm platform. Blink from the wrong
  end and you land in the hole.

- **What we learned:**
  - **A measurement that traces one line can be defeated by a 20 cm gap in your own geometry.** The section would
    have worked and the report would have said it did not.
  - **A character's tuning numbers are readable from the `.uasset` without opening Unreal.** Absence from a name
    table is itself the answer: it means the engine default, and that is a fact rather than an assumption. Cheaper
    and more reliable than a running editor, and it works when the editor is shut.
  - **Work that exists on exactly one machine's disk is not work yet.** Commit the imports before designing on top
    of them. This project has now lost a lane once and nearly lost another the same way.
  - A design doc's numbers are a proposal. `CITY.md`'s gap sizes were off in both directions and nothing would have
    caught it except doing the arithmetic.

- **Media:** none — the editor was closed for this run.
