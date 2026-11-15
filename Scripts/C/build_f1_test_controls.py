"""C-owned simulation keys and dispatcher fixtures; never implement A/B gameplay."""
import unreal,sys,json,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h);OUT={"passed":False}
try:
    pawn=h.asset("Narrative/Test/BP_TestPlayer_C")
    for name,typ,value in (("SimHealth",h.basic("real"),100),("SimStamina",h.basic("real"),100),("SimRetake",h.basic("int64"),2),("SimCooldown",h.basic("real"),0),("SimDetection",h.basic("real"),0),("CompletedDialogueRows",h.array_type(h.basic("name")),"()")):
        h.variable(pawn,name,typ,value,True,"C Test Simulation")
    for name,ins in (("PublishTestResources",[]),("ReportTestStoryEvent",[("Event",h.enum_type("EStoryEvent")),("Param",h.basic("name"))])):h.function(pawn,name,ins)
    h.compile_blueprint(pawn,warnings_as_errors=True)
    g=h.edit(pawn,"PublishTestResources");end=g.find_graph_entry_pin()
    for member,signal,args in (("BP_HealthComponent","OnHealthChanged",{"Current":h.get(g,"SimHealth"),"Max":100}),("BP_CombatComponent","OnStaminaChanged",{"Current":h.get(g,"SimStamina"),"Max":100}),("BP_TemporalComponent","OnRetakeChargesChanged",{"Current":h.get(g,"SimRetake"),"Max":2}),("BP_TemporalComponent","OnTemporalCutCooldown",{"Remaining":h.get(g,"SimCooldown"),"Total":10}),("TestStealth","OnDetectionChanged",{"Level":h.get(g,"SimDetection")})):
        end=h.emit_to(g,end,h.get(g,member),signal,**args)
    g=h.edit(pawn,"ReportTestStoryEvent")
    state=h.call(g,"/Script/Engine.GameplayStatics:GetGameState").find_result_pin()
    h.message(g,g.find_graph_entry_pin(),"ReportStoryEvent",state,Event=h.param(g,"Event"),Source=h.self_pin(g),Param=h.param(g,"Param"))
    g=h.edit(pawn,"EventGraph")
    bind=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_AssignDelegate")
    state=h.call(g,"/Script/Engine.GameplayStatics:GetGameState").find_result_pin()
    obj=h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=state,ComponentClass=h.asset("Narrative/BP_ObjectiveManager").generated_class().get_path_name()).find_result_pin()
    end,callback=h.bind_assign(g,bind.find_then_pin(),obj,"OnDialogueFinished")
    h.call(g,"/Script/Engine.KismetArrayLibrary:Array_Add",callback.find_then_pin(),TargetArray=h.get(g,"CompletedDialogueRows"),NewItem=callback.find_output_pin("Row"))
    pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
    end=h.setvar(g,end,"bShowMouseCursor",True,pc,unreal.PlayerController.static_class())
    end=h.call(g,"/Script/UMG.WidgetBlueprintLibrary:SetInputMode_GameAndUIEx",end,PlayerController=pc,InWidgetToFocus=None,InMouseLockMode="DoNotLock",bHideCursorDuringCapture=False,bFlushInput=False).find_then_pin()
    h.call(g,"/Script/Engine.KismetSystemLibrary:K2_SetTimer",end,Object=h.self_pin(g),FunctionName="PublishTestResources",Time=.3,bLooping=False)
    for key,event,param in (("1",0,""),("2",1,""),("3",2,""),("4",3,"NursingRecord"),("5",3,"FabricatedReport"),("6",4,""),("7",13,""),("8",6,""),("9",7,"OfficialCut"),("0",7,"AuthenticRecord"),("X",11,""),("P",10,"C_TestCheckpoint"),("Backspace",9,"")):
        g,node=h.key_event(pawn,key);h.invoke(g,node.find_output_pin("Pressed"),pawn,"ReportTestStoryEvent",Event="NewEnumerator"+str(event),Param=param)
    for key,var,typ,value in (("H","SimHealth",h.basic("real"),65),("J","SimStamina",h.basic("real"),35),("K","SimRetake",h.basic("int64"),1),("L","SimCooldown",h.basic("real"),6),("M","SimDetection",h.basic("real"),.7)):
        g,node=h.key_event(pawn,key)
        end=h.setvar(g,node.find_output_pin("Pressed"),var,value);h.invoke(g,end,pawn,"PublishTestResources")
    # This double sets movement input only when its enabled state actually changes.
    g=h.edit(pawn,"EventGraph")
    event=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_Event" and h.valid(n.find_output_pin("bEnabled")))
    old=event.find_then_pin().list_connected_pins()[0];event.find_then_pin().break_pin_links()
    changed=h.math(g,"NotEqual_BoolBool",event.find_output_pin("bEnabled"),h.get(g,"bTestGameplayInputEnabled"))
    yes,_=h.branch(g,event.find_then_pin(),changed);h.connect(yes,old)
    h.layout(pawn);h.save(pawn);OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    (repo/"Scripts/C/c_f1_controls_build.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_TEST_CONTROLS "+json.dumps(OUT))
