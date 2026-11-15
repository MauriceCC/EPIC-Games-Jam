"""Prepare a runtime-only Block 2.1 check with the real player in Whitechapel.

Set C_DOOR_SCENARIO to side_locked, side_open, archive_locked, archive_open,
records_locked or records_open. Restart PIE before selecting another scenario.
Only existing story events are reported; no private progression state is changed.
"""
import unreal,json
from pathlib import Path
scenario=globals().get('C_DOOR_SCENARIO','side_locked')
assert scenario in ('side_locked','side_open','archive_locked','archive_open','records_locked','records_open')
world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];assert 'L_Whitechapel.' in world.get_path_name()
pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method('GetObjectiveManager')
assert state.call_method('GetCurrentPhase').value==0,'Use a fresh PIE session for each scenario'
source_bp=unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C')
statics=unreal.get_default_object(unreal.GameplayStatics);source=statics.call_method('BeginDeferredActorSpawnFromClass',args=(world,source_bp.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));source=statics.call_method('FinishSpawningActor',args=(source,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
event_type=type(source.get_editor_property('EventToReport'))
def drain():
 for _ in range(100):
  if not manager.get_editor_property('bDialogueActive'):break
  hud.call_method('UseNarrativeInteraction')
def report(index,param=''):
 source.set_editor_property('EventToReport',event_type.cast(index));source.set_editor_property('EventParam',param);source.call_method('ReportConfiguredEvent');drain()
drain()
if scenario!='side_locked':report(0)
if scenario.startswith('archive') or scenario.startswith('records'):
 report(1);report(2)
if scenario in ('archive_open','records_locked','records_open'):
 report(3,'NursingRecord');report(3,'FabricatedReport');manager.call_method('TryStartTruthRevelation');drain()
if scenario=='records_open':report(6)
which='C_SideDoor' if scenario.startswith('side') else 'C_ArchiveGate' if scenario.startswith('archive') else 'C_RecordsDoor'
door=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Door').generated_class()) if a.get_actor_label()==which)
point=unreal.Vector(2735,4780,90) if which=='C_SideDoor' else door.get_actor_location()+unreal.Vector(-180,0,90)
assert pawn.call_method('K2_TeleportTo',args=(point,pawn.get_actor_rotation())),'The test approach position is blocked'
interaction=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class());interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt')
unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
out={'scenario':scenario,'door':which,'phase':state.call_method('GetCurrentPhase').value,'supervisor_defeated':manager.call_method('IsSupervisorDefeated'),'can_interact':door.call_method('CanInteract',args=(pawn,)),'position':list(pawn.get_actor_location().to_tuple())}
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
(repo/'Scripts/C/door_play_scenario.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_DOOR_PLAY_READY '+json.dumps(out))
