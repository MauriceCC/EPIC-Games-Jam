"""Move Jack through his configured waypoints after the escape is activated."""
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/'
jack = u.load_asset(root + 'Enemies/Jack/BP_Jack')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(jack))


def call(path, module='Engine'):
    node = graph.add_call_function_node('/Script/' + module + '.' + path)
    assert node, path
    return node


def link(source, target):
    assert source.is_valid() and target.is_valid()
    assert source.try_create_connection(target), target.get_pin_name()


def plug(node, name, source):
    link(source, lib.find_input_pin(node, name))


def get(name):
    return lib.find_output_pin(graph.add_get_member_variable_node(name), name)


def branch(source, condition):
    node = graph.add_branch_node()
    link(source, lib.find_execute_pin(node))
    link(condition, lib.find_condition_pin(node))
    return lib.find_then_pin(node), lib.find_output_pin(node, 'else')


def set_value(source, name, pin=None, value=None):
    node = graph.add_set_member_variable_node(name)
    if pin:
        plug(node, name, pin)
    else:
        assert lib.find_input_pin(node, name).set_pin_value(value), name
    link(source, lib.find_execute_pin(node))
    return lib.find_then_pin(node)


if not any('B_UpdateJackRoute' in str(lib.get_node_title(n)) for n in graph.list_all_nodes()):
    update = graph.add_custom_event_node('B_UpdateJackRoute')
    route = get('Waypoints')
    index = get('CurrentWaypointIndex')
    length = call('KismetArrayLibrary.Array_Length')
    plug(length, 'TargetArray', route)
    less = call('KismetMathLibrary.Less_IntInt')
    plug(less, 'A', index)
    plug(less, 'B', lib.find_result_pin(length))
    active, _ = branch(lib.find_then_pin(update), get('bEscaping'))
    advance, finished = branch(active, lib.find_result_pin(less))

    item = call('KismetArrayLibrary.Array_Get')
    plug(item, 'TargetArray', route)
    plug(item, 'Index', index)
    point = lib.find_output_pin(item, 'Item')
    distance = call('KismetMathLibrary.Vector_Distance2D')
    plug(distance, 'V1', lib.find_result_pin(call('Actor.K2_GetActorLocation')))
    plug(distance, 'V2', point)
    near = call('KismetMathLibrary.Less_DoubleDouble')
    plug(near, 'A', lib.find_result_pin(distance))
    assert lib.find_input_pin(near, 'B').set_pin_value('65.0')
    arrived, travel = branch(advance, lib.find_result_pin(near))

    next_index = call('KismetMathLibrary.Add_IntInt')
    plug(next_index, 'A', index)
    assert lib.find_input_pin(next_index, 'B').set_pin_value('1')
    set_value(arrived, 'CurrentWaypointIndex', pin=lib.find_result_pin(next_index))

    move = call('AIBlueprintHelperLibrary.SimpleMoveToLocation', module='AIModule')
    controller = lib.find_result_pin(call('Pawn.GetController'))
    plug(move, 'Controller', controller)
    plug(move, 'Goal', point)
    link(travel, lib.find_execute_pin(move))

    stop = call('Controller.StopMovement')
    link(controller, lib.find_self_pin(stop))
    link(set_value(set_value(finished, 'bEscaping', value='false'),
                   'bReachedRefuge', value='true'), lib.find_execute_pin(stop))

    assert lib.compile_blueprint(jack)
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(jack))
    tick = next(n for n in graph.list_all_nodes()
                if isinstance(n, u.K2Node_Event) and 'Tick' in str(lib.get_node_title(n)))
    previous, = lib.find_then_pin(tick).list_connected_pins()
    route_tick = graph.add_call_function_node(
        root + 'Enemies/Jack/BP_Jack.BP_Jack_C.B_UpdateJackRoute')
    assert route_tick
    ready, inactive = branch(lib.find_then_pin(tick), get('bEscaping'))
    # Preserve the prior test behavior for maps with no configured escape.
    has_route = call('KismetArrayLibrary.Array_Length')
    plug(has_route, 'TargetArray', get('Waypoints'))
    configured = call('KismetMathLibrary.Greater_IntInt')
    plug(configured, 'A', lib.find_result_pin(has_route))
    _, no_route = branch(inactive, lib.find_result_pin(configured))
    link(no_route, previous)
    delay = call('KismetSystemLibrary.Delay')
    assert lib.find_input_pin(delay, 'Duration').set_pin_value('0.25')
    link(ready, lib.find_execute_pin(delay))
    link(lib.find_then_pin(delay), lib.find_execute_pin(route_tick))

    assert lib.compile_blueprint(jack)
    assert assets.save_loaded_asset(jack)
print('B_JACK_ROUTE_SAVED')
