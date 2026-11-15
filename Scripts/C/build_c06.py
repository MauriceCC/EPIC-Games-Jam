"""C-06: DataTable dialogue playback, queued chains and narrative input locks."""
import unreal,sys,json,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h,umg_helpers_c as u
from importlib import reload
h=reload(h);u=reload(u)
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
OUT={"passed":False}
def declare(bp,name,inputs=(),outputs=()):
    g=h.edit(bp,name)
    if g:h.clear_body(g);return g
    return h.function(bp,name,inputs,outputs)
def player(g):return h.call(g,"/Script/Engine.GameplayStatics:GetPlayerPawn",PlayerIndex=0).find_result_pin()
def manager(g):
    state=h.call(g,"/Script/Engine.GameplayStatics:GetGameState").find_result_pin()
    return h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=state,ComponentClass=h.asset("Narrative/BP_ObjectiveManager").generated_class().get_path_name()).find_result_pin()
def hud(g,start):
    pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
    obj=h.call(g,"/Script/Engine.PlayerController:GetHUD",target=pc).find_result_pin()
    return h.cast(g,start,obj,h.asset("UI/BP_HUD").generated_class())[:2]
async def build():
    objective=h.asset("Narrative/BP_ObjectiveManager");hud_bp=h.asset("UI/BP_HUD");view=h.asset("UI/WBP_HUD")
    boolean=h.basic("bool");name=h.basic("name");text=h.basic("text")
    for n,t,d in (("bPresentationEnabled",boolean,False),("bDialogueActive",boolean,False),("bDocumentActive",boolean,False),("bNarrativeInputLocked",boolean,False),("CurrentDialogueRow",name,""),("NextDialogueRow",name,""),("DialogueQueue",h.array_type(name),"()")):
        h.variable(objective,n,t,d)
    specs={"QueueDialogue":([("RowName",name)],[]),"StartDialogue":([("RowName",name)],[]),"ShowDialogueRow":([("RowName",name)],[]),"AdvanceDialogue":([],[]),"AdvanceDialogueQueue":([],[]),"RefreshNarrativeInputLock":([],[]),"SetDocumentActive":([("Active",boolean)],[]),"PresentStoryPhase":([("Phase",h.enum_type("EStoryPhase"))],[]),"StartBriefing":([],[])}
    for n,(ins,outs) in specs.items():declare(objective,n,ins,outs)
    for n,ins in (("ShowDialogue",[("Speaker",text),("Body",text)]),("HideDialogue",[])):
        declare(hud_bp,n,ins);declare(view,n,ins)
    h.compile_blueprint(objective,warnings_as_errors=True);h.compile_blueprint(hud_bp,warnings_as_errors=True)
    dialogue=await u.create("WBP_Dialogue")
    root,box=await u.panel(dialogue,"DialoguePanel")
    await u.label(dialogue,box,"DialogueEyebrow","DEPARTMENT OF CONTINUITY / TRANSMISSION",12,u.GOLD)
    await u.label(dialogue,box,"SpeakerText","Department of Continuity",18,u.CYAN,True)
    area=await u.widget(dialogue,unreal.SizeBox,"DialogueArea",box);area.set_min_desired_height(100)
    await u.label(dialogue,area,"BodyText","",21,variable=True)
    await u.button(dialogue,box,"AdvanceButton","Continue [E]")
    declare(dialogue,"PresentLine",[("Speaker",text),("Body",text)]);declare(dialogue,"ContinueDialogue")
    h.compile_blueprint(dialogue,warnings_as_errors=True)
    g=h.edit(dialogue,"PresentLine");end=u.set_text(g,g.find_graph_entry_pin(),"SpeakerText",h.param(g,"Speaker"));u.set_text(g,end,"BodyText",h.param(g,"Body"))
    g=h.edit(dialogue,"ContinueDialogue");h.invoke(g,g.find_graph_entry_pin(),objective,"AdvanceDialogue",target=manager(g))
    await u.bind(dialogue,"AdvanceButton","ContinueDialogue")
    h.layout(dialogue);h.save(dialogue)
    canvas=unreal.find_object(None,view.get_path_name()+":WidgetTree.HUDCanvas")
    child=await u.widget(view,dialogue.generated_class(),"DialogueView",canvas,True)
    u.place(child,0,-24,760,270,(.5,1),(.5,1));child.set_visibility(unreal.SlateVisibility.COLLAPSED)
    h.compile_blueprint(view,warnings_as_errors=True)
    g=h.edit(view,"ShowDialogue")
    end=h.invoke(g,g.find_graph_entry_pin(),dialogue,"PresentLine",target=h.get(g,"DialogueView"),Speaker=h.param(g,"Speaker"),Body=h.param(g,"Body")).find_then_pin()
    u.visibility(g,end,h.get(g,"DialogueView"),"Visible")
    g=h.edit(view,"HideDialogue");u.visibility(g,g.find_graph_entry_pin(),h.get(g,"DialogueView"),"Collapsed")
    h.layout(view,["ShowDialogue","HideDialogue"]);h.save(view)
    for func in ("ShowDialogue","HideDialogue"):
        g=h.edit(hud_bp,func);args={k:h.param(g,k) for k in ("Speaker","Body")} if func=="ShowDialogue" else {}
        h.invoke(g,g.find_graph_entry_pin(),view,func,target=h.get(g,"View"),**args)
    # Documents and conversations share one lock owner, preserving nested locks.
    for func,active in (("OpenDocument",True),("CloseDocument",False)):
        g=h.edit(hud_bp,func);h.clear_body(g)
        start=g.find_graph_entry_pin()
        if not active:start,_=h.branch(g,start,h.get(g,"bDocumentOpen"))
        end=h.setvar(g,start,"bDocumentOpen",active)
        args={k:h.param(g,k) for k in ("Title","Body")} if active else {}
        end=h.invoke(g,end,view,"PresentDocument" if active else "HideDocument",target=h.get(g,"View"),**args).find_then_pin()
        h.invoke(g,end,objective,"SetDocumentActive",target=manager(g),Active=active)
    h.layout(hud_bp,["OpenDocument","CloseDocument","ShowDialogue","HideDialogue"]);h.save(hud_bp)
    g=h.edit(objective,"RefreshNarrativeInputLock")
    blocked=h.any_true(g,h.get(g,"bDialogueActive"),h.get(g,"bDocumentActive"))
    changed=h.math(g,"NotEqual_BoolBool",blocked,h.get(g,"bNarrativeInputLocked"))
    yes,_=h.branch(g,g.find_graph_entry_pin(),changed)
    end=h.setvar(g,yes,"bNarrativeInputLocked",blocked)
    end=h.message(g,end,"SetGameplayInputEnabled",player(g),bEnabled=h.not_(g,blocked)).find_then_pin()
    interaction=h.asset("Narrative/BP_InteractionComponent")
    focus=h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=player(g),ComponentClass=interaction.generated_class().get_path_name()).find_result_pin()
    locked=h.get(g,"LockedFocusActor",target=focus,cls=interaction.generated_class())
    h.message(g,end,"SetRetakeBlocked",player(g),bBlocked=h.any_true(g,blocked,h.is_valid(g,locked)))
    g=h.edit(objective,"SetDocumentActive")
    end=h.setvar(g,g.find_graph_entry_pin(),"bDocumentActive",h.param(g,"Active"))
    h.invoke(g,end,objective,"AdvanceDialogueQueue")
    g=h.edit(objective,"QueueDialogue")
    yes,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,"bPresentationEnabled"))
    exists=h.call(g,"/Script/Engine.DataTableFunctionLibrary:DoesDataTableRowExist",yes,Table=h.asset("Narrative/DT_Dialogue").get_path_name(),RowName=h.param(g,"RowName"))
    yes,_=h.branch(g,exists.find_then_pin(),exists.find_result_pin())
    yes,no=h.branch(g,yes,h.any_true(g,h.get(g,"bDialogueActive"),h.get(g,"bDocumentActive")))
    h.call(g,"/Script/Engine.KismetArrayLibrary:Array_Add",yes,TargetArray=h.get(g,"DialogueQueue"),NewItem=h.param(g,"RowName"))
    h.invoke(g,no,objective,"StartDialogue",RowName=h.param(g,"RowName"))
    g=h.edit(objective,"StartDialogue")
    end=h.setvar(g,g.find_graph_entry_pin(),"bDialogueActive",True)
    end=h.invoke(g,end,objective,"RefreshNarrativeInputLock").find_then_pin()
    end=h.message(g,end,"ClearRetakeHistory",player(g)).find_then_pin()
    h.invoke(g,end,objective,"ShowDialogueRow",RowName=h.param(g,"RowName"))
    g=h.edit(objective,"ShowDialogueRow")
    row=h.table_row(g,g.find_graph_entry_pin(),h.asset("Narrative/DT_Dialogue"),h.param(g,"RowName"))
    fields=h.break_struct(g,row.find_result_pin())
    end=h.setvar(g,row.find_then_pin(),"CurrentDialogueRow",h.param(g,"RowName"));end=h.setvar(g,end,"NextDialogueRow",fields["NextRow"])
    end=h.emit(g,end,"OnDialogueStarted",Row=h.param(g,"RowName"))
    end,typed=hud(g,end)
    index=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=fields["Speaker"]).find_result_pin()
    for i,label in enumerate(("Agent","Jack","Supervisor","Director","Future Self","Interventor","Department of Continuity")):
        yes,end=h.branch(g,end,h.math(g,"EqualEqual_IntInt",index,i))
        show=h.invoke(g,yes,hud_bp,"ShowDialogue",target=typed,Speaker=label,Body=fields["Text"])
        timed,_=h.branch(g,show.find_then_pin(),h.math(g,"Greater_DoubleDouble",fields["Duration"],0))
        h.call(g,"/Script/Engine.KismetSystemLibrary:K2_SetTimer",timed,Object=h.self_pin(g),FunctionName="AdvanceDialogue",Time=fields["Duration"],bLooping=False)
    # A malformed row is rejected before starting, and cannot hold an input lock.
    end=h.setvar(g,row.find_output_pin("RowNotFound"),"bDialogueActive",False)
    h.invoke(g,end,objective,"AdvanceDialogueQueue")
    g=h.edit(objective,"AdvanceDialogue")
    yes,_=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,"bDialogueActive"),h.not_(g,h.get(g,"bDocumentActive"))))
    timer=h.call(g,"/Script/Engine.KismetSystemLibrary:K2_ClearTimer",yes,Object=h.self_pin(g),FunctionName="AdvanceDialogue")
    end=h.emit(g,timer.find_then_pin(),"OnDialogueFinished",Row=h.get(g,"CurrentDialogueRow"))
    has_next=h.call(g,"/Script/Engine.KismetMathLibrary:NotEqual_NameName",A=h.get(g,"NextDialogueRow"),B="").find_result_pin()
    yes,no=h.branch(g,end,has_next)
    h.invoke(g,yes,objective,"ShowDialogueRow",RowName=h.get(g,"NextDialogueRow"))
    end=h.setvar(g,no,"bDialogueActive",False)
    end=h.setvar(g,end,"CurrentDialogueRow","");end=h.setvar(g,end,"NextDialogueRow","")
    end,typed=hud(g,end);end=h.invoke(g,end,hud_bp,"HideDialogue",target=typed).find_then_pin()
    h.invoke(g,end,objective,"AdvanceDialogueQueue")
    g=h.edit(objective,"AdvanceDialogueQueue")
    blocked=h.any_true(g,h.get(g,"bDialogueActive"),h.get(g,"bDocumentActive"))
    yes,no=h.branch(g,g.find_graph_entry_pin(),blocked)
    h.invoke(g,yes,objective,"RefreshNarrativeInputLock")
    length=h.call(g,"/Script/Engine.KismetArrayLibrary:Array_Length",TargetArray=h.get(g,"DialogueQueue")).find_result_pin()
    yes,no2=h.branch(g,no,h.math(g,"Greater_IntInt",length,0))
    item=h.call(g,"/Script/Engine.KismetArrayLibrary:Array_Get",TargetArray=h.get(g,"DialogueQueue"),Index=0).find_output_pin("Item")
    # Store the first item before removing it from the live array.
    end=h.setvar(g,yes,"NextDialogueRow",item)
    remove=h.call(g,"/Script/Engine.KismetArrayLibrary:Array_Remove",end,TargetArray=h.get(g,"DialogueQueue"),IndexToRemove=0)
    h.invoke(g,remove.find_then_pin(),objective,"StartDialogue",RowName=h.get(g,"NextDialogueRow"))
    h.invoke(g,no2,objective,"RefreshNarrativeInputLock")
    g=h.edit(objective,"PresentStoryPhase")
    yes,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,"bPresentationEnabled"))
    number=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=h.param(g,"Phase")).find_result_pin()
    for i,rows in ((1,("JackFound_01","FutureMessage_01")),(4,("Truth_01","Correction_Order"))):
        yes,no=h.branch(g,yes,h.math(g,"EqualEqual_IntInt",number,i))
        for row_name in rows:yes=h.invoke(g,yes,objective,"QueueDialogue",RowName=row_name).find_then_pin()
        yes=no
    g=h.edit(objective,"StartBriefing");h.invoke(g,g.find_graph_entry_pin(),objective,"QueueDialogue",RowName="Briefing_01")
    g,begin=h.event(objective,"ReceiveBeginPlay")
    end=h.setvar(g,begin.find_then_pin(),"bPresentationEnabled",True)
    h.call(g,"/Script/Engine.KismetSystemLibrary:K2_SetTimer",end,Object=h.self_pin(g),FunctionName="StartBriefing",Time=.2,bLooping=False)
    # Attach presentation after the existing phase notifications, preserving the sole writer.
    g=h.edit(objective,"CommitStoryPhase")
    candidates=[n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_CallDelegate" and "OnChecklistUpdated" in str(n.get_node_title()).replace(" ","")]
    assert len(candidates)==1
    pin=candidates[0].find_then_pin();previous=pin.list_connected_pins();pin.break_pin_links()
    call=h.invoke(g,pin,objective,"PresentStoryPhase",Phase=h.param(g,"NewPhase"))
    for target in previous:h.connect(call.find_then_pin(),target)
    h.layout(objective);h.save(objective)
    pawn=h.asset("Narrative/Test/BP_TestPlayer_C")
    g=h.edit(pawn,"HandleTestUse");h.clear_body(g)
    end,typed=hud(g,g.find_graph_entry_pin())
    yes,no=h.branch(g,end,h.get(g,"bDocumentOpen",typed,hud_bp.generated_class()))
    h.invoke(g,yes,hud_bp,"CloseDocument",target=typed)
    obj=manager(g);yes,no=h.branch(g,no,h.get(g,"bDialogueActive",obj,objective.generated_class()))
    h.invoke(g,yes,objective,"AdvanceDialogue",target=obj)
    yes,_=h.branch(g,no,h.get(g,"bTestGameplayInputEnabled"))
    h.invoke(g,yes,interaction,"TryInteract",target=h.get(g,"BP_InteractionComponent"))
    h.layout(pawn,["HandleTestUse"]);h.save(pawn)
    OUT["passed"]=True
async def guarded():
    try:await build()
    except Exception:OUT["error"]=traceback.format_exc();unreal.log_error(OUT["error"])
    finally:
        (repo/"Scripts/C/c06_build_result.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
        print("C06_BUILD "+json.dumps(OUT))
c_f1_loop=EditorEventLoopManager();c_f1_loop.__enter__();c_f1_task=c_f1_loop.loop.create_task(guarded())

