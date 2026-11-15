"""Read-only validation of the A sprint MVP migration (no saves). Run as a commandlet:
UnrealEditor-Cmd.exe Unscripted.uproject -run=pythonscript -script=Scripts/A/validate_a_sprint_mvp.py -unattended -nullrhi -nosound
Not a PIE session: calls saved functions on a transient player in the editor world.
"""
import json, sys, traceback
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, G, graph, snapshot
OUT = {'passed': False, 'checks': [], 'compile_failures': [], 'mode': 'commandlet; editor world; not PIE'}
def check(name, v):
    OUT['checks'].append({'name': name, 'passed': bool(v)}); assert v, name
def invoke(o, n, *a): return o.call_method(n, args=a)
def p(o, n): return o.get_editor_property(n)

actors = []
try:
    # 1) Every Unscripted Blueprint still compiles (consumers of BPI_PlayerControl / ReceiveCombatHit included).
    count = 0
    for path in unreal.EditorAssetLibrary.list_assets('/Game/Unscripted', recursive=True, include_folder=False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.Blueprint):
            count += 1
            if not L.compile_blueprint(asset): OUT['compile_failures'].append(path)
    OUT['blueprints_compiled'] = count
    check('All Unscripted Blueprints compile (%d)' % count, not OUT['compile_failures'])

    player = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
    controller = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerController')
    snap = snapshot(player)
    enum = ['Hit', 'Blocked', 'Parried', 'Dodged', 'Ignored']
    r = snap['ReceiveCombatHit']
    for node, label in [('K2Node_FunctionResult_1', 'Ignored'), ('K2Node_FunctionResult_2', 'Dodged'), ('K2Node_FunctionResult_3', 'Parried'), ('K2Node_FunctionResult_4', 'Hit')]:
        check('ReceiveCombatHit %s -> %s' % (node, label), r[node]['pins']['Result']['value'] == 'NewEnumerator%d' % enum.index(label))
    csnap = snapshot(controller)
    check('No PrintString in controller EventGraph', not [n for n in csnap['EventGraph'].values() if 'PrintString' in n['title'].replace(' ', '')])
    check('Controller has A_HandlePause', 'A_HandlePause' in csnap)
    pause = next(n for n in csnap['EventGraph'].values() if n['class'] == 'K2Node_EnhancedInputAction' and 'IA_Pause' in n['title'])
    check('IA_Pause.Started calls A_HandlePause', any('A_HandlePause' in csnap['EventGraph'][l[0]]['title'] for l in pause['pins']['Started']['links']))
    interact = next(n for n in csnap['EventGraph'].values() if n['class'] == 'K2Node_EnhancedInputAction' and 'IA_Interact' in n['title'])
    check('IA_Interact node kept (no extra consumer added)', not interact['pins']['Started']['links'])

    # 2) Functional checks on a transient player.
    # In-memory only (this validator never saves): allow the test to seed private state on the instance.
    for name in ('RetakeCharges', 'PosHistory', 'HPHistory', 'SnapAccum', 'bRetakeBlocked', 'bGameplayInputBlocked', 'bInvulnerable'):
        L.set_blueprint_variable_instance_editable(player, name, True)
    check('Player recompiles for the in-memory test', L.compile_blueprint(player))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    pawn = eas.spawn_actor_from_class(player.generated_class(), unreal.Vector(0, 3000, 300), transient=True); actors.append(pawn)
    check('Transient player spawned', pawn)
    def fill_history():
        pawn.set_editor_property('PosHistory', [unreal.Vector(10, 20, 30), unreal.Vector(40, 50, 60)])
        pawn.set_editor_property('HPHistory', [80.0, 90.0])
    pawn.set_editor_property('RetakeCharges', 2)
    check('Flags start cleared', not p(pawn, 'bRetakeBlocked') and not p(pawn, 'bGameplayInputBlocked'))

    invoke(pawn, 'SetRetakeBlocked', True)
    check('SetRetakeBlocked(true) sets the flag', p(pawn, 'bRetakeBlocked'))
    fill_history(); start = pawn.get_actor_location()
    invoke(pawn, 'DoRetake')
    check('Blocked retake keeps both charges', p(pawn, 'RetakeCharges') == 2)
    check('Blocked retake keeps history', len(p(pawn, 'PosHistory')) == 2)
    check('Blocked retake does not move the player', (pawn.get_actor_location() - start).length() < 0.01)
    invoke(pawn, 'SetRetakeBlocked', False)
    check('SetRetakeBlocked(false) clears the flag', not p(pawn, 'bRetakeBlocked'))

    invoke(pawn, 'SetGameplayInputEnabled', False)
    check('SetGameplayInputEnabled(false) blocks gameplay', p(pawn, 'bGameplayInputBlocked'))
    invoke(pawn, 'DoRetake')
    check('Retake ignored while gameplay input is disabled', p(pawn, 'RetakeCharges') == 2)
    invoke(pawn, 'DoDodge')
    check('Dodge ignored while gameplay input is disabled', not p(pawn, 'bInvulnerable'))
    invoke(pawn, 'SetGameplayInputEnabled', True)
    check('SetGameplayInputEnabled(true) restores gameplay', not p(pawn, 'bGameplayInputBlocked'))

    invoke(pawn, 'ClearRetakeHistory')
    check('ClearRetakeHistory empties position samples', len(p(pawn, 'PosHistory')) == 0)
    check('ClearRetakeHistory empties health samples', len(p(pawn, 'HPHistory')) == 0)
    check('ClearRetakeHistory resets the sample timer', p(pawn, 'SnapAccum') == 0)
    invoke(pawn, 'DoRetake')
    check('Retake with empty history does not spend a charge', p(pawn, 'RetakeCharges') == 2)

    fill_history()
    invoke(pawn, 'DoRetake')
    check('Unblocked retake still works (spends one charge)', p(pawn, 'RetakeCharges') == 1)
    check('Unblocked retake rewinds to the oldest sample', (pawn.get_actor_location() - unreal.Vector(10, 20, 30)).length() < 1.0)
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    for a in actors:
        try: a.destroy_actor()
        except Exception: pass
    (HERE / 'a_sprint_mvp_validation_result.json').write_text(json.dumps(OUT, indent=2, default=str), encoding='utf-8')
    print('A_SPRINT_MVP_VALIDATION passed=%s' % OUT['passed'])
