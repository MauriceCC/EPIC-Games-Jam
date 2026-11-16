"""Prepare authorized runtime-only prerequisites for personal ending acceptance.

records_door: fresh PIE, existing C fixture supplies the preceding story facts.
supervisor: after actual C-30, supply only B's pending boss-defeat report.
official/authentic: after the user opened the real Records door, approach a station.
No helper selects, confirms or registers a final document, or changes player health.
"""
import unreal,runpy,json
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
stage=globals().get('C_ENDING_STAGE','records_door');assert stage in ('records_door','supervisor','official','authentic')
world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];assert 'L_Whitechapel.' in world.get_path_name()
pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method('GetObjectiveManager')
if stage=='records_door':
 assert state.call_method('GetCurrentPhase').value==0,'Use a fresh PIE session for the prerequisite shortcut.'
 fixture=runpy.run_path(str(repo/'Scripts/C/prepare_closure_door_play.py'),init_globals={'C_DOOR_SCENARIO':'records_open'})
elif stage=='supervisor':
 assert state.call_method('GetCurrentPhase').value==4 and manager.get_editor_property('bTruthRevelationComplete'),'Complete C-30 before supplying the missing B report.'
 assert not manager.get_editor_property('bDialogueActive'),'Finish the current transmission with E first.'
 if not manager.call_method('IsSupervisorDefeated'):
  bp=unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C');s=unreal.get_default_object(unreal.GameplayStatics);source=s.call_method('BeginDeferredActorSpawnFromClass',args=(world,bp.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));source=s.call_method('FinishSpawningActor',args=(source,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));source.set_editor_property('EventToReport',type(source.get_editor_property('EventToReport')).cast(6));source.call_method('ReportConfiguredEvent')
 assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(4620,3000,90),pawn.get_actor_rotation()))
 interaction=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class());interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt')
else:
 assert state.call_method('GetCurrentPhase').value==4 and manager.call_method('IsSupervisorDefeated'),'The revelation and the Supervisor prerequisite must be completed first.'
 door=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Door').generated_class()) if a.get_actor_label()=='C_RecordsDoor')
 assert door.get_editor_property('bIsOpen'),'Open the real Records door with E first.'
 assert not hud.get_editor_property('bFinalConfirmationOpen'),'Cancel or finish the current confirmation first.'
 assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(5060,2600 if stage=='official' else 3400,90),pawn.get_actor_rotation()))
 interaction=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class());interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt')
unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
print('C_ENDING_PLAY_READY '+json.dumps({'stage':stage,'phase':state.call_method('GetCurrentPhase').value,'ending':manager.call_method('GetRegisteredEnding').value,'position':list(pawn.get_actor_location().to_tuple())}))
