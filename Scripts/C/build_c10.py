"""C-10: a timed, non-blocking continuity notice driven by the existing story event."""
import unreal,sys,json,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h,umg_helpers_c as u
from importlib import reload
h=reload(h);u=reload(u);OUT={"passed":False}
try:
    view=h.asset("UI/WBP_HUD");hud=h.asset("UI/BP_HUD");state=h.asset("Narrative/BP_GameState")
    for name in ("ShowContinuityNotice","HideContinuityNotice"):h.function(view,name)
    h.function(hud,"ShowContinuityNotice")
    h.compile_blueprint(view,warnings_as_errors=True);h.compile_blueprint(hud,warnings_as_errors=True)
    g=h.edit(view,"ShowContinuityNotice")
    end=u.visibility(g,g.find_graph_entry_pin(),h.get(g,"ContinuityText"),"Visible")
    h.call(g,"/Script/Engine.KismetSystemLibrary:K2_SetTimer",end,Object=h.self_pin(g),FunctionName="HideContinuityNotice",Time=3,bLooping=False)
    g=h.edit(view,"HideContinuityNotice");u.visibility(g,g.find_graph_entry_pin(),h.get(g,"ContinuityText"),"Collapsed")
    g=h.edit(hud,"ShowContinuityNotice");h.invoke(g,g.find_graph_entry_pin(),view,"ShowContinuityNotice",target=h.get(g,"View"))
    g=h.edit(state,"HandleRuntimeStoryEvent")
    branches=[n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_IfThenElse" and not n.find_output_pin("else").list_connected_pins()]
    # The branch testing event 9 is the only terminal event-selection branch.
    event_index=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=h.param(g,"Event")).find_result_pin()
    original=next(n for n in branches if any("RestoreCheckpoint" in str(p.get_owning_node().get_node_title()).replace(" ","") for p in n.find_output_pin("then").list_connected_pins()))
    yes,_=h.branch(g,original.find_output_pin("else"),h.math(g,"EqualEqual_IntInt",event_index,11))
    pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
    obj=h.call(g,"/Script/Engine.PlayerController:GetHUD",target=pc).find_result_pin()
    yes,typed,_=h.cast(g,yes,obj,hud.generated_class());h.invoke(g,yes,hud,"ShowContinuityNotice",target=typed)
    h.layout(view,["ShowContinuityNotice","HideContinuityNotice"]);h.layout(hud,["ShowContinuityNotice"]);h.layout(state,["HandleRuntimeStoryEvent"])
    h.save(view,hud,state);OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    (repo/"Scripts/C/c10_build_result.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C10_BUILD "+json.dumps(OUT))
