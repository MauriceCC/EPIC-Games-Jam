"""Use named Rotator fields and add isolated test navigation without touching A input."""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
pawn=h.asset("Narrative/Test/BP_TestPlayer_C")
camera=h.add_component(pawn,"TestCamera",unreal.CameraComponent)
camera.set_editor_property("relative_rotation",unreal.Rotator(pitch=-47,yaw=45,roll=0))
vector=unreal.BlueprintEditorLibrary.get_struct_type(unreal.load_object(None,"/Script/CoreUObject.Vector"))
h.function(pawn,"MoveTestPawn",[("Offset",vector)])
h.compile_blueprint(pawn,warnings_as_errors=True)
g=h.edit(pawn,"MoveTestPawn")
pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
blocked=h.call(g,"/Script/Engine.Controller:IsMoveInputIgnored",target=pc).find_result_pin()
yes,_=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,"bTestGameplayInputEnabled"),h.not_(g,blocked)))
h.call(g,"/Script/Engine.Actor:K2_AddActorWorldOffset",yes,DeltaLocation=h.param(g,"Offset"),bSweep=True,bTeleport=False)
for key,offset in (("Up","(X=60,Y=0,Z=0)"),("Down","(X=-60,Y=0,Z=0)"),("Right","(X=0,Y=60,Z=0)"),("Left","(X=0,Y=-60,Z=0)")):
    g,node=h.key_event(pawn,key);h.invoke(g,node.find_output_pin("Pressed"),pawn,"MoveTestPawn",Offset=offset)
h.layout(pawn);h.save(pawn)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=="/Game/Unscripted/Maps/Test/L_Test_C.L_Test_C"
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if actor.get_actor_label().startswith("C_F1_") and actor.get_actor_label().endswith("_Label"):
        actor.set_actor_rotation(unreal.Rotator(pitch=0,yaw=225,roll=0),False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
print("C_F1_CAMERA_READY")
