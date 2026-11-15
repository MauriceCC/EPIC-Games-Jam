"""Make the guard's existing temporal interface resume after the requested duration."""
import unreal as u

lib = u.BlueprintEditorLibrary
guard = u.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
events = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
freeze = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(guard, 'ApplyTemporalFreeze'))


def link(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


def call(graph, path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def set_value(node, name, value):
    assert lib.find_input_pin(node, name).set_pin_value(value), name


if not any('B_EndTemporalFreeze' in str(lib.get_node_title(node))
           for node in events.list_all_nodes()):
    entry = next(n for n in freeze.list_all_nodes() if isinstance(n, u.K2Node_FunctionEntry))
    result = next(n for n in freeze.list_all_nodes() if isinstance(n, u.K2Node_FunctionResult))
    latch = next(n for n in freeze.list_all_nodes() if isinstance(n, u.K2Node_VariableSet))
    duration = lib.find_output_pin(entry, 'Duration')
    output = [pin for pin in lib.list_input_pins(result)
              if str(pin.get_pin_name()) != 'execute']
    assert len(output) == 1, 'Expected one effective-duration output'

    release = events.add_custom_event_node('B_EndTemporalFreeze')
    clear = events.add_set_member_variable_node('bIsTemporalFrozen')
    set_value(clear, 'bIsTemporalFrozen', 'false')
    link(lib.find_then_pin(release), lib.find_execute_pin(clear))

    tick = next(n for n in events.list_all_nodes() if n.get_name() == 'K2Node_Event_2')
    assert 'Tick' in str(lib.get_node_title(tick))
    tick_output = lib.find_then_pin(tick)
    tick_targets = list(tick_output.list_connected_pins())
    assert len(tick_targets) == 1
    gate = events.add_branch_node()
    frozen = events.add_get_member_variable_node('bIsTemporalFrozen')
    link(lib.find_output_pin(frozen, 'bIsTemporalFrozen'), lib.find_condition_pin(gate))
    link(lib.find_output_pin(gate, 'else'), tick_targets[0])
    link(tick_output, lib.find_execute_pin(gate))

    positive = call(freeze, 'KismetMathLibrary.Greater_DoubleDouble')
    link(duration, lib.find_input_pin(positive, 'A'))
    branch = freeze.add_branch_node()
    link(lib.find_result_pin(positive), lib.find_condition_pin(branch))
    set_value(latch, 'bIsTemporalFrozen', 'true')
    link(lib.find_then_pin(branch), lib.find_execute_pin(latch))
    link(freeze.find_graph_entry_pin(), lib.find_execute_pin(branch))

    stop = call(freeze, 'Controller.StopMovement')
    controller = call(freeze, 'Pawn.GetController')
    link(lib.find_result_pin(controller), lib.find_self_pin(stop))
    link(lib.find_then_pin(latch), lib.find_execute_pin(stop))
    timer = call(freeze, 'KismetSystemLibrary.K2_SetTimer')
    set_value(timer, 'FunctionName', 'B_EndTemporalFreeze')
    link(duration, lib.find_input_pin(timer, 'Time'))
    link(lib.find_then_pin(stop), lib.find_execute_pin(timer))
    link(lib.find_then_pin(timer), lib.find_execute_pin(result))
    link(lib.find_output_pin(branch, 'else'), lib.find_execute_pin(result))
    link(duration, output[0])

    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
    print('B_GUARD_FREEZE_SAVED')
