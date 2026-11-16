"""Read-only pose samples for the death presentation pass."""
import json
from pathlib import Path
import unreal as u

ext = u.AnimPoseExtensions
out = {}
paths = ['Unscripted/Art/Characters/SK_Agent/Anims/A_SK_Agent_Death',
         'Unscripted/Art/Characters/SK_Agent/Anims/A_SK_Agent_Idle',
         'Unscripted/Player/Animation/Polish/A_Agent_Death',
         'Characters/Mannequins/Anims/Death/MM_Death_Front_01']
for path in paths:
    clip = u.load_asset('/Game/' + path)
    bones = list(u.AnimationLibrary.get_animation_track_names(clip))
    frames = []
    for i in range(31):
        time = clip.get_play_length() * i / 30
        pose = ext.get_anim_pose_at_time(clip, time, u.AnimPoseEvaluationOptions())
        frames.append({str(b): {'p': ext.get_bone_pose(pose, b, u.AnimPoseSpaces.WORLD).translation.to_tuple(),
                               'q': ext.get_bone_pose(pose, b, u.AnimPoseSpaces.LOCAL).rotation.to_tuple()}
                       for b in bones})
    out[path] = {'length': clip.get_play_length(), 'frames': frames}
Path(u.Paths.project_saved_dir(), 'death_motion_probe.json').write_text(json.dumps(out))
print('DEATH_MOTION_PROBE_OK')
