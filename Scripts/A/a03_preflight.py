"""Read-only prerequisites for A-03; run using Unreal's Python commandlet."""
import json
from pathlib import Path
import unreal

bp = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
L = unreal.BlueprintEditorLibrary
H = unreal.SubobjectDataBlueprintFunctionLibrary
out = {'components': [], 'api': {}}
for handle in unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(bp):
    obj = H.get_object(H.get_data(handle))
    if isinstance(obj, (unreal.CameraComponent, unreal.SpringArmComponent, unreal.CharacterMovementComponent)):
        row = {'name': obj.get_name(), 'path': obj.get_path_name()}
        for name in ('absolute_rotation','relative_rotation','inherit_pitch','inherit_yaw','inherit_roll','orient_rotation_to_movement','use_controller_desired_rotation'):
            try: row[name] = str(obj.get_editor_property(name))
            except Exception: pass
        out['components'].append(row)
for cls in (unreal.BlueprintGraphPin, unreal.BlueprintEditorLibrary, unreal.BlueprintGraphEditor):
    out['api'][cls.__name__] = {n: getattr(cls,n).__doc__ for n in dir(cls) if any(t in n for t in ('break_link','compile_blueprint','set_node_pos'))}
(Path(__file__).parent/'a03_preflight.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
