"""Install the Workshop side-door interaction and the validated route to the refuge."""
import json
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
runtime = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(runtime)]
import blueprint_helpers_c as h

worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
world = worlds.get_editor_world()
assert world.get_name() == 'L_Whitechapel' and not worlds.get_game_world()
nav = u.NavigationSystemV1
placed = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
pipe = placed['FA_XPipe_01']
jack = placed['B_Jack_Workshop']
pipe_mesh = pipe.get_component_by_class(u.StaticMeshComponent)
assert str(pipe_mesh.get_collision_profile_name()) == 'NoCollision', 'Persist the decorative pipe profile before generating the route.'
coordinates = [(2800,4800), (2800,4600), (2800,4200), (2900,3600), (2900,2800),
               (2800,2000), (2800,1400), (3100,500)]
route = []
previous = jack.get_actor_location()
for x, y in coordinates:
    point = nav.project_point_to_navigation(world, u.Vector(x,y,0), None, None, u.Vector(80,80,175))
    assert point is not None, (x,y)
    path = nav.find_path_to_location_synchronously(world, previous, point, jack)
    assert path and path.is_valid() and not path.is_partial(), (previous, point)
    route.append(point)
    previous = point

base = h.asset('Narrative/BP_Door')
name = 'BP_WorkshopEscapeDoor'
path = '/Game/Unscripted/Enemies/Jack/' + name
existing = u.EditorAssetLibrary.does_asset_exist(path)
bp = h.asset(path) if existing else h.create_actor_bp('Enemies/Jack', name, base.generated_class())
defaults = u.get_default_object(bp.generated_class())
defaults.set_editor_property('InteractionPrompt', 'Open the side door')
defaults.set_editor_property('InteractionPriority', 65)

g = h.override(bp, 'CanInteract')
h.clear_body(g)
state = h.call(g, '/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
interactor = h.param(g, 'Interactor')
ready = h.all_true(g, h.is_valid(g, state), h.is_valid(g, interactor),
                   h.get(g, 'bInteractionEnabled'), h.not_(g, h.get(g, 'bConsumed')))
yes, no = h.branch(g, g.find_graph_entry_pin(), ready)
phase = h.message(g, yes, 'GetCurrentPhase', state)
phase_pin = phase.find_result_pin()
enum = json.loads(phase_pin.get_pin_type_as_json_schema())['enum']
action = next(n for n in h.actions(g, [phase_pin]) if n.endswith(('|Igual(enumerador)', '|Equal(Enum)')))
equal = g.create_node_from_name(action, u.Vector2D(), [phase_pin])
h.connect(phase_pin, equal.find_input_pin('A'))
h.literal(equal.find_input_pin('B'), 'NewEnumerator' + str(enum.index('OpenEscapeRoute')))
h.result(g, phase.find_then_pin(), Result=equal.find_result_pin())
h.result(g, no, Result=False)
h.layout(bp, {'CanInteract'})
h.save(bp)

assert levels.set_current_level_by_name('L_Whitechapel_AI')
door = placed.get('B_WorkshopEscapeDoor')
if not door:
    door = actors.spawn_actor_from_class(bp.generated_class(),u.Vector(2800,4600,0),u.Rotator(yaw=90))
    assert door and door.get_outermost() == jack.get_outermost()
    door.set_actor_label('B_WorkshopEscapeDoor')
door.modify()
door.set_actor_scale3d(u.Vector(1, 1.77, 1))
mesh = door.get_editor_property('DoorMesh')
mesh.modify()
mesh.set_editor_property('bCanEverAffectNavigation', False)
jack.modify()
jack.set_editor_property('Waypoints', route)
# Save only the edited packages, including the persistent Recast data.
assert u.EditorLoadingAndSavingUtils.save_packages([jack.get_outermost(), pipe.get_outermost(), world.get_outermost()], False)
u.log('B_WORKSHOP_ESCAPE saved gated side door and eight connected Jack waypoints')
