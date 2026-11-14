"""Create missing non-partitioned F0 maps. Requires LFS lock on persistent map.

[PROPUESTA] Neutral 20m square test floors, lights and PlayerStart. This is
workspace scaffolding, not the Whitechapel blockout or F1 gameplay.
"""
import unreal
A = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
worlds = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ROOT = '/Game/Unscripted/Maps/'

def spawn(cls, name, pos=(0,0,0)):
    obj = actors.spawn_actor_from_class(cls, unreal.Vector(*pos))
    assert obj, name
    obj.set_actor_label(name)
    return obj

def floor():
    obj = spawn(unreal.StaticMeshActor, 'F0_TestFloor', (0,0,-10))
    obj.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
    obj.set_actor_scale3d(unreal.Vector(20,20,0.2))

def lighting():
    sun = spawn(unreal.DirectionalLight, 'F0_GlobalSun', (0,0,400))
    sun.set_actor_rotation(unreal.Rotator(-55,-25,0), False)
    sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sky = spawn(unreal.SkyLight, 'F0_GlobalSky', (0,0,400))
    sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)

def navigation():
    volume = spawn(unreal.NavMeshBoundsVolume, 'F0_NavigationBounds', (0,0,100))
    volume.set_actor_scale3d(unreal.Vector(11,11,3))
    center, extent = volume.get_actor_bounds(False)
    assert extent.x > 0 and extent.y > 0, 'NavMesh volume has no brush bounds'

for name in ['L_Whitechapel_Geo','L_Whitechapel_Light','L_Whitechapel_AI','L_Whitechapel_Story']:
    if A.does_asset_exist(ROOT+name):
        continue
    assert E.new_level(ROOT+name, False)
    if name.endswith('_Geo'):
        floor()
    if name.endswith('_Story'):
        spawn(unreal.PlayerStart, 'PlayerStart', (0,0,120))
    assert E.save_current_level()

for division in 'ABCD':
    path = ROOT+'Test/L_Test_'+division
    if A.does_asset_exist(path):
        continue
    assert E.new_level(path, False)
    floor()
    lighting()
    spawn(unreal.PlayerStart, 'PlayerStart', (0,0,120))
    navigation()
    assert E.save_current_level()

path = ROOT+'L_Whitechapel'
if not A.does_asset_exist(path):
    assert E.new_level(path, False)
else:
    assert E.load_level(path)
world = worlds.get_editor_world()
persistent = E.get_current_level()
loaded = {level.get_outermost().get_path_name() for level in unreal.EditorLevelUtils.get_levels(world)}
for suffix in ['Geo','Light','AI','Story']:
    level_path = ROOT+'L_Whitechapel_'+suffix
    if level_path not in loaded:
        unreal.EditorLevelUtils.add_level_to_world(world, level_path, unreal.LevelStreamingAlwaysLoaded)
assert E.set_current_level_by_name('L_Whitechapel')
labels = {a.get_actor_label() for a in actors.get_all_level_actors()}
if 'F0_GlobalSun' not in labels:
    lighting()
if 'F0_NavigationBounds' not in labels:
    navigation()
assert E.save_current_level()
print('F0 maps created; existing maps preserved')
