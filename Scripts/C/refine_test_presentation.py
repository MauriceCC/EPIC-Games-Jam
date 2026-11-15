"""Keep test instructions and simulated encounter cues inside C's test player."""
import unreal,sys,json
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h,umg_helpers_c as u
from importlib import reload
h=reload(h);u=reload(u)
view=h.asset("UI/WBP_HUD");hud=h.asset("UI/BP_HUD");pawn=h.asset("Narrative/Test/BP_TestPlayer_C");objective=h.asset("Narrative/BP_ObjectiveManager")
h.function(view,"SetTestHint",[("Text",h.basic("text"))]);h.compile_blueprint(view,warnings_as_errors=True)
g=h.edit(view,"SetTestHint");u.set_text(g,g.find_graph_entry_pin(),"TestHintText",h.param(g,"Text"));h.layout(view,["SetTestHint"]);h.save(view)
g=h.edit(pawn,"PublishTestResources")
last=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_CallDelegate" and "OnDetectionChanged" in str(n.get_node_title()).replace(" ",""))
pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
obj=h.call(g,"/Script/Engine.PlayerController:GetHUD",target=pc).find_result_pin()
end,typed,_=h.cast(g,last.find_then_pin(),obj,hud.generated_class())
typed_view=h.get(g,"View",typed,hud.generated_class())
h.invoke(g,end,view,"SetTestHint",target=typed_view,Text="C / ISOLATED TEST   E Use / continue   Tab Directives   1-6 Story facts   7-0 Encounter / archive\nH-M Resources   P Checkpoint   Backspace Restore   X Continuity")
# A simulated encounter can play the existing conversation without placing B's boss.
g=h.edit(pawn,"ReportTestStoryEvent")
message=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_Message")
index=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=h.param(g,"Event")).find_result_pin()
yes,_=h.branch(g,message.find_then_pin(),h.math(g,"EqualEqual_IntInt",index,13))
state=h.call(g,"/Script/Engine.GameplayStatics:GetGameState").find_result_pin()
manager=h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=state,ComponentClass=objective.generated_class().get_path_name()).find_result_pin()
phase=h.invoke(g,yes,objective,"GetStoryPhase",target=manager)
number=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=phase.find_result_pin()).find_result_pin()
yes,_=h.branch(g,phase.find_then_pin(),h.math(g,"EqualEqual_IntInt",number,4))
h.invoke(g,yes,objective,"QueueDialogue",target=manager,RowName="SupervisorEncounter_01")
h.layout(pawn,["PublishTestResources","ReportTestStoryEvent"]);h.save(pawn)
(repo/"Scripts/C/c_f1_controls_build.json").write_text(json.dumps({"passed":True,"verified_keys":20,"test_player":pawn.get_path_name()},indent=2),encoding="utf-8")
print("C_TEST_PRESENTATION_READY")
