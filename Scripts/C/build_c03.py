"""C-03: actor focus and single-target interaction. No foreign gameplay edits."""
import sys,json,traceback
from pathlib import Path
import unreal
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
OUT={"passed":False}
try:
    bp=h.asset("Narrative/BP_InteractionComponent")
    graph=unreal.BlueprintEditorLibrary.find_event_graph(bp)
    assert all(not n.find_then_pin().list_connected_pins() for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes() if n.get_class().get_name()=="K2Node_Event"),"Preserve authored event flow"
    actor=h.obj_type(unreal.Actor);number=h.basic("real");integer=h.basic("int");boolean=h.basic("bool");text=h.basic("text")
    for n,t,d,e in (("InteractionRadius",number,"220",True),("FocusRefreshInterval",number,"0.1",True),("bInteractionEnabled",boolean,True,False),("FocusedActor",actor,"",False),("FocusPrompt",text,"",False),("BestActor",actor,"",False),("BestPriority",integer,"-2147483648",False),("BestDistance",number,"1000000000",False)):
        h.variable(bp,n,t,d,e,"Interaction")
    specs={
      "RefreshFocus":([],[]),"EvaluateCandidate":([("Candidate",actor)],[]),
      "CommitSelectedFocus":([],[]),"ApplyFocus":([("Target",actor),("Prompt",text)],[]),
      "SetInteractionEnabled":([("Enabled",boolean)],[]),"TryInteract":([],[("Accepted",boolean)]),
      "GetFocusedActor":([],[("Target",actor)]),"GetFocusPrompt":([],[("Prompt",text)])}
    # Clear only this builder's new function graphs before redeclaring their signatures.
    for graph in list(unreal.BlueprintEditorLibrary.list_graphs(bp)):
        if any(graph.get_name()==name or graph.get_name().startswith(name+"_") for name in specs):
            unreal.BlueprintEditorLibrary.remove_graph(bp,graph)
    h.compile_blueprint(bp,warnings_as_errors=True)
    for n,(ins,outs) in specs.items():
        h.function(bp,n,ins,outs,private=n in ("EvaluateCandidate","CommitSelectedFocus","ApplyFocus"),replace=True)
    h.compile_blueprint(bp,warnings_as_errors=True)
    g=h.edit(bp,"GetFocusedActor");h.result(g,g.find_graph_entry_pin(),Target=h.get(g,"FocusedActor"))
    g=h.edit(bp,"GetFocusPrompt");h.result(g,g.find_graph_entry_pin(),Prompt=h.get(g,"FocusPrompt"))
    g=h.edit(bp,"ApplyFocus")
    actor_diff=h.math(g,"NotEqual_ObjectObject",h.get(g,"FocusedActor"),h.param(g,"Target"))
    equal_text=h.call(g,"/Script/Engine.KismetTextLibrary:EqualEqual_TextText",A=h.get(g,"FocusPrompt"),B=h.param(g,"Prompt")).find_result_pin()
    yes,_=h.branch(g,g.find_graph_entry_pin(),h.any_true(g,actor_diff,h.not_(g,equal_text)))
    end=h.setvar(g,yes,"FocusedActor",h.param(g,"Target"));end=h.setvar(g,end,"FocusPrompt",h.param(g,"Prompt"))
    h.emit(g,end,"OnFocusChanged",Target=h.get(g,"FocusedActor"),Prompt=h.get(g,"FocusPrompt"))
    g=h.edit(bp,"CommitSelectedFocus")
    yes,no=h.branch(g,g.find_graph_entry_pin(),h.is_valid(g,h.get(g,"BestActor")))
    prompt=h.message(g,yes,"GetInteractionText",h.get(g,"BestActor"),Interactor=h.call(g,"/Script/Engine.ActorComponent:GetOwner").find_result_pin())
    h.invoke(g,prompt.find_then_pin(),bp,"ApplyFocus",Target=h.get(g,"BestActor"),Prompt=prompt.find_result_pin())
    h.invoke(g,no,bp,"ApplyFocus",Target=None,Prompt="")
    g=h.edit(bp,"EvaluateCandidate")
    candidate=h.param(g,"Candidate");owner=h.call(g,"/Script/Engine.ActorComponent:GetOwner").find_result_pin()
    good=h.all_true(g,h.is_valid(g,candidate),h.math(g,"NotEqual_ObjectObject",candidate,owner))
    yes,_=h.branch(g,g.find_graph_entry_pin(),good)
    distance=h.call(g,"/Script/Engine.Actor:GetDistanceTo",target=owner,OtherActor=candidate).find_result_pin()
    near,_=h.branch(g,yes,h.math(g,"LessEqual_DoubleDouble",distance,h.get(g,"InteractionRadius")))
    can=h.message(g,near,"CanInteract",candidate,Interactor=owner)
    allowed,_=h.branch(g,can.find_then_pin(),can.find_result_pin())
    priority=h.message(g,allowed,"GetInteractionPriority",candidate)
    better=h.any_true(g,h.not_(g,h.is_valid(g,h.get(g,"BestActor"))),h.math(g,"Greater_IntInt",priority.find_result_pin(),h.get(g,"BestPriority")),h.all_true(g,h.math(g,"EqualEqual_IntInt",priority.find_result_pin(),h.get(g,"BestPriority")),h.math(g,"Less_DoubleDouble",distance,h.get(g,"BestDistance"))))
    yes,_=h.branch(g,priority.find_then_pin(),better)
    end=h.setvar(g,yes,"BestActor",candidate)
    end=h.setvar(g,end,"BestPriority",priority.find_result_pin());h.setvar(g,end,"BestDistance",distance)
    g=h.edit(bp,"RefreshFocus")
    owner=h.call(g,"/Script/Engine.ActorComponent:GetOwner").find_result_pin()
    yes,no=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,"bInteractionEnabled"),h.is_valid(g,owner)))
    h.invoke(g,no,bp,"ApplyFocus",Target=None,Prompt="")
    end=h.setvar(g,yes,"BestActor",None);end=h.setvar(g,end,"BestPriority",-2147483648);end=h.setvar(g,end,"BestDistance",1000000000)
    gather=h.call(g,"/Script/Engine.GameplayStatics:GetAllActorsWithInterface",start=end,Interface="/Game/Unscripted/Core/Interfaces/BPI_Interactable.BPI_Interactable_C")
    body,item,done=h.foreach(g,gather.find_then_pin(),gather.find_output_pin("OutActors"))
    h.invoke(g,body,bp,"EvaluateCandidate",Candidate=item)
    h.invoke(g,done,bp,"CommitSelectedFocus")
    g=h.edit(bp,"SetInteractionEnabled")
    end=h.setvar(g,g.find_graph_entry_pin(),"bInteractionEnabled",h.param(g,"Enabled"))
    h.invoke(g,end,bp,"RefreshFocus")
    g=h.edit(bp,"TryInteract")
    update=h.invoke(g,g.find_graph_entry_pin(),bp,"RefreshFocus")
    yes,no=h.branch(g,update.find_then_pin(),h.is_valid(g,h.get(g,"FocusedActor")))
    owner=h.call(g,"/Script/Engine.ActorComponent:GetOwner").find_result_pin()
    can=h.message(g,yes,"CanInteract",h.get(g,"FocusedActor"),Interactor=owner)
    yes,no2=h.branch(g,can.find_then_pin(),can.find_result_pin())
    use=h.message(g,yes,"Interact",h.get(g,"FocusedActor"),Interactor=owner)
    update=h.invoke(g,use.find_then_pin(),bp,"RefreshFocus")
    h.result(g,update.find_then_pin(),Accepted=True)
    h.result(g,no,Accepted=False);h.result(g,no2,Accepted=False)
    g,start=h.event(bp,"ReceiveBeginPlay")
    refresh=h.invoke(g,start.find_then_pin(),bp,"RefreshFocus")
    h.call(g,"/Script/Engine.KismetSystemLibrary:K2_SetTimer",start=refresh.find_then_pin(),Object=h.self_pin(g),FunctionName="RefreshFocus",Time=h.get(g,"FocusRefreshInterval"),bLooping=True)
    g,end=h.event(bp,"ReceiveEndPlay")
    h.call(g,"/Script/Engine.KismetSystemLibrary:K2_ClearTimer",start=end.find_then_pin(),Object=h.self_pin(g),FunctionName="RefreshFocus")
    h.layout(bp)
    h.save(bp)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    (repo/"Scripts/C/c03_build_result.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C03_BUILD "+json.dumps(OUT))
