"""Implement B's health and posture reaction using the shared hit payload."""
import json
import unreal as u

lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/'
guard_path = root + 'Enemies/BP_GuardBase'
guard = u.load_asset(guard_path)
guard_class = guard_path + '.BP_GuardBase_C'


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


if not lib.find_graph(guard, 'B_ReceiveCombatHit'):
    graph = u.BlueprintGraphEditor.create_and_edit_function_graph(guard, 'B_ReceiveCombatHit')
    hit_type = lib.get_struct_type(u.load_asset(root + 'Core/Structs/ST_HitInfo'))
    incoming = graph.add_graph_input_parameter('HitInfo', hit_type)
    enum = u.load_asset(root + 'Core/Enums/EHitResult')
    result_type = u.EdGraphPinType()
    result_type.import_text('(PinCategory="byte",PinSubCategoryObject="' + enum.get_path_name() + '")')
    values = json.loads(lib.pin_type_to_json_schema(result_type, u.Actor.static_class()))['enum']
    read = graph.create_node_from_name('||BreakSTHitInfo', u.Vector2D(300, 400), [incoming])
    assert read
    source, = lib.list_input_pins(read)
    link(incoming, source)
    fields = {str(pin.get_pin_name()).split('_')[0]: pin for pin in lib.list_output_pins(read)}

    branch = graph.add_branch_node()
    link(graph.find_graph_entry_pin(), lib.find_execute_pin(branch))
    health = graph.add_get_member_variable_node('B_Health')
    alive = graph.add_call_function_node('/Script/Engine.KismetMathLibrary.Greater_DoubleDouble')
    link(lib.find_output_pin(health, 'B_Health'), lib.find_input_pin(alive, 'A'))
    link(lib.find_result_pin(alive), lib.find_condition_pin(branch))

    posture = graph.add_call_function_node(guard_class + '.B_ApplyPostureDamage')
    damage = graph.add_call_function_node(guard_class + '.B_ApplyHealthDamage')
    assert posture and damage
    link(fields['PostureDamage'], lib.find_input_pin(posture, 'Amount'))
    link(fields['Damage'], lib.find_input_pin(damage, 'Damage'))
    link(lib.find_then_pin(branch), lib.find_execute_pin(posture))
    link(lib.find_then_pin(posture), lib.find_execute_pin(damage))
    hit = graph.add_graph_output_parameter('Result', result_type)
    ignored = graph.add_return_node()
    for node, response, start in [
        (hit, 'Hit', lib.find_then_pin(damage)),
        (ignored, 'Ignored', lib.find_output_pin(branch, 'else')),
    ]:
        assert lib.find_input_pin(node, 'Result').set_pin_value('NewEnumerator' + str(values.index(response)))
        link(start, lib.find_execute_pin(node))

    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
print('B_RECEIVE_COMBAT_HIT_HELPER_SAVED')
