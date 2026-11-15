"""Interrupt guard movement and attacks when accumulated hits break posture."""
import unreal as u

lib = u.BlueprintEditorLibrary
path = '/Game/Unscripted/Enemies/BP_GuardBase'
guard = u.load_asset(path)


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(name):
    node = graph.add_call_function_node('/Script/Engine.' + name)
    assert node, name
    return node


def set_default(node, field, value):
    assert lib.find_input_pin(node, field).set_pin_value(value), field


def get(var):
    return lib.find_output_pin(graph.add_get_member_variable_node(var), var)


def add_stun_gate(condition, inverted=False):
    prior, = condition.list_connected_pins()
    stun = get('bB_Stunned')
    if inverted:
        negate = call('KismetMathLibrary.Not_PreBool')
        link(stun, lib.find_input_pin(negate, 'A'))
        stun = lib.find_result_pin(negate)
    logic = 'BooleanAND' if inverted else 'BooleanOR'
    combine = call('KismetMathLibrary.' + logic)
    link(prior, lib.find_input_pin(combine, 'A'))
    link(stun, lib.find_input_pin(combine, 'B'))
    link(lib.find_result_pin(combine), condition)


if 'bB_Stunned' not in {str(n) for n in lib.list_member_variable_names(guard)}:
    assert lib.add_member_variable(guard, 'bB_Stunned', lib.get_basic_type_by_name('bool'))
    assert lib.compile_blueprint(guard)
    events = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
    graph = events
    recover = graph.add_custom_event_node('B_RecoverPosture')
    restored = graph.add_set_member_variable_node('CurrentPosture')
    link(get('MaxPosture'), lib.find_input_pin(restored, 'CurrentPosture'))
    link(lib.find_then_pin(recover), lib.find_execute_pin(restored))
    clear = graph.add_set_member_variable_node('bB_Stunned')
    set_default(clear, 'bB_Stunned', 'false')
    link(lib.find_then_pin(restored), lib.find_execute_pin(clear))

    graph = u.BlueprintGraphEditor.create_and_edit_function_graph(guard, 'B_ApplyPostureDamage')
    damage = graph.add_graph_input_parameter('Amount', lib.get_basic_type_by_name('real'))
    subtract = call('KismetMathLibrary.Subtract_DoubleDouble')
    link(get('CurrentPosture'), lib.find_input_pin(subtract, 'A'))
    link(damage, lib.find_input_pin(subtract, 'B'))
    update = graph.add_set_member_variable_node('CurrentPosture')
    link(lib.find_result_pin(subtract), lib.find_input_pin(update, 'CurrentPosture'))
    link(graph.find_graph_entry_pin(), lib.find_execute_pin(update))
    broken = call('KismetMathLibrary.LessEqual_DoubleDouble')
    link(lib.find_output_pin(update, 'Output_Get'), lib.find_input_pin(broken, 'A'))
    gate = graph.add_branch_node()
    link(lib.find_then_pin(update), lib.find_execute_pin(gate))
    link(lib.find_result_pin(broken), lib.find_condition_pin(gate))
    stunned = graph.add_set_member_variable_node('bB_Stunned')
    set_default(stunned, 'bB_Stunned', 'true')
    link(lib.find_then_pin(gate), lib.find_execute_pin(stunned))
    stop = call('Controller.StopMovement')
    controller = lib.find_result_pin(call('Pawn.GetController'))
    link(controller, lib.find_self_pin(stop))
    link(lib.find_then_pin(stunned), lib.find_execute_pin(stop))
    timer = call('KismetSystemLibrary.K2_SetTimer')
    set_default(timer, 'FunctionName', 'B_RecoverPosture')
    set_default(timer, 'Time', '1.8')
    link(lib.find_then_pin(stop), lib.find_execute_pin(timer))
    assert lib.compile_blueprint(guard)

    graph = events
    nodes = {node.get_name(): node for node in graph.list_all_nodes()}
    add_stun_gate(lib.find_condition_pin(nodes['K2Node_IfThenElse_8']), inverted=True)
    add_stun_gate(lib.find_condition_pin(nodes['K2Node_IfThenElse_6']), inverted=True)
    tick = nodes['K2Node_Event_2']
    tick_pin, = lib.find_then_pin(tick).list_connected_pins()
    tick_gate = tick_pin.get_owning_node()
    assert isinstance(tick_gate, u.K2Node_IfThenElse)
    add_stun_gate(lib.find_condition_pin(tick_gate))

    native_damage = next(n for n in graph.list_all_nodes()
                         if isinstance(n, u.K2Node_Event) and 'AnyDamage' in str(lib.get_node_title(n)))
    next_step, = lib.find_then_pin(native_damage).list_connected_pins()
    post = graph.add_call_function_node(path + '.BP_GuardBase_C.B_ApplyPostureDamage')
    assert post
    link(lib.find_output_pin(native_damage, 'Damage'), lib.find_input_pin(post, 'Amount'))
    link(lib.find_then_pin(native_damage), lib.find_execute_pin(post))
    link(lib.find_then_pin(post), next_step)

    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(guard, 'ApplyTemporalFreeze'))
    entry = next(n for n in graph.list_all_nodes() if isinstance(n, u.K2Node_FunctionEntry))
    cut_posture = graph.add_call_function_node(path + '.BP_GuardBase_C.B_ApplyPostureDamage')
    assert cut_posture
    link(lib.find_output_pin(entry, 'PostureDamage'), lib.find_input_pin(cut_posture, 'Amount'))
    timer = next(n for n in graph.list_all_nodes()
                 if 'settimer' in str(lib.get_node_title(n)).replace(' ', '').lower())
    result, = lib.find_then_pin(timer).list_connected_pins()
    link(lib.find_then_pin(timer), lib.find_execute_pin(cut_posture))
    link(lib.find_then_pin(cut_posture), result)
    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
print('B_GUARD_STUN_SAVED')
