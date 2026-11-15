"""Division C: build the explicitly authorized, isolated F0 UI previews.
Run through Unreal MCP's editor console. Only the three UI/Test assets are edited.
The CSV data is baked into presentation graphs; no shared gameplay contracts are used.
"""
import unreal
import csv
import json
import re
import traceback
from pathlib import Path
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
from editor_toolset.toolsets.blueprint import BlueprintTools
from toolset_registry.helpers import compile_blueprint

UI_ROOT = "/Game/Unscripted/UI/Test"
NAMES = ("WBP_DialoguePrototype_C", "WBP_ChecklistPrototype_C", "EUW_NarrativeTestLauncher_C")
SOURCE = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent / "SourceData" / "C"
INK = unreal.LinearColor(0.032, 0.045, 0.064, 1)
PANEL = unreal.LinearColor(0.055, 0.075, 0.10, 1)
PAPER = unreal.LinearColor(0.88, 0.91, 0.91, 1)
GOLD = unreal.LinearColor(0.82, 0.63, 0.31, 1)
MUTED = unreal.LinearColor(0.48, 0.60, 0.66, 1)
CYAN = unreal.LinearColor(0.34, 0.82, 0.78, 1)

def ref(obj):
    return {"refPath": obj.get_path_name()}
async def umg(name, **args):
    return await execute_tool("UMGToolSet.UMGToolSet", name, args)
def resolve(value):
    obj = unreal.find_object(None, value["refPath"])
    assert obj, value
    return obj
def connect(a, b):
    assert a.try_create_connection(b), "Could not connect " + str(a.get_pin_name()) + " -> " + str(b.get_pin_name())
def literal(pin, value):
    if isinstance(value, bool):
        value = "true" if value else "false"
    assert pin.set_pin_value(str(value)), "Invalid pin literal: " + str(value)
def call(g, path):
    node = g.add_call_function_node(path)
    assert node, path
    return node
def get(g, name):
    return g.add_get_member_variable_node(name).find_result_pin()
def assign(g, start, name, value):
    node = g.add_set_member_variable_node(name)
    connect(start, node.find_execute_pin())
    if isinstance(value, unreal.BlueprintGraphPin):
        connect(value, node.find_input_pin(name))
    else:
        literal(node.find_input_pin(name), value)
    return node.find_then_pin()
def action(g, start, widget, function, parameter, value):
    node = call(g, "/Script/UMG." + function)
    connect(start, node.find_execute_pin())
    connect(get(g, widget), node.find_self_pin())
    if isinstance(value, unreal.BlueprintGraphPin):
        connect(value, node.find_input_pin(parameter))
    else:
        literal(node.find_input_pin(parameter), value)
    return node.find_then_pin()
def text_action(g, start, widget, value):
    return action(g, start, widget, "TextBlock:SetText", "InText", value)
def compare(g, function, a, b):
    node = call(g, "/Script/Engine.KismetMathLibrary:" + function)
    connect(a, node.find_input_pin("A"))
    literal(node.find_input_pin("B"), b)
    return node.find_result_pin()
def branch(g, start, condition):
    node = g.add_branch_node()
    connect(start, node.find_execute_pin())
    connect(condition, node.find_input_pin("Condition"))
    return node.find_output_pin("then"), node.find_output_pin("else")
def new_function(bp, name):
    return unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, name)
def add_var(g, name, kind, value):
    assert g.add_member_variable(name, unreal.BlueprintEditorLibrary.get_basic_type_by_name(kind), str(value))
def invoke(g, start, bp, function, **values):
    node = call(g, bp.generated_class().get_path_name() + ":" + function)
    connect(start, node.find_execute_pin())
    for key, value in values.items():
        if isinstance(value, unreal.BlueprintGraphPin):
            connect(value, node.find_input_pin(key))
        else:
            literal(node.find_input_pin(key), value)
    return node.find_then_pin()
def layout_graphs(bp):
    for graph in BlueprintTools.list_graphs(bp):
        g = unreal.BlueprintGraphEditor.get_graph_editor(graph)
        for index, node in enumerate(g.list_all_nodes()):
            node.set_node_pos(unreal.IntPoint((index % 10) * 340, (index // 10) * 210))
async def widget(bp, cls, name, parent=None, variable=False):
    args = dict(widgetBlueprint=ref(bp), widgetClass=ref(cls if isinstance(cls, unreal.Class) else cls.static_class()), widgetDisplayName=name)
    if parent is not None:
        args["parentWidget"] = ref(parent)
    result = (await umg("AddWidget", **args))["returnValue"]
    w = resolve(result["widget"])
    if variable:
        await umg("ToggleWidgetAsVariable", widgetBlueprint=ref(bp), widget=ref(w), bIsVariable=True)
    return w
async def label(bp, parent, name, value, size=16, color=None, variable=False):
    w = await widget(bp, unreal.TextBlock, name, parent, variable)
    w.set_text(unreal.Text(value))
    w.set_auto_wrap_text(True)
    w.set_color_and_opacity(unreal.SlateColor(specified_color=color or PAPER))
    font = w.get_editor_property("font")
    font.set_editor_property("size", size)
    w.set_font(font)
    slot = w.get_editor_property("slot")
    if slot and hasattr(slot, "set_padding"):
        slot.set_padding(unreal.Margin(0, 0, 0, 8))
    return w
async def button(bp, parent, name, caption):
    w = await widget(bp, unreal.Button, name, parent, True)
    w.set_background_color(unreal.LinearColor(0.11, 0.18, 0.22, 1))
    w.set_tool_tip_text(caption)
    await label(bp, w, name + "Label", caption, 13, PAPER)
    slot = w.get_editor_property("slot")
    if slot and hasattr(slot, "set_padding"):
        slot.set_padding(unreal.Margin(0, 0, 8, 8))
    return w
async def panel(bp):
    root = await widget(bp, unreal.Border, "PreviewPanel")
    root.set_brush_color(PANEL)
    root.set_padding(unreal.Margin(24))
    return await widget(bp, unreal.VerticalBox, "PreviewContent", root)
async def bind(bp, button_name, target_function, **values):
    eg = unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp))
    before = {n.get_path_name() for n in eg.list_all_nodes()}
    result = await umg("BindToEventProperty", widgetBlueprint=ref(bp), eventName="OnClicked", propertyName=button_name, propertyClass=ref(unreal.Button.static_class()))
    assert result["returnValue"], button_name
    nodes = [n for n in eg.list_all_nodes() if n.get_path_name() not in before]
    assert len(nodes) == 1, (button_name, nodes)
    invoke(eg, nodes[0].find_then_pin(), bp, target_function, **values)
def construct(bp, target_function):
    node = unreal.BlueprintEditorLibrary.add_event_override(bp, "Construct", unreal.IntPoint(-400, -400))
    assert node, "Construct event unavailable"
    eg = unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp))
    invoke(eg, node.find_then_pin(), bp, target_function)

async def create_blueprint(name, utility=False):
    path = UI_ROOT + "/" + name
    assert name in NAMES
    bp = unreal.load_asset(path)
    if bp:
        # Rebuild only these exact preview assets, never shared or existing gameplay assets.
        tree = (await umg("GetWidgets", widgetBlueprint=ref(bp)))["returnValue"]
        for item in tree["widgets"]:
            if item.get("parent") in (None, "None") or (isinstance(item.get("parent"), dict) and not item["parent"].get("refPath")):
                await umg("RemoveWidget", widgetBlueprint=ref(bp), widget=item["widget"])
        for graph in list(BlueprintTools.list_graphs(bp)):
            if graph.get_name() == "EventGraph":
                eg = unreal.BlueprintGraphEditor.get_graph_editor(graph)
                eg.remove_nodes(eg.list_all_nodes())
            else:
                unreal.BlueprintEditorLibrary.remove_graph(bp, graph)
        for member in ("NextLineIndex", "CurrentLineIndex", "CompletedCount", "IsRewritten"):
            try:
                unreal.BlueprintEditorLibrary.remove_member_variable(bp, member)
            except Exception:
                pass
        return bp
    factory = unreal.EditorUtilityWidgetBlueprintFactory() if utility else unreal.WidgetBlueprintFactory()
    asset_class = unreal.EditorUtilityWidgetBlueprint if utility else unreal.WidgetBlueprint
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, UI_ROOT, asset_class, factory)
    assert bp, path
    return bp

async def build_dialogue(bp, rows):
    content = await panel(bp)
    await label(bp, content, "DialogueEyebrow", "01 / DIALOGUE PREVIEW", 12, GOLD)
    await label(bp, content, "DialogueHeading", "A story under orders.", 26)
    await label(bp, content, "DialogueHint", "Select a scene. Continue through its original lines.", 13, MUTED)
    selectors = await widget(bp, unreal.HorizontalBox, "SceneSelectorsA", content)
    selectors_b = await widget(bp, unreal.HorizontalBox, "SceneSelectorsB", content)
    by_name = {r["Name"]: i for i, r in enumerate(rows)}
    samples = [("BriefingButton", "Briefing", "Briefing_01"), ("JackButton", "Meet Jack", "JackFound_01"), ("TruthButton", "Revelation", "Truth_01"), ("CorrectionButton", "Correction", "Correction_Order"), ("OfficialButton", "Official ending", "EndingOfficial_01"), ("AuthenticButton", "True ending", "EndingAuthentic_01")]
    for index, (name, caption, row) in enumerate(samples):
        await button(bp, selectors if index < 3 else selectors_b, name, caption)
    await label(bp, content, "SpeakerText", "Department of Continuity", 14, CYAN, True)
    body_box = await widget(bp, unreal.SizeBox, "DialogueBodyArea", content)
    body_box.set_min_desired_height(130)
    body_box.set_max_desired_width(760)
    await label(bp, body_box, "DialogueBodyText", rows[0]["Text"], 20, PAPER, True)
    await label(bp, content, "DialogueStatusText", "Briefing / 1 of 5", 12, MUTED, True)
    controls = await widget(bp, unreal.HorizontalBox, "DialogueControls", content)
    await button(bp, controls, "ContinueButton", "Continue")
    await button(bp, controls, "DialogueResetButton", "Restart preview")
    await label(bp, content, "DialogueScope", "Simulated dialogue only. No mission progress or player input locks.", 11, MUTED)
    compile_blueprint(bp)
    show = new_function(bp, "ShowPreviewLine")
    show.add_graph_input_parameter("LineIndex", unreal.BlueprintEditorLibrary.get_basic_type_by_name("int"))
    add_var(show, "NextLineIndex", "int", 1)
    add_var(show, "CurrentLineIndex", "int", 0)
    start = show.find_graph_entry_pin()
    index_pin = start.get_owning_node().find_output_pin("LineIndex")
    speakers = {"System": "Department of Continuity", "FutureSelf": "Future Self", "Agent": "Agent", "Supervisor": "Supervisor", "Jack": "Jack"}
    for index, row in enumerate(rows):
        yes, start = branch(show, start, compare(show, "EqualEqual_IntInt", index_pin, index))
        next_index = by_name.get(row["NextRow"], -1)
        yes = assign(show, yes, "CurrentLineIndex", index)
        yes = assign(show, yes, "NextLineIndex", next_index)
        yes = text_action(show, yes, "SpeakerText", speakers.get(row["Speaker"], row["Speaker"]))
        yes = text_action(show, yes, "DialogueBodyText", row["Text"])
        status = "End of preview" if next_index < 0 else "Continue to the next line"
        yes = text_action(show, yes, "DialogueStatusText", status)
        action(show, yes, "ContinueButton", "Widget:SetIsEnabled", "bInIsEnabled", next_index >= 0)
    text_action(show, start, "DialogueStatusText", "End of preview")
    reset = new_function(bp, "ResetDialoguePreview")
    compile_blueprint(bp)
    invoke(reset, reset.find_graph_entry_pin(), bp, "ShowPreviewLine", LineIndex=0)
    advance = new_function(bp, "AdvanceDialoguePreview")
    invoke(advance, advance.find_graph_entry_pin(), bp, "ShowPreviewLine", LineIndex=get(advance, "NextLineIndex"))
    compile_blueprint(bp)
    for name, caption, row in samples:
        await bind(bp, name, "ShowPreviewLine", LineIndex=by_name[row])
    await bind(bp, "ContinueButton", "AdvanceDialoguePreview")
    await bind(bp, "DialogueResetButton", "ResetDialoguePreview")
    construct(bp, "ResetDialoguePreview")
    layout_graphs(bp)

async def build_checklist(bp, cases):
    content = await panel(bp)
    await label(bp, content, "ChecklistEyebrow", "02 / CHECKLIST PREVIEW", 12, GOLD)
    await label(bp, content, "ChecklistTitle", "DEPARTMENT OF CONTINUITY", 21)
    await label(bp, content, "ChecklistSubtitle", "OPERATION 1888", 14, CYAN, True)
    await label(bp, content, "ChecklistHint", "Complete simulated objectives, then inspect the Director's revised orders.", 13, MUTED)
    for index in range(4):
        row = await label(bp, content, "ObjectiveText" + str(index), "[ ] " + (cases[0][index] if index < 3 else cases[1][3]), 17, PAPER, True)
        if index == 3:
            row.set_visibility(unreal.SlateVisibility.COLLAPSED)
    await label(bp, content, "ChecklistStatusText", "0 / 3 objectives complete", 12, CYAN, True)
    controls = await widget(bp, unreal.HorizontalBox, "ChecklistControls", content)
    await button(bp, controls, "CompleteButton", "Complete next")
    await button(bp, controls, "RewriteButton", "Rewrite orders")
    controls_b = await widget(bp, unreal.HorizontalBox, "ChecklistControlsB", content)
    await button(bp, controls_b, "ChecklistResetButton", "Reset initial orders")
    await label(bp, content, "ChecklistContextText", "Initial assignment: find Jack, protect him, keep his identity secret.", 13, MUTED, True)
    await label(bp, content, "ChecklistScope", "Rewritten orders expose the manipulation. They do not choose the final dossier.", 11, MUTED)
    compile_blueprint(bp)
    refresh = new_function(bp, "RefreshChecklistPreview")
    add_var(refresh, "CompletedCount", "int", 0)
    add_var(refresh, "IsRewritten", "bool", "false")
    rewritten, original = branch(refresh, refresh.find_graph_entry_pin(), get(refresh, "IsRewritten"))
    for mode, start in [(0, original), (1, rewritten)]:
        items = cases[mode]
        start = text_action(refresh, start, "ChecklistSubtitle", "OPERATION 1888 - UPDATE" if mode else "OPERATION 1888")
        start = action(refresh, start, "ObjectiveText3", "Widget:SetVisibility", "InVisibility", "Visible" if mode else "Collapsed")
        start = text_action(refresh, start, "ChecklistContextText", "The Director is manufacturing a culprit. These are the Department's orders, not the truth." if mode else "Initial assignment: find Jack, protect him, keep his identity secret.")
        for index, item in enumerate(items):
            done, pending = branch(refresh, start, compare(refresh, "Greater_IntInt", get(refresh, "CompletedCount"), index))
            done = text_action(refresh, done, "ObjectiveText" + str(index), "[x] " + item)
            pending = text_action(refresh, pending, "ObjectiveText" + str(index), "[ ] " + item)
            # Both mutually exclusive branches continue into the next row.
            join = call(refresh, "/Script/UMG.Widget:SetIsEnabled")
            connect(done, join.find_execute_pin())
            connect(pending, join.find_execute_pin())
            connect(get(refresh, "CompleteButton"), join.find_self_pin())
            literal(join.find_input_pin("bInIsEnabled"), True)
            start = join.find_then_pin()
        # Match the CSV masks initially; clamp completion at the number of visible entries.
        all_done, active = branch(refresh, start, compare(refresh, "GreaterEqual_IntInt", get(refresh, "CompletedCount"), len(items)))
        all_done = text_action(refresh, all_done, "ChecklistStatusText", str(len(items)) + " / " + str(len(items)) + " objectives complete")
        action(refresh, all_done, "CompleteButton", "Widget:SetIsEnabled", "bInIsEnabled", False)
        # Show each partial count without exposing internal enum or asset names.
        for count in range(len(items)):
            yes, active = branch(refresh, active, compare(refresh, "EqualEqual_IntInt", get(refresh, "CompletedCount"), count))
            text_action(refresh, yes, "ChecklistStatusText", str(count) + " / " + str(len(items)) + " objectives complete")
    reset = new_function(bp, "ResetChecklistPreview")
    start = assign(reset, reset.find_graph_entry_pin(), "IsRewritten", False)
    start = assign(reset, start, "CompletedCount", 0)
    rewrite = new_function(bp, "RewriteChecklistPreview")
    start_rewrite = assign(rewrite, rewrite.find_graph_entry_pin(), "IsRewritten", True)
    start_rewrite = assign(rewrite, start_rewrite, "CompletedCount", 2)
    complete = new_function(bp, "CompleteNextPreviewObjective")
    add = call(complete, "/Script/Engine.KismetMathLibrary:Add_IntInt")
    connect(get(complete, "CompletedCount"), add.find_input_pin("A"))
    literal(add.find_input_pin("B"), 1)
    start_complete = assign(complete, complete.find_graph_entry_pin(), "CompletedCount", add.find_result_pin())
    compile_blueprint(bp)
    invoke(reset, start, bp, "RefreshChecklistPreview")
    invoke(rewrite, start_rewrite, bp, "RefreshChecklistPreview")
    invoke(complete, start_complete, bp, "RefreshChecklistPreview")
    compile_blueprint(bp)
    await bind(bp, "CompleteButton", "CompleteNextPreviewObjective")
    await bind(bp, "RewriteButton", "RewriteChecklistPreview")
    await bind(bp, "ChecklistResetButton", "ResetChecklistPreview")
    construct(bp, "ResetChecklistPreview")
    layout_graphs(bp)

async def build_launcher(bp, dialogue, checklist):
    root = await widget(bp, unreal.Border, "LabBackground")
    root.set_brush_color(INK)
    root.set_padding(unreal.Margin(18))
    scroll = await widget(bp, unreal.ScrollBox, "LabScroll", root)
    column = await widget(bp, unreal.VerticalBox, "LabContent", scroll)
    await label(bp, column, "LabTitle", "UNSCRIPTED / NARRATIVE LAB", 24, GOLD)
    await label(bp, column, "LabScope", "Division C - isolated F0 prototypes - simulated data", 12, MUTED)
    await label(bp, column, "LabMotto", "History belongs not to those who lived it, but to those who decide how it is told.", 14, PAPER)
    await widget(bp, dialogue.generated_class(), "DialoguePreview", column, True)
    await widget(bp, checklist.generated_class(), "ChecklistPreview", column, True)
    await label(bp, column, "LabFooter", "Presentation test only. No story transitions, gameplay systems, or shared maps are changed.", 12, MUTED)

async def build():
    global preview_assets, c_preview_widget
    rows = list(csv.DictReader((SOURCE / "DT_Dialogue.csv").open(encoding="utf-8-sig", newline="")))
    checklist = {r["Name"]: r for r in csv.DictReader((SOURCE / "DT_Checklist.csv").open(encoding="utf-8-sig", newline=""))}
    cases = [json.loads("[" + checklist[key]["Items"][1:-1] + "]") for key in ("FindJack", "FinalChoice")]
    assert len(rows) == 24 and [len(c) for c in cases] == [3, 4]
    existing_launcher = unreal.load_asset(UI_ROOT + "/" + NAMES[2])
    if existing_launcher:
        subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        subsystem.close_tab_by_id(subsystem.get_tab_id_from_blueprint(existing_launcher))
    preview_assets = [await create_blueprint(name, index == 2) for index, name in enumerate(NAMES)]
    dialogue, checklist_bp, launcher = preview_assets
    await build_dialogue(dialogue, rows)
    compile_blueprint(dialogue, warnings_as_errors=True)
    print("C_UI_DIALOGUE_COMPILED", len(rows))
    await build_checklist(checklist_bp, cases)
    compile_blueprint(checklist_bp, warnings_as_errors=True)
    print("C_UI_CHECKLIST_COMPILED")
    await build_launcher(launcher, dialogue, checklist_bp)
    for bp in preview_assets:
        compile_blueprint(bp, warnings_as_errors=True)
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
        print("C_UI_SAVED", bp.get_path_name())
    c_preview_widget = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem).spawn_and_register_tab(launcher)
    print("C_UI_BUILD_COMPLETE", c_preview_widget)
async def guarded_build():
    try:
        await build()
    except Exception:
        unreal.log_error("C_UI_BUILD_FAILED " + traceback.format_exc())
c_preview_loop = EditorEventLoopManager()
c_preview_loop.__enter__()
c_preview_task = c_preview_loop.loop.create_task(guarded_build())

