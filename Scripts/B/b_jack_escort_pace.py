"""Sync Jack's movement limit with the player for the entire active escort."""
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
    walk = float(next(row for row in csv.DictReader(data) if row['Name'] == 'Jack')['WalkSpeed'])

jack = h.asset('Enemies/Jack/BP_Jack')
name = 'B_SyncEscortSpeed'
old_name = 'B_ApplyEscortPace'
pace = h.edit(jack, name)
if pace is None:
    pace = h.function(jack, name)
else:
    h.clear_body(pace)

target = h.get(pace, 'CharacterMovement')
movement_class = u.CharacterMovementComponent.static_class()
active, idle = h.branch(pace, pace.find_graph_entry_pin(), h.get(pace, 'bEscaping'))
player = h.call(pace, '/Script/Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
has_player, missing = h.branch(pace, active, h.is_valid(pace, player))
player_movement = h.call(pace, '/Script/Engine.Pawn:GetMovementComponent', target=player).find_result_pin()
has_movement, no_movement = h.branch(pace, has_player, h.is_valid(pace, player_movement))
player_speed = h.call(pace, '/Script/Engine.MovementComponent:GetMaxSpeed', target=player_movement).find_result_pin()
h.setvar(pace, has_movement, 'MaxWalkSpeed', player_speed, target=target, cls=movement_class)
normal = h.setvar(pace, idle, 'MaxWalkSpeed', walk, target=target, cls=movement_class)
h.connect(missing, normal.get_owning_node().find_execute_pin())
h.connect(no_movement, normal.get_owning_node().find_execute_pin())
h.layout(jack, {name})
h.compile_blueprint(jack, warnings_as_errors=True)


def insert_pace(graph, source):
    successor, = source.list_connected_pins()
    old_call = successor.get_owning_node()
    title = str(old_call.get_node_title())
    if title == name:
        return
    if title == old_name:
        successor, = old_call.find_then_pin().list_connected_pins()
        graph.remove_nodes([old_call])
    else:
        source.break_pin_links()
    change = h.invoke(graph, source, jack, name)
    h.connect(change.find_then_pin(), successor)


movement = h.edit(jack, 'B_UpdateEscortMovement')
scan = next(node for node in movement.list_all_nodes() if str(node.get_node_title()) == 'B_FindEscortThreat')
insert_pace(movement, scan.find_then_pin())

events = h.edit(jack, 'EventGraph')
arrived = next(node for node in events.list_all_nodes() if node.get_name() == 'K2Node_VariableSet_2')
assert 'bReachedRefuge' in str(arrived.get_node_title())
insert_pace(events, arrived.find_then_pin())

old_pace = h.edit(jack, old_name)
if old_pace:
    u.BlueprintEditorLibrary.remove_graph(jack, old_pace.get_graph())
h.save(jack)
u.log(f'B_JACK_ESCORT_PACE_SAVED fallback={walk:g}; escort matches player max speed')
