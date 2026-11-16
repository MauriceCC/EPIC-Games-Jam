"""A-04 health migration, with editor closed. Saves only A packages.
Preserves public function signatures and existing dispatcher declarations.
"""
import json, sys, traceback, shutil, tempfile, hashlib
from pathlib import Path
import unreal
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from a03_graph_tools import L,G,graph,connect,snapshot
ROOT=HERE.parent.parent
HEALTH='/Game/Unscripted/Player/BP_HealthComponent'
PLAYER='/Game/Unscripted/Player/BP_PlayerCharacter'
OBSERVER='/Game/Unscripted/Player/Test/BP_HealthObserver_A'
OUT={'passed':False,'saved':[],'checks':[],'base_commit':'e95d5b9'}
def check(name,v):
    OUT['checks'].append({'name':name,'passed':bool(v)});assert v,name
def get(g,n):return g.add_get_member_variable_node(n).find_result_pin()
def value(pin,v):
    if isinstance(v,unreal.BlueprintGraphPin):connect(v,pin)
    else:assert pin.set_pin_value('true' if v is True else 'false' if v is False else str(v))
def call(g,path,start=None,**args):
    n=g.add_call_function_node(path)
    if start is not None:connect(start,n.find_execute_pin())
    for k,v in args.items():value(n.find_input_pin(k),v)
    return n
def math(g,name,**args):return call(g,'/Script/Engine.KismetMathLibrary:'+name,**args).find_result_pin()
def assign(g,start,n,v):
    node=g.add_set_member_variable_node(n);connect(start,node.find_execute_pin());value(node.find_input_pin(n),v);return node.find_then_pin()
def param(g,n):return g.find_graph_entry_pin().get_owning_node().find_output_pin(n)
def branch(g,start,c):
    n=g.add_branch_node();connect(start,n.find_execute_pin());connect(c,n.find_condition_pin());return n.find_then_pin(),n.find_output_pin('else')
def emit(g,start,name,**args):
    menu=[str(k) for k in g.list_available_nodes([start])]
    choices=[k for k in menu if name.lower() in k.replace(' ','').lower()]
    OUT.setdefault('dispatcher_menu',{})[name]=choices
    if not choices:OUT['menu_sample']=menu
    key=next(k for k in choices if k.replace(' ','').endswith(('|Call'+name,'|Llamar'+name)))
    n=g.create_node_from_name(key,unreal.Vector2D(0,0),[]);connect(start,n.find_execute_pin())
    for k,v in args.items():value(n.find_input_pin(k),v)
    return n.find_then_pin()
def clean_body(bp,name):
    g=graph(bp,name)
    g.remove_nodes([n for n in g.list_all_nodes() if n.get_class().get_name()!='K2Node_FunctionEntry'])
    return g
try:
    health=unreal.load_asset(HEALTH);player=unreal.load_asset(PLAYER)
    before=snapshot(health);player_before=snapshot(player)
    check('Migration not already applied','A_CommitHealth' not in before)
    check('No observer overwritten',not unreal.EditorAssetLibrary.does_asset_exist(OBSERVER))
    backup=Path(tempfile.mkdtemp(prefix='Unscripted_A04_'))
    for name in ('BP_HealthComponent','BP_PlayerCharacter'):
        shutil.copy2(ROOT/'Unscripted/Content/Unscripted/Player'/(name+'.uasset'),backup/(name+'.uasset'))
    OUT['backup']=str(backup)
    event=graph(health,'EventGraph')
    check('Guard field is new','bA_UpdatingHealth' not in [str(x) for x in L.list_member_variable_names(health)])
    assert event.add_member_variable('bA_UpdatingHealth',L.get_basic_type_by_name('bool'),'false')
    L.set_blueprint_variable_instance_editable(health,'bA_UpdatingHealth',False)
    typ=param(graph(health,'SetHealth'),'Value').get_pin_type()
    helper=G.create_and_edit_function_graph(health,'A_CommitHealth');helper.set_function_is_private()
    for n in ('PreviousHealth','NewHealth','Maximum'):helper.add_graph_input_parameter(n,typ)
    check('Helper signature registered',L.compile_blueprint(health))
    helper=graph(health,'A_CommitHealth')
    yes,_=branch(helper,helper.find_graph_entry_pin(),math(helper,'Not_PreBool',A=get(helper,'bA_UpdatingHealth')))
    end=assign(helper,yes,'bA_UpdatingHealth',True)
    end=assign(helper,end,'MaxHealth',param(helper,'Maximum'))
    end=assign(helper,end,'CurrentHealth',param(helper,'NewHealth'))
    end=emit(helper,end,'OnHealthChanged',Current=param(helper,'NewHealth'),Max=param(helper,'Maximum'))
    depleted=math(helper,'BooleanAND',A=math(helper,'Greater_DoubleDouble',A=param(helper,'PreviousHealth'),B=0),B=math(helper,'LessEqual_DoubleDouble',A=param(helper,'NewHealth'),B=0))
    yes,no=branch(helper,end,depleted)
    end=emit(helper,yes,'OnDepleted')
    assign(helper,end,'bA_UpdatingHealth',False);assign(helper,no,'bA_UpdatingHealth',False)
    check('Private commit function compiles',L.compile_blueprint(health))
    for name,arg in [('SetHealth','Value'),('ApplyHealthDamage','Amount')]:
        g=clean_body(health,name)
        maximum=math(g,'FMax',A=get(g,'MaxHealth'),B=0)
        requested=param(g,arg)
        if name=='ApplyHealthDamage':
            requested=math(g,'Subtract_DoubleDouble',A=get(g,'CurrentHealth'),B=math(g,'FMax',A=requested,B=0))
        new=math(g,'FClamp',Value=requested,Min=0,Max=maximum)
        call(g,health.generated_class().get_path_name()+':A_CommitHealth',g.find_graph_entry_pin(),PreviousHealth=get(g,'CurrentHealth'),NewHealth=new,Maximum=maximum)
    event=graph(health,'EventGraph')
    begin=next(n for n in event.list_all_nodes() if n.get_class().get_name()=='K2Node_Event' and 'Begin' in str(L.get_node_title(n)))
    event.remove_nodes([n for n in event.list_all_nodes() if n.get_class().get_name()!='K2Node_Event'])
    call(event,health.generated_class().get_path_name()+':SetHealth',begin.find_then_pin(),Value=get(event,'MaxHealth'))
    check('Health public functions compile',L.compile_blueprint(health))
    after=snapshot(health)
    check('Dispatcher graphs and signatures unchanged',all(before[n]==after[n] for n in ('OnHealthChanged','OnDepleted')))
    for name in ('SetHealth','ApplyHealthDamage'):
        old=next(n for n in before[name].values() if n['class']=='K2Node_FunctionEntry')
        new=next(n for n in after[name].values() if n['class']=='K2Node_FunctionEntry')
        check(name+' signature unchanged',{k:p['type'] for k,p in old['pins'].items()}=={k:p['type'] for k,p in new['pins'].items()})
    check('Player compiles against updated health',L.compile_blueprint(player))
    H=unreal.SubobjectDataBlueprintFunctionLibrary
    templates=[]
    for h in unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(player):
        obj=H.get_object(H.get_data(h))
        if obj and obj.get_class()==health.generated_class() and obj.get_path_name() not in [x.get_path_name() for x in templates]:templates.append(obj)
    check('Exactly one installed Health template',len(templates)==1)
    template=templates[0]
    OUT['player_health_before']={n:template.get_editor_property(n) for n in ('MaxHealth','CurrentHealth')}
    template.set_editor_property('MaxHealth',100.0);template.set_editor_property('CurrentHealth',100.0)
    check('A-03 and all player graphs untouched',snapshot(player)==player_before)

    # Real multicast observer, reusable with arbitrary component instances/owners.
    f=unreal.BlueprintFactory();f.set_editor_property('parent_class',health.generated_class())
    observer=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_HealthObserver_A','/Game/Unscripted/Player/Test',unreal.Blueprint,f)
    g=G.get_graph_editor(L.find_event_graph(observer))
    for name,t,default in [('ObservedHealth',L.get_object_reference_type(health.generated_class()),''),('ChangeCount',L.get_basic_type_by_name('int'),'0'),('DepletedCount',L.get_basic_type_by_name('int'),'0'),('LastCurrent',typ,'-1'),('LastMax',typ,'-1'),('bAttemptReentry',L.get_basic_type_by_name('bool'),'false')]:
        assert g.add_member_variable(name,t,default)
        if name in ('ObservedHealth','bAttemptReentry'):L.set_blueprint_variable_instance_editable(observer,name,True)
    check('Observer fields compile',L.compile_blueprint(observer))
    g=G.get_graph_editor(L.find_event_graph(observer))
    end=g.add_custom_event_node('BindHealth').find_then_pin()
    for signal,counter in [('OnHealthChanged','ChangeCount'),('OnDepleted','DepletedCount')]:
        callback=g.add_dispatcher_event_node(signal,health.generated_class())
        target=get(g,'ObservedHealth')
        key=next(str(a) for a in g.list_available_nodes([target]) if str(a).endswith('|BindEventto'+signal))
        binder=g.create_node_from_name(key,unreal.Vector2D(0,0),[target])
        connect(target,binder.find_self_pin());connect(callback.find_output_pin('OutputDelegate'),binder.find_input_pin('Delegate'));connect(end,binder.find_execute_pin());end=binder.find_then_pin()
        last=assign(g,callback.find_then_pin(),counter,math(g,'Add_IntInt',A=get(g,counter),B=1))
        if signal=='OnHealthChanged':
            last=assign(g,last,'LastCurrent',callback.find_output_pin('Current'));last=assign(g,last,'LastMax',callback.find_output_pin('Max'))
            yes,_=branch(g,last,get(g,'bAttemptReentry'))
            reentry=call(g,health.generated_class().get_path_name()+':ApplyHealthDamage',yes,Amount=1)
            connect(get(g,'ObservedHealth'),reentry.find_self_pin())
    check('Observer compiles',L.compile_blueprint(observer))
    for bp in (health,observer):
        for raw in L.list_graphs(bp):
            if raw.get_name() in ('OnHealthChanged','OnDepleted'):continue
            for i,n in enumerate(G.get_graph_editor(raw).list_all_nodes()):L.set_node_pos(n,unreal.IntPoint((i%6)*330,(i//6)*240))
    for bp in (health,player,observer):
        check('Save '+bp.get_name(),unreal.EditorAssetLibrary.save_loaded_asset(bp));OUT['saved'].append(bp.get_path_name())
    OUT['passed']=True
except Exception:
    OUT['error']=traceback.format_exc();unreal.log_error(OUT['error'])
finally:(HERE/'a04_implementation_result.json').write_text(json.dumps(OUT,indent=2),encoding='utf-8')
if not OUT['passed']:raise RuntimeError('A-04 migration failed; inspect report before retrying')
