import unreal, json
from pathlib import Path
bp = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerController')
g = unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp))
data = {'doc':g.list_available_nodes.__doc__}
lib = unreal.BlueprintEditorLibrary
data['global_cast_nodes'] = [
    str(name) for name in g.list_available_nodes([])
    if 'casttoenhancedinput' in str(name).replace(' ', '').lower()
]
data['global_enhanced_nodes'] = [
    str(name) for name in g.list_available_nodes([])
    if 'enhancedinput' in str(name).replace(' ', '').lower()
]
data['graph_api_docs'] = {
    name: getattr(getattr(unreal.BlueprintGraphEditor, name), '__doc__', None)
    for name in ('cast', 'retarget_node_class', 'add_node_pin', 'create_node_from_name')
}
input_subsystem = getattr(unreal, 'EnhancedInputLocalPlayerSubsystem', None)
data['enhanced_input_subsystem'] = {
    'class': str(input_subsystem),
    'static_class': str(input_subsystem.static_class()),
    'class_api': [name for name in dir(input_subsystem.static_class())
                  if 'function' in name.lower()],
    'methods': [name for name in dir(input_subsystem) if 'mapping' in name.lower()],
    'add_mapping_doc': getattr(getattr(input_subsystem, 'add_mapping_context', None), '__doc__', None),
    'remove_mapping_doc': getattr(getattr(input_subsystem, 'remove_mapping_context', None), '__doc__', None),
} if input_subsystem else None
try:
    data['mapping_nodes'] = [
        str(name) for name in g.list_available_nodes([lib.find_then_pin(
            next(node for node in g.list_all_nodes() if isinstance(node, unreal.K2Node_Event)
                 and 'BeginPlay' in str(lib.get_node_title(node)).replace(' ', ''))
        )])
        if 'mapping' in str(name).lower() or 'contexto' in str(name).lower()
    ]
    data['subsystem_interface_nodes'] = [
        str(name) for name in g.list_available_nodes([lib.find_result_pin(
            next(node for node in g.list_all_nodes()
                 if isinstance(node, unreal.K2Node_CallFunction)
                 and 'GetLocalPlayerSubSystemFromPlayerController'
                 in str(lib.get_node_title(node)).replace(' ', ''))
        )])
        if 'enhancedinputsubsysteminterface' in str(name).replace(' ', '').lower()
        or 'enhanced input subsystem interface' in str(name).lower()
    ]
    data['cast_nodes'] = [
        str(name) for name in g.list_available_nodes([lib.find_result_pin(
            next(node for node in g.list_all_nodes()
                 if isinstance(node, unreal.K2Node_CallFunction)
                 and 'GetLocalPlayerSubSystemFromPlayerController'
                 in str(lib.get_node_title(node)).replace(' ', ''))
        )])
        if 'enhancedinputlocalplayersubsystem' in str(name).replace(' ', '').lower()
    ]
except Exception as e:
    data['mapping_nodes_error'] = str(e)
try:
    begin_node = next(
        node for node in g.list_all_nodes()
        if isinstance(node, unreal.K2Node_Event)
        and 'BeginPlay' in str(lib.get_node_title(node)).replace(' ', '')
    )
    data['available_nodes'] = [
        str(name) for name in g.list_available_nodes([lib.find_then_pin(begin_node)])
        if any(term in str(name).lower() for term in ('self', 'referencia', 'reference'))
    ]
except Exception as e:
    data['available_nodes_error'] = str(e)
data['pin_api_docs'] = {
    name: getattr(getattr(unreal.BlueprintEditorLibrary, name), '__doc__', None)
    for name in ('list_all_pins', 'list_input_pins', 'list_output_pins', 'find_self_pin', 'find_result_pin')
}
data['graph_nodes'] = []
for node in g.list_all_nodes():
    item = {'name': str(node.get_name()), 'class': str(type(node)), 'title': str(lib.get_node_title(node))}
    try:
        pos = node.get_node_pos()
        item['position'] = [pos.x, pos.y]
    except Exception as e:
        item['position_error'] = str(e)
    try:
        pins = list(lib.list_all_pins(node))
        if not pins:
            pins = list(node.get_editor_property('pins'))
        item['pins'] = [
            {
                'name': str(pin.get_pin_name()),
                'direction': str(pin.get_pin_direction()),
                'connections': [str(other.get_pin_name()) for other in pin.list_connected_pins()],
                'value': str(pin.get_pin_value()),
                'type': pin.get_pin_type_as_json_schema(),
                'type_display': str(pin.get_pin_type_display_string()),
                'type_data': str(pin.get_pin_type()),
            }
            for pin in pins
        ]
    except Exception as e:
        item['pins_error'] = str(e)
    data['graph_nodes'].append(item)
(Path(unreal.Paths.project_saved_dir())/'F0_graph_probe.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
