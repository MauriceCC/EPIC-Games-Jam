"""Validate the actual dialogue chain and nested document/input locks in PIE."""
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
    manager=state.call_method("GetObjectiveManager");hud=unreal.GameplayStatics.get_player_controller(world,0).get_hud()
    view=p(hud,"View");dialogue=p(view,"DialogueView")
    check("Briefing starts from the imported DataTable",str(p(manager,"CurrentDialogueRow"))=="Briefing_01" and "OPERATION 1888" in str(p(dialogue,"BodyText").get_text()))
    check("Dialogue locks gameplay and personal Retake",not p(pawn,"bTestGameplayInputEnabled") and p(pawn,"bTestRetakeBlocked"))
    check("Dialogue hides the world-use prompt",str(p(view,"InteractionText").get_text())=="" and p(view,"InteractionBackdrop").get_visibility()==unreal.SlateVisibility.COLLAPSED)
    sequence=[]
    for i in range(5):
        sequence.append(str(p(manager,"CurrentDialogueRow")));pawn.call_method("HandleTestUse")
    check("NextRow plays all five briefing lines in order",sequence==["Briefing_0"+str(i) for i in range(1,6)])
    check("Last line restores gameplay and Retake",not p(manager,"bDialogueActive") and p(pawn,"bTestGameplayInputEnabled") and not p(pawn,"bTestRetakeBlocked"))
    manager.call_method("QueueDialogue",args=("MissingRow",))
    check("Invalid row cannot create a dangling input lock",not p(manager,"bDialogueActive") and not p(manager,"bNarrativeInputLocked"))
    manager.call_method("QueueDialogue",args=("JackFound_01",));manager.call_method("QueueDialogue",args=("FutureMessage_01",))
    sequence=[]
    for i in range(4):
        sequence.append(str(p(manager,"CurrentDialogueRow")))
        if i<3:check("Queued dialogue keeps Retake blocked "+str(i),p(pawn,"bTestRetakeBlocked"))
        pawn.call_method("HandleTestUse")
    check("A queued scene follows the NextRow chain",sequence==["JackFound_01","JackFound_02","JackFound_03","FutureMessage_01"])
    check("Queue drains and unlocks",not p(manager,"bDialogueActive") and len(p(manager,"DialogueQueue"))==0 and p(pawn,"bTestGameplayInputEnabled"))
    manager.call_method("QueueDialogue",args=("Correction_Order",))
    check("Contract row is preserved exactly",str(p(manager,"CurrentDialogueRow"))=="Correction_Order")
    hud.call_method("OpenDocument",args=("Test record","A document can temporarily cover a transmission."))
    check("Document keeps the world-use prompt hidden",str(p(view,"InteractionText").get_text())=="")
    manager.call_method("AdvanceDialogue")
    check("Document prevents accidental dialogue advancement",str(p(manager,"CurrentDialogueRow"))=="Correction_Order")
    pawn.call_method("HandleTestUse")
    check("Closing document preserves active dialogue lock",not p(hud,"bDocumentOpen") and p(manager,"bDialogueActive") and p(pawn,"bTestRetakeBlocked") and not p(pawn,"bTestGameplayInputEnabled"))
    pawn.call_method("HandleTestUse")
    check("Finishing Correction_Order unlocks once",not p(manager,"bDialogueActive") and p(pawn,"bTestGameplayInputEnabled") and not p(pawn,"bTestRetakeBlocked"))
    check("Dialogue is collapsed after completion",dialogue.get_visibility()==unreal.SlateVisibility.COLLAPSED)
    check("Finishing the modal UI restores the contextual prompt",str(p(view,"InteractionText").get_text()).startswith("[E] "))
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    OUT["check_count"]=len(OUT["checks"])
    (Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c06_pie_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C06_PIE "+json.dumps(OUT))
