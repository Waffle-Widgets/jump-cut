# A simple, casual stand: the owner's character sheet, and what "less stiff" did not mean

*Sun 15 Nov 2026, about 7:15 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the idle again, with a picture this time: an anime character sheet of a boy standing,
  front, side and back.

- **Prompt we gave the agent:**

  > Give him a simple, casual pose like this for his idle animation and make sure his clothes don't clip through his
  > apron. Make sure his arms don't look twisted up.

- **What happened:**

  **The previous answer to "too stiff" was the wrong kind of answer.** An hour ago the idle got a contrapposto:
  weight on one leg, a dropped hip, shoulders tipped the other way, the two hands in different places. That is
  more POSE. The sheet asks for less: feet under the shoulders, legs straight, arms hanging straight down close to
  the body, shoulders level, head level. `clip_idle.py` is back to a symmetric stand and keeps its life in small
  movement only - a 1.6 degree breath that lifts the collarbones and hands, the weight drifting 0.8 cm, the head
  turning 3 degrees on its own clock.

  **The twisted arms were the palms.** In the sheet the palms face the thighs and the thumbs point forward. The
  model is bound with its palms facing FORWARD, and the idle rolled the forearm only 55 degrees of the 90 that
  takes: the palms ended up facing half forward, which is how an arm looks when it is turned outward at the
  shoulder. It is 86 now, shared across shoulder, elbow and wrist (30 degrees each), and the elbow points straight
  back.

  **A strip of trouser in front of the apron's edge.** The apron's clearance check sampled the most forward THIRD
  of each leg's vertices. The skirt's side edge wraps round the outer front of the thigh, which is not in the
  front third. It samples the front half now (1,251 points, was 834).

  **Every other clip follows.** They start and end on this stand through the `STANCE` table in `cw_clip.py`, which
  now carries the palms too.

  ![The stand against the plumb line: his left side, his right side, front](../media/2026-11-15-simple-stand.png)
  ![In the game: front, side, back, three-quarter](../media/2026-11-15-simple-stand-in-game.png)

- **Not verified:** the idle was seen in the game as four stills. Its movement - whether the breath and drift
  read as alive or as nothing at all - needs a person watching it for a few seconds.

- **What we learned:**
  - "Too stiff" has two opposite fixes, more pose or more motion, and the reference picture says which. Ask for
    the picture before choosing.
  - When an arm "looks twisted", check which way the palm faces before touching the shoulder.
