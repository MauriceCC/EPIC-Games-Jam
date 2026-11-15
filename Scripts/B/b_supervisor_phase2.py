"""Make the Supervisor follow his low-health displacement with a faster pulse."""
import sys
from pathlib import Path
import unreal as u

repo=Path(u.Paths.project_dir()).resolve().parent
dep=Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0]=[str(repo/'Scripts/C'),str(dep)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
boss=h.asset('Enemies/BP_GuardBase')
name='B_SupervisorIsInSecondPhase'
if not h.edit(boss,name):
    g=h.function(boss,name,outputs=[('Result',h.basic('bool'))])
    life=h.get(g,'B_Health')
    initial=h.get(g,'B_CheckpointHealth')
    half=h.math(g,'LessEqual_IntInt',h.math(g,'Multiply_IntInt',life,2),initial)
    valid=h.all_true(g,half,h.math(g,'Greater_IntInt',life,0))
    h.result(g,g.find_graph_entry_pin(),Result=valid)
    h.compile_blueprint(boss,warnings_as_errors=True)

g=h.edit(boss,'B_UpdateSupervisorSpecial')
deadline=next(node for node in g.list_all_nodes()
              if isinstance(node,u.K2Node_VariableSet) and node.find_input_pin('B_SupervisorAbilityAt').is_valid())
base_time,=deadline.find_input_pin('B_SupervisorAbilityAt').list_connected_pins()
total=base_time.get_owning_node()
before,=deadline.find_execute_pin().list_connected_pins()
if name in str(before.get_owning_node().get_node_title()):
    low=before.get_owning_node()
else:
    before.break_pin_links()
    low=h.invoke(g,before,boss,name)
    h.connect(low.find_then_pin(),deadline.find_execute_pin())
    delay=h.call(g,'/Script/Engine.KismetMathLibrary:SelectFloat',A=2.8,B=4.0,
                 bPickA=low.find_result_pin()).find_result_pin()
    h.connect(delay,total.find_input_pin('B'))

move,=[n for n in g.list_all_nodes() if 'Set Actor Location' in str(n.get_node_title())]
flash_pin,=move.find_then_pin().list_connected_pins()
flash=flash_pin.get_owning_node()
assert 'SpawnSystemAtLocation' in str(flash.get_node_title()).replace(' ','')
if not flash.find_then_pin().list_connected_pins():
    now=h.call(g,'/Script/Engine.GameplayStatics:GetTimeSeconds').find_result_pin()
    valid_move=h.all_true(g,low.find_result_pin(),move.find_output_pin('ReturnValue'))
    follow,_=h.branch(g,flash.find_then_pin(),valid_move)
    h.setvar(g,follow,'B_SupervisorAbilityAt',h.math(g,'Add_DoubleDouble',now,1.15))
h.layout(boss,{name,'B_UpdateSupervisorSpecial'})
h.save(boss)
u.log('B_SUPERVISOR_PHASE2 saved half-health pulse cadence and displacement follow-up')
