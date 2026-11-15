"""Report the highest active detection value across all guards."""
import unreal as u

lib = u.BlueprintEditorLibrary
stealth = u.load_asset('/Game/Unscripted/Enemies/BP_StealthComponent')
asset_graph = lib.find_graph(stealth, 'ReportDetection')
assert asset_graph


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(name):
    node = graph.add_call_function_node('/Script/Engine.' + name)
    assert node, name
    return node


def plug(node, name, out):
    link(out, lib.find_input_pin(node, name))


if 'B_DetectionByGuard' not in {str(name) for name in lib.list_member_variable_names(stealth)}:
    graph = u.BlueprintGraphEditor.get_graph_editor(asset_graph)
    entry = next(n for n in graph.list_all_nodes() if isinstance(n, u.K2Node_FunctionEntry))
    actor = lib.find_output_pin(entry, 'Enemy')
    level = lib.find_output_pin(entry, 'Level')
    assert lib.add_member_variable(stealth, 'B_DetectionByGuard',
                                   lib.get_map_type(actor.get_pin_type(), level.get_pin_type()))
    assert lib.compile_blueprint(stealth)
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(stealth, 'ReportDetection'))
    entry = next(n for n in graph.list_all_nodes() if isinstance(n, u.K2Node_FunctionEntry))
    actor = lib.find_output_pin(entry, 'Enemy')
    level = lib.find_output_pin(entry, 'Level')
    storage = graph.add_get_member_variable_node('B_DetectionByGuard')
    records = lib.find_output_pin(storage, 'B_DetectionByGuard')
    clamp = call('KismetMathLibrary.FClamp')
    plug(clamp, 'Value', level)
    assert lib.find_input_pin(clamp, 'Max').set_pin_value('1.0')

    store = call('BlueprintMapLibrary.Map_Add')
    plug(store, 'TargetMap', records)
    plug(store, 'Key', actor)
    plug(store, 'Value', lib.find_result_pin(clamp))
    link(graph.find_graph_entry_pin(), lib.find_execute_pin(store))
    values = call('BlueprintMapLibrary.Map_Values')
    plug(values, 'TargetMap', records)
    value_array = lib.find_output_pin(values, 'Values')
    maximum = call('KismetMathLibrary.MaxOfFloatArray')
    plug(maximum, 'FloatArray', value_array)
    source = lib.find_then_pin(store)
    if lib.find_execute_pin(values).is_valid():
        link(source, lib.find_execute_pin(values))
        source = lib.find_then_pin(values)

    previous = graph.add_get_member_variable_node('DetectionLevel')
    difference = call('KismetMathLibrary.NotEqual_DoubleDouble')
    peak = lib.find_output_pin(maximum, 'MaxValue')
    plug(difference, 'A', lib.find_output_pin(previous, 'DetectionLevel'))
    plug(difference, 'B', peak)
    changed = graph.add_branch_node()
    link(source, lib.find_execute_pin(changed))
    link(lib.find_result_pin(difference), lib.find_condition_pin(changed))
    update = graph.add_set_member_variable_node('DetectionLevel')
    plug(update, 'DetectionLevel', peak)
    link(lib.find_then_pin(changed), lib.find_execute_pin(update))

    actions = [str(n) for n in graph.list_available_nodes([])
               if 'ondetectionchanged' in str(n).replace(' ', '').lower()]
    for action in actions:
        emit = graph.create_node_from_name(action, u.Vector2D(1100, 0), [])
        if emit and emit.get_class().get_name() == 'K2Node_CallDelegate':
            plug(emit, 'Level', peak)
            link(lib.find_then_pin(update), lib.find_execute_pin(emit))
            break
        if emit:
            graph.remove_nodes([emit])
    else:
        u.log_warning('OnDetectionChanged dispatcher call is unavailable in ReportDetection')
    assert lib.compile_blueprint(stealth)
    assert u.EditorAssetLibrary.save_loaded_asset(stealth)
print('B_STEALTH_AGGREGATE_SAVED')
