"""Exercise the saved interaction graphs through actual PIE actors and messages."""
import unreal,json,traceback
from pathlib import Path
OUT={"passed":False,"checks":[]}
spawned=[]
def check(name,value):
    OUT["checks"].append({"name":name,"passed":bool(value)})
    assert value,name
def prop(obj,name):return obj.get_editor_property(name)
try:
    world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
    pawn=unreal.GameplayStatics.get_player_pawn(world,0)
    check("C-owned test player is possessed",pawn.get_class().get_name()=="BP_TestPlayer_C_C")
    component=pawn.get_component_by_class(unreal.load_asset("/Game/Unscripted/Narrative/BP_InteractionComponent").generated_class())
    state=unreal.GameplayStatics.get_game_state(world)
    manager=state.call_method("GetObjectiveManager")
    for _ in range(40):
        if not prop(manager,"bDialogueActive"):break
        pawn.call_method("HandleTestUse")
    base=unreal.load_asset("/Game/Unscripted/Narrative/BP_InteractableBase").generated_class()
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world,base):actor.set_editor_property("bInteractionEnabled",False)
    check("C GameState is active",state.get_class().get_name()=="BP_GameState_C")
    pos=pawn.get_actor_location()
    statics=unreal.get_default_object(unreal.GameplayStatics)
    def spawn(name,offset,**config):
        bp=unreal.load_asset("/Game/Unscripted/Narrative/"+name)
        trans=unreal.Transform(location=pos+unreal.Vector(*offset))
        actor=statics.call_method("BeginDeferredActorSpawnFromClass",args=(world,bp.generated_class(),trans,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        for key,value in config.items():actor.set_editor_property(key,value)
        actor=statics.call_method("FinishSpawningActor",args=(actor,trans,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        spawned.append(actor);return actor
    def focus():component.call_method("RefreshFocus");return prop(component,"FocusedActor")
    door_stub=spawn("Test/BP_TestInteractable_C",(80,0,0),InteractionPriority=40,InteractionPrompt="Open test door")
    finisher=spawn("Test/BP_TestInteractable_C",(160,0,0),InteractionPriority=100,InteractionPrompt="Finish test target")
    check("Priority 100 beats the closer priority 40 door",focus()==finisher)
    count=prop(pawn,"FocusChangeCount");focus()
    check("Stable focus does not duplicate notifications",prop(pawn,"FocusChangeCount")==count)
    check("Single interaction accepted",component.call_method("TryInteract"))
    check("Only the selected target was used",prop(finisher,"InteractionCount")==1 and prop(door_stub,"InteractionCount")==0)
    check("Consumed target is excluded",focus()==door_stub)
    tie=spawn("Test/BP_TestInteractable_C",(35,0,0),InteractionPriority=40)
    check("Equal priorities select the shorter distance",focus()==tie)
    tie.set_actor_location(pos+unreal.Vector(600,0,0),False,True)
    check("Out-of-range target is excluded",focus()==door_stub)
    door_stub.set_editor_property("bInteractionEnabled",False)
    check("Disabled targets clear the focus",focus() is None)
    component.call_method("SetInteractionEnabled",args=(False,))
    check("Disabled interaction rejects use",not component.call_method("TryInteract"))
    component.call_method("SetInteractionEnabled",args=(True,))
    for actor in spawned:actor.destroy_actor()
    spawned.clear()
    door=spawn("BP_Door",(100,0,0))
    check("Story door cannot be consumed before Jack is found",focus() is None and not prop(door,"bIsOpen"))
    source=spawn("Test/BP_StoryEventTestSource_C",(1000,0,0))
    events=type(prop(source,"EventToReport"))
    source.set_editor_property("EventToReport",events.cast(0));source.call_method("ReportConfiguredEvent")
    for _ in range(40):
        if not prop(manager,"bDialogueActive"):break
        pawn.call_method("HandleTestUse")
    check("Found Jack unlocks the route door",state.call_method("GetCurrentPhase").value==1 and focus()==door)
    cleared=prop(pawn,"RetakeHistoryClearCount")
    component.call_method("TryInteract")
    check("Door opens once and reports the route",prop(door,"bIsOpen") and prop(door,"bConsumed") and state.call_method("GetCurrentPhase").value==2)
    check("Persistent door clears personal Retake history",prop(pawn,"RetakeHistoryClearCount")==cleared+1)
    check("Open door no longer has collision",not door.get_actor_enable_collision())
    component.call_method("TryInteract")
    check("Open door cannot be activated again",prop(door,"InteractionCount")==1)
    hideout=spawn("BP_Hideout",(100,0,0))
    check("Hideout is interactable",focus()==hideout)
    component.call_method("TryInteract")
    stealth=prop(pawn,"TestStealth")
    check("Entering calls the stealth contract",prop(hideout,"bOccupied") and prop(stealth,"bTestHidden"))
    check("Hidden agent cannot Retake",prop(pawn,"bTestRetakeBlocked"))
    check("Prompt changes to leave",str(prop(component,"FocusPrompt"))=="Leave hideout")
    distractor=spawn("Test/BP_TestInteractable_C",(40,0,0),InteractionPriority=100)
    check("Occupied hideout retains its exit focus",focus()==hideout)
    component.call_method("TryInteract")
    check("Leaving clears hidden state and Retake block",not prop(hideout,"bOccupied") and not prop(stealth,"bTestHidden") and not prop(pawn,"bTestRetakeBlocked"))
    check("Leaving releases the focus lock",focus()==distractor)
    check("Both SetHidden calls reached the component",prop(stealth,"HiddenChangeCount")==2)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    for actor in spawned:
        if unreal.SystemLibrary.is_valid(actor):actor.destroy_actor()
    OUT["check_count"]=len(OUT["checks"])
    (Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent/"Scripts/C/c03_c04_pie_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C03_C04_PIE "+json.dumps(OUT))
