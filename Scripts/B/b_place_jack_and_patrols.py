"""Place Jack in the Workshop and set two independently navigable Plaza patrols."""
import unreal as u

levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
nav = u.NavigationSystemV1
package = '/Game/Unscripted/Maps/L_Whitechapel_AI'
world = worlds.get_editor_world()
assert not worlds.get_game_world() and world.get_name() == 'L_Whitechapel'
assert not nav.is_navigation_being_built_or_locked(world), 'Wait for navigation generation.'
placed = {actor.get_actor_label(): actor for actor in actors.get_all_level_actors()
          if actor.get_outermost().get_path_name() == package}


def on_mesh(x, y):
    point = nav.project_point_to_navigation(world, u.Vector(x, y, 0), None, None, u.Vector(100, 100, 250))
    assert point is not None, (x, y)
    return point


def circuit(guard, coordinates):
    points = [on_mesh(x, y) for x, y in coordinates]
    legs = [(guard.get_actor_location(), points[0]), *zip(points, points[1:] + points[:1])]
    for start, end in legs:
        path = nav.find_path_to_location_synchronously(world, start, end, guard)
        assert path and path.is_valid() and not path.is_partial(), (start, end)
    return points


guards = [placed['BP_Pursuer'], placed['BP_Pursuer2']]
routes = [placed['BP_PatrolRoute'], placed['B_Plaza_East_Route']]
circuits = [
    circuit(guards[0], [(1750, 2140), (1300, 2040), (1120, 2180)]),
    circuit(guards[1], [(1940, 1590), (1680, 1420), (2040, 1150)]),
]
jack = placed.get('B_Jack_Workshop')
jack_class = u.load_class(None, '/Game/Unscripted/Enemies/Jack/BP_Jack.BP_Jack_C')
assert jack_class
jack_spot = on_mesh(3050, 5450)
capsule = u.get_default_object(jack_class).get_editor_property('capsule_component')
jack_spot.z += capsule.get_scaled_capsule_half_height()
assert levels.set_current_level_by_name('L_Whitechapel_AI')

with u.ScopedEditorTransaction('Place Jack and adjust Whitechapel patrols'):
    for guard, route, points in zip(guards, routes, circuits):
        route.modify()
        route.set_editor_property('Waypoints', points)
        guard.modify()
        guard.set_editor_property('PatrolRoute', route)
        u.log(f'B_WHITECHAPEL {guard.get_actor_label()} waypoints={points}')
    if not jack:
        jack = actors.spawn_actor_from_class(jack_class, jack_spot, u.Rotator(yaw=180))
        assert jack and jack.get_outermost().get_path_name() == package
        jack.set_actor_label('B_Jack_Workshop')
    else:
        jack.modify()
        assert jack.set_actor_location(jack_spot, False, False)
        assert jack.set_actor_rotation(u.Rotator(yaw=180), False)

assert u.EditorLoadingAndSavingUtils.save_packages([jack.get_outermost()], False)
u.log(f'B_WHITECHAPEL Jack at {jack.get_actor_location()}')
