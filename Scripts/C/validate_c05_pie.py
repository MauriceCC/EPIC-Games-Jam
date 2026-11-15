"""Verify actual evidence interactions, readable UMG content, and reveal guards."""
import unreal,json,traceback
from pathlib import Path
OUT={"passed":False,"checks":[]};spawned=[]
def check(name,value):
    OUT["checks"].append({"name":name,"passed":bool(value)})
    assert value,name
def prop(obj,name):return obj.get_editor_property(name)
try:
    world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
    pawn=unreal.GameplayStatics.get_player_pawn(world,0)
    hud=unreal.GameplayStatics.get_player_controller(world,0).get_hud()
    state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method("GetObjectiveManager")
    def drain():
        for _ in range(40):
            if not prop(manager,"bDialogueActive"):return
            pawn.call_method("HandleTestUse")
    drain()
    view=prop(hud,"View");doc=prop(view,"DocumentView")
    check("Real HUD has been added to the viewport",view.is_in_viewport())
    check("Document starts closed",not prop(hud,"bDocumentOpen"))
    statics=unreal.get_default_object(unreal.GameplayStatics)
    def spawn(name):
        bp=unreal.load_asset("/Game/Unscripted/Narrative/"+name)
        actor=statics.call_method("BeginDeferredActorSpawnFromClass",args=(world,bp.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        actor=statics.call_method("FinishSpawningActor",args=(actor,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));spawned.append(actor);return actor
    source=spawn("Test/BP_StoryEventTestSource_C");enum=type(prop(source,"EventToReport"))
    def report(index,param=""):
        source.set_editor_property("EventToReport",enum.cast(index));source.set_editor_property("EventParam",param);source.call_method("ReportConfiguredEvent")
    nursing=spawn("BP_Evidence");fabricated=spawn("BP_Evidence");duplicate=spawn("BP_Evidence")
    fabricated.set_editor_property("EvidenceType",type(prop(fabricated,"EvidenceType")).cast(1))
    nursing.call_method("Interact",args=(pawn,))
    check("Evidence cannot be lost before its phase",not prop(nursing,"bConsumed"))
    report(0);report(1);report(2)
    drain()
    nursing.call_method("Interact",args=(pawn,))
    check("Nursing record is registered once",prop(manager,"bEvidenceFound") and prop(nursing,"InteractionCount")==1)
    check("One evidence does not reveal truth",state.call_method("GetCurrentPhase").value==3)
    check("Document is visibly readable",doc.get_visibility()==unreal.SlateVisibility.VISIBLE and str(prop(doc,"DocumentTitle").get_text())=="Nursing Record" and "innocence" in str(prop(doc,"DocumentBody").get_text()))
    check("Document locks gameplay and Retake",not prop(pawn,"bTestGameplayInputEnabled") and prop(pawn,"bTestRetakeBlocked"))
    pawn.call_method("HandleTestUse")
    check("E action closes the document and restores gameplay",not prop(hud,"bDocumentOpen") and prop(pawn,"bTestGameplayInputEnabled") and not prop(pawn,"bTestRetakeBlocked"))
    duplicate.call_method("Interact",args=(pawn,));hud.call_method("CloseDocument")
    check("A duplicate type cannot satisfy both evidence guards",state.call_method("GetCurrentPhase").value==3 and not prop(manager,"bFalseReportFound"))
    fabricated.call_method("Interact",args=(pawn,))
    check("Two distinct records trigger guarded TruthRevealed",state.call_method("GetCurrentPhase").value==4 and prop(manager,"bFalseReportFound"))
    check("Fabrication text remains English and names innocent Jack",str(prop(doc,"DocumentTitle").get_text())=="Fabricated Report" and "innocent Jack" in str(prop(doc,"DocumentBody").get_text()))
    before=prop(fabricated,"InteractionCount");fabricated.call_method("Interact",args=(pawn,))
    check("Consumed evidence cannot fire twice",prop(fabricated,"InteractionCount")==before)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    for actor in spawned:
        if unreal.SystemLibrary.is_valid(actor):actor.destroy_actor()
    OUT["check_count"]=len(OUT["checks"])
    (Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c05_pie_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C05_PIE "+json.dumps(OUT))
