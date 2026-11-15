"""Use a C-owned respawn marker above the checkpoint's floor-level visual."""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
checkpoint=h.asset("Narrative/BP_Checkpoint");state=h.asset("Narrative/BP_GameState");mode=h.asset("Narrative/BP_GameMode")
point=h.add_component(checkpoint,"RespawnPoint",unreal.SceneComponent)
point.set_editor_property("relative_location",unreal.Vector(0,0,100))
transform=unreal.BlueprintEditorLibrary.get_struct_type(unreal.load_object(None,"/Script/CoreUObject.Transform"))
h.function(checkpoint,"GetRespawnTransform",outputs=[("Transform",transform)])
h.compile_blueprint(checkpoint,warnings_as_errors=True)
g=h.edit(checkpoint,"GetRespawnTransform")
position=h.call(g,"/Script/Engine.SceneComponent:K2_GetComponentToWorld",target=h.get(g,"RespawnPoint")).find_result_pin()
h.result(g,g.find_graph_entry_pin(),Transform=position)
h.layout(checkpoint,["GetRespawnTransform"]);h.save(checkpoint)
g=h.edit(state,"HandleRuntimeStoryEvent")
save=next(n for n in g.list_all_nodes() if "SaveCheckpoint" in str(n.get_node_title()).replace(" ",""))
start=save.find_execute_pin().list_connected_pins()[0];start.break_pin_links()
yes,typed,no=h.cast(g,start,h.param(g,"Source"),checkpoint.generated_class())
point=h.invoke(g,yes,checkpoint,"GetRespawnTransform",target=typed)
save_point=h.invoke(g,point.find_then_pin(),mode,"SaveCheckpoint",target=save.find_self_pin().list_connected_pins()[0],Id=h.param(g,"Param"),Transform=point.find_output_pin("Transform"))
h.connect(no,save.find_execute_pin())
h.layout(state,["HandleRuntimeStoryEvent"]);h.save(state)
print("C_CHECKPOINT_POSITION_READY")
