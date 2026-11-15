"""Presentation-only styling for the three existing Division C preview assets.
No graphs, variables, event handlers, dialogue data or gameplay state are edited.
"""
import unreal
import hashlib
import json
import traceback
from pathlib import Path
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
from editor_toolset.toolsets.blueprint import BlueprintTools
from toolset_registry.helpers import compile_blueprint

ROOT = "/Game/Unscripted/UI/Test/"
NAMES = ("WBP_DialoguePrototype_C", "WBP_ChecklistPrototype_C", "EUW_NarrativeTestLauncher_C")
REPORT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent / "Scripts/C/ui_style_validation.json"

def color(code):
    code = code.lstrip("#")
    values = [int(code[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values]
    return unreal.LinearColor(*linear, 1)
BG, CARD, FIELD = color("101315"), color("1B2023"), color("131719")
TEXT, MUTED, GOLD, CYAN = color("EEE8DC"), color("A9ACA7"), color("C5A46D"), color("8AB9B1")
EDGE = color("49463E")
WHITE = unreal.LinearColor(1, 1, 1, 1)
def ref(obj):
    return {"refPath": obj.get_path_name()}
async def umg(name, **args):
    return await execute_tool("UMGToolSet.UMGToolSet", name, args)
def resolve(value):
    return unreal.find_object(None, value["refPath"])
def fingerprint(bp):
    graphs = []
    count = 0
    for graph in BlueprintTools.list_graphs(bp):
        nodes = []
        for node in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
            count += 1
            pins = []
            for pin in node.list_all_pins():
                links = sorted((p.get_owning_node().get_name(), str(p.get_pin_name())) for p in pin.list_connected_pins())
                pins.append((str(pin.get_pin_name()), str(pin.get_pin_direction()), pin.get_pin_value(), links))
            nodes.append((node.get_name(), node.get_class().get_path_name(), pins))
        graphs.append((graph.get_name(), sorted(nodes)))
    defaults = {}
    cdo = unreal.get_default_object(bp.generated_class())
    for name in ("NextLineIndex", "CurrentLineIndex", "CompletedCount", "IsRewritten"):
        try:
            defaults[name] = cdo.get_editor_property(name)
        except Exception:
            pass
    data = json.dumps({"graphs": sorted(graphs), "primitive_defaults": defaults}, sort_keys=True)
    return {"sha256": hashlib.sha256(data.encode()).hexdigest(), "node_count": count, "graph_count": len(graphs), "primitive_defaults": defaults}
async def tree(bp):
    info = (await umg("GetWidgets", widgetBlueprint=ref(bp)))["returnValue"]
    return {i["widgetName"]: resolve(i["widget"]) for i in info["widgets"]}
async def add(bp, cls, name, parent, index=-1):
    widgets = await tree(bp)
    if name in widgets:
        return widgets[name]
    result = await umg("AddWidget", widgetBlueprint=ref(bp), widgetClass=ref(cls.static_class()), widgetDisplayName=name, parentWidget=ref(parent), childIndex=index)
    return resolve(result["returnValue"]["widget"])
async def move(bp, widget, parent, index=-1):
    if widget.get_parent() == parent:
        return
    await umg("MoveWidget", widgetBlueprint=ref(bp), widget=ref(widget), newParent=ref(parent), childIndex=index)
def margin(widget, left=0, top=0, right=0, bottom=0):
    slot = widget.get_editor_property("slot")
    if slot and hasattr(slot, "set_padding"):
        slot.set_padding(unreal.Margin(left, top, right, bottom))
def brush(background, edge=None, radius=3):
    outline = unreal.SlateBrushOutlineSettings(
        corner_radii=unreal.Vector4(radius, radius, radius, radius),
        color=unreal.SlateColor(specified_color=edge or background),
        width=1.0 if edge is not None else 0.0,
        rounding_type=unreal.SlateBrushRoundingType.FIXED_RADIUS)
    return unreal.SlateBrush(draw_as=unreal.SlateBrushDrawType.ROUNDED_BOX, tint_color=unreal.SlateColor(specified_color=background), outline_settings=outline)
def border(widget, background, edge=None, padding=0, radius=3):
    widget.set_brush(brush(background, edge, radius))
    widget.set_brush_color(WHITE)
    widget.set_padding(unreal.Margin(padding, padding, padding, padding))
def font(widget, size=13, weight="Regular", tint=None, tracking=0):
    info = widget.get_editor_property("font")
    info.set_editor_property("size", size)
    info.set_editor_property("typeface_font_name", weight)
    info.set_editor_property("letter_spacing", tracking)
    widget.set_font(info)
    widget.set_color_and_opacity(unreal.SlateColor(specified_color=tint or TEXT))
    widget.set_auto_wrap_text(True)
    widget.set_editor_property("justification", unreal.TextJustify.LEFT)
def button(widget, label_widget, primary=False):
    style = widget.get_editor_property("widget_style")
    style.set_editor_property("normal", brush(color("80643D") if primary else color("262D30"), GOLD if primary else color("4D5553"), 3))
    style.set_editor_property("hovered", brush(color("9B7A49") if primary else color("35403F"), GOLD, 3))
    style.set_editor_property("pressed", brush(color("675033") if primary else color("172022"), CYAN, 3))
    style.set_editor_property("disabled", brush(color("1B2022"), color("303735"), 3))
    for key in ("normal_foreground", "hovered_foreground", "pressed_foreground"):
        style.set_editor_property(key, unreal.SlateColor(specified_color=TEXT))
    style.set_editor_property("disabled_foreground", unreal.SlateColor(specified_color=MUTED))
    style.set_editor_property("normal_padding", unreal.Margin(12, 9, 12, 9))
    style.set_editor_property("pressed_padding", unreal.Margin(12, 10, 12, 8))
    widget.set_style(style)
    widget.set_background_color(WHITE)
    widget.set_color_and_opacity(WHITE)
    font(label_widget, 11, "Medium")
    label_widget.set_editor_property("justification", unreal.TextJustify.CENTER)
    label_widget.set_auto_wrap_text(False)
    slot = label_widget.get_editor_property("slot")
    slot.set_padding(unreal.Margin(0))
    slot.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_CENTER)
    slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
    own_slot = widget.get_editor_property("slot")
    if isinstance(own_slot, unreal.HorizontalBoxSlot):
        own_slot.set_size(unreal.SlateChildSize(value=1.0, size_rule=unreal.SlateSizeRule.FILL))
        own_slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_FILL)
        own_slot.set_padding(unreal.Margin(0, 0, 8, 0))
def style_buttons(widgets):
    for name, widget in widgets.items():
        if isinstance(widget, unreal.Button):
            label = widgets.get(name + "Label")
            if label is not None:
                button(widget, label, name in ("ContinueButton", "CompleteButton"))
    for name in ("SceneSelectorsA", "SceneSelectorsB", "DialogueControls", "ChecklistControls", "ChecklistControlsB"):
        row = widgets.get(name)
        if row and row.get_children_count():
            margin(row.get_child_at(row.get_children_count() - 1), 0, 0, 0, 0)
async def rule(bp, name, parent, index):
    box = await add(bp, unreal.SizeBox, name + "Size", parent, index)
    box.set_height_override(1)
    line = await add(bp, unreal.Border, name, box)
    border(line, EDGE, padding=0, radius=0)
    margin(box, 0, 6, 0, 16)
async def style_dialogue(bp):
    w = await tree(bp)
    border(w["PreviewPanel"], CARD, EDGE, 24, 5)
    for name, value in [(n, x) for n, x in w.items() if isinstance(x, unreal.TextBlock)]:
        font(value, 13)
        margin(value, 0, 0, 0, 10)
    font(w["DialogueEyebrow"], 10, "Medium", GOLD, 140)
    font(w["DialogueHeading"], 25, "Light")
    font(w["DialogueHint"], 12, "Regular", MUTED)
    font(w["SpeakerText"], 11, "Medium", CYAN, 55)
    font(w["DialogueBodyText"], 17, "Regular")
    font(w["DialogueStatusText"], 11, "Regular", CYAN)
    font(w["DialogueScope"], 10, "Regular", MUTED)
    margin(w["DialogueEyebrow"], bottom=9)
    margin(w["DialogueHeading"], bottom=2)
    margin(w["DialogueHint"], bottom=16)
    margin(w["SceneSelectorsA"], bottom=8)
    margin(w["SceneSelectorsB"], bottom=0)
    margin(w["SpeakerText"], bottom=12)
    margin(w["DialogueBodyText"], bottom=0)
    margin(w["DialogueStatusText"], bottom=12)
    margin(w["DialogueControls"], bottom=14)
    margin(w["DialogueScope"], bottom=0)
    await rule(bp, "DialogueHeaderRule", w["PreviewContent"], 2)
    frame = await add(bp, unreal.Border, "DialogueReadingFrame", w["PreviewContent"], 6)
    border(frame, FIELD, color("343B3B"), 16, 3)
    content = await add(bp, unreal.VerticalBox, "DialogueReadingContent", frame)
    await move(bp, w["SpeakerText"], content)
    await move(bp, w["DialogueBodyArea"], content)
    margin(w["SpeakerText"], bottom=12)
    w["DialogueBodyArea"].set_min_desired_height(128)
    margin(frame, 0, 18, 0, 14)
    style_buttons(w)
async def style_checklist(bp):
    w = await tree(bp)
    border(w["PreviewPanel"], CARD, EDGE, 24, 5)
    for name, value in [(n, x) for n, x in w.items() if isinstance(x, unreal.TextBlock)]:
        font(value, 13)
        margin(value, 0, 0, 0, 10)
    font(w["ChecklistEyebrow"], 10, "Medium", GOLD, 140)
    font(w["ChecklistTitle"], 17, "Medium", TEXT, 20)
    font(w["ChecklistSubtitle"], 11, "Medium", CYAN, 80)
    font(w["ChecklistHint"], 12, "Regular", MUTED)
    font(w["ChecklistStatusText"], 11, "Medium", CYAN)
    font(w["ChecklistContextText"], 12, "Regular", MUTED)
    font(w["ChecklistScope"], 10, "Regular", MUTED)
    margin(w["ChecklistEyebrow"], bottom=9)
    margin(w["ChecklistTitle"], bottom=10)
    margin(w["ChecklistSubtitle"], bottom=2)
    margin(w["ChecklistHint"], bottom=16)
    margin(w["ChecklistStatusText"], bottom=14)
    margin(w["ChecklistControls"], bottom=8)
    margin(w["ChecklistControlsB"], bottom=16)
    margin(w["ChecklistScope"], bottom=0)
    await rule(bp, "ChecklistHeaderRule", w["PreviewContent"], 3)
    frame = await add(bp, unreal.Border, "ChecklistOrdersFrame", w["PreviewContent"], 5)
    border(frame, FIELD, color("343B3B"), 16, 3)
    content = await add(bp, unreal.VerticalBox, "ChecklistOrdersContent", frame)
    for index in range(4):
        row = w["ObjectiveText" + str(index)]
        await move(bp, row, content)
        font(row, 15, "Regular")
        margin(row, 0, 0, 0, 12 if index < 2 else 8)
    margin(frame, 0, 0, 0, 16)
    context = await add(bp, unreal.Border, "ChecklistContextFrame", w["PreviewContent"], 10)
    border(context, color("242622"), color("444638"), 12, 3)
    await move(bp, w["ChecklistContextText"], context)
    margin(w["ChecklistContextText"], bottom=0)
    margin(context, bottom=14)
    style_buttons(w)
async def style_launcher(bp):
    w = await tree(bp)
    border(w["LabBackground"], BG, padding=28, radius=0)
    font(w["LabTitle"], 28, "Light", TEXT, 90)
    font(w["LabScope"], 10, "Medium", GOLD, 65)
    font(w["LabMotto"], 13, "Italic", MUTED)
    font(w["LabFooter"], 10, "Regular", MUTED)
    margin(w["LabTitle"], bottom=10)
    margin(w["LabScope"], bottom=10)
    margin(w["LabMotto"], bottom=0)
    margin(w["LabFooter"], top=18, bottom=2)
    header = await add(bp, unreal.Border, "LabHeader", w["LabContent"], 0)
    border(header, BG, padding=0, radius=0)
    content = await add(bp, unreal.VerticalBox, "LabHeaderContent", header)
    for name in ("LabTitle", "LabScope", "LabMotto"):
        await move(bp, w[name], content)
    margin(w["LabTitle"], bottom=10)
    margin(w["LabScope"], bottom=10)
    margin(w["LabMotto"], bottom=0)
    margin(header, 0, 0, 0, 24)
    columns = await add(bp, unreal.HorizontalBox, "LabPreviewColumns", w["LabContent"], 1)
    for index, name in enumerate(("DialoguePreview", "ChecklistPreview")):
        await move(bp, w[name], columns)
        slot = w[name].get_editor_property("slot")
        slot.set_size(unreal.SlateChildSize(value=0.54 if index == 0 else 0.46, size_rule=unreal.SlateSizeRule.FILL))
        slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_FILL)
        slot.set_padding(unreal.Margin(0 if index == 0 else 10, 0, 10 if index == 0 else 0, 0))
    margin(columns, bottom=0)

async def apply_style():
    global c_preview_widget, c_style_report
    assets = [unreal.load_asset(ROOT + name) for name in NAMES]
    assert all(assets), "Only the three existing prototypes can be styled."
    before = {bp.get_name(): fingerprint(bp) for bp in assets}
    original_names = {bp.get_name(): set((await tree(bp)).keys()) for bp in assets}
    subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
    subsystem.close_tab_by_id(subsystem.get_tab_id_from_blueprint(assets[2]))
    await style_dialogue(assets[0])
    await style_checklist(assets[1])
    for bp in assets[:2]:
        compile_blueprint(bp, warnings_as_errors=True)
    await style_launcher(assets[2])
    after = {}
    for bp in assets:
        compile_blueprint(bp, warnings_as_errors=True)
        after[bp.get_name()] = fingerprint(bp)
        assert before[bp.get_name()] == after[bp.get_name()], "Graph or primitive default changed: " + bp.get_name()
        assert original_names[bp.get_name()].issubset((await tree(bp)).keys()), "An original widget is missing"
    for bp in assets:
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    c_style_report = {"passed": True, "scope": [ROOT + name for name in NAMES], "logic_unchanged": before == after, "before": before, "after": after, "compile": "All three up to date without warnings", "save": "All three saved explicitly", "presentation": ["Charcoal, brass, ivory and muted cyan", "Two separate preview cards in adjacent columns", "Consistent control sizing, padding, alignment and interaction states", "Dedicated reading and orders panels", "Existing narrative text preserved"]}
    REPORT.write_text(json.dumps(c_style_report, indent=2), encoding="utf-8")
    c_preview_widget = subsystem.spawn_and_register_tab(assets[2])
    print("C_STYLE_COMPLETE", json.dumps(c_style_report))
async def guard_style():
    try:
        await apply_style()
    except Exception:
        unreal.log_error("C_STYLE_FAILED " + traceback.format_exc())
c_style_loop = EditorEventLoopManager()
c_style_loop.__enter__()
c_style_task = c_style_loop.loop.create_task(guard_style())

