"""Fix dynamic checklist wrapping and keep prompts legible over the test floor."""
import unreal,sys,traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/"Scripts/C"))
import blueprint_helpers_c as h,umg_helpers_c as u
from importlib import reload
h=reload(h);u=reload(u)
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
async def build():
    dark=unreal.LinearColor(.018,.027,.04,.98)
    for path,panel in (("WBP_Document","DocumentPanel"),("WBP_Dialogue","DialoguePanel"),("WBP_Checklist","ChecklistPanel"),("WBP_HUD","StatusPanel")):
        bp=h.asset("UI/"+path);unreal.find_object(None,bp.get_path_name()+":WidgetTree."+panel).set_brush_color(dark)
        if path=="WBP_Checklist":
            for i in range(4):
                for name in ("ItemRow"+str(i),"ItemText"+str(i)):
                    obj=unreal.find_object(None,bp.get_path_name()+":WidgetTree."+name)
                    obj.get_editor_property("slot").set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_FILL)
        if path!="WBP_HUD":h.save(bp)
    view=h.asset("UI/WBP_HUD");canvas=unreal.find_object(None,view.get_path_name()+":WidgetTree.HUDCanvas")
    for name,position in (("InteractionBackdrop",(0,-310,760,48,(.5,1),(.5,1))),("TestHintBackdrop",(24,-20,450,96,(0,1),(0,1)))):
        obj=await u.widget(view,unreal.Border,name,canvas,True);obj.set_brush_color(dark);u.place(obj,*position);obj.get_editor_property("slot").set_z_order(8);obj.set_visibility(unreal.SlateVisibility.COLLAPSED)
    prompt=unreal.find_object(None,view.get_path_name()+":WidgetTree.InteractionText");prompt.get_editor_property("slot").set_z_order(9)
    hint=unreal.find_object(None,view.get_path_name()+":WidgetTree.TestHintText");u.place(hint,36,-28,426,80,(0,1),(0,1));hint.get_editor_property("slot").set_z_order(9);hint.set_color_and_opacity(unreal.SlateColor(specified_color=u.PAPER))
    h.compile_blueprint(view,warnings_as_errors=True)
    g=h.edit(view,"SetInteraction")
    for node in list(g.list_all_nodes()):
        if node.get_class().get_name()=="K2Node_CallFunction" and str(node.get_node_title()).replace(" ","").startswith("SetText("):
            text_pin=node.find_input_pin("InText")
            empty=not text_pin.list_connected_pins()
            u.visibility(g,node.find_then_pin(),h.get(g,"InteractionBackdrop"),"Collapsed" if empty else "Visible")
    g=h.edit(view,"SetTestHint")
    node=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(" ","").startswith("SetText("))
    u.visibility(g,node.find_then_pin(),h.get(g,"TestHintBackdrop"),"Visible")
    h.layout(view,["SetInteraction","SetTestHint"]);h.save(view)
    # Keep C-only world labels readable without changing the integrator's floor or light.
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if actor.get_actor_label().startswith("C_F1_") and actor.get_actor_label().endswith("_Label"):
            actor.get_component_by_class(unreal.TextRenderComponent).set_text_render_color(unreal.Color(30,40,55,255))
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    print("C_F1_READABILITY_READY")
async def guarded():
    try:await build()
    except Exception:unreal.log_error(traceback.format_exc())
c_f1_loop=EditorEventLoopManager();c_f1_loop.__enter__();c_f1_task=c_f1_loop.loop.create_task(guarded())
