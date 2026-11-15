"""Apply only the C-01/C-02 ReportStoryEvent.Source contract correction."""
import unreal,json,traceback
from pathlib import Path
from toolset_registry.helpers import compile_blueprint
OUT={"passed":False}
try:
    bp=unreal.load_asset("/Game/Unscripted/Core/Interfaces/BPI_StoryEvents")
    graphs=unreal.BlueprintEditorLibrary.list_graphs(bp)
    current=next(g for g in graphs if g.get_name()=="ReportStoryEvent")
    g=unreal.BlueprintGraphEditor.get_graph_editor(current)
    assert all(n.get_class().get_name() in ("K2Node_FunctionEntry","K2Node_FunctionResult") for n in g.list_all_nodes()),"Unexpected authored interface body"
    entry=g.find_graph_entry_pin().get_owning_node()
    inputs={str(p.get_pin_name()):p for p in entry.list_output_pins()}
    assert set(inputs)=={"then","Event","Source","Param"},list(inputs)
    event_type=inputs["Event"].get_pin_type()
    OUT["before"]={name:inputs[name].get_pin_type().export_text() for name in ("Event","Source","Param")}
    assert "/Script/Blutility.ActorActionUtility" in OUT["before"]["Source"] or "/Script/Engine.Actor'" in OUT["before"]["Source"]
    if "/Script/Engine.Actor'" not in OUT["before"]["Source"]:
        unreal.BlueprintEditorLibrary.remove_graph(bp,current)
        compile_blueprint(bp,warnings_as_errors=True)
        g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,"ReportStoryEvent")
        for name,typ,default in (("Event",event_type,"NewEnumerator0"),("Source",unreal.BlueprintEditorLibrary.get_object_reference_type(unreal.Actor.static_class()),""),("Param",unreal.BlueprintEditorLibrary.get_basic_type_by_name("name"),"")):
            pin=g.add_graph_input_parameter(name,typ,default)
            assert str(pin.get_pin_name())==name
    compile_blueprint(bp,warnings_as_errors=True)
    entry=g.find_graph_entry_pin().get_owning_node()
    OUT["after"]={str(p.get_pin_name()):p.get_pin_type().export_text() for p in entry.list_output_pins() if str(p.get_pin_name())!="then"}
    assert OUT["after"]["Event"]==OUT["before"]["Event"]
    assert OUT["after"]["Param"]==OUT["before"]["Param"]
    assert "/Script/Engine.Actor'" in OUT["after"]["Source"]
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    target=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c01_c02_contract_fix.json"
    target.write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_SOURCE_FIX "+json.dumps(OUT))
