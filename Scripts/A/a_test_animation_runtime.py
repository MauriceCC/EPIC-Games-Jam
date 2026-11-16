"""Disposable PIE checks. Launch full editor on L_Test_B; never saves a map."""
import json
import time
import traceback
from pathlib import Path
import unreal as u

root='/Game/Unscripted/'
worlds=u.get_editor_subsystem(u.UnrealEditorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
loco_cls=u.load_asset(root+'Art/Characters/Shared/BP_LocomotionAnim').generated_class()
state={'started':time.monotonic(),'phase':-1,'checks':[],'actors':{}}
cases=[('Pursuer','normal'),('Interventor','normal'),('Supervisor','normal'),('Pursuer','freeze'),('Pursuer','stun'),('Player','DoLightAttack'),('Player','DoLightAttack'),('Player','DoDodge'),('Player','DoParry'),('Player','death')]
out=Path(u.Paths.project_dir()).resolve().parent/'Scripts/A/animation_runtime_validation.json'

def check(name,value):
    state['checks'].append({'name':name,'passed':bool(value)})
    assert value,name

def finish(error=None):
    out.write_text(json.dumps({'passed':error is None,'error':error,'checks':state['checks']},indent=2))
    u.unregister_slate_post_tick_callback(handle)
    level.editor_request_end_play()
    u.SystemLibrary.quit_editor()

def spawn(world,name,index):
    path='Player/BP_PlayerCharacter' if name=='Player' else 'Enemies/BP_'+name
    cls=u.load_asset(root+path).generated_class()
    actor=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,cls) if a.actor_has_tag('AnimationTest_'+name))
    actor.set_actor_tick_enabled(False)
    actor.get_editor_property('character_movement').disable_movement()
    mesh=actor.get_editor_property('mesh')
    mesh.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    return actor

def tick(dt):
    try:
        world=worlds.get_game_world()
        if not world:
            if time.monotonic()-state['started']>90:finish('PIE startup timeout')
            return
        if not state['actors']:
            for i,name in enumerate(('Pursuer','Interventor','Supervisor','Player')):state['actors'][name]=spawn(world,name,i+1)
            state['phase_start']=u.GameplayStatics.get_time_seconds(world)
            state['phase']=-1
        now=u.GameplayStatics.get_time_seconds(world)
        if state['phase']==-1 or now-state['phase_start']>2.2:
            if state['phase']>=0:
                name,action=cases[state['phase']]
                a=state['actors'][name]
                busy=a.get_component_by_class(loco_cls).get_editor_property('bBusy')
                check(name+' '+action+' completion',bool(busy)==(action=='death'))
            state['phase']+=1
            if state['phase']>=len(cases):finish();return
            state['phase_start']=now
            state['interrupted']=False
            name,action=cases[state['phase']]
            a=state['actors'][name]
            if name=='Player':
                if action=='death':
                    a.call_method('DoParry')
                    a.call_method('Die')
                else:a.call_method(action)
            else:
                a.call_method('B_BeginParryCue')
            check(name+' '+action+' takes animation ownership',a.get_component_by_class(loco_cls).get_editor_property('bBusy'))
            clip=a.get_editor_property('mesh').get_anim_instance().get_animation_asset()
            check(name+' '+action+' uses polished clip','/Animation/Polish/' in clip.get_path_name())
        name,action=cases[state['phase']]
        a=state['actors'][name]
        elapsed=now-state['phase_start']
        if elapsed>0.2 and not state['interrupted'] and action in ('freeze','stun'):
            state['interrupted']=True
            if action=='freeze':
                a.call_method('ApplyTemporalFreeze',args=(0.8,0.0))
            else:
                a.call_method('B_ApplyPostureDamage',args=(100.0,))
                a.call_method('B_CheckAttackVisual')
                check('Stun releases attack ownership',not a.get_component_by_class(loco_cls).get_editor_property('bBusy'))
    except Exception:finish(traceback.format_exc())

for i,name in enumerate(('Pursuer','Interventor','Supervisor','Player')):
    path='Player/BP_PlayerCharacter' if name=='Player' else 'Enemies/BP_'+name
    cls=u.load_asset(root+path).generated_class()
    actor=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(cls,u.Vector((i+1)*1000,0,3000))
    actor.set_editor_property('tags',['AnimationTest_'+name])
handle=u.register_slate_post_tick_callback(tick)
level.editor_request_begin_play()
