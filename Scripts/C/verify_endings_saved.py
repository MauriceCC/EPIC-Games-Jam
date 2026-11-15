"""Inspect saved C-31/C-32 and preserved C systems without saving packages."""
import unreal,sys,json,csv,hashlib,traceback,ast
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'));import blueprint_helpers_c as h
out={'passed':False,'checks':[],'asset_saves_performed':False}
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
def graphs(bp):return {g.get_name():unreal.BlueprintGraphEditor.get_graph_editor(g) for g in unreal.BlueprintEditorLibrary.list_graphs(bp)}
try:
 check('PIE has stopped',not unreal.EditorLevelLibrary.get_pie_worlds(False))
 production=('Narrative/BP_FinalChoice','Narrative/BP_ObjectiveManager','UI/BP_HUD','UI/WBP_Ending','Narrative/BP_Hideout','Narrative/BP_Door','UI/WBP_HUD')
 for path in production:h.compile_blueprint(h.asset(path),warnings_as_errors=True);check(path+' compiles without errors or warnings',True)
 registry=unreal.AssetRegistryHelpers.get_asset_registry();opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
 check('Production packages do not depend on Test or Developers assets',all(not any('/Test/' in str(p) or '/Developers/' in str(p) for p in registry.get_dependencies('/Game/Unscripted/'+name,opts)) for name in (*production,'Maps/L_Whitechapel_Story')))
 actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
 for name,pos,index,art,prompt in [('C_OfficialRecord',(5200,2600,0),1,'SM_RecordStation_Official','OfficialFilePrompt'),('C_AuthenticRecord',(5200,3400,0),2,'SM_RecordStation_Authentic','AuthenticFilePrompt')]:
  a=actors[name];mesh=a.get_editor_property('StationMesh')
  check(name+' is saved in Story at the planned location','/Maps/L_Whitechapel_Story.' in a.get_path_name() and a.get_actor_location().distance(unreal.Vector(*pos))<.01)
  check(name+' retains the intended final record',a.get_editor_property('SelectedEnding').value==index and str(a.get_editor_property('InteractionPromptRow'))==prompt)
  check(name+' reuses the original D mesh',mesh.get_editor_property('static_mesh').get_path_name()=='/Game/Unscripted/Art/Props/'+art+'/'+art+'.'+art)
  check(name+' mesh is attached and located with its actor',mesh.get_attach_parent()==a.root_component and mesh.get_world_location().distance(a.get_actor_location())<.01)
  check(name+' starts unconsumed with physical collision',not a.get_editor_property('bConsumed') and a.get_editor_property('RegistrationCount')==0 and mesh.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION)
 check('All previous C placements remain',all(n in actors for n in ('C_Closure_CP0','C_Closure_CP1','C_Closure_AlleyHideout','C_SideDoor','C_ArchiveGate','C_RecordsDoor','C_FutureMessage','C_NursingRecord','C_FabricatedReport')))
 manager=h.asset('Narrative/BP_ObjectiveManager');g=graphs(manager)
 writers=[name for name,gr in g.items() for n in gr.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'CurrentPhase' in {str(p.get_pin_name()) for p in n.list_all_pins()}]
 check('CommitStoryPhase remains the sole phase writer',writers==['CommitStoryPhase'])
 check('The two new ending queries write no state',all(n.get_class().get_name()!='K2Node_VariableSet' for name in ('CanChooseFinalDocument','GetRegisteredEnding') for n in g[name].list_all_nodes()))
 hud=h.asset('UI/BP_HUD');defaults=unreal.get_default_object(hud.generated_class());check('The ending UI is inactive on a fresh game',not defaults.get_editor_property('bEndingPresented') and not defaults.get_editor_property('bFinalConfirmationOpen') and defaults.get_editor_property('FinalView') is None)
 hg=graphs(hud);nodes=hg['PresentFinalEnding'].list_all_nodes();titles=[str(n.get_node_title()).replace(' ','') for n in nodes]
 check('The terminal boundary calls the shared Retake contracts',all(any(name in t for t in titles) for name in ('SetRetakeBlocked','ClearRetakeHistory','SetGameplayInputEnabled')))
 check('The terminal boundary blocks native pawn input and pauses gameplay',all(any(name in t for t in titles) for name in ('DisableInput','SetGamePaused','SetInputModeUIOnly')))
 vg=graphs(h.asset('UI/WBP_Ending'));check('Native modal keys reject operating-system repeats',any('IsRepeat' in str(n.get_node_title()).replace(' ','') for n in vg['OnKeyDown'].list_all_nodes()))
 check('The worldless regression fixture stays outside production',not any('/Test/' in str(p) for p in registry.get_dependencies('/Game/Unscripted/Narrative/BP_ObjectiveManager',opts)))
 source=list(csv.DictReader((repo/'SourceData/C/EndingText.csv').open(encoding='utf-8-sig',newline='')));rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(h.asset('Narrative/DT_EndingText')))
 def text_value(raw):return ast.literal_eval('['+raw[raw.index('(')+1:-1]+']')[-1] if raw.startswith(('NSLOCTEXT(','LOCTEXT(')) else raw
 actual={r['Name']:text_value(r['Text']) for r in rows};check('All ending copy matches its English source table',actual=={r['Name']:r['Text'].replace('\\n','\n') for r in source})
 prompts=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(h.asset('Narrative/DT_HUDText')));check('Both final interaction prompts are saved',all(any(r['Name']==name for r in prompts) for name in ('OfficialFilePrompt','AuthenticFilePrompt')))
 check('All content and map packages are saved',not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages() and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
 out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:out['check_count']=len(out['checks']);(repo/'Scripts/C/endings_saved_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_ENDINGS_SAVED '+json.dumps(out))
