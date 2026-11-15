"""Import C narrative data using the existing shared row structs."""
import unreal,csv,io,json,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
OUT={"passed":False,"tables":[]}
try:
    helper=unreal.get_default_object(unreal.load_class(None,"/Script/Engine.KismetNodeHelperLibrary"))
    for name,struct_name,enums in (("DT_Dialogue","ST_DialogueLine",{"Speaker":"ESpeaker"}),("DT_Checklist","ST_ChecklistRow",{"Phase":"EStoryPhase"})):
        source=repo/"SourceData/C"/(name+".csv")
        rows=list(csv.DictReader(source.open(encoding="utf-8-sig",newline="")))
        for field,enum_name in enums.items():
            enum=unreal.load_asset("/Game/Unscripted/Core/Enums/"+enum_name)
            count=7 if enum_name=="ESpeaker" else 6
            mapping={str(helper.call_method("GetEnumeratorUserFriendlyName",args=(enum,i))):str(helper.call_method("GetEnumeratorName",args=(enum,i))) for i in range(count)}
            for row in rows:row[field]=mapping[row[field]]
        stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),quoting=csv.QUOTE_ALL,lineterminator="\n");writer.writeheader();writer.writerows(rows)
        path="/Game/Unscripted/Narrative/"+name
        table=unreal.load_asset(path)
        if not table:
            factory=unreal.DataTableFactory();factory.set_editor_property("struct",unreal.load_asset("/Game/Unscripted/Core/Structs/"+struct_name))
            table=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,"/Game/Unscripted/Narrative",unreal.DataTable,factory)
        assert table
        assert unreal.DataTableFunctionLibrary.fill_data_table_from_csv_string(table,stream.getvalue())
        names=unreal.DataTableFunctionLibrary.get_data_table_row_names(table)
        assert len(names)==len(rows),(name,len(names),len(rows))
        assert unreal.EditorAssetLibrary.save_loaded_asset(table,False)
        OUT["tables"].append({"path":table.get_path_name(),"rows":len(names),"export":unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table)})
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    (repo/"Scripts/C/c_f1_table_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_TABLES "+str(OUT.get("passed"))+" "+OUT.get("error",""))
