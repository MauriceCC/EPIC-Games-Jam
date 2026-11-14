"""Verify and save the authorized append-only correction, then open player."""
import unreal, json
enum = unreal.load_asset('/Game/Unscripted/Core/Enums/EStoryEvent')
pin = unreal.EdGraphPinType()
pin.import_text('(PinCategory="byte",PinSubCategoryObject="'+enum.get_path_name()+'")')
values = json.loads(unreal.BlueprintEditorLibrary.pin_type_to_json_schema(pin,unreal.Actor.static_class()))['enum']
assert len(values)==14 and values[-1]=='SupervisorEncounterStarted', values
assert unreal.EditorAssetLibrary.save_loaded_asset(enum)
editors = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
editors.close_all_editors_for_asset(enum)
editors.open_editor_for_assets([unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')])
