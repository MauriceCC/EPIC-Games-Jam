"""Follow the player during the Workshop escort and give active guards space."""
from pathlib import Path
import sys
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
runtime = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(runtime)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
jack = h.asset('Enemies/Jack/BP_Jack')
guard = h.asset('Enemies/BP_GuardBase')
lib = u.BlueprintEditorLibrary
threat_name = 'B_ClosestEscortThreat'
range_name = 'B_ClosestEscortThreatDistance'
update_name = 'B_UpdateEscortMovement'
scan_name = 'B_FindEscortThreat'
arrival_name = 'B_CheckRefugeArrival'
path_check_name = 'B_IsRetreatPathClear'
threats_name = 'B_EscortThreats'
unsafe_path_name = 'bB_UnsafeRetreatPath'
danger_detection_radius = 540.0
danger_follow_distance = 360.0
danger_min_distance = 260.0
danger_max_distance = 440.0
refuge_radius = 550.0
events = h.edit(jack, 'EventGraph')
nodes = {n.get_name(): n for n in events.list_all_nodes()}


def set_waypoint_arrival_radius():
    # Leave room for both capsules when the player waits on the marker.
    radius = nodes['K2Node_CallFunction_34']
    h.literal(radius.find_input_pin('Value'), 125.0)


move_to_waypoint = next((node for node in nodes.values()
                         if str(node.get_node_title()) == 'SimpleMoveToLocation'), None)

for name, kind, default in (
    (threat_name, h.obj_type(u.Actor), ''),
    (threats_name, h.array_type(h.obj_type(u.Actor)), ''),
    (unsafe_path_name, h.basic('bool'), False),
    (range_name, h.basic('real'), 0.0),
    ('B_NextEscortMoveAt', h.basic('real'), 0.0),
):
    h.variable(jack, name, kind, default, category='Jack')
assert lib.compile_blueprint(jack)


def call(graph, method, start=None, target=None, **args):
    return h.call(graph, '/Script/' + method, start, target, **args)


def position(graph, actor=None):
    return call(graph, 'Engine.Actor:K2_GetActorLocation', target=actor).find_result_pin()


def distance(graph, first, second):
    return h.math(graph, 'Vector_Distance2D', first, second)


def move(graph, start, controller, goal):
    return call(graph, 'AIModule.AIBlueprintHelperLibrary:SimpleMoveToLocation',
                start, Controller=controller, Goal=goal)

def rebuild(name, inputs=()):
    graph = h.edit(jack, name)
    if graph is None:
        return h.function(jack, name, inputs=inputs)
    h.clear_body(graph)
    return graph


arrival = h.edit(jack, arrival_name)
if arrival is None:
    arrival = h.function(jack, arrival_name, outputs=(('Arrived', h.basic('bool')),))
else:
    h.clear_body(arrival)
waypoints = h.get(arrival, 'Waypoints')
count = call(arrival, 'Engine.KismetArrayLibrary:Array_Length', TargetArray=waypoints).find_result_pin()
player = call(arrival, 'Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
has_route = h.math(arrival, 'Greater_IntInt', count, 0)
ready, no_route = h.branch(arrival, arrival.find_graph_entry_pin(),
                           h.all_true(arrival, has_route, h.is_valid(arrival, player)))
last_index = h.math(arrival, 'Subtract_IntInt', count, 1)
refuge = call(arrival, 'Engine.KismetArrayLibrary:Array_Get', TargetArray=waypoints,
              Index=last_index).find_output_pin('Item')
jack_arrived = h.math(arrival, 'LessEqual_DoubleDouble',
                      h.math(arrival, 'Vector_Distance', position(arrival), refuge), refuge_radius)
player_arrived = h.math(arrival, 'LessEqual_DoubleDouble',
                        h.math(arrival, 'Vector_Distance', position(arrival, player), refuge), refuge_radius)
together = h.math(arrival, 'LessEqual_DoubleDouble',
                  h.math(arrival, 'Vector_Distance', position(arrival), position(arrival, player)),
                  danger_max_distance)
arrived, not_there = h.branch(arrival, ready, h.all_true(arrival, jack_arrived, player_arrived, together))
transform = call(arrival, 'Engine.Actor:GetTransform').find_result_pin()
checkpoint = h.setvar(arrival, arrived, 'B_LastReachedTransform', transform)
advance = h.setvar(arrival, checkpoint, 'CurrentWaypointIndex', count)
h.result(arrival, advance, Arrived=True)
waiting = h.result(arrival, not_there, Arrived=False)
h.connect(no_route, waiting.find_execute_pin())

scan = rebuild(scan_name)
start = h.setvar(scan, scan.find_graph_entry_pin(), threat_name, None)
start = h.setvar(scan, start, range_name, danger_detection_radius)
clear = call(scan, 'Engine.KismetArrayLibrary:Array_Clear', start, TargetArray=h.get(scan, threats_name))
guards = call(scan, 'Engine.GameplayStatics:GetAllActorsOfClass', clear.find_then_pin(),
              ActorClass=guard.generated_class().get_path_name())
item, actor, _ = h.foreach(scan, guards.find_then_pin(), guards.find_output_pin('OutActors'))
guard_pos = position(scan, actor)
player = call(scan, 'Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
gap = h.math(scan, 'FMin', distance(scan, position(scan), guard_pos),
             distance(scan, position(scan, player), guard_pos))
near, _ = h.branch(scan, item, h.math(scan, 'Less_DoubleDouble', gap, danger_detection_radius))
cast, enemy, _ = h.cast(scan, near, actor, guard.generated_class())
alive = h.invoke(scan, cast, guard, 'IsDefeated', target=enemy)
active = h.invoke(scan, alive.find_then_pin(), guard, 'B_CanRunEncounter', target=enemy)
danger, _ = h.branch(scan, active.find_then_pin(),
                    h.all_true(scan, h.not_(scan, alive.find_result_pin()), active.find_result_pin()))
record = call(scan, 'Engine.KismetArrayLibrary:Array_Add', danger,
              TargetArray=h.get(scan, threats_name), NewItem=actor)
nearest, _ = h.branch(scan, record.find_then_pin(),
                      h.math(scan, 'Less_DoubleDouble', gap, h.get(scan, range_name)))
changed = h.setvar(scan, nearest, threat_name, actor)
h.setvar(scan, changed, range_name, gap)

path_check = h.edit(jack, path_check_name)
if path_check is None:
    path_check = h.function(jack, path_check_name,
        inputs=(('Path', h.obj_type(u.NavigationPath)),), outputs=(('Clear', h.basic('bool')),))
else:
    h.clear_body(path_check)
path_points = h.get(path_check, 'PathPoints', target=h.param(path_check, 'Path'),
                    cls=u.NavigationPath.static_class())
start = h.setvar(path_check, path_check.find_graph_entry_pin(), unsafe_path_name, False)
segment, endpoint, done = h.foreach(path_check, start, path_points)
point_index = segment.get_owning_node().find_output_pin('Array Index')
check_segment, _ = h.branch(path_check, segment, h.all_true(path_check,
    h.math(path_check, 'Greater_IntInt', point_index, 0), h.not_(path_check, h.get(path_check, unsafe_path_name))))
prior = call(path_check, 'Engine.KismetArrayLibrary:Array_Get', TargetArray=path_points,
             Index=h.math(path_check, 'Subtract_IntInt', point_index, 1)).find_output_pin('Item')
guard_step, guard_actor, _ = h.foreach(path_check, check_segment, h.get(path_check, threats_name))
enemy_position = position(path_check, guard_actor)
closest = call(path_check, 'Engine.KismetMathLibrary:FindClosestPointOnSegment',
               Point=enemy_position, SegmentStart=prior, SegmentEnd=endpoint).find_result_pin()
# Allow Jack to exit an enemy's immediate reach, while ruling out paths that
# move him even closer or that enter another nearby enemy's reach.
initial_clearance = distance(path_check, position(path_check), enemy_position)
minimum_clearance = h.math(path_check, 'FMin', h.math(path_check, 'Subtract_DoubleDouble',
                                                    initial_clearance, 12.0), 285.0)
unsafe, _ = h.branch(path_check, guard_step, h.math(path_check, 'Less_DoubleDouble',
                                        distance(path_check, closest, enemy_position), minimum_clearance))
h.setvar(path_check, unsafe, unsafe_path_name, True)
h.result(path_check, done, Clear=h.not_(path_check, h.get(path_check, unsafe_path_name)))
assert lib.compile_blueprint(jack)

waypoint_type = nodes['K2Node_CallFunction_31'].find_input_pin('SpherePos').get_pin_type()
g = rebuild(update_name, (('Waypoint', waypoint_type), ('WaypointBlocked', h.basic('bool'))))
player = call(g, 'Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
controller = call(g, 'Engine.Pawn:GetController').find_result_pin()
now = call(g, 'Engine.GameplayStatics:GetTimeSeconds').find_result_pin()
refresh, _ = h.branch(g, g.find_graph_entry_pin(), h.math(g, 'GreaterEqual_DoubleDouble',
                      now, h.get(g, 'B_NextEscortMoveAt')))
start = h.setvar(g, refresh, 'B_NextEscortMoveAt', h.math(g, 'Add_DoubleDouble', now, 0.25))
controlled, _ = h.branch(g, start, h.is_valid(g, controller))
valid, missing = h.branch(g, controlled, h.is_valid(g, player))
call(g, 'Engine.Controller:StopMovement', missing, controller)
updated = h.invoke(g, valid, jack, scan_name)

player_pos = position(g, player)
jack_pos = position(g)
threat = h.get(g, threat_name)
in_danger = h.is_valid(g, threat)
escort_start = updated.find_then_pin()
if h.edit(jack, 'B_ApplyEscortPace'):
    escort_start = h.invoke(g, escort_start, jack, 'B_ApplyEscortPace', InDanger=in_danger).find_then_pin()
flee, safe = h.branch(g, escort_start, in_danger)
enemy_pos = position(g, threat)
enemy_gap = distance(g, jack_pos, enemy_pos)


def offset(direction, length):
    away = call(g, 'Engine.KismetMathLibrary:Normal2D', A=direction).find_result_pin()
    radius = call(g, 'Engine.KismetSystemLibrary:MakeLiteralDouble', Value=length).find_result_pin()
    return h.math(g, 'Multiply_VectorFloat', away, radius)


def player_side(direction):
    return h.math(g, 'Add_VectorVector', player_pos, offset(direction, danger_follow_distance))


def retreat(entries, candidate):
    nav = call(g, 'NavigationSystem.NavigationSystemV1:K2_ProjectPointToNavigation',
               Point=candidate, QueryExtent='80,80,180')
    reachable, blocked = h.branch(g, entries[0], nav.find_output_pin('ReturnValue'))
    for entry in entries[1:]:
        h.connect(entry, reachable.get_owning_node().find_execute_pin())
    goal = nav.find_output_pin('ProjectedLocation')
    player_gap = distance(g, goal, player_pos)
    goal_clearance = distance(g, goal, enemy_pos)
    farther = h.math(g, 'Greater_DoubleDouble', goal_clearance,
                     h.math(g, 'Add_DoubleDouble', enemy_gap, 25.0))
    current_player_gap = distance(g, jack_pos, player_pos)
    outside_band = h.any_true(g, h.math(g, 'Less_DoubleDouble', current_player_gap, danger_min_distance),
                              h.math(g, 'Greater_DoubleDouble', current_player_gap, danger_max_distance))
    safe_regroup = h.all_true(g, outside_band, h.math(g, 'GreaterEqual_DoubleDouble', goal_clearance, 350.0))
    outside_player = h.math(g, 'GreaterEqual_DoubleDouble', player_gap, danger_min_distance)
    in_leash = h.math(g, 'LessEqual_DoubleDouble', player_gap, danger_max_distance)
    accepted, rejected = h.branch(g, reachable,
        h.all_true(g, h.any_true(g, farther, safe_regroup), outside_player, in_leash))
    path = call(g, 'NavigationSystem.NavigationSystemV1:FindPathToLocationSynchronously',
                accepted, PathStart=jack_pos, PathEnd=goal, PathfindingContext=controller)
    path_result = path.find_result_pin()
    found, failed = h.branch(g, path.find_then_pin(), h.is_valid(g, path_result))
    valid = call(g, 'NavigationSystem.NavigationPath:IsValid', target=path_result).find_result_pin()
    partial = call(g, 'NavigationSystem.NavigationPath:IsPartial', target=path_result).find_result_pin()
    complete, incomplete = h.branch(g, found, h.all_true(g, valid, h.not_(g, partial)))
    inspected = h.invoke(g, complete, jack, path_check_name, Path=path_result)
    clear_path, unsafe_path = h.branch(g, inspected.find_then_pin(), inspected.find_output_pin('Clear'))
    move(g, clear_path, controller, goal)
    return blocked, rejected, failed, incomplete, unsafe_path


# Try the direct escape, the far side of the player and a route to either side.
away_from_enemy = h.math(g, 'Subtract_VectorVector', jack_pos, enemy_pos)
step = h.math(g, 'Add_VectorVector', jack_pos, offset(away_from_enemy, 255.0))
step_side = h.math(g, 'Subtract_VectorVector', step, player_pos)
far_side = h.math(g, 'Subtract_VectorVector', player_pos, enemy_pos)
left = h.math(g, 'RotateAngleAxis', far_side, 55.0, '0,0,1')
right = h.math(g, 'RotateAngleAxis', far_side, -55.0, '0,0,1')
unresolved = (flee,)
for direction in (step_side, far_side, left, right):
    unresolved = retreat(unresolved, player_side(direction))
stop = call(g, 'Engine.Controller:StopMovement', unresolved[0], controller)
for entry in unresolved[1:]:
    h.connect(entry, stop.find_execute_pin())
waypoint = h.param(g, 'Waypoint')
near_player = h.math(g, 'LessEqual_DoubleDouble', distance(g, waypoint, player_pos), 310.0)
route, stay_near = h.branch(g, safe, h.all_true(g, near_player, h.not_(g, h.param(g, 'WaypointBlocked'))))
move(g, route, controller, waypoint)

needs_follow = h.math(g, 'Greater_DoubleDouble', distance(g, jack_pos, player_pos), 170.0)
follow, stay = h.branch(g, stay_near, needs_follow)
follow_side = h.math(g, 'Subtract_VectorVector', jack_pos, player_pos)
follow_goal = h.math(g, 'Add_VectorVector', player_pos, offset(follow_side, 125.0))
follow_nav = call(g, 'NavigationSystem.NavigationSystemV1:K2_ProjectPointToNavigation',
                  Point=follow_goal, QueryExtent='80,80,180')
off_player, direct = h.branch(g, follow, follow_nav.find_output_pin('ReturnValue'))
move(g, off_player, controller, follow_nav.find_output_pin('ProjectedLocation'))
call(g, 'AIModule.AIBlueprintHelperLibrary:SimpleMoveToActor', direct, Controller=controller, Goal=player)
call(g, 'Engine.Controller:StopMovement', stay, controller)
h.layout(jack, {scan_name, update_name, arrival_name, path_check_name})
assert lib.compile_blueprint(jack)

events = h.edit(jack, 'EventGraph')
nodes = {n.get_name(): n for n in events.list_all_nodes()}
if move_to_waypoint is not None:
    waypoint_value, = move_to_waypoint.find_input_pin('Goal').list_connected_pins()
    blocker = nodes['K2Node_CallFunction_31']
    h.invoke(events, blocker.find_then_pin(), jack, update_name, Waypoint=waypoint_value,
             WaypointBlocked=blocker.find_output_pin('ReturnValue'))
    events.remove_nodes([move_to_waypoint, nodes['K2Node_IfThenElse_10'], nodes['K2Node_CallFunction_32']])
    escaping = nodes['K2Node_IfThenElse_3'].find_then_pin()
    old_gate, = escaping.list_connected_pins()
    old_check = old_gate.get_owning_node()
    assert 'B_CheckEscortDistance' in str(old_check.get_node_title())
    old_branch, = old_check.find_then_pin().list_connected_pins()
    events.remove_nodes([old_check, old_branch.get_owning_node()])
    h.connect(escaping, nodes['K2Node_IfThenElse_4'].find_execute_pin())

escaping = nodes['K2Node_IfThenElse_3'].find_then_pin()
next_step, = escaping.list_connected_pins()
if str(next_step.get_owning_node().get_node_title()) != arrival_name:
    escaping.break_pin_links()
    arrival_check = h.invoke(events, escaping, jack, arrival_name)
    finish, continue_route = h.branch(events, arrival_check.find_then_pin(), arrival_check.find_output_pin('Arrived'))
    h.connect(finish, nodes['K2Node_VariableSet_1'].find_execute_pin())
    h.connect(continue_route, next_step)

# Finishing the waypoint list alone should wait for the player at the refuge.
end_of_route = nodes['K2Node_IfThenElse_4'].find_output_pin('else')
if any(pin.get_owning_node().get_name() == 'K2Node_VariableSet_1'
       for pin in end_of_route.list_connected_pins()):
    end_of_route.break_pin_links()
    escort_controller = call(events, 'Engine.Pawn:GetController').find_result_pin()
    controlled, _ = h.branch(events, end_of_route, h.is_valid(events, escort_controller))
    call(events, 'Engine.Controller:StopMovement', controlled, escort_controller)

begin = nodes['K2Node_Event_0'].find_then_pin()
after_begin, = begin.list_connected_pins()
channel = after_begin.get_owning_node().find_input_pin('Channel')
if not channel.is_valid() or str(channel.get_pin_value()) != 'ECC_Pawn':
    begin.break_pin_links()
    capsule = h.get(events, 'CapsuleComponent')
    passthrough = call(events, 'Engine.PrimitiveComponent:SetCollisionResponseToChannel', begin,
                       capsule, Channel='ECC_Pawn', NewResponse='ECR_Ignore')
    h.connect(passthrough.find_then_pin(), after_begin)
set_waypoint_arrival_radius()
h.save(jack)
u.log('B_JACK_PLAYER_FOLLOW_SAVED')
