"""Turn a guard toward nearby audible player movement before resuming vision."""
import unreal as u

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play before editing guards.'
lib = u.BlueprintEditorLibrary
guard = u.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))


def link(output, target):
    assert output.is_valid() and target.is_valid(), (output, target)
    assert output.try_create_connection(target), str(target.get_pin_name())


def call(path, **inputs):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    for name, value in inputs.items():
        pin = lib.find_self_pin(node) if name == 'target' else lib.find_input_pin(node, name)
        if isinstance(value, str):
            assert pin.set_pin_value(value), (path, name, value)
        else:
            link(value, pin)
    return node


def result(path, **inputs):
    return lib.find_result_pin(call(path, **inputs))


def check(flow, condition, take_true=True):
    branch = graph.add_branch_node()
    link(flow, lib.find_execute_pin(branch))
    link(condition, lib.find_condition_pin(branch))
    yes, no = lib.find_then_pin(branch), lib.find_output_pin(branch, 'else')
    return (yes, no) if take_true else (no, yes)


def install():
    nodes = {node.get_name(): node for node in graph.list_all_nodes()}
    if any('FindLookAtRotation' in str(lib.get_node_title(node)) for node in nodes.values()):
        return
    # The false edge is the existing out-of-sight branch for patrol/idle.
    vision = nodes['K2Node_IfThenElse_4']
    outside_vision = lib.find_output_pin(vision, 'else')
    successors = list(outside_vision.list_connected_pins())
    assert len(successors) == 1
    outside_vision.break_pin_links()
    player = result('GameplayStatics.GetPlayerCharacter')
    valid = result('KismetSystemLibrary.IsValid', Object=player)
    flow, failed = check(outside_vision, valid)
    link(failed, successors[0])
    movement = result('Pawn.GetMovementComponent', target=player)
    crouched = result('NavMovementComponent.IsCrouching', target=movement)
    flow, failed = check(flow, crouched, False)
    link(failed, successors[0])
    ground = result('NavMovementComponent.IsMovingOnGround', target=movement)
    flow, failed = check(flow, ground)
    link(failed, successors[0])
    speed = result('KismetMathLibrary.VSizeXY', A=result('Actor.GetVelocity', target=player))
    flow, failed = check(flow, result('KismetMathLibrary.Greater_DoubleDouble', A=speed, B='30.0'))
    link(failed, successors[0])
    distance = result('Actor.GetDistanceTo', OtherActor=player)
    flow, failed = check(flow, result('KismetMathLibrary.LessEqual_DoubleDouble', A=distance, B='360.0'))
    link(failed, successors[0])
    controller = result('Pawn.GetController')
    clear = result('Controller.LineOfSightTo', target=controller, Other=player)
    flow, failed = check(flow, clear)
    link(failed, successors[0])
    look = result('KismetMathLibrary.FindLookAtRotation',
                  Start=result('Actor.K2_GetActorLocation'), Target=result('Actor.K2_GetActorLocation', target=player))
    split = call('KismetMathLibrary.BreakRotator', InRot=look)
    rotation = result('KismetMathLibrary.MakeRotator', Yaw=lib.find_output_pin(split, 'Yaw'))
    stop = call('Controller.StopMovement', target=controller)
    turn = call('Actor.K2_SetActorRotation', NewRotation=rotation)
    link(flow, lib.find_execute_pin(stop))
    link(lib.find_then_pin(stop), lib.find_execute_pin(turn))
    assert lib.compile_blueprint(guard)
    assert not graph.list_nodes_with_errors()
    assert u.EditorAssetLibrary.save_loaded_asset(guard, False)
    u.log('B_HEARING saved')


install()
