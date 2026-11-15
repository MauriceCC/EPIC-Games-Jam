"""Add a health pool and nonlethal defeat to the guard and its archetypes."""
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/Enemies/'
guard = u.load_asset(root + 'BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))


def link(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


def flow(source, target):
    link(lib.find_then_pin(source), lib.find_execute_pin(target))


def call(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def value(node, field, default):
    assert lib.find_input_pin(node, field).set_pin_value(default), field


def health_pin():
    node = graph.add_get_member_variable_node('B_Health')
    return lib.find_output_pin(node, 'B_Health')


if 'B_Health' not in {str(name) for name in lib.list_member_variable_names(guard)}:
    assert lib.add_member_variable(guard, 'B_Health', lib.get_basic_type_by_name('float'))
    assert lib.compile_blueprint(guard)
    graph = u.BlueprintGraphEditor.create_and_edit_function_graph(guard, 'B_ApplyHealthDamage')
    incoming = graph.add_graph_input_parameter('Damage', lib.get_basic_type_by_name('float'))
    previous = health_pin()
    remaining = call('KismetMathLibrary.Subtract_DoubleDouble')
    link(previous, lib.find_input_pin(remaining, 'A'))
    link(incoming, lib.find_input_pin(remaining, 'B'))

    alive = call('KismetMathLibrary.Greater_DoubleDouble')
    link(previous, lib.find_input_pin(alive, 'A'))
    take_hit = graph.add_branch_node()
    link(lib.find_result_pin(alive), lib.find_condition_pin(take_hit))
    link(graph.find_graph_entry_pin(), lib.find_execute_pin(take_hit))
    update = graph.add_set_member_variable_node('B_Health')
    link(lib.find_result_pin(remaining), lib.find_input_pin(update, 'B_Health'))
    flow(take_hit, update)
    defeated = call('KismetMathLibrary.LessEqual_DoubleDouble')
    link(lib.find_output_pin(update, 'Output_Get'), lib.find_input_pin(defeated, 'A'))
    check = graph.add_branch_node()
    link(lib.find_result_pin(defeated), lib.find_condition_pin(check))
    flow(update, check)

    stop = call('Controller.StopMovement')
    link(lib.find_result_pin(call('Pawn.GetController')), lib.find_self_pin(stop))
    flow(check, stop)
    pause = call('Actor.SetActorTickEnabled')
    value(pause, 'bEnabled', 'false')
    flow(stop, pause)
    collision = call('Actor.SetActorEnableCollision')
    value(collision, 'bNewActorEnableCollision', 'false')
    flow(pause, collision)
    pose = call('Actor.K2_SetActorRotation')
    value(pose, 'NewRotation', '(Pitch=90,Yaw=0,Roll=0)')
    flow(collision, pose)
    assert lib.compile_blueprint(guard)
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
    event = graph.create_node_from_name(
        'Añadirevento|Juego|Daños|EventoAnyDamage', u.Vector2D(0, 1800), [])
    assert event
    apply_path = root + 'BP_GuardBase.BP_GuardBase_C.B_ApplyHealthDamage'
    apply = graph.add_call_function_node(apply_path)
    assert apply
    link(lib.find_output_pin(event, 'Damage'), lib.find_input_pin(apply, 'Damage'))
    flow(event, apply)
    assert lib.compile_blueprint(guard)

for name, maximum in [('BP_GuardBase', 45), ('BP_Pursuer', 45),
                      ('BP_Interventor', 80), ('BP_Supervisor', 180)]:
    bp = u.load_asset(root + name)
    u.get_default_object(bp.generated_class()).set_editor_property('B_Health', float(maximum))
    assert assets.save_loaded_asset(bp)
print('B_GUARD_HEALTH_SAVED')
