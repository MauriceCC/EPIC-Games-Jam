"""Compile and explicitly save only the prepared C packages.

Run after closing the older editor session. Never invokes Save All.
"""
import unreal,json,sys,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
OUT={'passed':False,'compiled':[],'saved':[]}
try:
 assert not unreal.EditorLevelLibrary.get_pie_worlds(False),'Stop PIE first'
 for path in ('UI/WBP_Dialogue','UI/WBP_Checklist','UI/WBP_HUD','UI/BP_HUD','Narrative/BP_Hideout','Narrative/BP_GameMode'):
  bp=h.asset(path);h.compile_blueprint(bp,warnings_as_errors=True);OUT['compiled'].append(bp.get_path_name())
 for path in ('UI/WBP_Dialogue','UI/WBP_Checklist','UI/WBP_HUD','UI/BP_HUD','Narrative/BP_Hideout','Narrative/BP_GameMode','Narrative/DT_Dialogue','UI/Materials/M_UI_AgentVitals_C'):
  bp=h.asset(path);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False),path;OUT['saved'].append(bp.get_path_name())
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 assert levels.set_current_level_by_name('L_Whitechapel_Story')
 assert levels.save_current_level();OUT['saved'].append('/Game/Unscripted/Maps/L_Whitechapel_Story')
 OUT['dirty_content']=[x.get_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
 OUT['dirty_maps']=[x.get_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
 OUT['passed']=True
except Exception:OUT['error']=traceback.format_exc();unreal.log_error(OUT['error'])
finally:
 (repo/'Scripts/C/closure_block1_save_validation.json').write_text(json.dumps(OUT,indent=2),encoding='utf-8')
 print('C_CLOSURE_BLOCK1_SAVE '+json.dumps(OUT))
