"""Set the isolated C test map to the C-owned GameMode double."""
import unreal
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world=editor.get_editor_world()
assert world.get_path_name()=="/Game/Unscripted/Maps/Test/L_Test_C.L_Test_C"
settings=world.get_world_settings()
mode=unreal.load_asset("/Game/Unscripted/Narrative/Test/BP_TestGameMode_C")
settings.set_editor_property("default_game_mode",mode.generated_class())
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
print("C_F1_MAP_READY",settings.get_editor_property("default_game_mode"))
