"""Validate persisted C-01/C-02 dependencies after reopening the editor."""
import unreal,json,traceback
from pathlib import Path
from toolset_registry.helpers import compile_blueprint
ROOT="/Game/Unscripted/"
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
OUT={"passed":False,"checks":[],"compilation":[],"after_editor_restart":True,"asset_saves_performed":False}
def check(name,ok,details=None):
    OUT["checks"].append({"name":name,"passed":bool(ok),"details":details})
    assert ok,name
def signature(graph):
    g=unreal.BlueprintGraphEditor.get_graph_editor(graph)
    node=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_FunctionEntry")
    return {str(p.get_pin_name()):p.get_pin_type().export_text() for p in node.list_output_pins()}
try:
    for path in ("Core/Interfaces/BPI_StoryEvents","Narrative/BP_ObjectiveManager","Narrative/BP_GameState","Narrative/BP_GameMode","Narrative/Test/BP_StoryEventTestSource_C","Narrative/Test/BP_StoryProgressionObserver_C"):
        bp=unreal.load_asset(ROOT+path)
        compile_blueprint(bp,warnings_as_errors=True)
        OUT["compilation"].append({"asset":path,"passed":True})
    manager=unreal.load_asset(ROOT+"Narrative/BP_ObjectiveManager")
    baseline=json.loads((repo/"Scripts/C/c01_c02_dependency_inspection.json").read_text(encoding="utf-8-sig"))["BP_ObjectiveManager"]["graphs"]
    for name in ("OnStoryPhaseChanged","OnChecklistUpdated","OnDialogueStarted","OnDialogueFinished","OnEndingTriggered"):
        expected={p["name"]:p["type"] for n in baseline[name] if n["class"]=="K2Node_FunctionEntry" for p in n["pins"]}
        graph=next(g for g in unreal.BlueprintEditorLibrary.list_graphs(manager) if g.get_name()==name)
        check("Preserved dispatcher signature "+name,signature(graph)==expected)
    interface=unreal.load_asset(ROOT+"Core/Interfaces/BPI_StoryEvents")
    graph=next(g for g in unreal.BlueprintEditorLibrary.list_graphs(interface) if g.get_name()=="ReportStoryEvent")
    actual=signature(graph)
    fix=json.loads((repo/"Scripts/C/c01_c02_contract_fix.json").read_text(encoding="utf-8-sig"))
    check("Source persists as Actor","/Script/Engine.Actor'" in actual["Source"])
    check("Event type unchanged",actual["Event"]==fix["before"]["Event"])
    check("Param type unchanged",actual["Param"]==fix["before"]["Param"])
    ob=unreal.load_asset(ROOT+"Narrative/Test/BP_StoryProgressionObserver_C")
    g=unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(ob))
    target=next(p for n in g.list_all_nodes() for p in n.list_output_pins() if str(p.get_pin_name())=="ObservedManager")
    actions=[str(a) for a in g.list_available_nodes([target])]
    check("Public phase getter available to consumers",any("GetStoryPhase" in a for a in actions))
    for name in ("CurrentPhase","Ending","bJackFound","bEscapeRouteOpen","bJackSafe","bEvidenceFound","bFalseReportFound","bSupervisorEncountered","bSupervisorDefeated","bIsProcessingStoryEvent"):
        check("No external setter for private "+name,not any(("Set"+name) in a for a in actions))
    check("Private commit is not externally callable",not any("CommitStoryPhase" in a for a in actions))
    state=unreal.load_asset(ROOT+"Narrative/BP_GameState")
    mode=unreal.get_default_object(unreal.load_asset(ROOT+"Narrative/BP_GameMode").generated_class())
    check("GameMode preserves GameState class",mode.get_editor_property("game_state_class")==state.generated_class())
    check("L_Test_C exists",bool(unreal.load_asset(ROOT+"Maps/Test/L_Test_C")))
    # Run the functional validator against the freshly loaded serialized graphs.
    namespace={"__name__":"__c01_c02_persisted_unit_validation__"}
    exec(compile((repo/"Scripts/C/validate_c01_c02.py").read_text(encoding="utf-8-sig"),"<persisted C-01/C-02 tests>","exec"),namespace)
    OUT["unit_result"]={k:namespace["OUT"].get(k) for k in ("passed","check_count","failed","error")}
    check("Persisted functional tests pass",OUT["unit_result"]["passed"])
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    OUT["dirty_content"]=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
    OUT["dirty_maps"]=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
    (repo/"Scripts/C/c01_c02_final_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_PERSISTENCE "+json.dumps(OUT))
