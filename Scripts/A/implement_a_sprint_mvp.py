"""Sprint MVP (docs/plan/05_SPRINT_MVP_2H.md §4.1) — A1, A2, A3, A4. One-shot migration.

Run with the full editor via run_a_sprint_mvp_editor.py (the action database is needed).
Saves only A packages: Player/BP_PlayerCharacter and Player/BP_PlayerController.
Does not touch Core/ (contracts), other divisions' assets or maps.

A1  BPI_PlayerControl on the player: SetRetakeBlocked, ClearRetakeHistory, SetGameplayInputEnabled.
    DoRetake exits while bRetakeBlocked; DoMove/DoLightAttack/DoDodge/DoParry/DoTemporalCut/DoRetake
    exit while bGameplayInputBlocked.
A2  Remove the debug PrintString nodes of the controller (E, Ctrl, Tab, Esc, LookMouse x2).
A3  ReceiveCombatHit returns its real result per branch: dead -> Ignored, invulnerable (dodge) -> Dodged,
    parry window -> Parried, damage -> Hit.
A4  [PROPUESTA] Esc (IA_Pause) -> A_HandlePause: first press shows "Press Esc again to quit" for 3 s,
    a second press inside that window quits. To be replaced by WBP_Pause (C3) when it exists.
"""
import json, sys, traceback, shutil, tempfile
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, G, graph, connect, snapshot
ROOT = HERE.parent.parent
PLAYER = '/Game/Unscripted/Player/BP_PlayerCharacter'
CONTROLLER = '/Game/Unscripted/Player/BP_PlayerController'
OUT = {'passed': False, 'saved': [], 'checks': [], 'base_commit': '83ee5bf'}
GATED = ['DoMove', 'DoLightAttack', 'DoDodge', 'DoParry', 'DoTemporalCut', 'DoRetake']
QUIT_WINDOW = 3.0


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
def place(new_nodes, x, y):
    for i, n in enumerate(new_nodes): L.set_node_pos(n, unreal.IntPoint(x + (i % 5) * 300, y + (i // 5) * 200))


def gate_entry(g, condition_factory):
    """Insert Branch(condition) between the function entry and its first node. Returns new node names."""
    before = set(nodes_of(g))
    entry = g.find_graph_entry_pin()
    targets = list(entry.list_connected_pins())
    assert len(targets) == 1, [str(t.get_pin_name()) for t in targets]
    entry.break_pin_links()
    yes, _ = branch(g, entry, condition_factory(g))
    connect(yes, targets[0])
    new = [n for name, n in nodes_of(g).items() if name not in before]
    p = L.get_node_pos(entry.get_owning_node())
    place(new, p.x + 40, p.y - 260)
    return {n.get_name() for n in new}, (targets[0].get_owning_node().get_name(), str(targets[0].get_pin_name()))


try:
    player = unreal.load_asset(PLAYER); controller = unreal.load_asset(CONTROLLER)
    ppath = player.generated_class().get_path_name(); cpath = controller.generated_class().get_path_name()
    player_before = snapshot(player); controller_before = snapshot(controller)
    vars_before = [str(n) for n in L.list_member_variable_names(player)]
    check('Migration not already applied', 'bRetakeBlocked' not in vars_before and 'A_HandlePause' not in controller_before)
    backup = Path(tempfile.mkdtemp(prefix='Unscripted_A_SprintMVP_'))
    for rel in ('Player/BP_PlayerCharacter.uasset', 'Player/BP_PlayerController.uasset'):
        shutil.copy2(ROOT / 'Unscripted/Content/Unscripted' / rel, backup / Path(rel).name)
    OUT['backup'] = str(backup)
    boolean = L.get_basic_type_by_name('bool'); real = L.get_basic_type_by_name('real')

    # ---------------- A3: ReceiveCombatHit results ----------------
    g = graph(player, 'ReceiveCombatHit')
    n = nodes_of(g)
    results = {k: n[k] for k in ('K2Node_FunctionResult_1', 'K2Node_FunctionResult_2', 'K2Node_FunctionResult_3', 'K2Node_FunctionResult_4')}
    # Confirm each return node sits on the branch we expect before changing its literal.
    check('Result_1 follows the bDead branch', any(p.get_owning_node().get_name() == 'K2Node_IfThenElse_0' for p in results['K2Node_FunctionResult_1'].find_execute_pin().list_connected_pins()))
    check('Result_2 follows the bInvulnerable branch', any(p.get_owning_node().get_name() == 'K2Node_IfThenElse_1' for p in results['K2Node_FunctionResult_2'].find_execute_pin().list_connected_pins()))
    check('Result_3 follows the parry sound', any(p.get_owning_node().get_name() == 'K2Node_CallFunction_3' for p in results['K2Node_FunctionResult_3'].find_execute_pin().list_connected_pins()))
    check('Result_4 follows TakeHit', any(p.get_owning_node().get_name() == 'K2Node_CallFunction_4' for p in results['K2Node_FunctionResult_4'].find_execute_pin().list_connected_pins()))
    rpin = results['K2Node_FunctionResult_1'].find_input_pin('Result')
    enum_values = json.loads(rpin.get_pin_type_as_json_schema())['enum']
    OUT['ehitresult_values'] = enum_values
    check('EHitResult has the contract values', all(v in enum_values for v in ('Hit', 'Blocked', 'Parried', 'Dodged', 'Ignored')))
    wanted = {'K2Node_FunctionResult_1': 'Ignored', 'K2Node_FunctionResult_2': 'Dodged', 'K2Node_FunctionResult_3': 'Parried', 'K2Node_FunctionResult_4': 'Hit'}
    for name, label in wanted.items():
        pin = results[name].find_input_pin('Result')
        assert pin.set_pin_value('NewEnumerator' + str(enum_values.index(label))), (name, label)
    check('Player compiles after A3', L.compile_blueprint(player))

    # ---------------- A1: retake / input blocking ----------------
    ev = graph(player, 'EventGraph')
    for name in ('bRetakeBlocked', 'bGameplayInputBlocked'):
        assert ev.add_member_variable(name, boolean, 'false'), name
        L.set_blueprint_variable_category(player, name, 'Temporal' if 'Retake' in name else 'Input')
        L.set_blueprint_variable_instance_editable(player, name, False)
    check('Player compiles with new flags', L.compile_blueprint(player))

    edges = {}
    for fname in GATED:
        g = graph(player, fname)
        added, target = gate_entry(g, lambda gg: math(gg, 'Not_PreBool', A=get(gg, 'bGameplayInputBlocked')))
        edges[fname] = [(added, target)]
    g = graph(player, 'DoRetake')
    added, target = gate_entry(g, lambda gg: math(gg, 'Not_PreBool', A=get(gg, 'bRetakeBlocked')))
    edges['DoRetake'].append((added, target))
    check('Player compiles with entry gates', L.compile_blueprint(player))

    ev = graph(player, 'EventGraph')
    ev_before = set(nodes_of(ev))
    e_block = L.add_event_override(player, 'SetRetakeBlocked', unreal.IntPoint(0, 0)); check('SetRetakeBlocked event created', e_block)
    e_clear = L.add_event_override(player, 'ClearRetakeHistory', unreal.IntPoint(0, 0)); check('ClearRetakeHistory event created', e_clear)
    e_input = L.add_event_override(player, 'SetGameplayInputEnabled', unreal.IntPoint(0, 0)); check('SetGameplayInputEnabled event created', e_input)
    ev = graph(player, 'EventGraph')
    nb = nodes_of(ev)
    e_block = nb[e_block.get_name()]; e_clear = nb[e_clear.get_name()]; e_input = nb[e_input.get_name()]
    OUT['event_pins'] = {e.get_name(): [str(p.get_pin_name()) for p in L.list_all_pins(e)] for e in (e_block, e_clear, e_input)}
    assign(ev, e_block.find_then_pin(), 'bRetakeBlocked', e_block.find_output_pin('bBlocked'))
    # ClearRetakeHistory: drop all samples so R has nothing to rewind to (charges are not consumed: DoRetake requires samples).
    def empty(start, name):
        arr = get(ev, name)
        menu = [str(k) for k in ev.list_available_nodes([arr])]
        choices = [k for k in menu if k.replace(' ', '').endswith(('|Clear', '|Vaciar', '|Borrar'))]
        OUT.setdefault('clear_menu', {})[name] = choices or [k for k in menu if 'lear' in k or 'acia' in k][:20]
        assert choices, 'Array Clear action not found for ' + name
        node = ev.create_node_from_name(choices[0], unreal.Vector2D(0, 0), [arr])
        if not node.find_input_pin('TargetArray').list_connected_pins(): connect(arr, node.find_input_pin('TargetArray'))
        connect(start, node.find_execute_pin()); return node.find_then_pin()
    end = empty(e_clear.find_then_pin(), 'PosHistory')
    end = empty(end, 'HPHistory')
    assign(ev, end, 'SnapAccum', 0)
    assign(ev, e_input.find_then_pin(), 'bGameplayInputBlocked', math(ev, 'Not_PreBool', A=e_input.find_output_pin('bEnabled')))
    new_ev = [x for name, x in nodes_of(ev).items() if name not in ev_before]
    place(new_ev, -2400, 6000)
    check('Player compiles with BPI_PlayerControl events', L.compile_blueprint(player))

    player_after = snapshot(player)
    # Preservation: every pre-existing node keeps class, title, pins, values and links, except the documented edits.
    changed_values = {('ReceiveCombatHit', k, 'Result') for k in wanted}
    for gname, nodes in player_before.items():
        check('Graph kept: ' + gname, gname in player_after)
        allowed_new = set()
        rewired = {}
        for added, (tnode, tpin) in edges.get(gname, []):
            allowed_new |= added
        for nname, node in nodes.items():
            cur = player_after[gname][nname]
            assert cur['class'] == node['class'] and cur['title'] == node['title'] and cur['pins'].keys() == node['pins'].keys(), (gname, nname)
            for pname, old in node['pins'].items():
                new = cur['pins'][pname]
                if (gname, nname, pname) not in changed_values:
                    assert new['value'] == old['value'], (gname, nname, pname)
                assert new['type'] == old['type'], (gname, nname, pname)
                if gname in edges and (cur['class'] == 'K2Node_FunctionEntry' and pname == 'then'):
                    assert len(new['links']) == 1 and new['links'][0][0] in allowed_new, (gname, new['links'])
                    continue
                if gname in edges and any((nname, pname) == t for _, t in edges[gname]):
                    assert len(new['links']) == 1 and new['links'][0][0] in allowed_new, (gname, nname, pname, new['links'])
                    continue
                assert new['links'] == old['links'], (gname, nname, pname, old['links'], new['links'])
        added = set(player_after[gname]) - set(nodes)
        if gname == 'EventGraph':
            assert added == {x.get_name() for x in new_ev}, added
        else:
            assert added == allowed_new, (gname, added)
    check('Player: only documented edits in pre-existing graphs', True)
    for name, label in wanted.items():
        check('ReceiveCombatHit %s returns %s' % (name, label), player_after['ReceiveCombatHit'][name]['pins']['Result']['value'] == 'NewEnumerator' + str(enum_values.index(label)))

    # ---------------- A2: controller debug prints ----------------
    g = graph(controller, 'EventGraph')
    n = nodes_of(g)
    debug = [x for x in n.values() if x.get_class().get_name() == 'K2Node_CallFunction' and 'PrintString' in str(L.get_node_title(x)).replace(' ', '')]
    OUT['removed_prints'] = [(x.get_name(), x.find_input_pin('InString').get_pin_value()) for x in debug]
    check('Six debug prints found', len(debug) == 6)
    to_string = [x for x in n.values() if 'ToString' in str(L.get_node_title(x)).replace(' ', '') and any(p.get_owning_node() in debug for p in x.find_result_pin().list_connected_pins())]
    check('LookMouse ToString found', len(to_string) == 1)
    g.remove_nodes(debug + to_string)
    check('Controller compiles without prints', L.compile_blueprint(controller))

    # ---------------- A4: Esc -> double press to quit ----------------
    ev = graph(controller, 'EventGraph')
    assert ev.add_member_variable('bA_QuitArmed', boolean, 'false')
    assert ev.add_member_variable('A_QuitArmedAt', real, '-100.0')
    for name in ('bA_QuitArmed', 'A_QuitArmedAt'):
        L.set_blueprint_variable_instance_editable(controller, name, False)
    G.create_and_edit_function_graph(controller, 'A_HandlePause')
    check('Controller compiles with A_HandlePause shell', L.compile_blueprint(controller))
    g = graph(controller, 'A_HandlePause')
    now = call(g, '/Script/Engine.GameplayStatics:GetRealTimeSeconds').find_result_pin()
    recent = math(g, 'LessEqual_DoubleDouble', A=math(g, 'Subtract_DoubleDouble', A=now, B=get(g, 'A_QuitArmedAt')), B=QUIT_WINDOW)
    quit_now, arm = branch(g, g.find_graph_entry_pin(), math(g, 'BooleanAND', A=get(g, 'bA_QuitArmed'), B=recent))
    call(g, '/Script/Engine.KismetSystemLibrary:QuitGame', quit_now)
    end = assign(g, arm, 'bA_QuitArmed', True)
    end = assign(g, end, 'A_QuitArmedAt', now)
    call(g, '/Script/Engine.KismetSystemLibrary:PrintString', end, InString='Press Esc again to quit', bPrintToScreen=True, bPrintToLog=False,
         TextColor='(R=1.000000,G=1.000000,B=1.000000,A=1.000000)', Duration=QUIT_WINDOW, Key='A_QuitPrompt')
    for i, x in enumerate(g.list_all_nodes()):
        if x.get_class().get_name() != 'K2Node_FunctionEntry': L.set_node_pos(x, unreal.IntPoint(300 + (i % 5) * 320, (i // 5) * 220))
    ev = graph(controller, 'EventGraph')
    pause = next(x for x in ev.list_all_nodes() if x.get_class().get_name() == 'K2Node_EnhancedInputAction' and 'IA_Pause' in str(L.get_node_title(x)))
    check('IA_Pause.Started is free after removing its print', not pause.find_output_pin('Started').list_connected_pins())
    handler = call(ev, cpath + ':A_HandlePause', pause.find_output_pin('Started'))
    p = L.get_node_pos(pause); L.set_node_pos(handler, unreal.IntPoint(p.x + 400, p.y))
    check('Controller compiles with Esc handler', L.compile_blueprint(controller))

    controller_after = snapshot(controller)
    for gname, nodes in controller_before.items():
        check('Controller graph kept: ' + gname, gname in controller_after)
        for nname, node in nodes.items():
            if nname not in controller_after[gname]:
                assert gname == 'EventGraph' and ('PrintString' in node['title'].replace(' ', '') or 'ToString' in node['title'].replace(' ', '')), (gname, nname)
                continue
            cur = controller_after[gname][nname]
            for pname, old in node['pins'].items():
                new = cur['pins'][pname]
                assert new['value'] == old['value'] and new['type'] == old['type'], (gname, nname, pname)
                expected = [l for l in old['links'] if l[0] in controller_after[gname]]
                if nname == pause.get_name() and pname == 'Started':
                    expected = [(handler.get_name(), 'execute')]
                assert new['links'] == expected, (gname, nname, pname, expected, new['links'])
    check('Controller: only prints removed and Esc rewired', True)
    remaining = [x for x in graph(controller, 'EventGraph').list_all_nodes() if 'PrintString' in str(L.get_node_title(x)).replace(' ', '')]
    check('No PrintString left in controller EventGraph', not remaining)

    for bp in (player, controller):
        check('Save ' + bp.get_name(), unreal.EditorAssetLibrary.save_loaded_asset(bp, False)); OUT['saved'].append(bp.get_path_name())
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    (HERE / 'a_sprint_mvp_implementation_result.json').write_text(json.dumps(OUT, indent=2, default=str), encoding='utf-8')
if not OUT['passed']: raise RuntimeError('A sprint MVP migration failed; inspect report before retrying')
