"""[PROPUESTA] Expose Frame Cut and stealth controls on the B test pawn."""
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/Enemies/'
test_path = root + 'Test/BP_TestPlayer_B'
test = u.load_asset(test_path)
stealth_asset = root + 'BP_StealthComponent'
stealth_type = assets.load_blueprint_class(stealth_asset)
subobjects = u.get_engine_subsystem(u.SubobjectDataSubsystem)
data_lib = u.SubobjectDataBlueprintFunctionLibrary
handles = subobjects.k2_gather_subobject_data_for_blueprint(test)
if 'Stealth' not in {str(data_lib.get_variable_name(data_lib.get_data(h))) for h in handles}:
    request = u.AddNewSubobjectParams(
        parent_handle=handles[0], new_class=stealth_type, blueprint_context=test)
    handle, reason = subobjects.add_new_subobject(request)
    assert data_lib.is_handle_valid(handle), str(reason)
    assert subobjects.rename_subobject(handle, 'Stealth')
    assert lib.compile_blueprint(test)

graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(test))


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node(path)
    assert node, path
    return node


titles = [str(lib.get_node_title(n)).replace(' ', '').lower() for n in graph.list_all_nodes()]
if not any('applytemporalfreeze' in title for title in titles):
    key = graph.create_node_from_name(
        'Entrada|DebugEvents|KeyboardEvents|DebugKeyF', u.Vector2D(0, 1250), [])
    assert key
    find = call('/Script/Engine.GameplayStatics.GetActorOfClass')
    assert lib.find_input_pin(find, 'ActorClass').set_pin_value(root + 'BP_Pursuer.BP_Pursuer_C')
    target = lib.find_result_pin(find)
    link(lib.find_output_pin(key, 'Pressed'), lib.find_execute_pin(find))
    valid = call('/Script/Engine.KismetSystemLibrary.IsValid')
    link(target, lib.find_input_pin(valid, 'Object'))
    gate = graph.add_branch_node()
    link(lib.find_then_pin(find), lib.find_execute_pin(gate))
    link(lib.find_result_pin(valid), lib.find_condition_pin(gate))
    cut = call(root + 'BP_GuardBase.BP_GuardBase_C.ApplyTemporalFreeze')
    link(target, lib.find_self_pin(cut))
    link(lib.find_then_pin(gate), lib.find_execute_pin(cut))
    assert lib.find_input_pin(cut, 'Duration').set_pin_value('2.0')
    assert lib.find_input_pin(cut, 'PostureDamage').set_pin_value('10.0')

if not any('setcrouched' in title for title in titles):
    actions = [str(n) for n in graph.list_available_nodes([])
               if 'debugkeyleftctrl' in str(n).lower() or 'debugkeyleftcontrol' in str(n).lower()]
    assert actions, 'Left Ctrl action unavailable'
    key = graph.create_node_from_name(actions[0], u.Vector2D(0, 1650), [])
    assert key
    component = call('/Script/Engine.Actor.GetComponentByClass')
    assert lib.find_input_pin(component, 'ComponentClass').set_pin_value(stealth_asset + '.BP_StealthComponent_C')
    target = lib.find_result_pin(component)
    for pin, value in [('Pressed', 'true'), ('Released', 'false')]:
        setter = call(stealth_asset + '.BP_StealthComponent_C.SetCrouched')
        link(target, lib.find_self_pin(setter))
        link(lib.find_output_pin(key, pin), lib.find_execute_pin(setter))
        assert lib.find_input_pin(setter, 'bCrouched').set_pin_value(value)

assert lib.compile_blueprint(test)
assert assets.save_loaded_asset(test)
print('B_TEST_CONTROLS_SAVED')
