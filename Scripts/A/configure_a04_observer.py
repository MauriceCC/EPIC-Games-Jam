"""Make the test observer's two inputs configurable on test instances."""
import unreal
bp=unreal.load_asset('/Game/Unscripted/Player/Test/BP_HealthObserver_A')
for name in ('ObservedHealth','bAttemptReentry'):
    unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,name,True)
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
