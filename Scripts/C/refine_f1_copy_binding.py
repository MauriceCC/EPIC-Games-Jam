"""Read production narrative copy from C DataTables instead of baking text into graph nodes."""
import unreal,sys,json,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h,umg_helpers_c as u
from importlib import reload
h=reload(h);u=reload(u);OUT={"passed":False}
try:
    base=h.asset("Narrative/BP_InteractableBase");interaction=h.asset("Narrative/BP_InteractionComponent");hide=h.asset("Narrative/BP_Hideout")
    h.variable(base,"InteractionPromptRow",h.basic("name"),"",True,"Interaction")
    h.compile_blueprint(base,warnings_as_errors=True)
    g=h.edit(base,"GetInteractionText");h.clear_body(g)
    exists=h.call(g,"/Script/Engine.KismetMathLibrary:NotEqual_NameName",A=h.get(g,"InteractionPromptRow"),B="").find_result_pin()
    yes,no=h.branch(g,g.find_graph_entry_pin(),exists)
    row=h.table_row(g,yes,h.asset("Narrative/DT_HUDText"),h.get(g,"InteractionPromptRow"));fields=h.break_struct(g,row.find_result_pin())
    h.result(g,row.find_then_pin(),Result=fields["Text"])
    h.result(g,no,Result=h.get(g,"InteractionPrompt"));h.result(g,row.find_output_pin("RowNotFound"),Result=h.get(g,"InteractionPrompt"))
    h.layout(base,["GetInteractionText"]);h.save(base)
    for path,key in (("BP_Door","DoorPrompt"),("BP_Hideout","HideoutEnterPrompt"),("BP_Evidence","EvidencePrompt"),("BP_Checkpoint","CheckpointPrompt")):
        bp=h.asset("Narrative/"+path);h.compile_blueprint(bp,warnings_as_errors=True);unreal.get_default_object(bp.generated_class()).set_editor_property("InteractionPromptRow",key);h.save(bp)
    # Reversible hideout state selects row keys; visible text stays in the table.
    g=h.edit(hide,"ExecuteInteraction");h.clear_body(g)
    end=h.setvar(g,g.find_graph_entry_pin(),"bOccupied",h.not_(g,h.get(g,"bOccupied")));end=h.setvar(g,end,"Occupant",h.param(g,"Interactor"))
    stealth=h.message(g,end,"GetStealthComponent",h.param(g,"Interactor"))
    end=h.invoke(g,stealth.find_then_pin(),h.asset("Enemies/BP_StealthComponent"),"SetHidden",target=stealth.find_result_pin(),bHidden=h.get(g,"bOccupied")).find_then_pin()
    end=h.message(g,end,"SetRetakeBlocked",h.param(g,"Interactor"),bBlocked=h.get(g,"bOccupied")).find_then_pin()
    pc=h.call(g,"/Script/Engine.GameplayStatics:GetPlayerController",PlayerIndex=0).find_result_pin()
    end=h.call(g,"/Script/Engine.Controller:SetIgnoreMoveInput",end,pc,bNewMoveInput=h.get(g,"bOccupied")).find_then_pin()
    yes,no=h.branch(g,end,h.get(g,"bOccupied"))
    yes=h.setvar(g,yes,"InteractionPromptRow","HideoutLeavePrompt");no=h.setvar(g,no,"InteractionPromptRow","HideoutEnterPrompt");no=h.setvar(g,no,"Occupant",None)
    focus=h.call(g,"/Script/Engine.Actor:GetComponentByClass",target=h.param(g,"Interactor"),ComponentClass=interaction.generated_class().get_path_name()).find_result_pin()
    h.invoke(g,yes,interaction,"LockFocusTo",target=focus,Target=h.self_pin(g));h.invoke(g,no,interaction,"LockFocusTo",target=focus,Target=None)
    g=h.edit(hide,"ResetOccupancy")
    old=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_VariableSet" and "InteractionPrompt" in str(n.get_node_title()).replace(" ",""))
    start=old.find_execute_pin().list_connected_pins()[0];next_pins=old.find_then_pin().list_connected_pins();g.remove_nodes([old])
    end=h.setvar(g,start,"InteractionPromptRow","HideoutEnterPrompt")
    for target in next_pins:h.connect(end,target)
    h.layout(hide,["ExecuteInteraction","ResetOccupancy"]);h.save(hide)
    evidence=h.asset("Narrative/BP_Evidence");g=h.edit(evidence,"RecordEvidence")
    show=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(" ","")=="OpenDocument")
    start=show.find_execute_pin().list_connected_pins()[0];start.break_pin_links()
    token=h.call(g,"/Script/Engine.KismetStringLibrary:Conv_NameToString",InName=h.param(g,"Param")).find_result_pin()
    title_key=h.call(g,"/Script/Engine.KismetStringLibrary:Concat_StrStr",A=token,B="_Title").find_result_pin();title_key=h.call(g,"/Script/Engine.KismetStringLibrary:Conv_StringToName",InString=title_key).find_result_pin()
    body_key=h.call(g,"/Script/Engine.KismetStringLibrary:Concat_StrStr",A=token,B="_Summary").find_result_pin();body_key=h.call(g,"/Script/Engine.KismetStringLibrary:Conv_StringToName",InString=body_key).find_result_pin()
    title=h.table_row(g,start,h.asset("Narrative/DT_NarrativeText"),title_key);title_fields=h.break_struct(g,title.find_result_pin())
    body=h.table_row(g,title.find_then_pin(),h.asset("Narrative/DT_NarrativeText"),body_key);body_fields=h.break_struct(g,body.find_result_pin())
    h.connect(body.find_then_pin(),show.find_execute_pin());h.connect(title_fields["Text"],show.find_input_pin("Title"));h.connect(body_fields["Text"],show.find_input_pin("Body"))
    g=h.edit(evidence,"ExecuteInteraction")
    for node in g.list_all_nodes():
        if str(node.get_node_title()).replace(" ","")=="RecordEvidence":
            h.literal(node.find_input_pin("Title"),"");h.literal(node.find_input_pin("Body"),"")
    h.layout(evidence,["RecordEvidence","ExecuteInteraction"]);h.save(evidence)
    view=h.asset("UI/WBP_HUD");g=h.edit(view,"SetObjective");h.clear_body(g)
    index=h.call(g,"/Script/Engine.KismetMathLibrary:Conv_ByteToInt",InByte=h.param(g,"Phase")).find_result_pin();end=g.find_graph_entry_pin()
    for i,key in enumerate(("FindJack","OpenEscapeRoute","ProtectJack","DiscoverTruth","FinalChoice","GameEnded")):
        yes,end=h.branch(g,end,h.math(g,"EqualEqual_IntInt",index,i))
        row=h.table_row(g,yes,h.asset("Narrative/DT_HUDText"),key);fields=h.break_struct(g,row.find_result_pin());u.set_text(g,row.find_then_pin(),"ObjectiveText",fields["Text"])
    g=h.edit(view,"SetRetake")
    setter=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(" ","").startswith("SetText("))
    start=setter.find_execute_pin().list_connected_pins()[0];start.break_pin_links()
    row=h.table_row(g,start,h.asset("Narrative/DT_HUDText"),"RetakePrefix");fields=h.break_struct(g,row.find_result_pin())
    prefix=h.call(g,"/Script/Engine.KismetTextLibrary:Conv_TextToString",InText=fields["Text"]).find_result_pin()
    append=next(n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_CommutativeAssociativeBinaryOperator" and str(n.find_input_pin("A").get_pin_value())=="Retake ")
    h.literal(append.find_input_pin("A"),"");h.connect(prefix,append.find_input_pin("A"));h.connect(row.find_then_pin(),setter.find_execute_pin())
    h.layout(view,["SetObjective","SetRetake"]);h.save(view)
    hud=h.asset("UI/BP_HUD");g=h.edit(hud,"SyncDialogue")
    speaker_keys=(("Agent","Speaker_Agent"),("Jack","Speaker_Jack"),("Supervisor","Speaker_Supervisor"),("Director","Speaker_Director"),("Future Self","Speaker_FutureSelf"),("Interventor","Speaker_Interventor"),("Department of Continuity","Speaker_System"))
    for node in list(g.list_all_nodes()):
        if str(node.get_node_title()).replace(" ","")!="ShowDialogue":continue
        label=str(node.find_input_pin("Speaker").get_pin_value());key=next(key for text,key in speaker_keys if '"'+text+'"' in label)
        start=node.find_execute_pin().list_connected_pins()[0];start.break_pin_links()
        row=h.table_row(g,start,h.asset("Narrative/DT_UIStrings"),key);fields=h.break_struct(g,row.find_result_pin())
        h.literal(node.find_input_pin("Speaker"),"");h.connect(fields["Text"],node.find_input_pin("Speaker"));h.connect(row.find_then_pin(),node.find_execute_pin())
    h.layout(hud,["SyncDialogue"]);h.save(hud)
    OUT["passed"]=True
except Exception:OUT["error"]=traceback.format_exc()
finally:
    (repo/"Scripts/C/c_f1_copy_binding_validation.json").write_text(json.dumps(OUT,indent=2),encoding="utf-8")
    print("C_F1_COPY_BINDING "+json.dumps(OUT))
