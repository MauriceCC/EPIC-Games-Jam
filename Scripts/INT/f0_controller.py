"""Register the shared IMC for the local player controller at BeginPlay."""
import unreal

L = unreal.BlueprintEditorLibrary
G = unreal.BlueprintGraphEditor
A = unreal.EditorAssetLibrary
bp = A.load_asset('/Game/Unscripted/Player/BP_PlayerController')
graph = G.get_graph_editor(L.find_event_graph(bp))

def nodes():
    return graph.list_all_nodes()

def find_call(function_name):
    normalized = function_name.replace(' ', '').lower()
    return next((node for node in nodes()
                 if isinstance(node, unreal.K2Node_CallFunction)
                 and normalized in str(L.get_node_title(node)).replace(' ', '').lower()), None)

def connect_if_needed(output_pin, input_pin):
    if not any(pin.is_same_native_pin(input_pin) for pin in output_pin.list_connected_pins()):
        assert output_pin.try_create_connection(input_pin), 'Could not connect graph pins'

events = [node for node in nodes() if isinstance(node, unreal.K2Node_Event)]
begin = next((node for node in events
              if 'BeginPlay' in str(L.get_node_title(node)).replace(' ', '')), None)
if not begin:
    begin = L.add_event_override(bp, 'ReceiveBeginPlay', unreal.IntPoint(0, 0))
assert begin

local = find_call('IsLocalController')
if not local:
    local = graph.add_call_function_node('/Script/Engine.Controller.IsLocalController')

branches = [node for node in nodes() if isinstance(node, unreal.K2Node_IfThenElse)]
branch_local = branches[0] if branches else graph.add_branch_node()
connect_if_needed(L.find_then_pin(begin), L.find_execute_pin(branch_local))
connect_if_needed(L.find_result_pin(local), L.find_condition_pin(branch_local))

get_player = find_call('GetPlayerController')
if not get_player:
    get_player = graph.add_call_function_node('/Script/Engine.GameplayStatics.GetPlayerController')
assert L.find_input_pin(get_player, 'PlayerIndex').set_pin_value('0')

old_subsystem = find_call('GetLocalPlayerSubSystemFromPlayerController')
if old_subsystem:
    graph.remove_nodes([old_subsystem])
subsystem = graph.create_node_from_name(
    'Controladordejugador|Subsistemasdejugadorlocal|ObtenerEnhancedInputLocalPlayerSubsystem',
    unreal.Vector2D(900, 0), [L.find_result_pin(get_player)])
assert subsystem, 'Could not create Enhanced Input local player subsystem node'
controller_target = next((pin for pin in L.list_input_pins(subsystem)
                          if str(pin.get_pin_name()).lower() in ('self', 'target')), None)
if controller_target:
    connect_if_needed(L.find_result_pin(get_player), controller_target)

is_valid = find_call('IsValid')
if not is_valid:
    is_valid = graph.add_call_function_node('/Script/Engine.KismetSystemLibrary.IsValid')
connect_if_needed(L.find_result_pin(subsystem), L.find_input_pin(is_valid, 'Object'))

branches = [node for node in nodes() if isinstance(node, unreal.K2Node_IfThenElse)]
branch_valid = next((node for node in branches if node != branch_local), None)
if not branch_valid:
    branch_valid = graph.add_branch_node()
connect_if_needed(L.find_then_pin(branch_local), L.find_execute_pin(branch_valid))
connect_if_needed(L.find_result_pin(is_valid), L.find_condition_pin(branch_valid))

add = find_call('AddMappingContext')
if add:
    graph.remove_nodes([add])
add = graph.create_node_from_name(
    'Entrada|AddMappingContext', unreal.Vector2D(1320, 0),
    [L.find_then_pin(branch_valid)])
assert add
connect_if_needed(L.find_result_pin(subsystem), L.find_self_pin(add))
assert L.find_input_pin(add, 'MappingContext').set_pin_value(
    '/Game/Unscripted/Player/Input/IMC_Default.IMC_Default')
connect_if_needed(L.find_then_pin(branch_valid), L.find_execute_pin(add))

for index, node in enumerate([local, branch_local, get_player, subsystem,
                              is_valid, branch_valid, add]):
    L.set_node_pos(node, unreal.IntPoint(240 + index * 220, 0 if index % 2 else 180))

defaults = unreal.get_default_object(bp.generated_class())
defaults.set_editor_property('show_mouse_cursor', True)
assert L.compile_blueprint(bp)
assert A.save_loaded_asset(bp)
print('F0 controller mapping configured and compiled')
