"""Use Jack's run speed only while the escort detects a nearby guard."""
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
speed = h.call(pace, '/Script/Engine.KismetMathLibrary:SelectFloat',
               A=run, B=walk, bPickA=h.param(pace, 'InDanger')).find_result_pin()
h.setvar(pace, pace.find_graph_entry_pin(), 'MaxWalkSpeed', speed, target=target,
         cls=u.CharacterMovementComponent.static_class())
h.layout(jack, {name})
assert u.BlueprintEditorLibrary.compile_blueprint(jack)


def insert_pace(graph, source, in_danger):
    successor, = source.list_connected_pins()
    if str(successor.get_owning_node().get_node_title()) == name:
        return
    source.break_pin_links()
    change = h.invoke(graph, source, jack, name, InDanger=in_danger)
    h.connect(change.find_then_pin(), successor)


movement = h.edit(jack, 'B_UpdateEscortMovement')
scan = next(node for node in movement.list_all_nodes() if str(node.get_node_title()) == 'B_FindEscortThreat')
threat = h.get(movement, 'B_ClosestEscortThreat')
insert_pace(movement, scan.find_then_pin(), h.is_valid(movement, threat))

events = h.edit(jack, 'EventGraph')
arrived = next(node for node in events.list_all_nodes() if node.get_name() == 'K2Node_VariableSet_2')
assert 'bReachedRefuge' in str(arrived.get_node_title())
insert_pace(events, arrived.find_then_pin(), False)
h.save(jack)
u.log(f'B_JACK_ESCORT_PACE_SAVED walk={walk:g} run={run:g}')
