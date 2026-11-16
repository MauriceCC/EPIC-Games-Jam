"""Keep Workshop Jack within escort distance and at a walkable pace."""
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
dep = Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo/'Scripts/C'),str(dep)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
jack = h.asset('Enemies/Jack/BP_Jack')
name = 'B_CheckEscortDistance'
if not h.edit(jack,name):
    h.variable(jack,'bB_WaitingForEscort',h.basic('bool'),False,category='Jack')
    h.compile_blueprint(jack,warnings_as_errors=True)
    g = h.function(jack,name,outputs=[('Ready',h.basic('bool'))])
    player = h.call(g,'/Script/Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
    have,absent = h.branch(g,g.find_graph_entry_pin(),h.is_valid(g,player))
    radius = h.call(g,'/Script/Engine.KismetMathLibrary:SelectFloat',
                    A=300.0,B=460.0,bPickA=h.get(g,'bB_WaitingForEscort')).find_result_pin()
    distance = h.call(g,'/Script/Engine.Actor:GetDistanceTo',OtherActor=player).find_result_pin()
    close,far = h.branch(g,have,h.math(g,'LessEqual_DoubleDouble',distance,radius))
    resume = h.setvar(g,close,'bB_WaitingForEscort',False)
    h.result(g,resume,Ready=True)

    waiting = g.add_set_member_variable_node('bB_WaitingForEscort')
    h.literal(waiting.find_input_pin('bB_WaitingForEscort'),True)
    h.connect(absent,waiting.find_execute_pin())
    h.connect(far,waiting.find_execute_pin())
    controller = h.call(g,'/Script/Engine.Pawn:GetController').find_result_pin()
    valid,missing = h.branch(g,waiting.find_then_pin(),h.is_valid(g,controller))
    stop = h.call(g,'/Script/Engine.Controller:StopMovement',start=valid,target=controller)
    denied = h.result(g,stop.find_then_pin(),Ready=False)
    h.connect(missing,denied.find_execute_pin())
    h.compile_blueprint(jack,warnings_as_errors=True)

    g = h.edit(jack,'EventGraph')
    nodes = {node.get_name():node for node in g.list_all_nodes()}
    active = nodes['K2Node_IfThenElse_3'].find_then_pin()
    proceed, = active.list_connected_pins()
    assert proceed.get_owning_node().get_name()=='K2Node_IfThenElse_4'
    active.break_pin_links()
    escort = h.invoke(g,active,jack,name)
    yes,_ = h.branch(g,escort.find_then_pin(),escort.find_output_pin('Ready'))
    h.connect(yes,proceed)
    h.layout(jack,{name})

movement = u.get_default_object(jack.generated_class()).get_editor_property('character_movement')
movement.modify()
movement.set_editor_property('max_walk_speed',230.0)
h.save(jack)
u.log('B_JACK_ESCORT saved speed 230 cm/s; waits beyond 460 cm and resumes within 300 cm')
