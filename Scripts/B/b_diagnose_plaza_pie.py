"""Log live guard state during the manual Plaza test without editing assets."""
import unreal as u
from math import cos, radians


worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
guard_class = u.load_class(None, '/Game/Unscripted/Enemies/BP_GuardBase.BP_GuardBase_C')
assert guard_class, 'BP_GuardBase could not be loaded'


def field(actor, name):
    try:
        return actor.get_editor_property(name)
    except Exception:
        return '<unavailable>'


def route_goal(guard, location, first_sample):
    route = field(guard, 'PatrolRoute')
    index = field(guard, 'CurrentWaypointIndex')
    if not isinstance(route, u.Actor) or not isinstance(index, int):
        return f'route={route} index={index}'
    points = field(route, 'Waypoints')
    if isinstance(points, str) or not points:
        return f'route={route.get_actor_label()} empty'
    if first_sample:
        u.log(f'B_PLAZA {guard.get_actor_label()} route={route.get_actor_label()} '
              f'origin={route.get_actor_location()} points={list(points)}')
    point = points[index % len(points)]
    distance = ((location.x - point.x)**2 + (location.y - point.y)**2)**0.5
    return f'waypoint={index} waypoint_distance_cm={round(distance)}'


def sample(delta):
    global elapsed, previous, saw_pie
    world = worlds.get_game_world()
    if not world:
        if saw_pie:
            u.unregister_slate_post_tick_callback(handle)
        return
    saw_pie = True
    elapsed += delta
    if elapsed < 0.25:
        return
    elapsed = 0.0
    player = u.GameplayStatics.get_player_pawn(world, 0)
    if not player:
        return
    guards = u.GameplayStatics.get_all_actors_of_class(world, guard_class)
    if previous is None:
        u.log(f'B_PLAZA pawn={player.get_class().get_name()} guards={len(guards)}')
    current = {}
    for guard in guards:
        name = guard.get_actor_label()
        location = guard.get_actor_location()
        controller = guard.get_controller()
        projected = u.NavigationSystemV1.project_point_to_navigation(
            world, location, None, None, u.Vector(60, 60, 140))
        los = controller.line_of_sight_to(player, u.Vector(), False) if controller else False
        angle = field(guard, 'SightHalfAngle')
        facing = guard.get_dot_product_to(player)
        in_cone = facing >= cos(radians(angle)) if isinstance(angle, (int, float)) else None
        stats = (
            controller.get_class().get_name() if controller else None,
            projected is not None,
            los,
            round(guard.get_distance_to(player) / 100, 1),
            field(guard, 'B_Health'),
            field(guard, 'CurrentPosture'),
            field(guard, 'bIsTemporalFrozen'),
            field(guard, 'bCanAttack'),
            field(guard, 'CurrentAIState'),
            field(guard, 'bB_Stunned'),
            round(guard.get_velocity().length()),
            in_cone,
            tuple(round(coordinate) for coordinate in (location.x, location.y, location.z)),
            route_goal(guard, location, previous is None),
        )
        current[name] = stats
        if previous is None or previous.get(name) != stats:
            u.log(f'B_PLAZA {name} controller={stats[0]} nav={stats[1]} los={stats[2]} '
                  f'distance_m={stats[3]} hp={stats[4]} posture={stats[5]} '
                  f'frozen={stats[6]} can_attack={stats[7]} state={stats[8]} '
                  f'stunned={stats[9]} speed_cm_s={stats[10]} in_cone={stats[11]} '
                  f'position={stats[12]} {stats[13]}')
    previous = current


elapsed = 0.0
previous = None
saw_pie = False
def sample_once_per_interval(delta):
    try:
        sample(delta)
    except Exception:
        u.unregister_slate_post_tick_callback(handle)
        raise


handle = u.register_slate_post_tick_callback(sample_once_per_interval)
u.log('B_PLAZA diagnostic armed for the next PIE session')
