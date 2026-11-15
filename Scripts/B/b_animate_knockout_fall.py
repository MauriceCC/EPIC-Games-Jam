"""Animate the mesh falling whenever guard health reaches zero."""
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
runtime = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(runtime)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
guard = h.asset('Enemies/BP_GuardBase')
events = h.edit(guard, 'EventGraph')
event_name = 'B_PlayKnockoutFall'
if not any(event_name in str(n.get_node_title()) for n in events.list_all_nodes()):
    event = events.add_custom_event_node(event_name)
    mesh = h.get(events, 'Mesh')
    lean = h.call(events, '/Script/Engine.KismetMathLibrary:MakeRotator', Pitch=87.0).find_result_pin()
    rotation = h.call(events, '/Script/Engine.KismetMathLibrary:ComposeRotators',
                      A=h.get(events, 'B_StaggerRestRotation'), B=lean).find_result_pin()
    location = h.get(events, 'RelativeLocation', target=mesh, cls=u.SceneComponent.static_class())
    move = h.call(events, '/Script/Engine.KismetSystemLibrary:MoveComponentTo',
                  Component=mesh, TargetRelativeLocation=location, TargetRelativeRotation=rotation,
                  bEaseIn=True, bEaseOut=True, OverTime=0.32, bForceShortestRotationPath=True)
    h.connect(event.find_then_pin(), move.find_input_pin('Move'))
    h.compile_blueprint(guard, warnings_as_errors=True)

g = h.edit(guard, 'B_ApplyHealthDamage')
nodes = g.list_all_nodes()
write, = (n for n in nodes if isinstance(n, u.K2Node_VariableSet) and n.find_input_pin('B_Health').is_valid())
health = write.find_input_pin('B_Health')
if not any('Max' in str(pin.get_owning_node().get_node_title()) for pin in health.list_connected_pins()):
    remaining, = health.list_connected_pins()
    h.connect(h.math(g, 'Max', remaining, 0), health)
if not any(event_name in str(n.get_node_title()) for n in nodes):
    down, = [n for n in nodes if 'Set Relative Rotation' in str(n.get_node_title())]
    previous, = down.find_execute_pin().list_connected_pins()
    pause, = down.find_then_pin().list_connected_pins()
    g.remove_nodes([down])
    fall = h.invoke(g, previous, guard, event_name)
    h.connect(fall.find_then_pin(), pause)
h.save(guard)
u.log('B_KNOCKOUT_FALL saved 0.32 second fall and clamped health')
