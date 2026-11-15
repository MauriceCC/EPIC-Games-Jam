"""Read-only map inventory; never saves packages or modifies actors."""
import json
from pathlib import Path
import unreal as u

report = {}
for map_name in ('L_Whitechapel_AI', 'L_Whitechapel', 'Test/L_Test_B'):
    path = '/Game/Unscripted/Maps/' + map_name
    if not u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(path):
        report[map_name] = {'error': 'Could not load map'}
        continue
    rows = []
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        cls = actor.get_class().get_path_name()
        if '/Enemies/' not in cls:
            continue
        row = {'name': actor.get_actor_label(), 'class': cls,
               'object': actor.get_path_name(), 'location': str(actor.get_actor_location())}
        for field in ('Waypoints', 'PatrolRoute'):
            try:
                row[field] = str(actor.get_editor_property(field))
            except Exception:
                pass
        rows.append(row)
    report[map_name] = rows
output = Path(u.Paths.project_dir()).resolve().parent / 'SourceData/B/placement_audit.json'
output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print('B_PLACEMENT_AUDIT ' + str(output))
