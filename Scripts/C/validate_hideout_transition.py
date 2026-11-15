"""Supplement the live visual check with real-player controlled-transition assertions."""
import unreal,sys,json,asyncio,time,traceback
from pathlib import Path
sys.dont_write_bytecode=True
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
OUT={'passed':False,'checks':[],'entry_frames':[],'exit_frames':[],'asset_saves_performed':False}
def p(o,n):return o.get_editor_property(n)
def check(name,value):OUT['checks'].append({'name':name,'passed':bool(value)});assert value,name
def focus():unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
async def press(key):
 focus();await asyncio.sleep(.04)
 result=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':key});assert result['returnValue'],key
async def wait_for(predicate,seconds=12,frames=None):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  if frames is not None:
   v=pawn.get_velocity();frames.append({'time':unreal.GameplayStatics.get_time_seconds(world),'position':list(pawn.get_actor_location().to_tuple()),'speed_xy':(v.x*v.x+v.y*v.y)**.5,'mesh_hidden':p(mesh,'hidden_in_game'),'occupied':p(hide,'bOccupied'),'transitioning':p(hide,'bTransitioning'),'stage':p(hide,'MotionStage'),'veil':p(view,'HideoutTransitionVeil').get_render_opacity(),'locomotion_state':p(locomotion,'CurrentState')})
  if predicate():return
  await asyncio.sleep(.035)
 raise AssertionError('Wardrobe transition did not reach the expected state before the timeout')
async def test():
 global world,pawn,mesh,hide,view,locomotion
 world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();view=p(hud,'View');manager=unreal.GameplayStatics.get_game_state(world).call_method('GetObjectiveManager')
 check('The integrated real A player is used',pawn.get_class().get_path_name()=='/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C')
 for _ in range(40):
  if not p(manager,'bDialogueActive'):break
  hud.call_method('UseNarrativeInteraction')
 hide=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Hideout').generated_class())[0]
 mesh=pawn.get_component_by_class(unreal.SkeletalMeshComponent);capsule=pawn.get_component_by_class(unreal.CapsuleComponent)
 locomotion=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Art/Characters/Shared/BP_LocomotionAnim').generated_class())
 interact=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class())
 start=p(hide,'ExitPoint').get_world_location();pawn.set_actor_location(start,False,True)
 await asyncio.sleep(.12);interact.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt')
 OUT['initial_position']=list(pawn.get_actor_location().to_tuple());OUT['collision_before']=str(capsule.get_collision_enabled());OUT['hidden_before']=p(mesh,'hidden_in_game');OUT['health_before']={n:p(pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class()),n) for n in ('MaxHealth','CurrentHealth')}
 check('The real interaction component focuses the wardrobe',p(interact,'FocusedActor')==hide)
 check('Wardrobe accepts a living local player',hide.call_method('CanInteract',args=(pawn,)))
 await press('E');await wait_for(lambda:p(hide,'bTransitioning'),2)
 check('E starts a controlled entry instead of setting hidden immediately',p(hide,'Occupant')==pawn and not p(hide,'bOccupied'))
 await press('E')
 await wait_for(lambda:p(hide,'bOccupied') and not p(hide,'bTransitioning'),12,OUT['entry_frames'])
 check('Entry reaches the hidden state',p(hide,'bOccupied') and p(mesh,'hidden_in_game'))
 check('Hidden state displays the authored leave prompt',str(p(hide,'InteractionPromptRow'))=='HideoutLeavePrompt' and 'leave hideout' in str(p(view,'InteractionText').get_text()).lower())
 check('Entry never supplies automatic walking velocity',not any(f['speed_xy']>5 for f in OUT['entry_frames']))
 check('Entry uses no intermediate route toward the NPC',not p(hide,'MotionWaypoints'))
 check('The controlled reposition settles at the collision-safe dock',pawn.get_actor_location().distance(p(hide,'EntryDock').get_world_location())<14)
 check('The hidden body is no longer visible beside the wardrobe',p(mesh,'hidden_in_game'))
 check('The existing stealth component is marked hidden',p(pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Enemies/BP_StealthComponent').generated_class()),'bIsHidden'))
 check('Capsule collision is preserved while hidden',str(capsule.get_collision_enabled())==OUT['collision_before'])
 check('The transition veil clears after entry',not p(view,'HideoutTransitionVeil').is_visible() and p(view,'HideoutTransitionVeil').get_render_opacity()==0)
 check('Movement is locked while hidden',pc.is_move_input_ignored())
 charges=p(pawn,'RetakeCharges');ready=p(pawn,'bCutReady');await press('R');await press('F');await asyncio.sleep(.12)
 check('Retake and Frame Cut input cannot fire while hidden',p(pawn,'RetakeCharges')==charges and p(pawn,'bCutReady')==ready)
 await press('Tab');await asyncio.sleep(.3);check('The animated dossier still opens while hidden',p(view,'bChecklistRequested'))
 await press('Tab');await asyncio.sleep(.3);check('The animated dossier closes while hidden',not p(view,'bChecklistRequested'))
 await press('E');await wait_for(lambda:p(hide,'bTransitioning'),2)
 await wait_for(lambda:not p(hide,'bOccupied') and not p(hide,'bTransitioning'),12,OUT['exit_frames'])
 check('Exit restores the original mesh visibility',p(mesh,'hidden_in_game')==OUT['hidden_before'])
 check('Exit never supplies automatic walking velocity',not any(f['speed_xy']>5 for f in OUT['exit_frames']))
 check('Exit finishes in front of the wardrobe',pawn.get_actor_location().distance(p(hide,'ExitPoint').get_world_location())<14)
 check('Exit releases only the movement lock it owns',not pc.is_move_input_ignored() and not p(hide,'bOwnsMovementLock'))
 check('Capsule collision is restored unchanged',str(capsule.get_collision_enabled())==OUT['collision_before'])
 check('Focus is unlocked after exit',p(interact,'LockedFocusActor') is None)
 check('Exit leaves no black overlay',not p(view,'HideoutTransitionVeil').is_visible())
 check('Exit restores the authored enter prompt',str(p(hide,'InteractionPromptRow'))=='HideoutEnterPrompt' and 'enter hideout' in str(p(view,'InteractionText').get_text()).lower())
 await press('R');await asyncio.sleep(.12);check('The real Retake ability is usable after exit',p(pawn,'RetakeCharges')==charges-1)
 # Repeat entry and exercise the existing checkpoint/reset cleanup path.
 pawn.set_actor_location(start,False,True);await asyncio.sleep(.1);interact.call_method('RefreshFocus');await press('E')
 await wait_for(lambda:p(hide,'bOccupied') and not p(hide,'bTransitioning'))
 hide.call_method('ResetOccupancy');await asyncio.sleep(.3)
 check('Checkpoint cleanup restores a hidden player safely',not p(hide,'bOccupied') and not p(mesh,'hidden_in_game') and not pc.is_move_input_ignored())
 check('Checkpoint cleanup clears focus and veil',p(interact,'LockedFocusActor') is None and not p(view,'HideoutTransitionVeil').is_visible())
 # Approach from the open front corner and cancel an in-progress entry.
 assert pawn.call_method('K2_TeleportTo',args=(start+unreal.Vector(-110,0,0),pawn.get_actor_rotation()));await asyncio.sleep(.3);interact.call_method('RefreshFocus');await press('E')
 await wait_for(lambda:p(hide,'bTransitioning'),2);await asyncio.sleep(.12)
 hide.call_method('ResetOccupancy');await asyncio.sleep(.3)
 check('Interrupted entry restores movement and mesh visibility',not p(hide,'bTransitioning') and not p(mesh,'hidden_in_game') and not pc.is_move_input_ignored())
 check('Interrupted entry clears the focus lock and fade',p(interact,'LockedFocusActor') is None and not p(view,'HideoutTransitionVeil').is_visible())
 assert pawn.call_method('K2_TeleportTo',args=(start+unreal.Vector(-110,0,0),pawn.get_actor_rotation()));await asyncio.sleep(.3);interact.call_method('RefreshFocus');await press('E')
 await wait_for(lambda:p(hide,'bOccupied') and not p(hide,'bTransitioning'))
 check('An oblique interaction settles hidden without following a route',p(mesh,'hidden_in_game') and pawn.get_actor_location().distance(p(hide,'EntryDock').get_world_location())<14 and not p(hide,'MotionWaypoints'))
 # A movement lock acquired by another owner must survive C cleanup.
 pc.set_ignore_move_input(True);hide.call_method('ResetOccupancy');await asyncio.sleep(.05)
 check('Cleanup preserves an independent movement lock',pc.is_move_input_ignored() and not p(hide,'bOwnsMovementLock'))
 pc.set_ignore_move_input(False)
 check('Releasing the independent lock restores normal control',not pc.is_move_input_ignored())
 check('Hideout interaction does not change the narrative phase',unreal.GameplayStatics.get_game_state(world).call_method('GetCurrentPhase').value==0)
 health=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class())
 check('No health values are replaced by the transition',OUT['health_before']=={n:p(health,n) for n in ('MaxHealth','CurrentHealth')})
 OUT['passed']=True
async def guarded():
 try:await test()
 except Exception:OUT['error']=traceback.format_exc();unreal.log_error(OUT['error'])
 finally:
  OUT['check_count']=len(OUT['checks']);(repo/'Scripts/C/hideout_transition_validation.json').write_text(json.dumps(OUT,indent=2),encoding='utf-8');print('C_HIDEOUT_TRANSITION_TEST '+json.dumps({k:v for k,v in OUT.items() if not k.endswith('_frames')}))
c_hideout_test_loop=EditorEventLoopManager();c_hideout_test_loop.__enter__();c_hideout_test_task=c_hideout_test_loop.loop.create_task(guarded())
