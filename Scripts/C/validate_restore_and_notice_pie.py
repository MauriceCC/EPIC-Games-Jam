"""Check replacement-pawn HUD binding, hideout release and the non-blocking notice."""
import unreal,json,traceback
from pathlib import Path
OUT={"passed":False,"checks":[]}
def check(name,value):
    OUT["checks"].append({"name":name,"passed":bool(value)})
    assert value,name
def p(obj,name):return obj.get_editor_property(name)
try:
    world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0)
    state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method("GetObjectiveManager");mode=unreal.GameplayStatics.get_game_mode(world);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();view=p(hud,"View")
    for _ in range(40):
        if not p(manager,"bDialogueActive"):break
        pawn.call_method("HandleTestUse")
    events=type(p(unreal.get_default_object(unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C').generated_class()),'EventToReport'))
    pawn.call_method("ReportTestStoryEvent",args=(events.cast(11),""))
    check("Existing story event displays the continuity notice",p(view,"ContinuityText").get_visibility()==unreal.SlateVisibility.VISIBLE and str(p(view,"ContinuityText").get_text())=="CONTINUITY ALTERED")
    check("Notice changes neither phase nor input locks",state.call_method("GetCurrentPhase").value==0 and p(pawn,"bTestGameplayInputEnabled") and not p(pawn,"bTestRetakeBlocked"))
    statics=unreal.get_default_object(unreal.GameplayStatics);bp=unreal.load_asset("/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C")
    source=statics.call_method("BeginDeferredActorSpawnFromClass",args=(world,bp.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    source=statics.call_method("FinishSpawningActor",args=(source,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    source.set_editor_property("EventToReport",events.cast(9))
    old=pawn;pawn.destroy_actor();source.call_method("ReportConfiguredEvent")
    pawn=unreal.GameplayStatics.get_player_pawn(world,0)
    check("Missing pawn is recreated through the existing GameMode defaults",pawn and pawn!=old and pawn.get_class().get_name()=="BP_TestPlayer_C_C")
    check("Replacement receives the checkpoint listener call",p(pawn,"CheckpointRestoreCount")==1)
    check("HUD view is preserved across replacement",p(pc.get_hud(),"View")==view and view.is_in_viewport())
    pawn.set_editor_property("SimHealth",42);pawn.call_method("PublishTestResources")
    check("Native possession notification rebinds the HUD to the new components",abs(p(view,"HealthBar").get_editor_property("percent")-.42)<.0001)
    hideout=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset("/Game/Unscripted/Narrative/BP_Hideout").generated_class()))
    hideout.call_method("Interact",args=(pawn,))
    check("Replacement player can enter a hideout",p(hideout,"bOccupied") and p(pawn,"bTestRetakeBlocked") and p(p(pawn,"TestStealth"),"bTestHidden"))
    before=pawn.get_actor_location();pawn.call_method("MoveTestPawn",args=(unreal.Vector(60,0,0),))
    check("Test navigation respects the hideout movement lock",pawn.get_actor_location().distance(before)<.1)
    source.call_method("ReportConfiguredEvent")
    check("Checkpoint releases reversible C hideout occupancy",not p(hideout,"bOccupied") and p(hideout,"Occupant") is None and not p(p(pawn,"TestStealth"),"bTestHidden"))
    check("Restore clears the hideout focus and Retake lock",p(pawn,"BP_InteractionComponent").get_editor_property("LockedFocusActor") is None and not p(pawn,"bTestRetakeBlocked") and not pc.is_move_input_ignored())
    manager.call_method("QueueDialogue",args=("Correction_Order",))
    source.call_method("ReportConfiguredEvent")
    check("Restore during a conversation preserves narrative locks",p(manager,"bDialogueActive") and str(p(manager,"CurrentDialogueRow"))=="Correction_Order" and p(pawn,"bTestRetakeBlocked") and not p(pawn,"bTestGameplayInputEnabled"))
    pawn.call_method("HandleTestUse")
    check("Dialogue completion after restore releases movement exactly once",not p(manager,"bDialogueActive") and p(pawn,"bTestGameplayInputEnabled") and not pc.is_move_input_ignored())
    check("Repeated restores preserve the single progression manager",state.call_method("GetObjectiveManager")==manager and state.call_method("GetCurrentPhase").value==0)
    source.destroy_actor();OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    OUT["check_count"]=len(OUT["checks"])
    (Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c_restore_notice_pie_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_RESTORE_NOTICE_PIE "+json.dumps(OUT))
