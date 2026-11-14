"""Limit simultaneous melee windups to two guards in the active world."""
import unreal as u

lib = u.BlueprintEditorLibrary
guard = u.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
nodes = {node.get_name(): node for node in graph.list_all_nodes()}


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def input_(node, name):
    return lib.find_input_pin(node, name)


def call(name):
    node = graph.add_call_function_node('/Script/Engine.' + name)
    assert node, name
    return node


if not any('getallactorswithtag' in str(lib.get_node_title(n)).replace(' ', '').lower()
           for n in nodes.values()):
    windup = nodes['K2Node_VariableSet_9']
    impact = nodes['K2Node_IfThenElse_8']
    entry, = lib.find_execute_pin(windup).list_connected_pins()
    delayed, = lib.find_execute_pin(impact).list_connected_pins()

    tags = graph.add_get_member_variable_node('Tags')
    own_tags = lib.find_output_pin(tags, 'Tags')
    assert own_tags.is_valid()
    tag = 'B.MeleeWindup'
    active = call('GameplayStatics.GetAllActorsWithTag')
    assert input_(active, 'Tag').set_pin_value(tag)
    length = call('KismetArrayLibrary.Array_Length')
    link(lib.find_output_pin(active, 'OutActors'), input_(length, 'TargetArray'))
    limit = call('KismetMathLibrary.Less_IntInt')
    link(lib.find_result_pin(length), input_(limit, 'A'))
    assert input_(limit, 'B').set_pin_value('2')
    permit = graph.add_branch_node()
    link(entry, lib.find_execute_pin(active))
    link(lib.find_then_pin(active), lib.find_execute_pin(permit))
    link(lib.find_result_pin(limit), lib.find_condition_pin(permit))

    claim = call('KismetArrayLibrary.Array_AddUnique')
    link(own_tags, input_(claim, 'TargetArray'))
    assert input_(claim, 'NewItem').set_pin_value(tag)
    link(lib.find_then_pin(permit), lib.find_execute_pin(claim))
    link(lib.find_then_pin(claim), lib.find_execute_pin(windup))

    release = call('KismetArrayLibrary.Array_RemoveItem')
    link(own_tags, input_(release, 'TargetArray'))
    assert input_(release, 'Item').set_pin_value(tag)
    link(delayed, lib.find_execute_pin(release))
    link(lib.find_then_pin(release), lib.find_execute_pin(impact))
    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
print('B_ATTACK_TURNS_SAVED')
