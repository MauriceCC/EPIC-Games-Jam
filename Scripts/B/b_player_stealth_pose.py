"""Build prototype crouched locomotion for the Agent's Meshy skeleton."""
from math import cos, radians, sin, sqrt

import unreal as u

ASSETS = '/Game/Unscripted/Art/Characters/SK_Agent/Anims/A_SK_Agent_'
OUTPUT = '/Game/Unscripted/Player/Animation/'
TORSO_ANGLES = {'spine02': -20, 'spine01': -8, 'neck': 8}
LEG_TRACKS = ('upleg', 'leg', 'foot')
HIP_DROP_CM = 29.0


def quat_multiply(a, b):
    return u.Quat(
        a.w*b.x + a.x*b.w + a.y*b.z - a.z*b.y,
        a.w*b.y - a.x*b.z + a.y*b.w + a.z*b.x,
        a.w*b.z + a.x*b.y - a.y*b.x + a.z*b.w,
        a.w*b.w - a.x*b.x - a.y*b.y - a.z*b.z,
    )


def inverse(q):
    return u.Quat(-q.x, -q.y, -q.z, q.w)


def rotate(q, vector):
    point = u.Quat(vector.x, vector.y, vector.z, 0)
    result = quat_multiply(quat_multiply(q, point), inverse(q))
    return u.Vector(result.x, result.y, result.z)


def dot(a, b):
    return a.x*b.x + a.y*b.y + a.z*b.z


def unit(vector):
    length = vector.length()
    assert length > 0.0001, 'Zero-length Agent bone or IK axis'
    return vector * (1 / length)


def align(original, target):
    a, b = unit(original), unit(target)
    result = u.Quat(
        a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x,
        1 + dot(a, b),
    )
    length = sqrt(result.x**2 + result.y**2 + result.z**2 + result.w**2)
    assert length > 0.0001, 'Unexpected 180-degree leg rotation'
    return u.Quat(result.x/length, result.y/length, result.z/length, result.w/length)


def solve_leg(side, local, world, drop, weight, ankle_target=None):
    thigh_name, shin_name, foot_name = [side + suffix for suffix in LEG_TRACKS]
    thigh, shin, foot = [world[name] for name in (thigh_name, shin_name, foot_name)]
    upper_segment = shin.translation - thigh.translation
    lower_segment = foot.translation - shin.translation
    upper, lower = upper_segment.length(), lower_segment.length()
    hip = thigh.translation + drop
    ankle = u.Vector(
        foot.translation.x,
        foot.translation.y + (thigh.translation.y - foot.translation.y) * weight * 0.28,
        foot.translation.z,
    )
    if ankle_target is not None:
        ankle = ankle_target
    axis = unit(ankle - hip)
    distance = max(abs(upper - lower) + 0.01, min((ankle - hip).length(), upper + lower - 0.01))
    ankle = hip + axis * distance
    forward = u.Vector(0, 1, 0)
    bend = unit(forward - axis * dot(forward, axis))
    knee_offset = (upper*upper + distance*distance - lower*lower) / (2 * distance)
    knee = hip + axis * knee_offset + bend * sqrt(max(0, upper*upper - knee_offset*knee_offset))

    upper_rotation = quat_multiply(align(upper_segment, knee - hip), thigh.rotation)
    lower_rotation = quat_multiply(align(lower_segment, ankle - knee), shin.rotation)
    hips_rotation = quat_multiply(thigh.rotation, inverse(local[thigh_name].rotation))
    return {
        thigh_name: quat_multiply(inverse(hips_rotation), upper_rotation),
        shin_name: quat_multiply(inverse(upper_rotation), lower_rotation),
        foot_name: quat_multiply(inverse(lower_rotation), foot.rotation),
    }


def crouch_keys(local, world, suffix, weight, leg_rotations):
    parent_rotation = quat_multiply(world.rotation, inverse(local.rotation))
    half_angle = radians(TORSO_ANGLES.get(suffix, 0) * weight * 0.5)
    component_delta = u.Quat(sin(half_angle), 0, 0, cos(half_angle))
    delta = quat_multiply(quat_multiply(inverse(parent_rotation), component_delta), parent_rotation)
    translation = local.translation
    if suffix == 'hips':
        drop = rotate(inverse(parent_rotation), u.Vector(0, 0, -HIP_DROP_CM * weight))
        translation = u.Vector(
            translation.x + drop.x * local.scale3d.x / world.scale3d.x,
            translation.y + drop.y * local.scale3d.y / world.scale3d.y,
            translation.z + drop.z * local.scale3d.z / world.scale3d.z,
        )
    return translation, leg_rotations.get(suffix, quat_multiply(delta, local.rotation)), local.scale3d


def make_clip(source, name, mode):
    asset_path = OUTPUT + name
    assets = u.EditorAssetLibrary
    target = assets.load_asset(asset_path) if assets.does_asset_exist(asset_path) else assets.duplicate_loaded_asset(source, asset_path)
    assert target, asset_path
    controller = target.get_editor_property('controller')
    original_frames = u.AnimationLibrary.get_num_keys(source)
    assert original_frames > 1, source.get_name()
    options = u.AnimPoseEvaluationOptions()
    preview = u.AnimPoseExtensions.get_anim_pose_at_frame(source, 0, options)
    bones = u.AnimationLibrary.get_animation_track_names(source)
    suffixes = {str(bone).rsplit(':', 1)[-1].casefold(): bone for bone in bones}
    required = {'hips', *TORSO_ANGLES}
    required.update(side + suffix for side in ('left', 'right') for suffix in LEG_TRACKS)
    missing = required - suffixes.keys()
    assert not missing, f'Agent skeleton missing required tracks: {sorted(missing)}'

    controller.open_bracket('Generate Agent stealth animation')
    try:
        if mode == 'rise':
            controller.set_frame_rate(u.FrameRate(numerator=30, denominator=1))
            controller.set_number_of_frames(u.FrameNumber(value=12))
        target_frames = u.AnimationLibrary.get_num_keys(target)
        tracks = {bone: [] for bone in bones}
        for index in range(target_frames):
            if mode == 'rise':
                t = index / (target_frames - 1)
                weight = 1 - t*t*(3 - 2*t)
                pose = preview
            else:
                weight = 1.0
                pose = u.AnimPoseExtensions.get_anim_pose_at_frame(
                    source, min(index, original_frames - 1), options)
            local = {suffix: u.AnimPoseExtensions.get_bone_pose(pose, bone, u.AnimPoseSpaces.LOCAL)
                     for suffix, bone in suffixes.items()}
            world = {suffix: u.AnimPoseExtensions.get_bone_pose(pose, bone, u.AnimPoseSpaces.WORLD)
                     for suffix, bone in suffixes.items()}
            leg_rotations = {}
            if weight > 0:
                drop = u.Vector(0, 0, -HIP_DROP_CM * weight)
                for side in ('left', 'right'):
                    leg_rotations.update(solve_leg(side, local, world, drop, weight))
            for suffix, bone in suffixes.items():
                tracks[bone].append(crouch_keys(local[suffix], world[suffix], suffix, weight, leg_rotations))
        for bone, keys in tracks.items():
            translations, rotations, scales = map(list, zip(*keys))
            assert controller.set_bone_track_keys(bone, translations, rotations, scales), bone
    finally:
        controller.close_bracket()
    assert assets.save_loaded_asset(target)
    u.log(f'B_AGENT_POSE saved {name} ({target_frames} keys)')
    return target


def build():
    # Unreal exposes UAnimationBlueprintLibrary to Python via its ScriptName.
    if not hasattr(u, 'AnimationLibrary') and hasattr(u, 'load_module'):
        u.load_module('AnimationBlueprintLibrary')
    assert hasattr(u, 'AnimationLibrary'), 'Unreal did not load the AnimationBlueprintLibrary module.'
    idle = u.load_asset(ASSETS + 'Idle')
    walk = u.load_asset(ASSETS + 'Walk')
    assert idle and walk, 'Missing Agent source animations'
    return (
        idle,
        make_clip(idle, 'A_Agent_CrouchIdle', 'idle'),
        make_clip(walk, 'A_Agent_CrouchWalk', 'walk'),
        make_clip(idle, 'A_Agent_StandUp', 'rise'),
    )


if __name__ == '__main__':
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play before updating animations.'
    build()
