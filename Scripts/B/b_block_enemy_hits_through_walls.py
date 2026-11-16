"""Keep enemy melee and the Supervisor pulse from damaging through cover."""
from pathlib import Path
import sys

import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
toolset = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(toolset)]
import blueprint_helpers_c as h


def apply():
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    guard = h.asset('Enemies/BP_GuardBase')
    name = 'B_HasClearImpactPath'
    if h.edit(guard, name):
        return

    trace_graph = h.function(
        guard, name, inputs=(('Target', h.obj_type(u.Actor.static_class())),),
        outputs=(('Clear', h.basic('bool')),),
    )
    target = h.param(trace_graph, 'Target')
    ready, missing = h.branch(trace_graph, trace_graph.find_graph_entry_pin(), h.is_valid(trace_graph, target))
    h.result(trace_graph, missing, Clear=False)
    start = h.call(trace_graph, '/Script/Engine.Actor:K2_GetActorLocation').find_result_pin()
    end = h.call(trace_graph, '/Script/Engine.Actor:K2_GetActorLocation', target=target).find_result_pin()
    trace = h.call(
        trace_graph, '/Script/Engine.KismetSystemLibrary:LineTraceSingle', ready,
        Start=start, End=end, TraceChannel='TraceTypeQuery1', bIgnoreSelf=True,
    )
    impact = h.call(trace_graph, '/Script/Engine.GameplayStatics:BreakHitResult', Hit=trace.find_output_pin('OutHit'))
    clear = h.any_true(
        trace_graph, h.not_(trace_graph, trace.find_output_pin('ReturnValue')),
        h.math(trace_graph, 'EqualEqual_ObjectObject', impact.find_output_pin('HitActor'), target),
    )
    h.result(trace_graph, trace.find_then_pin(), Clear=clear)
    h.compile_blueprint(guard, warnings_as_errors=True)

    events = h.edit(guard, 'EventGraph')
    nodes = {node.get_name(): node for node in events.list_all_nodes()}
    # Gate the shared melee path before it chooses between the real player's
    # combat receiver and native damage. A blocked swing still enters cooldown.
    melee = nodes['K2Node_CallFunction_72']
    fallback = nodes['K2Node_CallFunction_9']
    pulse = nodes['K2Node_CallFunction_137']
    assert str(melee.get_node_title()) == 'GetActorOfClass'
    assert str(fallback.get_node_title()) == 'ApplyDamage'
    assert str(pulse.get_node_title()) == 'TakeHit'
    melee_target, = fallback.find_input_pin('DamagedActor').list_connected_pins()
    cooldown, = fallback.find_then_pin().list_connected_pins()
    pulse_target, = pulse.find_self_pin().list_connected_pins()

    def gate(attack, target_pin):
        entry = attack.find_execute_pin()
        previous, = entry.list_connected_pins()
        entry.break_pin_links()
        query = h.invoke(events, previous, guard, name, Target=target_pin)
        allowed, blocked = h.branch(events, query.find_then_pin(), query.find_output_pin('Clear'))
        h.connect(allowed, entry)
        return blocked

    h.connect(gate(melee, melee_target), cooldown)
    gate(pulse, pulse_target)
    h.layout(guard, {name})
    h.save(guard)
    u.log('B_IMPACT_VISIBILITY_SAVED')


apply()
