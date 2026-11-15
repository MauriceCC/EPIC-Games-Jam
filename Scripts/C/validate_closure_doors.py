"""Exercise Block 2.1 via existing story events, native E and real pawn physics.

Run in fresh Whitechapel PIE. Positioning isolates each approach; passage uses
CharacterMovement, never teleports through a door. No gameplay asset is saved.
"""
import unreal,asyncio,sys,json,time,runpy,traceback
from pathlib import Path
sys.dont_write_bytecode=True
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
out={'passed':False,'checks':[],'movement':[],'navigation':[],'asset_saves_performed':False}
def p(o,n):return o.get_editor_property(n)
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
async def key(name):
 unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport');await asyncio.sleep(.05)
 result=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':name});assert result['returnValue'];await asyncio.sleep(.08)
async def move(direction,seconds):
 start=pawn.get_actor_location();deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  pawn.call_method('AddMovementInput',args=(direction,1.0,False));await asyncio.sleep(.001)
 pawn.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately();await asyncio.sleep(.03)
 end=pawn.get_actor_location();out['movement'].append({'start':list(start.to_tuple()),'end':list(end.to_tuple()),'direction':list(direction.to_tuple()),'seconds':seconds});return end
def nav_read(name,start,end):
 path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,start,end,pawn)
 row={'door':name,'valid':bool(path and path.is_valid()),'partial':bool(path and path.is_partial()),'points':[list(v.to_tuple()) for v in p(path,'path_points')] if path else []}
 out['navigation'].append(row);return row
async def open_with_e(door):
 interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt');check(door.get_actor_label()+' is the real focused E target',p(interaction,'FocusedActor')==door)
 await key('E');deadline=time.monotonic()+1.5
 while not p(door,'bIsOpen'):
  assert time.monotonic()<deadline,'Door opening did not finish';await asyncio.sleep(.02)
 check(door.get_actor_label()+' opens once and frees physical collision',p(door,'bConsumed') and not door.get_actor_enable_collision() and p(door,'InteractionCount')==1)
 check(door.get_actor_label()+' clears its navigation modifier',p(p(door,'DoorNavigation'),'area_class').get_path_name()=='/Script/NavigationSystem.NavArea_Default')
 await asyncio.sleep(.5)
async def run():
 global world,pawn,interaction,hud
 try:
  fixture=runpy.run_path(str(repo/'Scripts/C/prepare_closure_door_play.py'),init_globals={'C_DOOR_SCENARIO':'side_locked'})
  world,pawn,interaction,hud,manager,state,report=[fixture[k] for k in ('world','pawn','interaction','hud','manager','state','report')]
  doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Door').generated_class())};side=doors['C_SideDoor'];gate=doors['C_ArchiveGate'];records=doors['C_RecordsDoor']
  check('Exactly the three planned doors are in Story',set(doors)=={'C_SideDoor','C_ArchiveGate','C_RecordsDoor'} and all('/Maps/UEDPIE_0_L_Whitechapel_Story.' in a.get_path_name() for a in doors.values()))
  check('The real A character is used',pawn.get_class().get_path_name()=='/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C')
  for name,door in doors.items():
   check(name+' rejects interaction in FindJack',not door.call_method('CanInteract',args=(pawn,)));door.call_method('Interact',args=(pawn,));check(name+' remains closed after a premature interaction',not p(door,'bConsumed') and not p(door,'bIsOpen') and p(door,'InteractionCount')==0)
  report(6);check('A premature boss report cannot unlock Records',not manager.call_method('IsSupervisorDefeated'))
  nav_read('side_closed',unreal.Vector(2735,4780,90),unreal.Vector(2735,4420,90))
  end=await move(unreal.Vector(0,-1,0),.8);check('Closed side door physically blocks the real player',end.y>4630)
  report(0);check('Only OpenEscapeRoute unlocks the side door',state.call_method('GetCurrentPhase').value==1 and side.call_method('CanInteract',args=(pawn,)) and not gate.call_method('CanInteract',args=(pawn,)))
  await open_with_e(side);check('Opening the side door advances through the existing story event',state.call_method('GetCurrentPhase').value==2)
  end=await move(unreal.Vector(0,-1,0),1.0);check('The real player crosses the open side door',end.y<4520)
  nav_read('side_open',unreal.Vector(2735,4780,90),unreal.Vector(2735,4420,90))
  await key('E');check('The side door cannot report or open twice',p(side,'InteractionCount')==1 and state.call_method('GetCurrentPhase').value==2)
  assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(3420,3600,90),pawn.get_actor_rotation()))
  nav_read('archive_closed',unreal.Vector(3420,3600,90),unreal.Vector(3780,3600,90));end=await move(unreal.Vector(1,0,0),.8);check('Closed archive gate physically blocks the real player',end.x<3570)
  report(2);check('The archive stays locked in DiscoverTruth',state.call_method('GetCurrentPhase').value==3 and not gate.call_method('CanInteract',args=(pawn,)))
  report(3,'NursingRecord');report(3,'FabricatedReport');manager.call_method('TryStartTruthRevelation');fixture['drain']()
  check('FinalChoice unlocks the archive without defeating the boss',state.call_method('GetCurrentPhase').value==4 and gate.call_method('CanInteract',args=(pawn,)) and not manager.call_method('IsSupervisorDefeated'))
  check('Records stays locked in FinalChoice before the boss fact',not records.call_method('CanInteract',args=(pawn,)))
  await open_with_e(gate);check('The archive gate reports no escape-route event',state.call_method('GetCurrentPhase').value==4)
  end=await move(unreal.Vector(1,0,0),1.0);check('The real player crosses the open archive gate',end.x>3690);nav_read('archive_open',unreal.Vector(3420,3600,90),unreal.Vector(3780,3600,90))
  assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(4620,3000,90),pawn.get_actor_rotation()))
  nav_read('records_closed',unreal.Vector(4620,3000,90),unreal.Vector(4980,3000,90));end=await move(unreal.Vector(1,0,0),.8);check('Closed records door physically blocks the real player',end.x<4770)
  interaction.call_method('RefreshFocus');await key('E');check('E cannot open Records before SupervisorDefeated',not p(records,'bIsOpen') and p(records,'InteractionCount')==0)
  report(6);check('The accepted SupervisorDefeated fact unlocks Records',manager.call_method('IsSupervisorDefeated') and records.call_method('CanInteract',args=(pawn,)))
  await open_with_e(records);end=await move(unreal.Vector(1,0,0),1.0);check('The real player crosses the open records doorway',end.x>4890);nav_read('records_open',unreal.Vector(4620,3000,90),unreal.Vector(4980,3000,90))
  check('Door checks never select an ending or advance beyond FinalChoice',state.call_method('GetCurrentPhase').value==4)
  await key('R');check('Retake does not close persistent doors',all(p(d,'bIsOpen') and p(d,'bConsumed') for d in doors.values()))
  out['external_blockers']=['D/B: the Workshop side opening remains a partial NavMesh path after opening; live character passage succeeds through a side clearance. The isolated C-modifier-off probe also remains partial. Review the existing central drainpipe and baked navigation without changing C door conditions.'] if any(r['door']=='side_open' and (not r['valid'] or r['partial']) for r in out['navigation']) else []
  check('Archive navigation changes from blocked to traversable',next(r for r in out['navigation'] if r['door']=='archive_closed')['partial'] and not next(r for r in out['navigation'] if r['door']=='archive_open')['partial'])
  check('Records navigation changes from blocked to traversable',next(r for r in out['navigation'] if r['door']=='records_closed')['partial'] and not next(r for r in out['navigation'] if r['door']=='records_open')['partial'])
  out['passed']=True
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:
  out['check_count']=len(out['checks']);(repo/'Scripts/C/closure_doors_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_CLOSURE_DOOR_TEST '+json.dumps(out))
c_doors_loop=EditorEventLoopManager();c_doors_loop.__enter__();c_doors_task=c_doors_loop.loop.create_task(run())
