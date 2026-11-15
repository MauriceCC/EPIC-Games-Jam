"""Show the team's telegraph effect at the start of every guard windup."""
import unreal as u

lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/'
guard = u.load_asset(root + 'Enemies/BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
effect = root + 'VFX/NS_EnemyTelegraph.NS_EnemyTelegraph'
assert u.load_asset(effect)


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


if not any(str(lib.find_input_pin(n, 'SystemTemplate').get_pin_value()) == effect
           for n in graph.list_all_nodes()
           if 'spawnsystematlocation' in str(lib.get_node_title(n)).replace(' ', '').lower()):
    delay = next(n for n in graph.list_all_nodes() if n.get_name() == 'K2Node_CallFunction_4')
    assert 'Delay' in str(lib.get_node_title(delay))
    windup, = lib.find_execute_pin(delay).list_connected_pins()
    location = graph.add_call_function_node('/Script/Engine.Actor.K2_GetActorLocation')
    spawn = graph.add_call_function_node('/Script/Niagara.NiagaraFunctionLibrary.SpawnSystemAtLocation')
    assert spawn
    template = lib.find_input_pin(spawn, 'SystemTemplate')
    assert template.set_pin_value(effect)
    link(lib.find_result_pin(location), lib.find_input_pin(spawn, 'Location'))
    link(windup, lib.find_execute_pin(spawn))
    link(lib.find_then_pin(spawn), lib.find_execute_pin(delay))
    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
print('B_ATTACK_TELEGRAPH_SAVED')
