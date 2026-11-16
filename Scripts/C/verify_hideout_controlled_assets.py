"""Compile only C's wardrobe and inspect the bounded repositioning strategy."""
import unreal,sys,json,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
out={'passed':False,'checks':[],'asset_saves_performed':False}
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
try:
 check('No PIE session is running',not unreal.EditorLevelLibrary.get_pie_worlds(False))
 bp=h.asset('Narrative/BP_Hideout');h.compile_blueprint(bp,warnings_as_errors=True)
 check('Wardrobe compiles without errors or warnings',True)
 graphs={gr.get_name():unreal.BlueprintGraphEditor.get_graph_editor(gr).list_all_nodes() for gr in unreal.BlueprintEditorLibrary.list_graphs(bp)}
 titles=[str(n.get_node_title()).replace(' ','').lower() for nodes in graphs.values() for n in nodes]
 check('No automatic walking or navigation call remains',not any(any(x in title for x in ('addmovementinput','simplemoveto','aimoveto')) for title in titles))
 check('Legacy movement bodies contain no executable path',all(not h.edit(bp,name).find_graph_entry_pin().list_connected_pins() for name in ('BuildApproachPath','DriveToNextPoint')))
 check('Collision and animation settings are never overridden',not any(any(x in title for x in ('setcollisionenabled','setactorenablecollision','playanimation','setanimationmode')) for title in titles))
 teleport_graphs={name for name,nodes in graphs.items() for n in nodes if 'teleport' in str(n.get_node_title()).lower()}
 check('Collision-checked repositioning is isolated to the hidden helper',teleport_graphs=={'TryHiddenReposition'})
 check('Independent watchdog and input debounce exist',{'AbortTransition','UpdateHideoutTransition','ExecuteInteraction'}<=graphs.keys() and 'NextUseAllowedAt' in {str(p.get_pin_name()) for n in graphs['ExecuteInteraction'] for p in n.list_all_pins()})
 check('Transition timing uses a real-time clock',any('realtimeseconds' in title for title in titles))
 check('Wardrobe retains its original C-owned HUD bridge','SetTransitionVeil' in graphs)
 actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
 hide=actors['C_Closure_AlleyHideout']
 check('Door and exit markers remain unchanged',hide.get_editor_property('EntryDock').get_world_location().distance(unreal.Vector(1100,3685,90))<.01 and hide.get_editor_property('ExitPoint').get_world_location().distance(unreal.Vector(1100,3750,90))<.01)
 npc=actors['NPC_Vagrant'];check('NPC remains in its original foreign sublevel and position','/Maps/L_Whitechapel_Geo.' in npc.get_path_name() and npc.get_actor_location().distance(unreal.Vector(1250,3720,0))<.01)
 opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
 check('Production wardrobe has no test dependency',not any('/Test/' in str(p) for p in unreal.AssetRegistryHelpers.get_asset_registry().get_dependencies('/Game/Unscripted/Narrative/BP_Hideout',opts)))
 check('All content and maps are saved',not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages() and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
 out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
 out['check_count']=len(out['checks']);(repo/'Scripts/C/hideout_controlled_asset_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_CONTROLLED_HIDEOUT_ASSETS '+json.dumps(out))
