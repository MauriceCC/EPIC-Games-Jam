"""Read-only final compilation, signature, source-data, scope and architecture checks."""
import unreal,sys,json,csv,re,ast,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
OUT={"passed":False,"checks":[],"compilation":[],"tables":[],"asset_saves_performed":False}
def check(name,value):
    OUT["checks"].append({"name":name,"passed":bool(value)})
    assert value,name
def text_value(raw):
    if isinstance(raw,str) and raw.startswith(("NSLOCTEXT(","LOCTEXT(")):
        # Unreal's text exporter escapes apostrophes using C/Python-style escapes.
        return ast.literal_eval("["+raw[raw.index("(")+1:-1]+"]")[-1]
    return raw
try:
    paths=["Narrative/"+x for x in ("BP_InteractionComponent","BP_InteractableBase","BP_Door","BP_Hideout","BP_Evidence","BP_ObjectiveManager","BP_GameState","BP_GameMode","BP_Checkpoint")]
    paths += ["UI/"+x for x in ("BP_HUD","WBP_HUD","WBP_Dialogue","WBP_Checklist","WBP_Document")]
    paths += ["Narrative/Test/"+x for x in ("BP_TestPlayer_C","BP_TestStealth_C","BP_TestGameMode_C","BP_TestInteractable_C","BP_StoryEventTestSource_C","BP_StoryProgressionObserver_C")]
    paths += ["Core/Interfaces/BPI_Interactable","Core/Interfaces/BPI_StoryEvents"]
    for path in paths:
        bp=h.asset(path);h.compile_blueprint(bp,warnings_as_errors=True)
        OUT["compilation"].append({"asset":bp.get_path_name(),"passed":True})
    interface=h.asset("Core/Interfaces/BPI_Interactable")
    for name in ("Interact","CanInteract","GetInteractionText"):
        g=h.edit(interface,name)
        entry=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_FunctionEntry")
        pin=entry.find_output_pin("Interactor")
        check(name+".Interactor is exactly Actor","/Script/Engine.Actor'" in pin.get_pin_type().export_text())
    g=h.edit(interface,"GetInteractionPriority")
    result=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_FunctionResult").find_input_pin("Result")
    check("GetInteractionPriority.Result is int32",result.get_pin_type().export_text().startswith('(PinCategory="int",'))
    for path in ("UI/BP_HUD","UI/WBP_HUD","UI/WBP_Dialogue","UI/WBP_Checklist","UI/WBP_Document"):
        bp=h.asset(path);casts=[];ticks=[]
        for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
            for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
                if n.get_class().get_name()=="K2Node_DynamicCast":
                    casts += [p.get_pin_type().export_text() for p in n.list_output_pins()]
                if n.get_class().get_name()=="K2Node_Event" and "Tick" in str(n.get_node_title()):ticks.append(bool(n.find_then_pin().list_connected_pins()))
        check(path+" has no connected Tick",not any(ticks))
        check(path+" has no cast to A or B",not any("/Player/" in x or "/Enemies/" in x for x in casts))
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
    opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
    for path in paths:
        if "/Test/" in path or path.startswith("Core/"):continue
        dependencies=[str(x) for x in registry.get_dependencies(h.ROOT+path,opts)]
        check(path+" does not depend on a test asset",not any(x.startswith("/Game/") and "/Test/" in x for x in dependencies))
    for name,source,key in (("DT_Dialogue","DT_Dialogue.csv","Name"),("DT_Checklist","DT_Checklist.csv","Name"),("DT_NarrativeText","NarrativeText.csv","Key"),("DT_UIStrings","UIStrings.csv","Key"),("DT_HUDText","DT_HUDText.csv","Name")):
        table=h.asset("Narrative/"+name)
        rows={x["Name"]:x for x in json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))}
        original=list(csv.DictReader((repo/"SourceData/C"/source).open(encoding="utf-8-sig",newline="")))
        check(name+" preserves all source row names",set(rows)=={r[key] for r in original})
        for row in original:
            actual=rows[row[key]]
            if "Text" in row:check(name+" source text "+row[key],text_value(actual["Text"])==row["Text"])
            if name=="DT_Dialogue":
                check("NextRow "+row[key],str(actual["NextRow"])==row["NextRow"])
                check("Duration "+row[key],float(actual["Duration"])==float(row["Duration"]))
            if name=="DT_Checklist":
                items=json.loads("["+row["Items"][1:-1]+"]")
                check("Checklist text "+row[key],[text_value(x) for x in actual["Items"]]==items)
                check("Checklist mask "+row[key],actual["CompletedMask"]==[x.lower()=="true" for x in row["CompletedMask"][1:-1].split(",")])
        OUT["tables"].append({"asset":table.get_path_name(),"rows":len(rows)})
    production=unreal.get_default_object(h.asset("Narrative/BP_GameMode").generated_class())
    check("Production GameMode keeps A's player",production.get_editor_property("default_pawn_class").get_path_name()=="/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C")
    check("Production GameMode keeps A's controller",production.get_editor_property("player_controller_class").get_path_name()=="/Game/Unscripted/Player/BP_PlayerController.BP_PlayerController_C")
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    check("Only L_Test_C is open",world.get_path_name()=="/Game/Unscripted/Maps/Test/L_Test_C.L_Test_C")
    check("C test GameMode override stays in the C map",world.get_world_settings().get_editor_property("default_game_mode")==h.asset("Narrative/Test/BP_TestGameMode_C").generated_class())
    check("All assets are explicitly saved",not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    check("Test map is explicitly saved",not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    OUT["check_count"]=len(OUT["checks"])
    OUT["dirty_content"]=[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
    OUT["dirty_maps"]=[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
    (repo/"Scripts/C/c_f1_asset_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_ASSETS "+str(OUT["passed"])+" "+OUT.get("error",""))
