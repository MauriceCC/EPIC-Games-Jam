"""C test player handles document input without changing the production player."""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
pawn=h.asset("Narrative/Test/BP_TestPlayer_C");hud_bp=h.asset("UI/BP_HUD")
h.variable(pawn,"bTestGameplayInputEnabled",h.basic("bool"),True)
g,e=h.event(pawn,"SetGameplayInputEnabled")
end=h.setvar(g,e.find_then_pin(),"bTestGameplayInputEnabled",e.find_output_pin("bEnabled"))
pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
h.call(g,"/Script/Engine.Controller:SetIgnoreMoveInput",start=end,target=pc,bNewMoveInput=h.not_(g,e.find_output_pin("bEnabled")))
h.function(pawn,"HandleTestUse")
h.compile_blueprint(pawn,warnings_as_errors=True)
g=h.edit(pawn,"HandleTestUse")
pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
hud=h.call(g,"/Script/Engine.PlayerController:GetHUD",target=pc).find_result_pin()
yes,typed,_=h.cast(g,g.find_graph_entry_pin(),hud,hud_bp.generated_class())
yes,no=h.branch(g,yes,h.get(g,"bDocumentOpen",target=typed,cls=hud_bp.generated_class()))
h.invoke(g,yes,hud_bp,"CloseDocument",target=typed)
allowed,_=h.branch(g,no,h.get(g,"bTestGameplayInputEnabled"))
h.invoke(g,allowed,h.asset("Narrative/BP_InteractionComponent"),"TryInteract",target=h.get(g,"BP_InteractionComponent"))
g=h.edit(pawn,"EventGraph")
key=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_InputKey")
key.find_output_pin("Pressed").break_pin_links()
h.invoke(g,key.find_output_pin("Pressed"),pawn,"HandleTestUse")
h.layout(pawn);h.save(pawn)
print("C_TEST_USE_READY")
