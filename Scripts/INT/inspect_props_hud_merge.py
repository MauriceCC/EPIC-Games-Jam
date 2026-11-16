"""Read-only snapshots for the authorized props/HUD integration. Run in UE Python."""
import json
import os
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
outdir = repo / 'Unscripted/Saved/PropsHudMerge'
outdir.mkdir(parents=True, exist_ok=True)
report = {'engine': u.SystemLibrary.get_engine_version(), 'blueprints': {}, 'actors': []}
lib = u.BlueprintEditorLibrary

def properties(obj, names):
    result = {}
    for name in names:
        try:
            result[name] = str(obj.get_editor_property(name))
        except Exception:
            pass
    return result

for relative in ['Player/BP_PlayerCharacter', 'Narrative/BP_FinalChoice',
                 'Narrative/BP_ObjectiveManager', 'Narrative/BP_GameMode']:
    bp = u.load_asset('/Game/Unscripted/' + relative)
    assert bp, relative
    data = {'graphs': {}, 'defaults': {}, 'components': []}
    report['blueprints'][relative] = data
    for raw in lib.list_graphs(bp):
        graph = u.BlueprintGraphEditor.get_graph_editor(raw)
        nodes = {}
        data['graphs'][raw.get_name()] = nodes
        for node in graph.list_all_nodes():
            pins = {}
            nodes[node.get_name()] = {'class': node.get_class().get_name(),
                                     'title': str(node.get_node_title()), 'pins': pins}
            for pin in node.list_all_pins():
                pins[str(pin.get_pin_name())] = {
                    'value': str(pin.get_pin_value()), 'type': pin.get_pin_type().export_text(),
                    'links': sorted((p.get_owning_node().get_name(), str(p.get_pin_name()))
                                    for p in pin.list_connected_pins())}
    cdo = u.get_default_object(bp.generated_class())
    data['defaults'] = properties(cdo, [str(n) for n in lib.list_member_variable_names(bp)])
    if isinstance(cdo, u.Character):
        data['movement'] = properties(cdo.character_movement,
            ['orient_rotation_to_movement', 'max_walk_speed', 'max_walk_speed_crouched'])
    helper = u.SubobjectDataBlueprintFunctionLibrary
    for handle in u.get_engine_subsystem(u.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(bp):
        obj = helper.get_object(helper.get_data(handle))
        if obj:
            names = ['MaxHealth', 'CurrentHealth', 'MaxStamina', 'CurrentStamina',
                     'LightAttackStaminaCost', 'DodgeStaminaCost', 'ParryStaminaCost',
                     'StaminaRegenRate', 'StaminaRegenDelay']
            data['components'].append({'name': str(helper.get_variable_name(helper.get_data(handle))),
                'class': obj.get_class().get_path_name(), 'properties': properties(obj, names)})

table = u.load_asset('/Game/Unscripted/Narrative/DT_HUDText')
report['hud_csv'] = u.DataTableFunctionLibrary.export_data_table_to_csv_string(table)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert levels.load_level('/Game/Unscripted/Maps/L_Whitechapel')
for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    package = actor.get_outermost().get_path_name()
    if package.endswith(('L_Whitechapel_Story', 'L_Whitechapel_AI')):
        report['actors'].append({'label': actor.get_actor_label(), 'name': actor.get_name(),
            'class': actor.get_class().get_path_name(), 'package': package,
            'location': str(actor.get_actor_location()), 'rotation': str(actor.get_actor_rotation()),
            'scale': str(actor.get_actor_scale3d()), 'properties': properties(actor, [
                'SelectedEnding', 'bAuthenticFile', 'bConfirmFile', 'InteractionPrompt',
                'InteractionPromptRow', 'InteractionPriority', 'EvidenceType', 'CheckpointId',
                'bInteractionEnabled', 'bReportsEscapeRoute', 'RequiredStoryPhase'])})
target = outdir / (os.environ.get('UNSCRIPTED_MERGE_SNAPSHOT', 'snapshot') + '.json')
target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print('MERGE_SNAPSHOT ' + str(target))
