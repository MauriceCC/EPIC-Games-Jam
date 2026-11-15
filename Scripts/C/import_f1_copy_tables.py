"""Keep production copy in C-owned DataTables, reusing the published dialogue row struct."""
import unreal,csv,io,json
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sources=(("DT_NarrativeText","NarrativeText.csv","Key"),("DT_UIStrings","UIStrings.csv","Key"),("DT_HUDText","DT_HUDText.csv","Name"))
OUT={"passed":False,"tables":[]}
for name,filename,key in sources:
    original=list(csv.DictReader((repo/"SourceData/C"/filename).open(encoding="utf-8-sig",newline="")))
    rows=[{"Name":r[key],"Speaker":"NewEnumerator6","Text":r["Text"],"Duration":"0","NextRow":"None"} for r in original]
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),quoting=csv.QUOTE_ALL,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    table=unreal.load_asset("/Game/Unscripted/Narrative/"+name)
    if not table:
        factory=unreal.DataTableFactory();factory.set_editor_property("struct",unreal.load_asset("/Game/Unscripted/Core/Structs/ST_DialogueLine"))
        table=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,"/Game/Unscripted/Narrative",unreal.DataTable,factory)
    assert unreal.DataTableFunctionLibrary.fill_data_table_from_csv_string(table,stream.getvalue())
    assert len(unreal.DataTableFunctionLibrary.get_data_table_row_names(table))==len(rows)
    assert unreal.EditorAssetLibrary.save_loaded_asset(table,False)
    OUT["tables"].append({"path":table.get_path_name(),"rows":len(rows)})
OUT["passed"]=True
(repo/"Scripts/C/c_f1_copy_tables_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
print("C_F1_COPY_TABLES "+json.dumps(OUT))
