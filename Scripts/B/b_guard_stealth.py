"""Use the player's stealth component during perception and publish per-guard detection."""
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/Enemies/'
guard = u.load_asset(root + 'BP_GuardBase')
stealth_class = root + 'BP_StealthComponent.BP_StealthComponent_C'


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node(path)
    assert node, path
    return node


def engine(path):
    return call('/Script/Engine.' + path)


def plug(node, name, out):
    link(out, lib.find_input_pin(node, name))


def get(name):
    return lib.find_output_pin(graph.add_get_member_variable_node(name), name)


def set_value(source, name, out=None):
    node = graph.add_set_member_variable_node(name)
    link(source, lib.find_execute_pin(node))
    if out is None:
        assert lib.find_input_pin(node, name).set_pin_value('1.0')
    else:
        plug(node, name, out)
    return lib.find_then_pin(node)


if 'B_VisibilityMultiplier' not in {str(n) for n in lib.list_member_variable_names(guard)}:
    for name in ('B_VisibilityMultiplier', 'B_SightScore'):
        assert lib.add_member_variable(guard, name, lib.get_basic_type_by_name('real'))
    assert lib.compile_blueprint(guard)
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
    nodes = {n.get_name(): n for n in graph.list_all_nodes()}
    tick = nodes['K2Node_Event_2']
    tick_out = lib.find_then_pin(tick)
    previous, = tick_out.list_connected_pins()

    player = lib.find_result_pin(engine('GameplayStatics.GetPlayerCharacter'))
    component = engine('Actor.GetComponentByClass')
    link(player, lib.find_self_pin(component))
    assert lib.find_input_pin(component, 'ComponentClass').set_pin_value(stealth_class)
    stealth = lib.find_result_pin(component)
    valid = engine('KismetSystemLibrary.IsValid')
    plug(valid, 'Object', stealth)
    gate = graph.add_branch_node()
    link(tick_out, lib.find_execute_pin(gate))
    link(lib.find_result_pin(valid), lib.find_condition_pin(gate))
    fail = set_value(lib.find_output_pin(gate, 'else'), 'B_VisibilityMultiplier')
    link(fail, previous)
    visibility = call(stealth_class + '.GetVisibilityMultiplier')
    link(stealth, lib.find_self_pin(visibility))
    begin = lib.find_then_pin(gate)
    execute = lib.find_execute_pin(visibility)
    if execute.is_valid():
        link(begin, execute)
        begin = lib.find_then_pin(visibility)
    multiplier = lib.find_output_pin(visibility, 'Result')
    begin = set_value(begin, 'B_VisibilityMultiplier', multiplier)

    for number in (2, 4, 6):
        compare = nodes[f'K2Node_PromotableOperator_{number}']
        threshold = lib.find_input_pin(compare, 'B')
        vision, = threshold.list_connected_pins()
        assert str(vision.get_pin_name()) == 'VisionRange'
        scaled = engine('KismetMathLibrary.Multiply_DoubleDouble')
        plug(scaled, 'A', vision)
        plug(scaled, 'B', get('B_VisibilityMultiplier'))
        link(lib.find_result_pin(scaled), threshold)

    sight, = lib.find_condition_pin(nodes['K2Node_IfThenElse_4']).list_connected_pins()
    desired = engine('KismetMathLibrary.SelectFloat')
    plug(desired, 'bPickA', sight)
    assert lib.find_input_pin(desired, 'A').set_pin_value('1.0')
    track = engine('KismetMathLibrary.FInterpTo_Constant')
    plug(track, 'Current', get('B_SightScore'))
    plug(track, 'Target', lib.find_result_pin(desired))
    plug(track, 'DeltaTime', lib.find_output_pin(tick, 'DeltaSeconds'))
    assert lib.find_input_pin(track, 'InterpSpeed').set_pin_value('0.9')
    begin = set_value(begin, 'B_SightScore', lib.find_result_pin(track))

    own_controller = lib.find_result_pin(engine('Pawn.GetController'))
    own_pawn = engine('Controller.K2_GetPawn')
    link(own_controller, lib.find_self_pin(own_pawn))
    report = call(stealth_class + '.ReportDetection')
    link(stealth, lib.find_self_pin(report))
    plug(report, 'Enemy', lib.find_result_pin(own_pawn))
    plug(report, 'Level', get('B_SightScore'))
    link(begin, lib.find_execute_pin(report))
    link(lib.find_then_pin(report), previous)

    assert lib.compile_blueprint(guard)
    u.get_default_object(guard.generated_class()).set_editor_property('B_VisibilityMultiplier', 1.0)
    assert assets.save_loaded_asset(guard)
print('B_GUARD_STEALTH_SAVED')
