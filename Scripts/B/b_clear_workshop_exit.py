"""Persist the nonblocking profile on the Workshop downpipe and rebuild navigation."""
import unreal as u
worlds=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not worlds.get_game_world()
world=worlds.get_editor_world()
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
pipe=next(a for a in actors if a.get_actor_label()=='FA_XPipe_01')
mesh=pipe.get_component_by_class(u.StaticMeshComponent)
pipe.modify()
mesh.modify()
mesh.set_collision_profile_name('NoCollision')
mesh.set_editor_property('bCanEverAffectNavigation',False)
assert mesh.get_collision_enabled()==u.CollisionEnabled.NO_COLLISION
assert str(mesh.get_collision_profile_name())=='NoCollision'
assert u.EditorLoadingAndSavingUtils.save_packages([pipe.get_outermost()],False)
u.SystemLibrary.execute_console_command(world,'RebuildNavigation')
elapsed=0
def check(dt):
    global elapsed
    elapsed+=dt
    if elapsed<1.5 or (elapsed<30 and u.NavigationSystemV1.is_navigation_being_built_or_locked(world)):return
    u.unregister_slate_post_tick_callback(handle)
    nav=u.NavigationSystemV1
    start=nav.project_point_to_navigation(world,u.Vector(2800,4800,0),None,None,u.Vector(65,65,175))
    end=nav.project_point_to_navigation(world,u.Vector(2800,4200,0),None,None,u.Vector(65,65,175))
    assert start is not None and end is not None
    path=nav.find_path_to_location_synchronously(world,start,end)
    assert path and path.is_valid() and not path.is_partial()
    assert u.EditorLoadingAndSavingUtils.save_packages([world.get_outermost()],False)
    print('B_PORTAL_PERSIST saved NoCollision profile and rebuilt Recast')
handle=u.register_slate_post_tick_callback(check)
