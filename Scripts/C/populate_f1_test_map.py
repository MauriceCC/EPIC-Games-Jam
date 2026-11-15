"""Place only C-owned fixtures in L_Test_C and preserve all existing map actors."""
import unreal,sys,json,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
OUT={"passed":False,"fixtures":[]}
try:
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert world.get_path_name()=="/Game/Unscripted/Maps/Test/L_Test_C.L_Test_C"
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
    start=next(a for a in existing.values() if isinstance(a,unreal.PlayerStart))
    origin=start.get_actor_location();ground=origin.z-100
    fixtures=(("JackReport","Test/BP_TestInteractable_C",(100,0),{"InteractionPriority":60,"InteractionPrompt":"Talk to Jack","bReportJackFound":True},"Jack / simulated report"),("EscapeDoor","BP_Door",(160,0),{},"Escape route"),("NursingRecord","BP_Evidence",(65,100),{},"Nursing Record"),("FabricatedReport","BP_Evidence",(140,100),{"EvidenceType":1},"Fabricated Report"),("Hideout","BP_Hideout",(-145,0),{},"Hideout"),("Checkpoint","BP_Checkpoint",(-80,-125),{"CheckpointId":"C_FieldCheckpoint"},"Checkpoint"),("FinisherPriority","Test/BP_TestInteractable_C",(120,-80),{"InteractionPriority":100,"InteractionPrompt":"Finish test target","bInteractionEnabled":False},"Finisher priority fixture / disabled"))
    for key,path,xy,config,title in fixtures:
        label="C_F1_"+key
        actor=existing.get(label)
        if actor is None:
            actor=actors.spawn_actor_from_class(h.asset("Narrative/"+path).generated_class(),unreal.Vector(origin.x+xy[0],origin.y+xy[1],ground))
            actor.set_actor_label(label)
            for name,value in config.items():
                if name=="EvidenceType":value=type(actor.get_editor_property(name)).cast(value)
                actor.set_editor_property(name,value)
        OUT["fixtures"].append(actor.get_path_name())
        text_label=label+"_Label"
        if text_label not in existing:
            marker=actors.spawn_actor_from_class(unreal.TextRenderActor,actor.get_actor_location()+unreal.Vector(0,0,140),unreal.Rotator(0,225,0))
            marker.set_actor_label(text_label)
            component=marker.get_component_by_class(unreal.TextRenderComponent)
            component.set_text(title);component.set_world_size(14)
            component.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    (repo/"Scripts/C/c_f1_map_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_MAP "+json.dumps(OUT))
