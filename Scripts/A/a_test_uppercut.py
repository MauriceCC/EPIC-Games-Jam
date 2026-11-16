"""Disposable PIE validation on L_Test_A; never saves a map or enemy asset."""
import json,sys,time,traceback
from pathlib import Path
import unreal as u
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python')]
from toolset_registry.helpers import compile_blueprint
from a_build_uppercut import DEST,DURATION,CONTACT
ROOT='/Game/Unscripted/'
worlds=u.get_editor_subsystem(u.UnrealEditorSubsystem);level=u.get_editor_subsystem(u.LevelEditorSubsystem)
state={'checks':[],'start':time.monotonic(),'phase':-1,'begun':False}
cases=['normal','insufficient','damage','blocked','retake','dodge','parry','death']
def check(name,value):
    state['checks'].append({'name':name,'passed':bool(value)})
    assert value,name
def prop(obj,key):return obj.get_editor_property(key)
def setprop(obj,key,value):obj.set_editor_property(key,value,u.PropertyAccessChangeNotifyMode.NEVER)
def finish(error=None):
    (HERE/'uppercut_validation.json').write_text(json.dumps({'passed':error is None,'error':error,'checks':state['checks'],'mode':'Full editor PIE, NullRHI; no rendered visual acceptance'},indent=2))
    if 'handle' in globals():u.unregister_slate_post_tick_callback(handle)
    level.editor_request_end_play();u.SystemLibrary.quit_editor()
def setup(world):
    actors=u.GameplayStatics.get_all_actors_of_class(world,u.Actor)
    found={str(t):a for a in actors for t in a.tags if str(t).startswith('UppercutTest_')}
    state['player']=found['UppercutTest_Player']
    state['targets']=[found['UppercutTest_'+n] for n in ('Front','Rear','Distant','Wall')]
    for a in [state['player']]+state['targets']:
        a.set_actor_tick_enabled(False);a.set_actor_enable_collision(False)
        a.character_movement.disable_movement()
        controller=a.get_controller()
        if controller:controller.stop_movement();controller.set_actor_tick_enabled(False)
    p=state['player'];state['combat']=p.get_component_by_class(u.load_asset(ROOT+'Player/BP_CombatComponent').generated_class())
    state['loco']=p.get_component_by_class(u.load_asset(ROOT+'Art/Characters/Shared/BP_LocomotionAnim').generated_class())
    state['combat'].set_component_tick_enabled(False)
    setprop(state['player'].mesh,'visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    state['ready']=True
def start_case(now):
    p=state['player'];combat=state['combat'];case=cases[state['phase']]
    p.call_method('A_CancelHeavyAttack');p.call_method('SetGameplayInputEnabled',args=(True,))
    state['baseline_health']=[prop(a,'B_Health') for a in state['targets']]
    combat.call_method('SetStamina',args=(5.0 if case=='insufficient' else 100.0,))
    p.call_method('DoHeavyAttack');p.set_actor_rotation(u.Rotator(0,0,0),False)
    state.setdefault('diagnostics',[]).append({'case':case,'current':prop(combat,'CurrentStamina'),'cost':prop(combat,'HeavyAttackStaminaCost'),'combat':combat.get_path_name(),'member':str(prop(p,'BP_CombatComponent'))})
    Path(u.Paths.project_saved_dir(),'uppercut_runtime_diagnostics.json').write_text(json.dumps(state['diagnostics'],indent=2))
    if case=='insufficient':
        check('Insufficient stamina rejects heavy',not prop(p,'bA_HeavyActive'))
        check('Rejected heavy spends no stamina',abs(prop(combat,'CurrentStamina')-5)<0.01)
    else:
        check(case+' starts heavy',prop(p,'bA_HeavyActive'))
        check(case+' spends 25 stamina',abs(prop(combat,'CurrentStamina')-75)<0.01)
        check(case+' owns animation',prop(state['loco'],'bBusy'))
        check(case+' plays supplied uppercut',p.mesh.get_anim_instance().get_animation_asset().get_path_name().split('.')[0]==DEST)
        p.call_method('DoHeavyAttack')
        check(case+' repeated input does not spend twice',abs(prop(combat,'CurrentStamina')-75)<0.01)
    state.update(case_start=now,interrupted=False,hit_checked=False)
def tick(dt):
    try:
        world=worlds.get_game_world()
        if not world:
            if time.monotonic()-state['start']>90:finish('PIE startup timeout')
            return
        now=u.GameplayStatics.get_time_seconds(world)
        if not state.get('ready'):setup(world)
        if state['phase']==-1:
            state['phase']=0;start_case(now);return
        case=cases[state['phase']];p=state['player'];elapsed=now-state['case_start']
        if elapsed>0.18 and not state['interrupted']:
            state['interrupted']=True
            check(case+' no damage during windup',all(abs(prop(a,'B_Health')-hp)<0.01 for a,hp in zip(state['targets'],state['baseline_health'])))
            if case=='damage':p.call_method('TakeHit',args=(1.0,))
            elif case=='blocked':p.call_method('SetGameplayInputEnabled',args=(False,))
            elif case=='retake':
                setprop(p,'PosHistory',[p.get_actor_location()]);setprop(p,'HPHistory',[100.0]);setprop(p,'StaminaHistory',[100.0])
                p.call_method('DoRetake')
            elif case=='death':p.call_method('Die')
            elif case=='dodge':p.call_method('DoDodge')
            elif case=='parry':p.call_method('DoParry')
            if case in ('damage','blocked','retake','dodge','parry','death'):
                check(case+' cancels active heavy',not prop(p,'bA_HeavyActive'))
                check(case+' clears pending hit',not prop(p,'bA_HeavyHitPending'))
        if elapsed>0.62 and not state['hit_checked']:
            state['hit_checked']=True
            expected=state['baseline_health'][0]-(28 if case=='normal' else 0)
            state['diagnostics'][-1].update(health=[prop(a,'B_Health') for a in state['targets']],position=list(p.get_actor_location().to_tuple()),forward=list(p.get_actor_forward_vector().to_tuple()),target_positions=[list(a.get_actor_location().to_tuple()) for a in state['targets']],pending=prop(p,'bA_HeavyHitPending'),active=prop(p,'bA_HeavyActive'))
            Path(u.Paths.project_saved_dir(),'uppercut_runtime_diagnostics.json').write_text(json.dumps(state['diagnostics'],indent=2))
            check(case+' front target damage',abs(prop(state['targets'][0],'B_Health')-expected)<0.01)
            check(case+' rear target untouched',abs(prop(state['targets'][1],'B_Health')-state['baseline_health'][1])<0.01)
            check(case+' distant target untouched',abs(prop(state['targets'][2],'B_Health')-state['baseline_health'][2])<0.01)
            check(case+' wall blocks hit',abs(prop(state['targets'][3],'B_Health')-state['baseline_health'][3])<0.01)
            p.call_method('A_HeavyHit');p.call_method('A_HeavyHit')
            check(case+' cannot apply damage twice',abs(prop(state['targets'][0],'B_Health')-expected)<0.01)
        if elapsed>1.25:
            check(case+' attack lock released',not prop(p,'bAttacking'))
            if case=='normal':check('Normal recovery releases locomotion',not prop(state['loco'],'bBusy'))
            state['phase']+=1
            if state['phase']>=len(cases):finish();return
            start_case(now)
    except Exception:finish(traceback.format_exc())

try:
    for name in ('BP_PlayerCharacter','BP_PlayerController'):
        compile_blueprint(u.load_asset(ROOT+'Player/'+name),warnings_as_errors=True)
        check(name+' compiles without warnings',True)
    clip=u.load_asset(DEST);idle=u.load_asset(ROOT+'Art/Characters/SK_Agent/Anims/A_SK_Agent_Idle')
    check('Uppercut uses agent skeleton',prop(clip,'skeleton')==prop(idle,'skeleton'))
    check('Uppercut length matches lock',abs(clip.get_play_length()-DURATION)<0.001)
    check('Uppercut does not move gameplay root',not prop(clip,'enable_root_motion'))
    ext=u.AnimPoseExtensions;options=u.AnimPoseEvaluationOptions()
    a=ext.get_anim_pose_at_time(clip,clip.get_play_length(),options);b=ext.get_anim_pose_at_time(idle,0,options)
    for bone in ('hips','lefthand','righthand','leftfoot','rightfoot'):
        delta=ext.get_bone_pose(a,bone,u.AnimPoseSpaces.WORLD).translation-ext.get_bone_pose(b,bone,u.AnimPoseSpaces.WORLD).translation
        check('Recovery returns '+bone+' to idle',delta.length()<0.1)
    # Only in memory, never saved: permit seeding personal Retake history.
    player_bp=u.load_asset(ROOT+'Player/BP_PlayerCharacter')
    for name in ('PosHistory','HPHistory','StaminaHistory'):
        u.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(player_bp,name,True)
    compile_blueprint(player_bp,warnings_as_errors=True)
    for name,path,x in [('Player','Player/BP_PlayerCharacter',0),('Front','Enemies/BP_Pursuer',100),('Rear','Enemies/BP_Pursuer',-100),('Distant','Enemies/BP_Pursuer',400),('Wall','Enemies/BP_Pursuer',100)]:
        actor=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(u.load_asset(ROOT+path).generated_class(),u.Vector(10000+x,10000,3000))
        if name=='Wall':actor.set_actor_location(u.Vector(10100,10070,3000),False,False)
        setprop(actor,'tags',['UppercutTest_'+name])
    wall=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(u.StaticMeshActor,u.Vector(10050,10035,3000))
    wall.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
    wall.set_actor_scale3d(u.Vector(0.2,0.2,2.0))
    handle=u.register_slate_post_tick_callback(tick);level.editor_request_begin_play()
except Exception:finish(traceback.format_exc())
