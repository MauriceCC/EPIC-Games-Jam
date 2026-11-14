"""Provide Jack's escape entry point and configure waypoints in L_Test_B."""
import unreal as u

assets = u.EditorAssetLibrary
lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/'
jack_class = root + 'Enemies/Jack/BP_Jack'
jack = u.load_asset(jack_class)
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(jack))


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


if not any('B_StartEscape' in str(lib.get_node_title(n)) for n in graph.list_all_nodes()):
    start = graph.add_custom_event_node('B_StartEscape')
    done = graph.add_get_member_variable_node('bReachedRefuge')
    gate = graph.add_branch_node()
    link(lib.find_then_pin(start), lib.find_execute_pin(gate))
    link(lib.find_output_pin(done, 'bReachedRefuge'), lib.find_condition_pin(gate))
    found = graph.add_set_member_variable_node('bJackFound')
    escape = graph.add_set_member_variable_node('bEscaping')
    assert lib.find_input_pin(found, 'bJackFound').set_pin_value('true')
    assert lib.find_input_pin(escape, 'bEscaping').set_pin_value('true')
    link(lib.find_output_pin(gate, 'else'), lib.find_execute_pin(found))
    link(lib.find_then_pin(found), lib.find_execute_pin(escape))
    assert lib.compile_blueprint(jack)
    assert assets.save_loaded_asset(jack)

pawn = u.load_asset(root + 'Enemies/Test/BP_TestPlayer_B')
test = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(pawn))
if not any(str(lib.find_input_pin(n, 'FunctionName').get_pin_value()) == 'B_StartEscape'
           for n in test.list_all_nodes() if 'settimer' in str(lib.get_node_title(n)).replace(' ', '').lower()):
    # [PROPUESTA] E starts this test route when the player is close to Jack.
    key = test.create_node_from_name(
        'Entrada|DebugEvents|KeyboardEvents|DebugKeyE', u.Vector2D(0, 750), [])
    assert key
    find = test.add_call_function_node('/Script/Engine.GameplayStatics.GetActorOfClass')
    assert lib.find_input_pin(find, 'ActorClass').set_pin_value(jack_class + '.BP_Jack_C')
    target = lib.find_result_pin(find)
    distance = test.add_call_function_node('/Script/Engine.Actor.GetDistanceTo')
    link(target, lib.find_input_pin(distance, 'OtherActor'))
    close = test.add_call_function_node('/Script/Engine.KismetMathLibrary.Less_DoubleDouble')
    link(lib.find_result_pin(distance), lib.find_input_pin(close, 'A'))
    assert lib.find_input_pin(close, 'B').set_pin_value('240.0')
    gate = test.add_branch_node()
    link(lib.find_output_pin(key, 'Pressed'), lib.find_execute_pin(find))
    link(lib.find_then_pin(find), lib.find_execute_pin(gate))
    link(lib.find_result_pin(close), lib.find_condition_pin(gate))
    timer = test.add_call_function_node('/Script/Engine.KismetSystemLibrary.K2_SetTimer')
    link(target, lib.find_input_pin(timer, 'Object'))
    assert lib.find_input_pin(timer, 'FunctionName').set_pin_value('B_StartEscape')
    assert lib.find_input_pin(timer, 'Time').set_pin_value('0.01')
    link(lib.find_then_pin(gate), lib.find_execute_pin(timer))
    assert lib.compile_blueprint(pawn)
    assert assets.save_loaded_asset(pawn)
else:
    find = next(n for n in test.list_all_nodes()
                if 'getactorofclass' in str(lib.get_node_title(n)).replace(' ', '').lower()
                and 'BP_Jack' in str(lib.find_input_pin(n, 'ActorClass').get_pin_value()))
    if not lib.find_execute_pin(find).list_connected_pins():
        key = next(n for n in test.list_all_nodes()
                   if lib.find_output_pin(n, 'Pressed').is_valid()
                   and n.get_node_pos().y > 500)
        pressed = lib.find_output_pin(key, 'Pressed')
        downstream, = pressed.list_connected_pins()
        link(pressed, lib.find_execute_pin(find))
        link(lib.find_then_pin(find), downstream)
        assert lib.compile_blueprint(pawn)
        assert assets.save_loaded_asset(pawn)

levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert levels.load_level(root + 'Maps/Test/L_Test_B')
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
placed = next(a for a in actors.get_all_level_actors() if a.get_class().get_name() == 'BP_Jack_C')
placed.modify()
assert placed.set_actor_rotation(u.Rotator(yaw=-45), False)
placed.set_editor_property('Waypoints', [
    u.Vector(450, -330, 0), u.Vector(620, -460, 0), u.Vector(770, -560, 0),
])
assert levels.save_current_level()
print('B_JACK_ESCAPE_SAVED')
