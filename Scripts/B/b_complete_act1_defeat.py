"""Finalize the defeated pose and keep Frame Cut from selecting a downed guard."""
import sys
from pathlib import Path

import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
tools = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(tools)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
guard = h.asset('Enemies/BP_GuardBase')
g = h.edit(guard, 'B_ApplyHealthDamage')
state = next(n for n in g.list_all_nodes()
             if isinstance(n, u.K2Node_VariableSet) and n.find_input_pin('CurrentAIState').is_valid())
param = state.find_input_pin('CurrentAIState')
if u.BlueprintEditorLibrary.get_member_variable_type(guard, 'B_DefeatedState') is None:
    h.variable(guard, 'B_DefeatedState', param.get_pin_type(), '', category='Combat')
    h.compile_blueprint(guard, warnings_as_errors=True)
    g = h.edit(guard, 'B_ApplyHealthDamage')
    state = next(n for n in g.list_all_nodes()
                 if isinstance(n, u.K2Node_VariableSet) and n.find_input_pin('CurrentAIState').is_valid())
    param = state.find_input_pin('CurrentAIState')
defaults = u.get_default_object(guard.generated_class())
state_type = type(defaults.get_editor_property('CurrentAIState'))
defaults.set_editor_property('B_DefeatedState', state_type.DEFEATED)
h.connect(h.get(g, 'B_DefeatedState'), param)
# Leave the actor and its capsule at the defeat location. Rotate and stop
# only the rendered mesh, so the neutralized person stays on the ground.
poses = [n for n in g.list_all_nodes() if 'Set Actor Rotation' in str(n.get_node_title())]
if poses:
    previous, = poses[0].find_execute_pin().list_connected_pins()
    successors = list(poses[0].find_then_pin().list_connected_pins())
    g.remove_nodes(poses)
    mesh = h.get(g, 'Mesh')
    lean = h.call(g, '/Script/Engine.KismetMathLibrary:MakeRotator', Pitch=87.0).find_result_pin()
    rotation = h.call(g, '/Script/Engine.KismetMathLibrary:ComposeRotators',
                      A=h.get(g, 'B_StaggerRestRotation'), B=lean).find_result_pin()
    down = h.call(g, '/Script/Engine.SceneComponent:K2_SetRelativeRotation', start=previous,
                  target=mesh, NewRotation=rotation, bSweep=False, bTeleport=True)
    pause = h.call(g, '/Script/Engine.ActorComponent:SetComponentTickEnabled',
                   start=down.find_then_pin(), target=mesh, bEnabled=False)
    for successor in successors:
        h.connect(pause.find_then_pin(), successor)

g = h.edit(guard, 'IsDefeated')
h.clear_body(g)
h.result(g, g.find_graph_entry_pin(),
         Result=h.math(g, 'LessEqual_DoubleDouble', h.get(g, 'B_Health'), 0.0))
h.save(guard)

# The player currently calls the guard Blueprint directly. Preserve that
# entry point while applying the guard's existing target-eligibility check.
player = h.asset('Player/BP_PlayerCharacter')
g = h.edit(player, 'DoTemporalCut')
if not any('CanBeTemporalCutTarget' in str(n.get_node_title()).replace(' ', '') for n in g.list_all_nodes()):
    nodes = {n.get_name(): n for n in g.list_all_nodes()}
    closer = nodes['K2Node_IfThenElse_1'].find_then_pin()
    accept, = closer.list_connected_pins()
    candidate = nodes['K2Node_MacroInstance_0'].find_output_pin('Array Element')
    closer.break_pin_links()
    check = h.invoke(g, closer, guard, 'CanBeTemporalCutTarget', target=candidate)
    eligible, _ = h.branch(g, check.find_then_pin(), check.find_result_pin())
    h.connect(eligible, accept)
    h.save(player)
u.log('B_ACT1_DEFEAT saved downed pose and Cut target filter')
