"""Integrate C-31/C-32 without rewriting existing HUD or progression functions.

Only C packages are edited. The real player receives the published interface
messages; native C-owned modal/terminal input prevents gameplay behind the UI.
"""
import unreal,sys,json,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h,umg_helpers_c as u
out={'passed':False,'saved':[],'actors':[]}
def graph(bp,name,inputs=(),outputs=(),override=False):
 g=h.edit(bp,name)
 if g:h.clear_body(g);return g
 return h.override(bp,name) if override else h.function(bp,name,inputs,outputs)
def player(g):return h.call(g,'/Script/Engine.GameplayStatics:GetPlayerPawn',PlayerIndex=0).find_result_pin()
def pc(g):return h.call(g,'/Script/Engine.GameplayStatics:GetPlayerController',PlayerIndex=0).find_result_pin()
def manager(g):return h.call(g,'/Script/Engine.Actor:GetComponentByClass',target=h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin(),ComponentClass=objective.generated_class().get_path_name()).find_result_pin()
def phase(g,obj):return h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=h.get(g,'CurrentPhase',obj,objective.generated_class())).find_result_pin()
def now(g):return h.call(g,'/Script/Engine.GameplayStatics:GetRealTimeSeconds').find_result_pin()
def merge(g,*pins):
 n=g.add_branch_node();h.literal(n.find_input_pin('Condition'),True)
 for p in pins:h.connect(p,n.find_execute_pin())
 return n.find_output_pin('then')
def cast_hud(g,start):return h.cast(g,start,h.call(g,'/Script/Engine.PlayerController:GetHUD',target=pc(g)).find_result_pin(),hud.generated_class())[:2]
def ending_index(g,value):return h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=value).find_result_pin()
def ending_valid(g,value):return h.any_true(g,h.math(g,'EqualEqual_IntInt',ending_index(g,value),1),h.math(g,'EqualEqual_IntInt',ending_index(g,value),2))
def same_ending(g,a,b):return h.math(g,'EqualEqual_IntInt',h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=a).find_result_pin(),h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=b).find_result_pin())
def ui_mode(g,start,only):
 if only:return h.call(g,'/Script/UMG.WidgetBlueprintLibrary:SetInputMode_UIOnlyEx',start,PlayerController=pc(g),InWidgetToFocus=h.get(g,'FinalView'),InMouseLockMode='DoNotLock',bFlushInput=True).find_then_pin()
 end=h.call(g,'/Script/UMG.WidgetBlueprintLibrary:SetInputMode_GameOnly',start,PlayerController=pc(g),bFlushInput=True).find_then_pin()
 return h.call(g,'/Script/UMG.WidgetBlueprintLibrary:SetFocusToGameViewport',end).find_then_pin()
try:
 assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
 objective=h.asset('Narrative/BP_ObjectiveManager');final=h.asset('Narrative/BP_FinalChoice');base=h.asset('Narrative/BP_InteractableBase');hud=h.asset('UI/BP_HUD');view=h.asset('UI/WBP_Ending')
 boolean=h.basic('bool');real=h.basic('real');actor=h.obj_type(unreal.Actor);ending=h.enum_type('EEndingType')
 for name,typ,default,editable in [('SelectedEnding',ending,'NewEnumerator1',True),('RegistrationCount',h.basic('int'),0,False)]:h.variable(final,name,typ,default,editable,'Final Registration')
 mesh=h.add_component(final,'StationMesh',unreal.StaticMeshComponent);mesh.set_static_mesh(h.asset('Art/Props/SM_RecordStation_Official/SM_RecordStation_Official'));mesh.set_collision_profile_name('BlockAll');mesh.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
 graph(final,'CanInteract',override=True);graph(final,'ExecuteInteraction',override=True);graph(final,'ConfirmRegistration',[('Interactor',actor)],[('Succeeded',boolean)])
 h.compile_blueprint(final,warnings_as_errors=True)
 specs=[('PendingFinalChoice',h.obj_type(final.generated_class()),''),('PendingFinalInteractor',actor,''),('FinalView',h.obj_type(view.generated_class()),''),('bFinalViewInViewport',boolean,False),('bFinalConfirmationOpen',boolean,False),('bEndingPresented',boolean,False),('FinalConfirmationOpenedAt',real,0),('bFinalOwnsMoveLock',boolean,False),('bPreviousFinalCursor',boolean,False)]
 for name,typ,default in specs:h.variable(hud,name,typ,default,False,'Final Registration')
 methods={'EnsureFinalView':[],'OpenFinalConfirmation':[('Station',h.obj_type(final.generated_class())),('Interactor',actor)],'ConfirmFinalChoice':[],'CancelFinalChoice':[],'PresentFinalEnding':[('Ending',ending)]}
 for name,inputs in methods.items():graph(hud,name,inputs)
 graph(objective,'CanChooseFinalDocument',outputs=[('Result',boolean)])
 graph(objective,'GetRegisteredEnding',outputs=[('Result',ending)])
 h.compile_blueprint(objective,warnings_as_errors=True);h.compile_blueprint(hud,warnings_as_errors=True)
 g=h.edit(objective,'CanChooseFinalDocument');h.result(g,g.find_graph_entry_pin(),Result=h.all_true(g,h.math(g,'EqualEqual_IntInt',phase(g,None),4),h.get(g,'bSupervisorDefeated'),h.get(g,'bTruthRevelationComplete'),h.math(g,'EqualEqual_IntInt',ending_index(g,h.get(g,'Ending')),0),h.not_(g,h.get(g,'bDialogueActive')),h.not_(g,h.get(g,'bDocumentActive'))))
 g=h.edit(objective,'GetRegisteredEnding');h.result(g,g.find_graph_entry_pin(),Result=h.get(g,'Ending'))
 g=h.edit(final,'CanInteract');obj=manager(g);yes,no=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.is_valid(g,obj),h.is_valid(g,h.param(g,'Interactor')),h.get(g,'bInteractionEnabled'),h.not_(g,h.get(g,'bConsumed')),ending_valid(g,h.get(g,'SelectedEnding'))));h.result(g,no,Result=False)
 ready=h.invoke(g,yes,objective,'CanChooseFinalDocument',target=obj);h.result(g,ready.find_then_pin(),Result=ready.find_result_pin())
 g=h.edit(final,'ExecuteInteraction');end,typed=cast_hud(g,g.find_graph_entry_pin());h.invoke(g,end,hud,'OpenFinalConfirmation',target=typed,Station=h.self_pin(g),Interactor=h.param(g,'Interactor'))
 g=h.edit(final,'ConfirmRegistration');query=h.invoke(g,g.find_graph_entry_pin(),final,'CanInteract',Interactor=h.param(g,'Interactor'));yes,no=h.branch(g,query.find_then_pin(),query.find_result_pin());h.result(g,no,Succeeded=False)
 loc=h.call(g,'/Script/Engine.Actor:K2_GetActorLocation',target=h.param(g,'Interactor')).find_result_pin();self_loc=h.call(g,'/Script/Engine.Actor:K2_GetActorLocation').find_result_pin();distance=h.math(g,'VSize',h.math(g,'Subtract_VectorVector',loc,self_loc))
 end,typed=cast_hud(g,yes)
 yes,no=h.branch(g,end,h.all_true(g,h.math(g,'LessEqual_DoubleDouble',distance,260),h.get(g,'bFinalConfirmationOpen',typed,hud.generated_class()),h.math(g,'EqualEqual_ObjectObject',h.get(g,'PendingFinalChoice',typed,hud.generated_class()),h.self_pin(g)),h.math(g,'EqualEqual_ObjectObject',h.get(g,'PendingFinalInteractor',typed,hud.generated_class()),h.param(g,'Interactor'))));h.result(g,no,Succeeded=False)
 a,b=h.branch(g,yes,h.math(g,'EqualEqual_IntInt',ending_index(g,h.get(g,'SelectedEnding')),1))
 ends=[]
 for pin,token in [(a,'OfficialCut'),(b,'AuthenticRecord')]:ends.append(h.invoke(g,pin,base,'ReportStoryFact',Event='NewEnumerator7',Param=token).find_then_pin())
 end=merge(g,*ends);obj=manager(g);phase_read=h.invoke(g,end,objective,'GetStoryPhase',target=obj);ending_read=h.invoke(g,phase_read.find_then_pin(),objective,'GetRegisteredEnding',target=obj);phase_value=h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=phase_read.find_result_pin()).find_result_pin();yes,no=h.branch(g,ending_read.find_then_pin(),h.all_true(g,h.math(g,'EqualEqual_IntInt',phase_value,5),same_ending(g,ending_read.find_result_pin(),h.get(g,'SelectedEnding'))));h.result(g,no,Succeeded=False)
 end=h.setvar(g,yes,'bConsumed',True);end=h.setvar(g,end,'RegistrationCount',h.math(g,'Add_IntInt',h.get(g,'RegistrationCount'),1));h.result(g,end,Succeeded=True)
 g=h.edit(hud,'EnsureFinalView');valid,missing=h.branch(g,g.find_graph_entry_pin(),h.is_valid(g,h.get(g,'FinalView')))
 create=g.create_node_from_name(next(x for x in h.actions(g) if x.split('|')[-1].replace(' ','') in ('CreateWidget','Crearwidget')),unreal.Vector2D(0,0),[])
 h.literal(create.find_input_pin('Class'),view.generated_class().get_path_name());h.connect(missing,create.find_execute_pin());h.connect(pc(g),create.find_input_pin('OwningPlayer'));end=h.setvar(g,create.find_then_pin(),'FinalView',create.find_result_pin());end=merge(g,valid,end)
 _,add=h.branch(g,end,h.get(g,'bFinalViewInViewport'));added=h.call(g,'/Script/UMG.UserWidget:AddToViewport',add,h.get(g,'FinalView'),ZOrder=100).find_then_pin();h.setvar(g,added,'bFinalViewInViewport',True)
 g=h.edit(hud,'OpenFinalConfirmation');yes,_=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.not_(g,h.get(g,'bFinalConfirmationOpen')),h.not_(g,h.get(g,'bEndingPresented')),h.is_valid(g,h.param(g,'Station')),h.is_valid(g,h.param(g,'Interactor'))))
 ready=h.invoke(g,yes,final,'CanInteract',target=h.param(g,'Station'),Interactor=h.param(g,'Interactor'));yes,_=h.branch(g,ready.find_then_pin(),ready.find_result_pin())
 end=h.invoke(g,yes,hud,'EnsureFinalView').find_then_pin();end=h.setvar(g,end,'PendingFinalChoice',h.param(g,'Station'));end=h.setvar(g,end,'PendingFinalInteractor',h.param(g,'Interactor'));end=h.setvar(g,end,'FinalConfirmationOpenedAt',now(g));end=h.setvar(g,end,'bFinalConfirmationOpen',True)
 end=h.setvar(g,end,'bPreviousFinalCursor',h.get(g,'bShowMouseCursor',pc(g),unreal.PlayerController.static_class()));end=h.setvar(g,end,'bShowMouseCursor',True,pc(g),unreal.PlayerController.static_class())
 ignored=h.call(g,'/Script/Engine.Controller:IsMoveInputIgnored',target=pc(g)).find_result_pin();end=h.setvar(g,end,'bFinalOwnsMoveLock',h.not_(g,ignored));acquire,skip=h.branch(g,end,h.get(g,'bFinalOwnsMoveLock'));locked=h.call(g,'/Script/Engine.Controller:SetIgnoreMoveInput',acquire,pc(g),bNewMoveInput=True).find_then_pin();end=merge(g,locked,skip)
 end=h.call(g,'/Script/Engine.Controller:StopMovement',end,pc(g)).find_then_pin();movement=h.call(g,'/Script/Engine.Pawn:GetMovementComponent',target=player(g)).find_result_pin();end=h.call(g,'/Script/Engine.MovementComponent:StopMovementImmediately',end,movement).find_then_pin()
 end=h.message(g,end,'SetGameplayInputEnabled',player(g),bEnabled=False).find_then_pin();end=h.message(g,end,'SetRetakeBlocked',player(g),bBlocked=True).find_then_pin()
 end=h.invoke(g,end,view,'PresentConfirmation',target=h.get(g,'FinalView'),Ending=h.get(g,'SelectedEnding',h.param(g,'Station'),final.generated_class())).find_then_pin();ui_mode(g,end,True)
 g=h.edit(hud,'CancelFinalChoice');yes,_=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,'bFinalConfirmationOpen'),h.not_(g,h.get(g,'bEndingPresented'))));end=h.setvar(g,yes,'bFinalConfirmationOpen',False)
 end=h.call(g,'/Script/UMG.Widget:RemoveFromParent',end,h.get(g,'FinalView')).find_then_pin();end=h.setvar(g,end,'bFinalViewInViewport',False);release,skip=h.branch(g,end,h.get(g,'bFinalOwnsMoveLock'));end=h.call(g,'/Script/Engine.Controller:SetIgnoreMoveInput',release,pc(g),bNewMoveInput=False).find_then_pin();end=merge(g,end,skip);end=h.setvar(g,end,'bFinalOwnsMoveLock',False)
 end=h.setvar(g,end,'bShowMouseCursor',h.get(g,'bPreviousFinalCursor'),pc(g),unreal.PlayerController.static_class());end=h.setvar(g,end,'PendingFinalChoice',None);end=h.setvar(g,end,'PendingFinalInteractor',None)
 end=h.invoke(g,end,objective,'RestoreNarrativeInputLock',target=manager(g)).find_then_pin();ui_mode(g,end,False)
 g=h.edit(hud,'ConfirmFinalChoice');yes,_=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,'bFinalConfirmationOpen'),h.not_(g,h.get(g,'bEndingPresented')),h.is_valid(g,h.get(g,'PendingFinalChoice')),h.math(g,'GreaterEqual_DoubleDouble',h.math(g,'Subtract_DoubleDouble',now(g),h.get(g,'FinalConfirmationOpenedAt')),.35)))
 accepted=h.invoke(g,yes,final,'ConfirmRegistration',target=h.get(g,'PendingFinalChoice'),Interactor=h.get(g,'PendingFinalInteractor'));_,failed=h.branch(g,accepted.find_then_pin(),accepted.find_output_pin('Succeeded'));h.invoke(g,failed,hud,'CancelFinalChoice')
 g=h.edit(hud,'PresentFinalEnding');obj=manager(g);phase_read=h.invoke(g,g.find_graph_entry_pin(),objective,'GetStoryPhase',target=obj);ending_read=h.invoke(g,phase_read.find_then_pin(),objective,'GetRegisteredEnding',target=obj);phase_value=h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=phase_read.find_result_pin()).find_result_pin();yes,_=h.branch(g,ending_read.find_then_pin(),h.all_true(g,h.not_(g,h.get(g,'bEndingPresented')),ending_valid(g,h.param(g,'Ending')),h.math(g,'EqualEqual_IntInt',phase_value,5),same_ending(g,h.param(g,'Ending'),ending_read.find_result_pin())))
 end=h.setvar(g,yes,'bEndingPresented',True);end=h.setvar(g,end,'bFinalConfirmationOpen',False);end=h.setvar(g,end,'PendingFinalChoice',None);end=h.setvar(g,end,'PendingFinalInteractor',None)
 end=h.invoke(g,end,hud,'EnsureFinalView').find_then_pin();end=h.message(g,end,'SetRetakeBlocked',player(g),bBlocked=True).find_then_pin();end=h.message(g,end,'ClearRetakeHistory',player(g)).find_then_pin();end=h.message(g,end,'SetGameplayInputEnabled',player(g),bEnabled=False).find_then_pin()
 end=h.call(g,'/Script/Engine.Controller:StopMovement',end,pc(g)).find_then_pin();end=h.call(g,'/Script/Engine.Actor:DisableInput',end,player(g),PlayerController=pc(g)).find_then_pin()
 end=h.call(g,'/Script/UMG.Widget:RemoveFromParent',end,h.get(g,'View')).find_then_pin();end=h.invoke(g,end,view,'PresentEnding',target=h.get(g,'FinalView'),Ending=h.param(g,'Ending')).find_then_pin();end=h.setvar(g,end,'bShowMouseCursor',True,pc(g),unreal.PlayerController.static_class());end=ui_mode(g,end,True)
 h.call(g,'/Script/Engine.GameplayStatics:SetGamePaused',end,bPaused=True)
 g=h.edit(hud,'EventGraph')
 if not any(n.get_class().get_name()=='K2Node_AssignDelegate' and 'OnEndingTriggered' in str(n.get_node_title()).replace(' ','') for n in g.list_all_nodes()):
  # Insert a guard before the existing E chain; preserve every original node.
  g=h.edit(hud,'UseNarrativeInteraction');entry=g.find_graph_entry_pin();original=entry.list_connected_pins();entry.break_pin_links();_,allow=h.branch(g,entry,h.get(g,'bEndingPresented'));yes,no=h.branch(g,allow,h.get(g,'bFinalConfirmationOpen'));h.invoke(g,yes,hud,'ConfirmFinalChoice')
  for pin in original:h.connect(no,pin)
  # Bind only the existing C dispatcher, after the existing BeginPlay setup.
  g=h.edit(hud,'EventGraph');tail=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='EnableNarrativeInput');assert not tail.find_then_pin().list_connected_pins()
  _,event=h.bind_assign(g,tail.find_then_pin(),manager(g),'OnEndingTriggered');h.invoke(g,event.find_then_pin(),hud,'PresentFinalEnding',Ending=event.find_output_pin('Ending'))
  tab=next(n for n in g.list_all_nodes() if n.get_class().get_name()=='K2Node_InputKey' and str(n.get_node_title())=='Tab');pin=tab.find_output_pin('Pressed');original=pin.list_connected_pins();pin.break_pin_links();yes,_=h.branch(g,pin,h.not_(g,h.any_true(g,h.get(g,'bFinalConfirmationOpen'),h.get(g,'bEndingPresented'))))
  for target in original:h.connect(yes,target)
 # Modal keys are handled by the focusable widget in UI-only input mode.
 for name,method in [('RequestConfirm','ConfirmFinalChoice'),('RequestCancel','CancelFinalChoice')]:
  g=graph(view,name);yes,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,'bConfirmationMode'));end,typed=cast_hud(g,yes);h.invoke(g,end,hud,method,target=typed)
 for name in ('OnKeyDown','OnKeyUp'):
  g=graph(view,name,override=True);key=h.call(g,'/Script/Engine.KismetInputLibrary:GetKey',Input=h.param(g,'InKeyEvent')).find_result_pin()
  equal=lambda value:h.call(g,'/Script/Engine.KismetInputLibrary:EqualEqual_KeyKey',A=key,B=value).find_result_pin()
  if name=='OnKeyUp':
   yes,no=h.branch(g,g.find_graph_entry_pin(),equal('E'));end=h.setvar(g,yes,'bConfirmKeyArmed',True);end=merge(g,end,no)
  else:
   repeat=h.call(g,'/Script/Engine.KismetInputLibrary:InputEvent_IsRepeat',Input=h.param(g,'InKeyEvent')).find_result_pin();yes,no=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,'bConfirmationMode'),equal('E'),h.not_(g,repeat)));end=h.invoke(g,yes,view,'RequestConfirm').find_then_pin();cancel,other=h.branch(g,no,h.all_true(g,h.get(g,'bConfirmationMode'),equal('BackSpace')));cancel=h.invoke(g,cancel,view,'RequestCancel').find_then_pin();end=merge(g,end,cancel);h.result(g,other,ReturnValue=h.call(g,'/Script/UMG.WidgetBlueprintLibrary:Unhandled').find_result_pin())
  h.result(g,end,ReturnValue=h.call(g,'/Script/UMG.WidgetBlueprintLibrary:Handled').find_result_pin())
 for bp in (objective,final,view,hud):h.layout(bp);h.save(bp);out['saved'].append(bp.get_path_name())
 cdo=unreal.get_default_object(final.generated_class());cdo.set_editor_property('InteractionPromptRow','OfficialFilePrompt');cdo.set_editor_property('InteractionPriority',45);h.save(final)
 prompts={'OfficialFilePrompt':'Examine official file','AuthenticFilePrompt':'Examine authentic file'}
 text=h.asset('Narrative/DT_HUDText');rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(text))
 for name,body in prompts.items():
  assert not any(r['Name']==name for r in rows);rows.append({'Name':name,'Speaker':'NewEnumerator6','Text':body,'Duration':0,'NextRow':'None'})
 assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(text,json.dumps(rows));assert unreal.EditorAssetLibrary.save_loaded_asset(text,False);out['saved'].append(text.get_path_name())
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.set_current_level_by_name('L_Whitechapel_Story');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
 for name,position,index,art,prompt in [('C_OfficialRecord',(5200,2600,0),1,'SM_RecordStation_Official','OfficialFilePrompt'),('C_AuthenticRecord',(5200,3400,0),2,'SM_RecordStation_Authentic','AuthenticFilePrompt')]:
  assert name not in existing,'Preserve an existing authored station'
  a=actors.spawn_actor_from_class(final.generated_class(),unreal.Vector(*position),unreal.Rotator());a.set_actor_label(name);assert '/Maps/L_Whitechapel_Story.' in a.get_path_name();a.set_editor_property('SelectedEnding',type(a.get_editor_property('SelectedEnding')).cast(index));a.set_editor_property('InteractionPromptRow',prompt);a.get_editor_property('StationMesh').set_static_mesh(h.asset('Art/Props/'+art+'/'+art));out['actors'].append({'name':name,'position':position,'ending':index})
 assert levels.save_current_level();out['saved'].append('/Game/Unscripted/Maps/L_Whitechapel_Story');out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:(repo/'Scripts/C/endings_integration_build.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_ENDINGS_INTEGRATION '+json.dumps(out))
