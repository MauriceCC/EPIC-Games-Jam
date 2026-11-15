"""Make guard patrols cycle through the editable points on BP_PatrolRoute."""
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/'
route_path = root + 'Enemies/BP_PatrolRoute'
route_bp = u.load_asset(route_path)
guard = u.load_asset(root + 'Enemies/BP_GuardBase')


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path, module='Engine'):
    node = graph.add_call_function_node('/Script/' + module + '.' + path)
    assert node, path
    return node


def plug(node, name, source):
    link(source, lib.find_input_pin(node, name))


def get(name):
    return lib.find_output_pin(graph.add_get_member_variable_node(name), name)


def branch(source, condition):
    node = graph.add_branch_node()
    link(source, lib.find_execute_pin(node))
    link(condition, lib.find_condition_pin(node))
    return lib.find_then_pin(node), lib.find_output_pin(node, 'else')


if not lib.find_graph(route_bp, 'B_GetPatrolPoints'):
    graph = u.BlueprintGraphEditor.create_and_edit_function_graph(route_bp, 'B_GetPatrolPoints')
    vector_array = lib.get_array_type(lib.get_struct_type(u.Vector.static_struct()))
    result = graph.add_graph_output_parameter('Points', vector_array)
    plug(result, 'Points', get('Waypoints'))
    link(graph.find_graph_entry_pin(), lib.find_execute_pin(result))
    assert lib.compile_blueprint(route_bp)
    assert assets.save_loaded_asset(route_bp)

graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
if not any('B_UpdatePatrol' in str(lib.get_node_title(n)) for n in graph.list_all_nodes()):
    event = graph.add_custom_event_node('B_UpdatePatrol')
    route = get('PatrolRoute')
    valid = call('KismetSystemLibrary.IsValid')
    plug(valid, 'Object', route)
    ready, _ = branch(lib.find_then_pin(event), lib.find_result_pin(valid))
    points = graph.add_call_function_node(route_path + '.BP_PatrolRoute_C.B_GetPatrolPoints')
    assert points
    link(route, lib.find_self_pin(points))
    link(ready, lib.find_execute_pin(points))
    array = lib.find_output_pin(points, 'Points')
    count = call('KismetArrayLibrary.Array_Length')
    plug(count, 'TargetArray', array)
    available = call('KismetMathLibrary.Greater_IntInt')
    plug(available, 'A', lib.find_result_pin(count))
    walk, _ = branch(lib.find_then_pin(points), lib.find_result_pin(available))
    index = get('CurrentWaypointIndex')
    wrap = call('KismetMathLibrary.Percent_IntInt')
    plug(wrap, 'A', index)
    plug(wrap, 'B', lib.find_result_pin(count))
    item = call('KismetArrayLibrary.Array_Get')
    plug(item, 'Index', lib.find_result_pin(wrap))
    plug(item, 'TargetArray', array)
    goal = lib.find_output_pin(item, 'Item')
    distance = call('KismetMathLibrary.Vector_Distance2D')
    plug(distance, 'V1', lib.find_result_pin(call('Actor.K2_GetActorLocation')))
    plug(distance, 'V2', goal)
    near = call('KismetMathLibrary.Less_DoubleDouble')
    plug(near, 'A', lib.find_result_pin(distance))
    assert lib.find_input_pin(near, 'B').set_pin_value('75.0')
    arrived, travel = branch(walk, lib.find_result_pin(near))
    next_index = call('KismetMathLibrary.Add_IntInt')
    plug(next_index, 'A', lib.find_result_pin(wrap))
    new_index = graph.add_set_member_variable_node('CurrentWaypointIndex')
    plug(new_index, 'CurrentWaypointIndex', lib.find_result_pin(next_index))
    link(arrived, lib.find_execute_pin(new_index))
    move = call('AIBlueprintHelperLibrary.SimpleMoveToLocation', module='AIModule')
    plug(move, 'Controller', lib.find_result_pin(call('Pawn.GetController')))
    plug(move, 'Goal', goal)
    link(travel, lib.find_execute_pin(move))
    assert lib.compile_blueprint(guard)

    nodes = {node.get_name(): node for node in graph.list_all_nodes()}
    prior = [nodes[f'K2Node_CallFunction_{i}'] for i in (20, 33, 44)]
    for move in prior:
        assert 'SimpleMoveToActor' in str(lib.get_node_title(move))
        source, = lib.find_execute_pin(move).list_connected_pins()
        update = graph.add_call_function_node(
            root + 'Enemies/BP_GuardBase.BP_GuardBase_C.B_UpdatePatrol')
        assert update
        link(source, lib.find_execute_pin(update))
    graph.remove_nodes(prior)
    assert lib.compile_blueprint(guard)
    assert assets.save_loaded_asset(guard)

levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
for relative in ('Maps/Test/L_Test_B', 'Maps/L_Whitechapel_AI'):
    assert levels.load_level(root + relative), relative
    current = actors.get_all_level_actors()
    for route in (a for a in current if a.get_class().get_name() == 'BP_PatrolRoute_C'):
        if not route.get_editor_property('Waypoints'):
            origin = route.get_actor_location()
            route.modify()
            route.set_editor_property('Waypoints', [
                origin + u.Vector(-270, 160, -origin.z),
                origin + u.Vector(270, 160, -origin.z),
                origin + u.Vector(0, 420, -origin.z),
            ])
    assert levels.save_current_level(), relative
print('B_GUARD_PATROL_SAVED')
