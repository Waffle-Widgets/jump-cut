# The register move reaches Unreal, and beat 1 was quietly unwinnable

**Fri Nov 13, 2026, ~11:15 PM Pacific — M Station.** (Dated Pacific. Some older files in this
folder carry the UTC date for the same evening; their names are left alone so links do not break.)

Justin finished for the night and the Team Owner moved his queue to M Station. Of his four tickets,
two are editor work and two cannot be done by any machine at all: **#15** (play the 18-step list)
and **#16** (press F, E, Left Shift) need fingers on a keyboard, because combat input is polled on
tick with `IsInputKeyDown` and a simulated press releases inside one call. Those went to the Team
Owner rather than being shuffled between machines to look owned.

This entry is **#56**, the Unreal half of the register move.

## It was unblocked, and Justin's audit had been right

He stopped on #56 saying the maker half the ticket claimed was "already on `main`" was not — it was
sitting in open PR #57. He was correct when he looked, at `8af0e86`. PR #57 merged as `2134afd`
about two hours before this session, so every row of that table is now true. Declining to merge
another lane's PR was the right call and cost nothing.

## Three things in the way that nobody had hit

**The editor opens on a modal.** First launch on M Station stopped dead with a **Check Out Assets**
dialog, the log frozen mid-startup and the MCP accepting connections but answering nothing. It has
no Win32 children — it is a Slate window — so there is no button to click by handle; `PostMessage`
`WM_CLOSE` cancels it. Cancelling is the right answer here: this project coordinates with `git lfs
lock` on named files, not with Unreal source control, so a blanket check-out at startup is exactly
what we do not want.

**`save_actor` cannot save an actor in this map.** `Lvl_JumpCut` is One File Per Actor, so each
actor owns a package under `Content/__ExternalActors__/...`. Both `SceneTools.save_actor` and
`AssetTools.save_assets` resolve that package and then save it as a *registry asset*, which it is
not, and fail with `Asset does not exist: /Game/__ExternalActors__/...` for every actor. The
failure is loud but it is easy to misread as "the actor is fine". Clicking the toolbar's **Save
Current Level** returned `true` and wrote nothing. What proved the actors really were dirty was the
autosave: it wrote all five to `Saved/Autosaves/` and named the exact five packages.

The route that works is the one this repo already documented — real `unreal` through the console
box, `EditorLoadingAndSavingUtils.save_packages([a.get_outermost()], False)`. That is now
`tools/jc_save_actors.py`, which takes actor labels, re-sets each full transform to guarantee the
package is dirty, saves only those packages, and writes its result to `Saved/jcpy/` so you can
check the thing it wrote rather than its return value. It deliberately does **not** call
`save_dirty_packages`, which saves every dirty package in the project.

**`jumpcut_city_place.py add` would have made duplicates.** `add` mode skips any layout row whose
**actor label** is already in the level. Inserting the register at index 1 renumbers the whole cafe
block, so of 15 cafe rows only 7 labels still matched: `add` would have skipped the counter —
leaving it unmoved, the one thing the ticket exists to fix — and spawned **eight** duplicate shelves,
tables and chairs beside the ones already there. Checking position rather than label showed the
good news: every layout cafe spot already had an actor standing on it except the register, so the
geometry was right and only the labels had drifted. Doing the renames first made `add` correct, but
by then there was nothing left for it to add but the register, so it was placed directly with the
same treatment the placer gives every city mesh.

## Beat 1 could not be won, and that was not in the ticket

The ticket's step 4 said the rescue run shortens from ~7.5 m to ~4.1 m so the window would be "too
easy". Measured in the level, the opposite was true twice over.

**The rescue dragged her into the wreck.** `CoworkerSafeOffset` is `(0, +320, 0)`. From her new spot
that lands on `(-540, +159)`, and the crashed car spans `y = -91` to `+173` there — a chest-height
trace from her to that point stops after **61 cm**. `-Y` is no better: 39 cm, into the counter. The
aisle runs east, so the offset is now `(+320, 0, 0)` → `(-220, -161)`, clear along its whole length
with floor under it.

**The shrapnel could not reach her.** `CoworkerSpawnShrapnel` launches at
`GetActorLocation + (0,0,90)`, so it already aims at wherever she stands — moving her re-aims it and
no graph edit was needed, which is the one part of step 3 that turned out free. But its *start*,
`ShrapnelSpawnLocation = (-470, 0, 185)`, is level with the car, and from there the line to her new
spot behind the counter is blocked by the car's own cab after **73 cm of a 200 cm flight**. Every
spawn point on the car's flank that does reach her is only 83–108 cm away, which at
`ShrapnelSpeed` 260 inside 0.25 dilation is **1.7 real seconds** — against a 3.5 s bullet-time
window. The player could not win. It now starts at `(-330, -60, 370)`, just under the 4.00 m
ceiling: a clear 364 cm fall, **5.6 real seconds**, comfortably longer than the window. Debris
thrown up by the crash coming down on her also reads better than debris sliding out of the wreck.

`ShrapnelSpeed` was left at 260. Changing it is a feel call and nobody has played this.

## What is verified, and what is not

Verified by **reloading the level from disk**, not from the script's own report: all five actors on
their exact layout spots with one copy each, no duplicate labels anywhere, `JC_City` at **246**
matching the layout's 246 exactly, the shrapnel line clear, the new safe spot clear with floor under
it, and the two Blueprint values persisted through the reload. `tools/jumpcut_city_layout.py` passes
with the shrapnel lane rewritten to the new flight.

**Not verified: anybody playing beat 1.** Every number here is a trace or a distance, not a run.
The window is now 5.6 s against 3.5 s on paper; whether the rescue *feels* right at 4.1 m is step 4
of #56 and still needs a person. Where the player starts is still untouched and still a design call.

## One more thing the editor does on every open

Thirty assets — 23 sounds and 7 UI textures — **re-import themselves every time the editor starts**,
because their source files are committed next to them inside `Content/`. For 28 the source matches
and it is harmless churn. For `T_UI_Title` and `T_UI_ToBeContinued` the committed `Content/` copy
was the **old rejected picture**, so every editor launch quietly reverted the asset to it. That is
the opposite of the advice we wrote down ("leave the source beside the asset"): leaving a *stale*
source means the watcher overwrites good work on a schedule. Both `Content/` PNGs now match
`Art/UI/`, the watcher re-imported them, and both `.uasset` are saved — so a packaged build gets the
right pictures. `T_UI_Title` itself is superseded by the title animation (#64); it was fixed anyway
rather than left as a landmine.
