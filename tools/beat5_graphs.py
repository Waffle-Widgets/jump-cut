# Beat 5: the two Blueprint changes the Stunt Double fight still needs.
#
# WHAT THIS FILE IS, AND HOW IT DIFFERS FROM tools/splice_graphs.py
# -----------------------------------------------------------------
# splice_graphs.py is a recipe for work that was BUILT AND MEASURED and then lost before it
# reached disk, so every id in it compiled and was read back. THIS FILE HAS NOT BEEN COMPILED.
# It was written on Justin's Mac mini on Fri Nov 13 2026 while the editor's MCP server was
# unreachable (it failed to bind 127.0.0.1:8000 at startup - see the devlog), from what the
# committed .uasset name tables actually contain. Treat the DSL below as a PROPOSAL to read
# back and correct, not as a transcript of something that worked. The DESIGN and the FINDINGS
# are solid; the node ids are the part to check.
#
# THE TWO FINDINGS THAT MADE THIS NECESSARY, read out of the committed assets
# --------------------------------------------------------------------------
#   strings BP_BossFreeze.uasset    -> BossExitGate, PlazaGateOpenForGood
#   strings BP_EnemyBase.uasset     -> neither
#   strings BP_StuntDouble.uasset   -> neither, and no BP_PlazaGate reference anywhere
#   strings BP_StuntStandIn.uasset  -> StandInFights and nothing else of its own
#
# 1. BEAT 5 HAS NO ENDING. BossExitGate and the EnemyDefeatedHook line that opens it live on
#    BP_BossFreeze, which is the CLEAVER boss. BP_StuntDouble is a BP_EnemyBase child, so when
#    the Stunt Double dies nothing opens, nothing is handed over, and the level just stands
#    there. This was never noticed because his fight was tested by calling functions and
#    reading health, which is exactly the kind of check that passes while the beat is unfinishable.
# 2. THE DESPAWN TIMER IS GENUINELY UNBUILT (issue #9). BP_StuntStandIn carries one variable of
#    its own, StandInFights. There is no idle, linger or despawn float anywhere in it.
#
# ------------------------------------------------------------------------------------------
# CHANGE 1 - the despawn timer (issue #9)
# ------------------------------------------------------------------------------------------
# The Team Owner's words: "The attack Stunt Double stays on the field only while in combat; a
# timer starts on him to disappear once nothing is in range to attack."
#
# IT GOES ON THE BOSS, NOT ON THE STAND-IN, and that is a deliberate choice:
#
#   * The boss already owns the attack stand-in. BossCallFighter holds FighterRef and allows at
#     most one alive at a time. If the stand-in destroyed itself, FighterRef would be left
#     dangling and the boss would never tag another one in - the despawn would silently end the
#     bodyguard trick for the rest of the fight instead of recycling it.
#   * The SOAK doubles must never despawn. They are BP_StuntStandIn too, with StandInFights
#     false, and they stand still by design with nothing in range to attack - which is exactly
#     the condition a timer on the stand-in would fire on. A despawn living on the stand-in
#     would delete the boss's entire damage shield a few seconds into every fight, which is the
#     opposite of the fight the Team Owner described. Keeping it on the boss, scoped to
#     FighterRef, cannot touch them.
#   * It makes the recorded intent true: "running away from the bodyguard a real option rather
#     than a stall" (docs/ROADMAP.md). Walk out of his reach and he walks off set.
#
# NEW VARIABLES on /Game/Game/Blueprints/BP_StuntDouble.BP_StuntDouble (BlueprintTools.add_variable):
#   float FighterIdleTimeout   default 4.0   INSTANCE EDITABLE (so a playtest can tune it without a recompile)
#   float FighterIdleLeft      default 0.0
#
# NEW FUNCTION GRAPH: BossTickFighter(DeltaSeconds: float)
#
# TIME-STOP: do NOT add a check for EnemyTimeStopped here. Confirm instead that the base's tick
# already skips EnemyThink while time-stopped (that is how the diving redirect is suppressed), in
# which case this is free. If it does NOT skip, add the guard - otherwise Freeze Frame would run
# the despawn clock down and make bodyguards evaporate when the player freezes time, which is a
# different and much stronger power than the one that was designed.

BOSS_TICK_FIGHTER = r'''
(fn BossTickFighter (DeltaSeconds)
  (bind f (Variables|Default|GetFighterRef))
  (if (Utilities|IsValid :Object f)
    (bind me (Transformation|GetActorLocation))
    (bind reach (Variables|Default|GetEnemyAttackRange))
    (bind d (CallFunction|EnemyDistToPlayer :self f))
    (if (> d reach)
      (Variables|Default|SetFighterIdleLeft (- (Variables|Default|GetFighterIdleLeft) DeltaSeconds))
      (Variables|Default|SetFighterIdleLeft (Variables|Default|GetFighterIdleTimeout)))
    (if (<= (Variables|Default|GetFighterIdleLeft) 0.0)
      (Actor|DestroyActor :self f)
      (Variables|Default|SetFighterRef none)
      (Variables|Default|SetFighterIdleLeft 0.0))))
'''

# IDS TO CHECK WITH get_node_infos BEFORE TRUSTING THE ABOVE - each of these is a guess:
#   Utilities|IsValid            the validity check's real id and whether its pin is :Object
#   CallFunction|EnemyDistToPlayer   calling one of OUR functions on ANOTHER actor. The target pin
#                                    is the trap: a positional argument lands in `self` and would
#                                    measure the BOSS's distance to the player, not the fighter's -
#                                    which still compiles and still looks plausible in play.
#   Actor|DestroyActor           needs the fighter in its target pin, not the boss. Same trap.
#   SetFighterRef none           how the DSL spells a null object literal. If there is no spelling
#                                for it, make a Blueprint-local `BossNoFighter` variable that is
#                                never assigned and set FighterRef from that.
#
# THEN, the one-line hook. BossCallFighter and EnemyThink BOTH already exist on BP_StuntDouble.
# write_graph_dsl REPLACES A WHOLE GRAPH, so:
#   1. read_graph_dsl on BP_StuntDouble:EnemyThink and keep the text as the backup.
#   2. Add exactly one `(CallFunction|BossTickFighter DeltaSeconds)` near the top of it, before
#      the existing state work, and write it back.
#   3. read_graph_dsl again and COUNT the call sites of BossTickFighter. write_graph_dsl appending
#      twice looks identical to appending once until you count.
#   4. compile_blueprint(warnings_as_errors=True).
#
# ------------------------------------------------------------------------------------------
# CHANGE 2 - give beat 5 an ending
# ------------------------------------------------------------------------------------------
# Mirrors BP_BossFreeze exactly (docs/FIRST_BUILD_DESIGN.md:519 and :543), so the two bosses end
# their beats the same way and tools/beat5_arena.py can wire the gate the same way d1_editor.py does.
#
# NEW VARIABLE on BP_StuntDouble:
#   BossExitGate   object ref -> BP_PlazaGate   default none   INSTANCE EDITABLE
#                  (instance editable is not optional: beat5_arena.py sets it on the PLACED boss,
#                   and ObjectTools.set_properties only writes instance-editable variables.)
#
# PATCH EnemyDefeatedHook, which already exists on BP_StuntDouble (it clears his stand-ins). Read
# it out first, then add this to the END of it, after the existing clear:
#
#   (if (Utilities|IsValid :Object (Variables|Default|GetBossExitGate))
#     (CallFunction|PlazaGateOpenForGood :self (Variables|Default|GetBossExitGate)))
#
# HE HANDS OVER NO POWER, deliberately. BP_BossFreeze has BossHandOverPower because the cleaver
# boss gives Splice. Whether the player ever GETS the Stunt Double power in the demo is still an
# open decision (GitHub issue #21), so this change does not pre-empt it: it opens the gate and
# nothing else. If #21 comes back "yes", that is one more call in the same hook.
#
# ------------------------------------------------------------------------------------------
# AFTER BOTH CHANGES
# ------------------------------------------------------------------------------------------
#   1. compile_blueprint(warnings_as_errors=True) on BP_StuntDouble.
#   2. ObjectTools.set_properties on /Game/Game/Blueprints/BP_StuntDouble.Default__BP_StuntDouble_C
#      with DEFAULTS below, then READ EVERY VALUE BACK. An exposed variable can accept a write with
#      no error at all and still read back unchanged.
#   3. Save BP_StuntDouble (git lfs lock it first - it is committed, so it is read-only and the
#      save fails silently).
#   4. Run `py tools/beat5_arena.py`. Its report now prints
#      `Boss_StuntDouble.BossExitGate = Gate_Beat5Exit` instead of the "beat 5 has no ending"
#      warning. That is the check that this change actually landed.
#   5. A PLACED Boss_StuntDouble will NOT pick up the new variables - a new variable's default does
#      not reach an actor already in the level, and it keeps its own serialized value in its own
#      actor package. Place the arena AFTER this change, or re-place the boss.
#
# WHAT A PERSON STILL HAS TO JUDGE, because none of it is measurable from here: whether 4 seconds
# is the right walk-off delay, whether the double leaving reads as a film gag or as a bug, and
# whether killing the boss and seeing a gate rise is an ending or an anticlimax (that last one is
# beat 6, issue #10).

DEFAULTS = {
    'FighterIdleTimeout': 4.0,
    'FighterIdleLeft': 0.0,
    # BossExitGate is left at none on the CDO on purpose: it is a level reference, so it is set on
    # the placed actor by tools/beat5_arena.py, never on the class.
}
