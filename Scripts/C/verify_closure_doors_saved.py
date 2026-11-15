"""Read saved Block 2.1 configuration and compile only C's changed Blueprints."""
import unreal,sys,json,traceback,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
out={'passed':False,'checks':[],'asset_saves_performed':False}
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
try:
 check('PIE has stopped',not unreal.EditorLevelLibrary.get_pie_worlds(False))
 for rel in ('Narrative/BP_Door','Narrative/BP_ObjectiveManager'):
  h.compile_blueprint(h.asset(rel),warnings_as_errors=True);check(rel+' compiles without errors or warnings',True)
 actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
 for name,pos,yaw,width,phase,report,boss in [('C_SideDoor',(2800,4600,0),0,200,1,True,False),('C_ArchiveGate',(3600,3600,0),90,400,4,False,False),('C_RecordsDoor',(4800,3000,0),90,400,4,False,True)]:
  a=actors[name];check(name+' belongs to Story at the reserved location','/Maps/L_Whitechapel_Story.' in a.get_path_name() and a.get_actor_location().distance(unreal.Vector(*pos))<.01)
  r=a.get_actor_rotation();check(name+' is upright and spans the opening',abs(r.pitch)<.01 and abs(r.roll)<.01 and abs(r.yaw-yaw)<.01 and a.get_editor_property('DoorWidth')==width)
  check(name+' has the planned unlock condition',a.get_editor_property('RequiredPhase').value==phase and a.get_editor_property('bRequireSupervisorDefeat')==boss and a.get_editor_property('bReportsEscapeRoute')==report)
  check(name+' starts closed and unconsumed',not a.get_editor_property('bIsOpen') and not a.get_editor_property('bConsumed') and not a.get_editor_property('bIsOpening'))
  check(name+' references existing D art only',a.get_editor_property('DoorMesh').get_editor_property('static_mesh').get_path_name().startswith('/Game/Unscripted/Art/Props/'))
  check(name+' owns a closed navigation modifier',a.get_editor_property('DoorNavigation').get_editor_property('area_class').get_path_name()=='/Script/NavigationSystem.NavArea_Null')
 check('Block 1 placements remain present',all(n in actors for n in ('C_Closure_CP0','C_Closure_CP1','C_Closure_AlleyHideout')))
 graphs=unreal.BlueprintEditorLibrary.list_graphs(h.asset('Narrative/BP_ObjectiveManager'));getter=next(g for g in graphs if g.get_name()=='IsSupervisorDefeated')
 check('The new C-only boss query writes no state',not any(n.get_class().get_name()=='K2Node_VariableSet' for n in unreal.BlueprintGraphEditor.get_graph_editor(getter).list_all_nodes()))
 registry=unreal.AssetRegistryHelpers.get_asset_registry();opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
 check('Production doors and Story have no test dependencies',all(not any('/Test/' in str(x) for x in registry.get_dependencies('/Game/Unscripted/'+rel,opts)) for rel in ('Narrative/BP_Door','Maps/L_Whitechapel_Story')))
 check('Every content and map package is saved',not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages() and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
 out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
 out['check_count']=len(out['checks']);(repo/'Scripts/C/closure_doors_saved_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_CLOSURE_DOORS_SAVED '+json.dumps(out))
