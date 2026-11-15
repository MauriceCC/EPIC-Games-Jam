"""[PROPUESTA] Stop Jack when a guard blocks the next section of his escape."""
import unreal as u

lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/Enemies/'
jack = u.load_asset(root + 'Jack/BP_Jack')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(jack))


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


if not any('sphereoverlapactors' in str(lib.get_node_title(n)).replace(' ', '').lower()
           for n in graph.list_all_nodes()):
    type_probe = call('KismetSystemLibrary.SphereOverlapActors')
    object_types = lib.find_input_pin(type_probe, 'ObjectTypes').get_pin_type()
    graph.remove_nodes([type_probe])
    assert lib.add_member_variable(jack, 'B_BlockingObjectTypes', object_types)
    assert lib.compile_blueprint(jack)
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(jack))
    # Insert the obstruction check after the waypoint exists and before pathfinding.
    move = next(n for n in graph.list_all_nodes()
                if 'simplemovetolocation' in str(lib.get_node_title(n)).replace(' ', '').lower())
    move_in = lib.find_execute_pin(move)
    travel, = move_in.list_connected_pins()
    goal, = lib.find_input_pin(move, 'Goal').list_connected_pins()
    controller, = lib.find_input_pin(move, 'Controller').list_connected_pins()
    overlap = call('KismetSystemLibrary.SphereOverlapActors')
    link(goal, lib.find_input_pin(overlap, 'SpherePos'))
    assert lib.find_input_pin(overlap, 'SphereRadius').set_pin_value('240.0')
    assert lib.find_input_pin(overlap, 'ActorClassFilter').set_pin_value(
        root + 'BP_GuardBase.BP_GuardBase_C')

    types = graph.add_get_member_variable_node('B_BlockingObjectTypes')
    link(lib.find_output_pin(types, 'B_BlockingObjectTypes'),
         lib.find_input_pin(overlap, 'ObjectTypes'))

    decide = graph.add_branch_node()
    link(travel, lib.find_execute_pin(overlap))
    link(lib.find_then_pin(overlap), lib.find_execute_pin(decide))
    link(lib.find_output_pin(overlap, 'ReturnValue'), lib.find_condition_pin(decide))
    link(lib.find_output_pin(decide, 'else'), move_in)
    wait = call('Controller.StopMovement')
    link(controller, lib.find_self_pin(wait))
    link(lib.find_then_pin(decide), lib.find_execute_pin(wait))
    assert lib.compile_blueprint(jack)
    pawn_channel = next(getattr(u.ObjectTypeQuery, name) for name in dir(u.ObjectTypeQuery)
                        if name.replace('_', '').lower() == 'objecttypequery3')
    u.get_default_object(jack.generated_class()).set_editor_property(
        'B_BlockingObjectTypes', [pawn_channel])
    assert u.EditorAssetLibrary.save_loaded_asset(jack)
print('B_JACK_CLEARANCE_SAVED')
