"""Retain the occupied hideout until the same agent chooses to leave."""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
hide=h.asset("Narrative/BP_Hideout");interaction=h.asset("Narrative/BP_InteractionComponent")
g=h.edit(hide,"ExecuteInteraction");h.clear_body(g)
end=h.setvar(g,g.find_graph_entry_pin(),"bOccupied",h.not_(g,h.get(g,"bOccupied")))
end=h.setvar(g,end,"Occupant",h.param(g,"Interactor"))
component=h.message(g,end,"GetStealthComponent",h.param(g,"Interactor"))
call=h.invoke(g,component.find_then_pin(),h.asset("Enemies/BP_StealthComponent"),"SetHidden",target=component.find_result_pin(),bHidden=h.get(g,"bOccupied"))
block=h.message(g,call.find_then_pin(),"SetRetakeBlocked",h.param(g,"Interactor"),bBlocked=h.get(g,"bOccupied"))
pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
move=h.call(g,"/Script/Engine.Controller:SetIgnoreMoveInput",start=block.find_then_pin(),target=pc,bNewMoveInput=h.get(g,"bOccupied"))
yes,no=h.branch(g,move.find_then_pin(),h.get(g,"bOccupied"))
yes=h.setvar(g,yes,"InteractionPrompt","Leave hideout")
no=h.setvar(g,no,"InteractionPrompt","Enter hideout");no=h.setvar(g,no,"Occupant",None)
focus=h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=h.param(g,"Interactor"),ComponentClass=interaction.generated_class().get_path_name()).find_result_pin()
h.invoke(g,yes,interaction,"LockFocusTo",target=focus,Target=h.self_pin(g))
h.invoke(g,no,interaction,"LockFocusTo",target=focus,Target=None)
h.layout(hide);h.save(hide)
print("C_HIDEOUT_FOCUS_FIXED")
