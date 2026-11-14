"""Open a requested F0 asset for manual editor operations, without saving it."""
import unreal, json
from pathlib import Path
request = json.loads((Path(unreal.Paths.project_saved_dir())/'F0_open_asset.json').read_text(encoding='utf-8-sig'))
assert request['asset'].startswith('/Game/Unscripted/')
asset = unreal.load_asset(request['asset'])
assert asset
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([asset])
