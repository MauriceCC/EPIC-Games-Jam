"""Advance patrol waypoints after a half-second pause and walk between them."""
from pathlib import Path
import runpy

import unreal as u

lib = u.BlueprintEditorLibrary
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play before applying the patrol fix.'
guard = u.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))


def link(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


def call(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def source(pin):
    linked, = pin.list_connected_pins()
    return linked


def previous_node(node):
    return source(lib.find_execute_pin(node)).get_owning_node()


def is_speed_setter(node):
    return 'MaxWalkSpeed' in str(lib.get_node_title(node)).replace(' ', '')


def literal(function, value):
    node = call('KismetSystemLibrary.' + function)
    pin, = lib.list_input_pins(node)
    assert pin.set_pin_value(value)
    assert float(pin.get_pin_value()) == float(value), function
    return lib.find_result_pin(node)


nodes = graph.list_all_nodes()
patrol_move, = [
    node for node in nodes
    if 'SimpleMoveToLocation' in str(lib.get_node_title(node))
    and str(source(lib.find_input_pin(node, 'Goal')).get_pin_name()) == 'Item'
]
arrival = previous_node(patrol_move)
if is_speed_setter(arrival):
    arrival = previous_node(arrival)
arrived = lib.find_then_pin(arrival)
next_step = source(arrived).get_owning_node()
if 'Delay' in str(lib.get_node_title(next_step)):
    set_index = source(lib.find_then_pin(next_step)).get_owning_node()
else:
    set_index = next_step
    delay = call('KismetSystemLibrary.Delay')
    assert lib.find_input_pin(delay, 'Duration').set_pin_value('0.5')
    link(arrived, lib.find_execute_pin(delay))
    link(lib.find_then_pin(delay), lib.find_execute_pin(set_index))
assert 'CurrentWaypointIndex' in str(lib.get_node_title(set_index))
increment = source(lib.find_input_pin(set_index, 'CurrentWaypointIndex')).get_owning_node()
operand = lib.find_input_pin(increment, 'B')
if not operand.list_connected_pins():
    link(literal('MakeLiteralInt', '1'), operand)
# Only read member state after Delay. The route array returned by the impure
# function belongs to the earlier execution and is unnecessary for incrementing.
index_input = lib.find_input_pin(increment, 'A')
if str(source(index_input).get_pin_name()) != 'CurrentWaypointIndex':
    index = graph.add_get_member_variable_node('CurrentWaypointIndex')
    link(lib.find_output_pin(index, 'CurrentWaypointIndex'), index_input)


def configure_speed(move, speed):
    execute = lib.find_execute_pin(move)
    before = source(execute)
    if is_speed_setter(before.get_owning_node()):
        setter = before.get_owning_node()
    else:
        movement = graph.add_get_member_variable_node('CharacterMovement')
        component = lib.find_output_pin(movement, 'CharacterMovement')
        setter = graph.add_set_member_variable_node(
            'MaxWalkSpeed', '/Script/Engine.CharacterMovementComponent')
        assert setter
        link(component, lib.find_self_pin(setter))
        link(before, lib.find_execute_pin(setter))
        link(lib.find_then_pin(setter), execute)
    speed_pin = lib.find_input_pin(setter, 'MaxWalkSpeed')
    if not speed_pin.list_connected_pins():
        link(literal('MakeLiteralFloat', str(speed)), speed_pin)


configure_speed(patrol_move, 180.0)
for node in nodes:
    if 'SimpleMoveToActor' in str(lib.get_node_title(node)):
        configure_speed(node, 600.0)

assert lib.compile_blueprint(guard), 'Could not compile BP_GuardBase.'
assert u.EditorAssetLibrary.save_loaded_asset(guard), 'Could not save BP_GuardBase.'
u.log('B_PATROL_LOOP saved 0.5-second stop, waypoint increment and patrol walk speed')
runpy.run_path(str(Path(__file__).with_name('b_diagnose_plaza_pie.py')), run_name='__main__')
