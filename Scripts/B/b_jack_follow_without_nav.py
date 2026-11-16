"""Allow Workshop Jack to follow a visible escort while navigation loads."""
from pathlib import Path
import sys

import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
runtime = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(runtime)]
import blueprint_helpers_c as h


def navigation_ready(graph, point):
    return h.call(
        graph, '/Script/NavigationSystem.NavigationSystemV1:K2_ProjectPointToNavigation',
        Point=point, QueryExtent='60,60,150',
    ).find_output_pin('ReturnValue')


def apply():
    worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not worlds.get_game_world(), 'Stop Play before editing Jack.'
    jack = h.asset('Enemies/Jack/BP_Jack')
    name = 'B_FollowVisibleEscortWithoutNav'
    if h.edit(jack, name):
        return

    graph = h.function(jack, name)
    enabled, _ = h.branch(graph, graph.find_graph_entry_pin(), h.get(graph, 'bEscaping'))
    position = h.call(graph, '/Script/Engine.Actor:K2_GetActorLocation').find_result_pin()
    _, loading = h.branch(graph, enabled, navigation_ready(graph, position))
    player = h.call(graph, '/Script/Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
    controller = h.call(graph, '/Script/Engine.Pawn:GetController').find_result_pin()
    ready, _ = h.branch(graph, loading, h.all_true(graph, h.is_valid(graph, player), h.is_valid(graph, controller)))

    destination = h.call(graph, '/Script/Engine.Actor:K2_GetActorLocation', target=player).find_result_pin()
    sight = h.call(graph, '/Script/Engine.Controller:LineOfSightTo', target=controller, Other=player).find_result_pin()
    distance = h.math(graph, 'Vector_Distance2D', position, destination)
    follow, _ = h.branch(graph, ready, h.all_true(
        graph, sight, h.math(graph, 'Greater_DoubleDouble', distance, 170.0),
    ))
    direction = h.call(
        graph, '/Script/Engine.KismetMathLibrary:GetDirectionUnitVector',
        From=position, To=destination,
    ).find_result_pin()

    # While navigation is unavailable, keep the visible player nearby unless
    # the direct route would bring Jack into a guard's immediate reach.
    threat = h.get(graph, 'B_ClosestEscortThreat')
    danger, clear = h.branch(graph, follow, h.is_valid(graph, threat))
    threat_position = h.call(graph, '/Script/Engine.Actor:K2_GetActorLocation', target=threat).find_result_pin()
    to_threat = h.math(graph, 'Subtract_VectorVector', threat_position, position)
    toward_threat = h.math(graph, 'Greater_DoubleDouble', h.math(graph, 'Dot_VectorVector', to_threat, direction), 0.0)
    nearby = h.math(graph, 'Less_DoubleDouble', h.math(graph, 'Vector_Distance2D', position, threat_position), 285.0)
    _, safe = h.branch(graph, danger, h.all_true(graph, toward_threat, nearby))
    step = h.call(graph, '/Script/Engine.Pawn:AddMovementInput', clear, WorldDirection=direction)
    h.connect(safe, step.find_execute_pin())
    h.compile_blueprint(jack, warnings_as_errors=True)

    events = h.edit(jack, 'EventGraph')
    story, = [node for node in events.list_all_nodes() if str(node.get_node_title()) == 'B_UpdateStoryEscape']
    branch = story.find_then_pin()
    next_step, = branch.list_connected_pins()
    branch.break_pin_links()
    follow = h.invoke(events, branch, jack, name)
    h.connect(follow.find_then_pin(), next_step)

    # Keep speed and threat scanning active. Avoid sending a navigation
    # request or StopMovement while the per-frame movement fallback runs.
    movement = h.edit(jack, 'B_UpdateEscortMovement')
    sync, = [node for node in movement.list_all_nodes() if str(node.get_node_title()) == 'B_SyncEscortSpeed']
    previous = sync.find_then_pin()
    next_step, = previous.list_connected_pins()
    previous.break_pin_links()
    position = h.call(movement, '/Script/Engine.Actor:K2_GetActorLocation').find_result_pin()
    use_nav, _ = h.branch(movement, previous, navigation_ready(movement, position))
    h.connect(use_nav, next_step)

    h.layout(jack, {name})
    h.save(jack)
    u.log('B_JACK_COLD_FOLLOW_SAVED')


apply()
