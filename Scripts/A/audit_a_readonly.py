"""Read saved A assets without compiling, changing graphs, or saving packages."""
import json
from pathlib import Path
import unreal

OUT = Path(__file__).resolve().parent / 'audit_a_readonly.json'
L = unreal.BlueprintEditorLibrary
A = unreal.EditorAssetLibrary
report = {'mode': 'saved-assets commandlet inspection; not PIE', 'engine': unreal.SystemLibrary.get_engine_version(), 'blueprints': {}, 'input': {}, 'errors': []}

def props(obj, names):
    result = {}
    for name in names:
        try:
            result[name] = str(obj.get_editor_property(name))
        except Exception as exc:
            result[name + '_error'] = str(exc)
    return result

try:
    for path in A.list_assets('/Game/Unscripted/Player', recursive=True, include_folder=False):
        asset = A.load_asset(path)
        if isinstance(asset, unreal.Blueprint):
            data = {'graphs': [], 'defaults': {}}
            report['blueprints'][path] = data
            try:
                data['parent'] = str(L.get_blueprint_parent_class(asset))
                for graph in L.list_graphs(asset):
                    gd = {'name': graph.get_name(), 'nodes': []}
                    data['graphs'].append(gd)
                    editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
                    for node in editor.list_all_nodes():
                        nd = {'name': node.get_name(), 'title': str(L.get_node_title(node)), 'class': node.get_class().get_name(), 'pins': []}
                        gd['nodes'].append(nd)
                        for pin in L.list_all_pins(node):
                            nd['pins'].append({'name': str(pin.get_pin_name()), 'direction': str(pin.get_pin_direction()), 'value': str(pin.get_pin_value()), 'type': pin.get_pin_type().export_text(), 'links': [{'node': p.get_owning_node().get_name(), 'pin': str(p.get_pin_name())} for p in pin.list_connected_pins()]})
                default = unreal.get_default_object(asset.generated_class())
                names = [str(n) for n in L.list_member_variable_names(asset)]
                data['variables'] = names
                data['defaults'] = props(default, names)
                if isinstance(default, unreal.PlayerController):
                    data['defaults'].update(props(default, ['show_mouse_cursor']))
                if isinstance(default, unreal.Character):
                    data['defaults'].update(props(default, ['auto_possess_player', 'use_controller_rotation_yaw']))
                data['interfaces'] = {name: unreal.SystemLibrary.does_class_implement_interface(asset.generated_class(), A.load_asset('/Game/Unscripted/Core/Interfaces/' + name).generated_class()) for name in ['BPI_Damageable','BPI_PlayerControl','BPI_CheckpointListener']}
                helper = unreal.SubobjectDataBlueprintFunctionLibrary
                handles = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(asset)
                data['components'] = [str(helper.get_variable_name(helper.get_data(h))) for h in handles]
                data['component_details'] = []
                for h in handles:
                    obj = helper.get_object(helper.get_data(h))
                    if obj:
                        item = {'name': obj.get_name(), 'class': obj.get_class().get_path_name()}
                        if isinstance(obj, unreal.CameraComponent):
                            item.update(props(obj, ['relative_location','relative_rotation','projection_mode','field_of_view','ortho_width','auto_activate']))
                        elif isinstance(obj, unreal.SpringArmComponent):
                            item.update(props(obj, ['relative_rotation','target_arm_length','use_pawn_control_rotation','do_collision_test']))
                        data['component_details'].append(item)
            except Exception as exc:
                data['error'] = str(exc)
        elif isinstance(asset, unreal.InputAction):
            report['input'][path] = props(asset, ['value_type', 'accumulation_behavior', 'triggers', 'modifiers'])
        elif isinstance(asset, unreal.InputMappingContext):
            mappings = asset.get_editor_property('default_key_mappings').get_editor_property('mappings')
            report['input'][path] = [{'action': str(m.get_editor_property('action').get_path_name()), 'key': m.get_editor_property('key').export_text(), 'triggers': str(m.get_editor_property('triggers')), 'modifiers': [{'class': mod.get_class().get_name(), 'properties': props(mod, ['x','y','z'] if isinstance(mod, unreal.InputModifierNegate) else ['order'])} for mod in m.get_editor_property('modifiers')]} for m in mappings]
    mode = A.load_asset('/Game/Unscripted/Narrative/BP_GameMode')
    report['game_mode_defaults'] = props(unreal.get_default_object(mode.generated_class()), ['default_pawn_class','player_controller_class','game_state_class','hud_class'])
except Exception as exc:
    report['errors'].append(str(exc))
finally:
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print('A_READONLY_AUDIT: ' + str(OUT))
