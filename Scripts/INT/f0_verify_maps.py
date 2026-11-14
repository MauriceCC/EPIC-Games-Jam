"""Read-only report of the editor's current world and loaded streaming levels."""
import json
from pathlib import Path
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
report = {
    'world': world.get_path_name() if world else None,
    'streaming_levels': [],
    'actors': [],
    'world_level_api': [name for name in dir(world)
                        if 'level' in name.lower() or 'stream' in name.lower()] if world else [],
}
if world:
    for level in unreal.EditorLevelUtils.get_levels(world):
        item = {'object': str(level)}
        for prop in ('package_name_to_load', 'should_be_loaded', 'should_be_visible',
                     'level_transform', 'outer'):
            try:
                item[prop] = str(level.get_editor_property(prop))
            except Exception:
                pass
        report['streaming_levels'].append(item)
    report['actors'] = [
        actor.get_actor_label()
        for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    ]

output = Path(unreal.Paths.project_saved_dir()) / 'F0_map_verification.json'
output.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
print('F0 current-world audit: ' + str(output))
