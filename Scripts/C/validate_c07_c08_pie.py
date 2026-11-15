"""Check actual dispatcher-driven HUD updates and intermediate checklist animation frames."""
import unreal,json,traceback
from pathlib import Path
OUT={"passed":False,"checks":[]}
def check(name,value):
    OUT["checks"].append({"name":name,"passed":bool(value)})
    assert value,name
def p(obj,name):return obj.get_editor_property(name)
try:
    world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
    pawn=unreal.GameplayStatics.get_player_pawn(world,0);state=unreal.GameplayStatics.get_game_state(world)
    manager=state.call_method("GetObjectiveManager");hud=unreal.GameplayStatics.get_player_controller(world,0).get_hud();view=p(hud,"View");checklist=p(view,"ChecklistView")
    check("Checklist starts with the three protective directives",str(p(checklist,"ItemText0").get_text())=="Locate Jack." and "Protect Jack" in str(p(checklist,"ItemText1").get_text()) and "identity secret" in str(p(checklist,"ItemText2").get_text()) and p(checklist,"ItemRow3").get_visibility()==unreal.SlateVisibility.COLLAPSED)
    check("HUD health and stamina initialized through real dispatchers",p(view,"HealthBar").get_editor_property('percent')==1 and p(view,"StaminaBar").get_editor_property('percent')==1)
    for name,value in (("SimHealth",65),("SimStamina",35),("SimRetake",1),("SimCooldown",6),("SimDetection",.7)):pawn.set_editor_property(name,value)
    pawn.call_method("PublishTestResources")
    for name,want in (("HealthBar",.65),("StaminaBar",.35),("CutCooldownBar",.6),("DetectionBar",.7)):
        check("Dispatcher updates "+name,abs(p(view,name).get_editor_property('percent')-want)<.0001)
    check("Retake counter consumes the existing integer width",str(p(view,"RetakeText").get_text())=="Retake 1 / 2")
    hud.call_method("ToggleChecklist");check("Checklist can be hidden",checklist.get_visibility()==unreal.SlateVisibility.COLLAPSED)
    hud.call_method("ToggleChecklist");check("Checklist can be reopened",checklist.get_visibility()==unreal.SlateVisibility.VISIBLE)
    def drain():
        for _ in range(40):
            if not p(manager,"bDialogueActive"):return
            pawn.call_method("HandleTestUse")
        raise AssertionError("Dialogue queue did not drain")
    drain()
    pawn.call_method("ReportTestStoryEvent",args=(type(p(unreal.get_default_object(unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C').generated_class()),'EventToReport')).cast(0),""))
    check("Phase dispatcher changes the objective",str(p(view,"ObjectiveText").get_text())=="Open the escape route.")
    check("Completed checklist item has a visible strike",p(checklist,"Strike0").get_visibility()==unreal.SlateVisibility.VISIBLE)
    drain()
    source_enum=type(p(unreal.get_default_object(unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C').generated_class()),'EventToReport'))
    for index,param in ((1,""),(2,""),(3,"NursingRecord"),(3,"FabricatedReport"),(4,"")):
        pawn.call_method("ReportTestStoryEvent",args=(source_enum.cast(index),param))
    check("Truth phase starts an actual rewrite",p(checklist,"bRewriteAnimating") and p(checklist,"bHasRewritten"))
    # Pause the live timer to inspect deterministic intermediate frames, then resume it.
    unreal.get_default_object(unreal.SystemLibrary).call_method("K2_ClearTimer",args=(checklist,"AdvanceRewrite"))
    checklist.call_method("AdvanceRewrite")
    check("The original orders fade before replacement",.7<p(checklist,"ChecklistRows").get_render_opacity()<.8 and "identity secret" in str(p(checklist,"ItemText2").get_text()))
    for _ in range(3):checklist.call_method("AdvanceRewrite")
    check("Rewrite swaps to four explicit fabricated-case orders","Frame Jack as Jack the Ripper."==str(p(checklist,"ItemText2").get_text()) and "Eliminate Jack" in str(p(checklist,"ItemText3").get_text()) and p(checklist,"ItemRow3").get_visibility()==unreal.SlateVisibility.VISIBLE)
    check("The replacement begins faded",p(checklist,"ChecklistRows").get_render_opacity()<.1)
    for _ in range(4):checklist.call_method("AdvanceRewrite")
    check("Animation finishes fully visible",not p(checklist,"bRewriteAnimating") and p(checklist,"ChecklistRows").get_render_opacity()==1)
    drain()
    rows=[str(x) for x in p(pawn,"CompletedDialogueRows")]
    check("Correction_Order emits exactly one completion",rows.count("Correction_Order")==1)
    check("All queued scene rows finish in order",rows==["Briefing_0"+str(i) for i in range(1,6)]+["JackFound_01","JackFound_02","JackFound_03","FutureMessage_01"]+["Truth_0"+str(i) for i in range(1,6)]+["Correction_Order"])
    check("Final objective does not demand incrimination",str(p(view,"ObjectiveText").get_text())=="Choose which account to archive.")
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    OUT["check_count"]=len(OUT["checks"])
    (Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c07_c08_pie_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C07_C08_PIE "+json.dumps(OUT))

