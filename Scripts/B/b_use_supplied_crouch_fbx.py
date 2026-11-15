"""Import and retarget the user's crouch clips, then use their walk in game."""
from pathlib import Path
import runpy
import unreal as u

HERE = Path(__file__).parent
DOWNLOADS = Path('C:/Users/jalfa/Downloads')
CLIPS = [DOWNLOADS / 'CrouchWalk.FBX', DOWNLOADS / 'CrouchIdle.FBX']
assert all(path.is_file() for path in CLIPS), CLIPS
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play before importing.'

# Prevent the standing locomotion component from overriding the crouch clips.
runpy.run_path(str(HERE / 'b_fix_crouch_animation_priority.py'))
helpers = runpy.run_path(str(HERE / 'b_import_crouch_mocap.py'))
source = u.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
assert isinstance(source, u.SkeletalMesh)
skeleton = source.get_editor_property('skeleton')
animations = [helpers['import_fbx'](path, u.AnimSequence, skeleton) for path in CLIPS]
output = helpers['retarget_clips'](source, animations, 'A_Agent_User_', 'IK_Supplied_Crouch', 'RTG_Supplied_Crouch_Agent')
# Keep the existing quiet stance. The supplied idle is ready to compare in the asset editor.
helpers['wire_player']({'A_Agent_CrouchWalk': output[animations[0].get_name()]})
u.log('B_SUPPLIED_CROUCH saved supplied walk on SK_Agent')
runpy.run_path(str(HERE / 'b_diagnose_stealth_pie.py'), run_name='__main__')
