import unreal as u
if 'handle' in globals():
    try:
        u.unregister_slate_post_tick_callback(handle)
    except Exception:
        pass
u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_end_play()


def restore_previous_motion(dt):
    if u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world():
        return
    u.unregister_slate_post_tick_callback(restore_handle)
    lib = u.BlueprintEditorLibrary
    bp = u.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))
    nodes = {n.get_name(): n for n in graph.list_all_nodes()}
    events = {str(lib.get_node_title(n)): n for n in graph.list_all_nodes() if isinstance(n, u.K2Node_CustomEvent)}
    for event, branch in [('B_UpdateAgentStealthPose', 'K2Node_IfThenElse_3'),
                          ('B_UpdateStandingFootsteps', 'K2Node_IfThenElse_16')]:
        out = lib.find_then_pin(events[event])
        target = lib.find_execute_pin(nodes[branch])
        assert target.is_valid()
        out.break_pin_links()
        assert out.try_create_connection(target)
    assert lib.compile_blueprint(bp)
    assert not graph.list_nodes_with_errors()
    assert u.EditorAssetLibrary.save_loaded_asset(bp, False)
    blend = u.load_asset('/Game/Unscripted/Player/Animation/B_MotionSync/BS_Agent_PostureSpeed')
    u.get_editor_subsystem(u.AssetEditorSubsystem).close_all_editors_for_asset(blend)
    u.log('B_MOTION_ROLLBACK restored original stealth and footsteps event connections; saved with zero graph errors')


restore_handle = u.register_slate_post_tick_callback(restore_previous_motion)
