# 2026-11-15 — The crash sound lands when the car hits the wall, not when it stops (Justin's Mac mini)

- **What we asked for:** "Sounds around the car crash in the opening cinematic are mistimed." Line each sound's
  hit up with the frame it belongs to.
- **Prompt(s) we gave the agent:** relayed from Justin's list, item B: *"list them against the visual events ...
  and retime so each transient lands on its visual frame."*
- **What happened:**
  - There is only **one** sound in the crash: `SFX_CarCrash`, played by `BP_OpeningDirector.CineCrashSoundStep`.
    The explosion's sound belongs to the later explosion beat and already plays on the same frame as its fire.
  - Measured the file itself: an engine run-up, then the hit at **0.340 s** (first 50%-of-peak window), then
    glass for about 0.8 s.
  - Timeline of the opening (sequence keys in `tools/b1_opening_cine.py`, checked against the director's own
    values in the placed actor):

    | Visual event | Time | Sound before | Sound after |
    |---|---|---|---|
    | car bursts through the wall (wall breaks) | 4.70 s | - | crash hit **4.71 s** |
    | cab hits, driver thrown | 4.95 s | - | glass spray 4.75-5.5 s |
    | car rocks to rest | 6.20 s | crash hit **6.21 s** | - |
    | body lands (ragdoll on) | 6.47 s | none | none |
    | fire lights | 7.00 s | none | none |

    So the crash hit was arriving **1.51 s late**, on the car settling, because it was keyed to `CineImpactTime`
    (6.2 s, the frame the wreck takes over from the flying car) instead of the wall break.
  - **Fix:** in `CineCrashSoundStep`, swapped the `CineImpactTime` getter for `CineWallTime` and the lead from
    0.33 to 0.34 (the file's measured hit). Same node count (12), read back.
  - **Measured in PIE** with `tools/c2_pie.py crash`: the sound fires at director time 4.373 s, so its hit lands at
    4.713 s; the wall-break flag flips on the frame at 4.688-4.70 s. The sequence clock and the director clock
    agree within one frame (8.003 vs 8.000).
- **Left out:** the body landing and the fire lighting have no sound at all. Adding them would be new sounds, not
  a retime.
- **Not yet checked by a person:** this is timing by numbers. Audio output latency is not measured. Justin needs
  to watch the opening with sound on and say whether the hit lands on the wall.
- **What we learned:** "impact time" in this code meant the frame the wreck asset takes over, not the moment
  of impact. Name timing variables after what you see on screen.
