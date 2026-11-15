"""Keep defeated guards out of combat, including attacks already winding up."""
import json
import unreal as u

lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/'
guard = u.load_asset(root + 'Enemies/BP_GuardBase')
health = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(guard, 'B_ApplyHealthDamage'))


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


if not any('CurrentAIState' in str(lib.get_node_title(n)) for n in health.list_all_nodes()):
    stop = next(n for n in health.list_all_nodes()
                if 'stopmovement' in str(lib.get_node_title(n)).replace(' ', '').lower())
    previous, = lib.find_execute_pin(stop).list_connected_pins()
    next_step, = lib.find_then_pin(stop).list_connected_pins()
    set_state = health.add_set_member_variable_node('CurrentAIState')
    enum = u.load_asset(root + 'Core/Enums/EEnemyAIState')
    pin_type = u.EdGraphPinType()
    pin_type.import_text('(PinCategory="byte",PinSubCategoryObject="' + enum.get_path_name() + '")')
    values = json.loads(lib.pin_type_to_json_schema(pin_type, u.Actor.static_class()))['enum']
    assert lib.find_input_pin(set_state, 'CurrentAIState').set_pin_value(
        'NewEnumerator' + str(values.index('Defeated')))
    controller, = lib.find_self_pin(stop).list_connected_pins()
    valid = health.add_call_function_node('/Script/Engine.KismetSystemLibrary.IsValid')
    link(controller, lib.find_input_pin(valid, 'Object'))
    branch = health.add_branch_node()
    link(previous, lib.find_execute_pin(set_state))
    link(lib.find_then_pin(set_state), lib.find_execute_pin(branch))
    link(lib.find_result_pin(valid), lib.find_condition_pin(branch))
    link(lib.find_then_pin(branch), lib.find_execute_pin(stop))
    link(lib.find_output_pin(branch, 'else'), next_step)

    events = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
    impact = next(n for n in events.list_all_nodes() if n.get_name() == 'K2Node_IfThenElse_8')
    condition = lib.find_condition_pin(impact)
    eligible, = condition.list_connected_pins()
    get_health = events.add_get_member_variable_node('B_Health')
    alive = events.add_call_function_node('/Script/Engine.KismetMathLibrary.Greater_DoubleDouble')
    link(lib.find_output_pin(get_health, 'B_Health'), lib.find_input_pin(alive, 'A'))
    both = events.add_call_function_node('/Script/Engine.KismetMathLibrary.BooleanAND')
    link(eligible, lib.find_input_pin(both, 'A'))
    link(lib.find_result_pin(alive), lib.find_input_pin(both, 'B'))
    link(lib.find_result_pin(both), condition)

    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
print('B_GUARD_DEFEAT_STATE_SAVED')
