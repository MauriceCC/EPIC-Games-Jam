"""Move the Plaza's original waypoint pattern to its relocated route actor."""
import unreal as u


def fix_plaza_patrol():
    worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    world = worlds.get_editor_world()
    assert not worlds.get_game_world(), 'Stop PIE before applying the Plaza route fix.'
    assert world.get_name() == 'L_Whitechapel', 'Open the persistent L_Whitechapel map.'

    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    ai_package = '/Game/Unscripted/Maps/L_Whitechapel_AI'
    routes = [
        actor for actor in actors
        if actor.get_class().get_name() == 'BP_PatrolRoute_C'
        and actor.get_actor_label() == 'BP_PatrolRoute'
        and actor.get_outermost().get_path_name() == ai_package
    ]
    assert len(routes) == 1, f'Expected one Plaza route in {ai_package}, found {len(routes)}'
    route = routes[0]
    guards = [
        actor for actor in actors
        if actor.get_class().get_name() == 'BP_Pursuer_C'
        and actor.get_editor_property('PatrolRoute') == route
    ]
    assert len(guards) == 2, 'Expected both Plaza Pursuers to use this route.'

    origin = route.get_actor_location()
    assert abs(origin.x - 1500) < 50 and abs(origin.y - 2000) < 50, 'Plaza route moved.'
    original = [(-300, 150, 0), (300, 150, 0), (0, -300, 0)]
    current = [(point.x, point.y, point.z) for point in route.get_editor_property('Waypoints')]
    relocated = [(origin.x + x, origin.y + y, z) for x, y, z in original]
    nav = u.NavigationSystemV1
    points = []
    for x, y, z in relocated:
        projected = nav.project_point_to_navigation(
            world, u.Vector(x, y, z), None, None, u.Vector(70, 70, 150))
        assert projected is not None, f'No NavMesh near Plaza waypoint {(x, y, z)}'
        points.append(projected)

    if current == [(point.x, point.y, point.z) for point in points]:
        u.log('B_PLAZA_PATROL route already corrected')
        return
    assert current == original, f'Unexpected Plaza waypoints: {current}'

    starts = [guard.get_actor_location() for guard in guards]
    legs = list(zip(points, points[1:] + points[:1]))
    legs.extend((start, points[0]) for start in starts)
    for start, end in legs:
        path = nav.find_path_to_location_synchronously(world, start, end, guards[0], None)
        assert path and path.is_valid() and not path.is_partial(), f'Incomplete Plaza path {start} → {end}'

    with u.ScopedEditorTransaction('Correct Plaza patrol waypoints'):
        route.modify()
        route.set_editor_property('Waypoints', points)
    assert u.EditorLoadingAndSavingUtils.save_packages([route.get_outermost()], False), 'Could not save AI sublevel.'
    u.log(f'B_PLAZA_PATROL saved {ai_package}: {points}')


fix_plaza_patrol()
