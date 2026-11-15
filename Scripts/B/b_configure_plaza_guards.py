"""Set up one Plaza sentry, one patroller, and a wider sight cone."""
from pathlib import Path
import runpy

import unreal as u

AI_PACKAGE = '/Game/Unscripted/Maps/L_Whitechapel_AI'
SIGHT_RANGE_CM = 750.0
SIGHT_HALF_ANGLE = 70.0
# Lead with the far end so the first movement is across the Plaza.
PATROL_POINTS = ((1800, 2150), (1200, 2150))


def navigable_circuit(world, guard, coordinates):
    nav = u.NavigationSystemV1
    points = []
    for x, y in coordinates:
        point = nav.project_point_to_navigation(
            world, u.Vector(x, y, 0), None, None, u.Vector(70, 70, 150))
        assert point is not None, f'No NavMesh near Plaza waypoint {(x, y)}'
        points.append(point)
    legs = [(guard.get_actor_location(), points[0])]
    legs.extend(zip(points, points[1:] + points[:1]))
    for start, end in legs:
        path = nav.find_path_to_location_synchronously(world, start, end, guard, None)
        assert path and path.is_valid() and not path.is_partial(), f'Incomplete Plaza path {start} → {end}'
        last = path.get_editor_property('path_points')[-1]
        assert (last.x - end.x)**2 + (last.y - end.y)**2 < 75**2, f'Path stops short of {end}'
    return points


def apply():
    worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    world = worlds.get_editor_world()
    assert not worlds.get_game_world(), 'Stop PIE before changing Plaza patrol.'
    assert world.get_name() == 'L_Whitechapel', 'Open L_Whitechapel.'
    guard_base = u.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
    blueprints = u.BlueprintEditorLibrary
    for field in ('VisionRange', 'SightHalfAngle'):
        blueprints.set_blueprint_variable_instance_editable(guard_base, field, True)
    assert blueprints.compile_blueprint(guard_base), 'Could not compile BP_GuardBase.'

    actors = u.get_editor_subsystem(u.EditorActorSubsystem)
    placed = {
        actor.get_actor_label(): actor for actor in actors.get_all_level_actors()
        if actor.get_outermost().get_path_name() == AI_PACKAGE
    }
    route = placed['BP_PatrolRoute']
    patroller = placed['BP_Pursuer']
    sentry = placed['BP_Pursuer2']
    for guard in (patroller, sentry):
        assert guard.get_class().get_name() == 'BP_Pursuer_C'
    points = navigable_circuit(world, patroller, PATROL_POINTS)

    with u.ScopedEditorTransaction('Configure Plaza patroller and sentry'):
        route.modify()
        route.set_editor_property('Waypoints', points)
        for guard in (patroller, sentry):
            guard.modify()
            guard.set_editor_property('VisionRange', SIGHT_RANGE_CM)
            guard.set_editor_property('SightHalfAngle', SIGHT_HALF_ANGLE)
        patroller.set_editor_property('PatrolRoute', route)
        sentry.set_editor_property('PatrolRoute', None)
        assert sentry.set_actor_rotation(u.Rotator(yaw=135), False)

    assert u.EditorAssetLibrary.save_loaded_asset(guard_base), 'Could not save BP_GuardBase.'
    assert u.EditorLoadingAndSavingUtils.save_packages([route.get_outermost()], False)
    u.log(f'B_PLAZA_SETUP saved patroller and sentry with {SIGHT_HALF_ANGLE * 2:.0f} degree sight cones')


apply()
runpy.run_path(str(Path(__file__).with_name('b_diagnose_plaza_pie.py')), run_name='__main__')
