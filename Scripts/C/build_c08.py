"""C-08: reactive UMG HUD; consume published dispatchers without foreign casts or Tick."""
import unreal,sys,json,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h,umg_helpers_c as u
from importlib import reload
h=reload(h);u=reload(u)
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
OUT={"passed":False}
def declare(bp,name,inputs=()):
    g=h.edit(bp,name)
    if g:h.clear_body(g);return g
    return h.function(bp,name,inputs)
def player(g):return h.call(g,"/Script/Engine.GameplayStatics:GetPlayerPawn",PlayerIndex=0).find_result_pin()
def component(g,path,actor=None):return h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=actor or player(g),ComponentClass=h.asset(path).generated_class().get_path_name()).find_result_pin()
def manager(g):return component(g,"Narrative/BP_ObjectiveManager",h.call(g,"/Script/Engine.GameplayStatics:GetGameState").find_result_pin())
async def build():
    view=h.asset("UI/WBP_HUD");hud=h.asset("UI/BP_HUD");objective=h.asset("Narrative/BP_ObjectiveManager")
    canvas=unreal.find_object(None,view.get_path_name()+":WidgetTree.HUDCanvas")
    panel,box=await u.panel(view,"StatusPanel",canvas);u.place(panel,24,24,340,350)
    await u.label(view,box,"OperationText","UNSCRIPTED / OPERATION 1888",12,u.GOLD)
    for name,title,color in (("Health","Health",u.CYAN),("Stamina","Stamina",u.GOLD),("CutCooldown","Frame Cut cooldown",u.MUTED),("Detection","Detection",unreal.LinearColor(.75,.34,.26,1))):
        await u.label(view,box,name+"Caption",title,12,u.MUTED)
        size=await u.widget(view,unreal.SizeBox,name+"Area",box);size.set_height_override(9)
        bar=await u.widget(view,unreal.ProgressBar,name+"Bar",size,True);bar.set_fill_color_and_opacity(color);bar.set_percent(1 if name in ("Health","Stamina") else 0)
    await u.label(view,box,"RetakeText","Retake 2 / 2",15,u.PAPER,True)
    await u.label(view,box,"ObjectiveText","Locate Jack.",18,u.PAPER,True)
    prompt=await u.label(view,canvas,"InteractionText","",18,u.PAPER,True);u.place(prompt,0,-310,760,40,(.5,1),(.5,1))
    notice=await u.label(view,canvas,"ContinuityText","CONTINUITY ALTERED",24,u.GOLD,True);u.place(notice,0,28,760,45,(.5,0),(.5,0));notice.set_visibility(unreal.SlateVisibility.COLLAPSED)
    hint=await u.label(view,canvas,"TestHintText","",12,u.MUTED,True);u.place(hint,24,-20,1000,42,(0,1),(0,1))
    real=h.basic("real");integer=h.basic("int64");text=h.basic("text")
    specs={"SetHealth":[("Current",real),("Max",real)],"SetStamina":[("Current",real),("Max",real)],"SetRetake":[("Current",integer),("Max",integer)],"SetCutCooldown":[("Remaining",real),("Total",real)],"SetDetection":[("Level",real)],"SetInteraction":[("Prompt",text)],"SetObjective":[("Phase",h.enum_type("EStoryPhase"))]}
    for name,ins in specs.items():declare(view,name,ins)
    h.compile_blueprint(view,warnings_as_errors=True)
    for name,bar,a,b in (("SetHealth","HealthBar","Current","Max"),("SetStamina","StaminaBar","Current","Max"),("SetCutCooldown","CutCooldownBar","Remaining","Total")):
        g=h.edit(view,name)
        denominator=h.math(g,"FMax",h.param(g,b),.0001)
        fraction=h.math(g,"FClamp",h.math(g,"Divide_DoubleDouble",h.param(g,a),denominator),0,1)
        h.call(g,"/Script/UMG.ProgressBar:SetPercent",g.find_graph_entry_pin(),h.get(g,bar),InPercent=fraction)
    g=h.edit(view,"SetDetection")
    h.call(g,"/Script/UMG.ProgressBar:SetPercent",g.find_graph_entry_pin(),h.get(g,"DetectionBar"),InPercent=h.math(g,"FClamp",h.param(g,"Level"),0,1))
    g=h.edit(view,"SetRetake")
    current=h.call(g,"/Script/Engine.KismetStringLibrary:Conv_Int64ToString",InInt=h.param(g,"Current")).find_result_pin()
    maximum=h.call(g,"/Script/Engine.KismetStringLibrary:Conv_Int64ToString",InInt=h.param(g,"Max")).find_result_pin()
    first=h.call(g,"/Script/Engine.KismetStringLibrary:Concat_StrStr",A="Retake ",B=current).find_result_pin()
    first=h.call(g,"/Script/Engine.KismetStringLibrary:Concat_StrStr",A=first,B=" / ").find_result_pin()
    result=h.call(g,"/Script/Engine.KismetStringLibrary:Concat_StrStr",A=first,B=maximum).find_result_pin()
    u.set_text(g,g.find_graph_entry_pin(),"RetakeText",h.call(g,"/Script/Engine.KismetTextLibrary:Conv_StringToText",InString=result).find_result_pin())
    g=h.edit(view,"SetInteraction")
    empty=h.call(g,"/Script/Engine.KismetTextLibrary:TextIsEmpty",InText=h.param(g,"Prompt")).find_result_pin()
    yes,no=h.branch(g,g.find_graph_entry_pin(),empty);u.set_text(g,yes,"InteractionText","")
    prompt=h.call(g,"/Script/Engine.KismetTextLibrary:Conv_TextToString",InText=h.param(g,"Prompt")).find_result_pin()
    prompt=h.call(g,"/Script/Engine.KismetStringLibrary:Concat_StrStr",A="[E] ",B=prompt).find_result_pin()
    u.set_text(g,no,"InteractionText",h.call(g,"/Script/Engine.KismetTextLibrary:Conv_StringToText",InString=prompt).find_result_pin())
    g=h.edit(view,"SetObjective")
    index=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=h.param(g,"Phase")).find_result_pin();end=g.find_graph_entry_pin()
    for i,label in enumerate(("Locate Jack.","Open the escape route.","Protect Jack on the way to the refuge.","Examine the two records.","Choose which account to archive.","The record has been archived.")):
        yes,end=h.branch(g,end,h.math(g,"EqualEqual_IntInt",index,i));u.set_text(g,yes,"ObjectiveText",label)
    h.layout(view,list(specs));h.save(view)
    declare(hud,"SyncDialogue");declare(hud,"ScheduleDialogueSync");h.compile_blueprint(hud,warnings_as_errors=True)
    g=h.edit(hud,"ScheduleDialogueSync")
    h.call(g,"/Script/Engine.KismetSystemLibrary:K2_SetTimer",g.find_graph_entry_pin(),Object=h.self_pin(g),FunctionName="SyncDialogue",Time=.001,bLooping=False)
    g=h.edit(hud,"SyncDialogue")
    obj=manager(g);active=h.all_true(g,h.get(g,"bDialogueActive",obj,objective.generated_class()),h.not_(g,h.get(g,"bDocumentOpen")))
    yes,no=h.branch(g,g.find_graph_entry_pin(),active)
    h.invoke(g,no,hud,"HideDialogue")
    row=h.table_row(g,yes,h.asset("Narrative/DT_Dialogue"),h.get(g,"CurrentDialogueRow",obj,objective.generated_class()))
    fields=h.break_struct(g,row.find_result_pin());end=row.find_then_pin()
    index=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=fields["Speaker"]).find_result_pin()
    for i,label in enumerate(("Agent","Jack","Supervisor","Director","Future Self","Interventor","Department of Continuity")):
        yes,end=h.branch(g,end,h.math(g,"EqualEqual_IntInt",index,i));h.invoke(g,yes,hud,"ShowDialogue",Speaker=label,Body=fields["Text"])
    # Update the objective from the same phase snapshot used by the checklist.
    g=h.edit(hud,"UpdateChecklist")
    tail=next(n for n in g.list_all_nodes() if "RefreshChecklist" in str(n.get_node_title()).replace(" ",""))
    phase=next(n for n in g.list_all_nodes() if "GetStoryPhase" in str(n.get_node_title()).replace(" ","")).find_result_pin()
    h.invoke(g,tail.find_then_pin(),view,"SetObjective",target=h.get(g,"View"),Phase=phase)
    # Bind real component signals; all callbacks have the declaration's actual pin types.
    g=h.edit(hud,"EventGraph")
    initial=next(n for n in g.list_all_nodes() if "UpdateChecklist" in str(n.get_node_title()).replace(" ","") and n.find_execute_pin().list_connected_pins() and n.find_execute_pin().list_connected_pins()[0].get_owning_node().get_class().get_name()!="K2Node_CustomEvent")
    end=initial.find_then_pin()
    for path,signal,handler,params in (("Player/BP_HealthComponent","OnHealthChanged","SetHealth",("Current","Max")),("Player/BP_CombatComponent","OnStaminaChanged","SetStamina",("Current","Max")),("Player/BP_TemporalComponent","OnRetakeChargesChanged","SetRetake",("Current","Max")),("Player/BP_TemporalComponent","OnTemporalCutCooldown","SetCutCooldown",("Remaining","Total")),("Narrative/BP_InteractionComponent","OnFocusChanged","SetInteraction",("Prompt",))):
        end,callback=h.bind_assign(g,end,component(g,path),signal)
        h.invoke(g,callback.find_then_pin(),view,handler,target=h.get(g,"View"),**{p:callback.find_output_pin(p) for p in params})
    stealth=h.message(g,end,"GetStealthComponent",player(g))
    end,callback=h.bind_assign(g,stealth.find_then_pin(),stealth.find_result_pin(),"OnDetectionChanged")
    h.invoke(g,callback.find_then_pin(),view,"SetDetection",target=h.get(g,"View"),Level=callback.find_output_pin("Level"))
    for signal,handler in (("OnDialogueStarted","SyncDialogue"),("OnDialogueFinished","ScheduleDialogueSync")):
        end,callback=h.bind_assign(g,end,manager(g),signal)
        h.invoke(g,callback.find_then_pin(),hud,handler)
    h.invoke(g,end,hud,"SyncDialogue")
    # Documents also synchronize presentation when they cover an existing conversation.
    for name in ("OpenDocument","CloseDocument"):
        graph=h.edit(hud,name)
        tail=next(n for n in graph.list_all_nodes() if "SetDocumentActive" in str(n.get_node_title()).replace(" ",""))
        h.invoke(graph,tail.find_then_pin(),hud,"SyncDialogue")
    h.layout(hud);h.save(hud)
    # Remove direct UI coupling from progression. Dialogue presentation now listens to dispatchers.
    h.variable(objective,"FinishedDialogueRow",h.basic("name"),"")
    g=h.edit(objective,"ShowDialogueRow");h.clear_body(g)
    row=h.table_row(g,g.find_graph_entry_pin(),h.asset("Narrative/DT_Dialogue"),h.param(g,"RowName"));fields=h.break_struct(g,row.find_result_pin())
    end=h.setvar(g,row.find_then_pin(),"CurrentDialogueRow",h.param(g,"RowName"));end=h.setvar(g,end,"NextDialogueRow",fields["NextRow"])
    end=h.emit(g,end,"OnDialogueStarted",Row=h.param(g,"RowName"))
    yes,_=h.branch(g,end,h.math(g,"Greater_DoubleDouble",fields["Duration"],0))
    h.call(g,"/Script/Engine.KismetSystemLibrary:K2_SetTimer",yes,Object=h.self_pin(g),FunctionName="AdvanceDialogue",Time=fields["Duration"],bLooping=False)
    end=h.setvar(g,row.find_output_pin("RowNotFound"),"bDialogueActive",False);h.invoke(g,end,objective,"AdvanceDialogueQueue")
    g=h.edit(objective,"AdvanceDialogue");h.clear_body(g)
    yes,_=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,"bDialogueActive"),h.not_(g,h.get(g,"bDocumentActive"))))
    end=h.call(g,"/Script/Engine.KismetSystemLibrary:K2_ClearTimer",yes,Object=h.self_pin(g),FunctionName="AdvanceDialogue").find_then_pin()
    end=h.setvar(g,end,"FinishedDialogueRow",h.get(g,"CurrentDialogueRow"))
    more=h.call(g,"/Script/Engine.KismetMathLibrary:NotEqual_NameName",A=h.get(g,"NextDialogueRow"),B="").find_result_pin()
    yes,no=h.branch(g,end,more)
    end=h.emit(g,yes,"OnDialogueFinished",Row=h.get(g,"FinishedDialogueRow"));h.invoke(g,end,objective,"ShowDialogueRow",RowName=h.get(g,"NextDialogueRow"))
    end=h.setvar(g,no,"bDialogueActive",False);end=h.setvar(g,end,"CurrentDialogueRow","");end=h.setvar(g,end,"NextDialogueRow","")
    end=h.emit(g,end,"OnDialogueFinished",Row=h.get(g,"FinishedDialogueRow"));h.invoke(g,end,objective,"AdvanceDialogueQueue")
    h.layout(objective,["ShowDialogueRow","AdvanceDialogue"]);h.save(objective)
    OUT["passed"]=True
async def guarded():
    try:await build()
    except Exception:OUT["error"]=traceback.format_exc();unreal.log_error(OUT["error"])
    finally:
        (repo/"Scripts/C/c08_build_result.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
        print("C08_BUILD "+json.dumps(OUT))
c_f1_loop=EditorEventLoopManager();c_f1_loop.__enter__();c_f1_task=c_f1_loop.loop.create_task(guarded())
