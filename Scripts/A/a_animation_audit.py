"""Read-only animation wiring audit, runnable in Unreal Python commandlet."""
import json
from pathlib import Path
import unreal as u

out = {}
lib = u.BlueprintEditorLibrary
for path in ('Player/BP_PlayerCharacter', 'Enemies/BP_GuardBase', 'Art/Characters/Shared/BP_LocomotionAnim'):
    bp = u.load_asset('/Game/Unscripted/' + path)
    data = {'graphs': {}, 'defaults': {}}
    cdo = u.get_default_object(bp.generated_class())
    for name in lib.list_member_variable_names(bp):
        try:
            data['defaults'][str(name)] = str(cdo.get_editor_property(str(name)))
        except Exception:
            pass
    for graph in lib.list_graphs(bp):
        g = u.BlueprintGraphEditor.get_graph_editor(graph)
        data['graphs'][graph.get_name()] = [{'id': n.get_name(), 'title': str(n.get_node_title()), 'pins': [
            {'name': str(p.get_pin_name()), 'value': str(p.get_pin_value()), 'links': [q.get_owning_node().get_name()+'.'+str(q.get_pin_name()) for q in p.list_connected_pins()]}
            for p in n.list_all_pins()]} for n in g.list_all_nodes()]
    out[path] = data
Path(u.Paths.project_saved_dir(), 'animation_audit.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print('ANIMATION_AUDIT_OK')
