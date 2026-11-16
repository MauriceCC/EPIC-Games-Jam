"""Render five rigs at six fall times in a disposable editor scene. Saves no map."""
import time
import traceback
from pathlib import Path
import unreal as u

root='/Game/Unscripted/'
editor=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
out=Path(u.Paths.project_saved_dir()).resolve()/'DeathPreview'
out.mkdir(exist_ok=True)
actors=[]
for i,who in enumerate(('Agent','Pursuer_A','Pursuer_B','Interventor','Supervisor')):
    actor=editor.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(i*230,0,3000))
    mesh=actor.get_component_by_class(u.SkeletalMeshComponent)
    mesh.set_skeletal_mesh_asset(u.load_asset(root+'Art/Characters/SK_'+who+'/SK_'+who))
    folder='Player' if who=='Agent' else 'Enemies'
    clip=u.load_asset(root+folder+'/Animation/Polish/A_'+who+'_Death')
    mesh.override_animation_data(clip,False,False,0,1)
    actors.append((mesh,clip))
floor=editor.spawn_actor_from_class(u.StaticMeshActor,u.Vector(460,0,2989))
floor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
floor.set_actor_scale3d(u.Vector(16,8,.2))
light=editor.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,4000),u.Rotator(-50,-30,0))
light.light_component.set_intensity(5)
sky=editor.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,4000))
sky.light_component.set_intensity(1.5)
camera=editor.spawn_actor_from_class(u.CameraActor,u.Vector(1250,1400,3950))
rotation=u.MathLibrary.find_look_at_rotation(camera.get_actor_location(),u.Vector(460,0,3060))
camera.set_actor_rotation(rotation,False)
camera.camera_component.set_field_of_view(50)
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(camera.get_actor_location(),rotation)
state={'time':time.monotonic(),'started':time.monotonic(),'index':0,'pending':False,'task':None}
times=(0,.25,.60,.90,1.4,2.0)


def finish(error=None):
    (out/'result.txt').write_text(error or 'Rendered 6 samples; no assets or maps saved.')
    u.unregister_slate_post_tick_callback(handle)
    u.SystemLibrary.quit_editor()


def tick(dt):
    try:
        if time.monotonic()-state['started']>180:finish('Render timeout');return
        if state['task']:
            if not state['task'].is_task_done():return
            state['task']=None;state['index']+=1;state['pending']=False;state['time']=time.monotonic()
        if time.monotonic()-state['time']<2:return
        if state['index']>=len(times):finish();return
        if not state['pending']:
            for mesh,clip in actors:
                # SetPosition updates the live instance; OverrideAnimationData
                # forces TickAnimation/RefreshBoneTransforms in the editor.
                mesh.set_position(times[state['index']],False)
                mesh.override_animation_data(clip,False,False,times[state['index']],1)
            state['pending']=True;state['time']=time.monotonic();return
        state['task']=u.AutomationLibrary.take_high_res_screenshot(1600,900,str(out/('death_%02d.png'%state['index'])),camera=camera)
    except Exception:finish(traceback.format_exc())


handle=u.register_slate_post_tick_callback(tick)
