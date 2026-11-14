"""Read-only details used to select supported editor operations."""
import unreal
from pathlib import Path
import json
names = ['Blueprint', 'BPInterfaceDescription', 'UserDefinedEnum', 'UserDefinedStruct',
         'SubobjectDataSubsystem', 'EditorLevelUtils', 'EditorLevelLibrary',
         'LevelEditorSubsystem', 'Enum', 'StructBase', 'SystemLibrary']
report = {}
for name in names:
    cls = getattr(unreal, name, None)
    if cls:
        report[name] = {'doc': cls.__doc__, 'methods': [n for n in dir(cls) if not n.startswith('_')]}
for name, path in [('enum','Core/Enums/ECombatState'), ('struct','Core/Structs/ST_HitInfo'), ('bp','Player/BP_PlayerCharacter')]:
    obj = unreal.load_asset('/Game/Unscripted/'+path)
    props = {}
    for prop in ['names','Names','display_name_map','DisplayNameMap','editor_data','EditorData','implemented_interfaces','ImplementedInterfaces']:
        try:
            props[prop] = str(obj.get_editor_property(prop))
        except Exception as e:
            props[prop] = str(e)
    report[name] = props
(Path(unreal.Paths.project_saved_dir())/'F0_probe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
