"""Read-only asset checks and one manual PIE-run observer."""
import unreal as u
lib = u.BlueprintEditorLibrary
bp = u.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
g = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))
print('B_MOTION_CHECK errors', len(g.list_nodes_with_errors()), 'warnings', len(g.list_nodes_with_warnings()))
blend = u.load_asset('/Game/Unscripted/Player/Animation/B_MotionSync/BS_Agent_PostureSpeed')
print('B_MOTION_CHECK samples', len(blend.get_editor_property('sample_data')))
worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
if '_b_motion_observer' in globals():
    try:
        u.unregister_slate_post_tick_callback(_b_motion_observer)
    except Exception:
        pass
_b_motion_seen = False
_b_motion_elapsed = 0.0


def observe_motion(dt):
    global _b_motion_seen, _b_motion_elapsed
    world = worlds.get_game_world()
    if not world:
        if _b_motion_seen:
            u.unregister_slate_post_tick_callback(_b_motion_observer)
            u.log('B_MOTION_CHECK PIE ended')
        return
    _b_motion_seen = True
    _b_motion_elapsed += dt
    if _b_motion_elapsed < 0.2:
        return
    _b_motion_elapsed = 0.0
    pawn = u.GameplayStatics.get_player_character(world, 0)
    if not pawn:
        return
    mesh = pawn.get_editor_property('mesh')
    instance = mesh.get_anim_instance()
    velocity = pawn.get_velocity()
    speed = (velocity.x**2 + velocity.y**2)**0.5
    asset = instance.get_animation_asset() if isinstance(instance, u.AnimSingleNodeInstance) else None
    left = mesh.get_socket_location('leftfoot')
    right = mesh.get_socket_location('rightfoot')
    crouched = pawn.get_editor_property('bIsCrouched')
    u.log(f'B_MOTION_CHECK crouched={crouched} speed={speed:.1f} anim={asset.get_name() if asset else None} '
          f'time={mesh.get_position():.3f} foot_delta={left.z-right.z:.2f}')


_b_motion_observer = u.register_slate_post_tick_callback(observe_motion)
print('B_MOTION_CHECK observer armed for manual Play')
