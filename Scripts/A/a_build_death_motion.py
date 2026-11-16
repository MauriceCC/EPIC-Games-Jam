"""[PROPUESTA] Grounded, articulated falls for A/B; original art is read-only.

Run in Unreal Python before a_install_death_presentation.py. This is an authored
animation pass, not ragdoll: neutralized civilians retain their nonlethal state.
"""
import json
import math
import sys
from pathlib import Path
import unreal as u

sys.path.insert(0, str(Path(__file__).parent))
from a_polish_animation_assets import pose, local, multiply, blend

ROOT = '/Game/Unscripted/'
EXT = u.AnimPoseExtensions
RATE = 60
DURATION = 2.0
SUPPORT = {'hips': 10, 'spine': 9, 'spine01': 9, 'spine02': 9,
           'head': 11, 'leftarm': 5, 'rightarm': 5,
           'leftforearm': 4, 'rightforearm': 4, 'lefthand': 3, 'righthand': 3,
           'leftupleg': 6, 'rightupleg': 6, 'leftleg': 5, 'rightleg': 5,
           'leftfoot': 4, 'rightfoot': 4, 'lefttoebase': 2, 'righttoebase': 2}


def curve(keys, t):
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if t <= b:
            k = max(0, min(1, (t-a)/(b-a)))
            k = k*k*(3-2*k)
            return va + (vb-va)*k
    return keys[-1][1]


def conjugate(q):
    return u.Quat(-q.x,-q.y,-q.z,q.w)


def aim_delta(a, b):
    """Shortest rotation between two nonzero directions."""
    a, b = a/a.length(), b/b.length()
    cross = u.Vector(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
    w = 1+a.x*b.x+a.y*b.y+a.z*b.z
    norm = math.sqrt(cross.length()**2+w*w)
    if norm < .00001:
        return u.Quat(1,0,0,0)
    return u.Quat(cross.x/norm,cross.y/norm,cross.z/norm,w/norm)


def main():
    source = u.load_asset(ROOT+'Art/Characters/SK_Agent/Anims/A_SK_Agent_Death')
    ref_idle = u.load_asset(ROOT+'Art/Characters/SK_Agent/Anims/A_SK_Agent_Idle')
    ref = pose(ref_idle, 0)
    first = local(pose(source, 0), 'hips').translation
    source_poses = [pose(source, min(i/RATE/1.85, 1)*source.get_play_length())
                    for i in range(round(DURATION*RATE)+1)]
    report = []
    for who in ('Agent', 'Pursuer_A', 'Pursuer_B', 'Interventor', 'Supervisor'):
        folder = 'Player' if who == 'Agent' else 'Enemies'
        idle = u.load_asset(ROOT+'Art/Characters/SK_'+who+'/Anims/A_SK_'+who+'_Idle')
        neutral = pose(idle, 0)
        bones = list(u.AnimationLibrary.get_animation_track_names(idle))
        destination = ROOT+folder+'/Animation/Polish/A_'+who+'_Death'
        target = u.load_asset(destination) if u.EditorAssetLibrary.does_asset_exist(destination) else u.EditorAssetLibrary.duplicate_loaded_asset(idle, destination)
        base_hips = local(neutral, 'hips').translation
        stature = base_hips.z/local(ref, 'hips').translation.z
        data = {str(b): [] for b in bones}
        for i, sample in enumerate(source_poses):
            seconds = i/RATE
            progress = min(seconds/1.85, 1)
            for bone in bones:
                base, reference, action = local(neutral, bone), local(ref, bone), local(sample, bone)
                if str(bone) == 'armature':
                    action = base
                elif str(bone) == 'hips':
                    # Remove the imported 1.27 m initial offset and aerial launch.
                    # Keep the backward momentum and the original articulated recoil.
                    delta = action.translation-first
                    z = curve([(0, 1), (.12, .95), (.27, .70), (.40, .26),
                               (.51, .29), (.70, .26), (1, .26)], progress)
                    action.translation = u.Vector(base_hips.x+delta.x*stature,
                                                  base_hips.y+delta.y*stature*.85,
                                                  base_hips.z*z)
                else:
                    # Preserve target bone lengths, including the four enemy rigs.
                    action.translation = base.translation
                if who != 'Agent' and str(bone) != 'armature':
                    q = reference.rotation
                    action.rotation = multiply(base.rotation, multiply(u.Quat(-q.x,-q.y,-q.z,q.w), action.rotation))
                # The source is a launched backward hit. Reduce the airborne
                # leg kick and arm flail while retaining asymmetric knee/elbow
                # articulation, then recover its settled pose without a pop.
                if str(bone) in ('leftupleg','rightupleg','leftleg','rightleg',
                                 'leftarm','rightarm','leftforearm','rightforearm'):
                    minimum = .32 if 'upleg' in str(bone) else .62
                    weight = curve([(0,1),(.10,1),(.25,minimum),(.45,minimum),
                                    (.65,.82),(.82,1),(1,1)], progress)
                    _, action.rotation, _ = blend(base,action,weight)
                data[str(bone)].append(blend(base, action, seconds/.18))
        controller = target.get_editor_property('controller')
        controller.open_bracket('Grounded death: recoil, collapse and settle')
        try:
            controller.set_frame_rate(u.FrameRate(numerator=RATE, denominator=1))
            controller.set_number_of_frames(u.FrameNumber(value=round(DURATION*RATE)))
            for bone in bones:
                assert controller.set_bone_track_keys(bone, *map(list, zip(*data[str(bone)])))
        finally:
            controller.close_bracket()
        # Keep the feet low as support gives way instead of reproducing the
        # source's high kick. Rotate the thigh chain (no bone stretching), using
        # component-space geometry and converting back through the pelvis.
        for i in range(round(DURATION*RATE)+1):
            progress = min(i/RATE/1.85,1)
            weight = curve([(0,0),(.10,0),(.23,.9),(.40,1),(.58,.9),(.76,0),(1,0)],progress)
            if weight == 0: continue
            p = pose(target,i/RATE)
            parent = EXT.get_bone_pose(p,'hips',u.AnimPoseSpaces.WORLD).rotation
            for side in ('left','right'):
                thigh = EXT.get_bone_pose(p,side+'upleg',u.AnimPoseSpaces.WORLD)
                foot = EXT.get_bone_pose(p,side+'foot',u.AnimPoseSpaces.WORLD).translation
                if foot.z <= 18*stature: continue
                current = foot-thigh.translation
                length = current.length()
                z = max(-length+.01,min(length-.01,14*stature-thigh.translation.z))
                xy = math.sqrt(current.x*current.x+current.y*current.y)
                reach = math.sqrt(max(0,length*length-z*z))
                desired = u.Vector(current.x/max(xy,.001)*reach,current.y/max(xy,.001)*reach,z)
                rotation = multiply(conjugate(parent),multiply(aim_delta(current,desired),thigh.rotation))
                old = data[side+'upleg'][i]
                a, b = u.Transform(), u.Transform()
                a.translation, a.rotation, a.scale3d = old
                b.translation, b.rotation, b.scale3d = old[0], rotation, old[2]
                data[side+'upleg'][i] = blend(a,b,weight)
        controller.open_bracket('Reduce airborne kick without stretching legs')
        try:
            for bone in ('leftupleg','rightupleg'):
                assert controller.set_bone_track_keys(bone,*map(list,zip(*data[bone])))
        finally:
            controller.close_bracket()
        # Contact correction is sampled on the retargeted hierarchy, not guessed
        # from the source stature. Raise the pelvis only to prevent floor penetration.
        corrections = []
        for i in range(round(DURATION*RATE)+1):
            p = pose(target, i/RATE)
            low = min(EXT.get_bone_pose(p, b, u.AnimPoseSpaces.WORLD).translation.z-radius*stature
                      for b, radius in SUPPORT.items())
            corrections.append(max(0, -low))
        hips = data['hips']
        # Smooth the contact envelope with a short conservative neighbourhood.
        for i, (position, rotation, scale) in enumerate(hips):
            correction = max(corrections[max(0,i-1):i+2])
            hips[i] = (position+u.Vector(0,0,correction), rotation, scale)
        controller.open_bracket('Support clearance for target proportions')
        try:
            assert controller.set_bone_track_keys('hips', *map(list, zip(*hips)))
        finally:
            controller.close_bracket()
        assert u.EditorAssetLibrary.save_loaded_asset(target, False)
        report.append({'asset': destination, 'duration': DURATION,
                       'maximum_contact_correction_cm': max(corrections)})
    Path(u.Paths.project_saved_dir(), 'death_motion_build.json').write_text(json.dumps(report, indent=2))
    print('DEATH_MOTION_BUILT', len(report))


if __name__ == '__main__':
    main()
