# Beat 1 plays itself: no key presses, letterbox bars, and only one car

**Sat 14 Nov 2026, evening.** Justin played the opening cinematic that landed an hour
earlier and sent six pieces of feedback. Five of them are built; one is a question with
an answer rather than a change.

## What he asked for

> 1. I can see two cars. I think the map one is spawned in on impact. Needs to be
>    created once the cinimatic one settles. 2. Fire is a cone, do we have fire assets?
>    3. I see two sphere markers at the first point. One moving up and down. I think
>    that one. Though it's shape should be a cone pointing down. 4. We shouldn;t need
>    to click anything when hitting these checkpoints. Just move on with the story
>    beats. Probably need text boxes to tell the player what to do and provide the
>    storyline. 5. When we get to the cowoker lets have pulling them out of the way be
>    a cinematic. Not needing the player to do it. 6. Can we transition in the
>    widescreen black boxes on the top and bottom of the screen when entering/exiting
>    cinematics. Giving the player a hint they are in/out of control

## 1. Two cars — the timing was off by 1.5 seconds, and the keyframes said so

`LS_Beat1_Opening`'s `CineCar` spawnable stops moving at **frame 186 (6.20 s)**, at
exactly `(-520, 0, 0)` rotation zero — which is the real wreck's placed transform.
`BP_OpeningDirector.CineImpactTime` was **4.70 s**, frame 141, where the spawnable is
still in the air at `x = -900`. So the real wreck appeared on impact and the thrown one
kept flying into it: two cars, for a second and a half.

`CineImpactTime` is now **6.20**, and the `CineCar` spawn track gets a `False` key at
frame 186 so the cinematic car is despawned on the same frame the real one appears.
They never coexist — which also matters because two identical coincident meshes are a
perfect depth tie, the exact defect we spent yesterday removing from the city kit (#67).
The thrown body gets the same treatment at frame 194, where the real body appears.

## 3. The second sphere was the "press F" prompt, and it is drawn every tick

There were three spheres near the first objective, not two. `Marker_Crash` and
`Marker_FreezeFrameGiven` are already invisible (`vis=False` on their components), so
they were not it. The culprit is `BP_CrashDriver`'s own **`TouchPrompt`** component, and
hiding it in the level would not have worked: `DriverTickStep` ran
`SetVisibility(TouchPrompt, DriverCanTouch())` **every frame**, so it switched itself
back on the moment the player got close. It is now hidden unconditionally.

`B1_Objective_Beacon` becomes a cone pointing down — `/Engine/BasicShapes/Cone`, pitch
180, scale `(0.45, 0.45, 0.7)`, keeping its `M_PropBlue` material and its bob.

The coworker carries the identical leftover (`RescuePrompt`, shown by
`CoworkerCanRescueNow`). It is **not** fixed in the Blueprint: `CoworkerTickStep` turned
out to have 42 nodes for 7 printed statements — orphans from an earlier rewrite — and
rewriting it the day before submission is not worth it. In practice the prompt can only
appear for about one frame now, because the moment `CoworkerCanRescueNow` is true the
director starts the rescue, which sets `Holding` and makes it false again.

## 4 and 5. The beat advances by walking, and the rescue is a cinematic

Both of these turned out to be the same change, and most of the work was already in the
Blueprints. `DriverTryTouch` and `CoworkerCanRescueNow` were **already range-gated** —
the F key only decided *when* to ask. So the director now asks every tick while the
objective is live, and "press F in range" becomes "get close enough".

- Walk up to the driver → Freeze Frame is granted, caption, objective moves on.
- The car catches fire on its own two seconds later, caption.
- Walk up to the coworker → **the rescue takes over**. Input and movement lock, the bars
  come in, `CoworkerTryRescue` takes her hand, the director walks the player to the safe
  spot with her following, the car goes up, control comes back, caption.

`BP_OpeningDirector.AutoBeats` (instance-editable, default on) puts the key presses back.

The captions are a new widget, `WBP_CineOverlay`, created and owned by the director:
two black bars and a caption box. Nothing else in the game has to know about it.

## 6. Letterbox

The same widget. `CineBarsSet(Alpha)` scales both bars from their outer edge, and the
director lerps `BarAlpha` toward `BarTarget` at 3.2/second: in at the start of the
opening, out when control is handed over, in again for the rescue, out at the end.

## Four things that cost time, all now in CLAUDE.md

**A positional argument to `CallFunction|X` lands in the SELF pin.**
`(CallFunction|CineRescueStep DeltaSeconds)` fails with *"Could not connect pin
DeltaSeconds to self"*. Worse, `read_graph_dsl` **prints** calls in exactly that form, so
reading a graph and writing it back is not safe. Name every pin:
`(CallFunction|CineRescueStep :DeltaSeconds DeltaSeconds)`.

**A swept `SetActorLocation` that begins already touching something returns to the START
point.** The first rescue build moved the player **zero centimetres in 4.4 seconds**
while the fuse ran out and the blast killed her, because he was standing against a cafe
table. `bSweep` is false for the cinematic move; it is a directed shot down an aisle he
has just walked up.

**A UMG `Border`'s default brush draws nothing.** It is `DrawAs = Image` with
`ImageType = NoImage` and `ResourceObject = None`, so setting `BrushColor` tints an empty
brush and you get an invisible panel that reports a perfectly healthy render transform.
Give it `/Engine/EngineResources/WhiteSquareTexture` and tint that.

**`CaptureEditorImage` does not composite UMG.** Three captures of the running game came
back with no bars and no caption while the live widget reported
`renderScale = (1, 1)`, `visibility = HitTestInvisible` and `IsInViewport = True`. The
instrument cannot see the thing being measured. `SlateInspector.WaitFor` on the caption's
own text **does** find it — that is the check to use for a widget.

## Measured, in Play mode, with no key pressed at any point

Driver step: `DriverTouched` false → **true** and `HasFreezeFrame` false → **true** on
proximity alone. Objective 1 → 2 → 3. Captions advanced through all four lines.

Rescue: player `(-360, -101)` → **`(382.8, -45.8)`**, coworker `(-540, -161)` →
`(273, -59)` = **796 cm** from the blast origin against a 700 cm radius,
`Blown = true`, **`CoworkerDead = false`**, player health **100** (it was 70 when she
died in the broken run). Bars 0 → 1 → 0, input locked then released, caption
"Out to the street."

## What is not done

**Nobody has looked at this.** Every number above is a script reading live actors, and
the one thing that needs eyes — do the black bars and the caption box actually look
right — is the one thing the capture path provably cannot show.

**Freeze Frame is now granted and never used by the player in beat 1.** The rescue is a
cinematic, so the power that beat 1 exists to teach is never pressed. The cinematic could
call `FreezeFrameStart` itself and play the rescue in bullet time; it does not yet,
because time dilation would stretch every number in `CineRescueStep`.

**2. Fire.** The flame is still a stylised orange cone. See the next section.

## 2. Do we have fire assets? Precisely:

- **`T_FX_Explosion_6x6`** — a 36-frame AI-generated explosion sheet, imported at
  `/Game/Game/FX/Textures/`. It is an *explosion*, not a loop, and nothing uses it:
  the blast currently has no visual at all, which is a bigger hole than the cone.
- **`tools/unreal_make_fire_flipbook_mat.py`** — the recipe for real fire, baked from a
  Niagara Fluids sim to an 8x8 atlas. The script is here; **the atlas it reads
  (`NS_FireBoomFluid3D_BakedAtlas_Texture2D_0`) is not in this project** — it came from
  the practice repo. Baking a new one needs Niagara Fluids and a sim bake (the
  `niagara-fluids` skill covers it).
- No looping fire sheet, no `NS_*` fire system, no Starter Content.

So: a believable fire is a bake, not a swap. The cheap win in between is to put
`T_FX_Explosion_6x6` on the blast as a SubUV card, which costs one material and one
actor and gives the explosion a picture.
