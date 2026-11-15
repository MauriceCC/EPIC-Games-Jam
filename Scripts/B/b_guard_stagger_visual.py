"""Add a brief stagger pose and a smooth return using the guards' existing rigs."""
import sys
from pathlib import Path

import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
tools = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(tools)]
import blueprint_helpers_c as h

worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not worlds.get_game_world()
bp = h.asset('Enemies/BP_GuardBase')
if h.edit(bp, 'B_UpdateStaggerPose'):
    raise RuntimeError('The guard already has a stagger presentation graph.')

h.variable(bp, 'B_StaggerPoseAlpha', h.basic('real'), '0.0', category='Stagger')
rotation_type = u.BlueprintEditorLibrary.get_struct_type(u.Rotator.static_struct())
h.variable(bp, 'B_StaggerRestRotation', rotation_type, '', category='Stagger')
h.compile_blueprint(bp, warnings_as_errors=True)

g = h.function(bp, 'B_UpdateStaggerPose', [('DeltaSeconds', h.basic('real'))])
active = h.get(g, 'bB_Stunned')
alpha = h.get(g, 'B_StaggerPoseAlpha')
alive = h.math(g, 'Greater_DoubleDouble', h.get(g, 'B_Health'), 0.0)
thawed = h.not_(g, h.get(g, 'bIsTemporalFrozen'))
has_pose = h.any_true(g, active, h.math(g, 'Greater_DoubleDouble', alpha, 0.0))
yes, _ = h.branch(g, g.find_graph_entry_pin(), h.all_true(g, alive, thawed, has_pose))
target = h.call(g, '/Script/Engine.KismetMathLibrary:SelectFloat', A=1.0, B=0.0, bPickA=active).find_result_pin()
# Approach the flinch faster than the recovery.
speed = h.call(g, '/Script/Engine.KismetMathLibrary:SelectFloat', A=9.0, B=3.5, bPickA=active).find_result_pin()
blend = h.call(g, '/Script/Engine.KismetMathLibrary:FInterpTo_Constant',
               Current=alpha, Target=target, DeltaTime=h.param(g, 'DeltaSeconds'), InterpSpeed=speed).find_result_pin()
end = h.setvar(g, yes, 'B_StaggerPoseAlpha', blend)
weight = h.get(g, 'B_StaggerPoseAlpha')
lean = h.call(g, '/Script/Engine.KismetMathLibrary:MakeRotator',
              Pitch=h.math(g, 'Multiply_DoubleDouble', weight, 16.0),
              Roll=h.math(g, 'Multiply_DoubleDouble', weight, 8.0)).find_result_pin()
rotation = h.call(g, '/Script/Engine.KismetMathLibrary:ComposeRotators',
                  A=h.get(g, 'B_StaggerRestRotation'), B=lean).find_result_pin()
h.call(g, '/Script/Engine.SceneComponent:K2_SetRelativeRotation', start=end,
       target=h.get(g, 'Mesh'), NewRotation=rotation, bSweep=False, bTeleport=True)
h.compile_blueprint(bp, warnings_as_errors=True)

g = h.edit(bp, 'EventGraph')
begin = next(n for n in g.list_all_nodes() if isinstance(n, u.K2Node_Event) and 'BeginPlay' in str(n.get_node_title()))
tick = next(n for n in g.list_all_nodes() if isinstance(n, u.K2Node_Event) and 'Tick' in str(n.get_node_title()))
before = begin.find_then_pin()
previous = list(before.list_connected_pins())
before.break_pin_links()
mesh = h.get(g, 'Mesh')
initial = h.get(g, 'RelativeRotation', target=mesh, cls=u.SceneComponent.static_class())
end = h.setvar(g, before, 'B_StaggerRestRotation', initial)
for successor in previous:
    h.connect(end, successor)
before = tick.find_then_pin()
previous = list(before.list_connected_pins())
before.break_pin_links()
update = h.invoke(g, before, bp, 'B_UpdateStaggerPose', DeltaSeconds=tick.find_output_pin('DeltaSeconds'))
for successor in previous:
    h.connect(update.find_then_pin(), successor)
h.layout(bp, {'B_UpdateStaggerPose'})
h.save(bp)
u.log('B_STAGGER_VISUAL saved')
