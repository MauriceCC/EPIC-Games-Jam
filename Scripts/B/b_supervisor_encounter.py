"""Add the Supervisor's circular pulse, navigable side-step, and story signals."""
import json
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
dep = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(dep)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
guard = h.asset('Enemies/BP_GuardBase')
player = h.asset('Player/BP_PlayerCharacter')
pulse = 'B_SupervisorPulse'
update = 'B_UpdateSupervisorSpecial'

for name,typ,value in [('bB_SupervisorStarted','bool',False),('bB_SupervisorBlinkNext','bool',False),
                       ('bB_SupervisorBusy','bool',False),('B_SupervisorAbilityAt','real',0.0)]:
    h.variable(guard,name,h.basic(typ),value,category='Supervisor')
h.compile_blueprint(guard,warnings_as_errors=True)

def report(g,flow,event,param):
    gs=h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
    yes,no=h.branch(g,flow,h.is_valid(g,gs))
    node=h.message(g,yes,'ReportStoryEvent',gs,Source=h.self_pin(g),Param=param)
    pin=node.find_input_pin('Event')
    names=json.loads(pin.get_pin_type_as_json_schema())['enum']
    h.literal(pin,'NewEnumerator'+str(names.index(event)))
    return node.find_then_pin(),no

def position(g,actor=None):
    return h.call(g,'/Script/Engine.Actor:K2_GetActorLocation',target=actor).find_result_pin()

def effect(g,flow,name,where,scale='1,1,1'):
    return h.call(g,'/Script/Niagara.NiagaraFunctionLibrary:SpawnSystemAtLocation',start=flow,
                  SystemTemplate='/Game/Unscripted/VFX/'+name+'.'+name,Location=where,Scale=scale).find_then_pin()

def ready(g):
    return h.all_true(g,h.math(g,'Greater_IntInt',h.get(g,'B_Health'),0),
                      h.not_(g,h.get(g,'bIsTemporalFrozen')),h.not_(g,h.get(g,'bB_Stunned')))

def nearby(g,pawn,max_distance):
    distance=h.call(g,'/Script/Engine.Actor:GetDistanceTo',OtherActor=pawn).find_result_pin()
    return h.math(g,'LessEqual_DoubleDouble',distance,max_distance)

g=h.edit(guard,'EventGraph')
if not any(pulse in str(n.get_node_title()) for n in g.list_all_nodes()):
    event=g.add_custom_event_node(pulse)
    stop=h.call(g,'/Script/Engine.Controller:StopMovement',start=event.find_then_pin(),
                target=h.call(g,'/Script/Engine.Pawn:GetController').find_result_pin())
    flash=effect(g,stop.find_then_pin(),'NS_EnemyTelegraph',position(g),'2,2,1')
    pause=h.call(g,'/Script/Engine.KismetSystemLibrary:Delay',start=flash,Duration=0.65)
    clear=h.setvar(g,pause.find_then_pin(),'bB_SupervisorBusy',False)
    valid,_=h.branch(g,clear,ready(g))
    pawn=h.call(g,'/Script/Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
    valid,_=h.branch(g,valid,h.is_valid(g,pawn))
    hit,_=h.branch(g,valid,nearby(g,pawn,280.0))
    typed,target,_=h.cast(g,hit,pawn,player.generated_class())
    h.invoke(g,typed,player,'TakeHit',target=target,Amount=20.0)
    h.compile_blueprint(guard,warnings_as_errors=True)

g=h.edit(guard,update) or h.function(guard,update)
h.clear_body(g)
available=h.invoke(g,g.find_graph_entry_pin(),guard,'B_CanRunEncounter')
pawn=h.call(g,'/Script/Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
active,_=h.branch(g,available.find_then_pin(),h.all_true(g,available.find_result_pin(),ready(g),h.is_valid(g,pawn)))
in_range,_=h.branch(g,active,nearby(g,pawn,470.0))
started, ongoing=h.branch(g,in_range,h.not_(g,h.get(g,'bB_SupervisorStarted')))
mark=h.setvar(g,started,'bB_SupervisorStarted',True)
reported,unavailable=report(g,mark,'SupervisorEncounterStarted','Archive')
time=h.call(g,'/Script/Engine.GameplayStatics:GetTimeSeconds').find_result_pin()
due=h.math(g,'GreaterEqual_DoubleDouble',time,h.get(g,'B_SupervisorAbilityAt'))
can=h.all_true(g,due,h.get(g,'bCanAttack'),h.not_(g,h.get(g,'bB_SupervisorBusy')))
start,_=h.branch(g,ongoing,can)
decision=start.get_owning_node()
for entry in (reported,unavailable):
    h.connect(entry,decision.find_execute_pin())
next_time=h.math(g,'Add_DoubleDouble',time,4.0)
start=h.setvar(g,start,'B_SupervisorAbilityAt',next_time)
blink,circular=h.branch(g,start,h.get(g,'bB_SupervisorBlinkNext'))
arm=h.setvar(g,circular,'bB_SupervisorBlinkNext',True)
arm=h.setvar(g,arm,'bB_SupervisorBusy',True)
h.invoke(g,arm,guard,pulse)
start=h.setvar(g,blink,'bB_SupervisorBlinkNext',False)
right=h.call(g,'/Script/Engine.Actor:GetActorRightVector').find_result_pin()
offset=h.call(g,'/Script/Engine.KismetMathLibrary:Multiply_VectorFloat',A=right,B=230.0).find_result_pin()
goal=h.call(g,'/Script/Engine.KismetMathLibrary:Add_VectorVector',A=position(g),B=offset).find_result_pin()
nav=h.call(g,'/Script/NavigationSystem.NavigationSystemV1:K2_ProjectPointToNavigation',Point=goal)
allowed,_=h.branch(g,start,nav.find_output_pin('ReturnValue'))
from_fx=effect(g,allowed,'NS_TemporalCut',position(g))
height=h.call(g,'/Script/Engine.CapsuleComponent:GetScaledCapsuleHalfHeight',target=h.get(g,'CapsuleComponent')).find_result_pin()
up=h.call(g,'/Script/Engine.KismetMathLibrary:MakeVector',Z=height).find_result_pin()
landing=h.call(g,'/Script/Engine.KismetMathLibrary:Add_VectorVector',
               A=nav.find_output_pin('ProjectedLocation'),B=up).find_result_pin()
move=h.call(g,'/Script/Engine.Actor:K2_SetActorLocation',start=from_fx,
            NewLocation=landing,bSweep=True,bTeleport=True)
effect(g,move.find_then_pin(),'NS_TemporalCut',position(g))
h.compile_blueprint(guard,warnings_as_errors=True)

g=h.edit(guard,'EventGraph')
begin=next(n for n in g.list_all_nodes() if isinstance(n,u.K2Node_Event) and 'BeginPlay' in str(n.get_node_title()))
# Keep the guard's initial pose and checkpoint snapshot ahead of the story gates.
nodes={n.get_name():n for n in g.list_all_nodes()}
capture=nodes['K2Node_VariableSet_16']
if not capture.find_then_pin().list_connected_pins():
    branch_pin,=begin.find_then_pin().list_connected_pins()
    begin.find_then_pin().break_pin_links()
    h.connect(begin.find_then_pin(),nodes['K2Node_VariableSet_33'].find_execute_pin())
    h.connect(capture.find_then_pin(),branch_pin)
branch_pin,=capture.find_then_pin().list_connected_pins()
listener=branch_pin.get_owning_node()
timer,_=h.branch(g,listener.find_output_pin('else'),h.math(g,'EqualEqual_IntInt',h.get(g,'B_StoryGate'),3))
h.call(g,'/Script/Engine.KismetSystemLibrary:K2_SetTimer',start=timer,Object=h.self_pin(g),
       FunctionName=update,Time=0.25,bLooping=True)
tick=next(n for n in g.list_all_nodes() if isinstance(n,u.K2Node_Event) and 'Tick' in str(n.get_node_title()))
call,=tick.find_then_pin().list_connected_pins()
gate,=call.get_owning_node().find_then_pin().list_connected_pins()
condition=gate.get_owning_node().find_input_pin('Condition')
old,=condition.list_connected_pins()
h.connect(h.all_true(g,old,h.not_(g,h.get(g,'bB_SupervisorBusy'))),condition)

g=h.edit(guard,'B_ApplyHealthDamage')
fall,=[n for n in g.list_all_nodes() if 'B_PlayKnockoutFall' in str(n.get_node_title())]
is_boss,_=h.branch(g,fall.find_then_pin(),h.math(g,'EqualEqual_IntInt',h.get(g,'B_StoryGate'),3))
report(g,is_boss,'SupervisorDefeated','Archive')
h.layout(guard,{update})
h.save(guard)
u.log('B_SUPERVISOR saved pulse, navigable displacement, start and defeat')
