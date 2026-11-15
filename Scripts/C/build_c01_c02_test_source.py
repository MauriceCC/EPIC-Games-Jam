"""Build an isolated C-owned Actor that reports the existing story interface."""
import unreal,json,traceback
from pathlib import Path
from toolset_registry.helpers import compile_blueprint
OUT={"passed":False}
try:
    path="/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C"
    bp=unreal.load_asset(path)
    # This exact C test fixture is the only asset authored by this script.
    f=unreal.BlueprintFactory()
    f.set_editor_property("parent_class",unreal.Actor)
    bp=bp or unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_StoryEventTestSource_C","/Game/Unscripted/Narrative/Test",unreal.Blueprint,f)
    assert bp
    interface=unreal.load_asset("/Game/Unscripted/Core/Interfaces/BPI_StoryEvents")
    sg=unreal.BlueprintGraphEditor.get_graph_editor_by_name(interface,"ReportStoryEvent")
    event_type=sg.find_graph_entry_pin().get_owning_node().find_output_pin("Event").get_pin_type()
    eg=unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp))
    if unreal.BlueprintEditorLibrary.get_member_variable_type(bp,"EventToReport") is None:assert eg.add_member_variable("EventToReport",event_type,"NewEnumerator0")
    if unreal.BlueprintEditorLibrary.get_member_variable_type(bp,"EventParam") is None:assert eg.add_member_variable("EventParam",unreal.BlueprintEditorLibrary.get_basic_type_by_name("name"),"")
    for name in ("EventToReport","EventParam"):
        unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,name,True)
        unreal.BlueprintEditorLibrary.set_blueprint_variable_category(bp,name,"Story Test")
    old=next((x for x in unreal.BlueprintEditorLibrary.list_graphs(bp) if x.get_name()=="ReportConfiguredEvent"),None)
    g=unreal.BlueprintGraphEditor.get_graph_editor(old) if old else unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,"ReportConfiguredEvent")
    g.remove_nodes([n for n in g.list_all_nodes() if n.get_class().get_name()!="K2Node_FunctionEntry"])
    g.set_is_call_in_editor_function(True)
    gs=g.add_call_function_node("/Script/Engine.GameplayStatics:GetGameState")
    options=[str(a) for a in g.list_available_nodes([gs.find_result_pin()]) if "ReportStoryEvent" in str(a)]
    OUT["interface_actions"]=options
    message_id=next(a for a in options if "Mensaje" in a or "Message" in a)
    message=g.create_node_from_name(message_id,unreal.Vector2D(500,0),[gs.find_result_pin()])
    def connect(a,b):
        assert a.try_create_connection(b),(str(a.get_pin_name()),str(b.get_pin_name()))
    self_id=next(str(a) for a in g.list_available_nodes([]) if str(a).startswith("Variables|") and ("mismo" in str(a).lower() or "referencetoself" in str(a).lower().replace(" ","")))
    self_node=g.create_node_from_name(self_id,unreal.Vector2D(0,220),[])
    connect(g.find_graph_entry_pin(),message.find_execute_pin())
    connect(g.add_get_member_variable_node("EventToReport").find_result_pin(),message.find_input_pin("Event"))
    connect(g.add_get_member_variable_node("EventParam").find_result_pin(),message.find_input_pin("Param"))
    connect(self_node.find_result_pin(),message.find_input_pin("Source"))
    # GetGameState uses its native hidden self world context.
    for i,n in enumerate(g.list_all_nodes()):n.set_node_pos(unreal.IntPoint((i%4)*360,(i//4)*220))
    compile_blueprint(bp,warnings_as_errors=True)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
    manager=unreal.load_asset("/Game/Unscripted/Narrative/BP_ObjectiveManager")
    compile_blueprint(manager,warnings_as_errors=True)
    assert unreal.EditorAssetLibrary.save_loaded_asset(manager,False)
    state=unreal.load_asset("/Game/Unscripted/Narrative/BP_GameState")
    compile_blueprint(state,warnings_as_errors=True)
    assert unreal.EditorAssetLibrary.save_loaded_asset(state,False)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    target=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c01_c02_test_source_build.json"
    target.write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_TEST_SOURCE "+json.dumps(OUT))
