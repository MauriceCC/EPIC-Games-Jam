"""Final C-only compiler, shader, dependency and save-state verification."""
import unreal,sys,json,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
out={'passed':False,'compiled':[],'materials':[],'checks':[]}
def check(name,value):out['checks'].append({'name':name,'passed':bool(value)});assert value,name
try:
 check('PIE has stopped',not unreal.EditorLevelLibrary.get_pie_worlds(False))
 registry=unreal.AssetRegistryHelpers.get_asset_registry();opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
 for rel in ('UI/BP_HUD','UI/WBP_HUD','UI/WBP_Checklist','UI/WBP_Dialogue','Narrative/BP_Hideout'):
  bp=h.asset(rel);h.compile_blueprint(bp,warnings_as_errors=True);out['compiled'].append(bp.get_path_name())
  check(rel+' has no test dependency',not any('/Test/' in str(x) for x in registry.get_dependencies('/Game/Unscripted/'+rel,opts)))
  for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
   for node in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
    if rel.startswith('UI/') and node.get_class().get_name()=='K2Node_Event' and 'Tick' in str(node.get_node_title()):check(rel+' does not use Tick',not node.find_then_pin().list_connected_pins())
 hide=h.asset('Narrative/BP_Hideout');cdo=unreal.get_default_object(hide.generated_class())
 titles=[str(n.get_node_title()).replace(' ','').lower() for gr in unreal.BlueprintEditorLibrary.list_graphs(hide) for n in unreal.BlueprintGraphEditor.get_graph_editor(gr).list_all_nodes()]
 check('Wardrobe never teleports, overrides collision or replaces animation',not any(any(x in title for x in ('setactorlocation','setactortransform','setcollisionenabled','setactorenablecollision','playanimation')) for title in titles))
 check('Wardrobe uses native pawn movement',any('addmovementinput' in title for title in titles))
 check('Wardrobe consumes gameplay input only while enabled',cdo.get_editor_property('block_input') and cdo.get_editor_property('input_priority')==20 and cdo.get_editor_property('auto_receive_input')==unreal.AutoReceiveInput.DISABLED)
 actor=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='C_Closure_AlleyHideout')
 check('Saved wardrobe dock faces the door',actor.get_editor_property('EntryDock').get_world_location().distance(unreal.Vector(1100,3685,90))<.01)
 check('Saved wardrobe exit stays clear of the alley wall',actor.get_editor_property('ExitPoint').get_world_location().distance(unreal.Vector(1100,3750,90))<.01)
 out['package_dependencies']={rel:sorted(str(x) for x in registry.get_dependencies('/Game/Unscripted/'+rel,opts) if str(x).startswith('/Game/Unscripted/')) for rel in ('UI/BP_HUD','UI/WBP_HUD','UI/WBP_Checklist','UI/WBP_Dialogue','Narrative/BP_Hideout','Maps/L_Whitechapel_Story')}
 for rel in ('UI/Materials/M_UI_AgentVitals_C','UI/Materials/M_UI_DepartmentPlate_C'):
  mat=h.asset(rel);errors=list(unreal.MaterialEditingLibrary.recompile_material(mat));check(rel+' compiles without shader errors',not errors)
  assert unreal.EditorAssetLibrary.save_loaded_asset(mat,False);out['materials'].append(mat.get_path_name())
 mat=h.asset('UI/Materials/M_UI_AgentVitals_C');exprs=unreal.MaterialEditingLibrary.get_material_expressions(mat)
 mask=next(x for x in exprs if isinstance(x,unreal.MaterialExpressionComponentMask) and x.get_editor_property('r') and x.get_editor_property('g') and x.get_editor_property('b'))
 shader=next(x for x in unreal.MaterialEditingLibrary.get_inputs_for_material_expression(mat,mask) if isinstance(x,unreal.MaterialExpressionCustom))
 check('The connected portrait shader contains the new bust and unknown-health state','float hair' in shader.get_editor_property('code') and 'HealthKnown' in shader.get_editor_property('code'))
 view=h.asset('UI/WBP_HUD');drawer=unreal.find_object(None,view.get_path_name()+':WidgetTree.ChecklistDrawer');check('Dossier default is saved as collapsed',drawer.get_visibility()==unreal.SlateVisibility.COLLAPSED)
 out['dirty_content']=[x.get_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
 out['dirty_maps']=[x.get_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
 check('All content and maps are saved',not out['dirty_content'] and not out['dirty_maps'])
 out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
 (repo/'Scripts/C/narrative_presentation_asset_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print('C_PRESENTATION_FINAL_ASSETS '+json.dumps(out))
