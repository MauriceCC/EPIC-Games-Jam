"""Integrate C-30 using existing narrative, document, checklist and HUD systems.

Run with PIE stopped. No Core contract, foreign asset or final-choice system is edited.
"""
import unreal,sys,json,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h,umg_helpers_c as u
out={'passed':False,'saved':[],'actors':[]}
def graph(bp,name,inputs=(),outputs=()):
 g=h.edit(bp,name)
 if g:h.clear_body(g);return g
 return h.function(bp,name,inputs,outputs)
def merge(g,*pins):
 n=g.add_branch_node();h.literal(n.find_input_pin('Condition'),True)
 for p in pins:h.connect(p,n.find_execute_pin())
 return n.find_output_pin('then')
def index(g,pin):return h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=pin).find_result_pin()
def phase(g):return index(g,h.get(g,'CurrentPhase'))
def now(g):return h.call(g,'/Script/Engine.GameplayStatics:GetRealTimeSeconds').find_result_pin()
def timer(g,start,fn,seconds,loop=False):return h.call(g,'/Script/Engine.KismetSystemLibrary:K2_SetTimer',start,Object=h.self_pin(g),FunctionName=fn,Time=seconds,bLooping=loop,bMaxOncePerFrame=True).find_then_pin()
def clear(g,start,fn):return h.call(g,'/Script/Engine.KismetSystemLibrary:K2_ClearTimer',start,Object=h.self_pin(g),FunctionName=fn).find_then_pin()
def report(g,start,event,source=None):
 state=h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
 return h.message(g,start,'ReportStoryEvent',state,Event='NewEnumerator'+str(event),Source=source or state,Param='').find_then_pin()
def manager(g):
 state=h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
 return h.call(g,'/Script/Engine.Actor:GetComponentByClass',target=state,ComponentClass=objective.generated_class().get_path_name()).find_result_pin()
try:
 assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
 objective=h.asset('Narrative/BP_ObjectiveManager');evidence=h.asset('Narrative/BP_Evidence');base=h.asset('Narrative/BP_InteractableBase');view=h.asset('UI/WBP_HUD');checklist=h.asset('UI/WBP_Checklist')
 boolean=h.basic('bool');real=h.basic('real');actor=h.obj_type(unreal.Actor)
 for name,typ,default in [('bFutureMessageQueued',boolean,False),('bFutureMessageRead',boolean,False),('FutureMessageSource',actor,''),('bTruthRevelationStarted',boolean,False),('bTruthRevelationComplete',boolean,False),('bTruthNoticeReported',boolean,False)]:
  h.variable(objective,name,typ,default,False,'Integrated Narrative')
 specs=[('CanReadFutureMessage',[],[('Result',boolean)]),('ReadFutureMessage',[('Source',actor)],[]),('CanCollectEvidence',[('Kind',h.enum_type('EEvidenceType'))],[('Result',boolean)]),('TryStartTruthRevelation',[],[]),('HandleIntegratedDialogueFinished',[('Row',h.basic('name'))],[])]
 for name,ins,outs in specs:graph(objective,name,ins,outs)
 h.compile_blueprint(objective,warnings_as_errors=True)
 g=graph(objective,'CanReadFutureMessage');h.result(g,g.find_graph_entry_pin(),Result=h.all_true(g,h.get(g,'bJackFound'),h.math(g,'GreaterEqual_IntInt',phase(g),1),h.math(g,'LessEqual_IntInt',phase(g),2),h.not_(g,h.get(g,'bFutureMessageQueued')),h.not_(g,h.get(g,'bDialogueActive')),h.not_(g,h.get(g,'bDocumentActive'))))
 g=graph(objective,'ReadFutureMessage');can=h.invoke(g,g.find_graph_entry_pin(),objective,'CanReadFutureMessage');yes,_=h.branch(g,can.find_then_pin(),can.find_result_pin());end=h.setvar(g,yes,'FutureMessageSource',h.param(g,'Source'));end=h.setvar(g,end,'bFutureMessageQueued',True);h.invoke(g,end,objective,'QueueDialogue',RowName='FutureMessage_01')
 g=graph(objective,'CanCollectEvidence');kind=index(g,h.param(g,'Kind'));fresh=h.any_true(g,h.all_true(g,h.math(g,'EqualEqual_IntInt',kind,0),h.not_(g,h.get(g,'bEvidenceFound'))),h.all_true(g,h.math(g,'EqualEqual_IntInt',kind,1),h.not_(g,h.get(g,'bFalseReportFound'))));h.result(g,g.find_graph_entry_pin(),Result=h.all_true(g,h.math(g,'EqualEqual_IntInt',phase(g),3),h.get(g,'bJackSafe'),fresh,h.not_(g,h.get(g,'bDocumentActive')),h.not_(g,h.get(g,'bDialogueActive'))))
 g=graph(objective,'TryStartTruthRevelation');ready=h.invoke(g,g.find_graph_entry_pin(),objective,'CanRevealTruth');yes,_=h.branch(g,ready.find_then_pin(),h.all_true(g,ready.find_result_pin(),h.get(g,'bPresentationEnabled'),h.not_(g,h.get(g,'bTruthRevelationStarted')),h.not_(g,h.get(g,'bDialogueActive')),h.not_(g,h.get(g,'bDocumentActive'))));end=h.setvar(g,yes,'bTruthRevelationStarted',True);h.invoke(g,end,objective,'QueueDialogue',RowName='Truth_01')
 g=graph(objective,'HandleIntegratedDialogueFinished');is_future=h.math(g,'EqualEqual_NameName',h.param(g,'Row'),'FutureMessage_01');yes,next_case=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,is_future,h.get(g,'bFutureMessageQueued'),h.not_(g,h.get(g,'bFutureMessageRead'))));end=h.setvar(g,yes,'bFutureMessageRead',True);report(g,end,12,h.get(g,'FutureMessageSource'))
 yes,_=h.branch(g,next_case,h.all_true(g,h.math(g,'EqualEqual_NameName',h.param(g,'Row'),'Truth_05'),h.get(g,'bTruthRevelationStarted'),h.not_(g,h.get(g,'bTruthRevelationComplete'))));ready=h.invoke(g,yes,objective,'CanRevealTruth');yes,_=h.branch(g,ready.find_then_pin(),ready.find_result_pin());end=h.setvar(g,yes,'bTruthRevelationComplete',True);end=report(g,end,4);yes,_=h.branch(g,end,h.all_true(g,h.math(g,'EqualEqual_IntInt',phase(g),4),h.not_(g,h.get(g,'bTruthNoticeReported'))));end=h.setvar(g,yes,'bTruthNoticeReported',True);report(g,end,11)
 # Keep the sole phase writer and every existing event route. Add only the
 # presentation-complete guard to the already guarded TruthRevealed branch.
 g=h.edit(objective,'ProcessStoryEvent');commit=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='CommitStoryPhase' and str(n.find_input_pin('NewPhase').get_pin_value())=='NewEnumerator4')
 branch_pin=commit.find_execute_pin().list_connected_pins()[0];branch=branch_pin.get_owning_node();condition=branch.find_input_pin('Condition');old=condition.list_connected_pins()[0];condition.break_pin_links();h.connect(h.all_true(g,old,h.get(g,'bTruthRevelationComplete')),condition)
 # Remove the two automatic queues now served by the actual scene interaction
 # and by the existing five-line Supervisor conversation before the phase change.
 g=h.edit(objective,'PresentStoryPhase')
 for row in ('FutureMessage_01','Truth_01'):
  n=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='QueueDialogue' and str(n.find_input_pin('RowName').get_pin_value())==row)
  previous=list(n.find_execute_pin().list_connected_pins());following=list(n.find_then_pin().list_connected_pins());g.remove_nodes([n])
  for a in previous:
   for b in following:h.connect(a,b)
 g=h.edit(objective,'SetDocumentActive');advance=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='AdvanceDialogueQueue');h.invoke(g,advance.find_then_pin(),objective,'TryStartTruthRevelation')
 g=h.edit(objective,'AdvanceDialogue');final=next(n for n in g.list_all_nodes() if n.get_class().get_name()=='K2Node_CallDelegate' and any(str(p.get_owning_node().get_node_title()).replace(' ','')=='AdvanceDialogueQueue' for p in n.find_then_pin().list_connected_pins()))
 following=list(final.find_then_pin().list_connected_pins());final.find_then_pin().break_pin_links();end=h.invoke(g,final.find_then_pin(),objective,'HandleIntegratedDialogueFinished',Row=h.get(g,'FinishedDialogueRow')).find_then_pin()
 for b in following:h.connect(end,b)
 h.layout(objective);h.save(objective);out['saved'].append(objective.get_path_name())
 # Keep the existing evidence text/data bindings and document presenter.
 g=h.edit(evidence,'RecordEvidence');show=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='OpenDocument');show.find_then_pin().break_pin_links()
 obsolete=[n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='CanRevealTruth' or n.get_class().get_name()=='K2Node_IfThenElse' or (str(n.get_node_title()).replace(' ','')=='ReportStoryFact' and str(n.find_input_pin('Event').get_pin_value())=='NewEnumerator4')];g.remove_nodes(obsolete)
 g=graph(evidence,'CanInteract');obj=manager(g);valid,no=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.is_valid(g,obj),h.is_valid(g,h.param(g,'Interactor')),h.get(g,'bInteractionEnabled'),h.not_(g,h.get(g,'bConsumed'))));h.result(g,no,Result=False);query=h.invoke(g,valid,objective,'CanCollectEvidence',target=obj,Kind=h.get(g,'EvidenceType'));h.result(g,query.find_then_pin(),Result=query.find_result_pin());h.layout(evidence,['RecordEvidence','CanInteract']);h.save(evidence);out['saved'].append(evidence.get_path_name())
 # A small C-owned interactable reuses D's folder art and existing dialogue UI.
 future=unreal.load_asset('/Game/Unscripted/Narrative/BP_FutureMessage_C')
 if not future:
  factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',base.generated_class());future=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_FutureMessage_C','/Game/Unscripted/Narrative',unreal.Blueprint,factory)
 mesh=h.add_component(future,'MessageMesh',unreal.StaticMeshComponent);mesh.set_static_mesh(h.asset('Art/Props/SM_Folder_Report/SM_Folder_Report'));mesh.set_editor_property('relative_location',unreal.Vector(0,0,90));mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);mesh.set_editor_property('can_ever_affect_navigation',False)
 for fn in ('CanInteract','ExecuteInteraction'):h.override(future,fn)
 h.compile_blueprint(future,warnings_as_errors=True)
 g=graph(future,'CanInteract');obj=manager(g);yes,no=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.is_valid(g,obj),h.is_valid(g,h.param(g,'Interactor')),h.get(g,'bInteractionEnabled'),h.not_(g,h.get(g,'bConsumed'))));h.result(g,no,Result=False);query=h.invoke(g,yes,objective,'CanReadFutureMessage',target=obj);h.result(g,query.find_then_pin(),Result=query.find_result_pin())
 g=graph(future,'ExecuteInteraction');end=h.setvar(g,g.find_graph_entry_pin(),'bConsumed',True);h.invoke(g,end,objective,'ReadFutureMessage',target=manager(g),Source=h.self_pin(g));unreal.get_default_object(future.generated_class()).set_editor_property('InteractionPromptRow','FutureMessagePrompt');h.layout(future);h.save(future);out['saved'].append(future.get_path_name())
 text=h.asset('Narrative/DT_HUDText');rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(text));assert not any(r['Name']=='FutureMessagePrompt' for r in rows);rows.append({'Name':'FutureMessagePrompt','Speaker':'System','Text':'Read future message','Duration':0,'NextRow':'None'});assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(text,json.dumps(rows));assert unreal.EditorAssetLibrary.save_loaded_asset(text,False);out['saved'].append(text.get_path_name())
 # Bring the existing rewrite on screen; preserve manual Tab ownership.
 for name,typ,default in [('bAutoOpenedRewrite',boolean,False),('ContinuityNoticeStartedAt',real,0)]:h.variable(view,name,typ,default,False,'Narrative Presentation')
 graph(view,'FinishRewritePresentation');graph(view,'StepContinuityNotice');h.compile_blueprint(view,warnings_as_errors=True)
 g=h.edit(view,'ToggleChecklist');entry=g.find_graph_entry_pin();following=list(entry.list_connected_pins());entry.break_pin_links();end=h.setvar(g,entry,'bAutoOpenedRewrite',False)
 for b in following:h.connect(end,b)
 g=h.edit(view,'RefreshChecklist');entry=g.find_graph_entry_pin();following=list(entry.list_connected_pins());entry.break_pin_links();needs=h.all_true(g,h.math(g,'EqualEqual_IntInt',index(g,h.param(g,'Phase')),4),h.not_(g,h.get(g,'bHasRewritten',h.get(g,'ChecklistView'),checklist.generated_class())),h.not_(g,h.get(g,'bChecklistRequested')));yes,no=h.branch(g,entry,needs);end=h.invoke(g,yes,view,'ToggleChecklist').find_then_pin();end=h.setvar(g,end,'bAutoOpenedRewrite',True);end=timer(g,end,'FinishRewritePresentation',2.4);end=merge(g,end,no)
 for b in following:h.connect(end,b)
 g=graph(view,'FinishRewritePresentation');yes,no=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,'bAutoOpenedRewrite'),h.get(g,'bChecklistRequested')));end=h.invoke(g,yes,view,'ToggleChecklist').find_then_pin();h.setvar(g,merge(g,end,no),'bAutoOpenedRewrite',False)
 g=graph(view,'ShowContinuityNotice');end=h.setvar(g,g.find_graph_entry_pin(),'ContinuityNoticeStartedAt',now(g));end=u.visibility(g,end,h.get(g,'ContinuityText'),'HitTestInvisible');end=h.call(g,'/Script/UMG.Widget:SetRenderOpacity',end,h.get(g,'ContinuityText'),InOpacity=0).find_then_pin();timer(g,end,'StepContinuityNotice',.016,True)
 g=graph(view,'StepContinuityNotice');elapsed=h.math(g,'Subtract_DoubleDouble',now(g),h.get(g,'ContinuityNoticeStartedAt'));a=h.math(g,'FMin',h.math(g,'FClamp',h.math(g,'Divide_DoubleDouble',elapsed,.2),0,1),h.math(g,'FClamp',h.math(g,'Divide_DoubleDouble',h.math(g,'Subtract_DoubleDouble',3,elapsed),.25),0,1));end=h.call(g,'/Script/UMG.Widget:SetRenderOpacity',g.find_graph_entry_pin(),h.get(g,'ContinuityText'),InOpacity=a).find_then_pin();translation=h.call(g,'/Script/Engine.KismetMathLibrary:MakeVector2D',X=0,Y=h.math(g,'Multiply_DoubleDouble',h.math(g,'Subtract_DoubleDouble',1,a),-12)).find_result_pin();end=h.call(g,'/Script/UMG.Widget:SetRenderTranslation',end,h.get(g,'ContinuityText'),Translation=translation).find_then_pin();yes,_=h.branch(g,end,h.math(g,'GreaterEqual_DoubleDouble',elapsed,3));h.invoke(g,yes,view,'HideContinuityNotice')
 g=graph(view,'HideContinuityNotice');end=clear(g,g.find_graph_entry_pin(),'StepContinuityNotice');end=clear(g,end,'HideContinuityNotice');u.visibility(g,end,h.get(g,'ContinuityText'),'Collapsed');unreal.find_object(None,view.get_path_name()+':WidgetTree.ContinuityText').get_editor_property('slot').set_position(unreal.Vector2D(0,120));h.layout(view,['RefreshChecklist','ToggleChecklist','FinishRewritePresentation','ShowContinuityNotice','StepContinuityNotice','HideContinuityNotice']);h.save(view);out['saved'].append(view.get_path_name())
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert levels.set_current_level_by_name('L_Whitechapel_Story');existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
 specs=[('C_FutureMessage',future,(2900,5300,0),None,None),('C_NursingRecord',evidence,(3340,460,0),0,'SM_Ledger_Nursing'),('C_FabricatedReport',evidence,(2400,1200,0),1,'SM_Folder_Report')]
 for label,bp,pos,kind,art_name in specs:
  a=existing.get(label)
  if a is None:a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(*pos),unreal.Rotator());a.set_actor_label(label)
  assert '/Maps/L_Whitechapel_Story.' in a.get_path_name()
  if kind is None:a.set_editor_property('InteractionPromptRow','FutureMessagePrompt')
  else:
   a.set_editor_property('EvidenceType',type(a.get_editor_property('EvidenceType')).cast(kind));component=a.get_editor_property('EvidenceMesh');component.set_static_mesh(h.asset('Art/Props/'+art_name+'/'+art_name));component.set_relative_scale3d(unreal.Vector(1,1,1));component.set_relative_location(unreal.Vector(0,0,110 if kind==0 else 120),False,True);component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);component.set_editor_property('can_ever_affect_navigation',False)
  out['actors'].append({'name':label,'path':a.get_path_name(),'position':pos})
 assert levels.save_current_level();out['saved'].append('/Game/Unscripted/Maps/L_Whitechapel_Story');out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
 (repo/'Scripts/C/c30_build.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C30_BUILD '+json.dumps(out))
