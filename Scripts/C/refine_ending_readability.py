"""Refine only C's new newspaper/message copy and column spacing."""
import unreal,csv,json
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
table=unreal.load_asset('/Game/Unscripted/Narrative/DT_EndingText')
rows=list(csv.DictReader((repo/'SourceData/C/EndingText.csv').open(encoding='utf-8-sig',newline='')))
assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps([{'Name':r['Name'],'Speaker':'NewEnumerator6','Text':r['Text'].replace('\\n','\n'),'Duration':0,'NextRow':'None'} for r in rows]))
assert unreal.EditorAssetLibrary.save_loaded_asset(table,False)
bp=unreal.load_asset('/Game/Unscripted/UI/WBP_Ending')
for name,size in [('NewspaperLeft',16),('MessageBody',19)]:
 obj=unreal.find_object(None,bp.get_path_name()+':WidgetTree.'+name);font=obj.get_editor_property('font');font.set_editor_property('size',size);obj.set_font(font)
column=unreal.find_object(None,bp.get_path_name()+':WidgetTree.PaperColumn');column.get_editor_property('slot').set_size(unreal.Vector2D(1,188))
from toolset_registry.helpers import compile_blueprint
compile_blueprint(bp,warnings_as_errors=True);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False);print('C_ENDING_READABILITY_SAVED')
