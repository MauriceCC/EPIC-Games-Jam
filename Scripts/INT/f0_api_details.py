"""Read-only API and shared-type metadata audit."""
import unreal, json
from pathlib import Path
report = {}
for cls_name in ['CubeBuilder','EditorLevelUtils','LevelEditorSubsystem','EditorActorSubsystem','NiagaraSystemFactoryNew','MetaSoundSourceFactory','InputMappingContext','InputAction','BlueprintGraphEditor']:
    cls = getattr(unreal, cls_name, None)
    if cls:
        report[cls_name] = {'doc': cls.__doc__, 'methods': {n: getattr(cls,n).__doc__ for n in dir(cls) if n in ['build','create_new_streaming_level','add_level_to_world','new_level','save_current_level','load_level','spawn_actor_from_class','map_key','add_call_function_node','add_get_member_variable_node','create_node_from_name']}}
L = unreal.BlueprintEditorLibrary
for path in unreal.EditorAssetLibrary.list_assets('/Game/Unscripted/Core', recursive=True, include_folder=False):
    obj = unreal.load_asset(path)
    if isinstance(obj, unreal.UserDefinedEnum):
        p = unreal.EdGraphPinType()
        p.import_text('(PinCategory="byte",PinSubCategoryObject="'+obj.get_path_name()+'")')
        report[path] = L.pin_type_to_json_schema(p, unreal.Actor.static_class())
    elif isinstance(obj, unreal.UserDefinedStruct):
        report[path] = L.pin_type_to_json_schema(L.get_struct_type(obj), unreal.Actor.static_class())
(Path(unreal.Paths.project_saved_dir())/'F0_api_details.json').write_text(json.dumps(report,indent=2), encoding='utf-8')
