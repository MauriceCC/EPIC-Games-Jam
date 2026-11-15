"""Log actual crouch, movement, and animation state during one manual PIE run."""
import unreal as u

worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
elapsed = 0.0
seen_pie = False


def field(obj, *names):
    for name in names:
        try:
            return obj.get_editor_property(name)
        except Exception:
            continue
    return None


def sample(delta_time):
    global elapsed, seen_pie
    world = worlds.get_game_world()
    if not world:
        if seen_pie:
            u.unregister_slate_post_tick_callback(handle)
        return
    seen_pie = True
    elapsed += delta_time
    if elapsed < 0.25:
        return
    elapsed = 0.0
    pawn = u.GameplayStatics.get_player_character(world, 0)
    if not pawn:
        return
    mesh = pawn.get_editor_property('mesh')
    movement = pawn.get_editor_property('character_movement')
    velocity = pawn.get_velocity()
    input_vector = pawn.get_last_movement_input_vector()
    instance = mesh.get_anim_instance()
    asset = field(instance, 'current_asset', 'CurrentAsset') if instance else None
    hips = mesh.get_socket_location('hips')
    head = mesh.get_socket_location('head')
    left = mesh.get_socket_location('leftfoot')
    right = mesh.get_socket_location('rightfoot')
    foot_z = min(left.z, right.z)
    u.log(
        f'B_STEALTH_PIE crouched={field(pawn, "is_crouched", "bIsCrouched")} '
        f'pose={field(pawn, "B_StealthPoseState")} '
        f'speed={(velocity.x**2 + velocity.y**2)**0.5:.1f} '
        f'max_crouch_speed={field(movement, "max_walk_speed_crouched")} '
        f'input=({input_vector.x:.2f},{input_vector.y:.2f}) '
        f'anim_time={mesh.get_position():.2f} playing={mesh.is_playing()} '
        f'mode={field(movement, "movement_mode")} '
        f'asset={asset.get_name() if asset else None} hip_cm={hips.z-foot_z:.1f} '
        f'head_cm={head.z-foot_z:.1f} feet_delta_cm={abs(left.z-right.z):.1f} '
        f'anim_instance={instance.get_class().get_name() if instance else None}'
    )


def checked_sample(delta_time):
    try:
        sample(delta_time)
    except Exception:
        u.unregister_slate_post_tick_callback(handle)
        raise


handle = u.register_slate_post_tick_callback(checked_sample)
u.log('B_STEALTH_PIE diagnostic armed')
