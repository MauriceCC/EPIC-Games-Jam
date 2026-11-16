"""Reload/compile assets and validate skeleton, timing and recovery boundaries."""
import json
import sys
from pathlib import Path
import unreal as u
repo=Path(u.Paths.project_dir()).resolve().parent
sys.path.insert(0,str(Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python'))
from toolset_registry.helpers import compile_blueprint
checks=[]
def check(name,value):
    checks.append({'name':name,'passed':bool(value)})
    assert value,name
root='/Game/Unscripted/'
for name in ('Player/BP_PlayerCharacter','Enemies/BP_GuardBase','Enemies/BP_Pursuer','Enemies/BP_Interventor','Enemies/BP_Supervisor'):
    bp=u.load_asset(root+name)
    compile_blueprint(bp,warnings_as_errors=True)
    check(name+' compiles without warnings',True)
for folder,who,actions in [('Player','Agent',('Attack1','Attack2','Dodge','Parry','Hit','Death'))]+[('Enemies',who,('Attack',)) for who in ('Pursuer_A','Pursuer_B','Interventor','Supervisor')]:
    idle=u.load_asset(root+'Art/Characters/SK_'+who+'/Anims/A_SK_'+who+'_Idle')
    for action in actions:
        clip=u.load_asset(root+folder+'/Animation/Polish/A_'+who+'_'+action)
        check(who+' '+action+' skeleton',clip.get_editor_property('skeleton')==idle.get_editor_property('skeleton'))
        p=u.AnimPoseExtensions.get_anim_pose_at_time(clip,clip.get_play_length(),u.AnimPoseEvaluationOptions())
        neutral=u.AnimPoseExtensions.get_anim_pose_at_time(idle,0,u.AnimPoseEvaluationOptions())
        if action!='Death':
            for bone in ('hips','lefthand','righthand'):
                a=u.AnimPoseExtensions.get_bone_pose(p,bone,u.AnimPoseSpaces.WORLD).translation
                b=u.AnimPoseExtensions.get_bone_pose(neutral,bone,u.AnimPoseSpaces.WORLD).translation
                check(who+' '+action+' recovers '+bone,(a-b).length()<0.1)
player=u.load_asset(root+'Player/BP_PlayerCharacter')
cdo=u.get_default_object(player.generated_class())
for action in ('Attack1','Attack2','Dodge','Parry','Hit','Death'):
    check('Player uses polished '+action,'/Player/Animation/Polish/' in cdo.get_editor_property('Anim'+action).get_path_name())
(repo/'Scripts/A/animation_polish_validation.json').write_text(json.dumps({'passed':True,'checks':checks},indent=2),encoding='utf-8')
print('ANIMATION_POLISH_VALIDATED',len(checks))
