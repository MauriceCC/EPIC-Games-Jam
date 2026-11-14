"""[PROPUESTA] Make L_Test_B playable independently of the production input."""
import unreal as u

assets = u.EditorAssetLibrary
lib = u.BlueprintEditorLibrary
root = '/Game/Unscripted/'
template = '/Game/TopDown/Blueprints/BP_TopDownGameMode'
folder = root + 'Enemies/Test'
topdown = '/Game/TopDown/Blueprints/'


def blueprint(name, parent_path):
    path = folder + '/' + name
    if assets.does_asset_exist(path):
        return u.load_asset(path)
    factory = u.BlueprintFactory()
    factory.set_editor_property('parent_class', assets.load_blueprint_class(parent_path))
    instance = u.AssetToolsHelpers.get_asset_tools().create_asset(
        name, folder, u.Blueprint, factory)
    assert instance and lib.compile_blueprint(instance), path
    return instance


pawn = blueprint('BP_TestPlayer_B', topdown + 'BP_TopDownCharacter')
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(pawn))


def call(path):
    result = graph.add_call_function_node('/Script/Engine.' + path)
    assert result, path
    return result


def link(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


def value(node, name, default):
    assert lib.find_input_pin(node, name).set_pin_value(default), name


if not any('DebugKeySpaceBar' in str(lib.get_node_title(n)) or
           'ApplyRadialDamage' in str(lib.get_node_title(n)) for n in graph.list_all_nodes()):
    # The click-to-move template supplies navigation and a gameplay camera.
    action = graph.create_node_from_name(
        'Entrada|DebugEvents|KeyboardEvents|DebugKeySpaceBar', u.Vector2D(0, 0), [])
    assert action, 'Space Bar test event'
    attack = call('GameplayStatics.ApplyRadialDamage')
    link(lib.find_output_pin(action, 'Pressed'), lib.find_execute_pin(attack))
    link(lib.find_result_pin(call('Actor.K2_GetActorLocation')), lib.find_input_pin(attack, 'Origin'))
    value(attack, 'BaseDamage', '24')
    value(attack, 'DamageRadius', '220')
    value(attack, 'bDoFullDamage', 'true')
    assert lib.compile_blueprint(pawn)
assert assets.save_loaded_asset(pawn)

mode = blueprint('BP_TestGameMode_B', template)
defaults = u.get_default_object(mode.generated_class())
defaults.set_editor_property('default_pawn_class', pawn.generated_class())
defaults.set_editor_property(
    'player_controller_class', assets.load_blueprint_class(topdown + 'BP_TopDownController'))
assert assets.save_loaded_asset(mode)

levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert levels.load_level(root + 'Maps/Test/L_Test_B')
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
settings = world.get_world_settings() if hasattr(world, 'get_world_settings') else (
    u.GameplayStatics.get_actor_of_class(world, u.WorldSettings))
assert settings, 'Missing world settings'
settings.modify()
settings.set_editor_property('default_game_mode', mode.generated_class())
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
placed = {actor.get_actor_label(): actor for actor in actors.get_all_level_actors()}
camera_label = 'Test_B_IsometricCamera'
camera_location = u.Vector(-1800, -1800, 1800)
camera_rotation = u.Rotator(pitch=-35.264, yaw=45, roll=0)
camera = placed.get(camera_label)
if camera is None:
    camera = actors.spawn_actor_from_class(u.CameraActor, camera_location, camera_rotation)
    assert camera
    camera.set_actor_label(camera_label)
assert camera.set_actor_location(camera_location, False, True)
assert camera.set_actor_rotation(camera_rotation, False)
camera.set_editor_property('auto_activate_for_player', u.AutoReceiveInput.PLAYER0)
component = camera.get_editor_property('camera_component')
component.set_editor_property('projection_mode', u.CameraProjectionMode.ORTHOGRAPHIC)
component.set_editor_property('ortho_width', 3100.0)

patrol_class = assets.load_blueprint_class(root + 'Enemies/BP_PatrolRoute')
route = placed.get('Test_B_PatrolRoute')
if route is None:
    route = actors.spawn_actor_from_class(patrol_class, u.Vector(0, 0, 50))
    assert route
    route.set_actor_label('Test_B_PatrolRoute')
route.set_editor_property('Waypoints', [
    u.Vector(-350, 0, 0), u.Vector(350, 0, 0), u.Vector(0, 350, 0),
])

pursuer_class = assets.load_blueprint_class(root + 'Enemies/BP_Pursuer')
for label, location in [
    ('Test_B_Pursuer_1', u.Vector(-200, 100, 110)),
    ('Test_B_Pursuer_2', u.Vector(200, 100, 110)),
    ('Test_B_Pursuer_3', u.Vector(-460, 450, 110)),
]:
    pursuer = placed.get(label)
    if pursuer is None:
        pursuer = actors.spawn_actor_from_class(pursuer_class, location, u.Rotator(yaw=-45))
        assert pursuer
        pursuer.set_actor_label(label)
    pursuer.set_editor_property('PatrolRoute', route)

if 'BP_Jack' not in placed:
    jack = actors.spawn_actor_from_class(
        assets.load_blueprint_class(root + 'Enemies/Jack/BP_Jack'),
        u.Vector(300, -300, 110), u.Rotator(yaw=-45))
    assert jack
    jack.set_actor_label('BP_Jack')
assert levels.save_current_level()
print('B_PLAYTEST_SAVED')
