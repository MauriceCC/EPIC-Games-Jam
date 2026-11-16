"""Bake an in-place forward dodge roll on the existing Agent skeleton."""
import math

import unreal as u

from a_polish_animation_assets import local, multiply, pose

ROOT = '/Game/Unscripted/'
RATE = 60
FRAMES = 33
# The agent's imported skeleton faces +Y. Rotation around -X pitches forward.
ROLL_AXIS = u.Vector(-1, 0, 0)
SUPPORT = {
    'hips': 11, 'spine': 10, 'spine01': 10, 'spine02': 9, 'head': 10,
    'leftforearm': 4, 'rightforearm': 4, 'lefthand': 3, 'righthand': 3,
    'leftleg': 5, 'rightleg': 5, 'leftfoot': 4, 'rightfoot': 4,
    'lefttoebase': 2, 'righttoebase': 2,
}


def sample(keys, time, ease=True):
    for (start, a), (end, b) in zip(keys, keys[1:]):
        if time <= end:
            t = (time - start) / (end - start)
            if ease:
                t = t * t * (3 - 2 * t)
            return a + (b - a) * t
    return keys[-1][1]


def inverse(q):
    return u.Quat(-q.x, -q.y, -q.z, q.w)


def pitch(degrees):
    radians = math.radians(degrees) / 2
    return u.Quat(ROLL_AXIS.x * math.sin(radians), 0, 0, math.cos(radians))


def main():
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    idle = u.load_asset(ROOT + 'Art/Characters/SK_Agent/Anims/A_SK_Agent_Idle')
    neutral = pose(idle, 0)
    path = ROOT + 'Player/Animation/Polish/A_Agent_Dodge'
    assets = u.EditorAssetLibrary
    target = u.load_asset(path) if assets.does_asset_exist(path) else assets.duplicate_loaded_asset(idle, path)
    assert target.get_editor_property('skeleton') == idle.get_editor_property('skeleton')
    bones = [str(bone) for bone in u.AnimationLibrary.get_animation_track_names(idle)]
    rest = {bone: local(neutral, bone) for bone in bones}

    # Tuck feet and knees under a rounded torso, then plant the feet to rise.
    joint_pitch = {'spine': 18, 'spine01': 8, 'spine02': 9, 'neck': 15}
    for side, weight in (('left', 1.0), ('right', .91)):
        joint_pitch.update({side + bone: angle * weight for bone, angle in (
            ('upleg', -98), ('leg', 131), ('foot', -16), ('arm', -36), ('forearm', -60),
        )})
    joint_pitch = {bone: angle for bone, angle in joint_pitch.items() if bone in rest}
    parent_rotation = {}
    for bone in ('hips', *joint_pitch):
        world = u.AnimPoseExtensions.get_bone_pose(neutral, bone, u.AnimPoseSpaces.WORLD)
        parent_rotation[bone] = multiply(world.rotation, inverse(rest[bone].rotation))

    tracks = {bone: [] for bone in bones}
    for frame in range(FRAMES + 1):
        t = frame / FRAMES
        # Normalized pelvis pitch sampled from Sprinting Forward Roll.fbx.
        # The character movement supplies the forward travel.
        roll = sample(((0, 0), (.10, 31), (.20, 57), (.30, 86),
                       (.40, 114), (.50, 154), (.55, 195), (.60, 274),
                       (.70, 291), (.80, 323), (.90, 350), (1, 360)), t, ease=False)
        tuck = sample(((0, 0), (.25, .70), (.43, 1), (.66, 1), (.85, .45), (1, 0)), t)
        for bone, base in rest.items():
            position, rotation = base.translation, base.rotation
            if bone == 'hips' or bone in joint_pitch:
                angle = roll if bone == 'hips' else joint_pitch[bone] * tuck
                parent = parent_rotation[bone]
                rotation = multiply(inverse(parent), multiply(pitch(angle), multiply(parent, rotation)))
            tracks[bone].append((position, rotation, base.scale3d))

    controller = target.get_editor_property('controller')
    controller.open_bracket('Forward dodge roll')
    try:
        controller.set_frame_rate(u.FrameRate(numerator=RATE, denominator=1))
        controller.set_number_of_frames(u.FrameNumber(value=FRAMES))
        for bone, keys in tracks.items():
            assert controller.set_bone_track_keys(bone, *map(list, zip(*keys))), bone
    finally:
        controller.close_bracket()

    # Place the lowest support point near the floor during contact.
    offsets = []
    for frame in range(FRAMES + 1):
        sampled = pose(target, frame / RATE)
        low = min(u.AnimPoseExtensions.get_bone_pose(sampled, bone, u.AnimPoseSpaces.WORLD).translation.z - radius
                  for bone, radius in SUPPORT.items())
        offsets.append(-low * sample(((0, 0), (.17, 1), (.81, 1), (1, 0)), frame / FRAMES))
    hips = tracks['hips']
    controller.open_bracket('Ground the shoulder and feet')
    try:
        for i, (location, rotation, scale) in enumerate(hips):
            # The armature track is kept at its idle transform.
            hips[i] = (location + u.Vector(0, 0, offsets[i]), rotation, scale)
        assert controller.set_bone_track_keys('hips', *map(list, zip(*hips)))
    finally:
        controller.close_bracket()

    assert assets.save_loaded_asset(target, False)
    return target


if __name__ == '__main__':
    main()
