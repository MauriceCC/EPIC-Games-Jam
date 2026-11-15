"""Replace range debug prints with a timed Blueprint attack."""
import unreal as u

L = u.BlueprintEditorLibrary
A = u.EditorAssetLibrary
root = '/Game/Unscripted/'
bp = u.load_asset(root + 'Enemies/BP_GuardBase')
g = u.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp))

def inp(node, pin):
    p = L.find_input_pin(node, pin)
    assert p.is_valid(), (node, pin)
    return p

def link(output, input_):
    assert output.try_create_connection(input_), (output.get_pin_name(), input_.get_pin_name())

def flow(first, second):
    link(L.find_then_pin(first), L.find_execute_pin(second))

def value(node, pin, text):
    assert inp(node, pin).set_pin_value(text), (node, pin, text)

def call(path):
    node = g.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node

prints = [n for n in g.list_all_nodes()
          if 'PrintString' in str(L.get_node_title(n))
          and 'In Combat' in inp(n, 'InString').get_pin_value()]
assert prints, 'Expected original combat placeholders'
event = g.add_custom_event_node('B_TryMeleeAttack')
assert L.compile_blueprint(bp)
for node in prints:
    sources = L.find_execute_pin(node).list_connected_pins()
    assert len(sources) == 1
    trigger = g.add_call_function_node(root + 'Enemies/BP_GuardBase.BP_GuardBase_C.B_TryMeleeAttack')
    assert trigger, 'Attack custom event is not available'
    link(sources[0], L.find_execute_pin(trigger))
g.remove_nodes(prints)

def gate(source, condition):
    branch = g.add_branch_node()
    link(source, L.find_execute_pin(branch))
    link(condition, L.find_condition_pin(branch))
    return L.find_then_pin(branch)

def get(name):
    return L.find_output_pin(g.add_get_member_variable_node(name), name)

def set_flag(source, name, flag):
    node = g.add_set_member_variable_node(name)
    link(source, L.find_execute_pin(node))
    value(node, name, flag)
    return L.find_then_pin(node)

def delay(source, seconds):
    node = call('KismetSystemLibrary.Delay')
    link(source, L.find_execute_pin(node))
    value(node, 'Duration', seconds)
    return L.find_then_pin(node)

def not_(pin):
    node = call('KismetMathLibrary.Not_PreBool')
    link(pin, inp(node, 'A'))
    return L.find_result_pin(node)

ready = gate(L.find_then_pin(event), get('bCanAttack'))
ready = gate(ready, not_(get('bIsTemporalFrozen')))
windup = set_flag(ready, 'bCanAttack', 'false')
impact = delay(windup, '0.45')
player = L.find_result_pin(call('GameplayStatics.GetPlayerCharacter'))
valid = call('KismetSystemLibrary.IsValid')
link(player, inp(valid, 'Object'))
range_branch = g.add_branch_node()
link(impact, L.find_execute_pin(range_branch))
distance = call('Actor.GetDistanceTo')
link(player, inp(distance, 'OtherActor'))
in_range = call('KismetMathLibrary.Less_DoubleDouble')
link(L.find_result_pin(distance), inp(in_range, 'A'))
link(get('AttackRange'), inp(in_range, 'B'))

def both(left, right):
    node = call('KismetMathLibrary.BooleanAND')
    link(left, inp(node, 'A'))
    link(right, inp(node, 'B'))
    return L.find_result_pin(node)

eligible = both(L.find_result_pin(valid), both(L.find_result_pin(in_range), not_(get('bIsTemporalFrozen'))))
link(eligible, L.find_condition_pin(range_branch))
# Temporary native damage endpoint while A's combat receiver is a stub.
hit = call('GameplayStatics.ApplyDamage')
link(player, inp(hit, 'DamagedActor'))
link(get('AttackDamage'), inp(hit, 'BaseDamage'))
flow(range_branch, hit)
cooldown = call('KismetSystemLibrary.Delay')
value(cooldown, 'Duration', '1.25')
flow(hit, cooldown)
link(L.find_output_pin(range_branch, 'else'), L.find_execute_pin(cooldown))

set_flag(L.find_then_pin(cooldown), 'bCanAttack', 'true')
assert L.compile_blueprint(bp)
assert A.save_loaded_asset(bp)
print('B_MELEE_SAVED')




