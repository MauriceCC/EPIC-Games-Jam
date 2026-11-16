"""[PROPUESTA] Retarget supplied uppercut and bake an in-place 1.05 s action.
Writes only Player/Animation/Uppercut; shared art/skeleton stays read-only.
"""
import json, math, sys
from pathlib import Path
import unreal as u
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from a_sample_uppercut import mul,inv,rotate,sample
from a_polish_animation_assets import blend

ROOT='/Game/Unscripted/'
DEST=ROOT+'Player/Animation/Uppercut/A_Agent_HeavyUppercut'
DURATION=1.066666667
CONTACT=0.466666667
SOURCE_START=0.65
SOURCE_CONTACT=34/30
SOURCE_END=1.9

def main():
    data=sample()
    idle=u.load_asset(ROOT+'Art/Characters/SK_Agent/Anims/A_SK_Agent_Idle')
    ext=u.AnimPoseExtensions;local=u.AnimPoseSpaces.LOCAL;world=u.AnimPoseSpaces.WORLD
    neutral=ext.get_anim_pose_at_time(idle,0,u.AnimPoseEvaluationOptions())
    bones=list(map(str,u.AnimationLibrary.get_animation_track_names(idle)))
    mapping={n.lower():n for n in data['bones']}
    mapping.update(spine02='Spine',spine01='Spine1',spine='Spine2',head_end='HeadTop_End')
    refs={b:ext.get_ref_bone_pose(neutral,b,world) for b in bones}
    restlocal={b:ext.get_ref_bone_pose(neutral,b,local) for b in bones}
    def qtuple(q):return (q.x,q.y,q.z,q.w)
    # Align anatomical left/right axes, independent of the mesh import yaw.
    side=refs['lefthand'].translation-refs['righthand'].translation
    srcside=[a-b for a,b in zip(data['bones']['LeftHand']['rest']['p'],data['bones']['RightHand']['rest']['p'])]
    yaw=math.atan2(side.y,side.x)-math.atan2(srcside[1],srcside[0])
    align=(0,0,math.sin(yaw/2),math.cos(yaw/2))
    target=u.load_asset(DEST) if u.EditorAssetLibrary.does_asset_exist(DEST) else u.EditorAssetLibrary.duplicate_loaded_asset(idle,DEST)
    parents={}
    for b in bones:
        path=[str(n).lower() for n in u.AnimationLibrary.find_bone_path_to_root(idle,b)]
        parents[b]=path[1] if path and path[0]==b and len(path)>1 else (path[-2] if path and path[-1]==b and len(path)>1 else None)
    frames=32;tracks={b:[] for b in bones};stats=[]
    for i in range(frames+1):
        seconds=i/30
        t=SOURCE_START+(SOURCE_CONTACT-SOURCE_START)*seconds/CONTACT if seconds<=CONTACT else SOURCE_CONTACT+(SOURCE_END-SOURCE_CONTACT)*(seconds-CONTACT)/(DURATION-CONTACT)
        fi=t*30;lo=min(int(fi),len(data['frames'])-1);hi=min(lo+1,len(data['frames'])-1);alpha=fi-lo
        globalq={};sourced={}
        for b in bones:
            source=mapping.get(b)
            if source is None:continue
            qa=data['frames'][lo][source]['q'];qb=data['frames'][hi][source]['q']
            sign=-1 if sum(a*c for a,c in zip(qa,qb))<0 else 1
            q=[a*(1-alpha)+c*alpha*sign for a,c in zip(qa,qb)];length=math.sqrt(sum(v*v for v in q));q=[v/length for v in q]
            delta=mul(mul(align,mul(q,inv(data['bones'][source]['rest']['q']))),inv(align))
            globalq[b]=mul(delta,qtuple(refs[b].rotation))
        for b in bones:
            base=ext.get_bone_pose(neutral,b,local);action=u.Transform()
            action.translation=restlocal[b].translation;action.rotation=restlocal[b].rotation;action.scale3d=restlocal[b].scale3d
            parent=parents[b]
            if b in globalq:
                parentq=globalq.get(parent,qtuple(refs[parent].rotation) if parent else (0,0,0,1))
                action.rotation=u.Quat(*mul(inv(parentq),globalq[b]))
            if b=='hips':
                source=data['frames'][lo]['Hips']['p'];rest=data['bones']['Hips']['rest']['p']
                dz=(source[2]-rest[2])*refs['hips'].translation.z/max(rest[2],0.01)
                # Translate vertically in component space; no forward root drift.
                parentq=qtuple(refs[parent].rotation) if parent else (0,0,0,1)
                delta=rotate(inv(parentq),(0,0,dz))
                action.translation=restlocal[b].translation+u.Vector(*delta)
            edge=min(1.0,seconds/0.12,(DURATION-seconds)/0.22)
            tracks[b].append(blend(base,action,edge))
    c=target.get_editor_property('controller');c.open_bracket('Retarget Surprise Uppercut to agent')
    try:
        c.set_frame_rate(u.FrameRate(numerator=30,denominator=1));c.set_number_of_frames(u.FrameNumber(value=frames))
        for b,values in tracks.items():
            p,q,s=map(list,zip(*values));assert c.set_bone_track_keys(b,p,q,s)
    finally:c.close_bracket()
    target.set_editor_property('enable_root_motion',False)
    assert u.EditorAssetLibrary.save_loaded_asset(target,False)
    report={'asset':DEST,'source_sha256':data['sha256'],'duration':target.get_play_length(),'contact':CONTACT,'source_interval':[SOURCE_START,SOURCE_CONTACT,SOURCE_END],'align_yaw_degrees':math.degrees(yaw),'parents':parents,'poses':{}}
    for label,time in [('idle',0),('windup',0.3),('contact',CONTACT),('followthrough',0.6),('end',DURATION)]:
        p=ext.get_anim_pose_at_time(target,time,u.AnimPoseEvaluationOptions())
        report['poses'][label]={b:list(ext.get_bone_pose(p,b,world).translation.to_tuple()) for b in bones}
    (HERE/'uppercut_bake.json').write_text(json.dumps(report,indent=2))
    print('UPPERCUT_BAKED',DEST)

if __name__=='__main__':main()
