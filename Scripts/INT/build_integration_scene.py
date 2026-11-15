"""Build the integration sandbox from the existing Division B test map."""
import unreal as ue

root = "/Game/Unscripted/"
source = root + "Maps/Test/L_Test_B"
target = root + "Maps/Test/L_Test_Integration_Iso"
assets = ue.EditorAssetLibrary
levels = ue.get_editor_subsystem(ue.LevelEditorSubsystem)
actors = ue.get_editor_subsystem(ue.EditorActorSubsystem)

if not assets.does_asset_exist(target):
    assert assets.duplicate_asset(source, target), target
assert levels.load_level(target), target

def box(label, position, scale, parent=None):
    obj = actors.spawn_actor_from_class(ue.StaticMeshActor, ue.Vector(*position))
    assert obj, label
    obj.set_actor_label(label)
    obj.static_mesh_component.set_static_mesh(ue.load_asset("/Engine/BasicShapes/Cube.Cube"))
    obj.set_actor_scale3d(ue.Vector(*scale))
    if parent:
        obj.set_actor_enable_collision(False)
        rule = ue.AttachmentRule.KEEP_WORLD
        obj.attach_to_actor(parent, "", rule, rule, rule, False)

labels = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
for name, x, y, scale in [
    ("Checkpoint", -250, -250, (0.65, 0.65, 0.15)),
    ("Door", 0, 570, (1.3, 0.25, 1.8)),
    ("Evidence", -400, 430, (0.4, 0.4, 0.25)),
    ("Hideout", 520, -300, (1.4, 0.8, 0.7)),
    ("FinalChoice", 0, 780, (1.2, 0.65, 0.7)),
]:
    label = "Integration_" + name
    obj = labels.get(label)
    if obj is None:
        cls = assets.load_blueprint_class(root + "Narrative/BP_" + name)
        assert cls, name
        obj = actors.spawn_actor_from_class(cls, ue.Vector(x, y, 25))
        assert obj, name
        obj.set_actor_label(label)
    if label + "_Marker" not in labels:
        box(label + "_Marker", (x, y, scale[2] * 50), scale, obj)

if "Integration_Cover" not in labels:
    box("Integration_Cover", (500, -50, 40), (2, 0.6, 0.8))

# The inherited test instance had a 90-degree pitch. Keep the character upright.
jack = labels["BP_Jack"]
rotation = jack.get_actor_rotation()
assert jack.set_actor_rotation(ue.Rotator(pitch=0, yaw=rotation.yaw, roll=0), False)

# [PROPUESTA] Frame the entire sandbox with the existing isometric camera.
camera_label = "Integration_IsometricCamera"
camera_location = ue.Vector(-1800, -1800, 1800)
camera_rotation = ue.Rotator(pitch=-35.264, yaw=45, roll=0)
camera = labels.get(camera_label)
if camera is None:
    camera = actors.spawn_actor_from_class(ue.CameraActor, camera_location, camera_rotation)
    assert camera
    camera.set_actor_label(camera_label)
assert camera.set_actor_location(camera_location, False, True)
assert camera.set_actor_rotation(camera_rotation, False)
camera.set_editor_property("auto_activate_for_player", ue.AutoReceiveInput.PLAYER0)
component = camera.get_editor_property("camera_component")
component.set_editor_property("projection_mode", ue.CameraProjectionMode.ORTHOGRAPHIC)
# The 2,000-unit square projects to about 2,828 units at a yaw of 45 degrees.
component.set_editor_property("ortho_width", 3100.0)
assert levels.save_current_level(), target
print("INTEGRATION_SAVED " + target)
print("INTEGRATION_ACTORS " + ", ".join(
    a.get_class().get_name() for a in actors.get_all_level_actors()))



