"""Rebind C's HUD to replacement pawns through the native controller notification."""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
hud=h.asset("UI/BP_HUD");g=h.edit(hud,"EventGraph")
def title(n):return str(n.get_node_title()).replace(" ","")
first=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_AssignDelegate" and "OnHealthChanged" in title(n))
last=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_AssignDelegate" and "OnDetectionChanged" in title(n))
old_start=first.find_execute_pin().list_connected_pins()[0]
old_end=last.find_then_pin().list_connected_pins()[0]
old_start.break_pin_links();last.find_then_pin().break_pin_links()
h.connect(old_start,old_end)
event=g.add_custom_event_node("BindPlayerSignals")
pawn=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerPawn",PlayerIndex=0).find_result_pin()
yes,_=h.branch(g,event.find_then_pin(),h.is_valid(g,pawn));h.connect(yes,first.find_execute_pin())
h.compile_blueprint(hud,warnings_as_errors=True)
# Append the native observer to the existing one-time story initialization chain.
tail=next(n for n in g.list_all_nodes() if title(n)=="SyncDialogue" and n.find_execute_pin().list_connected_pins() and n.find_execute_pin().list_connected_pins()[0].get_owning_node().get_class().get_name()=="K2Node_AssignDelegate")
pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
end,callback=h.bind_assign(g,tail.find_then_pin(),pc,"OnPossessedPawnChanged")
h.invoke(g,callback.find_then_pin(),hud,"BindPlayerSignals")
h.invoke(g,end,hud,"BindPlayerSignals")
h.layout(hud);h.save(hud)
print("C_HUD_POSSESSION_READY")
