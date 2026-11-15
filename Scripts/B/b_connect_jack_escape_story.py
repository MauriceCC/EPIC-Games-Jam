"""Start Jack's configured escape in ProtectJack and report arrival once."""
import json
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
runtime = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(runtime)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
jack = h.asset('Enemies/Jack/BP_Jack')
start_name = 'B_UpdateStoryEscape'
if h.edit(jack, start_name):
    raise RuntimeError('Jack story escape is already installed.')

g = h.function(jack, start_name)
waypoints = h.get(g, 'Waypoints')
count = h.call(g, '/Script/Engine.KismetArrayLibrary:Array_Length', TargetArray=waypoints).find_result_pin()
ready = h.all_true(g, h.get(g, 'bJackFound'), h.not_(g, h.get(g, 'bEscaping')),
                   h.not_(g, h.get(g, 'bReachedRefuge')), h.math(g, 'Greater_IntInt', count, 0))
candidate, _ = h.branch(g, g.find_graph_entry_pin(), ready)
state = h.call(g, '/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
valid, _ = h.branch(g, candidate, h.is_valid(g, state))
phase = h.message(g, valid, 'GetCurrentPhase', state)
phase_pin = phase.find_result_pin()
phase_names = json.loads(phase_pin.get_pin_type_as_json_schema())['enum']
action = next(name for name in h.actions(g, [phase_pin])
              if name.endswith(('|Igual(enumerador)', '|Equal(Enum)')))
comparison = g.create_node_from_name(action, u.Vector2D(), [phase_pin])
h.connect(phase_pin, comparison.find_input_pin('A'))
h.literal(comparison.find_input_pin('B'), 'NewEnumerator' + str(phase_names.index('ProtectJack')))
protect, _ = h.branch(g, phase.find_then_pin(), comparison.find_result_pin())
h.invoke(g, protect, jack, 'B_StartEscape')
h.compile_blueprint(jack, warnings_as_errors=True)

g = h.edit(jack, 'EventGraph')
nodes = {n.get_name(): n for n in g.list_all_nodes()}
tick = nodes['K2Node_Event_2'].find_then_pin()
old_path, = tick.list_connected_pins()
tick.break_pin_links()
update = h.invoke(g, tick, jack, start_name)
h.connect(update.find_then_pin(), old_path)

# Keep the waypoint increment explicit to survive reconstruction of the
# old promotable arithmetic node when opening this asset in another editor.
one = h.call(g, '/Script/Engine.KismetSystemLibrary:MakeLiteralInt', Value=1).find_result_pin()
h.connect(one, nodes['K2Node_PromotableOperator_4'].find_input_pin('B'))
radius = h.call(g, '/Script/Engine.KismetSystemLibrary:MakeLiteralDouble', Value=105.0).find_result_pin()
h.connect(radius, nodes['K2Node_PromotableOperator_3'].find_input_pin('B'))

stop = nodes['K2Node_CallFunction_23']
assert 'StopMovement' in str(stop.get_node_title())
state = h.call(g, '/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
valid, _ = h.branch(g, stop.find_then_pin(), h.is_valid(g, state))
arrived = h.message(g, valid, 'ReportStoryEvent', state, Source=h.self_pin(g), Param='Refuge')
event = arrived.find_input_pin('Event')
events = json.loads(event.get_pin_type_as_json_schema())['enum']
h.literal(event, 'NewEnumerator' + str(events.index('JackReachedRefuge')))
h.layout(jack, {start_name})
h.save(jack)
u.log('B_JACK_ESCAPE story phase gate, waypoint progression, and arrival saved')
