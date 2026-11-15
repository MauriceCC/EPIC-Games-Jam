import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools
from pathlib import Path
out={}
for name in ("BP_GameMode","BP_GameState","BP_ObjectiveManager"):
 bp=unreal.load_asset("/Game/Unscripted/Narrative/"+name)
 data={"class":BlueprintTools.get_parent(bp).get_path_name(),"variables":[str(x) for x in unreal.BlueprintEditorLibrary.list_member_variable_names(bp)],"graphs":{}}
 for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
  g=unreal.BlueprintGraphEditor.get_graph_editor(graph)
  data["graphs"][graph.get_name()]=[{"class":n.get_class().get_name(),"pins":[{"name":str(p.get_pin_name()),"type":p.get_pin_type().export_text(),"links":[str(x.get_owning_node().get_name())+":"+str(x.get_pin_name()) for x in p.list_connected_pins()]} for p in n.list_all_pins()]} for n in g.list_all_nodes()]
 if name=="BP_GameMode":
  cdo=unreal.get_default_object(bp.generated_class())
  data["defaults"]={p:str(cdo.get_editor_property(p)) for p in ("game_state_class","player_controller_class","default_pawn_class","hud_class")}
 if name=="BP_ObjectiveManager":
  try:data["new_variables"]=str(bp.get_editor_property("new_variables"))
  except Exception as e:data["variable_metadata_error"]=str(e)
  g=unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp))
  data["dispatcher_actions"]=[str(x) for x in g.list_available_nodes([]) if "OnStoryPhaseChanged" in str(x) or "OnEndingTriggered" in str(x)]
 out[name]=data
out["dirty_content"]=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
out["dirty_maps"]=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
target=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c01_c02_dependency_inspection.json"
target.write_text(json.dumps(out,indent=2),encoding="utf-8")
print("C_F1_DEPENDENCIES",[(name,list(data.get("graphs",{}))) for name,data in out.items() if isinstance(data,dict)])
