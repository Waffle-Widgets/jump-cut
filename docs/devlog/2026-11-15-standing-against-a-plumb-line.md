# Standing against a plumb line: the owner sent photographs of people standing, and we measured ours

*Sun 15 Nov 2026, about 4:30 AM Pacific — GameStation · Blender 5.3.0 · by Fable 5.2 (`claude-fable-5-2`)*

- **What we asked for:** the idle rebuilt an hour earlier still was not right. The owner sent four pictures of people
  standing idle, three photographs from the side and an anime character sheet.

- **Prompt we gave the agent:**

  > here are some examples of people standing up idle.

- **What happened:**

  **What the references share,** written down before touching anything: from the side, the ear, the shoulder, the
  hip and the ankle sit on ONE vertical line; the knees are straight; the arms hang straight down beside the body
  with the hand resting a little in front of the hip; the head is level.

  **A tool that measures exactly that.** `Art/Blender/posture_check.py` prints how far forward of the ankle each
  landmark sits, the bend at knee and elbow, and how far outside the hips the hands hang, then renders the pose
  large from both sides and the front with a red plumb line through the ankle. The contact sheets we had been
  judging by are 230 pixels a tile; none of this was visible in them.

  ![The idle from an hour earlier, with the plumb line](../media/2026-11-15-posture-before.png)

  | | an hour ago | now | the references |
  |---|---|---|---|
  | head tilt, forward of vertical | 12 degrees: staring at the floor | 4 | level |
  | shoulders relative to the hips | 5-8 cm BEHIND | on them | on them |
  | knee bend (the bones' own kink is about 19) | 29-30 | 19-20 | straight |
  | hands outside the hip joints | 13-17 cm, an "A" | 7-11 | beside the body |
  | elbow bend | 3: locked | 15: relaxed | slight |

  The changes are five numbers at the top of `clip_idle.py`, each with the measurement that set it: the pelvis
  pitched 5 degrees to bring the shoulders over the hips, the head lifted 12, the legs straightened, the hands
  brought in and a little forward, the collarbones eased from 28 to 24 and drawn back.

  **"The ragged hem" was a thigh.** The front view showed bites out of the bottom of the apron. The first guess was
  that the skirt's vertex selection had missed the shaded hem, and growing the selection did add 126 vertices -
  but the picture did not change. The bite was his LEFT THIGH coming through the corner of the skirt. The apron's
  clearance check allowed each point on a leg to come "no closer than it sits at rest", and the model rests with
  its legs spread wider than the skirt: the outer thighs sat BESIDE it and further forward than its surface, so
  they were still allowed that far forward when he stood with his legs together. Now no point is allowed further
  forward than the back face of the panel it is under, measured from the skirt's own vertices.

  ![Now: both sides and the front](../media/2026-11-15-posture-after.png)
  ![In the game: side, front, back](../media/2026-11-15-idle-in-game-against-references.png)

- **Not done:** this is one pose. Every attack still begins and ends on the older neutral stand (ankles behind the
  hips, head down), and blends to this idle. The same five numbers belong in that neutral stand too.

- **What we learned:**
  - Write down what the reference shows as things that can be MEASURED, then measure. "Does it look like the
    photo" got this wrong twice in one night.
  - When a picture does not change after a fix, the fix was for a different problem. Look again at what the
    picture actually shows before making the fix bigger.
