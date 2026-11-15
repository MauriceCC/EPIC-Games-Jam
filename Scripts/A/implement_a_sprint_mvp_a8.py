"""Sprint MVP (docs/plan/05_SPRINT_MVP_2H.md §4.1) — A8 [PROPUESTA]. One-shot migration on top of A1–A7.

Run with the full editor via run_a_sprint_mvp_a8_editor.py.
Saves only A packages: Player/BP_PlayerCharacter and the new Player/CS_PlayerHit_A.

Hit-stop: AttackHit, after ApplyDamage on each enemy in range, sets that enemy's CustomTimeDilation to
HITSTOP_DILATION, remembers it in A_HitStopTargets and (re)starts a HITSTOP_SECONDS timer on the player that
calls A_EndHitStop, which restores 1.0 on every remembered valid actor. Only the hit enemy slows; never global.
Camera shake: TakeHit (damage actually received) starts CS_PlayerHit_A on player controller 0 before the
existing death/hit-reaction branch.
"""
import json, sys, traceback, shutil, tempfile
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, G, graph, connect, snapshot
ROOT = HERE.parent.parent
PLAYER = '/Game/Unscripted/Player/BP_PlayerCharacter'
SHAKE_DIR, SHAKE_NAME = '/Game/Unscripted/Player', 'CS_PlayerHit_A'
HITSTOP_DILATION, HITSTOP_SECONDS = 0.05, 0.06
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
def branch(g, start, c):
    n = g.add_branch_node(); connect(start, n.find_execute_pin()); connect(c, n.find_condition_pin()); return n.find_then_pin(), n.find_output_pin('else')
def nodes_of(g): return {n.get_name(): n for n in g.list_all_nodes()}
def menu(g, context, accept, label):
    keys = [str(k) for k in g.list_available_nodes([context])]
    choices = [k for k in keys if accept(k.replace(' ', ''))]
    OUT['menus'][label] = choices or [k for k in keys if 'ilation' in k or 'Matriz' in k][:40]
    assert choices, label
    return g.create_node_from_name(choices[0], unreal.Vector2D(0, 0), [context])
def set_dilation(g, start, actor, amount):
    n = menu(g, actor, lambda k: k.split('|')[-1] in ('SetCustomTimeDilation', 'AsignarCustomTimeDilation', 'EstablecerCustomTimeDilation'), 'SetCustomTimeDilation')
    if not n.find_self_pin().list_connected_pins(): connect(actor, n.find_self_pin())
    connect(start, n.find_execute_pin())
    pin = n.find_input_pin('CustomTimeDilation'); value(pin, amount)
    return n
def link_between(g, out_node, out_pin, in_node, in_pin):
    n = nodes_of(g); a = n[out_node].find_output_pin(out_pin); b = n[in_node].find_input_pin(in_pin)
    check('%s: %s.%s -> %s.%s present' % (g.get_graph().get_name(), out_node, out_pin, in_node, in_pin), any(p.is_same_native_pin(b) for p in a.list_connected_pins()))
    a.break_pin_links(); return a, b
def place(g, before, x, y):
    new = [n for name, n in nodes_of(g).items() if name not in before]
    for i, n in enumerate(new): L.set_node_pos(n, unreal.IntPoint(x + (i % 6) * 300, y + (i // 6) * 200))
    return {n.get_name() for n in new}

try:
    player = unreal.load_asset(PLAYER)
    ppath = player.generated_class().get_path_name()
    before = snapshot(player)
    names = [str(n) for n in L.list_member_variable_names(player)]
    check('A1-A7 already applied', 'bRetakeBlocked' in names and 'StaminaHistory' in names)
    check('Migration not already applied', 'A_HitStopTargets' not in names and 'A_EndHitStop' not in before)
    check('No shake asset overwritten', not unreal.EditorAssetLibrary.does_asset_exist(SHAKE_DIR + '/' + SHAKE_NAME))
    check('LegacyCameraShake available', hasattr(unreal, 'LegacyCameraShake'))
    backup = Path(tempfile.mkdtemp(prefix='Unscripted_A_SprintMVP_A8_'))
    shutil.copy2(ROOT / 'Unscripted/Content/Unscripted/Player/BP_PlayerCharacter.uasset', backup / 'BP_PlayerCharacter.uasset')
    OUT['backup'] = str(backup)
    added = {}; edited = set()

    # ---- Camera shake asset (A-owned) ----
    f = unreal.BlueprintFactory(); f.set_editor_property('parent_class', unreal.LegacyCameraShake)
    shake = unreal.AssetToolsHelpers.get_asset_tools().create_asset(SHAKE_NAME, SHAKE_DIR, unreal.Blueprint, f)
    check('Shake asset created', shake)
    check('Shake compiles', L.compile_blueprint(shake))
    cdo = unreal.get_default_object(shake.generated_class())
    cdo.set_editor_property('oscillation_duration', 0.18)
    cdo.set_editor_property('oscillation_blend_in_time', 0.02)
    cdo.set_editor_property('oscillation_blend_out_time', 0.08)
    def osc(amp, freq):
        o = unreal.FOscillator(); o.set_editor_property('amplitude', amp); o.set_editor_property('frequency', freq); return o
    loc = unreal.VOscillator(); loc.set_editor_property('x', osc(4.0, 35.0)); loc.set_editor_property('y', osc(4.0, 30.0)); loc.set_editor_property('z', osc(2.0, 40.0))
    cdo.set_editor_property('loc_oscillation', loc)
    rot = unreal.ROscillator(); rot.set_editor_property('roll', osc(0.6, 30.0))
    cdo.set_editor_property('rot_oscillation', rot)
    OUT['shake'] = {'duration': cdo.get_editor_property('oscillation_duration')}
    shake_class = shake.generated_class().get_path_name()

    # ---- Hit-stop state and restore function ----
    ev = graph(player, 'EventGraph')
    actor_array = unreal.EdGraphPinType(); actor_array.import_text('(PinCategory="object",PinSubCategoryObject="/Script/Engine.Actor",ContainerType=Array)')
    assert ev.add_member_variable('A_HitStopTargets', actor_array, '')
    L.set_blueprint_variable_category(player, 'A_HitStopTargets', 'Combat')
    L.set_blueprint_variable_instance_editable(player, 'A_HitStopTargets', False)
    G.create_and_edit_function_graph(player, 'A_EndHitStop')
    check('Player compiles with hit-stop shell', L.compile_blueprint(player))
    g = graph(player, 'A_EndHitStop')
    loop = g.add_macro_node('/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:ForEachLoop')
    check('ForEachLoop macro available', loop)
    connect(get(g, 'A_HitStopTargets'), loop.find_input_pin('Array'))
    connect(g.find_graph_entry_pin(), loop.find_input_pin('Exec'))
    element = loop.find_output_pin('Array Element')
    ok, _ = branch(g, loop.find_output_pin('LoopBody'), call(g, '/Script/Engine.KismetSystemLibrary:IsValid', Object=element).find_result_pin())
    set_dilation(g, ok, element, 1.0)
    arr = get(g, 'A_HitStopTargets')
    clear = menu(g, arr, lambda k: k.endswith(('|Clear', '|Vaciar')), 'Clear')
    if not clear.find_input_pin('TargetArray').list_connected_pins(): connect(arr, clear.find_input_pin('TargetArray'))
    connect(loop.find_output_pin('Completed'), clear.find_execute_pin())
    for i, x in enumerate(g.list_all_nodes()):
        if x.get_class().get_name() != 'K2Node_FunctionEntry': L.set_node_pos(x, unreal.IntPoint(300 + (i % 4) * 320, (i // 4) * 220))
    check('Player compiles with A_EndHitStop', L.compile_blueprint(player))

    # ---- AttackHit: start hit-stop on each damaged enemy ----
    g = graph(player, 'AttackHit'); b0 = set(nodes_of(g))
    a, b = link_between(g, 'K2Node_CallFunction_7', 'then', 'K2Node_CallFunction_8', 'execute')
    edited |= {('AttackHit', 'K2Node_CallFunction_7', 'then'), ('AttackHit', 'K2Node_CallFunction_8', 'execute'), ('AttackHit', 'K2Node_MacroInstance_0', 'Array Element')}
    target = nodes_of(g)['K2Node_MacroInstance_0'].find_output_pin('Array Element')
    sd = set_dilation(g, a, target, HITSTOP_DILATION)
    arr = get(g, 'A_HitStopTargets')
    add = menu(g, arr, lambda k: k.endswith(('|AddUnique', '|Añadirúnico', '|Agregarúnico')), 'AddUnique')
    if not add.find_input_pin('TargetArray').list_connected_pins(): connect(arr, add.find_input_pin('TargetArray'))
    connect(target, add.find_input_pin('NewItem'))
    connect(sd.find_then_pin(), add.find_execute_pin())
    timer = call(g, '/Script/Engine.KismetSystemLibrary:K2_SetTimer', add.find_then_pin(), FunctionName='A_EndHitStop', Time=HITSTOP_SECONDS, bLooping=False)
    connect(timer.find_then_pin(), b)
    added['AttackHit'] = place(g, b0, 1800, 700)
    check('Player compiles with hit-stop in AttackHit', L.compile_blueprint(player))

    # ---- TakeHit: camera shake on damage received ----
    g = graph(player, 'TakeHit'); b0 = set(nodes_of(g))
    a, b = link_between(g, 'K2Node_CallFunction_0', 'then', 'K2Node_IfThenElse_0', 'execute')
    edited |= {('TakeHit', 'K2Node_CallFunction_0', 'then'), ('TakeHit', 'K2Node_IfThenElse_0', 'execute')}
    pc = call(g, '/Script/Engine.GameplayStatics:GetPlayerController', PlayerIndex=0).find_result_pin()
    valid, invalid = branch(g, a, call(g, '/Script/Engine.KismetSystemLibrary:IsValid', Object=pc).find_result_pin())
    sh = call(g, '/Script/Engine.PlayerController:ClientStartCameraShake', valid, target=pc, Scale=1.0)
    value(sh.find_input_pin('Shake'), shake_class)
    connect(sh.find_then_pin(), b); connect(invalid, b)
    added['TakeHit'] = place(g, b0, 600, 500)
    check('Player compiles with camera shake', L.compile_blueprint(player))

    after = snapshot(player)
    added['A_EndHitStop'] = set(after['A_EndHitStop'])
    for gname, nodes in before.items():
        check('Graph kept: ' + gname, gname in after)
        for nname, node in nodes.items():
            cur = after[gname][nname]
            assert cur['class'] == node['class'] and cur['title'] == node['title'] and cur['pins'].keys() == node['pins'].keys(), (gname, nname)
            for pname, old in node['pins'].items():
                new = cur['pins'][pname]
                assert new['value'] == old['value'] and new['type'] == old['type'], (gname, nname, pname)
                if (gname, nname, pname) in edited:
                    extra = [l for l in new['links'] if l not in old['links']]
                    assert all(l[0] in added.get(gname, set()) for l in extra), (gname, nname, pname, extra)
                    continue
                assert new['links'] == old['links'], (gname, nname, pname, old['links'], new['links'])
        assert set(after[gname]) - set(nodes) == added.get(gname, set()), (gname, set(after[gname]) - set(nodes))
    check('Only the documented edges changed; all previous nodes and values kept', set(after) - set(before) == {'A_EndHitStop'})
    for bp in (shake, player):
        check('Save ' + bp.get_name(), unreal.EditorAssetLibrary.save_loaded_asset(bp, False)); OUT['saved'].append(bp.get_path_name())
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    (HERE / 'a_sprint_mvp_a8_implementation_result.json').write_text(json.dumps(OUT, indent=2, default=str, ensure_ascii=False), encoding='utf-8')
if not OUT['passed']: raise RuntimeError('A8 migration failed; inspect report before retrying')
