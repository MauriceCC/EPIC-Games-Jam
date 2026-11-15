"""Exercise the player's normal animation graph in a temporary Play session."""
import unreal as u

worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
level = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not worlds.get_game_world(), 'Stop Play first.'
elapsed = 0.
samples = [[], [], []]
waited = 0.


def verify_player_motion(dt):
    global elapsed, waited
    try:
        waited += dt
        world = worlds.get_game_world()
        pawn = u.GameplayStatics.get_player_character(world, 0) if world else None
        if not pawn:
            assert waited < 18, 'No player'
            return
        elapsed += dt
        stage = int(elapsed / 2.)
        if stage >= 3:
            for i, group in enumerate(samples):
                u.log(f'B_PLAYER_PROOF stage={i} speed={max(x[0] for x in group):.1f} '
                      f'phase_range={max(x[1] for x in group)-min(x[1] for x in group):.3f} '
                      f'foot_range={max(x[2] for x in group)-min(x[2] for x in group):.1f} '
                      f'hip={sum(x[3] for x in group)/len(group):.1f} assets={set(x[4] for x in group)}')
            u.unregister_slate_post_tick_callback(motion_verify_handle)
            level.editor_request_end_play()
            return
        pawn.add_movement_input(u.Vector(1, 0, 0), 1.)
        if stage == 1:
            pawn.call_method('Crouch', args=(False,))
        else:
            pawn.call_method('UnCrouch', args=(False,))
        if elapsed % 2. > .55:
            mesh = pawn.get_editor_property('mesh')
            left = mesh.get_socket_location('leftfoot').z
            right = mesh.get_socket_location('rightfoot').z
            asset = mesh.get_anim_instance().get_animation_asset()
            samples[stage].append((pawn.get_velocity().length(), mesh.get_position(), left-right,
                                   mesh.get_socket_location('hips').z-min(left, right),
                                   asset.get_name() if asset else None))
    except Exception as error:
        u.log_error(f'B_PLAYER_PROOF {error}')
        u.unregister_slate_post_tick_callback(motion_verify_handle)
        level.editor_request_end_play()


motion_verify_handle = u.register_slate_post_tick_callback(verify_player_motion)
level.editor_request_begin_play()
