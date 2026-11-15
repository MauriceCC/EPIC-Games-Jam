"""Let guards build suspicion, investigate last contact and return to patrol."""
import json
import unreal as u

lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/'
guard = u.load_asset(root + 'Enemies/BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
nodes = {node.get_name(): node for node in graph.list_all_nodes()}


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node(path)
    assert node, path
    return node


def engine(path):
    return call('/Script/Engine.' + path)


def get(name):
    return lib.find_output_pin(graph.add_get_member_variable_node(name), name)


def branch(source, condition):
    node = graph.add_branch_node()
    link(source, lib.find_execute_pin(node))
    link(condition, lib.find_condition_pin(node))
    return lib.find_then_pin(node), lib.find_output_pin(node, 'else')


def comparison(name, value, threshold):
    node = engine('KismetMathLibrary.' + name)
    link(value, lib.find_input_pin(node, 'A'))
    assert lib.find_input_pin(node, 'B').set_pin_value(threshold)
    return lib.find_result_pin(node)


def state(source, name):
    node = graph.add_set_member_variable_node('CurrentAIState')
    inp = lib.find_input_pin(node, 'CurrentAIState')
    enum = json.loads(inp.get_pin_type_as_json_schema())['enum']
    assert inp.set_pin_value('NewEnumerator' + str(enum.index(name)))
    link(source, lib.find_execute_pin(node))
    return lib.find_then_pin(node)


if not any('LastKnownPlayerLocation' in str(lib.get_node_title(n)) for n in nodes.values()):
    vision = nodes['K2Node_IfThenElse_4']
    old_visible, = lib.find_then_pin(vision).list_connected_pins()
    old_patrol, = lib.find_output_pin(vision, 'else').list_connected_pins()
    # The existing sight score rises during contact and decays when line of sight is lost.
    score = get('B_SightScore')
    player = lib.find_result_pin(engine('GameplayStatics.GetPlayerCharacter'))
    player_location = engine('Actor.K2_GetActorLocation')
    link(player, lib.find_self_pin(player_location))
    remember = graph.add_set_member_variable_node('LastKnownPlayerLocation')
    link(lib.find_result_pin(player_location), lib.find_input_pin(remember, 'LastKnownPlayerLocation'))
    link(lib.find_then_pin(vision), lib.find_execute_pin(remember))

    component = engine('Actor.GetComponentByClass')
    link(player, lib.find_self_pin(component))
    assert lib.find_input_pin(component, 'ComponentClass').set_pin_value(
        root + 'Enemies/BP_StealthComponent.BP_StealthComponent_C')
    has_stealth = engine('KismetSystemLibrary.IsValid')
    link(lib.find_result_pin(component), lib.find_input_pin(has_stealth, 'Object'))
    graded, immediate = branch(lib.find_then_pin(remember), lib.find_result_pin(has_stealth))
    link(immediate, old_visible)
    confirmed, suspicion = branch(graded, comparison('GreaterEqual_DoubleDouble', score, '0.60'))
    link(confirmed, old_visible)
    stop = engine('Controller.StopMovement')
    controller = lib.find_result_pin(engine('Pawn.GetController'))
    link(controller, lib.find_self_pin(stop))
    link(state(suspicion, 'Suspicious'), lib.find_execute_pin(stop))

    investigate, resume = branch(lib.find_output_pin(vision, 'else'),
                                  comparison('Greater_DoubleDouble', score, '0.05'))
    link(resume, old_patrol)
    search = call('/Script/AIModule.AIBlueprintHelperLibrary.SimpleMoveToLocation')
    link(controller, lib.find_input_pin(search, 'Controller'))
    link(get('LastKnownPlayerLocation'), lib.find_input_pin(search, 'Goal'))
    link(state(investigate, 'Return'), lib.find_execute_pin(search))
    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
print('B_GUARD_INVESTIGATE_SAVED')
