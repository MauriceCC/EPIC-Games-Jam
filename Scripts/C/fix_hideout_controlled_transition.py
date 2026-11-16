"""Replace C wardrobe auto-walking with a bounded, collision-checked hidden transition.

Run once with PIE stopped. Changes only BP_Hideout and its C-owned Story instances.
The existing HUD fade is reused unchanged. No NPC, player, animation or contract is edited.
"""
import unreal,sys
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
bp=h.asset('Narrative/BP_Hideout');interaction=h.asset('Narrative/BP_InteractionComponent');stealth=h.asset('Enemies/BP_StealthComponent')
real=h.basic('real');vector=unreal.BlueprintEditorLibrary.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'));rotator=unreal.BlueprintEditorLibrary.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Rotator'))

def graph(name,inputs=(),outputs=()):
 g=h.edit(bp,name)
 if g:h.clear_body(g);return g
 return h.function(bp,name,inputs,outputs)
def now(g):return h.call(g,'/Script/Engine.GameplayStatics:GetRealTimeSeconds').find_result_pin()
def self_call(g,start,name,**args):return h.invoke(g,start,bp,name,**args).find_then_pin()
def merge(g,*pins):
 n=g.add_branch_node();h.literal(n.find_input_pin('Condition'),True)
 for p in pins:h.connect(p,n.find_execute_pin())
 return n.find_output_pin('then')
def location(g,target):return h.call(g,'/Script/Engine.Actor:K2_GetActorLocation',target=target).find_result_pin()
def rotation(g,target):return h.call(g,'/Script/Engine.Actor:K2_GetActorRotation',target=target).find_result_pin()
def marker(g,name):return h.call(g,'/Script/Engine.SceneComponent:K2_GetComponentLocation',target=h.get(g,name)).find_result_pin()
def timer(g,start,name,seconds,loop=False):return h.call(g,'/Script/Engine.KismetSystemLibrary:K2_SetTimer',start,Object=h.self_pin(g),FunctionName=name,Time=seconds,bLooping=loop,bMaxOncePerFrame=True).find_then_pin()
def clear(g,start,name):return h.call(g,'/Script/Engine.KismetSystemLibrary:K2_ClearTimer',start,Object=h.self_pin(g),FunctionName=name).find_then_pin()
def halt(g,start):
 end=h.call(g,'/Script/Engine.MovementComponent:StopMovementImmediately',start,h.get(g,'MotionComponent')).find_then_pin()
 return h.call(g,'/Script/Engine.Pawn:ConsumeMovementInputVector',end,h.get(g,'MovingPawn')).find_then_pin()
def focus_component(g):return h.call(g,'/Script/Engine.Actor:GetComponentByClass',target=h.get(g,'Occupant'),ComponentClass=interaction.generated_class().get_path_name()).find_result_pin()
def hidden(g,start,value):
 msg=h.message(g,start,'GetStealthComponent',h.get(g,'Occupant'));yes,no=h.branch(g,msg.find_then_pin(),h.is_valid(g,msg.find_result_pin()))
 end=h.invoke(g,yes,stealth,'SetHidden',target=msg.find_result_pin(),bHidden=value).find_then_pin()
 return merge(g,end,no)
def face(g,start,target):
 s=h.call(g,'/Script/Engine.KismetMathLibrary:BreakVector',InVec=start);t=h.call(g,'/Script/Engine.KismetMathLibrary:BreakVector',InVec=target)
 flat=h.call(g,'/Script/Engine.KismetMathLibrary:MakeVector',X=t.find_output_pin('X'),Y=t.find_output_pin('Y'),Z=s.find_output_pin('Z')).find_result_pin()
 return h.call(g,'/Script/Engine.KismetMathLibrary:FindLookAtRotation',Start=start,Target=flat).find_result_pin()
def begin_watch(g,start):
 end=h.setvar(g,start,'TransitionStartedReal',now(g));end=h.setvar(g,end,'NextUseAllowedAt',h.math(g,'Add_DoubleDouble',now(g),.5))
 return timer(g,end,'AbortTransition',1.5)

for name,typ,default in [('TransitionStartedReal',real,0),('NextUseAllowedAt',real,0),('EntryReturnLocation',vector,'(X=0,Y=0,Z=0)'),('EntryReturnRotation',rotator,'(Pitch=0,Yaw=0,Roll=0)'),('LastSafeLocation',vector,'(X=0,Y=0,Z=0)'),('LastSafeRotation',rotator,'(Pitch=0,Yaw=0,Roll=0)')]:h.variable(bp,name,typ,default,False,'Hideout Transition')
graph('AbortTransition');graph('TryHiddenReposition',[('Destination',vector),('Facing',rotator)],[('Success',h.basic('bool'))])
h.compile_blueprint(bp,warnings_as_errors=True)

# Delete every automatic movement body, including unreachable legacy call sites.
for name in ('BuildApproachPath','DriveToNextPoint'):graph(name)
g=graph('TryHiddenReposition');end=h.setvar(g,g.find_graph_entry_pin(),'LastSafeLocation',location(g,h.get(g,'MovingPawn')));end=h.setvar(g,end,'LastSafeRotation',rotation(g,h.get(g,'MovingPawn')))
move=h.call(g,'/Script/Engine.Actor:K2_TeleportTo',end,h.get(g,'MovingPawn'),DestLocation=h.param(g,'Destination'),DestRotation=h.param(g,'Facing'))
distance=h.math(g,'VSize',h.math(g,'Subtract_VectorVector',location(g,h.get(g,'MovingPawn')),h.param(g,'Destination')))
yes,no=h.branch(g,move.find_then_pin(),h.all_true(g,move.find_result_pin(),h.math(g,'LessEqual_DoubleDouble',distance,12)))
h.result(g,yes,Success=True)
back=h.call(g,'/Script/Engine.Actor:K2_TeleportTo',no,h.get(g,'MovingPawn'),DestLocation=h.get(g,'LastSafeLocation'),DestRotation=h.get(g,'LastSafeRotation'))
h.result(g,back.find_then_pin(),Success=False)

g=graph('BeginEntry');end=h.setvar(g,g.find_graph_entry_pin(),'Occupant',h.param(g,'Interactor'))
end,pawn,failed=h.cast(g,end,h.param(g,'Interactor'),unreal.Pawn.static_class());self_call(g,failed,'ReleaseOccupant')
end=h.setvar(g,end,'MovingPawn',pawn)
for name,cls in [('MotionComponent',unreal.CharacterMovementComponent),('OccupantMesh',unreal.SkeletalMeshComponent)]:
 comp=h.call(g,'/Script/Engine.Actor:GetComponentByClass',target=pawn,ComponentClass=cls.static_class().get_path_name()).find_result_pin();end=h.setvar(g,end,name,comp)
end=h.setvar(g,end,'OccupantController',h.call(g,'/Script/Engine.GameplayStatics:GetPlayerController',PlayerIndex=0).find_result_pin())
end=h.setvar(g,end,'bOriginalHidden',h.get(g,'bHiddenInGame',h.get(g,'OccupantMesh'),unreal.SceneComponent.static_class()))
end=h.setvar(g,end,'EntryReturnLocation',location(g,pawn));end=h.setvar(g,end,'EntryReturnRotation',rotation(g,pawn))
end=h.setvar(g,end,'bTransitioning',True);end=h.setvar(g,end,'bExiting',False)
end=h.call(g,'/Script/Engine.Controller:StopMovement',end,h.get(g,'OccupantController')).find_then_pin();end=halt(g,end)
end=h.call(g,'/Script/Engine.Controller:SetIgnoreMoveInput',end,h.get(g,'OccupantController'),bNewMoveInput=True).find_then_pin();end=h.setvar(g,end,'bOwnsMovementLock',True)
end=h.call(g,'/Script/Engine.Actor:EnableInput',end,PlayerController=h.get(g,'OccupantController')).find_then_pin()
end=h.invoke(g,end,interaction,'LockFocusTo',target=focus_component(g),Target=h.self_pin(g)).find_then_pin()
end=h.message(g,end,'SetRetakeBlocked',h.get(g,'Occupant'),bBlocked=True).find_then_pin();end=h.message(g,end,'ClearRetakeHistory',h.get(g,'Occupant')).find_then_pin()
end=h.call(g,'/Script/Engine.KismetArrayLibrary:Array_Clear',end,TargetArray=h.get(g,'MotionWaypoints')).find_then_pin();end=h.setvar(g,end,'WaypointIndex',0)
self_call(g,begin_watch(g,end),'StartDoorFade')

g=graph('ExecuteInteraction');allowed,_=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.not_(g,h.get(g,'bTransitioning')),h.math(g,'GreaterEqual_DoubleDouble',now(g),h.get(g,'NextUseAllowedAt'))))
yes,no=h.branch(g,allowed,h.get(g,'bOccupied'));self_call(g,yes,'BeginExit');self_call(g,no,'BeginEntry',Interactor=h.param(g,'Interactor'))
g=graph('BeginExit');end=clear(g,g.find_graph_entry_pin(),'ValidateOccupant');end=h.setvar(g,end,'bTransitioning',True);end=h.setvar(g,end,'bExiting',True);self_call(g,begin_watch(g,end),'StartDoorFade')
g=graph('StartDoorFade');end=halt(g,g.find_graph_entry_pin());end=h.setvar(g,end,'MotionStage',1);end=h.setvar(g,end,'PhaseStartedAt',now(g));timer(g,end,'UpdateHideoutTransition',.016,True)
g=graph('UpdateHideoutTransition');valid,invalid=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.is_valid(g,h.get(g,'MovingPawn')),h.is_valid(g,h.get(g,'MotionComponent')),h.is_valid(g,h.get(g,'OccupantMesh')),h.is_valid(g,h.get(g,'OccupantController'))));self_call(g,invalid,'AbortTransition')
late,on_time=h.branch(g,valid,h.math(g,'GreaterEqual_DoubleDouble',h.math(g,'Subtract_DoubleDouble',now(g),h.get(g,'TransitionStartedReal')),1.5));self_call(g,late,'AbortTransition')
msg=h.message(g,on_time,'IsDefeated',h.get(g,'Occupant'));dead,alive=h.branch(g,msg.find_then_pin(),msg.find_result_pin());self_call(g,dead,'AbortTransition');self_call(g,alive,'UpdateDoorFade')

g=graph('UpdateDoorFade');duration=h.math(g,'FClamp',h.get(g,'FadeDuration'),.08,.22);alpha=h.math(g,'FClamp',h.math(g,'Divide_DoubleDouble',h.math(g,'Subtract_DoubleDouble',now(g),h.get(g,'PhaseStartedAt')),duration),0,1)
outward,back=h.branch(g,g.find_graph_entry_pin(),h.math(g,'EqualEqual_IntInt',h.get(g,'MotionStage'),1));end=self_call(g,outward,'SetTransitionVeil',Alpha=alpha);black,_=h.branch(g,end,h.math(g,'GreaterEqual_DoubleDouble',alpha,1))
exiting,entering=h.branch(g,black,h.get(g,'bExiting'))
entry=h.invoke(g,entering,bp,'TryHiddenReposition',Destination=marker(g,'EntryDock'),Facing=face(g,marker(g,'EntryDock'),location(g,h.self_pin(g))))
okay,failed=h.branch(g,entry.find_then_pin(),entry.find_output_pin('Success'));self_call(g,failed,'AbortTransition')
end=h.call(g,'/Script/Engine.SceneComponent:SetHiddenInGame',okay,h.get(g,'OccupantMesh'),NewHidden=True,bPropagateToChildren=True).find_then_pin();end=hidden(g,end,True);end=h.setvar(g,end,'bOccupied',True);end=h.setvar(g,end,'MotionStage',2);h.setvar(g,end,'PhaseStartedAt',now(g))
exit_move=h.invoke(g,exiting,bp,'TryHiddenReposition',Destination=marker(g,'ExitPoint'),Facing=face(g,marker(g,'EntryDock'),marker(g,'ExitPoint')))
okay,failed=h.branch(g,exit_move.find_then_pin(),exit_move.find_output_pin('Success'))
# A blocked exit returns to the pre-entry safe position; otherwise release at the
# already collision-valid door dock. Every failure restores visibility/control.
fallback=h.invoke(g,failed,bp,'TryHiddenReposition',Destination=h.get(g,'EntryReturnLocation'),Facing=h.get(g,'EntryReturnRotation'));self_call(g,fallback.find_then_pin(),'AbortTransition')
end=h.call(g,'/Script/Engine.SceneComponent:SetHiddenInGame',okay,h.get(g,'OccupantMesh'),NewHidden=h.get(g,'bOriginalHidden'),bPropagateToChildren=True).find_then_pin();end=hidden(g,end,False);end=h.setvar(g,end,'bOccupied',False);end=h.setvar(g,end,'MotionStage',2);h.setvar(g,end,'PhaseStartedAt',now(g))
end=self_call(g,back,'SetTransitionVeil',Alpha=h.math(g,'Subtract_DoubleDouble',1,alpha));done,_=h.branch(g,end,h.math(g,'GreaterEqual_DoubleDouble',alpha,1));yes,no=h.branch(g,done,h.get(g,'bExiting'));self_call(g,yes,'FinishExit');self_call(g,no,'FinishEntry')
g=graph('FinishEntry');end=clear(g,g.find_graph_entry_pin(),'UpdateHideoutTransition');end=clear(g,end,'AbortTransition');end=halt(g,end);end=h.setvar(g,end,'bTransitioning',False);end=h.setvar(g,end,'NextUseAllowedAt',h.math(g,'Add_DoubleDouble',now(g),.25));end=h.setvar(g,end,'InteractionPromptRow','HideoutLeavePrompt');end=self_call(g,end,'SetTransitionVeil',Alpha=0);end=h.invoke(g,end,interaction,'RefreshFocus',target=focus_component(g)).find_then_pin();timer(g,end,'ValidateOccupant',.1,True)
g=graph('AbortTransition');yes,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,'bTransitioning'));end=h.call(g,'/Script/Engine.KismetSystemLibrary:PrintString',yes,InString='Hideout transition cancelled; player control restored.',bPrintToScreen=False,bPrintToLog=True).find_then_pin();self_call(g,end,'ReleaseOccupant')

# Preserve the existing idempotent visibility/stealth/focus/input cleanup.
g=h.edit(bp,'ReleaseOccupant');start=g.find_graph_entry_pin();old=list(start.list_connected_pins());start.break_pin_links();end=clear(g,start,'AbortTransition');end=h.setvar(g,end,'NextUseAllowedAt',h.math(g,'Add_DoubleDouble',now(g),.25))
for pin in old:h.connect(end,pin)
for n in list(g.list_all_nodes()):
 if str(n.get_node_title()).replace(' ','')=='StopMovementImmediately':
  old=list(n.find_then_pin().list_connected_pins());n.find_then_pin().break_pin_links();end=h.call(g,'/Script/Engine.Pawn:ConsumeMovementInputVector',n.find_then_pin(),h.get(g,'MovingPawn')).find_then_pin()
  for pin in old:h.connect(end,pin)
g=h.edit(bp,'ValidateOccupant')
for n in list(g.list_all_nodes()):
 if n.get_class().get_name()=='K2Node_IfThenElse' and not n.find_output_pin('else').list_connected_pins():halt(g,n.find_output_pin('else'))
h.layout(bp);h.save(bp)
dirty=unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages();assert all(p.get_name()=='/Game/Unscripted/Maps/L_Whitechapel_Story' for p in dirty)
if dirty:
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.set_current_level_by_name('L_Whitechapel_Story');assert levels.save_current_level()
print('C_CONTROLLED_HIDEOUT_SAVED')
