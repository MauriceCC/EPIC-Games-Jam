"""Run C-30 in Whitechapel PIE with real E input and the actual A character.

Only missing B reports (JackFound/JackReachedRefuge) are simulated. The real
side door, future message, both evidence actors and dialogue completion are used.
No health fixture, private-state writes, final registration or asset save occurs.
"""
import unreal,sys,asyncio,time,json,traceback,base64
from pathlib import Path
sys.dont_write_bytecode=True
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
order=globals().get('C30_EVIDENCE_ORDER','nursing_first')
out={'passed':False,'checks':[],'rows':[],'rewrite_frames':[],'evidence_order':order,'asset_saves_performed':False}
def p(o,n):return o.get_editor_property(n)
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
def phase():return state.call_method('GetCurrentPhase').value
def focus():unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
async def key(name):
 focus();await asyncio.sleep(.035);r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':name});assert r['returnValue'];await asyncio.sleep(.055)
async def capture(label):
 await asyncio.sleep(.04)
 r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','Screenshot',{'ref':'w1'})
 path=repo/('SourceData/C/Previews/C30_'+order+'_'+label+'.png');path.write_bytes(base64.b64decode(r['returnValue']['data']));out.setdefault('captures',[]).append(str(path))
async def finish_dialogue():
 for _ in range(90):
  if not p(manager,'bDialogueActive'):return
  row=str(p(manager,'CurrentDialogueRow'))
  if not out['rows'] or out['rows'][-1]!=row:out['rows'].append(row)
  await key('E')
 raise AssertionError('Dialogue did not finish within the bounded E input sequence')
def report(index,param=''):
 source.set_editor_property('EventToReport',event_type.cast(index));source.set_editor_property('EventParam',param);source.call_method('ReportConfiguredEvent')
async def approach(point):
 assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(*point),pawn.get_actor_rotation()))
 await asyncio.sleep(.1);interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt');focus()
async def run():
 global world,pawn,hud,state,manager,interaction,source,event_type
 try:
  await asyncio.sleep(.4)
  world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();view=p(hud,'View');state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method('GetObjectiveManager');interaction=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class())
  unreal.SystemLibrary.execute_console_command(world,'viewmode lit',pc)
  check('Integrated Whitechapel uses the real player',pawn.get_class().get_path_name()=='/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C' and 'L_Whitechapel.' in world.get_path_name())
  check('The run starts in FindJack',phase()==0)
  health=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class());health_before={n:p(health,n) for n in ('MaxHealth','CurrentHealth')}
  bp=unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C');s=unreal.get_default_object(unreal.GameplayStatics);source=s.call_method('BeginDeferredActorSpawnFromClass',args=(world,bp.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));source=s.call_method('FinishSpawningActor',args=(source,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));event_type=type(p(source,'EventToReport'))
  future=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_FutureMessage_C').generated_class())[0]
  evidences={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Evidence').generated_class())}
  check('Future message and both records are real Story actors',set(evidences)=={'C_NursingRecord','C_FabricatedReport'} and all('/Maps/UEDPIE_0_L_Whitechapel_Story.' in a.get_path_name() for a in [future,*evidences.values()]))
  check('No evidence or future interaction is available before Jack',not future.call_method('CanInteract',args=(pawn,)) and all(not a.call_method('CanInteract',args=(pawn,)) for a in evidences.values()))
  report(4);report(3,'NursingRecord');report(6);check('Early truth, evidence and boss reports cannot advance the story',phase()==0 and not p(manager,'bEvidenceFound') and not manager.call_method('IsSupervisorDefeated'))
  await finish_dialogue();report(0);await finish_dialogue()
  check('Finding Jack does not play the future message remotely',phase()==1 and not p(manager,'bFutureMessageQueued') and 'FutureMessage_01' not in out['rows'])
  await approach((3040,5300,90));check('The future message is the focused E interaction',p(interaction,'FocusedActor')==future)
  await key('E');check('Native E starts the existing future-self line',str(p(manager,'CurrentDialogueRow'))=='FutureMessage_01' and p(future,'bConsumed'))
  await key('E');await capture('FutureMessage');await finish_dialogue()
  check('Completing the future line records it once without changing phase',p(manager,'bFutureMessageRead') and p(future,'InteractionCount')==1 and phase()==1)
  await key('E');check('A repeated future interaction is rejected',p(future,'InteractionCount')==1 and not p(manager,'bDialogueActive'))
  await approach((2735,4780,90));side=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Door').generated_class()) if a.get_actor_label()=='C_SideDoor');await key('E');await asyncio.sleep(.45)
  check('The real side door supplies EscapeRouteOpened',p(side,'bIsOpen') and phase()==2)
  check('Evidence remains unavailable before Jack reaches the refuge',all(not a.call_method('CanInteract',args=(pawn,)) for a in evidences.values()))
  await approach((3000,800,90));report(2);check('The missing B refuge report enables DiscoverTruth only',phase()==3 and not p(manager,'bTruthRevelationStarted'))
  names=['C_NursingRecord','C_FabricatedReport'];names=names[::-1] if order=='report_first' else names
  positions={'C_NursingRecord':(3460,460,90),'C_FabricatedReport':(2520,1200,90)}
  for number,name in enumerate(names):
   record=evidences[name];await approach(positions[name]);check(name+' is focused for E',p(interaction,'FocusedActor')==record)
   await key('E');check(name+' opens its existing document view',p(record,'bConsumed') and p(hud,'bDocumentOpen') and p(manager,'bDocumentActive'))
   check(name+' does not advance while the document is still open',phase()==3 and not p(manager,'bTruthRevelationStarted'))
   # Even an external report with both records must not bypass the final line.
   report(4);check(name+' cannot be used to skip the revelation',phase()==3)
   if number==1:await capture('SecondEvidence')
   await key('E')
   check(name+' closes with E',not p(hud,'bDocumentOpen') and not p(manager,'bDocumentActive'))
   check(name+' cannot be consumed twice',not record.call_method('CanInteract',args=(pawn,)) and p(record,'InteractionCount')==1)
   if number==0:
    check('One evidence cannot start the Supervisor revelation',phase()==3 and not p(manager,'bDialogueActive') and not p(manager,'bTruthRevelationStarted'))
    token='NursingRecord' if name=='C_NursingRecord' else 'FabricatedReport';report(3,token);report(4);check('Duplicate evidence does not replace the missing record',phase()==3 and not p(manager,'bTruthRevelationStarted'))
  check('Both read documents start the Supervisor conversation in DiscoverTruth',phase()==3 and str(p(manager,'CurrentDialogueRow'))=='Truth_01' and p(manager,'bTruthRevelationStarted'))
  report(4);check('TruthRevealed still cannot bypass an unfinished Supervisor conversation',phase()==3 and not p(manager,'bTruthRevelationComplete'))
  for expected in ('Truth_01','Truth_02','Truth_03','Truth_04','Truth_05'):
   check(expected+' appears in the authored order',str(p(manager,'CurrentDialogueRow'))==expected and phase()==3)
   out['rows'].append(expected);await key('E')
   check(expected+' is fully revealed before advancing',str(p(p(view,'DialogueView'),'BodyText').get_text())==str(p(p(view,'DialogueView'),'FullLine')) and phase()==3)
   if expected=='Truth_05':await capture('Supervisor')
   await key('E')
  check('Only the final confirmed Supervisor line reaches FinalChoice',phase()==4 and p(manager,'bTruthRevelationComplete') and p(manager,'bEvidenceFound') and p(manager,'bFalseReportFound') and p(manager,'bJackSafe'))
  check('The existing Correction_Order follows the revelation',str(p(manager,'CurrentDialogueRow'))=='Correction_Order')
  checklist=p(view,'ChecklistView');notice=p(view,'ContinuityText')
  check('The closed dossier opens automatically for its visible rewrite',p(view,'bChecklistRequested') and p(checklist,'bRewriteAnimating'))
  check('The existing continuity story notice is reported',p(manager,'bTruthNoticeReported') and notice.is_visible())
  for _ in range(25):
   out['rewrite_frames'].append({'time':unreal.GameplayStatics.get_real_time_seconds(world),'drawer_alpha':p(view,'ChecklistAlpha'),'rewrite_step':p(checklist,'RewriteStep'),'notice_alpha':notice.get_render_opacity(),'notice_y':notice.get_editor_property('render_transform').translation.y});await asyncio.sleep(.025)
  await capture('RewriteAndNotice')
  check('The notice uses a real intermediate fade and slide',any(0<f['notice_alpha']<1 and f['notice_y']<0 for f in out['rewrite_frames']))
  await asyncio.sleep(.4)
  check('The old completed directives survive the rewrite',p(checklist,'bHasRewritten') and p(checklist,'Strike0').is_visible() and p(checklist,'Strike1').is_visible())
  check('The new orders explicitly frame innocent Jack and hide his identity','Frame Jack' in str(p(checklist,'ItemText2').get_text()) and 'without revealing his identity' in str(p(checklist,'ItemText3').get_text()))
  await finish_dialogue();reported_at=p(view,'ContinuityNoticeStartedAt');report(4);report(2);report(3,'NursingRecord');report(0)
  check('Duplicate or stale story reports cannot replay the reveal or notice',phase()==4 and not p(manager,'bDialogueActive') and p(view,'ContinuityNoticeStartedAt')==reported_at)
  await asyncio.sleep(2.5)
  check('The automatically opened dossier returns to its compact state',not p(view,'bChecklistRequested') and p(view,'ChecklistDrawer').get_visibility()==unreal.SlateVisibility.COLLAPSED)
  check('The non-blocking continuity notice finishes cleanly',not notice.is_visible())
  await key('Tab');await asyncio.sleep(.3);check('Tab can reopen the revised dossier',p(view,'bChecklistRequested') and 'Frame Jack' in str(p(checklist,'ItemText2').get_text()));await key('Tab')
  check('C-30 selects no ending and leaves Supervisor defeat pending',phase()==4 and not manager.call_method('IsSupervisorDefeated') and p(manager,'Ending').value==0)
  await key('R');check('Retake cannot erase collected evidence or the revelation',phase()==4 and p(manager,'bTruthRevelationComplete') and all(p(a,'bConsumed') for a in evidences.values()))
  check('The HUD uses unchanged real health data',health_before=={n:p(health,n) for n in ('MaxHealth','CurrentHealth')})
  out['passed']=True
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:
  out['check_count']=len(out['checks']);(repo/('Scripts/C/c30_'+order+'_validation.json')).write_text(json.dumps(out,indent=2),encoding='utf-8');print('C30_PLAY_TEST '+json.dumps({k:v for k,v in out.items() if k!='rewrite_frames'}))
c30_loop=EditorEventLoopManager();c30_loop.__enter__();c30_task=c30_loop.loop.create_task(run())
