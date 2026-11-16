"""Keep dodge movement grounded and gate repeated dodges before stamina is spent."""
import sys
from pathlib import Path

import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
toolset = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(toolset)]
import blueprint_helpers_c as h

ROLL_SECONDS = .55
RECOVERY_SECONDS = .50


def apply():
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    player = h.asset('Player/BP_PlayerCharacter')
    next_dodge = 'A_NextDodgeTime'
    if u.BlueprintEditorLibrary.get_member_variable_type(player, next_dodge) is not None:
        return
    h.variable(player, next_dodge, h.basic('real'), 0, category='Combat')
    h.compile_blueprint(player, warnings_as_errors=True)
    graph = h.edit(player, 'DoDodge')
    nodes = {node.get_name(): node for node in graph.list_all_nodes()}
    launch = nodes['K2Node_CallFunction_7']
    animation = nodes['K2Node_CallFunction_8']
    stamina = nodes['K2Node_CallFunction_10']
    assert str(launch.get_node_title()) == 'LaunchCharacter'
    assert str(animation.get_node_title()) == 'PlayOneShot'
    assert str(stamina.get_node_title()) == 'TryConsumeStamina'

    now = h.call(graph, '/Script/Engine.GameplayStatics:GetTimeSeconds').find_result_pin()
    stamina_in = stamina.find_execute_pin()
    ready_source, = stamina_in.list_connected_pins()
    stamina_in.break_pin_links()
    ready, _ = h.branch(
        graph, ready_source, h.math(graph, 'GreaterEqual_DoubleDouble', now, h.get(graph, next_dodge)),
    )
    h.connect(ready, stamina_in)

    start, = launch.find_execute_pin().list_connected_pins()
    desired, = launch.find_input_pin('LaunchVelocity').list_connected_pins()
    continuation, = launch.find_then_pin().list_connected_pins()
    graph.remove_nodes([launch])
    start = h.setvar(graph, start, next_dodge,
                     h.math(graph, 'Add_DoubleDouble', now, ROLL_SECONDS + RECOVERY_SECONDS))

    movement = h.get(graph, 'CharacterMovement')
    velocity = h.call(graph, '/Script/Engine.Actor:GetVelocity').find_result_pin()
    horizontal = h.math(graph, 'Multiply_VectorVector', velocity, '1,1,0')
    impulse = h.math(graph, 'Subtract_VectorVector', desired, horizontal)
    move = h.call(
        graph, '/Script/Engine.CharacterMovementComponent:AddImpulse', start,
        target=movement, Impulse=impulse, bVelocityChange=True,
    )
    h.connect(move.find_then_pin(), continuation)
    h.literal(animation.find_input_pin('Duration'), ROLL_SECONDS)
    h.save(player)
    u.log('A_ROLL_MOVEMENT_SAVED')


apply()
