"""Compile C assets, inspect dependencies and enforce the Block 1 package scope."""
import unreal,json,sys,traceback,csv
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
OUT={'passed':False,'checks':[],'compiled':[],'asset_saves_performed':False}
def check(name,ok):
 OUT['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
try:
 check('Editor is inspecting the integrated Whitechapel map',unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()=='/Game/Unscripted/Maps/L_Whitechapel.L_Whitechapel')
 paths=['Narrative/'+x for x in ('BP_InteractionComponent','BP_InteractableBase','BP_Checkpoint','BP_Door','BP_Hideout','BP_Evidence','BP_ObjectiveManager','BP_GameState','BP_GameMode')]+['UI/'+x for x in ('BP_HUD','WBP_HUD','WBP_Dialogue','WBP_Checklist','WBP_Document')]
 registry=unreal.AssetRegistryHelpers.get_asset_registry();opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
 for path in paths:
  bp=h.asset(path);h.compile_blueprint(bp,warnings_as_errors=True);OUT['compiled'].append(bp.get_path_name())
  check(path+' has no production dependency on test fixtures',not any('/Test/' in str(x) for x in registry.get_dependencies(h.ROOT+path,opts)))
  if path.startswith('UI/'):
   for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
    for node in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
     if node.get_class().get_name()=='K2Node_DynamicCast':check(path+' avoids concrete A/B casts',not any('/Player/' in pin.get_pin_type().export_text() or '/Enemies/' in pin.get_pin_type().export_text() for pin in node.list_output_pins()))
     if node.get_class().get_name()=='K2Node_Event' and 'Tick' in str(node.get_node_title()):check(path+' has no connected Tick',not node.find_then_pin().list_connected_pins())
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 own={a.get_actor_label():a for a in actors if a.get_actor_label().startswith('C_Closure_')}
 check('Block 1 places exactly CP0, CP1 and the alley wardrobe',set(own)=={'C_Closure_CP0','C_Closure_CP1','C_Closure_AlleyHideout'})
 check('All placed C actors belong only to Story',all('/Maps/L_Whitechapel_Story.' in a.get_path_name() for a in own.values()))
 check('Checkpoint identifiers match the closure plan',str(own['C_Closure_CP0'].get_editor_property('CheckpointId'))=='CP0' and str(own['C_Closure_CP1'].get_editor_property('CheckpointId'))=='CP1')
 mesh=own['C_Closure_AlleyHideout'].get_component_by_class(unreal.StaticMeshComponent)
 check('C wardrobe references D art without editing D assets',mesh.get_editor_property('static_mesh').get_path_name()=='/Game/Unscripted/Art/Props/SM_Wardrobe_A/SM_Wardrobe_A.SM_Wardrobe_A')
 cdo=unreal.get_default_object(h.asset('Narrative/BP_GameMode').generated_class())
 check('Production GameMode preserves the real A pawn and controller',cdo.get_editor_property('default_pawn_class').get_path_name()=='/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C' and cdo.get_editor_property('player_controller_class').get_path_name()=='/Game/Unscripted/Player/BP_PlayerController.BP_PlayerController_C')
 check('Production GameMode uses C HUD',cdo.get_editor_property('hud_class')==h.asset('UI/BP_HUD').generated_class())
 table=h.asset('Narrative/DT_Dialogue');rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))
 check('All 24 authored dialogue rows remain present',len(rows)==24)
 warning=next(x for x in rows if x['Name']=='Briefing_05')
 enum=h.asset('Core/Enums/ESpeaker');helper=unreal.get_default_object(unreal.load_class(None,'/Script/Engine.KismetNodeHelperLibrary'))
 director=str(helper.call_method('GetEnumeratorName',args=(enum,3)))
 check('The Director delivers the final initial order',str(warning['Speaker']) in ('Director',director))
 mat=h.asset('UI/Materials/M_UI_AgentVitals_C')
 check('UI material compiles without shader errors',not unreal.MaterialEditingLibrary.recompile_material(mat))
 OUT['dirty_content']=[x.get_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
 OUT['dirty_maps']=[x.get_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
 check('Every dirty content package belongs to C',all(x.startswith(('/Game/Unscripted/UI/','/Game/Unscripted/Narrative/')) for x in OUT['dirty_content']))
 check('Only Story may have unsaved map changes',all(x=='/Game/Unscripted/Maps/L_Whitechapel_Story' for x in OUT['dirty_maps']))
 OUT['passed']=True
except Exception:OUT['error']=traceback.format_exc();unreal.log_error(OUT['error'])
finally:
 OUT['check_count']=len(OUT['checks'])
 (repo/'Scripts/C/closure_asset_validation.json').write_text(json.dumps(OUT,indent=2),encoding='utf-8')
 print('C_CLOSURE_ASSETS '+json.dumps(OUT))
