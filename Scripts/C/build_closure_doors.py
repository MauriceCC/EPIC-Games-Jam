"""Implement only closure Block 2.1 in C's BP_Door and Story sublevel."""
import unreal,sys,json,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
out={'passed':False,'saved':[],'doors':[]}
def graph(bp,name,inputs=()):
 g=h.edit(bp,name)
 if g:h.clear_body(g);return g
 return h.function(bp,name,inputs)
def now(g):return h.call(g,'/Script/Engine.GameplayStatics:GetRealTimeSeconds').find_result_pin()
def vec(g,x=0,y=0,z=0):return h.call(g,'/Script/Engine.KismetMathLibrary:MakeVector',X=x,Y=y,Z=z).find_result_pin()
try:
 assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
 bp=h.asset('Narrative/BP_Door');base=h.asset('Narrative/BP_InteractableBase');objective=h.asset('Narrative/BP_ObjectiveManager')
 boolean=h.basic('bool');real=h.basic('real')
 for name,typ,default,editable in [('RequiredPhase',h.enum_type('EStoryPhase'),'NewEnumerator1',True),('bRequireSupervisorDefeat',boolean,False,True),('DoorWidth',real,200,True),('bDoubleLeaf',boolean,False,True),('bIsOpening',boolean,False,False),('OpeningStartedAt',real,0,False)]:h.variable(bp,name,typ,default,editable,'Door')
 primary=h.add_component(bp,'DoorMesh',unreal.StaticMeshComponent);secondary=h.add_component(bp,'RightDoorMesh',unreal.StaticMeshComponent);blocker=h.add_component(bp,'PassageBlocker',unreal.BoxComponent);nav=h.add_component(bp,'DoorNavigation',unreal.NavModifierComponent)
 for c in (primary,secondary):
  c.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);c.set_editor_property('can_ever_affect_navigation',False)
 blocker.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE);blocker.set_box_extent(unreal.Vector(100,18,150));blocker.set_editor_property('relative_location',unreal.Vector(0,0,150));blocker.set_collision_profile_name('BlockAll');blocker.set_editor_property('can_ever_affect_navigation',False)
 nav.set_editor_property('area_class',unreal.load_class(None,'/Script/NavigationSystem.NavArea_Null'))
 nav.set_editor_property('failsafe_extent',unreal.Vector(100,20,300))
 graph(bp,'ApplyDoorPose',[('Alpha',real)]);graph(bp,'UpdateDoorOpening');graph(bp,'FinishDoorOpening')
 # Expose only the existing private fact to C's door; do not alter its writers.
 if not h.edit(objective,'IsSupervisorDefeated'):
  h.function(objective,'IsSupervisorDefeated',outputs=[('Result',boolean)])
  h.compile_blueprint(objective,warnings_as_errors=True)
  getter=h.edit(objective,'IsSupervisorDefeated');h.result(getter,getter.find_graph_entry_pin(),Result=h.get(getter,'bSupervisorDefeated'));h.layout(objective,['IsSupervisorDefeated']);h.save(objective);out['saved'].append(objective.get_path_name())
 placeholder=graph(bp,'CanInteract');h.result(placeholder,placeholder.find_graph_entry_pin(),Result=False)
 h.compile_blueprint(bp,warnings_as_errors=True)
 g=graph(bp,'CanInteract');state=h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin();phase=h.message(g,g.find_graph_entry_pin(),'GetCurrentPhase',state)
 actual=h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=phase.find_result_pin()).find_result_pin();required=h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=h.get(g,'RequiredPhase')).find_result_pin()
 valid,no=h.branch(g,phase.find_then_pin(),h.all_true(g,h.is_valid(g,state),h.is_valid(g,h.param(g,'Interactor')),h.get(g,'bInteractionEnabled'),h.not_(g,h.get(g,'bConsumed')),h.not_(g,h.get(g,'bIsOpening')),h.not_(g,h.get(g,'bIsOpen')),h.math(g,'EqualEqual_IntInt',actual,required)));h.result(g,no,Result=False)
 boss,normal=h.branch(g,valid,h.get(g,'bRequireSupervisorDefeat'));h.result(g,normal,Result=True)
 manager=h.call(g,'/Script/Engine.Actor:GetComponentByClass',target=state,ComponentClass=objective.generated_class().get_path_name()).find_result_pin();yes,no=h.branch(g,boss,h.is_valid(g,manager));h.result(g,no,Result=False);query=h.invoke(g,yes,objective,'IsSupervisorDefeated',target=manager);h.result(g,query.find_then_pin(),Result=query.find_result_pin())
 g=graph(bp,'ExecuteInteraction');end=h.setvar(g,g.find_graph_entry_pin(),'bConsumed',True);end=h.setvar(g,end,'bIsOpening',True);end=h.setvar(g,end,'OpeningStartedAt',now(g))
 # A bounded opening never takes ownership of player input or movement.
 end=h.call(g,'/Script/Engine.KismetSystemLibrary:K2_SetTimer',end,Object=h.self_pin(g),FunctionName='FinishDoorOpening',Time=.8,bLooping=False).find_then_pin()
 h.call(g,'/Script/Engine.KismetSystemLibrary:K2_SetTimer',end,Object=h.self_pin(g),FunctionName='UpdateDoorOpening',Time=.016,bLooping=True,bMaxOncePerFrame=True)
 g=graph(bp,'ApplyDoorPose');alpha=h.math(g,'FClamp',h.param(g,'Alpha'),0,1);smooth=h.math(g,'Multiply_DoubleDouble',h.math(g,'Multiply_DoubleDouble',alpha,alpha),h.math(g,'Subtract_DoubleDouble',3,h.math(g,'Multiply_DoubleDouble',2,alpha)))
 angle=h.math(g,'Multiply_DoubleDouble',smooth,100);half=h.math(g,'Divide_DoubleDouble',h.get(g,'DoorWidth'),2);leaf_half=h.math(g,'SelectFloat',h.math(g,'Divide_DoubleDouble',h.get(g,'DoorWidth'),4),half,h.get(g,'bDoubleLeaf'))
 end=g.find_graph_entry_pin()
 for component,sign in [('DoorMesh',1),('RightDoorMesh',-1)]:
  yaw=h.math(g,'Multiply_DoubleDouble',angle,sign);offset=h.call(g,'/Script/Engine.KismetMathLibrary:RotateAngleAxis',InVect=vec(g,h.math(g,'Multiply_DoubleDouble',leaf_half,sign)),AngleDeg=yaw,Axis='(X=0,Y=0,Z=1)').find_result_pin();position=h.math(g,'Add_VectorVector',offset,vec(g,h.math(g,'Multiply_DoubleDouble',half,-sign)))
  end=h.call(g,'/Script/Engine.SceneComponent:K2_SetRelativeLocation',end,h.get(g,component),NewLocation=position,bSweep=False,bTeleport=True).find_then_pin();rot=h.call(g,'/Script/Engine.KismetMathLibrary:MakeRotator',Yaw=yaw).find_result_pin();end=h.call(g,'/Script/Engine.SceneComponent:K2_SetRelativeRotation',end,h.get(g,component),NewRotation=rot,bSweep=False,bTeleport=True).find_then_pin()
 g=graph(bp,'UpdateDoorOpening');alpha=h.math(g,'FClamp',h.math(g,'Divide_DoubleDouble',h.math(g,'Subtract_DoubleDouble',now(g),h.get(g,'OpeningStartedAt')),.3),0,1);end=h.invoke(g,g.find_graph_entry_pin(),bp,'ApplyDoorPose',Alpha=alpha).find_then_pin();yes,_=h.branch(g,end,h.math(g,'GreaterEqual_DoubleDouble',alpha,1));h.invoke(g,yes,bp,'FinishDoorOpening')
 g=graph(bp,'FinishDoorOpening');end,_=h.branch(g,g.find_graph_entry_pin(),h.not_(g,h.get(g,'bIsOpen')))
 for name in ('UpdateDoorOpening','FinishDoorOpening'):end=h.call(g,'/Script/Engine.KismetSystemLibrary:K2_ClearTimer',end,Object=h.self_pin(g),FunctionName=name).find_then_pin()
 end=h.invoke(g,end,bp,'ApplyDoorPose',Alpha=1).find_then_pin();end=h.setvar(g,end,'bIsOpen',True);end=h.setvar(g,end,'bIsOpening',False)
 end=h.call(g,'/Script/Engine.Actor:SetActorEnableCollision',end,bNewActorEnableCollision=False).find_then_pin();end=h.call(g,'/Script/NavigationSystem.NavModifierComponent:SetAreaClass',end,h.get(g,'DoorNavigation'),NewAreaClass='/Script/NavigationSystem.NavArea_Default').find_then_pin()
 valid,invalid=h.branch(g,end,h.is_valid(g,h.get(g,'LastInteractor')));end=h.message(g,valid,'ClearRetakeHistory',h.get(g,'LastInteractor')).find_then_pin();join=g.add_branch_node();h.literal(join.find_input_pin('Condition'),True);h.connect(end,join.find_execute_pin());h.connect(invalid,join.find_execute_pin())
 yes,_=h.branch(g,join.find_output_pin('then'),h.get(g,'bReportsEscapeRoute'));h.invoke(g,yes,base,'ReportStoryFact',Event='NewEnumerator1',Param='')
 h.layout(bp);h.save(bp);out['saved'].append(bp.get_path_name())
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 assert levels.set_current_level_by_name('L_Whitechapel_Story')
 existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
 specs=[('C_SideDoor',(2800,4600,0),0,200,'SM_Door_Wood_Leaf',False,1,True,False,'Open escape route'),('C_ArchiveGate',(3600,3600,0),90,400,'SM_IronGate_A',False,4,False,False,'Open archive gate'),('C_RecordsDoor',(4800,3000,0),90,400,'SM_Door_Agency_Leaf',True,4,False,True,'Open records door')]
 for label,pos,yaw,width,mesh_name,double,phase,report,boss,prompt in specs:
  a=existing.get(label)
  if a is None:a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(*pos),unreal.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label(label)
  a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
  assert '/Maps/L_Whitechapel_Story.' in a.get_path_name(),a.get_path_name()
  for name,value in [('DoorWidth',width),('bDoubleLeaf',double),('bReportsEscapeRoute',report),('bRequireSupervisorDefeat',boss),('InteractionPromptRow',''),('InteractionPrompt',prompt)]:a.set_editor_property(name,value)
  a.set_editor_property('RequiredPhase',type(a.get_editor_property('RequiredPhase')).cast(phase))
  art=h.asset('Art/Props/'+mesh_name+'/'+mesh_name);bounds=art.get_bounding_box();leaf_width=width/2 if double else width
  for name,on in [('DoorMesh',True),('RightDoorMesh',double)]:
   c=a.get_editor_property(name);c.set_static_mesh(art if on else None);c.set_visibility(on);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
   if on:c.set_relative_scale3d(unreal.Vector(leaf_width/(bounds.max.x-bounds.min.x),1,300/(bounds.max.z-bounds.min.z)))
  a.get_editor_property('PassageBlocker').set_box_extent(unreal.Vector(width/2,18,150));a.get_editor_property('DoorNavigation').set_editor_property('failsafe_extent',unreal.Vector(width/2,20,300));a.call_method('ApplyDoorPose',args=(0.0,))
  out['doors'].append({'name':label,'path':a.get_path_name(),'location':pos,'required_phase':phase,'requires_supervisor':boss,'mesh':art.get_path_name()})
 assert levels.save_current_level();out['saved'].append('/Game/Unscripted/Maps/L_Whitechapel_Story');out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
 (repo/'Scripts/C/closure_doors_build.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_CLOSURE_DOORS_BUILD '+json.dumps(out))
