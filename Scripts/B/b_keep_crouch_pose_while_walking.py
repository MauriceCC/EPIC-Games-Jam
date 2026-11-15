"""Restore the original crouch idle and carry its silhouette into the walk."""
from pathlib import Path
import runpy
import unreal as u

ROOT = '/Game/Unscripted/'
ANIMATION = ROOT + 'Player/Animation/'
ASSETS = u.EditorAssetLibrary
ext = u.AnimPoseExtensions
options = u.AnimPoseEvaluationOptions()
leg_solver = runpy.run_path(str(Path(__file__).with_name('b_player_stealth_pose.py')))['solve_leg']


def read(sequence, frame, bones, space):
    pose = ext.get_anim_pose_at_frame(sequence, frame, options)
    return {name: ext.get_bone_pose(pose, bone, space) for name, bone in bones.items()}


def build_walk():
    idle = u.load_asset(ANIMATION + 'A_Agent_CrouchIdle')
    walk = u.load_asset(ROOT + 'Art/Characters/SK_Agent/Anims/A_SK_Agent_Walk')
    output = u.load_asset(ANIMATION + 'A_Agent_CrouchWalk')
    assert idle and walk and output
    bones = {str(bone).casefold(): bone for bone in u.AnimationLibrary.get_animation_track_names(output)}
    local = read(idle, 0, bones, u.AnimPoseSpaces.LOCAL)
    stance = read(idle, 0, bones, u.AnimPoseSpaces.WORLD)
    frame_count = u.AnimationLibrary.get_num_keys(walk)
    assert frame_count > 2 and frame_count == u.AnimationLibrary.get_num_keys(output)
    motion_bones = {name: bones[name] for name in ('hips', 'leftfoot', 'rightfoot')}
    steps = [read(walk, frame, motion_bones, u.AnimPoseSpaces.WORLD) for frame in range(frame_count)]
    feet = {}
    for side in ('left', 'right'):
        name = side + 'foot'
        offsets = [step[name].translation - step['hips'].translation for step in steps]
        center_y = sum(offset.y for offset in offsets) / frame_count
        floor_z = min(step[name].translation.z for step in steps)
        neutral = stance[name].translation
        feet[side] = [
            u.Vector(neutral.x, neutral.y + (offset.y - center_y) * 0.65,
                     neutral.z + max(0.0, step[name].translation.z - floor_z) * 0.65)
            for step, offset in zip(steps, offsets)
        ]
        # Duplicate the opening contact on the final frame for a clean wrap.
        feet[side][-1] = feet[side][0]

    rotations = {name: [] for name in bones}
    for frame in range(frame_count):
        legs = {}
        for side, targets in feet.items():
            legs.update(leg_solver(side, local, stance, u.Vector(), 0.0, targets[frame]))
        for name in bones:
            rotations[name].append(legs.get(name, local[name].rotation))

    editor = output.get_editor_property('controller')
    editor.open_bracket('Carry crouch stance through walking')
    try:
        for name, track in bones.items():
            assert editor.set_bone_track_keys(
                track, [local[name].translation] * frame_count, rotations[name],
                [local[name].scale3d] * frame_count), name
    finally:
        editor.close_bracket()

    check_bones = {name: bones[name] for name in ('hips', 'leftfoot', 'rightfoot')}
    result = [read(output, frame, check_bones, u.AnimPoseSpaces.WORLD) for frame in range(frame_count)]
    expected = stance['hips'].translation
    assert max((sample['hips'].translation - expected).length() for sample in result) < 0.5
    for name in ('leftfoot', 'rightfoot'):
        first = result[0][name].translation
        assert max((sample[name].translation - first).length() for sample in result) > 2.0, name
    assert ASSETS.save_loaded_asset(output, False)
    return {
        'A_Agent_Mocap_Idle_crouching': idle,
        'A_Agent_Mocap_Walk_crouched_forwards': output,
    }


def wire_original_assets(replacements):
    lib = u.BlueprintEditorLibrary
    player = u.load_asset(ROOT + 'Player/BP_PlayerCharacter')
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(player))
    pins = [
        lib.find_input_pin(node, 'NewAnimToPlay') for node in graph.list_all_nodes()
        if 'PlayAnimation' in str(lib.get_node_title(node)).replace(' ', '')
    ]
    for imported, desired in replacements.items():
        pin, = [pin for pin in pins if imported in str(pin.get_pin_value())
                or desired.get_name() in str(pin.get_pin_value())]
        assert pin.set_pin_value(desired.get_path_name())
    assert lib.compile_blueprint(player)
    assert ASSETS.save_loaded_asset(player)
    u.log('B_CROUCH_WALK saved original idle and verified moving feet at the same hip height')


assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play before changing crouch clips.'
wire_original_assets(build_walk())
runpy.run_path(str(Path(__file__).with_name('b_diagnose_stealth_pie.py')), run_name='__main__')
