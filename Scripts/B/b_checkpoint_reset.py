"""[PROPUESTA] Restore surviving guards and Jack while preserving completed outcomes."""
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/Enemies/'


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def get(field):
    return lib.find_output_pin(graph.add_get_member_variable_node(field), field)


def set_(source, field, value):
    write = graph.add_set_member_variable_node(field)
    inp = lib.find_input_pin(write, field)
    if isinstance(value, str):
        assert inp.set_pin_value(value), field
    else:
        link(value, inp)
    link(source, lib.find_execute_pin(write))
    return lib.find_then_pin(write)


for relative, is_jack in [('BP_GuardBase', False), ('Jack/BP_Jack', True)]:
    bp = u.load_asset(root + relative)
    if 'B_CheckpointStart' in {str(n) for n in lib.list_member_variable_names(bp)}:
        continue
    assert lib.add_member_variable(bp, 'B_CheckpointStart', lib.get_struct_type(u.Transform.static_struct()))
    if not is_jack:
        assert lib.add_member_variable(bp, 'B_CheckpointHealth', lib.get_basic_type_by_name('int'))
    assert lib.compile_blueprint(bp)
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))
    begin = next(n for n in graph.list_all_nodes()
                 if isinstance(n, u.K2Node_Event) and 'BeginPlay' in str(lib.get_node_title(n)))
    first = lib.find_then_pin(begin)
    previous = list(first.list_connected_pins())
    save = set_(first, 'B_CheckpointStart', lib.find_result_pin(call('Actor.GetTransform')))
    if not is_jack:
        save = set_(save, 'B_CheckpointHealth', get('B_Health'))
    for old in previous:
        link(save, old)

    restore = graph.add_custom_event_node('B_ResetAtCheckpoint')
    gate = graph.add_branch_node()
    if is_jack:
        finished = get('bReachedRefuge')
    else:
        depleted = call('KismetMathLibrary.LessEqual_DoubleDouble')
        link(get('B_Health'), lib.find_input_pin(depleted, 'A'))
        finished = lib.find_result_pin(depleted)
    link(finished, lib.find_condition_pin(gate))
    link(lib.find_then_pin(restore), lib.find_execute_pin(gate))
    reset = set_(lib.find_output_pin(gate, 'else'), 'CurrentWaypointIndex', '0')
    if is_jack:
        reset = set_(reset, 'bEscaping', 'false')
    else:
        reset = set_(reset, 'B_Health', get('B_CheckpointHealth'))
        reset = set_(reset, 'CurrentPosture', get('MaxPosture'))
        reset = set_(reset, 'bB_Stunned', 'false')
        reset = set_(reset, 'bCanAttack', 'true')
        reset = set_(reset, 'bIsTemporalFrozen', 'true')
        clear = call('KismetSystemLibrary.K2_ClearTimer')
        assert lib.find_input_pin(clear, 'FunctionName').set_pin_value('B_EndTemporalFreeze')
        link(reset, lib.find_execute_pin(clear))
        timer = call('KismetSystemLibrary.K2_SetTimer')
        assert lib.find_input_pin(timer, 'FunctionName').set_pin_value('B_EndTemporalFreeze')
        assert lib.find_input_pin(timer, 'Time').set_pin_value('0.5')
        link(lib.find_then_pin(clear), lib.find_execute_pin(timer))
        reset = lib.find_then_pin(timer)

    stop = call('Controller.StopMovement')
    link(lib.find_result_pin(call('Pawn.GetController')), lib.find_self_pin(stop))
    link(reset, lib.find_execute_pin(stop))
    transform = call('Actor.K2_SetActorTransform')
    link(get('B_CheckpointStart'), lib.find_input_pin(transform, 'NewTransform'))
    assert lib.find_input_pin(transform, 'bTeleport').set_pin_value('true')
    link(lib.find_then_pin(stop), lib.find_execute_pin(transform))
    assert lib.compile_blueprint(bp)
    assert assets.save_loaded_asset(bp)
print('B_CHECKPOINT_RESET_SAVED')
