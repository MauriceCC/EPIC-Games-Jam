"""Sprint MVP (docs/plan/05_SPRINT_MVP_2H.md §4.1) — A6 and A7. One-shot migration on top of A1–A4.

Run with the full editor via run_a_sprint_mvp_p1_editor.py. Saves only Player/BP_PlayerCharacter.

A6  Retake also rewinds stamina: Tick samples CurrentStamina into StaminaHistory next to PosHistory/HPHistory
    (same 0.1 s cadence and 30-sample cap); DoRetake restores the oldest sample with SetStamina when the
    histories are aligned, then clears it with the others. ClearRetakeHistory clears it too.
    Fix: B_ResumePlayerAtCheckpoint now empties the retake history and refills stamina, so R after a
    respawn can no longer rewind to positions/health from before the death.
    (Retake without samples already refused to spend a charge: DoRetake requires PosHistory > 0.)
A7  Frame Cut needs line of sight: inside the candidate loop, after B's CanBeTemporalCutTarget (which already
    rejects defeated and frozen guards), a Visibility line trace from the agent to the candidate must hit
    nothing or a Pawn. Walls/props block the Cut; other characters in between do not.
"""
import json, sys, traceback, shutil, tempfile
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, G, graph, connect, snapshot
ROOT = HERE.parent.parent
PLAYER = '/Game/Unscripted/Player/BP_PlayerCharacter'
COMBAT = '/Game/Unscripted/Player/BP_CombatComponent'
OUT = {'passed': False, 'saved': [], 'checks': [], 'menus': {}}


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
def branch(g, start, c):
    n = g.add_branch_node(); connect(start, n.find_execute_pin()); connect(c, n.find_condition_pin()); return n.find_then_pin(), n.find_output_pin('else')
def nodes_of(g): return {n.get_name(): n for n in g.list_all_nodes()}
def menu(g, context, suffixes, label):
    keys = [str(k) for k in g.list_available_nodes([context])]
    choices = [k for k in keys if k.replace(' ', '').endswith(tuple(s.replace(' ', '') for s in suffixes))]
    OUT['menus'][label] = choices or [k for k in keys if 'Matriz' in k or 'Array' in k or 'Stamina' in k][:40]
    assert choices, label
    return g.create_node_from_name(choices[0], unreal.Vector2D(0, 0), [context])
def array_op(g, start, name, suffixes, label, **args):
    arr = get(g, name)
    n = menu(g, arr, suffixes, label)
    tgt = n.find_input_pin('TargetArray')
    tgt = tgt if tgt is not None and tgt.is_valid() else n.find_input_pin('Array')
    if not tgt.list_connected_pins(): connect(arr, tgt)
    if start is not None: connect(start, n.find_execute_pin())
    for k, v in args.items(): value(n.find_input_pin(k), v)
    return n
CLEAR = ('|Clear', '|Vaciar')
ADD = ('|Add', '|Añadir', '|Agregar')
REMOVE = ('|RemoveIndex', '|Eliminarindice', '|Eliminaríndice', '|Quitaríndice')
LENGTH = ('|Length', '|Longitud')
GETCOPY = ('|Get(acopy)', '|Obtener(unacopia)')
def length(g, name): return array_op(g, None, name, LENGTH, 'Length.' + name).find_output_pin('ReturnValue')
def comp(g): return get(g, 'BP_CombatComponent')
def comp_get(g, field):
    c = comp(g)
    n = menu(g, c, ('|Get' + field, '|Obtener' + field), 'Get' + field)
    if not n.find_self_pin().list_connected_pins(): connect(c, n.find_self_pin())
    return n.find_output_pin(field)
def link_between(g, out_node, out_pin, in_node, in_pin):
    n = nodes_of(g); a = n[out_node].find_output_pin(out_pin); b = n[in_node].find_input_pin(in_pin)
    check('%s: %s.%s -> %s.%s present' % (g.get_graph().get_name(), out_node, out_pin, in_node, in_pin), any(p.is_same_native_pin(b) for p in a.list_connected_pins()))
    a.break_pin_links()
    return a, b
def tail(g, start_pin):
    pin = start_pin
    while pin.list_connected_pins():
        pin = pin.list_connected_pins()[0].get_owning_node().find_then_pin()
    return pin

EDITED = set()  # (graph, node, pin) whose links may differ from the snapshot
def mark(gname, *pairs):
    for node, pin in pairs: EDITED.add((gname, node, pin))
def place(g, before, x, y):
    new = [n for name, n in nodes_of(g).items() if name not in before]
    for i, n in enumerate(new): L.set_node_pos(n, unreal.IntPoint(x + (i % 6) * 300, y + (i // 6) * 200))
    return {n.get_name() for n in new}

try:
    player = unreal.load_asset(PLAYER); combat = unreal.load_asset(COMBAT)
    cpath = combat.generated_class().get_path_name()
    before = snapshot(player)
    names = [str(n) for n in L.list_member_variable_names(player)]
    check('A1-A4 already applied', 'bRetakeBlocked' in names)
    check('Migration not already applied', 'StaminaHistory' not in names)
    backup = Path(tempfile.mkdtemp(prefix='Unscripted_A_SprintMVP_P1_'))
    shutil.copy2(ROOT / 'Unscripted/Content/Unscripted/Player/BP_PlayerCharacter.uasset', backup / 'BP_PlayerCharacter.uasset')
    OUT['backup'] = str(backup)
    added = {}

    ev = graph(player, 'EventGraph')
    real_array = unreal.EdGraphPinType(); real_array.import_text('(PinCategory="real",PinSubCategory="double",ContainerType=Array)')
    assert ev.add_member_variable('StaminaHistory', real_array, ''), 'StaminaHistory'
    L.set_blueprint_variable_category(player, 'StaminaHistory', 'Temporal')
    L.set_blueprint_variable_instance_editable(player, 'StaminaHistory', False)
    check('Player compiles with StaminaHistory', L.compile_blueprint(player))

    # ---- A6 Tick sampling (EventGraph) ----
    g = graph(player, 'EventGraph'); b0 = set(nodes_of(g))
    a, b = link_between(g, 'K2Node_CallArrayFunction_1', 'then', 'K2Node_IfThenElse_2', 'execute')
    mark('EventGraph', ('K2Node_CallArrayFunction_1', 'then'), ('K2Node_IfThenElse_2', 'execute'))
    n = array_op(g, a, 'StaminaHistory', ADD, 'Add', NewItem=comp_get(g, 'CurrentStamina'))
    connect(n.find_then_pin(), b)
    rm = nodes_of(g)['K2Node_CallArrayFunction_4']
    check('HP Remove Index has a free then', not rm.find_then_pin().list_connected_pins())
    mark('EventGraph', ('K2Node_CallArrayFunction_4', 'then'))
    array_op(g, rm.find_then_pin(), 'StaminaHistory', REMOVE, 'RemoveIndex', IndexToRemove=0)
    # ClearRetakeHistory event (added by A1): append the stamina clear at the end of its chain.
    clear_ev = next(x for x in g.list_all_nodes() if x.get_class().get_name() == 'K2Node_Event' and 'ClearRetakeHistory' in str(L.get_node_title(x)).replace(' ', ''))
    end = tail(g, clear_ev.find_then_pin())
    mark('EventGraph', (end.get_owning_node().get_name(), 'then'))
    array_op(g, end, 'StaminaHistory', CLEAR, 'Clear')
    added['EventGraph'] = place(g, b0, -2400, 7200)
    check('Player compiles after Tick sampling', L.compile_blueprint(player))

    # ---- A6 DoRetake restore ----
    g = graph(player, 'DoRetake'); b0 = set(nodes_of(g))
    a, b = link_between(g, 'K2Node_CallFunction_7', 'then', 'K2Node_VariableSet_0', 'execute')
    mark('DoRetake', ('K2Node_CallFunction_7', 'then'), ('K2Node_VariableSet_0', 'execute'))
    aligned = math(g, 'BooleanAND', A=math(g, 'EqualEqual_IntInt', A=length(g, 'StaminaHistory'), B=length(g, 'PosHistory')),
                   B=math(g, 'Greater_IntInt', A=length(g, 'StaminaHistory'), B=0))
    yes, no = branch(g, a, aligned)
    item = array_op(g, None, 'StaminaHistory', GETCOPY, 'GetCopy')
    value(item.find_input_pin('Dimension 1'), 0)
    out = next(p for p in L.list_all_pins(item) if 'OUTPUT' in str(p.get_pin_direction()).upper() and 'exec' not in p.get_pin_type().export_text())
    restore = call(g, cpath + ':SetStamina', yes, target=comp(g), Value=out)
    connect(restore.find_then_pin(), b); connect(no, b)
    a, b = link_between(g, 'K2Node_CallArrayFunction_2', 'then', 'K2Node_CallDelegate_0', 'execute')
    mark('DoRetake', ('K2Node_CallArrayFunction_2', 'then'), ('K2Node_CallDelegate_0', 'execute'))
    n = array_op(g, a, 'StaminaHistory', CLEAR, 'Clear')
    connect(n.find_then_pin(), b)
    added['DoRetake'] = place(g, b0, 1200, 900)
    check('Player compiles after DoRetake restore', L.compile_blueprint(player))

    # ---- A6 fix: respawn clears the retake history and refills stamina ----
    g = graph(player, 'B_ResumePlayerAtCheckpoint'); b0 = set(nodes_of(g))
    a, b = link_between(g, 'K2Node_CallFunction_5', 'then', 'K2Node_IfThenElse_0', 'execute')
    mark('B_ResumePlayerAtCheckpoint', ('K2Node_CallFunction_5', 'then'), ('K2Node_IfThenElse_0', 'execute'))
    end = array_op(g, a, 'PosHistory', CLEAR, 'Clear').find_then_pin()
    end = array_op(g, end, 'HPHistory', CLEAR, 'Clear').find_then_pin()
    end = array_op(g, end, 'StaminaHistory', CLEAR, 'Clear').find_then_pin()
    end = assign(g, end, 'SnapAccum', 0)
    refill = call(g, cpath + ':SetStamina', end, target=comp(g), Value=comp_get(g, 'MaxStamina'))
    connect(refill.find_then_pin(), b)
    added['B_ResumePlayerAtCheckpoint'] = place(g, b0, 600, 700)
    check('Player compiles after respawn fix', L.compile_blueprint(player))

    # ---- A7 Frame Cut line of sight ----
    g = graph(player, 'DoTemporalCut'); b0 = set(nodes_of(g))
    loop = nodes_of(g)['K2Node_MacroInstance_0']
    element = loop.find_output_pin('Array Element')
    a, b = link_between(g, 'K2Node_IfThenElse_3', 'then', 'K2Node_VariableSet_2', 'execute')
    mark('DoTemporalCut', ('K2Node_IfThenElse_3', 'then'), ('K2Node_VariableSet_2', 'execute'), ('K2Node_MacroInstance_0', 'Array Element'))
    me = call(g, '/Script/Engine.Actor:K2_GetActorLocation').find_result_pin()
    there = call(g, '/Script/Engine.Actor:K2_GetActorLocation', target=element).find_result_pin()
    trace = call(g, '/Script/Engine.KismetSystemLibrary:LineTraceSingle', a, Start=me, End=there)
    tc = trace.find_input_pin('TraceChannel'); OUT['trace_channel_default'] = str(tc.get_pin_value())
    value(tc, 'TraceTypeQuery1')  # Visibility
    value(trace.find_input_pin('bIgnoreSelf'), True)
    brk = call(g, '/Script/Engine.GameplayStatics:BreakHitResult')
    connect(trace.find_output_pin('OutHit'), brk.find_input_pin('Hit'))
    hit_class = call(g, '/Script/Engine.GameplayStatics:GetObjectClass', Object=brk.find_output_pin('HitActor')).find_result_pin()
    is_pawn = call(g, '/Script/Engine.KismetMathLibrary:ClassIsChildOf', TestClass=hit_class)
    value(is_pawn.find_input_pin('ParentClass'), '/Script/Engine.Pawn')
    visible = math(g, 'BooleanOR', A=math(g, 'Not_PreBool', A=trace.find_output_pin('ReturnValue')), B=is_pawn.find_result_pin())
    yes, _ = branch(g, trace.find_then_pin(), visible)
    connect(yes, b)
    added['DoTemporalCut'] = place(g, b0, 1400, 900)
    check('Player compiles with Cut line of sight', L.compile_blueprint(player))

    after = snapshot(player)
    for gname, nodes in before.items():
        check('Graph kept: ' + gname, gname in after)
        for nname, node in nodes.items():
            cur = after[gname][nname]
            assert cur['class'] == node['class'] and cur['title'] == node['title'] and cur['pins'].keys() == node['pins'].keys(), (gname, nname)
            for pname, old in node['pins'].items():
                new = cur['pins'][pname]
                assert new['value'] == old['value'] and new['type'] == old['type'], (gname, nname, pname)
                if (gname, nname, pname) in EDITED:
                    kept = [l for l in old['links'] if l in new['links']]
                    extra = [l for l in new['links'] if l not in old['links']]
                    assert all(l[0] in added.get(gname, set()) for l in extra), (gname, nname, pname, extra)
                    continue
                assert new['links'] == old['links'], (gname, nname, pname, old['links'], new['links'])
        assert set(after[gname]) - set(nodes) == added.get(gname, set()), (gname, set(after[gname]) - set(nodes))
    check('Only the documented edges changed; all previous nodes and values kept', True)
    check('Save BP_PlayerCharacter', unreal.EditorAssetLibrary.save_loaded_asset(player, False)); OUT['saved'].append(PLAYER)
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    (HERE / 'a_sprint_mvp_p1_implementation_result.json').write_text(json.dumps(OUT, indent=2, default=str, ensure_ascii=False), encoding='utf-8')
if not OUT['passed']: raise RuntimeError('A sprint MVP P1 migration failed; inspect report before retrying')
