"""Real-player E acceptance of both guarded endings, modal cancellation and Retake.

The existing C fixture prepares prior story facts for these isolated ending tests.
No health values, private progression flags, player or enemy assets are changed.
"""
import unreal,asyncio,sys,json,runpy,time,traceback,base64
from pathlib import Path
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
which=globals().get('C_ENDING_CASE','official');assert which in ('official','authentic')
out={'passed':False,'checks':[],'ending_case':which,'asset_saves_performed':False}
def p(o,n):return o.get_editor_property(n)
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
async def key(name):
 if not p(hud,'bFinalConfirmationOpen') and not p(hud,'bEndingPresented'):unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
 await asyncio.sleep(.035);r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':name});assert r['returnValue'];await asyncio.sleep(.085)
async def capture(name):
 folder=repo/'SourceData/C/Previews';folder.mkdir(exist_ok=True)
 r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','Screenshot',{'ref':'w1'});path=folder/('Ending_'+which+'_'+name+'.png');path.write_bytes(base64.b64decode(r['returnValue']['data']));out.setdefault('captures',[]).append(str(path))
async def approach(point):
 assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(*point),pawn.get_actor_rotation()))
 await asyncio.sleep(.08);interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt')
async def run():
 global world,pawn,pc,hud,interaction
 try:
  await asyncio.sleep(.4)
  world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method('GetObjectiveManager');interaction=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class());health=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class());health_before={n:p(health,n) for n in ('MaxHealth','CurrentHealth')}
  unreal.SystemLibrary.execute_console_command(world,'viewmode lit',pc)
  stations={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_FinalChoice').generated_class())};station=stations['C_OfficialRecord' if which=='official' else 'C_AuthenticRecord'];other=next(a for a in stations.values() if a!=station);point=(5060,2600 if which=='official' else 3400,90)
  check('The real Whitechapel character is used',pawn.get_class().get_path_name()=='/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C' and 'L_Whitechapel.' in world.get_path_name())
  check('Both authored stations belong to Story',set(stations)=={'C_OfficialRecord','C_AuthenticRecord'} and all('/Maps/UEDPIE_0_L_Whitechapel_Story.' in a.get_path_name() for a in stations.values()))
  check('Both stations reject FindJack',all(not a.call_method('CanInteract',args=(pawn,)) for a in stations.values()))
  check('An unconfirmed registration method cannot start a final',not station.call_method('ConfirmRegistration',args=(pawn,)) and manager.call_method('GetRegisteredEnding').value==0)
  fixture=runpy.run_path(str(repo/'Scripts/C/prepare_closure_door_play.py'),init_globals={'C_DOOR_SCENARIO':'records_locked'});report=fixture['report']
  check('The existing revelation reaches FinalChoice without selecting an ending',state.call_method('GetCurrentPhase').value==4 and p(manager,'bTruthRevelationComplete') and manager.call_method('GetRegisteredEnding').value==0)
  check('Both stations remain locked until SupervisorDefeated',all(not a.call_method('CanInteract',args=(pawn,)) for a in stations.values()))
  report(7,'OfficialCut');check('A premature registration report remains rejected',manager.call_method('GetRegisteredEnding').value==0)
  report(6);check('Supervisor defeat unlocks access but never selects an ending',manager.call_method('IsSupervisorDefeated') and manager.call_method('GetRegisteredEnding').value==0 and not p(hud,'bEndingPresented'))
  door=fixture['door'];await key('E');await asyncio.sleep(.5);check('The Records door still opens through native E',p(door,'bIsOpen'))
  runpy.run_path(str(repo/'Scripts/C/prepare_endings_play.py'),init_globals={'C_ENDING_STAGE':which});await asyncio.sleep(.08);check('The personal Play helper approaches the intended normal E target',p(interaction,'FocusedActor')==station)
  await key('E');await asyncio.sleep(.7);final=p(hud,'FinalView')
  check('E opens the spatial choice confirmation without registering it',p(hud,'bFinalConfirmationOpen') and manager.call_method('GetRegisteredEnding').value==0 and final.is_in_viewport())
  check('The confirmation names the selected record and permanent consequence',str(p(final,'ConfirmationTitle').get_text())==('ARCHIVE THE OFFICIAL ACCOUNT?' if which=='official' else 'PRESERVE THE AUTHENTIC RECORD?') and 'Retake cannot undo it' in str(p(final,'PermanentWarning').get_text()))
  check('The modal is focused for native keyboard input',final.has_keyboard_focus() or final.has_user_focus(pc))
  probe_class=unreal.load_asset('/Game/Unscripted/UI/Test/BP_UIReadabilityProbe_C');assert probe_class,'The C layout test fixture is required'
  lib=unreal.get_default_object(unreal.GameplayStatics);probe=lib.call_method('BeginDeferredActorSpawnFromClass',args=(world,probe_class.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));probe=lib.call_method('FinishSpawningActor',args=(probe,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
  for name in ('ConfirmationTitle','ConfirmationBody','PermanentWarning','CancelButtonText','ConfirmButtonText'):
   desired,allocated,_,_=probe.call_method('MeasureWidget',args=(p(final,name),));out.setdefault('confirmation_layout',[]).append({'name':name,'desired':[desired.x,desired.y],'allocated':[allocated.x,allocated.y]});check(name+' fits its confirmation text allocation',desired.x<=allocated.x+2 and desired.y<=allocated.y+2)
  charges=p(pawn,'RetakeCharges');await key('R');check('Retake cannot run behind the confirmation',p(pawn,'RetakeCharges')==charges and manager.call_method('GetRegisteredEnding').value==0)
  await capture('Confirmation');await key('BackSpace');check('Backspace cancels and restores the real player control',not p(hud,'bFinalConfirmationOpen') and not pc.is_move_input_ignored() and manager.call_method('GetRegisteredEnding').value==0 and not p(station,'bConsumed'))
  check('Cancellation preserves the existing gameplay HUD',p(hud,'View').is_in_viewport())
  # Preserve an independent movement lock rather than resetting the controller.
  pc.set_ignore_move_input(True);await key('E');await asyncio.sleep(.4);await key('BackSpace');check('Cancel preserves a movement lock owned by another system',pc.is_move_input_ignored() and not p(hud,'bFinalOwnsMoveLock'));pc.set_ignore_move_input(False)
  # Confirming a stale/remote station fails safely and closes the modal.
  await key('E');await asyncio.sleep(.4);assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(5000,3000,90),pawn.get_actor_rotation()));await key('E');check('A stale out-of-range confirmation cannot register a file',not p(hud,'bFinalConfirmationOpen') and not pc.is_move_input_ignored() and manager.call_method('GetRegisteredEnding').value==0)
  await approach(point);await key('E');await asyncio.sleep(.75)
  # Count the published multicast without changing its production owner.
  observer_bp=unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryProgressionObserver_C');observer=unreal.new_object(observer_bp.generated_class());observer.set_editor_property('ObservedManager',manager);observer.call_method('BindObservers')
  await key('E');await asyncio.sleep(.85)
  selected=1 if which=='official' else 2;check('The second deliberate E confirms the selected ending',state.call_method('GetCurrentPhase').value==5 and manager.call_method('GetRegisteredEnding').value==selected and p(hud,'bEndingPresented'))
  check('Only the selected station is consumed exactly once',p(station,'bConsumed') and p(station,'RegistrationCount')==1 and not p(other,'bConsumed') and p(other,'RegistrationCount')==0)
  check('The shared ending dispatcher fires exactly once',p(observer,'ObservedEndingCount')==1 and p(observer,'LastObservedEnding').value==selected)
  check('The terminal presentation replaces the gameplay HUD',final.is_in_viewport() and not p(hud,'View').is_in_viewport() and not p(final,'bConfirmationMode'))
  check('The correct cinematic ending page is displayed',p(final,'OfficialPageFrame').is_visible()==(which=='official') and p(final,'AuthenticPageFrame').is_visible()==(which=='authentic'))
  check('The end screen completes its fade while gameplay is paused',unreal.GameplayStatics.is_game_paused(world) and p(final,'PresentationAlpha')==1 and not p(final,'bPresentationAnimating'))
  if which=='official':check('The newspaper never publishes Jack identity','Jack' not in str(p(final,'NewspaperLeft').get_text())+str(p(final,'NewspaperRight').get_text()) and 'innocent' in str(p(final,'OutcomeConsequence').get_text()))
  else:check('The next-self message preserves Jack innocence and warns of the memory erasure','Jack was innocent' in str(p(final,'MessageBody').get_text()) and 'erase my memory' in str(p(final,'MessageBody').get_text()) and 'previous self' in str(p(final,'MessageSignature').get_text()).lower())
  # Keep FGeometry inside the native test Blueprint; Python receives plain vectors.
  probe_class=unreal.load_asset('/Game/Unscripted/UI/Test/BP_UIReadabilityProbe_C')
  if probe_class:
   names=['OutcomeNumber','OutcomeEyebrow','OutcomeTitle','OutcomeConsequence','ArchiveSeal','EndingQuote','EndingFooter']+(['NewspaperMasthead','NewspaperDateline','NewspaperHeadline','NewspaperDeck','NewspaperLeft','NewspaperRight','NewspaperFootnote'] if which=='official' else ['MessageChannel','MessageTitle','MessageBody','MessageWarning','MessagePromise','MessageSignature'])
   for name in names:
    desired,allocated,_,_=probe.call_method('MeasureWidget',args=(p(final,name),));out.setdefault('text_layout',[]).append({'name':name,'desired':[desired.x,desired.y],'allocated':[allocated.x,allocated.y]});check(name+' fits its final-screen text allocation',desired.x<=allocated.x+2 and desired.y<=allocated.y+2)
  await capture('Final')
  before=(pawn.get_actor_location(),p(pawn,'RetakeCharges'),manager.call_method('GetRegisteredEnding').value)
  for k in ('R','E','F','Tab','BackSpace'):await key(k)
  other.call_method('Interact',args=(pawn,));report(7,'AuthenticRecord' if which=='official' else 'OfficialCut');report(6)
  check('Retake and repeated input cannot undo or replace the final',pawn.get_actor_location().distance(before[0])<.01 and p(pawn,'RetakeCharges')==before[1] and manager.call_method('GetRegisteredEnding').value==selected and p(station,'RegistrationCount')==1 and p(observer,'ObservedEndingCount')==1)
  check('The second station remains unusable in GameEnded',not other.call_method('CanInteract',args=(pawn,)) and not other.call_method('ConfirmRegistration',args=(pawn,)))
  check('No health fixture or foreign gameplay state was substituted',health_before=={n:p(health,n) for n in ('MaxHealth','CurrentHealth')})
  out['external_dependencies']=['A: the real pawn does not implement SetRetakeBlocked/ClearRetakeHistory yet. C sends those messages; the terminal UI also blocks real input, disables the pawn input component and pauses gameplay. Persistent narrative facts reject further registration.','B: a natural boss/escort run still requires B integration. The existing C fixture prepares preceding story facts for isolated ending tests; C-30 real-E acceptance runs separately.']
  out['passed']=True
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:out['check_count']=len(out['checks']);(repo/('Scripts/C/ending_'+which+'_validation.json')).write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_ENDING_PLAY_TEST '+json.dumps(out))
c_endings_play_loop=EditorEventLoopManager();c_endings_play_loop.__enter__();c_endings_play_task=c_endings_play_loop.loop.create_task(run())
