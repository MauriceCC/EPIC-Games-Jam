"""Run the original F0 preview assertions without resaving any prototype or old report."""
from pathlib import Path
import unreal
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
source=repo/"Unscripted/Content/Unscripted/Narrative/Test/verify_ui_prototypes.py"
code=source.read_text(encoding="utf-8-sig")
save_line='        check("Asset saves: " + bp.get_name(), unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False))'
assert code.count(save_line)==1
code=code.replace(save_line,"")
code=code.replace('report_path = project / "Content/Unscripted/Narrative/Test/ui_preview_validation.json"','report_path = project.parent / "Scripts/C/c_f0_prototype_regression.json"')
exec(compile(code,"<read-only F0 preview regression>","exec"))
