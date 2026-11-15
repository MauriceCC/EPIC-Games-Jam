"""Clear a neutralized guard's contribution to the player's detection meter."""
import unreal as u

lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/Enemies/'
guard = u.load_asset(root + 'BP_GuardBase')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(guard, 'B_ApplyHealthDamage'))
stealth_class = root + 'BP_StealthComponent.BP_StealthComponent_C'


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node(path)
    assert node, path
    return node


if not any('reportdetection' in str(lib.get_node_title(n)).replace(' ', '').lower()
           for n in graph.list_all_nodes()):
    pose = next(n for n in graph.list_all_nodes()
                if 'setactorrotation' in str(lib.get_node_title(n)).replace(' ', '').lower())
    player = lib.find_result_pin(call('/Script/Engine.GameplayStatics.GetPlayerCharacter'))
    component = call('/Script/Engine.Actor.GetComponentByClass')
    link(player, lib.find_self_pin(component))
    assert lib.find_input_pin(component, 'ComponentClass').set_pin_value(stealth_class)
    target = lib.find_result_pin(component)
    valid = call('/Script/Engine.KismetSystemLibrary.IsValid')
    link(target, lib.find_input_pin(valid, 'Object'))
    branch = graph.add_branch_node()
    link(lib.find_then_pin(pose), lib.find_execute_pin(branch))
    link(lib.find_result_pin(valid), lib.find_condition_pin(branch))

    own = call('/Script/Engine.Controller.K2_GetPawn')
    controller = call('/Script/Engine.Pawn.GetController')
    link(lib.find_result_pin(controller), lib.find_self_pin(own))
    report = call(stealth_class + '.ReportDetection')
    link(target, lib.find_self_pin(report))
    link(lib.find_result_pin(own), lib.find_input_pin(report, 'Enemy'))
    assert lib.find_input_pin(report, 'Level').set_pin_value('0.0')
    link(lib.find_then_pin(branch), lib.find_execute_pin(report))
    assert lib.compile_blueprint(guard)
    assert u.EditorAssetLibrary.save_loaded_asset(guard)
print('B_GUARD_DEFEAT_STEALTH_SAVED')
