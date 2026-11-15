"""Compile and inspect only C-30 packages; never save unrelated assets."""
import unreal,sys,json,csv,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
out={'passed':False,'checks':[],'asset_saves_performed':False}
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
try:
 check('PIE has stopped',not unreal.EditorLevelLibrary.get_pie_worlds(False))
 paths=('Narrative/BP_ObjectiveManager','Narrative/BP_Evidence','Narrative/BP_FutureMessage_C','UI/WBP_HUD')
 for rel in (*paths,'Narrative/Test/BP_C30ProgressionFixture_C'):
  h.compile_blueprint(h.asset(rel),warnings_as_errors=True);check(rel+' compiles without errors or warnings',True)
 registry=unreal.AssetRegistryHelpers.get_asset_registry();opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
 check('No production package depends on a test fixture',all(not any('/Test/' in str(x) for x in registry.get_dependencies('/Game/Unscripted/'+rel,opts)) for rel in (*paths,'Maps/L_Whitechapel_Story')))
 actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
 for name,position,mesh_name,height in [('C_FutureMessage',(2900,5300,0),'SM_Folder_Report',90),('C_NursingRecord',(3340,460,0),'SM_Ledger_Nursing',110),('C_FabricatedReport',(2400,1200,0),'SM_Folder_Report',120)]:
  a=actors[name];check(name+' persists in Story at its authored location','/Maps/L_Whitechapel_Story.' in a.get_path_name() and a.get_actor_location().distance(unreal.Vector(*position))<.01)
  component=a.get_editor_property('MessageMesh' if name=='C_FutureMessage' else 'EvidenceMesh')
  check(name+' reuses unmodified D art',component.get_editor_property('static_mesh').get_path_name()=='/Game/Unscripted/Art/Props/'+mesh_name+'/'+mesh_name+'.'+mesh_name)
  check(name+' is placed on its existing support',abs(component.get_editor_property('relative_location').z-height)<.01)
  check(name+' starts available for its guarded interaction',not a.get_editor_property('bConsumed'))
 check('Both distinct evidence kinds persist',actors['C_NursingRecord'].get_editor_property('EvidenceType').value==0 and actors['C_FabricatedReport'].get_editor_property('EvidenceType').value==1)
 check('Previous checkpoints, hideout and all three doors remain',all(n in actors for n in ('C_Closure_CP0','C_Closure_CP1','C_Closure_AlleyHideout','C_SideDoor','C_ArchiveGate','C_RecordsDoor')))
 check('No final-choice actor was added',not any('BP_FinalChoice' in a.get_class().get_path_name() for a in actors.values()))
 manager=h.asset('Narrative/BP_ObjectiveManager');cdo=unreal.get_default_object(manager.generated_class())
 check('Revelation and message completion start false',all(not cdo.get_editor_property(n) for n in ('bFutureMessageQueued','bFutureMessageRead','bTruthRevelationStarted','bTruthRevelationComplete','bTruthNoticeReported')))
 write_graphs=[g.get_name() for g in unreal.BlueprintEditorLibrary.list_graphs(manager) for n in unreal.BlueprintGraphEditor.get_graph_editor(g).list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'CurrentPhase' in {str(p.get_pin_name()) for p in n.list_all_pins()}]
 check('Only the existing CommitStoryPhase function writes the phase',write_graphs==['CommitStoryPhase'])
 view=h.asset('UI/WBP_HUD');notice=unreal.find_object(None,view.get_path_name()+':WidgetTree.ContinuityText');check('Notice is positioned below the incoming-transmission header',notice.get_editor_property('slot').get_position().y==120)
 check('The full dossier remains collapsed by default',unreal.find_object(None,view.get_path_name()+':WidgetTree.ChecklistDrawer').get_visibility()==unreal.SlateVisibility.COLLAPSED)
 rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(h.asset('Narrative/DT_HUDText')));check('The future-message prompt is saved in the existing table',sum(r['Name']=='FutureMessagePrompt' for r in rows)==1)
 dialogue=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(h.asset('Narrative/DT_Dialogue')));check('All 24 existing narrative rows remain',len(dialogue)==24)
 check('All content and map packages are saved',not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages() and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
 out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
 out['check_count']=len(out['checks']);(repo/'Scripts/C/c30_saved_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C30_SAVED '+json.dumps(out))
