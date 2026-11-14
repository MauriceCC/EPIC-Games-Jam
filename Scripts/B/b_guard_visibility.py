"""Add facing and line-of-sight checks to the existing guard detection branches."""
import unreal as u

lib = u.BlueprintEditorLibrary
guard = u.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))


def connect(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


def function(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def all_true(first, second):
    node = function('KismetMathLibrary.BooleanAND')
    connect(first, lib.find_input_pin(node, 'A'))
    connect(second, lib.find_input_pin(node, 'B'))
    return lib.find_result_pin(node)


nodes = {node.get_name(): node for node in graph.list_all_nodes()}
if not any('LineOfSightTo' in str(lib.get_node_title(node)) for node in nodes.values()):
    states = []
    for branch_idx, comparison_idx in ((0, 2), (2, 4), (4, 6)):
        branch = nodes[f'K2Node_IfThenElse_{branch_idx}']
        comparison = nodes[f'K2Node_PromotableOperator_{comparison_idx}']
        range_pin = lib.find_input_pin(comparison, 'B')
        assert any(str(source.get_pin_name()) == 'VisionRange'
                   for source in range_pin.list_connected_pins())
        states.append((lib.find_condition_pin(branch), lib.find_result_pin(comparison)))

    player = lib.find_result_pin(function('GameplayStatics.GetPlayerCharacter'))
    controller = lib.find_result_pin(function('Pawn.GetController'))
    sight = function('Controller.LineOfSightTo')
    connect(controller, lib.find_self_pin(sight))
    connect(player, lib.find_input_pin(sight, 'Other'))

    angle = graph.add_get_member_variable_node('SightHalfAngle')
    cosine = function('KismetMathLibrary.DegCos')
    connect(lib.find_output_pin(angle, 'SightHalfAngle'), lib.find_input_pin(cosine, 'A'))
    dot = function('Actor.GetDotProductTo')
    connect(player, lib.find_input_pin(dot, 'OtherActor'))
    facing = function('KismetMathLibrary.GreaterEqual_DoubleDouble')
    connect(lib.find_result_pin(dot), lib.find_input_pin(facing, 'A'))
    connect(lib.find_result_pin(cosine), lib.find_input_pin(facing, 'B'))
    visible = all_true(lib.find_result_pin(sight), lib.find_result_pin(facing))

    for condition, in_range in states:
        # A boolean input accepts one source, so this connection replaces the range-only gate.
        connect(all_true(in_range, visible), condition)

    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
    print('B_GUARD_VISIBILITY_SAVED')
