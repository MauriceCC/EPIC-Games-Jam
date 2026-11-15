"""Validate the actual GameMode/GameState/component/interface path in L_Test_C PIE."""
import unreal,json,traceback
from pathlib import Path
OUT={"passed":False,"checks":[]}
def check(name,value):
    OUT["checks"].append({"name":name,"passed":bool(value)})
    assert value,name
try:
    worlds=unreal.EditorLevelLibrary.get_pie_worlds(False)
    assert len(worlds)==1
    world=worlds[0]
    check("PIE uses L_Test_C","L_Test_C" in world.get_path_name())
    state=unreal.GameplayStatics.get_game_state(world)
    mode=unreal.GameplayStatics.get_game_mode(world)
    check("Existing C GameMode",mode.get_class().get_name()=="BP_GameMode_C")
    check("Existing C GameState",state.get_class().get_name()=="BP_GameState_C")
    manager=state.call_method("GetObjectiveManager")
    check("Existing ObjectiveManager component",manager and manager.get_outer()==state)
    check("Primary state starts at FindJack",state.call_method("GetCurrentPhase").value==0)
    fixture=unreal.load_asset("/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C")
    statics=unreal.get_default_object(unreal.GameplayStatics)
    actor=statics.call_method("BeginDeferredActorSpawnFromClass",args=(world,fixture.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    source=statics.call_method("FinishSpawningActor",args=(actor,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    check("Source is a normal C-owned Actor",isinstance(source,unreal.Actor) and not isinstance(source,unreal.ActorActionUtility))
    event_class=type(source.get_editor_property("EventToReport"))
    helper=unreal.get_default_object(unreal.load_class(None,"/Script/Engine.KismetNodeHelperLibrary"))
    enum=unreal.load_asset("/Game/Unscripted/Core/Enums/EStoryEvent")
    events={str(helper.call_method("GetEnumeratorUserFriendlyName",args=(enum,i))):i for i in range(14)}
    ob_class=unreal.load_asset("/Game/Unscripted/Narrative/Test/BP_StoryProgressionObserver_C").generated_class()
    observer=unreal.new_object(ob_class,outer=state)
    observer.set_editor_property("ObservedManager",manager);observer.call_method("BindObservers")
    def report(event,param=""):
        source.set_editor_property("EventToReport",event_class.cast(events[event]))
        source.set_editor_property("EventParam",param)
        source.call_method("ReportConfiguredEvent")
    report("EscapeRouteOpened")
    check("Interface rejects premature route report",state.call_method("GetCurrentPhase").value==0)
    for event,want in (("JackFound",1),("EscapeRouteOpened",2),("JackReachedRefuge",3)):
        report(event)
        check("GameState forwards "+event,state.call_method("GetCurrentPhase").value==want)
        check("Stable manager identity "+event,state.call_method("GetObjectiveManager")==manager)
    report("TruthRevealed")
    check("Interface reveal waits for both evidence records",state.call_method("GetCurrentPhase").value==3)
    report("EvidenceCollected","NursingRecord");report("EvidenceCollected","NursingRecord");report("TruthRevealed")
    check("Interface duplicate evidence cannot reveal truth",state.call_method("GetCurrentPhase").value==3)
    report("EvidenceCollected","FabricatedReport")
    report("TruthRevealed")
    check("Explicit reveal advances to FinalChoice",state.call_method("GetCurrentPhase").value==4)
    report("SupervisorEncounterStarted")
    check("Appended event reaches manager",manager.get_editor_property("bSupervisorEncountered"))
    report("FinalDocumentRegistered","AuthenticRecord")
    check("Registration blocked before supervisor defeat",state.call_method("GetCurrentPhase").value==4)
    report("SupervisorDefeated")
    check("Defeat never selects ending",manager.get_editor_property("Ending").value==0 and state.call_method("GetCurrentPhase").value==4)
    report("FinalDocumentRegistered","AuthenticRecord")
    check("Valid simulated registration ends session",state.call_method("GetCurrentPhase").value==5 and manager.get_editor_property("Ending").value==2)
    check("Exactly five phase notifications",observer.get_editor_property("ObservedPhaseChangeCount")==5)
    check("Exactly one ending notification",observer.get_editor_property("ObservedEndingCount")==1)
    report("FinalDocumentRegistered","OfficialCut");report("JackFound")
    check("Terminal phase and ending cannot be overwritten",state.call_method("GetCurrentPhase").value==5 and manager.get_editor_property("Ending").value==2)
    source.destroy_actor()
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    OUT["check_count"]=len(OUT["checks"])
    (Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c01_c02_pie_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_PIE_VALIDATION "+json.dumps(OUT))
