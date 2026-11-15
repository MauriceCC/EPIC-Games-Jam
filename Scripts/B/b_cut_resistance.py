"""Apply the Supervisor's resistance and expose guard eligibility for Frame Cut."""
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/Enemies/'
guard = u.load_asset(root + 'BP_GuardBase')


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(graph, path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def get(graph, field):
    return lib.find_output_pin(graph.add_get_member_variable_node(field), field)


if 'B_CutDurationScale' not in {str(name) for name in lib.list_member_variable_names(guard)}:
    assert lib.add_member_variable(guard, 'B_CutDurationScale', lib.get_basic_type_by_name('int'))
    assert lib.compile_blueprint(guard)
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(guard, 'ApplyTemporalFreeze'))
    entry = next(n for n in graph.list_all_nodes() if isinstance(n, u.K2Node_FunctionEntry))
    duration = lib.find_output_pin(entry, 'Duration')
    consumers = list(duration.list_connected_pins())
    assert len(consumers) >= 2

    scale = call(graph, 'KismetMathLibrary.Multiply_DoubleDouble')
    link(duration, lib.find_input_pin(scale, 'A'))
    link(get(graph, 'B_CutDurationScale'), lib.find_input_pin(scale, 'B'))
    clamp = call(graph, 'KismetMathLibrary.FMax')
    link(lib.find_result_pin(scale), lib.find_input_pin(clamp, 'A'))
    for target in consumers:
        link(lib.find_result_pin(clamp), target)

    existing = lib.find_graph(guard, 'CanBeTemporalCutTarget')
    if existing:
        check_graph = u.BlueprintGraphEditor.get_graph_editor(existing)
        result = next(n for n in check_graph.list_all_nodes() if isinstance(n, u.K2Node_FunctionResult))
        outcome = next(p for p in lib.list_input_pins(result) if str(p.get_pin_name()) != 'execute')
    else:
        check_graph = u.BlueprintGraphEditor.create_and_edit_function_graph(
            guard, 'CanBeTemporalCutTarget')
        result = check_graph.add_graph_output_parameter('Result', lib.get_basic_type_by_name('bool'))
        outcome = lib.find_input_pin(result, 'Result')
    alive = call(check_graph, 'KismetMathLibrary.Greater_DoubleDouble')
    link(get(check_graph, 'B_Health'), lib.find_input_pin(alive, 'A'))
    thawed = call(check_graph, 'KismetMathLibrary.Not_PreBool')
    link(get(check_graph, 'bIsTemporalFrozen'), lib.find_input_pin(thawed, 'A'))
    allowed = call(check_graph, 'KismetMathLibrary.BooleanAND')
    link(lib.find_result_pin(alive), lib.find_input_pin(allowed, 'A'))
    link(lib.find_result_pin(thawed), lib.find_input_pin(allowed, 'B'))
    link(lib.find_result_pin(allowed), outcome)
    link(check_graph.find_graph_entry_pin(), lib.find_execute_pin(result))
    assert lib.compile_blueprint(guard)

graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(guard, 'ApplyTemporalFreeze'))
if not any('maprangeclamped' in str(lib.get_node_title(n)).replace(' ', '').lower()
           for n in graph.list_all_nodes()):
    multiplier = next(n for n in graph.list_all_nodes()
                      if isinstance(n, u.K2Node_PromotableOperator) and '*' in str(lib.get_node_title(n)))
    percentage = call(graph, 'KismetMathLibrary.MapRangeClamped')
    link(get(graph, 'B_CutDurationScale'), lib.find_input_pin(percentage, 'Value'))
    assert lib.find_input_pin(percentage, 'InRangeB').set_pin_value('100.0')
    assert lib.find_input_pin(percentage, 'OutRangeB').set_pin_value('1.0')
    link(lib.find_result_pin(percentage), lib.find_input_pin(multiplier, 'B'))
    assert lib.compile_blueprint(guard)

for name, scale in [('BP_GuardBase', 100), ('BP_Supervisor', 35)]:
    asset = u.load_asset(root + name)
    u.get_default_object(asset.generated_class()).set_editor_property('B_CutDurationScale', scale)
    assert assets.save_loaded_asset(asset)
print('B_CUT_RESISTANCE_SAVED')
