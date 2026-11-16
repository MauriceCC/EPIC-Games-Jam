"""Supplement live keyboard/visual acceptance with C-only PIE fault injection.

Uses the real Whitechapel player. Marker and timer changes are runtime-only;
never saves assets, replaces health, or edits the NPC or another division.
"""
import unreal,sys,asyncio,json,time,traceback
from pathlib import Path
sys.dont_write_bytecode=True
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
out={'passed':False,'checks':[],'asset_saves_performed':False}
def p(o,n):return o.get_editor_property(n)
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
async def key(name):
 unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
 await asyncio.sleep(.05);result=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':name});assert result['returnValue'];await asyncio.sleep(.05)
async def settled():
 end=time.monotonic()+2.5
 while p(hide,'bTransitioning'):
  assert time.monotonic()<end,'Transition exceeded its real-time recovery deadline'
  await asyncio.sleep(.02)
 await asyncio.sleep(.3)
def released():return not p(hide,'bOccupied') and not p(hide,'bTransitioning') and not p(hide,'bOwnsMovementLock') and not p(mesh,'hidden_in_game') and not pc.is_move_input_ignored() and not p(view,'HideoutTransitionVeil').is_visible()
async def run():
 global hide,pawn,pc,mesh,view
 dock=exit_marker=None
 try:
  world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();view=p(hud,'View');mesh=pawn.get_component_by_class(unreal.SkeletalMeshComponent)
  check('Fault tests use the real A player',pawn.get_class().get_path_name()=='/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C')
  manager=unreal.GameplayStatics.get_game_state(world).call_method('GetObjectiveManager')
  for _ in range(40):
   if not p(manager,'bDialogueActive'):break
   hud.call_method('UseNarrativeInteraction')
  hide=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Hideout').generated_class())[0]
  dock=p(hide,'EntryDock');exit_marker=p(hide,'ExitPoint');dock_position=dock.get_world_location();exit_position=exit_marker.get_world_location()
  health=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class());health_before={n:p(health,n) for n in ('CurrentHealth','MaxHealth')}
  collision_before=str(pawn.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled())
  interaction=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class())
  hide.call_method('ResetOccupancy');await asyncio.sleep(.3)
  pawn.set_actor_location(exit_position,False,True);interaction.call_method('RefreshFocus')
  # This is the live position of the existing NPC, read without modifying it.
  npc=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_name()=='SkeletalMeshActor_2')
  blocked=npc.get_actor_location()+unreal.Vector(0,0,90)
  dock.set_world_location(blocked,False,True)
  before=pawn.get_actor_location();await key('E');await settled()
  check('Blocked entry restores visibility and input instead of walking',released())
  check('Blocked entry preserves the safe source position',pawn.get_actor_location().distance(before)<12)
  dock.set_world_location(dock_position,False,True);await asyncio.sleep(.3);interaction.call_method('RefreshFocus')
  await key('E');await settled();check('Valid entry remains available after a failed entry',p(hide,'bOccupied') and p(mesh,'hidden_in_game'))
  exit_marker.set_world_location(blocked,False,True)
  await key('E');await settled()
  check('Blocked exit uses a safe fallback and restores control',released() and pawn.get_actor_location().distance(before)<12)
  exit_marker.set_world_location(exit_position,False,True)
  # Simulate losing the fade update; the independent one-shot watchdog must free it.
  interaction.call_method('RefreshFocus');await asyncio.sleep(.3);await key('E')
  check('A transition is active before interrupting its update',p(hide,'bTransitioning'))
  unreal.get_default_object(unreal.SystemLibrary).call_method('K2_ClearTimer',args=(hide,'UpdateHideoutTransition'))
  started=time.monotonic();await settled()
  check('Independent watchdog recovers a stalled transition',released() and time.monotonic()-started<2.1)
  await asyncio.sleep(.3);interaction.call_method('RefreshFocus');await key('E');hide.call_method('ResetOccupancy');await asyncio.sleep(.35)
  check('Explicit cancellation cannot leave hidden visibility, focus or input locked',released() and p(interaction,'LockedFocusActor') is None)
  await asyncio.sleep(.3);interaction.call_method('RefreshFocus');await key('E');await settled();await key('Tab');await asyncio.sleep(.3)
  check('The dossier still opens while hidden',p(view,'bChecklistRequested'))
  await key('Tab');await asyncio.sleep(.3);check('The dossier still closes while hidden',not p(view,'bChecklistRequested'))
  charges=p(pawn,'RetakeCharges');ready=p(pawn,'bCutReady');await key('R');await key('F')
  check('Hidden input cannot activate either temporal ability',p(pawn,'RetakeCharges')==charges and p(pawn,'bCutReady')==ready)
  pc.set_ignore_move_input(True);hide.call_method('ResetOccupancy');await asyncio.sleep(.05)
  check('Cleanup preserves an independently acquired movement lock',pc.is_move_input_ignored() and not p(hide,'bOwnsMovementLock'))
  pc.set_ignore_move_input(False)
  check('Releasing the independent lock restores input',released())
  check('No health state is invented or changed',health_before=={n:p(health,n) for n in ('CurrentHealth','MaxHealth')})
  check('Capsule collision remains unchanged',str(pawn.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled())==collision_before)
  out['passed']=True
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:
  if dock is not None:dock.set_world_location(dock_position,False,True)
  if exit_marker is not None:exit_marker.set_world_location(exit_position,False,True)
  if 'hide' in globals():hide.call_method('ResetOccupancy')
  out['check_count']=len(out['checks']);(repo/'Scripts/C/hideout_recovery_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_HIDEOUT_RECOVERY '+json.dumps(out))
c_recovery_loop=EditorEventLoopManager();c_recovery_loop.__enter__();c_recovery_task=c_recovery_loop.loop.create_task(run())
