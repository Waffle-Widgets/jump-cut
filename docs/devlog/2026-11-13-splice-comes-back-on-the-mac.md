# Splice comes back, on a different machine

*Fri Nov 13 2026, 18:20 UTC — Justin's Mac mini*

Splice was built and measured on GameStation yesterday evening and then lost: the editor's "Save Content"
dialog was clicked through at 17:44 UTC with `BP_Player` and `WBP_HUD` still dirty, almost certainly to give
the 5090 back to the renders. The committed assets had no Splice in them. It is on disk now, rebuilt here.

## The open question answered itself

The ask left on the board was "restore from the autosave, or re-run the recipe?" On this machine there is only
one answer. The autosaves were copied to `JumpCut/Saved/jcpy/recovered/` — on GameStation, outside git. They
are not on the Mac and never were. So the route was `tools/splice_graphs.py`, which is also the route the
recipe itself says reproduces exactly what was tested.

Worth recording for next time: a recovery artefact kept deliberately outside git is a recovery artefact that
exists on exactly one machine. The recipe travelled because it was committed.

## What the Mac turned out to have

The established note in this project said the Mac mini had no jump-cut clone and no git-lfs. Both are now
wrong. There is a clone at `~/Documents/GitHub/jump-cut` with all 469 LFS objects materialised, `git-lfs`
3.8.1, and a full 43 GB UE 5.8 install at `~/Epic Games/UE_5.8` — not the `/Users/Shared` path the launcher's
folder suggests. `ModelContextProtocol` ships with that engine and is already built for Mac, so the editor
exposes the same toolset GameStation drives. Nothing about this work is Windows-only.

One wrinkle: the MCP server only listens once the editor is running, so a session that starts with Unreal
closed binds no Unreal tools at all. Driving the endpoint directly over HTTP works fine — it is an ordinary
streamable-HTTP MCP server on `127.0.0.1:8000/mcp`, and `call_tool` takes `toolset_name` and `tool_name`
separately.

## Checked at the pin level, because the printer can hide a wrong graph

`read_graph_dsl` collapses two things that matter here, so reading the DSL back is not enough:

- The stop-short vector came back printed as `(Math|Vector|vector-vector (Collision|BreakHitResult _outhit) ...)`,
  which reads as "the hit result's first pin" — `bBlockingHit`, a boolean. The actual wiring is **output 5,
  `ImpactPoint`**, which is correct. The printed form and the right answer are indistinguishable.
- The trace's keyword arguments did not print at all. Read directly: `TraceChannel = TraceTypeQuery1`
  (Visibility), `bIgnoreSelf = true`, `bTraceComplex = false`.

Visibility is the entire design. The Pawn collision preset ignores that channel, so the blink passes through
people and stops only on world geometry — which is what makes the Team Owner's beat-5 call work with no code
in the stunt-double fight at all.

All nine defaults read back exact. `BP_Player` compiled with warnings as errors, one `(fn ...)` per graph (no
duplicate append).

## The HUD box was never a restore

The `WBP_HUD` autosave pre-dated the `HudRefresh` edit by six seconds, so those lines had never been saved
anywhere — on this machine or that one. They are new work. `SpliceBox`, `SpliceIcon`, `SpliceKey` and
`SpliceBar` now sit third along the bottom-left row in violet, labelled `SHIFT`.

Two notes. `AddWidget` will not take a null parent on a tree that already has a root — it has to be told
`HudRoot` explicitly, or it fails with "Widget can't have children". And exactly as the recipe predicted, the
`CanvasPanel` and the `TextBlock` came out as non-variables while the `Image` and `ProgressBar` came out as
variables already; `HudRefresh` cannot reference a non-variable, so both needed toggling.

Because patching `HudRefresh` means rewriting the whole function, all **11** `HudShowIf` nodes were audited
afterwards to confirm every `Target` pin still pointed at its widget. None was lost.

## Two traps, both silent

**`HudShowIf` prints positionally but takes a `Target` parameter.** Writing the function back as printed is
rejected outright — "Could not connect pin HudPlayerRef to self" — and the whole write is discarded. Every
call needs the `:Target` / `:Show` keyword form, not only the new ones.

**The reader mis-attributes the player's health getters.** `GetHealth` and `GetMaxHealth` print as
`Class|AbilitySystemTestAttributeSet|...`, a colliding engine class. Written back as printed they are rejected
the same way; they have to be `Class|BPPlayer|`.

Both failures look like a problem with your edit. Neither is.

## What is verified and what is not

Verified here: the graphs, pin for pin; the defaults; a clean compile with warnings as errors; a clean map
check; a Play-In-Editor session in which the live pawn carries every Splice value and produced **no Blueprint
runtime errors**.

Not verified here: **nobody has pressed Left Shift.** The distances in the GameStation entry — 600 cm open,
0 on cooldown, 455 against a wall 500 away, 600 straight through a goon and through the cleaver boss — are
that machine's measurements and were not re-taken. Re-taking them needs the temporary debug hook again: the
Splice variables are not instance-editable, and the editor's tool-script sandbox has no `unreal` module, so
`SpliceStart` cannot be driven from outside. Given the graph is pin-for-pin identical to the one that produced
those numbers, that was not worth spending feature-freeze day on.

Beat 4 still has no gaps to cross. The power exists; the platforming does not.
