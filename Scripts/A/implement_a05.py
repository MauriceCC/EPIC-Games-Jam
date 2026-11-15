"""A-05 stamina migration (one-shot). Run with the full editor via run_a05_editor.py.
Saves only A packages: BP_CombatComponent, BP_PlayerCharacter, Player/Test/BP_StaminaHUDTest_A
and Maps/Test/L_Test_A. Preserves the existing dispatcher declarations and every
pre-existing node/value of the player except the three gated execution edges.
"""
import json, sys, traceback, shutil, tempfile
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, G, graph, connect, snapshot
ROOT = HERE.parent.parent
COMBAT = '/Game/Unscripted/Player/BP_CombatComponent'
PLAYER = '/Game/Unscripted/Player/BP_PlayerCharacter'
HUDTEST = '/Game/Unscripted/Player/Test/BP_StaminaHUDTest_A'
MAP = '/Game/Unscripted/Maps/Test/L_Test_A'
# [PROPUESTA] Initial values: docs/03 (100, 30/s, costs 10/25/20/10); 0.6 s pause is A's choice.
TUNABLES = [('MaxStamina', 100.0), ('StaminaRegenRate', 30.0), ('StaminaRegenDelay', 0.6),
            ('LightAttackStaminaCost', 10.0), ('HeavyAttackStaminaCost', 25.0),
            ('DodgeStaminaCost', 20.0), ('ParryStaminaCost', 10.0)]
GATES = {'DoLightAttack': 'LightAttackStaminaCost', 'DoDodge': 'DodgeStaminaCost', 'DoParry': 'ParryStaminaCost'}
OUT = {'passed': False, 'saved': [], 'checks': [], 'base_commit': 'be77859'}

def check(name, v):
    OUT['checks'].append({'name': name, 'passed': bool(v)}); assert v, name
def get(g, n): return g.add_get_member_variable_node(n).find_result_pin()
def value(pin, v):
    assert pin is not None and pin.is_valid(), 'missing pin'
    if isinstance(v, unreal.BlueprintGraphPin): connect(v, pin)
    else: assert pin.set_pin_value('true' if v is True else 'false' if v is False else str(v)), (str(pin.get_pin_name()), v)
def call(g, path, start=None, target=None, **args):
    n = g.add_call_function_node(path)
    assert n, path
    if start is not None: connect(start, n.find_execute_pin())
    if target is not None: connect(target, n.find_self_pin())
    for k, v in args.items(): value(n.find_input_pin(k), v)
    return n
def math(g, name, **args): return call(g, '/Script/Engine.KismetMathLibrary:' + name, **args).find_result_pin()
def assign(g, start, n, v):
    node = g.add_set_member_variable_node(n); connect(start, node.find_execute_pin()); value(node.find_input_pin(n), v); return node.find_then_pin()
def param(g, n): return g.find_graph_entry_pin().get_owning_node().find_output_pin(n)
def branch(g, start, c):
    n = g.add_branch_node(); connect(start, n.find_execute_pin()); connect(c, n.find_condition_pin()); return n.find_then_pin(), n.find_output_pin('else')
def menu_node(g, context, suffixes, label):
    menu = [str(k) for k in g.list_available_nodes([context])]
    choices = [k for k in menu if k.replace(' ', '').endswith(tuple(suffixes))]
    OUT.setdefault('menu', {})[label] = choices
    if not choices: OUT['menu_sample_' + label] = menu
    assert choices, label
    return g.create_node_from_name(choices[0], unreal.Vector2D(0, 0), [context])
def emit(g, start, name, **args):
    n = menu_node(g, start, ('|Call' + name, '|Llamar' + name), 'Call' + name); connect(start, n.find_execute_pin())
    for k, v in args.items(): value(n.find_input_pin(k), v)
    return n.find_then_pin()
def result_nodes(g): return [n for n in g.list_all_nodes() if n.get_class().get_name() == 'K2Node_FunctionResult']
def ret(g, start, out_name, v, reuse):
    node = reuse.pop() if reuse else g.add_return_node()
    connect(start, node.find_execute_pin()); value(node.find_input_pin(out_name), v)
def tidy(g, x0=0, y0=0):
    for i, n in enumerate(g.list_all_nodes()):
        if n.get_class().get_name() not in ('K2Node_FunctionEntry',): L.set_node_pos(n, unreal.IntPoint(x0 + (i % 6) * 330, y0 + (i // 6) * 240))

try:
    combat = unreal.load_asset(COMBAT); player = unreal.load_asset(PLAYER)
    cpath = combat.generated_class().get_path_name()
    combat_before = snapshot(combat); player_before = snapshot(player)
    check('Migration not already applied', 'A_CommitStamina' not in combat_before)
    check('No HUD test fixture overwritten', not unreal.EditorAssetLibrary.does_asset_exist(HUDTEST))
    check('Combat starts as F0 shell (BeginPlay/Tick unconnected)', len(combat_before['EventGraph']) == 2)
    backup = Path(tempfile.mkdtemp(prefix='Unscripted_A05_'))
    for rel in ('Player/BP_CombatComponent.uasset', 'Player/BP_PlayerCharacter.uasset', 'Maps/Test/L_Test_A.umap'):
        shutil.copy2(ROOT / 'Unscripted/Content/Unscripted' / rel, backup / Path(rel).name)
    OUT['backup'] = str(backup)

    real = L.get_basic_type_by_name('real'); boolean = L.get_basic_type_by_name('bool')
    check('Dispatcher pins are real', 'PinCategory="real"' in next(iter(combat_before['OnStaminaChanged'].values()))['pins']['Current']['type'])
    ev = graph(combat, 'EventGraph')
    for name, default in TUNABLES + [('CurrentStamina', 100.0), ('A_RegenPauseRemaining', 0.0)]:
        assert ev.add_member_variable(name, real, str(default)), name
        L.set_blueprint_variable_category(combat, name, 'Stamina')
        L.set_blueprint_variable_instance_editable(combat, name, name in dict(TUNABLES))
    assert ev.add_member_variable('bA_UpdatingStamina', boolean, 'false')
    L.set_blueprint_variable_instance_editable(combat, 'bA_UpdatingStamina', False)
    for name, ins, outs, private, pure in [
            ('A_CommitStamina', ('NewStamina', 'Maximum'), (), True, False),
            ('SetStamina', ('Value',), (), False, False),
            ('HasStamina', ('Cost',), ('bHasStamina',), False, True),
            ('TryConsumeStamina', ('Cost',), ('bConsumed',), False, False)]:
        f = G.create_and_edit_function_graph(combat, name)
        for i in ins: f.add_graph_input_parameter(i, real)
        for o in outs: f.add_graph_output_parameter(o, boolean)
        if private: f.set_function_is_private()
        if pure: f.set_is_pure_function(True); f.set_is_const_function(True)
    check('Stamina fields and signatures compile', L.compile_blueprint(combat))

    # A_CommitStamina: guarded single write + notification with captured values.
    g = graph(combat, 'A_CommitStamina')
    yes, _ = branch(g, g.find_graph_entry_pin(), math(g, 'Not_PreBool', A=get(g, 'bA_UpdatingStamina')))
    end = assign(g, yes, 'bA_UpdatingStamina', True)
    end = assign(g, end, 'MaxStamina', param(g, 'Maximum'))
    end = assign(g, end, 'CurrentStamina', param(g, 'NewStamina'))
    end = emit(g, end, 'OnStaminaChanged', Current=param(g, 'NewStamina'), Max=param(g, 'Maximum'))
    assign(g, end, 'bA_UpdatingStamina', False)
    # SetStamina: clamp to [0, max(MaxStamina, 0)].
    g = graph(combat, 'SetStamina')
    maximum = math(g, 'FMax', A=get(g, 'MaxStamina'), B=0)
    call(g, cpath + ':A_CommitStamina', g.find_graph_entry_pin(), NewStamina=math(g, 'FClamp', Value=param(g, 'Value'), Min=0, Max=maximum), Maximum=maximum)
    # HasStamina (pure): the full cost must be available.
    g = graph(combat, 'HasStamina')
    ret(g, g.find_graph_entry_pin(), 'bHasStamina', math(g, 'GreaterEqual_DoubleDouble', A=get(g, 'CurrentStamina'), B=math(g, 'FMax', A=param(g, 'Cost'), B=0)), result_nodes(g))
    # TryConsumeStamina: refuse during a notification or without enough stamina.
    g = graph(combat, 'TryConsumeStamina'); reuse = result_nodes(g)
    ok = math(g, 'BooleanAND', A=math(g, 'Not_PreBool', A=get(g, 'bA_UpdatingStamina')), B=call(g, cpath + ':HasStamina', Cost=param(g, 'Cost')).find_output_pin('bHasStamina'))
    yes, no = branch(g, g.find_graph_entry_pin(), ok)
    paid, free = branch(g, yes, math(g, 'Greater_DoubleDouble', A=param(g, 'Cost'), B=0))
    end = assign(g, paid, 'A_RegenPauseRemaining', get(g, 'StaminaRegenDelay'))
    spend = call(g, cpath + ':SetStamina', end, Value=math(g, 'Subtract_DoubleDouble', A=get(g, 'CurrentStamina'), B=param(g, 'Cost')))
    ret(g, spend.find_then_pin(), 'bConsumed', True, reuse)
    ret(g, free, 'bConsumed', True, reuse)
    ret(g, no, 'bConsumed', False, reuse)
    check('Stamina functions compile', L.compile_blueprint(combat))

    # EventGraph: BeginPlay fills; Tick waits for the pause, then regenerates Rate/s.
    g = graph(combat, 'EventGraph')
    events = {str(L.get_node_title(n)): n for n in g.list_all_nodes() if n.get_class().get_name() == 'K2Node_Event'}
    begin = next(n for t, n in events.items() if 'Begin' in t); tick = next(n for t, n in events.items() if 'Tick' in t)
    end = assign(g, begin.find_then_pin(), 'A_RegenPauseRemaining', 0)
    call(g, cpath + ':SetStamina', end, Value=get(g, 'MaxStamina'))
    delta = tick.find_output_pin('DeltaSeconds')
    paused, running = branch(g, tick.find_then_pin(), math(g, 'Greater_DoubleDouble', A=get(g, 'A_RegenPauseRemaining'), B=0))
    assign(g, paused, 'A_RegenPauseRemaining', math(g, 'FMax', A=math(g, 'Subtract_DoubleDouble', A=get(g, 'A_RegenPauseRemaining'), B=delta), B=0))
    # Rate > 0 was added afterwards by patch_a05_regen_guard.py (already applied to the saved asset).
    low, _ = branch(g, running, math(g, 'BooleanAND', A=math(g, 'Less_DoubleDouble', A=get(g, 'CurrentStamina'), B=math(g, 'FMax', A=get(g, 'MaxStamina'), B=0)), B=math(g, 'Greater_DoubleDouble', A=get(g, 'StaminaRegenRate'), B=0)))
    gain = math(g, 'Multiply_DoubleDouble', A=get(g, 'StaminaRegenRate'), B=delta)
    call(g, cpath + ':SetStamina', low, Value=math(g, 'Add_DoubleDouble', A=get(g, 'CurrentStamina'), B=gain))
    check('Combat component compiles', L.compile_blueprint(combat))
    combat_after = snapshot(combat)
    check('Dispatcher declarations unchanged', all(combat_before[n] == combat_after[n] for n in ('OnStaminaChanged', 'OnCombatStateChanged')))
    for raw in L.list_graphs(combat):
        if raw.get_name() not in ('OnStaminaChanged', 'OnCombatStateChanged'): tidy(G.get_graph_editor(raw))

    # Player: gate light attack, dodge and parry after their existing guard branch.
    check('Player compiles against new combat', L.compile_blueprint(player))
    edges = {}
    for fname, cost in GATES.items():
        g = graph(player, fname)
        nodes = {n.get_name(): n for n in g.list_all_nodes()}
        br, act = nodes['K2Node_IfThenElse_0'], nodes['K2Node_VariableSet_0']
        then, execute = br.find_then_pin(), act.find_execute_pin()
        check(fname + ' guard -> action edge found', any(p.is_same_native_pin(execute) for p in then.list_connected_pins()))
        then.break_pin_links()
        comp = g.add_get_member_variable_node('BP_CombatComponent').find_result_pin()
        getter = menu_node(g, comp, ('|Obtener' + cost, '|Get' + cost), fname + '.' + cost)
        connect(comp, getter.find_self_pin())
        try_node = call(g, cpath + ':TryConsumeStamina', then, target=comp, Cost=getter.find_output_pin(cost))
        ok, _ = branch(g, try_node.find_then_pin(), try_node.find_output_pin('bConsumed'))
        connect(ok, execute)
        new = [n for n in g.list_all_nodes() if n.get_name() not in nodes]
        p = L.get_node_pos(act)
        for i, n in enumerate(new): L.set_node_pos(n, unreal.IntPoint(p.x + i * 260, p.y + 420))
        edges[fname] = (try_node.get_name(), {n.get_name() for n in new})
    check('Player compiles with stamina gates', L.compile_blueprint(player))
    player_after = snapshot(player)
    check('No player graph added or removed', set(player_after) == set(player_before))
    for gname, nodes in player_before.items():
        for nname, node in nodes.items():
            cur = player_after[gname][nname]
            assert cur['class'] == node['class'] and cur['title'] == node['title'] and cur['pins'].keys() == node['pins'].keys(), (gname, nname)
            for pname, old in node['pins'].items():
                new = cur['pins'][pname]
                assert new['value'] == old['value'] and new['type'] == old['type'], (gname, nname, pname)
                expected = old['links']
                if gname in GATES and nname == 'K2Node_IfThenElse_0' and pname == 'then': expected = [(edges[gname][0], 'execute')]
                if gname in GATES and nname == 'K2Node_VariableSet_0' and pname == 'execute':
                    expected = [l for l in new['links'] if l[0] in edges[gname][1] and l[1] == 'then']
                    assert len(expected) == 1, (gname, new['links'])
                assert new['links'] == expected, (gname, nname, pname, new['links'])
        added = set(player_after[gname]) - set(nodes)
        assert added == (edges[gname][1] if gname in GATES else set()), (gname, added)
    check('Only the three gated edges changed in pre-existing player graphs', True)
    H = unreal.SubobjectDataBlueprintFunctionLibrary
    templates = []
    for h in unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(player):
        obj = H.get_object(H.get_data(h))
        if obj and obj.get_class() == combat.generated_class() and obj.get_path_name() not in [x.get_path_name() for x in templates]: templates.append(obj)
    check('Exactly one installed Combat template', len(templates) == 1)
    OUT['template_before'] = {n: templates[0].get_editor_property(n) for n, _ in TUNABLES + [('CurrentStamina', 0)]}
    for n, v in TUNABLES + [('CurrentStamina', 100.0)]: templates[0].set_editor_property(n, v)

    # Test HUD fixture (A-owned, Player/Test): shows the real player's stamina in PIE.
    f = unreal.BlueprintFactory(); f.set_editor_property('parent_class', unreal.Actor)
    hud = unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_StaminaHUDTest_A', '/Game/Unscripted/Player/Test', unreal.Blueprint, f)
    g = G.get_graph_editor(L.find_event_graph(hud))
    for name, t, default, editable in [('ObservedCombat', L.get_object_reference_type(combat.generated_class()), '', True),
            ('bPrintToScreen', boolean, 'true', True), ('bAttemptReentry', boolean, 'false', True),
            ('ChangeCount', L.get_basic_type_by_name('int'), '0', False), ('LastCurrent', real, '-1', False), ('LastMax', real, '-1', False),
            ('LastReentryResult', boolean, 'false', False)]:
        assert g.add_member_variable(name, t, default), name
        L.set_blueprint_variable_instance_editable(hud, name, editable)
    show = G.create_and_edit_function_graph(hud, 'A_ShowStamina')
    for i in ('Current', 'Max'): show.add_graph_input_parameter(i, real)
    g.add_custom_event_node('BindCombat')
    check('HUD fixture skeleton compiles', L.compile_blueprint(hud))
    hpath = hud.generated_class().get_path_name()
    g = graph(hud, 'A_ShowStamina')
    end = assign(g, g.find_graph_entry_pin(), 'ChangeCount', math(g, 'Add_IntInt', A=get(g, 'ChangeCount'), B=1))
    end = assign(g, end, 'LastCurrent', param(g, 'Current')); end = assign(g, end, 'LastMax', param(g, 'Max'))
    yes, no = branch(g, end, get(g, 'bAttemptReentry'))
    re = call(g, cpath + ':TryConsumeStamina', yes, target=get(g, 'ObservedCombat'), Cost=1)
    end2 = assign(g, re.find_then_pin(), 'LastReentryResult', re.find_output_pin('bConsumed'))
    s = lambda pin: call(g, '/Script/Engine.KismetStringLibrary:Conv_IntToString', InInt=call(g, '/Script/Engine.KismetMathLibrary:Round', A=pin).find_result_pin()).find_result_pin()
    cat = lambda a, b: call(g, '/Script/Engine.KismetStringLibrary:Concat_StrStr', A=a, B=b).find_result_pin()
    text = cat(cat(cat('Stamina: ', s(param(g, 'Current'))), ' / '), s(param(g, 'Max')))
    for start in (end2, no):
        pr, _ = branch(g, start, get(g, 'bPrintToScreen'))
        call(g, '/Script/Engine.KismetSystemLibrary:PrintString', pr, InString=text, bPrintToScreen=True, bPrintToLog=False, Duration=3600, Key='A_StaminaHUDTest')
    g = G.get_graph_editor(L.find_event_graph(hud))
    bind = next(n for n in g.list_all_nodes() if 'BindCombat' in str(L.get_node_title(n)))
    target = get(g, 'ObservedCombat')
    valid, _ = branch(g, bind.find_then_pin(), call(g, '/Script/Engine.KismetSystemLibrary:IsValid', Object=target).find_result_pin())
    binder = menu_node(g, target, ('|BindEventtoOnStaminaChanged',), 'BindOnStaminaChanged')
    # Create Event -> A_ShowStamina (same Current/Max signature as the dispatcher).
    callback = menu_node(g, binder.find_input_pin('Delegate'), ('|CreateEvent', '|Crearevento'), 'CreateEvent')
    OUT['compatible_delegate_functions'] = [str(x) for x in L.list_compatible_functions_for_delegate(callback)] if hasattr(L, 'list_compatible_functions_for_delegate') else None
    L.set_create_delegate_function(callback, 'A_ShowStamina')
    connect(callback.find_output_pin('OutputDelegate'), binder.find_input_pin('Delegate'))
    connect(target, binder.find_self_pin()); connect(valid, binder.find_execute_pin())
    cur = menu_node(g, target, ('|ObtenerCurrentStamina', '|GetCurrentStamina'), 'GetCurrentStamina'); connect(target, cur.find_self_pin())
    mx = menu_node(g, target, ('|ObtenerMaxStamina', '|GetMaxStamina'), 'GetMaxStamina'); connect(target, mx.find_self_pin())
    call(g, hpath + ':A_ShowStamina', binder.find_then_pin(), Current=cur.find_output_pin('CurrentStamina'), Max=mx.find_output_pin('MaxStamina'))
    begin = next(n for n in g.list_all_nodes() if n.get_class().get_name() == 'K2Node_Event' and 'Begin' in str(L.get_node_title(n)))
    # Wait for the GameMode to possess the player, then observe its Combat unless one was assigned.
    delay = call(g, '/Script/Engine.KismetSystemLibrary:Delay', begin.find_then_pin(), Duration=0.2)
    missing, present = branch(g, delay.find_then_pin(), math(g, 'Not_PreBool', A=call(g, '/Script/Engine.KismetSystemLibrary:IsValid', Object=get(g, 'ObservedCombat')).find_result_pin()))
    pawn = call(g, '/Script/Engine.GameplayStatics:GetPlayerCharacter', PlayerIndex=0).find_result_pin()
    find = call(g, '/Script/Engine.Actor:GetComponentByClass', target=pawn); value(find.find_input_pin('ComponentClass'), cpath)
    end = assign(g, missing, 'ObservedCombat', find.find_result_pin())
    call(g, hpath + ':BindCombat', end); call(g, hpath + ':BindCombat', present)
    check('HUD fixture compiles', L.compile_blueprint(hud))
    for raw in L.list_graphs(hud): tidy(G.get_graph_editor(raw))

    # Place one fixture in A's own test map.
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    check('Load L_Test_A', les.load_level(MAP))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    check('No fixture already placed', not [a for a in eas.get_all_level_actors() if a.get_class() == hud.generated_class()])
    actor = eas.spawn_actor_from_class(hud.generated_class(), unreal.Vector(0, 0, 200))
    actor.set_actor_label('A_StaminaHUDTest')
    OUT['map_game_mode_override'] = str(unreal.EditorLevelLibrary.get_editor_world().get_world_settings().get_editor_property('default_game_mode'))

    for bp in (combat, player, hud):
        check('Save ' + bp.get_name(), unreal.EditorAssetLibrary.save_loaded_asset(bp)); OUT['saved'].append(bp.get_path_name())
    check('Save L_Test_A', les.save_current_level()); OUT['saved'].append(MAP)
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    (HERE / 'a05_implementation_result.json').write_text(json.dumps(OUT, indent=2, default=str), encoding='utf-8')
if not OUT['passed']: raise RuntimeError('A-05 migration failed; inspect report before retrying')
