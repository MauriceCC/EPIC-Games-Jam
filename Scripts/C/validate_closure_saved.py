"""Smoke-check the saved C HUD in the integrated level with native keyboard input."""
import unreal,json
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();view=hud.get_editor_property('View')
mode=unreal.GameplayStatics.get_game_mode(world);state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method('GetObjectiveManager')
if globals().get('C_SAVED_STAGE')=='focus':
 assert view.is_in_viewport()
 assert str(manager.get_editor_property('CurrentDialogueRow'))=='Briefing_01'
 unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
else:
 out={
  'real_player':unreal.GameplayStatics.get_player_pawn(world,0).get_class().get_path_name()=='/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C',
  'hud_visible':view.is_in_viewport(),
  'native_e_advances':str(manager.get_editor_property('CurrentDialogueRow'))=='Briefing_02',
  'native_tab_hides':not view.get_editor_property('ChecklistView').is_visible(),
  'cp0_saved':str(mode.get_editor_property('CheckpointId'))=='CP0',
  'health_problem_is_reported':str(view.get_editor_property('HealthValueText').get_text())=='UNAVAILABLE',
  'phase_preserved':state.call_method('GetCurrentPhase').value==0,
 }
 out['passed']=all(out.values())
 (repo/'Scripts/C/closure_saved_smoke_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 assert out['passed'],out
 print('C_CLOSURE_SAVED_SMOKE '+json.dumps(out))
