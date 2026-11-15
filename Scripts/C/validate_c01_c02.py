"""Exercise real C-01/C-02 Blueprint functions and multicast dispatchers.
Run inside Unreal through MCP. No assets are modified or saved.
"""
import unreal,json,itertools,traceback
from pathlib import Path
ROOT="/Game/Unscripted/"
OUT={"passed":False,"checks":[],"failed":[]}
KEEP=[]
def check(name,condition,details=None):
    item={"name":name,"passed":bool(condition)}
    if details is not None:item["details"]=details
    OUT["checks"].append(item)
    if not condition:OUT["failed"].append(item)
def prop(obj,name):return obj.get_editor_property(name)
def phase(m):return m.call_method("GetStoryPhase").value
try:
    manager_bp=unreal.load_asset(ROOT+"Narrative/BP_ObjectiveManager")
    fixture_bp=unreal.load_asset(ROOT+'Narrative/Test/BP_C30ProgressionFixture_C')
    assert fixture_bp,'C-30 worldless state fixture is required; production never references it.'
    observer_bp=unreal.load_asset(ROOT+"Narrative/Test/BP_StoryProgressionObserver_C")
    source_bp=unreal.load_asset(ROOT+"Narrative/Test/BP_StoryEventTestSource_C")
    event_class=type(unreal.get_default_object(source_bp.generated_class()).get_editor_property("EventToReport"))
    helper=unreal.get_default_object(unreal.load_class(None,"/Script/Engine.KismetNodeHelperLibrary"))
    enum=unreal.load_asset(ROOT+"Core/Enums/EStoryEvent")
    EVENTS={}
    for i in range(255):
        raw=str(helper.call_method("GetEnumeratorName",args=(enum,i)))
        if raw=="None" or raw.endswith("_MAX"):break
        EVENTS[str(helper.call_method("GetEnumeratorUserFriendlyName",args=(enum,i)))]=i
    expected_old=["JackFound","EscapeRouteOpened","JackReachedRefuge","EvidenceCollected","TruthRevealed","InterventorTurnedHostile","SupervisorDefeated","FinalDocumentRegistered","EnemyNeutralized","PlayerDefeated","CheckpointReached","ContinuityAltered","FutureMessageRead"]
    check("Enum preserves all original numeric values",all(EVENTS[n]==i for i,n in enumerate(expected_old)))
    check("Encounter event appended at 13",EVENTS.get("SupervisorEncounterStarted")==13 and len(EVENTS)==14)
    def report(m,event,param=""):
        m.call_method("HandleStoryEvent",args=(event_class.cast(EVENTS[event]),None,param))
    def observer(m,reentry=False):
        obj=unreal.new_object(observer_bp.generated_class())
        obj.set_editor_property("ObservedManager",m)
        obj.set_editor_property("bAttemptReentrantReport",reentry)
        obj.call_method("BindObservers")
        KEEP.append(obj)
        return obj
    def session(stage=0):
        m=unreal.new_object(fixture_bp.generated_class());KEEP.append(m)
        steps=[("JackFound",""),("EscapeRouteOpened",""),("JackReachedRefuge","")]
        for e,p in steps[:min(stage,3)]:report(m,e,p)
        if stage>=4:
            report(m,"EvidenceCollected","NursingRecord");report(m,"EvidenceCollected","FabricatedReport")
            # Worldless state fixture: presentation is exercised with native E in C-30 PIE tests.
            m.call_method('ConfirmRevelationForStateTest');report(m,"TruthRevealed")
        if stage>=5:
            report(m,"SupervisorDefeated");report(m,"FinalDocumentRegistered","OfficialCut")
        return m
    m=session();check("Default phase FindJack",phase(m)==0)
    for flag in ("bJackFound","bEscapeRouteOpen","bJackSafe","bEvidenceFound","bFalseReportFound","bSupervisorEncountered","bSupervisorDefeated"):
        check("Default "+flag,not prop(m,flag))
    check("Default Ending None",prop(m,"Ending").value==0)
    check("Default revelation completion is false",not prop(m,'bTruthRevelationComplete'))
    rules=json.loads((Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"SourceData/C/StoryTransitions.json").read_text(encoding="utf-8-sig"))
    phase_names=rules["phases"]
    # Cross-product expectations come from the independently prepared C transition table.
    for stage,event in itertools.product(range(6),EVENTS):
        m=session(stage);o=observer(m)
        before=phase(m)
        expected=before
        for rule in rules["transitions"]:
            if rule["phase"]!=phase_names[before] or rule["event"]!=event:continue
            if not all(prop(m,flag) for flag in rule["required_flags"]):continue
            if rule.get('presentation_completion_row') and not prop(m,'bTruthRevelationComplete'):continue
            if rule["requires_supervisor_defeat"] and not prop(m,"bSupervisorDefeated"):continue
            if rule["allowed_endings"] and "InvalidParam" not in rule["allowed_endings"]:continue
            expected=phase_names.index(rule["next_phase"])
        report(m,event,"InvalidParam")
        check("Phase/event guard %s %s"%(stage,event),phase(m)==expected)
        check("Phase notification count %s %s"%(stage,event),prop(o,"ObservedPhaseChangeCount")==(1 if expected!=before else 0))
    m=session();a=observer(m);b=observer(m)
    for event,want in (("JackFound",1),("EscapeRouteOpened",2),("JackReachedRefuge",3)):
        report(m,event);report(m,event)
        check("Sequence and duplicate "+event,phase(m)==want and prop(a,"ObservedPhaseChangeCount")==want and prop(b,"ObservedPhaseChangeCount")==want)
    check("Two multicast subscribers receive every transition",prop(a,"ObservedPhaseChangeCount")==3 and prop(b,"ObservedPhaseChangeCount")==3)
    for token in ("","Unknown","Nursing Record","OfficialCut"):
        m=session(3);o=observer(m)
        report(m,"EvidenceCollected",token);report(m,"TruthRevealed")
        check("Invalid evidence parameter "+repr(token),phase(m)==3 and not prop(m,"bEvidenceFound") and not prop(m,"bFalseReportFound") and prop(o,"ObservedChecklistCount")==0)
    for first,second in (("NursingRecord","FabricatedReport"),("FabricatedReport","NursingRecord")):
        m=session(3);o=observer(m)
        report(m,"EvidenceCollected",first);report(m,"EvidenceCollected",first);report(m,"TruthRevealed")
        check("Duplicate evidence does not replace other record "+first,phase(m)==3 and prop(o,"ObservedChecklistCount")==1)
        report(m,"EvidenceCollected",second)
        check("Both records do not auto-reveal "+first,phase(m)==3)
        report(m,'TruthRevealed');check('Evidence alone cannot bypass the Supervisor dialogue '+first,phase(m)==3)
        m.call_method('ConfirmRevelationForStateTest')
        report(m,"TruthRevealed");report(m,"TruthRevealed")
        check("Explicit reveal after distinct evidence "+first,phase(m)==4 and prop(o,"ObservedPhaseChangeCount")==1)
        check("Facts remain recorded "+first,all(prop(m,f) for f in ("bJackFound","bEscapeRouteOpen","bJackSafe","bEvidenceFound","bFalseReportFound")))
    m=session();o=observer(m)
    report(m,"EvidenceCollected","NursingRecord");report(m,"SupervisorDefeated")
    for event in ("JackFound","EscapeRouteOpened","JackReachedRefuge"):report(m,event)
    report(m,"TruthRevealed")
    check("Premature evidence and boss reports are not banked",phase(m)==3 and not prop(m,"bEvidenceFound") and not prop(m,"bSupervisorDefeated"))
    for ending,value in (("OfficialCut",1),("AuthenticRecord",2)):
        m=session(4);o=observer(m)
        report(m,"FinalDocumentRegistered",ending)
        check("Registration requires supervisor gate "+ending,phase(m)==4 and prop(m,"Ending").value==0)
        report(m,"SupervisorEncounterStarted");report(m,"SupervisorEncounterStarted")
        check("Encounter notification is idempotent "+ending,prop(m,"bSupervisorEncountered") and phase(m)==4)
        report(m,"SupervisorDefeated");report(m,"SupervisorDefeated")
        check("Defeat unlocks but never selects ending "+ending,phase(m)==4 and prop(m,"Ending").value==0 and prop(o,"ObservedEndingCount")==0)
        for invalid in ("","None","Official","Jack"):
            report(m,"FinalDocumentRegistered",invalid)
            check("Invalid registration %s %s"%(ending,invalid),phase(m)==4 and prop(m,"Ending").value==0)
        report(m,"FinalDocumentRegistered",ending)
        check("Valid registration selects exactly one ending "+ending,phase(m)==5 and prop(m,"Ending").value==value and prop(o,"ObservedEndingCount")==1)
        for e in EVENTS:report(m,e,"AuthenticRecord" if value==1 else "OfficialCut")
        check("GameEnded remains terminal "+ending,phase(m)==5 and prop(m,"Ending").value==value and prop(o,"ObservedEndingCount")==1 and prop(o,"ObservedPhaseChangeCount")==1)
    m=session();o=observer(m,True)
    report(m,"JackFound")
    check("Synchronous reentrant report cannot skip a phase",phase(m)==1 and prop(o,"ObservedPhaseChangeCount")==1 and not prop(m,"bEscapeRouteOpen"))
    report(m,"EscapeRouteOpened")
    check("Normal report works after reentry guard releases",phase(m)==2 and not prop(m,"bIsProcessingStoryEvent"))
    # The sole writer is a private manager function, never GameState or senders.
    writes=[]
    for bp in (manager_bp,unreal.load_asset(ROOT+"Narrative/BP_GameState"),source_bp):
        for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
            for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
                if n.get_class().get_name()=="K2Node_VariableSet" and any(str(p.get_pin_name())=="CurrentPhase" for p in n.list_all_pins()):
                    writes.append(bp.get_name()+"."+graph.get_name())
    check("Only CommitStoryPhase writes CurrentPhase",writes==["BP_ObjectiveManager.CommitStoryPhase"],writes)
    OUT["passed"]=not OUT["failed"]
except Exception:OUT["error"]=traceback.format_exc()
finally:
    OUT["check_count"]=len(OUT["checks"])
    OUT["passed_count"]=sum(c["passed"] for c in OUT["checks"])
    OUT["passed"]=OUT["passed"] and not OUT.get("error")
    (Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c01_c02_unit_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_UNIT_VALIDATION "+json.dumps({k:OUT.get(k) for k in ("passed","check_count","passed_count","failed","error")}))
