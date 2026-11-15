"""Bring the arms closer during crouch walk and resume locomotion after rising."""
from pathlib import Path
import runpy
import unreal as u

HERE = Path(__file__).parent
ROOT = '/Game/Unscripted/'
ANIMATION = ROOT + 'Player/Animation/'
ASSETS = u.EditorAssetLibrary
LIB = u.BlueprintEditorLibrary
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play first.'
player = u.load_asset(ROOT + 'Player/BP_PlayerCharacter')
graph = u.BlueprintGraphEditor.get_graph_editor(LIB.find_event_graph(player))


def link(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


def call(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def adjust_arms():
    math = runpy.run_path(str(HERE / 'b_player_stealth_pose.py'))
    mul, inv, align, unit, dot = [math[name] for name in ('quat_multiply', 'inverse', 'align', 'unit', 'dot')]
    source = u.load_asset(ANIMATION + 'A_Agent_User_CrouchWalk')
    assert source, 'Missing supplied Agent crouch walk'
    path = ANIMATION + 'A_Agent_CrouchWalk_ArmsIn'
    target = u.load_asset(path) if ASSETS.does_asset_exist(path) else ASSETS.duplicate_loaded_asset(source, path)
    ext = u.AnimPoseExtensions
    tracks = {str(bone).casefold(): bone for bone in u.AnimationLibrary.get_animation_track_names(source)}
    options = u.AnimPoseEvaluationOptions()
    keys = {side + 'arm': [] for side in ('left', 'right')}
    for frame in range(u.AnimationLibrary.get_num_keys(source)):
        pose = ext.get_anim_pose_at_frame(source, frame, options)
        world = {side + part: ext.get_bone_pose(pose, tracks[side + part], u.AnimPoseSpaces.WORLD)
                 for side in ('left', 'right') for part in ('arm', 'forearm')}
        sideways = unit(world['rightarm'].translation - world['leftarm'].translation)
        for side in ('left', 'right'):
            name = side + 'arm'
            original = world[side + 'forearm'].translation - world[name].translation
            outward = sideways if side == 'right' else sideways * -1
            adjusted = original - outward * (max(0.0, dot(original, outward)) * 0.25)
            local = ext.get_bone_pose(pose, tracks[name], u.AnimPoseSpaces.LOCAL)
            parent = mul(world[name].rotation, inv(local.rotation))
            delta = align(original, adjusted)
            keys[name].append((local.translation, mul(inv(parent), mul(delta, world[name].rotation)), local.scale3d))
    controller = target.get_editor_property('controller')
    controller.open_bracket('Bring crouch walk arms closer')
    try:
        for name, samples in keys.items():
            translation, rotation, scale = map(list, zip(*samples))
            assert controller.set_bone_track_keys(tracks[name], translation, rotation, scale), name
    finally:
        controller.close_bracket()
    assert ASSETS.save_loaded_asset(target, False)
    return target


def blend_rise(source, destination, name, frames, moving):
    path = ANIMATION + name
    target = u.load_asset(path) if ASSETS.does_asset_exist(path) else ASSETS.duplicate_loaded_asset(destination, path)
    tracks = u.AnimationLibrary.get_animation_track_names(target)
    ext = u.AnimPoseExtensions
    options = u.AnimPoseEvaluationOptions()
    stationary = ext.get_anim_pose_at_frame(source, 0, options)
    final = ext.get_anim_pose_at_frame(destination, 0, options)
    controller = target.get_editor_property('controller')
    controller.open_bracket('Blend out of crouch')
    try:
        controller.set_frame_rate(u.FrameRate(numerator=30, denominator=1))
        controller.set_number_of_frames(u.FrameNumber(value=frames))
        poses = [ext.get_anim_pose_at_frame(source, frame, options) if moving else stationary
                 for frame in range(frames + 1)]
        for bone in tracks:
            end = ext.get_bone_pose(final, bone, u.AnimPoseSpaces.LOCAL)
            translations, rotations, scales = [], [], []
            for index, pose in enumerate(poses):
                t = index / frames
                t = t*t*(3 - 2*t)
                start = ext.get_bone_pose(pose, bone, u.AnimPoseSpaces.LOCAL)
                translations.append(start.translation * (1 - t) + end.translation * t)
                scales.append(start.scale3d * (1 - t) + end.scale3d * t)
                a, b = start.rotation, end.rotation
                first = (a.x, a.y, a.z, a.w)
                last = (b.x, b.y, b.z, b.w)
                sign = -1 if sum(x*y for x, y in zip(first, last)) < 0 else 1
                values = [x * (1 - t) + y * t * sign for x, y in zip(first, last)]
                size = sum(value*value for value in values)**0.5
                rotations.append(u.Quat(*(value / size for value in values)))
            assert controller.set_bone_track_keys(bone, translations, rotations, scales), bone
    finally:
        controller.close_bracket()
    assert ASSETS.save_loaded_asset(target, False)
    return target


def choose_moving_rise(standing, walking_clip):
    execute = LIB.find_execute_pin(standing)
    previous, = execute.list_connected_pins()
    if isinstance(previous.get_owning_node(), u.K2Node_IfThenElse):
        return
    mesh, = LIB.find_self_pin(standing).list_connected_pins()
    velocity = call('KismetMathLibrary.VSizeXY')
    link(LIB.find_result_pin(call('Actor.GetVelocity')), LIB.find_input_pin(velocity, 'A'))
    threshold = call('KismetMathLibrary.Greater_DoubleDouble')
    link(LIB.find_result_pin(velocity), LIB.find_input_pin(threshold, 'A'))
    assert LIB.find_input_pin(threshold, 'B').set_pin_value('30.0')
    branch = graph.add_branch_node()
    link(previous, LIB.find_execute_pin(branch))
    link(LIB.find_result_pin(threshold), LIB.find_condition_pin(branch))
    link(LIB.find_output_pin(branch, 'else'), execute)
    play = call('SkeletalMeshComponent.PlayAnimation')
    link(mesh, LIB.find_self_pin(play))
    assert LIB.find_input_pin(play, 'NewAnimToPlay').set_pin_value(walking_clip.get_path_name())
    assert LIB.find_input_pin(play, 'bLooping').set_pin_value('false')
    link(LIB.find_then_pin(branch), LIB.find_execute_pin(play))
    for target in LIB.find_then_pin(standing).list_connected_pins():
        link(LIB.find_then_pin(play), target)


def restore_walk(idle_play):
    start, = LIB.find_execute_pin(idle_play).list_connected_pins()
    if isinstance(start.get_owning_node(), u.K2Node_IfThenElse):
        return
    locomotion_class = ROOT + 'Art/Characters/Shared/BP_LocomotionAnim.BP_LocomotionAnim_C'
    component_node = start.get_owning_node()
    component, = LIB.find_self_pin(component_node).list_connected_pins()
    mesh, = LIB.find_self_pin(idle_play).list_connected_pins()

    def locomotion_field(name):
        node = graph.add_get_member_variable_node(name, locomotion_class)
        link(component, LIB.find_self_pin(node))
        return LIB.find_output_pin(node, name)

    speed = call('KismetMathLibrary.VSizeXY')
    link(LIB.find_result_pin(call('Actor.GetVelocity')), LIB.find_input_pin(speed, 'A'))

    def compare(previous, threshold):
        test = call('KismetMathLibrary.Greater_DoubleDouble')
        link(LIB.find_result_pin(speed), LIB.find_input_pin(test, 'A'))
        link(locomotion_field(threshold), LIB.find_input_pin(test, 'B'))
        node = graph.add_branch_node()
        link(previous, LIB.find_execute_pin(node))
        link(LIB.find_result_pin(test), LIB.find_condition_pin(node))
        return LIB.find_then_pin(node), LIB.find_output_pin(node, 'else')

    moving, stopped = compare(start, 'WalkThreshold')
    running, walking = compare(moving, 'RunThreshold')
    link(stopped, LIB.find_execute_pin(idle_play))
    for execute, animation in [(walking, 'WalkAnim'), (running, 'RunAnim')]:
        play = call('SkeletalMeshComponent.PlayAnimation')
        link(mesh, LIB.find_self_pin(play))
        link(locomotion_field(animation), LIB.find_input_pin(play, 'NewAnimToPlay'))
        assert LIB.find_input_pin(play, 'bLooping').set_pin_value('true')
        link(execute, LIB.find_execute_pin(play))


def install_footsteps():
    global graph
    name = 'B_UpdateStandingFootsteps'
    if any(name in str(LIB.get_node_title(node)) for node in graph.list_all_nodes()):
        return
    next_step = 'B_NextFootstepTime'
    if next_step not in {str(var) for var in LIB.list_member_variable_names(player)}:
        assert LIB.add_member_variable(player, next_step, LIB.get_basic_type_by_name('real'))
        assert LIB.compile_blueprint(player)
        graph = u.BlueprintGraphEditor.get_graph_editor(LIB.find_event_graph(player))

    event = graph.add_custom_event_node(name)
    start = LIB.find_then_pin(event)

    def check(condition, continue_when=True):
        nonlocal start
        branch = graph.add_branch_node()
        link(start, LIB.find_execute_pin(branch))
        link(condition, LIB.find_condition_pin(branch))
        start = LIB.find_then_pin(branch) if continue_when else LIB.find_output_pin(branch, 'else')

    crouched = graph.add_get_member_variable_node('bIsCrouched', '/Script/Engine.Character')
    check(LIB.find_output_pin(crouched, 'bIsCrouched'), False)
    movement = call('Pawn.GetMovementComponent')
    grounded = call('NavMovementComponent.IsMovingOnGround')
    link(LIB.find_result_pin(movement), LIB.find_self_pin(grounded))
    check(LIB.find_result_pin(grounded))
    speed = call('KismetMathLibrary.VSizeXY')
    link(LIB.find_result_pin(call('Actor.GetVelocity')), LIB.find_input_pin(speed, 'A'))
    moving = call('KismetMathLibrary.Greater_DoubleDouble')
    link(LIB.find_result_pin(speed), LIB.find_input_pin(moving, 'A'))
    assert LIB.find_input_pin(moving, 'B').set_pin_value('30.0')
    check(LIB.find_result_pin(moving))

    time = LIB.find_result_pin(call('GameplayStatics.GetTimeSeconds'))
    previous_time = graph.add_get_member_variable_node(next_step)
    ready = call('KismetMathLibrary.GreaterEqual_DoubleDouble')
    link(time, LIB.find_input_pin(ready, 'A'))
    link(LIB.find_output_pin(previous_time, next_step), LIB.find_input_pin(ready, 'B'))
    check(LIB.find_result_pin(ready))
    step = call('GameplayStatics.PlaySoundAtLocation')
    cue = u.load_asset(ROOT + 'Audio/SC_Footstep_Cobble')
    assert cue and LIB.find_input_pin(step, 'Sound').set_pin_value(cue.get_path_name())
    link(LIB.find_result_pin(call('Actor.K2_GetActorLocation')), LIB.find_input_pin(step, 'Location'))
    link(start, LIB.find_execute_pin(step))
    later = call('KismetMathLibrary.Add_DoubleDouble')
    link(time, LIB.find_input_pin(later, 'A'))
    interval = call('KismetSystemLibrary.MakeLiteralDouble')
    interval_input, = LIB.list_input_pins(interval)
    assert interval_input.set_pin_value('0.38')
    link(LIB.find_result_pin(interval), LIB.find_input_pin(later, 'B'))
    store = graph.add_set_member_variable_node(next_step)
    link(LIB.find_result_pin(later), LIB.find_input_pin(store, next_step))
    link(LIB.find_then_pin(step), LIB.find_execute_pin(store))

    assert LIB.compile_blueprint(player)
    tick, = [node for node in graph.list_all_nodes()
             if isinstance(node, u.K2Node_Event) and 'Tick' in str(LIB.get_node_title(node))]
    start = LIB.find_then_pin(tick)
    previous = list(start.list_connected_pins())
    update = graph.add_call_function_node(
        ROOT + 'Player/BP_PlayerCharacter.BP_PlayerCharacter_C.' + name)
    assert update
    link(start, LIB.find_execute_pin(update))
    for target in previous:
        link(LIB.find_then_pin(update), target)


animation = adjust_arms()
pins = []
for node in graph.list_all_nodes():
    if 'PlayAnimation' in str(LIB.get_node_title(node)).replace(' ', ''):
        pin = LIB.find_input_pin(node, 'NewAnimToPlay')
        pins.append((str(pin.get_pin_value()), pin, node))
walk_names = ('A_Agent_CrouchWalk', 'A_Agent_User_CrouchWalk',
              'A_Agent_CrouchWalk_ArmsIn', 'A_Agent_Mocap_Walk_crouched_forwards')
walk_pin, = [pin for value, pin, _ in pins if any(name in value for name in walk_names)]
assert walk_pin.set_pin_value(animation.get_path_name())
idle_names = ('A_Agent_CrouchIdle', 'A_Agent_User_CrouchIdle', 'A_Agent_Mocap_Idle_crouching')
quiet, = [pin for value, pin, _ in pins if any(name in value for name in idle_names)]
crouch_idle = u.load_asset(ANIMATION + 'A_Agent_User_CrouchIdle')
assert crouch_idle and quiet.set_pin_value(crouch_idle.get_path_name())
idle, = [node for value, _, node in pins if 'A_SK_Agent_Idle' in value]
rise, = [node for value, _, node in pins if '/A_Agent_StandUp.' in value]
base_animation = ROOT + 'Art/Characters/SK_Agent/Anims/A_SK_Agent_'
blend_rise(crouch_idle, u.load_asset(base_animation + 'Idle'), 'A_Agent_StandUp', 12, False)
moving_rise = blend_rise(animation, u.load_asset(base_animation + 'Walk'), 'A_Agent_RiseIntoWalk', 7, True)
choose_moving_rise(rise, moving_rise)
restore_walk(idle)
install_footsteps()
assert LIB.compile_blueprint(player)
assert ASSETS.save_loaded_asset(player, False)
u.log('B_CROUCH_POLISH saved crouch poses, standing locomotion handoff and silent stealth')
runpy.run_path(str(HERE / 'b_diagnose_stealth_pie.py'), run_name='__main__')
