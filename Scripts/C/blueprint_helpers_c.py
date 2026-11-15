"""Reusable native Blueprint graph helpers for Division C editor scripts."""
import unreal
from toolset_registry.helpers import compile_blueprint
ROOT="/Game/Unscripted/"
ACTION_CACHE={}
def asset(path):
    obj=unreal.load_asset(path if path.startswith("/") else ROOT+path)
    assert obj,path
    return obj
def obj_type(cls):return unreal.BlueprintEditorLibrary.get_object_reference_type(cls if isinstance(cls,unreal.Class) else cls.static_class())
def basic(name):return unreal.BlueprintEditorLibrary.get_basic_type_by_name(name)
def enum_type(name):
    e=asset("Core/Enums/"+name);t=unreal.EdGraphPinType()
    assert t.import_text('(PinCategory="byte",PinSubCategoryObject="'+e.get_path_name()+'")')
    return t
def array_type(t):
    out=unreal.EdGraphPinType()
    assert out.import_text(t.export_text().replace("ContainerType=None","ContainerType=Array"))
    return out
def edit(bp,name):
    found=next((x for x in unreal.BlueprintEditorLibrary.list_graphs(bp) if x.get_name()==name),None)
    return unreal.BlueprintGraphEditor.get_graph_editor(found) if found else None
def function(bp,name,inputs=(),outputs=(),private=False,replace=False):
    old=edit(bp,name)
    if old:
        assert replace,"Preserve authored function "+bp.get_name()+"."+name
        unreal.BlueprintEditorLibrary.remove_graph(bp,old.get_graph())
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,name)
    for n,t in inputs:
        p=g.add_graph_input_parameter(n,t)
        assert str(p.get_pin_name())==n,(name,n,str(p.get_pin_name()))
    for n,t in outputs:g.add_graph_output_parameter(n,t)
    if private:g.set_function_is_private()
    return g
def variable(bp,name,typ,default="",editable=False,category="Narrative"):
    if unreal.BlueprintEditorLibrary.get_member_variable_type(bp,name) is None:
        g=unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp))
        assert g.add_member_variable(name,typ,"true" if default is True else "false" if default is False else str(default)),name
    unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,name,editable)
    unreal.BlueprintEditorLibrary.set_blueprint_variable_category(bp,name,category)
def valid(p):return p is not None and p.is_valid()
def connect(a,b):
    assert valid(a) and valid(b),(str(a),str(b))
    if any(p.is_same_native_pin(b) for p in a.list_connected_pins()):return
    assert a.try_create_connection(b),(str(a.get_pin_name()),a.get_pin_type().export_text(),str(b.get_pin_name()),b.get_pin_type().export_text())
def literal(pin,value):
    assert valid(pin)
    v="" if value is None else "true" if value is True else "false" if value is False else str(value)
    assert pin.set_pin_value(v),(str(pin.get_pin_name()),v)
def value(pin,item):
    if isinstance(item,unreal.BlueprintGraphPin):connect(item,pin)
    else:literal(pin,item)
def get(g,name,target=None,cls=None):
    n=g.add_get_member_variable_node(name,cls.get_path_name() if cls else "")
    if target is not None:connect(target,n.find_self_pin())
    return n.find_result_pin()
def setvar(g,start,name,item,target=None,cls=None):
    n=g.add_set_member_variable_node(name,cls.get_path_name() if cls else "")
    connect(start,n.find_execute_pin())
    if target is not None:connect(target,n.find_self_pin())
    value(n.find_input_pin(name),item)
    return n.find_then_pin()
def param(g,name):return g.find_graph_entry_pin().get_owning_node().find_output_pin(name)
def call(g,path,start=None,target=None,**args):
    assert unreal.load_object(None,path),path
    n=g.add_call_function_node(path)
    if start is not None:connect(start,n.find_execute_pin())
    if target is not None:connect(target,n.find_self_pin())
    for key,item in args.items():value(n.find_input_pin(key),item)
    return n
def invoke(g,start,bp,name,target=None,**args):return call(g,bp.generated_class().get_path_name()+":"+name,start,target,**args)
def math(g,name,*args):
    n=call(g,"/Script/Engine.KismetMathLibrary:"+name)
    pins=[p for p in n.list_input_pins() if str(p.get_pin_name())!="self"]
    assert len(args)<=len(pins),name
    # Promotable operators resolve wildcard types from connected data first.
    for p,v in zip(pins,args):
        if isinstance(v,unreal.BlueprintGraphPin):value(p,v)
    for p,v in zip(pins,args):
        if not isinstance(v,unreal.BlueprintGraphPin):value(p,v)
    return n.find_result_pin()
def all_true(g,*args):
    out=args[0]
    for item in args[1:]:out=math(g,"BooleanAND",out,item)
    return out
def any_true(g,*args):
    out=args[0]
    for item in args[1:]:out=math(g,"BooleanOR",out,item)
    return out
def not_(g,item):return math(g,"Not_PreBool",item)
def is_valid(g,item):return call(g,"/Script/Engine.KismetSystemLibrary:IsValid",Object=item).find_result_pin()
def branch(g,start,condition):
    n=g.add_branch_node();connect(start,n.find_execute_pin());value(n.find_input_pin("Condition"),condition)
    return n.find_output_pin("then"),n.find_output_pin("else")
def result(g,start=None,**outputs):
    nodes=[n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_FunctionResult"]
    n=nodes[0] if len(nodes)==1 and not nodes[0].find_execute_pin().list_connected_pins() else g.add_return_node()
    if start is not None:connect(start,n.find_execute_pin())
    for key,item in outputs.items():value(n.find_input_pin(key),item)
    return n
def self_pin(g):
    options=actions(g)
    key=next(x for x in options if x.startswith("Variables|") and ("mismo" in x.lower() or "referencetoself" in x.lower().replace(" ","")))
    return g.create_node_from_name(key,unreal.Vector2D(0,0),[]).find_result_pin()
def actions(g,pins=None):
    # Cache unfiltered menus only; typed context menus depend on their pin instances.
    if pins is not None:return [str(a) for a in g.list_available_nodes(pins)]
    key=g.get_graph().get_path_name()
    if key not in ACTION_CACHE:ACTION_CACHE[key]=[str(a) for a in g.list_available_nodes([])]
    return ACTION_CACHE[key]
def message(g,start,name,target,**args):
    options=actions(g,[target])
    key=next(x for x in options if x.endswith("|"+name+"(Mensaje)") or x.endswith("|"+name+"(Message)"))
    n=g.create_node_from_name(key,unreal.Vector2D(0,0),[target])
    if not n.find_self_pin().list_connected_pins():connect(target,n.find_self_pin())
    if start is not None:connect(start,n.find_execute_pin())
    for k,v in args.items():value(n.find_input_pin(k),v)
    return n
def emit(g,start,name,**args):
    key=next(x for x in actions(g) if x.endswith("|Call"+name))
    n=g.create_node_from_name(key,unreal.Vector2D(0,0),[])
    connect(start,n.find_execute_pin())
    for k,v in args.items():value(n.find_input_pin(k),v)
    return n.find_then_pin()

def emit_to(g,start,target,name,**args):
    key=next(x for x in actions(g,[target]) if x.endswith("|Call"+name))
    n=g.create_node_from_name(key,unreal.Vector2D(0,0),[target])
    if not n.find_self_pin().list_connected_pins():connect(target,n.find_self_pin())
    connect(start,n.find_execute_pin())
    for k,v in args.items():value(n.find_input_pin(k),v)
    return n.find_then_pin()
def foreach(g,start,array):
    n=g.add_macro_node("/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:ForEachLoop")
    assert n
    connect(array,n.find_input_pin("Array"));connect(start,n.find_input_pin("Exec"))
    return n.find_output_pin("LoopBody"),n.find_output_pin("Array Element"),n.find_output_pin("Completed")
def override(bp,name):
    g=edit(bp,name)
    if g:return g
    graph=unreal.BlueprintEditorLibrary.add_function_override(bp,name)
    assert graph,(bp.get_name(),name)
    return unreal.BlueprintGraphEditor.get_graph_editor(graph)
def event(bp,name):
    n=unreal.BlueprintEditorLibrary.add_event_override(bp,name,unreal.IntPoint(0,0));assert n,name
    return unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp)),n
def layout(bp,names=None):
    for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
        if names is not None and graph.get_name() not in names:continue
        g=unreal.BlueprintGraphEditor.get_graph_editor(graph)
        for i,n in enumerate(g.list_all_nodes()):n.set_node_pos(unreal.IntPoint((i%7)*350,(i//7)*230))
def save(*bps):
    for bp in bps:
        compile_blueprint(bp,warnings_as_errors=True)
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False),bp.get_path_name()
def create_actor_bp(folder,name,parent=unreal.Actor):
    path=ROOT+folder+"/"+name
    assert not unreal.EditorAssetLibrary.does_asset_exist(path),"Preserve existing asset "+path
    f=unreal.BlueprintFactory();f.set_editor_property("parent_class",parent)
    bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,ROOT+folder,unreal.Blueprint,f)
    assert bp,path
    return bp

def add_component(bp,name,cls,parent=None):
    subsystem=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    data=unreal.SubobjectDataBlueprintFunctionLibrary
    handles=subsystem.k2_gather_subobject_data_for_blueprint(bp)
    existing=next((x for x in handles if str(data.get_variable_name(data.get_data(x)))==name),None)
    if existing:return data.get_object(data.get_data(existing))
    params=unreal.AddNewSubobjectParams(parent_handle=parent or handles[0],new_class=cls if isinstance(cls,unreal.Class) else cls.static_class(),blueprint_context=bp)
    handle,reason=subsystem.add_new_subobject(params)
    assert data.is_handle_valid(handle),str(reason)
    assert subsystem.rename_subobject(handle,name)
    return data.get_object(data.get_data(handle))
def cast(g,start,target,cls):
    name=cls.get_name().removesuffix("_C").replace("_","")
    choices=actions(g,[target])
    key=next(x for x in choices if x.split("|")[-1].replace("_","").lower()=="castto"+name.lower())
    n=g.create_node_from_name(key,unreal.Vector2D(0,0),[target])
    if not n.find_input_pin("Object").list_connected_pins():connect(target,n.find_input_pin("Object"))
    if start is not None:connect(start,n.find_execute_pin())
    data=next(p for p in n.list_output_pins() if p.get_pin_type().export_text().startswith('(PinCategory="object"'))
    return n.find_output_pin("then"),data,n.find_output_pin("CastFailed")
def clear_body(g):
    keep={"K2Node_FunctionEntry","K2Node_FunctionResult"}
    g.remove_nodes([n for n in g.list_all_nodes() if n.get_class().get_name() not in keep])
    for n in g.list_all_nodes():
        for p in n.list_all_pins():p.break_pin_links()

def bind_assign(g,start,target,name):
    before={n.get_path_name() for n in g.list_all_nodes()}
    key=next(x for x in actions(g,[target]) if x.endswith("|Assign"+name))
    n=g.create_node_from_name(key,unreal.Vector2D(0,0),[target])
    if not n.find_self_pin().list_connected_pins():connect(target,n.find_self_pin())
    connect(start,n.find_execute_pin())
    callbacks=[x for x in g.list_all_nodes() if x.get_path_name() not in before and x.get_class().get_name()=="K2Node_CustomEvent"]
    assert len(callbacks)==1,(name,[(x.get_class().get_name(),x.get_name()) for x in g.list_all_nodes() if x.get_path_name() not in before])
    return n.find_then_pin(),callbacks[0]
def key_event(bp,key):
    g=unreal.BlueprintGraphEditor.get_graph_editor(unreal.BlueprintEditorLibrary.find_event_graph(bp))
    key={"Backspace":"Retroceso","Up":"Arriba","Down":"Abajo","Left":"Izquierda","Right":"Derecha"}.get(key,key)
    existing=next((n for n in g.list_all_nodes() if n.get_class().get_name()=="K2Node_InputKey" and str(n.get_node_title())==key),None)
    if existing:return g,existing
    choices=actions(g)
    name=next(x for x in choices if x.endswith("|"+key) and ("teclado" in x.lower() or "keyboard" in x.lower()))
    return g,g.create_node_from_name(name,unreal.Vector2D(0,0),[])

def table_row(g,start,table,row):
    key=next(x for x in actions(g) if x.endswith("|Obtenerfiladetabladedatos") or x.endswith("|GetDataTableRow"))
    n=g.create_node_from_name(key,unreal.Vector2D(0,0),[])
    literal(n.find_input_pin("DataTable"),table.get_path_name())
    value(n.find_input_pin("RowName"),row);connect(start,n.find_execute_pin())
    return n

def break_struct(g,pin):
    name=next(x for x in ("ST_DialogueLine","ST_ChecklistRow") if x in pin.get_pin_type().export_text())
    key=next(x for x in actions(g,[pin]) if x.split("|")[-1].replace("_","").replace(" ","").lower()=="break"+name.replace("_","").lower())
    n=g.create_node_from_name(key,unreal.Vector2D(0,0),[pin])
    for p in n.list_input_pins():
        if p.get_pin_type().export_text().startswith('(PinCategory="struct"') and not p.list_connected_pins():connect(pin,p)
    return {str(p.get_pin_name()).split("_")[0]:p for p in n.list_output_pins()}
