"""Exercise the real blend on a disposable mesh in PIE, without input or map saves."""
import json
from pathlib import Path
import unreal as u
worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
level = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not worlds.get_game_world(), 'Stop manual Play before this isolated test.'
phases = [('walk', 180., 0.), ('crouch', 140., 1.), ('rise', 180., 0.), ('run', 340., 0.)]
state = {'elapsed': 0., 'actor': None, 'samples': {}, 'hips': {}, 'phase': -1}
output = Path(u.Paths.project_saved_dir()) / 'B_MotionSync' / 'blend_test.json'


def finish(error=None):
    results = {}
    for name, samples in state['samples'].items():
        results[name] = {'samples': len(samples), 'foot_motion_cm': max(samples) - min(samples)}
        results[name]['hip_height'] = sum(state['hips'][name]) / len(state['hips'][name])
    passed = error is None and len(results) == 4 and all(r['foot_motion_cm'] > 5. for r in results.values())
    passed = passed and results['walk']['hip_height'] - results['crouch']['hip_height'] > 10.
    output.write_text(json.dumps({'passed': passed, 'error': error, 'results': results}, indent=2))
    u.log('B_BLEND_TEST ' + output.read_text())
    u.unregister_slate_post_tick_callback(handle)
    level.editor_request_end_play()


def tick(dt):
    try:
        world = worlds.get_game_world()
        if not world:
            state['elapsed'] += dt
            if state['elapsed'] > 15:
                finish('PIE did not start')
            return
        if state['actor'] is None:
            state['elapsed'] += dt
            if state['elapsed'] < 1.0:
                return
            player = u.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
            actors = u.GameplayStatics.get_all_actors_of_class(world, player.generated_class())
            if not actors:
                state['elapsed'] += dt
                if state['elapsed'] > 15:
                    finish('No player spawned in simulation')
                return
            actor = actors[0]
            actor.set_actor_tick_enabled(False)
            actor.set_actor_location(u.Vector(0, 0, 3000), False, True)
            actor.get_editor_property('character_movement').disable_movement()
            loco_class = u.load_class(None, '/Game/Unscripted/Art/Characters/Shared/BP_LocomotionAnim.BP_LocomotionAnim_C')
            actor.get_component_by_class(loco_class).set_component_tick_enabled(False)
            state['actor'] = actor
            mesh = actor.get_component_by_class(u.SkeletalMeshComponent)
            source = u.get_default_object(player.generated_class()).get_editor_property('mesh')
            mesh.set_skeletal_mesh_asset(source.get_skeletal_mesh_asset())
            mesh.set_editor_property('visibility_based_anim_tick_option', u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
            mesh.play_animation(u.load_asset('/Game/Unscripted/Player/Animation/B_MotionSync/BS_Agent_PostureSpeed'), True)
            state['mesh'] = mesh
            state['elapsed'] = 0.
        state['elapsed'] += dt
        phase = int(state['elapsed'] / 2.5)
        if phase >= len(phases):
            finish()
            return
        name, speed, crouched = phases[phase]
        mesh = state['mesh']
        current = mesh.get_anim_instance().get_animation_asset()
        assert current and current.get_name() == 'BS_Agent_PostureSpeed', 'Test animation overwritten: ' + str(current)
        mesh.get_anim_instance().set_blend_space_position(u.Vector(speed, crouched, 0))
        if state['elapsed'] % 2.5 > 0.5:
            left = mesh.get_socket_location('leftfoot')
            right = mesh.get_socket_location('rightfoot')
            state['samples'].setdefault(name, []).append(left.z - right.z)
            hips = mesh.get_socket_location('hips')
            state['hips'].setdefault(name, []).append(hips.z - min(left.z, right.z))
    except Exception as error:
        finish(str(error))


handle = u.register_slate_post_tick_callback(tick)
level.editor_request_begin_play()
print('B_BLEND_TEST started isolated mesh test')
