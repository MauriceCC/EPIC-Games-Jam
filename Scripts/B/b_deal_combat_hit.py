"""Send B's melee impacts to the production player's combat receiver."""
import json
import unreal as u

lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/'
guard_path = root + 'Enemies/BP_GuardBase'
guard = u.load_asset(guard_path)
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
player_path = root + 'Player/BP_PlayerCharacter'


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node(path)
    assert node, path
    return node


def engine(path):
    return call('/Script/Engine.' + path)


def plug(node, name, source):
    link(source, lib.find_input_pin(node, name))


def get(name):
    return lib.find_output_pin(graph.add_get_member_variable_node(name), name)


if not any('receivecombathit' in str(lib.get_node_title(n)).replace(' ', '').lower()
           for n in graph.list_all_nodes()):
    nodes = {n.get_name(): n for n in graph.list_all_nodes()}
    native_damage = nodes['K2Node_CallFunction_9']
    assert 'ApplyDamage' in str(lib.get_node_title(native_damage))
    previous, = lib.find_execute_pin(native_damage).list_connected_pins()
    cooldown, = lib.find_then_pin(native_damage).list_connected_pins()

    actual_player = engine('GameplayStatics.GetActorOfClass')
    assert lib.find_input_pin(actual_player, 'ActorClass').set_pin_value(player_path + '.BP_PlayerCharacter_C')
    link(previous, lib.find_execute_pin(actual_player))
    target = lib.find_result_pin(actual_player)
    valid = engine('KismetSystemLibrary.IsValid')
    plug(valid, 'Object', target)
    choose = graph.add_branch_node()
    link(lib.find_then_pin(actual_player), lib.find_execute_pin(choose))
    link(lib.find_result_pin(valid), lib.find_condition_pin(choose))
    link(lib.find_output_pin(choose, 'else'), lib.find_execute_pin(native_damage))

    receive = call(player_path + '.BP_PlayerCharacter_C.ReceiveCombatHit')
    link(target, lib.find_self_pin(receive))
    info = lib.find_input_pin(receive, 'HitInfo')
    candidates = [str(n) for n in graph.list_available_nodes([info])
                  if 'makesthitinfo' in str(n).replace('_', '').replace(' ', '').lower()]
    assert candidates, 'Make ST_HitInfo'
    make = graph.create_node_from_name(candidates[0], u.Vector2D(1200, 2500), [info])
    assert make
    built, = lib.list_output_pins(make)
    link(built, info)
    fields = {str(pin.get_pin_name()).split('_')[0]: pin for pin in lib.list_input_pins(make)}
    link(get('AttackDamage'), fields['Damage'])
    link(get('PostureDamage'), fields['PostureDamage'])
    assert fields['bParryable'].set_pin_value('true')
    own = engine('Controller.K2_GetPawn')
    link(lib.find_result_pin(engine('Pawn.GetController')), lib.find_self_pin(own))
    link(lib.find_result_pin(own), fields['Instigator'])
    player_location = engine('Actor.K2_GetActorLocation')
    link(target, lib.find_self_pin(player_location))
    link(lib.find_result_pin(player_location), fields['HitLocation'])
    direction = engine('KismetMathLibrary.GetDirectionUnitVector')
    plug(direction, 'From', lib.find_result_pin(engine('Actor.K2_GetActorLocation')))
    plug(direction, 'To', lib.find_result_pin(player_location))
    link(lib.find_result_pin(direction), fields['HitDirection'])
    link(lib.find_then_pin(choose), lib.find_execute_pin(receive))

    parried = engine('KismetMathLibrary.EqualEqual_ByteByte')
    response = lib.find_output_pin(receive, 'Result')
    plug(parried, 'A', response)
    values = json.loads(response.get_pin_type_as_json_schema())['enum']
    assert lib.find_input_pin(parried, 'B').set_pin_value(str(values.index('Parried')))
    react = graph.add_branch_node()
    link(lib.find_then_pin(receive), lib.find_execute_pin(react))
    link(lib.find_result_pin(parried), lib.find_condition_pin(react))
    link(lib.find_output_pin(react, 'else'), cooldown)
    stagger = call(guard_path + '.BP_GuardBase_C.B_ApplyPostureDamage')
    plug(stagger, 'Amount', get('MaxPosture'))
    link(lib.find_then_pin(react), lib.find_execute_pin(stagger))
    link(lib.find_then_pin(stagger), cooldown)

make = next(n for n in graph.list_all_nodes()
            if isinstance(n, u.K2Node_MakeStruct)
            and 'hitinfo' in str(lib.get_node_title(n)).replace(' ', '').replace('_', '').lower())
attack_type = next(pin for pin in lib.list_input_pins(make)
                   if str(pin.get_pin_name()).startswith('AttackType'))
kinds = json.loads(attack_type.get_pin_type_as_json_schema())['enum']
assert attack_type.set_pin_value('NewEnumerator' + str(kinds.index('EnemyBasic')))
assert lib.compile_blueprint(guard)
assert u.EditorAssetLibrary.save_loaded_asset(guard)
print('B_DEAL_COMBAT_HIT_SAVED')
