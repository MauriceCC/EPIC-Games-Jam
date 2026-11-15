"""Native UMG construction helpers. Existing F0 previews are never rebuilt."""
import unreal
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
import blueprint_helpers_c as h
INK=unreal.LinearColor(0.032,0.045,0.064,1)
PANEL=unreal.LinearColor(0.055,0.075,0.1,0.97)
PAPER=unreal.LinearColor(0.88,0.91,0.91,1)
GOLD=unreal.LinearColor(0.82,0.63,0.31,1)
MUTED=unreal.LinearColor(0.48,0.60,0.66,1)
CYAN=unreal.LinearColor(0.34,0.82,0.78,1)
def ref(obj):return {"refPath":obj.get_path_name()}
async def tool(name,**args):return await execute_tool("UMGToolSet.UMGToolSet",name,args)
async def widget(bp,cls,name,parent=None,variable=False):
    existing=unreal.find_object(None,bp.get_path_name()+":WidgetTree."+name)
    if existing:return existing
    args={"widgetBlueprint":ref(bp),"widgetClass":ref(cls if isinstance(cls,unreal.Class) else cls.static_class()),"widgetDisplayName":name}
    if parent is not None:args["parentWidget"]=ref(parent)
    result=(await tool("AddWidget",**args))["returnValue"]
    obj=unreal.find_object(None,result["widget"]["refPath"]);assert obj,name
    if variable:await tool("ToggleWidgetAsVariable",widgetBlueprint=ref(bp),widget=ref(obj),bIsVariable=True)
    return obj
async def create(name):
    assert name in ("WBP_Document","WBP_Dialogue","WBP_Checklist","WBP_HUD")
    existing=unreal.load_asset("/Game/Unscripted/UI/"+name)
    if existing:return existing
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,"/Game/Unscripted/UI",unreal.WidgetBlueprint,unreal.WidgetBlueprintFactory())
async def label(bp,parent,name,text,size=16,color=PAPER,variable=False):
    obj=await widget(bp,unreal.TextBlock,name,parent,variable)
    obj.set_text(text);obj.set_auto_wrap_text(True);obj.set_color_and_opacity(unreal.SlateColor(specified_color=color))
    font=obj.get_editor_property("font");font.set_editor_property("size",size);obj.set_font(font)
    slot=obj.get_editor_property("slot")
    if slot and hasattr(slot,"set_padding"):slot.set_padding(unreal.Margin(0,0,0,9))
    return obj
async def button(bp,parent,name,text):
    obj=await widget(bp,unreal.Button,name,parent,True)
    obj.set_background_color(unreal.LinearColor(0.11,0.18,0.22,1))
    await label(bp,obj,name+"Label",text,14)
    obj.set_editor_property("is_focusable",False)
    return obj
async def panel(bp,name="Panel",parent=None):
    root=await widget(bp,unreal.Border,name,parent,True)
    root.set_brush_color(PANEL);root.set_padding(unreal.Margin(22))
    return root,await widget(bp,unreal.VerticalBox,name+"Content",root)
async def bind(bp,button,function,**args):
    g=h.edit(bp,"EventGraph");before={n.get_path_name() for n in g.list_all_nodes()}
    result=await tool("BindToEventProperty",widgetBlueprint=ref(bp),eventName="OnClicked",propertyName=button,propertyClass=ref(unreal.Button.static_class()))
    assert result["returnValue"]
    event=next(n for n in g.list_all_nodes() if n.get_path_name() not in before)
    h.invoke(g,event.find_then_pin(),bp,function,**args)
def set_text(g,start,widget,text):return h.call(g,"/Script/UMG.TextBlock:SetText",start,h.get(g,widget),InText=text).find_then_pin()
def visibility(g,start,target,value):return h.call(g,"/Script/UMG.Widget:SetVisibility",start,target,InVisibility=value).find_then_pin()
def place(widget,x,y,width,height,anchor=(0,0),align=(0,0)):
    slot=widget.get_editor_property("slot")
    slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(*anchor),maximum=unreal.Vector2D(*anchor)))
    slot.set_alignment(unreal.Vector2D(*align));slot.set_position(unreal.Vector2D(x,y));slot.set_size(unreal.Vector2D(width,height))
    return slot
