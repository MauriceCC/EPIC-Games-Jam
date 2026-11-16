"""Disposable PIE checks for A/B death and checkpoint interruption; saves no map.

Launch full editor on L_Test_B with -ExecCmds="py <absolute script path>".
"""
import json
import time
import traceback
from pathlib import Path
import unreal as u

ROOT = '/Game/Unscripted/'
worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
level = u.get_editor_subsystem(u.LevelEditorSubsystem)
loco_cls = u.load_asset(ROOT+'Art/Characters/Shared/BP_LocomotionAnim').generated_class()
report = Path(u.Paths.project_dir()).resolve().parent/'Scripts/A/death_runtime_validation.json'
state = {'started':time.monotonic(),'actors':{},'checks':[],'stage':0}
cases = [('Pursuer','Pursuer_A','idle'), ('Pursuer','Pursuer_B','idle'),
         ('Interventor','Interventor','attack'), ('Supervisor','Supervisor','freeze'),
         ('Pursuer','Pursuer_A','stun'), ('Player','Agent','death'), ('Player','Agent','restore')]


def check(name, value):
    state['checks'].append({'name':name,'passed':bool(value)})
    assert value, name


def finish(error=None):
    report.write_text(json.dumps({'passed':error is None,'error':error,'checks':state['checks']},indent=2))
    u.unregister_slate_post_tick_callback(handle)
    level.editor_request_end_play()
    u.SystemLibrary.quit_editor()


def tick(dt):
    try:
        if time.monotonic()-state['started']>90:
            finish('PIE timeout'); return
        world = worlds.get_game_world()
        if not world: return
        now = u.GameplayStatics.get_time_seconds(world)
        if not state['actors']:
            all_actors = u.GameplayStatics.get_all_actors_of_class(world,u.Character)
            for i,(kind,who,action) in enumerate(cases):
                a = next(a for a in all_actors if a.actor_has_tag('DeathTest_'+str(i)))
                a.set_actor_tick_enabled(False)
                a.get_editor_property('character_movement').disable_movement()
                mesh = a.get_editor_property('mesh')
                mesh.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
                if kind!='Player':
                    mesh.set_skeletal_mesh_asset(u.load_asset(ROOT+'Art/Characters/SK_'+who+'/SK_'+who))
                    a.set_editor_property('B_StoryGate',0)
                state['actors'][i]=a
            state['phase_start']=now
            return
        elapsed = now-state['phase_start']
        if state['stage']==0 and elapsed>.2:
            for i,(kind,who,action) in enumerate(cases):
                a = state['actors'][i]
                if kind=='Player':
                    a.call_method('DoParry')
                    a.call_method('Die')
                    check(action+' player is marked dead', a.get_editor_property('bDead'))
                else:
                    if action=='attack': a.call_method('B_BeginParryCue')
                    if action=='freeze': a.call_method('ApplyTemporalFreeze',args=(.8,0.0))
                    if action=='stun': a.call_method('B_ApplyPostureDamage',args=(100.0,))
                    a.call_method('B_ApplyHealthDamage',args=(999,))
                    check(who+' '+action+' is defeated',a.call_method('IsDefeated'))
                mesh=a.get_editor_property('mesh')
                check(who+' '+action+' evaluates skeleton',mesh.is_component_tick_enabled())
                check(who+' '+action+' owns final pose',a.get_component_by_class(loco_cls).get_editor_property('bBusy'))
                check(who+' '+action+' uses its death clip',mesh.get_anim_instance().get_animation_asset().get_name()=='A_'+who+'_Death')
                state['position_'+str(i)]=a.get_actor_location()
                state['hips_'+str(i)]=mesh.get_socket_location('hips')
            state['stage']=1; state['phase_start']=now
        elif state['stage']==1 and elapsed>.35:
            a=state['actors'][5]
            before=a.get_editor_property('mesh').get_position()
            a.call_method('Die')
            check('Repeated lethal callback does not restart fall',abs(a.get_editor_property('mesh').get_position()-before)<.02)
            a=state['actors'][6]
            a.call_method('B_ResumePlayerAtCheckpoint',args=(a.get_actor_transform(),))
            check('Early checkpoint clears dead flag',not a.get_editor_property('bDead'))
            check('Early checkpoint releases held animation',not a.get_component_by_class(loco_cls).get_editor_property('bBusy'))
            state['stage']=2
        elif state['stage']==2 and elapsed>1.1:
            for i,(kind,who,action) in enumerate(cases[:5]):
                a=state['actors'][i]; mesh=a.get_editor_property('mesh')
                check(who+' '+action+' playback progressed',mesh.get_position()>1.0)
                check(who+' '+action+' bones actually collapse',mesh.get_socket_location('hips').z < state['hips_'+str(i)].z-25)
                check(who+' '+action+' holds after old timers expire',a.get_component_by_class(loco_cls).get_editor_property('bBusy'))
                check(who+' '+action+' body stays at defeat location',(a.get_actor_location()-state['position_'+str(i)]).length()<1)
            check('Player remains defeated while fall plays',state['actors'][5].get_editor_property('bDead'))
            state['stage']=3
        elif state['stage']==3 and elapsed>2.7:
            for i,(kind,who,action) in enumerate(cases[:5]):
                a=state['actors'][i];mesh=a.get_editor_property('mesh')
                check(who+' '+action+' reaches final frame',abs(mesh.get_position()-2)<.04)
                check(who+' '+action+' keeps final pose',a.get_component_by_class(loco_cls).get_editor_property('bBusy'))
                check(who+' '+action+' cannot be frozen again',not a.call_method('CanBeTemporalCutTarget'))
            a=state['actors'][6]
            check('Cancelled death cannot fire after checkpoint',not a.get_editor_property('bDead'))
            # Fixtures are above the map: Walking naturally transitions to Falling.
            check('Checkpoint restored movement',a.get_editor_property('character_movement').movement_mode!=u.MovementMode.MOVE_NONE)
            finish()
    except Exception:
        finish(traceback.format_exc())


for i,(kind,who,action) in enumerate(cases):
    path='Player/BP_PlayerCharacter' if kind=='Player' else 'Enemies/BP_'+kind
    cls=u.load_asset(ROOT+path).generated_class()
    a=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(cls,u.Vector((i+1)*1000,0,3000))
    a.set_editor_property('tags',['DeathTest_'+str(i)])
handle=u.register_slate_post_tick_callback(tick)
level.editor_request_begin_play()
