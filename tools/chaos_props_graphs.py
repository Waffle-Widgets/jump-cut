"""Graph text for "punches reach the furniture" (beats 1-3 clean-up, item 5, Nov 13).

BP_Player gains PlayerSmashProps (Hard bool), called once per punch from PlayerPunch:
  * every GeometryCollectionActor inside the punch arc (reach = PunchRange + 70) gets external strain at its middle
    (radius 150 for a light punch, 300 for the finisher) and a radial push. The same push throws the
    crate stack's pieces about 7x faster than a barrier's or a table's (measured), so actors tagged JC_BreakSoft
    get 0.15 of it;
  * every StaticMeshActor tagged JC_Knock inside the arc gets an impulse away from the player and up.
The assets and the placed actors come from tools/unreal_chaos_props.py.

Usage (maker-safe: this file only prints text):
    python tools/chaos_props_graphs.py > JumpCut/Saved/jcpy/chaos_props_graphs.json
The builder adds the function graph PlayerSmashProps with one bool input "Hard", pushes both graphs with
BlueprintTools.write_graph_dsl, compiles, then reads back and counts nodes.
"""
import json
from goon_individual_graphs import PLAYER, V

SMASH = f'''
(fn PlayerSmashProps (Hard)
  (bind here (Transformation|GetActorLocation))
  (bind fwd (Transformation|GetActorForwardVector))
  (bind reach (+ ({V}GetPunchRange) 70.0))
  (bind gcs (Actor|GetAllActorsOfClass "/Script/GeometryCollectionEngine.GeometryCollectionActor"))
  (for g gcs
    (bind gloc (Transformation|GetActorLocation :self g))
    (bind to (- gloc here))
    (bind dir (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x to) :Y (.y to) :Z 0.0)))
    (if (and (<= (Math|Vector|VectorLengthXY to) reach) (>= (Math|Vector|DotProduct :A fwd :B dir) ({V}GetPunchArcDot)))
      (bind comp (Class|GeometryCollectionActor|GetGeometryCollectionComponent :self g))
      (bind spot (+ gloc (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 55.0)))
      (bind soft (select (Actor|ActorHasTag :self g :Tag "JC_BreakSoft") 0.15 1.0))
      (ChaosPhysics|ApplyExternalStrain :self comp :ItemIndex 0 :Location spot :Radius (select Hard 300.0 150.0) :PropagationDepth 0 :PropagationFactor 1.0 :Strain 5000000.0)
      (Physics|AddRadialImpulse :self comp :Origin (- spot (* dir 60.0)) :Radius 300.0 :Strength (* (select Hard 500.0 300.0) soft) :Falloff "RIF_Linear" :bVelChange true)))
  (bind props (Actor|GetAllActorsOfClasswithTag "/Script/Engine.StaticMeshActor" :Tag "JC_Knock"))
  (for p props
    (bind ploc (Transformation|GetActorLocation :self p))
    (bind pto (- ploc here))
    (bind pdir (Math|Vector|Normalize (Math|Vector|MakeVector :X (.x pto) :Y (.y pto) :Z 0.0)))
    (if (and (<= (Math|Vector|VectorLengthXY pto) reach) (>= (Math|Vector|DotProduct :A fwd :B pdir) ({V}GetPunchArcDot)))
      (bind sm (Class|StaticMeshActor|GetStaticMeshComponent :self p))
      (Physics|AddImpulse :self sm :Impulse (+ (* pdir (select Hard 600.0 350.0)) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z (select Hard 300.0 180.0))) :bVelChange true))))
'''

_anchor = f'    ({V}SetComboStep (select fin 0 step))'
assert _anchor in PLAYER['PlayerPunch']
PUNCH = PLAYER['PlayerPunch'].replace(_anchor, '    (CallFunction|PlayerSmashProps :Hard fin)\n' + _anchor)

if __name__ == '__main__':
    print(json.dumps({'PlayerSmashProps': SMASH, 'PlayerPunch': PUNCH}, indent=1))
