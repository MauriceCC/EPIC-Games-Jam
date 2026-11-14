"""Give the Interventor a slower charged attack and light-hit blocking."""
import json
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/Enemies/'
guard = u.load_asset(root + 'BP_GuardBase')


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def get(name):
    return lib.find_output_pin(graph.add_get_member_variable_node(name), name)


def both(first, second):
    node = call('KismetMathLibrary.BooleanAND')
    link(first, lib.find_input_pin(node, 'A'))
    link(second, lib.find_input_pin(node, 'B'))
    return lib.find_result_pin(node)


if 'bB_BlocksLight' not in {str(n) for n in lib.list_member_variable_names(guard)}:
    assert lib.add_member_variable(guard, 'bB_BlocksLight', lib.get_basic_type_by_name('bool'))
    assert lib.add_member_variable(guard, 'B_WindupSeconds', lib.get_basic_type_by_name('real'))
    assert lib.compile_blueprint(guard)
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
    delay = next(n for n in graph.list_all_nodes() if n.get_name() == 'K2Node_CallFunction_4')
    assert 'Delay' in str(lib.get_node_title(delay))
    link(get('B_WindupSeconds'), lib.find_input_pin(delay, 'Duration'))

    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(guard, 'B_ReceiveCombatHit'))
    original = next(n for n in graph.list_all_nodes() if isinstance(n, u.K2Node_IfThenElse))
    yes = lib.find_then_pin(original)
    remaining, = yes.list_connected_pins()
    read = next(n for n in graph.list_all_nodes() if n.get_class().get_name() == 'K2Node_BreakStruct')
    kind = next(pin for pin in lib.list_output_pins(read)
                if str(pin.get_pin_name()).startswith('AttackType'))
    kinds = json.loads(kind.get_pin_type_as_json_schema())['enum']
    assert kinds[:3] == ['Light1', 'Light2', 'Light3'], kinds
    light = call('KismetMathLibrary.LessEqual_ByteByte')
    link(kind, lib.find_input_pin(light, 'A'))
    assert lib.find_input_pin(light, 'B').set_pin_value('2')
    steady = call('KismetMathLibrary.Not_PreBool')
    link(get('bB_Stunned'), lib.find_input_pin(steady, 'A'))
    blocks = both(get('bB_BlocksLight'), both(lib.find_result_pin(light), lib.find_result_pin(steady)))
    gate = graph.add_branch_node()
    link(yes, lib.find_execute_pin(gate))
    link(blocks, lib.find_condition_pin(gate))
    link(lib.find_output_pin(gate, 'else'), remaining)
    blocked = graph.add_return_node()
    result = lib.find_input_pin(blocked, 'Result')
    values = json.loads(result.get_pin_type_as_json_schema())['enum']
    assert result.set_pin_value('NewEnumerator' + str(values.index('Blocked')))
    link(lib.find_then_pin(gate), lib.find_execute_pin(blocked))
    assert lib.compile_blueprint(guard)

for name, duration, blocks in [
    ('BP_GuardBase', 0.45, False),
    ('BP_Interventor', 0.85, True),
    ('BP_Supervisor', 0.55, False),
]:
    bp = u.load_asset(root + name)
    defaults = u.get_default_object(bp.generated_class())
    defaults.set_editor_property('B_WindupSeconds', duration)
    defaults.set_editor_property('bB_BlocksLight', blocks)
    assert assets.save_loaded_asset(bp)
print('B_ENEMY_ARCHETYPES_SAVED')
