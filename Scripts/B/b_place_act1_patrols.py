"""Place two additional Act I patrols in their AI sublevel on connected paths."""
import unreal as u

worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
nav = u.NavigationSystemV1
world = worlds.get_editor_world()
package = '/Game/Unscripted/Maps/L_Whitechapel_AI'
root = '/Game/Unscripted/Enemies/'
assert not worlds.get_game_world() and world.get_name() == 'L_Whitechapel'
assert not nav.is_navigation_being_built_or_locked(world)
placed = {actor.get_actor_label(): actor for actor in actors.get_all_level_actors()
          if actor.get_outermost().get_path_name() == package}
guard_class = u.load_class(None, root + 'BP_Pursuer.BP_Pursuer_C')
route_class = u.load_class(None, root + 'BP_PatrolRoute.BP_PatrolRoute_C')
capsule = u.get_default_object(guard_class).get_editor_property('capsule_component')


def project(x, y):
    point = nav.project_point_to_navigation(world, u.Vector(x, y, 0), None, None, u.Vector(145, 145, 250))
    assert point is not None, (x, y)
    return point


# The blockout maps plan coordinates (u, v) to Unreal (X=v, Y=u).
plans = {
    'Alley': [(1565, 3000), (1565, 4375), (1665, 3750)],
    'Yard': [(1075, 4875), (1075, 5500), (1075, 5250)],
}
circuits = {}
for label, coordinates in plans.items():
    points = [project(x, y) for x, y in coordinates]
    for start, end in zip(points, points[1:] + points[:1]):
        path = nav.find_path_to_location_synchronously(world, start, end, placed['BP_Pursuer'])
        assert path and path.is_valid() and not path.is_partial(), (label, start, end)
    circuits[label] = points


def actor(label, cls, location):
    existing = placed.get(label)
    if existing:
        existing.modify()
        existing.set_actor_location(location, False, True)
        return existing
    new = actors.spawn_actor_from_class(cls, location, u.Rotator())
    assert new and new.get_outermost().get_path_name() == package
    new.set_actor_label(label)
    return new


assert levels.set_current_level_by_name('L_Whitechapel_AI')
with u.ScopedEditorTransaction('Place Act I patrols'):
    for label, points in circuits.items():
        location = points[-1] + u.Vector(0, 0, capsule.get_scaled_capsule_half_height())
        guard = actor(f'B_{label}_Pursuer', guard_class, location)
        route = actor(f'B_{label}_Route', route_class, points[-1])
        route.set_editor_property('Waypoints', points)
        guard.set_editor_property('PatrolRoute', route)
        guard.set_editor_property('VisionRange', 750.0)
        guard.set_editor_property('SightHalfAngle', 70.0)
        u.log(f'B_ACT1 {label}: {points}')
assert u.EditorLoadingAndSavingUtils.save_packages([guard.get_outermost()], False)
