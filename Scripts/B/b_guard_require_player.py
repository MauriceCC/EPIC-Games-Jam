"""Gate guard perception before evaluating any pawn-dependent expressions."""
import unreal as u

lib = u.BlueprintEditorLibrary
guard = u.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))


def link(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


def call(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


tick, = [
    node for node in graph.list_all_nodes()
    if isinstance(node, u.K2Node_Event) and 'Tick' in str(lib.get_node_title(node))
]
start = lib.find_then_pin(tick)
previous, = start.list_connected_pins()
previous_node = previous.get_owning_node()

# The previous branch checks StealthComponent, whose target already reads the pawn.
# A separate execution guard prevents Blueprint from evaluating that pure chain.
condition, = lib.find_condition_pin(previous_node).list_connected_pins()
validation = condition.get_owning_node()
target, = lib.find_input_pin(validation, 'Object').list_connected_pins()
if 'GetPlayerCharacter' not in str(lib.get_node_title(target.get_owning_node())):
    player = call('GameplayStatics.GetPlayerCharacter')
    is_valid = call('KismetSystemLibrary.IsValid')
    link(lib.find_result_pin(player), lib.find_input_pin(is_valid, 'Object'))
    ready = graph.add_branch_node()
    link(lib.find_result_pin(is_valid), lib.find_condition_pin(ready))
    link(start, lib.find_execute_pin(ready))
    link(lib.find_then_pin(ready), previous)
    assert lib.compile_blueprint(guard), 'Could not compile BP_GuardBase.'
    assert u.EditorAssetLibrary.save_loaded_asset(guard), 'Could not save BP_GuardBase.'
u.log('B_GUARD_REQUIRE_PLAYER saved and compiled')
