"""Report the same nonlethal outcome for normal hits and finishers."""
import json
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
runtime = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(runtime)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
guard = h.asset('Enemies/BP_GuardBase')
g = h.edit(guard, 'B_ApplyHealthDamage')
nodes = g.list_all_nodes()
if not any('ReportStoryEvent' in str(n.get_node_title()).replace(' ', '') for n in nodes):
    fall, = [n for n in nodes if 'B_PlayKnockoutFall' in str(n.get_node_title())]
    start = fall.find_then_pin()
    resume, = start.list_connected_pins()
    start.break_pin_links()
    state = h.call(g, '/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
    yes, no = h.branch(g, start, h.is_valid(g, state))
    report = h.message(g, yes, 'ReportStoryEvent', state, Source=h.self_pin(g), Param='NonLethal')
    event = report.find_input_pin('Event')
    names = json.loads(event.get_pin_type_as_json_schema())['enum']
    h.literal(event, 'NewEnumerator' + str(names.index('EnemyNeutralized')))
    h.connect(report.find_then_pin(), resume)
    h.connect(no, resume)
    h.save(guard)

adapter = h.asset('Enemies/BP_GuardFinisher')
g = h.edit(adapter, 'ExecuteInteraction')
nodes = g.list_all_nodes()
report = [n for n in nodes if 'ReportStoryEvent' in str(n.get_node_title()).replace(' ', '')]
if report:
    apply, = [n for n in nodes if 'B_ApplyHealthDamage' in str(n.get_node_title())]
    check, = apply.find_then_pin().list_connected_pins()
    branch = check.get_owning_node()
    valid, = branch.find_input_pin('Condition').list_connected_pins()
    predicate = valid.get_owning_node()
    state, = predicate.find_input_pin('Object').list_connected_pins()
    g.remove_nodes([branch, predicate, state.get_owning_node(), *report])
    h.save(adapter)
u.log('B_KNOCKOUT_EVENT saved one common EnemyNeutralized report')
