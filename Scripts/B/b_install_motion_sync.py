"""Player-only continuous crouch blend and foot-contact audio (UE editor Python).

Does not alter shared locomotion, source clips, skeletons, maps or contracts.
Run outside PIE. Existing stealth input and combat remain authoritative.
"""
from pathlib import Path
from datetime import datetime
import shutil
import unreal as u

ROOT = '/Game/Unscripted/'
DEST = ROOT + 'Player/Animation/B_MotionSync/'
LIB = u.BlueprintEditorLibrary
ASSETS = u.EditorAssetLibrary
PLAYER = ROOT + 'Player/BP_PlayerCharacter'
LOCO = ROOT + 'Art/Characters/Shared/BP_LocomotionAnim.BP_LocomotionAnim_C'


def phase_aligned(source, name):
    """Copy a loop and align its left descending contact to normalized time zero."""
    target = u.load_asset(DEST + name) if ASSETS.does_asset_exist(DEST + name) else None
    if target:
        return target
    target = ASSETS.duplicate_loaded_asset(source, DEST + name)
    ext = u.AnimPoseExtensions
    options = u.AnimPoseEvaluationOptions()
    count = u.AnimationLibrary.get_num_keys(source)
    poses = [ext.get_anim_pose_at_frame(source, i, options) for i in range(count - 1)]
    bones = u.AnimationLibrary.get_animation_track_names(source)
    left, = [b for b in bones if str(b).lower() == 'leftfoot']
    heights = [ext.get_bone_pose(p, left, u.AnimPoseSpaces.WORLD).translation.z for p in poses]
    threshold = min(heights) + (max(heights) - min(heights)) * 0.12
    contacts = [i for i, z in enumerate(heights) if z <= threshold < heights[i - 1]]
    assert contacts, 'No left-foot descending contact: ' + source.get_name()
    offset = contacts[0]
    ordered = poses[offset:] + poses[:offset]
    ordered.append(ordered[0])
    controller = target.get_editor_property('controller')
    controller.open_bracket('Align locomotion foot phase')
    try:
        for bone in bones:
            track = [ext.get_bone_pose(p, bone, u.AnimPoseSpaces.LOCAL) for p in ordered]
            assert controller.set_bone_track_keys(bone, [t.translation for t in track],
                                                  [t.rotation for t in track], [t.scale3d for t in track])
    finally:
        controller.close_bracket()
    assert ASSETS.save_loaded_asset(target, False)
    u.log('B_MOTION phase aligned ' + name + ' frame=' + str(offset))
    return target


def build_blend():
    path = DEST + 'BS_Agent_PostureSpeed'
    existing = u.load_asset(path) if ASSETS.does_asset_exist(path) else None
    if existing:
        assert u.get_editor_subsystem(u.AssetEditorSubsystem).open_editor_for_assets([existing])
        assert ASSETS.save_loaded_asset(existing, False)
        return existing
    base = ROOT + 'Art/Characters/SK_Agent/Anims/A_SK_Agent_'
    idle = u.load_asset(base + 'Idle')
    crouch_idle = u.load_asset(ROOT + 'Player/Animation/A_Agent_User_CrouchIdle')
    walk = phase_aligned(u.load_asset(base + 'Walk'), 'A_Walk_Phase')
    run = phase_aligned(u.load_asset(base + 'Run'), 'A_Run_Phase')
    crouch = phase_aligned(u.load_asset(ROOT + 'Player/Animation/A_Agent_CrouchWalk_ArmsIn'), 'A_Crouch_Phase')
    factory = u.BlendSpaceFactoryNew()
    factory.set_editor_property('target_skeleton', idle.get_editor_property('skeleton'))
    blend = u.AssetToolsHelpers.get_asset_tools().create_asset('BS_Agent_PostureSpeed', DEST.rstrip('/'), u.BlendSpace, factory)
    axes = list(blend.get_editor_property('blend_parameters'))
    for axis, label, maximum, divisions in [(0, 'Speed', 340.0, 17), (1, 'Crouched', 1.0, 4)]:
        for key, value in [('display_name', label), ('min', 0.0), ('max', maximum), ('grid_num', divisions)]:
            axes[axis].set_editor_property(key, value)
    blend.set_editor_property('blend_parameters', axes)
    smoothing = list(blend.get_editor_property('interpolation_param'))
    for i, seconds in [(0, 0.10), (1, 0.22)]:
        smoothing[i].set_editor_property('interpolation_time', seconds)
    blend.set_editor_property('interpolation_param', smoothing)
    samples = []
    for clip, speed, crouched, rate in [(idle, 0, 0, 1), (walk, 180, 0, 1), (run, 340, 0, 1),
                                       (crouch_idle, 0, 1, 1), (crouch, 140, 1, 1), (crouch, 340, 1, 340 / 140)]:
        sample = u.BlendSample()
        sample.set_editor_property('animation', clip)
        sample.set_editor_property('sample_value', u.Vector(speed, crouched, 0))
        sample.set_editor_property('rate_scale', rate)
        samples.append(sample)
    blend.set_editor_property('sample_data', samples)
    blend.set_editor_property('axis_to_scale_animation', u.BlendSpaceAxis.BSA_X)
    # Setting SampleData through reflection does not call ResampleData. The native
    # BlendSpace editor builds its runtime triangulation on construction.
    assert u.get_editor_subsystem(u.AssetEditorSubsystem).open_editor_for_assets([blend])
    assert ASSETS.save_loaded_asset(blend, False)
    return blend


def install():
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play first.'
    player = u.load_asset(PLAYER)
    graph = u.BlueprintGraphEditor.get_graph_editor(LIB.find_event_graph(player))
    marker = 'B_MotionSyncV1'
    if any(str(LIB.get_node_title(n)) == marker for n in graph.list_all_nodes()):
        u.log('B_MOTION already installed; no changes')
        return
    events = {str(LIB.get_node_title(n)): n for n in graph.list_all_nodes() if isinstance(n, u.K2Node_CustomEvent)}
    assert 'B_UpdateAgentStealthPose' in events and 'B_UpdateStandingFootsteps' in events
    blend = build_blend()
    backup = Path(u.Paths.project_saved_dir()) / 'B_MotionSync' / datetime.now().strftime('%Y%m%d_%H%M%S')
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(u.Paths.project_content_dir()) / 'Unscripted/Player/BP_PlayerCharacter.uasset', backup)
    for name in ('B_LeftFootRaised', 'B_RightFootRaised'):
        if name not in {str(v) for v in LIB.list_member_variable_names(player)}:
            assert LIB.add_member_variable(player, name, LIB.get_basic_type_by_name('bool'))
    assert LIB.compile_blueprint(player)
    graph = u.BlueprintGraphEditor.get_graph_editor(LIB.find_event_graph(player))
    before = set(graph.list_all_nodes())
    original = [(LIB.find_then_pin(events[name]), list(LIB.find_then_pin(events[name]).list_connected_pins()))
                for name in ('B_UpdateAgentStealthPose', 'B_UpdateStandingFootsteps')]

    def link(a, b):
        assert a.is_valid() and b.is_valid()
        assert a.try_create_connection(b), str(b.get_pin_name())

    def value(pin, val):
        assert pin.set_pin_value(str(val).lower() if isinstance(val, bool) else str(val)), str(pin.get_pin_name())

    def call(name, **inputs):
        n = graph.add_call_function_node('/Script/Engine.' + name)
        assert n, name
        for key, val in inputs.items():
            p = LIB.find_self_pin(n) if key == 'self' else LIB.find_input_pin(n, key)
            if hasattr(val, 'is_valid'):
                link(val, p)
            else:
                value(p, val)
        return n

    def result(name, **inputs):
        return LIB.find_result_pin(call(name, **inputs))

    def get(name, owner='', target=None):
        n = graph.add_get_member_variable_node(name, owner)
        if target is not None:
            link(target, LIB.find_self_pin(n))
        return LIB.find_output_pin(n, name)

    def setvar(start, name, val):
        n = graph.add_set_member_variable_node(name)
        link(start, LIB.find_execute_pin(n))
        p = LIB.find_input_pin(n, name)
        if hasattr(val, 'is_valid'):
            link(val, p)
        else:
            value(p, val)
        return LIB.find_then_pin(n)

    def branch(start, condition):
        n = graph.add_branch_node()
        link(start, LIB.find_execute_pin(n))
        link(condition, LIB.find_condition_pin(n))
        return LIB.find_then_pin(n), LIB.find_else_pin(n)

    def invoke(start, name, **inputs):
        n = call(name, **inputs)
        link(start, LIB.find_execute_pin(n))
        return LIB.find_then_pin(n)

    try:
        event = graph.add_custom_event_node(marker)
        start = LIB.find_then_pin(event)
        mesh = get('Mesh', '/Script/Engine.Character')
        loco = get('LocomotionAnim')
        crouched = get('bIsCrouched', '/Script/Engine.Character')
        start, _ = branch(start, result('KismetSystemLibrary.IsValid', Object=loco))
        start = invoke(start, 'ActorComponent.SetComponentTickEnabled', self=loco, bEnabled=False)
        # The combat component continues owning one-shot animations while busy.
        busy, start = branch(start, get('bBusy', LOCO, loco))
        dead, start = branch(start, get('bDead'))
        for blocked in (busy, dead):
            tail = setvar(blocked, 'B_LeftFootRaised', False)
            setvar(tail, 'B_RightFootRaised', False)
        # Keep the gameplay stealth component driven by the actual capsule posture.
        stealth_class = ROOT + 'Enemies/BP_StealthComponent.BP_StealthComponent_C'
        stealth = result('Actor.GetComponentByClass', ComponentClass=stealth_class)
        valid, invalid = branch(start, result('KismetSystemLibrary.IsValid', Object=stealth))
        sync = graph.add_call_function_node(stealth_class + '.SetCrouched')
        link(valid, LIB.find_execute_pin(sync))
        link(stealth, LIB.find_self_pin(sync))
        param, = [p for p in LIB.list_input_pins(sync) if str(p.get_pin_name()) not in ('self', 'execute')]
        link(crouched, param)
        # Preserve the old event's callable name while replacing only its implementation.
        anim = result('SkeletalMeshComponent.GetAnimInstance', self=mesh)
        choices = [str(n) for n in graph.list_available_nodes([]) if str(n).endswith('|CastToAnimSingleNodeInstance')]
        cast = graph.create_node_from_name(choices[0], u.Vector2D(0, 0), [])
        link(LIB.find_then_pin(sync), LIB.find_execute_pin(cast))
        link(invalid, LIB.find_execute_pin(cast))
        link(anim, LIB.find_input_pin(cast, 'Object'))
        single, = [p for p in LIB.list_output_pins(cast) if str(p.get_pin_name()).startswith('As')]
        asset = result('AnimSingleNodeInstance.GetAnimationAsset', self=single)
        equal = result('KismetMathLibrary.EqualEqual_ObjectObject', A=asset, B=blend.get_path_name())
        playing, replace = branch(LIB.find_then_pin(cast), equal)
        replace = invoke(replace, 'AnimSingleNodeInstance.SetAnimationAsset', self=single,
                         NewAsset=blend.get_path_name(), bIsLooping=True, InPlayRate=1.0)
        speed = result('KismetMathLibrary.VSizeXY', A=result('Actor.GetVelocity'))
        posture = result('KismetMathLibrary.Conv_BoolToFloat', InBool=crouched)
        vector = result('KismetMathLibrary.MakeVector', X=speed, Y=posture, Z=0.0)
        update = call('AnimSingleNodeInstance.SetBlendSpacePosition', self=single, InPosition=vector)
        link(playing, LIB.find_execute_pin(update))
        link(replace, LIB.find_execute_pin(update))
        start = LIB.find_then_pin(update)
        moving = result('KismetMathLibrary.Greater_DoubleDouble', A=speed, B=30.0)
        start, stopped = branch(start, moving)
        silent, start = branch(start, crouched)
        grounded = result('NavMovementComponent.IsMovingOnGround', self=result('Pawn.GetMovementComponent'))
        start, airborne = branch(start, grounded)
        for reset in (stopped, silent, airborne):
            tail = setvar(reset, 'B_LeftFootRaised', False)
            setvar(tail, 'B_RightFootRaised', False)
        # Hysteresis: arm only after a foot rises; sound once as it returns to the
        # stance foot's level. Actual mesh motion determines cadence at every speed.
        for foot, other, name in [('leftfoot', 'rightfoot', 'B_LeftFootRaised'),
                                  ('rightfoot', 'leftfoot', 'B_RightFootRaised')]:
            pos = result('SceneComponent.GetSocketLocation', self=mesh, InSocketName=foot)
            other_pos = result('SceneComponent.GetSocketLocation', self=mesh, InSocketName=other)
            delta = result('KismetMathLibrary.Subtract_VectorVector', A=pos, B=other_pos)
            xyz = call('KismetMathLibrary.BreakVector', InVec=delta)
            z = LIB.find_output_pin(xyz, 'Z')
            high, low = branch(start, result('KismetMathLibrary.Greater_DoubleDouble', A=z, B=5.0))
            armed = setvar(high, name, True)
            down, middle = branch(low, result('KismetMathLibrary.LessEqual_DoubleDouble', A=z, B=1.5))
            hit, already = branch(down, get(name))
            hit = setvar(hit, name, False)
            hit = invoke(hit, 'GameplayStatics.PlaySoundAtLocation', Sound=ROOT + 'Audio/SC_Footstep_Cobble.SC_Footstep_Cobble', Location=pos)
            # Merge paths through a harmless setter to run the other foot as well.
            merge = graph.add_set_member_variable_node('B_StealthPoseState')
            value(LIB.find_input_pin(merge, 'B_StealthPoseState'), 0)
            for pin in (armed, middle, already, hit):
                link(pin, LIB.find_execute_pin(merge))
            start = LIB.find_then_pin(merge)
        assert LIB.compile_blueprint(player), 'New motion graph failed to compile'
        assert not graph.list_nodes_with_errors(), 'Graph has errors'
        # Only switch over after the replacement compiles; keep old nodes for recovery.
        for output, _ in original:
            output.break_pin_links()
        run = graph.add_call_function_node(PLAYER + '.BP_PlayerCharacter_C.' + marker)
        link(original[0][0], LIB.find_execute_pin(run))
        assert LIB.compile_blueprint(player)
        assert ASSETS.save_loaded_asset(player, False)
        u.log('B_MOTION installed continuous posture/speed blend and contact footsteps. Backup: ' + str(backup))
    except Exception:
        graph.remove_nodes([n for n in graph.list_all_nodes() if n not in before])
        for output, targets in original:
            output.break_pin_links()
            for target in targets:
                link(output, target)
        LIB.compile_blueprint(player)
        raise


if __name__ == '__main__':
    install()
