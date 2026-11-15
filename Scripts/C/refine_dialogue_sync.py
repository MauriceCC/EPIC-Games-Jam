"""Finish notifications now expose the correct active flag, allowing immediate HUD sync."""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
hud=h.asset("UI/BP_HUD");g=h.edit(hud,"EventGraph")
node=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(" ","")=="ScheduleDialogueSync")
start=node.find_execute_pin().list_connected_pins()[0]
g.remove_nodes([node]);h.invoke(g,start,hud,"SyncDialogue")
old=h.edit(hud,"ScheduleDialogueSync");unreal.BlueprintEditorLibrary.remove_graph(hud,old.get_graph())
h.layout(hud);h.save(hud)
print("C_DIALOGUE_SYNC_READY")
