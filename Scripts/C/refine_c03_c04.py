"""Guard persistent story interactions and retain the occupied hideout focus."""
import unreal,sys,json,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h
from importlib import reload
h=reload(h)
OUT={"passed":False}
try:
    interaction=h.asset("Narrative/BP_InteractionComponent")
    base=h.asset("Narrative/BP_InteractableBase")
    actor=h.obj_type(unreal.Actor)
    h.variable(interaction,"LockedFocusActor",actor,"")
    if not h.edit(interaction,"LockFocusTo"):h.function(interaction,"LockFocusTo",[("Target",actor)])
    h.compile_blueprint(interaction,warnings_as_errors=True)
    g=h.edit(interaction,"LockFocusTo");h.clear_body(g)
    end=h.setvar(g,g.find_graph_entry_pin(),"LockedFocusActor",h.param(g,"Target"))
    h.invoke(g,end,interaction,"RefreshFocus")
    g=h.edit(interaction,"EvaluateCandidate")
    entry=g.find_graph_entry_pin();old=entry.list_connected_pins()[0];entry.break_pin_links()
    allowed=h.any_true(g,h.not_(g,h.is_valid(g,h.get(g,"LockedFocusActor"))),h.math(g,"EqualEqual_ObjectObject",h.param(g,"Candidate"),h.get(g,"LockedFocusActor")))
    yes,_=h.branch(g,entry,allowed);h.connect(yes,old)
    h.save(interaction)
    door=h.asset("Narrative/BP_Door")
    g=h.override(door,"CanInteract");h.clear_body(g)
    state=h.call(g,"/Script/Engine.GameplayStatics:GetGameState").find_result_pin()
    phase=h.message(g,g.find_graph_entry_pin(),"GetCurrentPhase",state)
    phase_int=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=phase.find_result_pin()).find_result_pin()
    permitted=h.any_true(g,h.not_(g,h.get(g,"bReportsEscapeRoute")),h.all_true(g,h.is_valid(g,state),h.math(g,"EqualEqual_IntInt",phase_int,1)))
    permitted=h.all_true(g,permitted,h.get(g,"bInteractionEnabled"),h.not_(g,h.get(g,"bConsumed")),h.is_valid(g,h.param(g,"Interactor")))
    h.result(g,phase.find_then_pin(),Result=permitted)
    hide=h.asset("Narrative/BP_Hideout")
    g=h.override(hide,"CanInteract");h.clear_body(g)
    stealth=h.message(g,g.find_graph_entry_pin(),"GetStealthComponent",h.param(g,"Interactor"))
    permitted=h.all_true(g,h.get(g,"bInteractionEnabled"),h.not_(g,h.get(g,"bConsumed")),h.is_valid(g,h.param(g,"Interactor")),h.is_valid(g,stealth.find_result_pin()),h.any_true(g,h.not_(g,h.get(g,"bOccupied")),h.math(g,"EqualEqual_ObjectObject",h.param(g,"Interactor"),h.get(g,"Occupant"))))
    h.result(g,stealth.find_then_pin(),Result=permitted)
    g=h.edit(hide,"ExecuteInteraction")
    # The base already checked CanInteract before dispatching this implementation.
    for node in g.list_all_nodes():
        if node.get_class().get_name()=="K2Node_CallFunction" and "SetIgnoreMoveInput" in str(node.get_node_title()):
            pass
    # Append a focus lock to each exit branch, after the presentation changes.
    for name,lock in (("InteractionPrompt",True),("Occupant",False)):
        setters=[n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_VariableSet" and h.valid(n.find_input_pin(name)) and not n.find_then_pin().list_connected_pins()]
        for node in setters:
            if lock and str(node.find_input_pin(name).get_pin_value())!="Leave hideout":continue
            component=h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=h.param(g,"Interactor"),ComponentClass=interaction.generated_class().get_path_name()).find_result_pin()
            h.invoke(g,node.find_then_pin(),interaction,"LockFocusTo",target=component,Target=h.self_pin(g) if lock else None)
    h.layout(interaction);h.layout(door);h.layout(hide)
    h.save(interaction,door,hide)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    (repo/"Scripts/C/c03_c04_refinement.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C03_C04_REFINEMENT "+json.dumps(OUT))
