"""[PROPUESTA] Bake local action clips with contact timing and eased recovery.

Only writes Player/Animation and Enemies/Animation. Original art stays read-only.
Run inside Unreal editor Python, outside PIE.
"""
import json
from pathlib import Path
import unreal as u

ROOT = '/Game/Unscripted/'
ASSETS = u.EditorAssetLibrary
EXT = u.AnimPoseExtensions
OPTIONS = u.AnimPoseEvaluationOptions()

def pose(clip, time):
    return EXT.get_anim_pose_at_time(clip, time, OPTIONS)

def local(p, bone):
    return EXT.get_bone_pose(p, bone, u.AnimPoseSpaces.LOCAL)

def multiply(a,b):
    return u.Quat(a.w*b.x+a.x*b.w+a.y*b.z-a.z*b.y,
                  a.w*b.y-a.x*b.z+a.y*b.w+a.z*b.x,
                  a.w*b.z+a.x*b.y-a.y*b.x+a.z*b.w,
                  a.w*b.w-a.x*b.x-a.y*b.y-a.z*b.z)

def blend(a, b, t):
    t = max(0.0, min(1.0, t))
    t = t*t*(3-2*t)
    qa, qb = a.rotation, b.rotation
    aa, bb = (qa.x,qa.y,qa.z,qa.w), (qb.x,qb.y,qb.z,qb.w)
    sign = -1 if sum(x*y for x,y in zip(aa,bb)) < 0 else 1
    q = [x*(1-t)+y*t*sign for x,y in zip(aa,bb)]
    norm = sum(x*x for x in q)**0.5
    return (a.translation*(1-t)+b.translation*t, u.Quat(*(x/norm for x in q)), a.scale3d*(1-t)+b.scale3d*t)

def bake(source, idle, destination, seconds, contact=None, source_contact=None, source_end=None, hold=False):
    bones = list(u.AnimationLibrary.get_animation_track_names(idle))
    assert set(map(str,bones)) == set(map(str,u.AnimationLibrary.get_animation_track_names(source)))
    # Duplicate the target's idle: preserves the target skeleton and proportions.
    target = u.load_asset(destination) if ASSETS.does_asset_exist(destination) else ASSETS.duplicate_loaded_asset(idle,destination)
    assert target.get_editor_property('skeleton') == idle.get_editor_property('skeleton')
    neutral = pose(idle,0)
    source_idle = u.load_asset(ROOT+'Art/Characters/SK_Agent/Anims/A_SK_Agent_Idle')
    reference = pose(source_idle,0)
    frames = round(seconds*30)
    source_end = source_end or source.get_play_length()
    poses=[]
    for i in range(frames+1):
        t=i/frames
        if contact:
            sample = source_contact*t/contact if t<=contact else source_contact+(source_end-source_contact)*(t-contact)/(1-contact)
        else: sample=source_end*t
        poses.append(pose(source,sample))
    controller=target.get_editor_property('controller')
    controller.open_bracket('Polish action contact and recovery')
    try:
        controller.set_frame_rate(u.FrameRate(numerator=30,denominator=1))
        controller.set_number_of_frames(u.FrameNumber(value=frames))
        for bone in bones:
            base=local(neutral,bone)
            ref=local(reference,bone)
            samples=[]
            for i,p in enumerate(poses):
                t=i/frames
                action=local(p,bone)
                if source.get_editor_property('skeleton') != idle.get_editor_property('skeleton'):
                    # Same named hierarchy; retain target bone lengths. Root/hips
                    # keep the source motion delta, scaled to target stature.
                    ratio=base.translation.length()/max(ref.translation.length(),0.001)
                    action.translation=base.translation+(action.translation-ref.translation)*ratio
                    q=ref.rotation
                    action.rotation=multiply(base.rotation,multiply(u.Quat(-q.x,-q.y,-q.z,q.w),action.rotation))
                edge=min(1.0,t/0.10) if hold else min(1.0,t/0.10,(1-t)/0.18)
                samples.append(blend(base,action,edge))
            positions,rotations,scales=map(list,zip(*samples))
            assert controller.set_bone_track_keys(bone,positions,rotations,scales)
    finally: controller.close_bracket()
    assert ASSETS.save_loaded_asset(target,False)
    return target

def main():
    base=ROOT+'Art/Characters/SK_Agent/Anims/A_SK_Agent_'
    idle=u.load_asset(base+'Idle')
    report=[]
    for action,seconds,contact,source_contact,end in (
        ('Attack1',0.6,0.5,20/30,1.5),
        ('Attack2',0.75,0.4,25/30,65/30),
        ('Dodge',0.6,None,None,None),('Parry',0.6,None,None,None),
        ('Hit',0.6,None,None,None)):
        clip=bake(u.load_asset(base+action),idle,ROOT+'Player/Animation/Polish/A_Agent_'+action,seconds,contact,source_contact,end,action=='Death')
        report.append(clip.get_path_name())
    for who in ('Pursuer_A','Pursuer_B','Interventor','Supervisor'):
        idle=u.load_asset(ROOT+'Art/Characters/SK_'+who+'/Anims/A_SK_'+who+'_Idle')
        clip=bake(u.load_asset(base+'Attack1'),idle,ROOT+'Enemies/Animation/Polish/A_'+who+'_Attack',1.0,0.6,20/30,1.5)
        report.append(clip.get_path_name())
    # Death has its own grounded trajectory/contact pass. A generic rebake would
    # reintroduce the imported offset and launch into every future animation rebuild.
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from a_build_death_motion import main as build_deaths
    build_deaths()
    Path(u.Paths.project_saved_dir(),'animation_polish_assets.json').write_text(json.dumps(report,indent=2))
    print('ANIMATION_POLISH_ASSETS_OK')

if __name__=='__main__': main()
