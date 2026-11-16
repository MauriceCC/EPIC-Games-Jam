"""Keep guards pursuing their visible target while Whitechapel loads navigation."""
import json
from pathlib import Path
import sys

import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
toolset = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(toolset)]
import blueprint_helpers_c as h


def apply():
    worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not worlds.get_game_world(), 'Stop PIE before editing the guard Blueprint.'
    guard = h.asset('Enemies/BP_GuardBase')
    name = 'B_SimpleMoveToVisibleActor'
    if h.edit(guard, name):
        return

    events = h.edit(guard, 'EventGraph')
    chase_nodes = [
        node for node in events.list_all_nodes()
        if str(node.get_node_title()).replace(' ', '') == 'SimpleMoveToActor'
    ]
    assert len(chase_nodes) == 3, 'Expected the three authored guard chase paths.'
    chase_node_names = {node.get_name() for node in chase_nodes}

    chase = h.function(guard, name, inputs=(
        ('Controller', h.obj_type(u.Controller.static_class())),
        ('Goal', h.obj_type(u.Actor.static_class())),
    ))
    controller = h.param(chase, 'Controller')
    goal = h.param(chase, 'Goal')
    ready, _ = h.branch(
        chase, chase.find_graph_entry_pin(),
        h.all_true(chase, h.is_valid(chase, controller), h.is_valid(chase, goal)),
    )
    position = h.call(chase, '/Script/Engine.Actor:K2_GetActorLocation').find_result_pin()
    destination = h.call(chase, '/Script/Engine.Actor:K2_GetActorLocation', target=goal).find_result_pin()
    on_navmesh = h.call(
        chase, '/Script/NavigationSystem.NavigationSystemV1:K2_ProjectPointToNavigation',
        Point=position, QueryExtent='60,60,150',
    ).find_output_pin('ReturnValue')
    use_nav, direct = h.branch(chase, ready, on_navmesh)
    h.call(
        chase, '/Script/AIModule.AIBlueprintHelperLibrary:SimpleMoveToActor',
        use_nav, Controller=controller, Goal=goal,
    )

    # All callers already require the player's line of sight, confirmed detection
    # and pursuit range. CharacterMovement still sweeps the capsule against walls.
    direction = h.call(
        chase, '/Script/Engine.KismetMathLibrary:GetDirectionUnitVector',
        From=position, To=destination,
    ).find_result_pin()
    h.call(
        chase, '/Script/Engine.Pawn:AddMovementInput',
        direct, WorldDirection=direction, ScaleValue=1.0, bForce=False,
    )
    h.compile_blueprint(guard, warnings_as_errors=True)

    events = h.edit(guard, 'EventGraph')
    nodes = {node.get_name(): node for node in events.list_all_nodes()}
    chase_nodes = [node for key, node in nodes.items() if key in chase_node_names]
    # Restore the state written by the original chase and attack branches.
    for number, state in ((0, 'Combat'), (1, 'Chase'), (3, 'Combat'),
                          (4, 'Chase'), (6, 'Combat'), (7, 'Chase')):
        pin = nodes[f'K2Node_VariableSet_{number}'].find_input_pin('CurrentAIState')
        names = json.loads(pin.get_pin_type_as_json_schema())['enum']
        h.literal(pin, 'NewEnumerator' + str(names.index(state)))

    for move in chase_nodes:
        entry, = move.find_execute_pin().list_connected_pins()
        controller_pin, = move.find_input_pin('Controller').list_connected_pins()
        goal_pin, = move.find_input_pin('Goal').list_connected_pins()
        assert not move.find_then_pin().list_connected_pins(), 'Chase has downstream execution.'
        follow = h.invoke(events, entry, guard, name, Controller=controller_pin, Goal=goal_pin)
        follow.set_node_pos(move.get_node_pos())
    events.remove_nodes(chase_nodes)
    h.layout(guard, {name})
    h.save(guard)
    u.log('B_CHASE_FIXED: saved navigation fallback in BP_GuardBase')


apply()
