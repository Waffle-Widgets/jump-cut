# 2026-11-15 — The gameplay video, the last build and the submission (GameStation)

- **What we asked for:** the 30-60 second gameplay video the jam form requires, a fresh Windows build with
  the afternoon's imports in it, and help filling in the itch.io page and the jam form. All of it in the last
  two and a quarter hours before the 5:59 PM Pacific deadline.

- **Prompt(s) we gave the agent:**
  - *"Do you have the requirements for the video we need to submit?"* (3:43 PM)
  - *"Let's plan out the video before we start shooting."*
  - Manny's outline, which replaced the agent's shot list: *"the video opens up to the calm cafe and the car
    crash. The main character rushes over to check on the driver and as he touches him the power transfers to
    him. Just then the explosion starts to go off and the skill activates, he reacts quickly to pick up his
    coworker and move her out of harms way. Once she is safe time starts again. Cut to the thugs in the alley
    ... just before he gets punched he freezes time and throws punches at them ... Then it cuts to the boss
    teleporting around showing off his power. Then it cuts to black with the boss laughing and the title card
    displaying the name."*
  - *"Go ahead and make that video."*
  - *"in that cover art it looks like he is missing half his right leg."*
  - *"is there anyway to enable DLSS or any other Nvidia features to qualify for those prizes?"*

- **What happened:**
  - **The agent could not play the game, and said so.** A timed freeze before a punch and a 9-second rescue
    are out of reach when every key press takes it several seconds. Manny played one run in editor Play mode
    (2 min 32 s) with OBS recording; the agent did the edit.
  - **The first ffmpeg on the PC could not open the recording.** GameStation has two copies of ffmpeg that
    came with other programs. The one bundled with SteelSeries GG has no Matroska reader, so OBS's `.mkv`
    failed with *"Invalid data found when processing input"*. The one bundled with Lian-Li L-Connect is a full
    build and did the whole edit. Nothing was installed.
  - **The agent found the scenes without watching the video.** It made contact sheets (one frame every 2 s,
    then every 0.5 s for the three scenes), read them as pictures and picked nine cuts by timestamp.
  - **OBS had recorded at half size.** The profile's output was 1720x720 for a 3440x1440 screen, so the
    1920x1080 file is an upscale. We kept the full ultrawide picture with black bars, except the opening
    crash, which the game draws as a small 16:9 picture in the middle of a 21:9 view: that shot was cropped
    and enlarged to fill the frame. There was no time to record again.
  - **The recording was almost silent** (mean -53.9 dB, peak -28.5 dB), so the edit raises it 22 dB behind a
    limiter. The agent cannot hear; Manny checked it by ear.
  - **The result:** 42 seconds, 1920x1080, 60 fps, hard cuts only, ending on black and the name. No boss
    laugh: the game has no voice sounds and nobody had time to record one.
  - **The build:** the newest zip was from 2:50 PM and lacked everything imported since (the paved plaza, the
    lamps, the street and cafe props). A fresh package took 1.1 minutes, came to 330 MB and stayed up for the
    script's 20-second launch check.
  - **A scare at 5:08 PM:** *"Couldn't start ... JumpCut-Win64-Shipping.exe ... CreateProcess() returned 2"*.
    The build was fine. `JumpCut.exe` at the top of the zip is a 171 KB launcher, and it had been copied to
    the Desktop without the folders beside it. We added a "how to run" line to the page for the judges.
  - **The cover's leg.** The picture shows the barista mid-stride with one foot toward the camera and the
    knee hidden, which reads as half a leg. With no time to redraw, the cover was cropped to end at the apron.
  - **The NVIDIA award: we said no, twice.** No NVIDIA plugin was on the PC. Adding DLSS meant a download, an
    editor restart, the first compile of the day, a new package, a new play-through and a new 330 MB upload,
    with under an hour left and a tested build already uploaded. The NVIDIA boxes stayed unticked.
  - **Submitted** before the deadline, for Glass Box, Render Royalty and Best Team.

- **What we learned:**
  - Check the recorder's output size before the take, not after. One look at OBS's Video settings would have
    given us a native-resolution video.
  - The plan had the final build at noon and the video at 3 PM. We started the video at 3:43 PM while assets
    were still being imported. It worked, with nothing to spare; a first video on Saturday would have removed
    the risk.
  - A contact sheet lets an agent that cannot watch video still cut one.
  - Tell players to extract the whole zip. The launcher at the top of an Unreal build does nothing by itself.
  - The itch.io form takes a YouTube or Vimeo link, so the video's file size never mattered.

- **Media:** ![One frame per second of the finished 42-second video](../media/2026-11-15-gameplay-video-sheet.jpg)
