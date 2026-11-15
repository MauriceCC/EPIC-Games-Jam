"""Hide world-use prompts while E belongs to document/dialogue presentation."""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
for name,label in (("WBP_Document","CloseButtonLabel"),("WBP_Dialogue","AdvanceButtonLabel")):
    bp=h.asset("UI/"+name);obj=unreal.find_object(None,bp.get_path_name()+":WidgetTree."+label)
    obj.set_auto_wrap_text(False);h.save(bp)
hud=h.asset("UI/BP_HUD");view=h.asset("UI/WBP_HUD");objective=h.asset("Narrative/BP_ObjectiveManager");interaction=h.asset("Narrative/BP_InteractionComponent")
h.function(hud,"RefreshInteractionPrompt");h.compile_blueprint(hud,warnings_as_errors=True)
g=h.edit(hud,"RefreshInteractionPrompt")
state=h.call(g,"/Script/Engine.GameplayStatics:GetGameState").find_result_pin()
manager=h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=state,ComponentClass=objective.generated_class().get_path_name()).find_result_pin()
blocked=h.any_true(g,h.get(g,"bDocumentOpen"),h.get(g,"bDialogueActive",manager,objective.generated_class()))
yes,no=h.branch(g,g.find_graph_entry_pin(),blocked)
h.invoke(g,yes,view,"SetInteraction",target=h.get(g,"View"),Prompt="")
pawn=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerPawn",PlayerIndex=0).find_result_pin()
valid,_=h.branch(g,no,h.is_valid(g,pawn))
component=h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=pawn,ComponentClass=interaction.generated_class().get_path_name()).find_result_pin()
prompt=h.invoke(g,valid,interaction,"GetFocusPrompt",target=component)
h.invoke(g,prompt.find_then_pin(),view,"SetInteraction",target=h.get(g,"View"),Prompt=prompt.find_output_pin("Prompt"))
g=h.edit(hud,"SyncDialogue")
entry=g.find_graph_entry_pin();old=entry.list_connected_pins()[0];entry.break_pin_links()
end=h.invoke(g,entry,hud,"RefreshInteractionPrompt").find_then_pin();h.connect(end,old)
g=h.edit(hud,"EventGraph")
old=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(" ","")=="SetInteraction")
start=old.find_execute_pin().list_connected_pins()[0];g.remove_nodes([old]);h.invoke(g,start,hud,"RefreshInteractionPrompt")
last=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_AssignDelegate" and "OnDetectionChanged" in str(n.get_node_title()).replace(" ",""))
h.invoke(g,last.find_then_pin(),hud,"RefreshInteractionPrompt")
h.layout(hud,["RefreshInteractionPrompt","SyncDialogue","EventGraph"]);h.save(hud)
print("C_MODAL_PROMPT_READY")
