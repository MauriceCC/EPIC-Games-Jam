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
events = h.edit(jack, 'EventGraph')
nodes = {n.get_name(): n for n in events.list_all_nodes()}


def set_waypoint_arrival_radius():
    # Leave room for both capsules when the player waits on the marker.
    radius = nodes['K2Node_CallFunction_34']
    h.literal(radius.find_input_pin('Value'), 125.0)


move_to_waypoint = nodes.get('K2Node_CallFunction_21')

for name, kind, default in (
    (threat_name, h.obj_type(u.Actor), ''),
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


scan = rebuild(scan_name)
start = h.setvar(scan, scan.find_graph_entry_pin(), threat_name, None)
start = h.setvar(scan, start, range_name, 460.0)
guards = call(scan, 'Engine.GameplayStatics:GetAllActorsOfClass', start,
              ActorClass=guard.generated_class().get_path_name())
item, actor, _ = h.foreach(scan, guards.find_then_pin(), guards.find_output_pin('OutActors'))
guard_pos = position(scan, actor)
player = call(scan, 'Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
gap = h.math(scan, 'Min', distance(scan, position(scan), guard_pos),
             distance(scan, position(scan, player), guard_pos))
near, _ = h.branch(scan, item, h.math(scan, 'Less_DoubleDouble', gap, h.get(scan, range_name)))
cast, enemy, _ = h.cast(scan, near, actor, guard.generated_class())
alive = h.invoke(scan, cast, guard, 'IsDefeated', target=enemy)
active = h.invoke(scan, alive.find_then_pin(), guard, 'B_CanRunEncounter', target=enemy)
danger, _ = h.branch(scan, active.find_then_pin(),
                    h.all_true(scan, h.not_(scan, alive.find_result_pin()), active.find_result_pin()))
changed = h.setvar(scan, danger, threat_name, actor)
h.setvar(scan, changed, range_name, gap)
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
    return h.math(g, 'Add_VectorVector', player_pos, offset(direction, 225.0))


def retreat(start, candidate):
    nav = call(g, 'NavigationSystem.NavigationSystemV1:K2_ProjectPointToNavigation',
               Point=candidate, QueryExtent='80,80,180')
    reachable, blocked = h.branch(g, start, nav.find_output_pin('ReturnValue'))
    goal = nav.find_output_pin('ProjectedLocation')
    player_gap = distance(g, goal, player_pos)
    farther = h.math(g, 'Greater_DoubleDouble', distance(g, goal, enemy_pos),
                     h.math(g, 'Add_DoubleDouble', enemy_gap, 25.0))
    outside_player = h.math(g, 'GreaterEqual_DoubleDouble', player_gap, 115.0)
    in_leash = h.math(g, 'LessEqual_DoubleDouble', player_gap, 280.0)
    accepted, rejected = h.branch(g, reachable, h.all_true(g, farther, outside_player, in_leash))
    move(g, accepted, controller, goal)
    return blocked, rejected


# Step away from the guard first, then try the far side of the player.
# Never make the player the movement goal while a threat is active.
away_from_enemy = h.math(g, 'Subtract_VectorVector', jack_pos, enemy_pos)
step = h.math(g, 'Add_VectorVector', jack_pos, offset(away_from_enemy, 255.0))
step_side = h.math(g, 'Subtract_VectorVector', step, player_pos)
blocked, rejected = retreat(flee, player_side(step_side))
far_side = player_side(h.math(g, 'Subtract_VectorVector', player_pos, enemy_pos))
secondary_start = g.add_branch_node()
h.literal(secondary_start.find_input_pin('Condition'), True)
h.connect(blocked, secondary_start.find_execute_pin())
h.connect(rejected, secondary_start.find_execute_pin())
blocked, rejected = retreat(secondary_start.find_then_pin(), far_side)
stop = call(g, 'Engine.Controller:StopMovement', blocked, controller)
h.connect(rejected, stop.find_execute_pin())
waypoint = h.param(g, 'Waypoint')
near_player = h.math(g, 'LessEqual_DoubleDouble', distance(g, waypoint, player_pos), 310.0)
route, stay_near = h.branch(g, safe, h.all_true(g, near_player, h.not_(g, h.param(g, 'WaypointBlocked'))))
move(g, route, controller, waypoint)

needs_follow = h.math(g, 'Greater_DoubleDouble', distance(g, jack_pos, player_pos), 170.0)
follow, stay = h.branch(g, stay_near, needs_follow)
call(g, 'AIModule.AIBlueprintHelperLibrary:SimpleMoveToActor', follow, Controller=controller, Goal=player)
call(g, 'Engine.Controller:StopMovement', stay, controller)
h.layout(jack, {scan_name, update_name})
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
