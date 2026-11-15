"""Give stealth playback exclusive control while crouching and rising."""
from pathlib import Path
import runpy
import unreal as u

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play before editing the Player Blueprint.'
lib = u.BlueprintEditorLibrary
player = u.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(player))


def link(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


poses = (
    (('A_Agent_CrouchIdle',), False),
    (('A_Agent_CrouchWalk', 'A_Agent_User_CrouchWalk'), False),
    (('A_Agent_StandUp',), False),
    (('A_SK_Agent_Idle',), True),
)
nodes = [node for node in graph.list_all_nodes()
         if 'PlayAnimation' in str(lib.get_node_title(node)).replace(' ', '')]
for animation_names, enable_locomotion in poses:
    play, = [node for node in nodes
             if any(name in str(lib.find_input_pin(node, 'NewAnimToPlay').get_pin_value())
                    for name in animation_names)]
    execute = lib.find_execute_pin(play)
    previous, = execute.list_connected_pins()
    title = str(lib.get_node_title(previous.get_owning_node())).replace(' ', '')
    if 'SetComponentTickEnabled' in title:
        continue
    component = graph.add_get_member_variable_node('LocomotionAnim')
    target = lib.find_output_pin(component, 'LocomotionAnim')
    setter = graph.add_call_function_node('/Script/Engine.ActorComponent.SetComponentTickEnabled')
    assert setter
    link(target, lib.find_self_pin(setter))
    assert lib.find_input_pin(setter, 'bEnabled').set_pin_value(str(enable_locomotion).lower())
    link(previous, lib.find_execute_pin(setter))
    link(lib.find_then_pin(setter), execute)

assert lib.compile_blueprint(player)
assert u.EditorAssetLibrary.save_loaded_asset(player)
u.log('B_CROUCH_PRIORITY saved exclusive crouch playback')
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('b_diagnose_stealth_pie.py')), run_name='__main__')
