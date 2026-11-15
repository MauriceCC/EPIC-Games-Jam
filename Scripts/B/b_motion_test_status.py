import unreal as u
print('WORLD', u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world())
print('GLOBALS', [k for k in globals() if k in ('handle', 'tick', 'observe_motion')])
b = u.load_asset('/Game/Unscripted/Player/Animation/B_MotionSync/BS_Agent_PostureSpeed')
print('AXES', [(a.get_editor_property('min'), a.get_editor_property('max')) for a in b.get_editor_property('blend_parameters')])
print('SAMPLES', [(a.get_editor_property('animation').get_name(), str(a.get_editor_property('sample_value'))) for a in b.get_editor_property('sample_data')])
u.get_editor_subsystem(u.AssetEditorSubsystem).close_all_editors_for_asset(b)
print('B_MOTION preview closed')
