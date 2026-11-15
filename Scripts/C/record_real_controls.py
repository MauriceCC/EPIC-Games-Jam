"""Record live Slate keyboard results without modifying any asset."""
import unreal,json
from pathlib import Path
world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
view=unreal.GameplayStatics.get_player_controller(world,0).get_hud().get_editor_property("View")
if "c_real_controls" not in globals():c_real_controls={"passed":False,"checks":[]}
def check(name,value):
    c_real_controls["checks"].append({"name":name,"passed":bool(value)})
    assert value,name
if c_control_stage=="hidden":
    check("Actual Tab hides the checklist",view.get_editor_property("ChecklistView").get_visibility()==unreal.SlateVisibility.COLLAPSED)
elif c_control_stage=="visible":
    check("Actual Tab reopens the checklist",view.get_editor_property("ChecklistView").get_visibility()==unreal.SlateVisibility.VISIBLE)
    for name,want in (("HealthBar",.65),("StaminaBar",.35),("CutCooldownBar",.6),("DetectionBar",.7)):
        check("Actual key updates "+name,abs(view.get_editor_property(name).get_editor_property("percent")-want)<.0001)
    check("Actual key updates Retake",str(view.get_editor_property("RetakeText").get_text())=="Retake 1 / 2")
elif c_control_stage=="notice":
    check("Actual X shows the notice",view.get_editor_property("ContinuityText").get_visibility()==unreal.SlateVisibility.VISIBLE)
elif c_control_stage=="expired":
    check("Real notice timer expires",view.get_editor_property("ContinuityText").get_visibility()==unreal.SlateVisibility.COLLAPSED)
    c_real_controls["passed"]=True
c_real_controls["check_count"]=len(c_real_controls["checks"])
(Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c_f1_real_controls_validation.json").write_text(json.dumps(c_real_controls,indent=2),encoding="utf-8")
unreal.get_default_object(unreal.load_class(None,"/Script/UMG.WidgetBlueprintLibrary")).call_method("SetFocusToGameViewport")
print("C_REAL_CONTROLS",c_control_stage,c_real_controls)
