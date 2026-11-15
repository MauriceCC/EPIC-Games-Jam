"""Verify checkpoint reporting and multicast restoration without rewinding narrative facts."""
import unreal,json,traceback
from pathlib import Path
OUT={"passed":False,"checks":[]};spawned=[]
def check(name,value):
    OUT["checks"].append({"name":name,"passed":bool(value)})
    assert value,name
def p(obj,name):return obj.get_editor_property(name)
try:
    world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0)
    state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method("GetObjectiveManager");mode=unreal.GameplayStatics.get_game_mode(world);hud=unreal.GameplayStatics.get_player_controller(world,0).get_hud();view=p(hud,"View")
    def drain():
        for _ in range(40):
            if not p(manager,"bDialogueActive"):return
            pawn.call_method("HandleTestUse")
        raise AssertionError("Dialogue did not drain")
    drain()
    check("GameMode captures an initial fallback checkpoint",p(mode,"bHasCheckpoint") and str(p(mode,"CheckpointId"))=="InitialSpawn")
    pos=pawn.get_actor_location();statics=unreal.get_default_object(unreal.GameplayStatics)
    def spawn(name,offset):
        bp=unreal.load_asset("/Game/Unscripted/Narrative/"+name);transform=unreal.Transform(location=pos+unreal.Vector(*offset))
        actor=statics.call_method("BeginDeferredActorSpawnFromClass",args=(world,bp.generated_class(),transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        actor=statics.call_method("FinishSpawningActor",args=(actor,transform,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));spawned.append(actor);return actor
    cp=spawn("BP_Checkpoint",(60,0,-100));cp.call_method("Interact",args=(pawn,))
    desired=cp.call_method("GetRespawnTransform").translation
    check("Physical checkpoint saves its raised respawn marker",str(p(mode,"CheckpointId"))=="C_Checkpoint" and p(mode,"RespawnTransform").translation.distance(desired)<.1)
    observer=spawn("Test/BP_TestPlayer_C",(1000,500,0))
    enum=type(p(unreal.get_default_object(unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C').generated_class()),'EventToReport'))
    def report(index,param=""):pawn.call_method("ReportTestStoryEvent",args=(enum.cast(index),param))
    report(0);drain()
    door=spawn("BP_Door",(100,0,0));door.call_method("Interact",args=(pawn,));report(2)
    evidence=spawn("BP_Evidence",(120,0,0));evidence.call_method("Interact",args=(pawn,));hud.call_method("CloseDocument")
    check("Story facts exist before restore",state.call_method("GetCurrentPhase").value==3 and p(manager,"bEvidenceFound") and p(door,"bIsOpen") and p(evidence,"bConsumed"))
    pawn.set_actor_location(pos+unreal.Vector(900,0,0),False,True)
    for name,value in (("SimHealth",0),("SimStamina",10),("SimRetake",0),("SimCooldown",8),("SimDetection",1)):pawn.set_editor_property(name,value)
    pawn.call_method("PublishTestResources");report(9)
    check("Defeat routes through GameState to GameMode",p(mode,"RestoreCount")==1 and not p(mode,"bRestoreInProgress"))
    check("The player receives the published listener call",p(pawn,"CheckpointRestoreCount")==1 and str(p(pawn,"LastRestoredCheckpoint"))=="C_Checkpoint")
    check("Every actor listener is notified",p(observer,"CheckpointRestoreCount")==1)
    check("Player is moved to the respawn marker",pawn.get_actor_location().distance(desired)<.1)
    check("The C double restores two Retake charges",p(pawn,"SimRetake")==2 and str(p(view,"RetakeText").get_text())=="Retake 2 / 2")
    check("Resource dispatchers update the existing HUD after restore",p(view,"HealthBar").get_editor_property("percent")==1 and p(view,"StaminaBar").get_editor_property("percent")==1)
    check("Checkpoint never resets the story phase or evidence facts",state.call_method("GetCurrentPhase").value==3 and p(manager,"bEvidenceFound") and not p(manager,"bFalseReportFound"))
    check("Persistent world interactions stay consumed",p(door,"bIsOpen") and not door.get_actor_enable_collision() and p(evidence,"bConsumed"))
    mode.call_method("SaveCheckpoint",args=("",unreal.Transform()))
    check("Empty checkpoint identifiers are rejected",str(p(mode,"CheckpointId"))=="C_Checkpoint")
    report(9)
    check("Subsequent restores remain usable",p(mode,"RestoreCount")==2 and p(pawn,"CheckpointRestoreCount")==2 and p(observer,"CheckpointRestoreCount")==2)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    for actor in spawned:
        if unreal.SystemLibrary.is_valid(actor):actor.destroy_actor()
    OUT["check_count"]=len(OUT["checks"])
    (Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c09_pie_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C09_PIE "+json.dumps(OUT))
