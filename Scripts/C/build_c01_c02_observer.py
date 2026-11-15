"""Create a C-only observer fixture for real Blueprint multicast and reentry tests."""
import unreal,json,traceback
from pathlib import Path
from toolset_registry.helpers import compile_blueprint
OUT={"passed":False}
try:
    manager=unreal.load_asset("/Game/Unscripted/Narrative/BP_ObjectiveManager")
    path="/Game/Unscripted/Narrative/Test/BP_StoryProgressionObserver_C"
    bp=unreal.load_asset(path)
    assert not bp,"Preserve an existing observer fixture"
    f=unreal.BlueprintFactory();f.set_editor_property("parent_class",manager.generated_class())
    bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_StoryProgressionObserver_C","/Game/Unscripted/Narrative/Test",unreal.Blueprint,f)
    assert bp
    g=unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp))
    integer=unreal.BlueprintEditorLibrary.get_basic_type_by_name("int")
    boolean=unreal.BlueprintEditorLibrary.get_basic_type_by_name("bool")
    phase=unreal.BlueprintEditorLibrary.get_member_variable_type(manager,"CurrentPhase")
    ending=unreal.BlueprintEditorLibrary.get_member_variable_type(manager,"Ending")
    for name,typ,default in (("ObservedManager",unreal.BlueprintEditorLibrary.get_object_reference_type(manager.generated_class()),""),("ObservedPhaseChangeCount",integer,"0"),("ObservedEndingCount",integer,"0"),("ObservedChecklistCount",integer,"0"),("LastObservedPhase",phase,"NewEnumerator0"),("LastObservedEnding",ending,"NewEnumerator0"),("bAttemptReentrantReport",boolean,"false")):
        assert g.add_member_variable(name,typ,default)
    for name in ("ObservedManager","bAttemptReentrantReport"):unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,name,True)
    compile_blueprint(bp,warnings_as_errors=True)
    def connect(a,b):assert a.try_create_connection(b)
    def get(name):return g.add_get_member_variable_node(name).find_result_pin()
    def assign(start,name,value):
        n=g.add_set_member_variable_node(name);connect(start,n.find_execute_pin())
        if isinstance(value,unreal.BlueprintGraphPin):connect(value,n.find_input_pin(name))
        else:assert n.find_input_pin(name).set_pin_value(str(value))
        return n.find_then_pin()
    start=g.add_custom_event_node("BindObservers").find_then_pin()
    for signal,counter,param,last in (("OnStoryPhaseChanged","ObservedPhaseChangeCount","NewPhase","LastObservedPhase"),("OnEndingTriggered","ObservedEndingCount","Ending","LastObservedEnding"),("OnChecklistUpdated","ObservedChecklistCount",None,None)):
        callback=g.add_dispatcher_event_node(signal,manager.generated_class())
        assert callback,signal
        target=get("ObservedManager")
        action=next(str(a) for a in g.list_available_nodes([target]) if str(a).endswith("|BindEventto"+signal))
        binder=g.create_node_from_name(action,unreal.Vector2D(0,0),[target])
        if not binder.find_self_pin().list_connected_pins():connect(target,binder.find_self_pin())
        connect(callback.find_output_pin("OutputDelegate"),binder.find_input_pin("Delegate"))
        connect(start,binder.find_execute_pin())
        start=binder.find_then_pin()
        plus=g.add_call_function_node("/Script/Engine.KismetMathLibrary:Add_IntInt")
        connect(get(counter),plus.find_input_pin("A"));assert plus.find_input_pin("B").set_pin_value("1")
        end=assign(callback.find_then_pin(),counter,plus.find_result_pin())
        if param:end=assign(end,last,callback.find_output_pin(param))
        if signal=="OnStoryPhaseChanged":
            condition=g.add_branch_node()
            connect(end,condition.find_execute_pin());connect(get("bAttemptReentrantReport"),condition.find_input_pin("Condition"))
            report=g.add_call_function_node(manager.generated_class().get_path_name()+":HandleStoryEvent")
            connect(condition.find_output_pin("then"),report.find_execute_pin())
            connect(get("ObservedManager"),report.find_self_pin())
            assert report.find_input_pin("Event").set_pin_value("NewEnumerator1")
    for i,n in enumerate(g.list_all_nodes()):n.set_node_pos(unreal.IntPoint((i%7)*360,(i//7)*240))
    for name in ("ObservedManager","bAttemptReentrantReport"):unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,name,True)
    compile_blueprint(bp,warnings_as_errors=True)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    target=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c01_c02_observer_build.json"
    target.write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_OBSERVER "+json.dumps(OUT))
