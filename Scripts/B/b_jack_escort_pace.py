"""Match Jack's escort sprint to the player's current movement speed."""
import csv
from pathlib import Path
import sys
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
runtime = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(runtime)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
with (repo / 'SourceData/B/DT_EnemyBalance.csv').open(newline='', encoding='utf-8') as data:
    speeds = next(row for row in csv.DictReader(data) if row['Name'] == 'Jack')
walk, run = float(speeds['WalkSpeed']), float(speeds['RunSpeed'])
assert run > walk > 0

jack = h.asset('Enemies/Jack/BP_Jack')
name = 'B_ApplyEscortPace'
pace = h.edit(jack, name)
if pace is None:
    pace = h.function(jack, name, inputs=(('InDanger', h.basic('bool')),))
else:
    h.clear_body(pace)
target = h.get(pace, 'CharacterMovement')
movement_class = u.CharacterMovementComponent.static_class()
in_danger, safe = h.branch(pace, pace.find_graph_entry_pin(), h.param(pace, 'InDanger'))
player = h.call(pace, '/Script/Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
has_player, missing = h.branch(pace, in_danger, h.is_valid(pace, player))
player_movement = h.call(pace, '/Script/Engine.Pawn:GetMovementComponent', target=player).find_result_pin()
player_speed = h.call(pace, '/Script/Engine.MovementComponent:GetMaxSpeed', target=player_movement).find_result_pin()
sprint = h.math(pace, 'Multiply_DoubleDouble', player_speed, 0.97)
h.setvar(pace, has_player, 'MaxWalkSpeed', sprint, target=target, cls=movement_class)
normal = h.setvar(pace, safe, 'MaxWalkSpeed', walk, target=target, cls=movement_class)
h.connect(missing, normal.get_owning_node().find_execute_pin())
h.layout(jack, {name})
assert u.BlueprintEditorLibrary.compile_blueprint(jack)


def insert_pace(graph, source, in_danger=None):
    successor, = source.list_connected_pins()
    if str(successor.get_owning_node().get_node_title()) == name:
        return
    if in_danger is None:
        in_danger = h.is_valid(graph, h.get(graph, 'B_ClosestEscortThreat'))
    source.break_pin_links()
    change = h.invoke(graph, source, jack, name, InDanger=in_danger)
    h.connect(change.find_then_pin(), successor)


movement = h.edit(jack, 'B_UpdateEscortMovement')
scan = next(node for node in movement.list_all_nodes() if str(node.get_node_title()) == 'B_FindEscortThreat')
insert_pace(movement, scan.find_then_pin())

events = h.edit(jack, 'EventGraph')
arrived = next(node for node in events.list_all_nodes() if node.get_name() == 'K2Node_VariableSet_2')
assert 'bReachedRefuge' in str(arrived.get_node_title())
insert_pace(events, arrived.find_then_pin(), False)
h.save(jack)
u.log(f'B_JACK_ESCORT_PACE_SAVED walk={walk:g}, danger pace=97% of player max speed')
