"""Explicitly start the installed BlendSpace when taking over the mesh."""
import unreal as u

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play first.'
lib = u.BlueprintEditorLibrary
bp = u.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
g = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))
nodes = g.list_all_nodes()
setter, = [n for n in nodes if 'SetAnimationAsset' in str(lib.get_node_title(n)).replace(' ', '')
           and 'BS_Agent_PostureSpeed' in str(lib.find_input_pin(n, 'NewAsset').get_pin_value())]
out = lib.find_then_pin(setter)
target, = out.list_connected_pins()
if 'SetPlaying' not in str(lib.get_node_title(target.get_owning_node())).replace(' ', ''):
    single, = lib.find_self_pin(setter).list_connected_pins()
    play = g.add_call_function_node('/Script/Engine.AnimSingleNodeInstance.SetPlaying')
    assert single.try_create_connection(lib.find_self_pin(play))
    assert lib.find_input_pin(play, 'bIsPlaying').set_pin_value('true')
    assert out.try_create_connection(lib.find_execute_pin(play))
    assert lib.find_then_pin(play).try_create_connection(target)
    assert lib.compile_blueprint(bp)
    assert not g.list_nodes_with_errors()
    assert u.EditorAssetLibrary.save_loaded_asset(bp, False)
print('B_MOTION playback starts explicitly')
