"""Read-only inspection of the running editor and F0 assets."""
import json
from pathlib import Path
import unreal

report = {
    "engine": unreal.SystemLibrary.get_engine_version(),
    "project": unreal.Paths.get_project_file_path(),
    "assets": list(unreal.EditorAssetLibrary.list_assets('/Game/Unscripted', recursive=True, include_folder=False)),
    "api": {},
}
for name in dir(unreal):
    if any(term in name for term in ('Blueprint', 'Graph', 'Enum', 'Struct')) and any(term in name for term in ('Library', 'Subsystem', 'Editor')):
        cls = getattr(unreal, name)
        report['api'][name] = [x for x in dir(cls) if not x.startswith('_')]
output = Path(unreal.Paths.project_saved_dir()) / 'F0_inspection.json'
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('F0 inspection: ' + str(output))
