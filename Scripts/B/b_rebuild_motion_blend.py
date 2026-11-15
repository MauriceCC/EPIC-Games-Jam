"""Build BlendSpace runtime triangulation through its native asset editor."""
import unreal as u
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play first.'
blend = u.load_asset('/Game/Unscripted/Player/Animation/B_MotionSync/BS_Agent_PostureSpeed')
print('BEFORE', [s.get_editor_property('animation').get_name() for s in blend.get_editor_property('sample_data')])
editor = u.get_editor_subsystem(u.AssetEditorSubsystem)
assert editor.open_editor_for_assets([blend])
assert u.EditorAssetLibrary.save_loaded_asset(blend, False)
print('AFTER', [s.get_editor_property('animation').get_name() for s in blend.get_editor_property('sample_data')])
print('PREVIEW_API', [n for n in dir(u.SkeletalMeshComponent) if any(w in n for w in ('tick_animation', 'refresh_bone', 'animation', 'pose'))])
print('PLAY_API', [n for n in dir(u.LevelEditorSubsystem) if 'play' in n])
